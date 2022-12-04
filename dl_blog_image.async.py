import asyncio
import re
import aiohttp
from bs4 import BeautifulSoup
from aiohttp import ClientSession

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds", "ocha-norma", "countrygirls", "risa-ogata", "shimizu--saki",
             "kumai-yurina-blog", "sudou-maasa-blog", "sugaya-risako-blog", "miyamotokarin-official",
             "kobushi-factory", "sayumimichishige-blog"]


async def run_all() -> None:
    list_pages_count = await asyncio.gather(*[parse_list_pages_count(blog_name=blog_name) for blog_name in blog_list])
    for blog_name, count in zip(blog_list, list_pages_count):
        await asyncio.gather(*[parse_list_page(blog_name=blog_name, order=i) for i in range(1, count + 1)])


async def parse_list_pages_count(blog_name: str) -> int:
    async with ClientSession() as session:
        async with session.get(f"https://ameblo.jp/{blog_name}/entrylist.html") as resp:
            resp_html = await resp.text()
            last_url = BeautifulSoup(resp_html, 'html.parser').find('a', class_='skin-paginationEnd')['href']
            return int(re.search('entrylist-(.*?).html', last_url).group(1))


async def parse_list_page(blog_name: str, order: int):
    async with ClientSession() as session:
        async with session.get(f"https://ameblo.jp/{blog_name}/entrylist-{order}.html") as resp:
            resp_html = await resp.text()
            archiveBody = BeautifulSoup(resp_html, 'html.parser').find('ul', class_='skin-archiveList')
            print(len(archiveBody), blog_name, order)


asyncio.run(run_all())
