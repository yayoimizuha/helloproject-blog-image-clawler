import re
import sys
from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientConnectorError
from itertools import chain
from asyncio import gather, run, Semaphore, sleep
from datetime import datetime
from aiofiles import open
from os import path, getcwd, utime, stat
from tqdm.asyncio import tqdm

PARALLEL_LIMIT = 300

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds", "ocha-norma", "countrygirls", "risa-ogata", "shimizu--saki",
             "kumai-yurina-blog", "sudou-maasa-blog", "sugaya-risako-blog", "miyamotokarin-official",
             "kobushi-factory", "sayumimichishige-blog"]

# blog_list = ["risa-ogata"]

request_header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'
}

url_list: list = list()


def debug_print(*print_str: object, end: str = '\n'):
    if False:
        print(print_str, end='')
        print(end)


async def run_all() -> None:
    sem: Semaphore = Semaphore(PARALLEL_LIMIT)
    session: ClientSession = ClientSession(trust_env=True, headers=request_header)
    list_pages_count = await gather(*[parse_list_pages_count(blog_name=blog_name) for blog_name in blog_list],
                                    return_exceptions=True)
    for name, pages in zip(blog_list, list_pages_count):
        print(name, pages)

    url_lists: list = list()
    for blog_name, count in zip(blog_list, list_pages_count):
        url_lists.extend(await tqdm.gather(*[parse_list_page(blog_name, i, sem, session) for i in range(1, count + 1)],
                                           desc=blog_name))

    global url_list
    url_list = list(chain.from_iterable(url_lists))
    # pprint.pprint(url_list)
    for url in url_list:
        if 'html' not in url:
            print(url)

    image_links = await tqdm.gather(*[parse_image(url, sem, session) for url in url_list], desc="scan blog")
    image_links = [i for i in image_links if type(i) is list]
    async with open(file=path.join(getcwd(), "log.log"), mode="w", encoding='utf-8') as f:
        await f.write(str(image_links))
    # print(image_links)
    image_link_package = list(chain.from_iterable(image_links))
    # pprint(image_link_package)

    await tqdm.gather(
        *[download_image(filename, url, date, sem, session) for filename, url, date in image_link_package],
        desc="downloading images")

    await session.close()


async def parse_list_pages_count(blog_name: str) -> int:
    async with ClientSession(trust_env=True, headers=request_header) as session:
        async with session.get(f"https://ameblo.jp/{blog_name}/entrylist.html") as resp:
            resp_html = await resp.text()
            last_url = BeautifulSoup(resp_html, 'lxml').find('a', class_='skin-paginationEnd')['href']
    return int(re.search('entrylist-(.*?).html', last_url).group(1))


async def parse_list_page(blog_name: str, order: int, sem: Semaphore, session: ClientSession) -> list[str]:
    async with sem:
        async with session.get(f"https://ameblo.jp/{blog_name}/entrylist-{order}.html") as resp:
            resp_html = await resp.text()
    debug_print(blog_name, order)
    archive_body = BeautifulSoup(resp_html, 'lxml').find('ul', class_='skin-archiveList')
    blog_boxes = archive_body.find_all('li', class_='skin-borderQuiet')
    page_url_list: list[str] = list()
    for blog_box in blog_boxes:
        title = blog_box.find('h2', {'data-uranus-component': 'entryItemTitle'})
        url = "https://ameblo.jp" + title.find('a')['href']
        if "secret.ameba.jp" in url:
            continue
        debug_print(title.text, url)
        page_url_list.append(url)
    return page_url_list


async def parse_image(url: str, sem: Semaphore, session: ClientSession) -> list[tuple[str, str, datetime]]:
    while True:
        async with sem:
            try:
                async with session.get(url) as resp:
                    resp_html = await resp.text()
                    await sleep(1.0)
                    break
            except ClientConnectorError as e:
                await sleep(5.0)
                print(e, file=sys.stderr)
    theme = grep_theme(resp_html)
    date = datetime.fromisoformat(grep_modified_time(resp_html))
    blog_account = url.split('/')[-2]
    blog_entry = url.split('/')[-1].split('.')[0].removeprefix("entry-")
    parse = BeautifulSoup(resp_html, 'lxml')
    debug_print(url_list.index(url), end='\t')
    debug_print(theme + "　" * (8 - len(theme)), end='')
    debug_print(date.date(), end='\t')
    debug_print(parse.find('title').text)
    entry_body = parse.find('div', {'data-uranus-component': 'entryBody'})
    for span in entry_body.find_all('span'):
        span.decompose()
    for emoji in entry_body.find_all('img', class_='emoji'):
        emoji.decompose()
    image_divs = entry_body.find_all('img', class_='PhotoSwipeImage')
    return_list = list()
    for div in image_divs:
        return_list.append((
            '='.join([theme, blog_account, blog_entry]) + '-' + div["data-image-order"] + '.jpg',
            str(div["src"]).split('?')[0],
            date
        ))
    # filename , url ,date
    # pprint(return_list)
    return return_list


async def download_image(filename: str, url: str, date: datetime, sem: Semaphore, session: ClientSession) -> None:
    filepath = path.join(getcwd(), "dl_await", filename)
    if path.isfile(filepath):
        # print(f"file already downloaded.: {filename}")
        return
    async with sem:
        # print("download: ", url)
        async with session.get(url) as resp:
            async with open(file=filepath, mode="wb") as f:
                await f.write(await resp.read())
    utime(path=filepath, times=(stat(path=filepath).st_atime, date.timestamp()))


theme_regex = re.compile('"theme_name":"(.*?)"')
modified_time_regex = re.compile('"dateModified":"(.*?)"')


def grep_theme(html: str) -> str:
    return str(theme_regex.search(html).group(1))


def grep_modified_time(html: str) -> str:
    return str(modified_time_regex.search(html).group(1))


run(run_all())
