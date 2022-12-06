import pprint
import re
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from itertools import chain
from asyncio import gather, run, Semaphore
from datetime import datetime

PARALLEL_LIMIT = 300

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds", "ocha-norma", "countrygirls", "risa-ogata", "shimizu--saki",
             "kumai-yurina-blog", "sudou-maasa-blog", "sugaya-risako-blog", "miyamotokarin-official",
             "kobushi-factory", "sayumimichishige-blog"]

blog_list = ["ocha-norma"]

request_header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'
}


async def run_all() -> None:
    sem: Semaphore = Semaphore(PARALLEL_LIMIT)
    session: ClientSession = ClientSession(trust_env=True, headers=request_header)
    list_pages_count = await gather(*[parse_list_pages_count(blog_name=blog_name) for blog_name in blog_list],
                                    return_exceptions=True)
    for name, pages in zip(blog_list, list_pages_count):
        print(name, pages)

    url_lists: list = list()

    for blog_name, count in zip(blog_list, list_pages_count):
        url_lists.extend(
            await gather(*[parse_list_page(blog_name, i, sem, session) for i in range(1, count + 1)],
                         return_exceptions=True))
    url_list = list(chain.from_iterable(url_lists))
    # pprint.pprint(url_list)
    for url in url_list:
        if 'html' not in url:
            print(url)

    image_link = await gather(*[parse_image(url, sem, session) for url in url_list])
    pprint.pprint(list(chain.from_iterable(image_link)))

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
    print(blog_name, order, sep='\t')
    archive_body = BeautifulSoup(resp_html, 'lxml').find('ul', class_='skin-archiveList')
    blog_boxes = archive_body.find_all('li', class_='skin-borderQuiet')
    url_list: list[str] = list()
    for blog_box in blog_boxes:
        title = blog_box.find('h2', {'data-uranus-component': 'entryItemTitle'})
        # print(title.text, "https://ameblo.jp" + title.find('a')['href'])
        url_list.append("https://ameblo.jp" + title.find('a')['href'])
    return url_list


# filename , url ,date
async def parse_image(url: str, sem: Semaphore, session: ClientSession) -> list[tuple[str, str, datetime]]:
    async with sem:
        async with session.get(url) as resp:
            resp_html = await resp.text()
    theme = grep_theme(resp_html)
    date = datetime.fromisoformat(grep_modified_time(resp_html))
    blog_account = url.split('/')[-2]
    blog_entry = url.split('/')[-1].split('.')[0]
    parse = BeautifulSoup(resp_html, 'lxml')
    print(theme, end='\t')
    print(parse.find('title').text, end='\t')
    print(grep_modified_time(resp_html))
    entry_body = parse.find('div', {'data-uranus-component': 'entryBody'})
    image_divs = entry_body.find_all('img', class_='PhotoSwipeImage')
    return_list = list()
    for div in image_divs:
        return_list.append((
            '='.join([theme, blog_account, blog_entry]) + '-' + div["data-image-order"] + '.jpg',
            str(div["src"]).split('?')[0],
            date
        ))
    return return_list


theme_regex = re.compile('"theme_name":"(.*?)"')
modified_time_regex = re.compile('"dateModified":"(.*?)"')


def grep_theme(html: str) -> str:
    return str(theme_regex.search(html).group(1))


def grep_modified_time(html: str) -> str:
    return str(modified_time_regex.search(html).group(1))


run(run_all())
