import re
import sys
from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientConnectorError, ClientTimeout
from itertools import chain
from asyncio import run, Semaphore, sleep
from datetime import datetime
from aiofiles import open
from os import path, getcwd, utime, stat, cpu_count
from tqdm.asyncio import tqdm
from concurrent.futures import as_completed, ProcessPoolExecutor, Future

PARALLEL_LIMIT = 300
blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds", "ocha-norma", "countrygirls", "risa-ogata", "shimizu--saki",
             "kumai-yurina-blog", "sudou-maasa-blog", "sugaya-risako-blog", "miyamotokarin-official",
             "kobushi-factory", "sayumimichishige-blog"]

# blog_list = ["juicejuice-official"]

request_header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'
}


def debug_print(*print_str: object, end: str = '\n'):
    if False:
        print(print_str, end='')
        print(end)


async def run_each(name: str) -> None:
    sem: Semaphore = Semaphore(PARALLEL_LIMIT)
    session: ClientSession = ClientSession(trust_env=True, headers=request_header, timeout=ClientTimeout(total=10 * 60))

    list_pages_count = await parse_list_pages_count(name)

    print(name, list_pages_count)

    url_lists = await tqdm.gather(*[parse_list_page(name, i, sem, session) for i in range(1, list_pages_count + 1)],
                                  desc=name)

    url_list = list(chain.from_iterable(url_lists))

    for url in url_list:
        if 'html' not in url:
            print(url)

    executor = ProcessPoolExecutor(max_workers=cpu_count())
    futures = await tqdm.gather(*[parse_blog_post(url, sem, session, executor) for url in url_list], desc="scan blog")
    images_list = list()
    for future in tqdm(as_completed(futures), desc="waiting processing " + name, total=len(futures)):
        images_list.append(future.result())
    executor.shutdown()
    image_link_package = list(chain.from_iterable(images_list))

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


def parse_image(html: str, url: str) -> list:
    blog_account = url.split('/')[-2]
    theme = theme_curator(grep_theme(html), blog_account)
    date = datetime.fromisoformat(grep_modified_time(html))
    blog_entry = url.split('/')[-1].split('.')[0].removeprefix("entry-")
    parse = BeautifulSoup(html, 'lxml')
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
    return return_list


async def parse_blog_post(url: str, sem: Semaphore, session: ClientSession, executor: ProcessPoolExecutor) -> Future:
    # -> list[tuple[str, str, datetime]]:

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

    return executor.submit(parse_image, resp_html, url)


async def download_image(filename: str, url: str, date: datetime, sem: Semaphore, session: ClientSession) -> None:
    filepath = path.join(getcwd(), "dl_await", filename)
    if path.isfile(filepath):
        # print(f"file already downloaded.: {filename}")
        return
    async with sem:
        # print("download: ", url)
        async with session.get(url) as resp:
            if resp.content_type != "image/jpeg":
                return
            async with open(file=filepath, mode="wb") as f:
                await f.write(await resp.read())
    utime(path=filepath, times=(stat(path=filepath).st_atime, date.timestamp()))


theme_regex = re.compile('"theme_name":"(.*?)"')
modified_time_regex = re.compile('"dateModified":"(.*?)"')


def grep_theme(html: str) -> str:
    return str(theme_regex.search(html).group(1))


def grep_modified_time(html: str) -> str:
    return str(modified_time_regex.search(html).group(1))


def theme_curator(theme: str, blog_id: str) -> str:
    if theme == "":
        theme = 'None'
    elif 'risa-ogata' == blog_id:
        theme = '小片リサ'
    elif 'shimizu--saki' == blog_id:
        theme = "清水佐紀"
    elif 'kumai-yurina-blog' == blog_id:
        theme = "熊井友理奈"
    elif 'sudou-maasa-blog' == blog_id:
        theme = "須藤茉麻"
    elif 'sugaya-risako-blog' == blog_id:
        theme = "菅谷梨沙子"
    elif 'miyamotokarin-official' == blog_id:
        theme = "宮本佳林"
    elif 'sayumimichishige-blog' == blog_id:
        theme = "道重さゆみ"
    elif '梁川 奈々美' in theme:
        theme = '梁川奈々美'
    return theme


if __name__ == '__main__':
    for blog in blog_list:
        run(run_each(blog))
