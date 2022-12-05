import asyncio
import pprint
import re
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from itertools import chain

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
    list_pages_count = await asyncio.gather(*[parse_list_pages_count(blog_name=blog_name) for blog_name in blog_list],
                                            return_exceptions=True)
    print(list_pages_count)

    url_lists: list = list()
    for blog_name, count in zip(blog_list, list_pages_count):
        url_lists.extend(
            await asyncio.gather(*[parse_list_page(blog_name=blog_name, order=i) for i in range(1, count + 1)],
                                 return_exceptions=True))
    url_list = list(chain.from_iterable(url_lists))
    pprint.pprint(url_list)

    await asyncio.gather(*[parse_image(url) for url in url_list])


async def parse_list_pages_count(blog_name: str) -> int:
    async with ClientSession(trust_env=True, headers=request_header) as session:
        async with session.get(f"https://ameblo.jp/{blog_name}/entrylist.html") as resp:
            resp_html = await resp.text()
            last_url = BeautifulSoup(resp_html, 'html.parser').find('a', class_='skin-paginationEnd')['href']
            return int(re.search('entrylist-(.*?).html', last_url).group(1))


async def parse_list_page(blog_name: str, order: int) -> list[str]:
    async with ClientSession(trust_env=True, headers=request_header) as session:
        async with session.get(f"https://ameblo.jp/{blog_name}/entrylist-{order}.html") as resp:
            resp_html = await resp.text()
            print(blog_name, order, sep='\t')
            archive_body = BeautifulSoup(resp_html, 'html.parser').find('ul', class_='skin-archiveList')
            blog_boxes = archive_body.find_all('li', class_='skin-borderQuiet')
            url_list: list[str] = list()
            for blog_box in blog_boxes:
                title = blog_box.find('h2', {'data-uranus-component': 'entryItemTitle'})
                # print(title.text, "https://ameblo.jp" + title.find('a')['href'])
                url_list.append("https://ameblo.jp" + title.find('a')['href'])
            return url_list


async def parse_image(url: str) -> tuple[str, str]:
    async with ClientSession(trust_env=True, headers=request_header) as session:
        async with session.get(url) as resp:
            resp_html = await resp.text()
            theme = grep_theme(resp_html)
            print(theme, end='\t')
            print(BeautifulSoup(resp_html, 'html.parser').find('title').text, end='\t')
            print(grep_modified_time(resp_html))


theme_regex = re.compile('"theme_name":"(.*?)"')
modified_time_regex = re.compile('"dateModified":"(.*?)"')


def grep_theme(html: str) -> str:
    return str(theme_regex.search(html).group(1))


def grep_modified_time(html: str) -> str:
    return str(modified_time_regex.search(html).group(1))


asyncio.run(run_all())
