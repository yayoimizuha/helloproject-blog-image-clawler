import sys
import time
import pprint
from bs4 import BeautifulSoup
import re
import requests
import joblib
import urllib.request
import itertools
import datetime
import os
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ssl._create_default_https_context = ssl._create_unverified_context

N_JOBS = 40

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds"]

blog_list.clear()
blog_list = ["morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro", "beyooooonds-chicatetsu", "beyooooonds"]


def safe_request_get_as_text(url):
    text = ""
    get_error = 0
    while get_error == 0:
        try:
            text = requests.get(url).text
            get_error += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(1) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            get_error = 0
        if get_error > 5:
            continue

    return text


def inspect_entry_list(url):
    print(" Processing: " + url)
    sys.stderr.flush()
    sys.stdout.flush()
    item_tags = BeautifulSoup(safe_request_get_as_text(url), 'html.parser').find('ul', {'class': 'skin-archiveList'}) \
        .find_all('h2', {'data-uranus-component': 'entryItemTitle'})
    hrefs = []
    for tag in item_tags:
        hrefs.append("https://ameblo.jp" + BeautifulSoup(str(tag), 'html.parser').find('a')['href'])
    return hrefs


def diary_link_crawler(keyword):
    dairy_url_list = []

    # Inspect page num
    pagination_num = int(
        re.search('entrylist-(.*?).html',
                  BeautifulSoup(safe_request_get_as_text("https://ameblo.jp/" + keyword + "/entrylist.html"),
                                'html.parser').find('a', {'data-uranus-component': 'paginationEnd'})['href']).group(1))
    print("ページ数:" + str(pagination_num))
    sys.stderr.flush()
    sys.stdout.flush()
    # Extract 1st page.
    dairy_url_list.append(inspect_entry_list("https://ameblo.jp/" + keyword + "/entrylist.html"))

    # Generating each page links
    pagination_links = []
    pagination_links.clear()
    for x in range(2, int(pagination_num) + 1):
        pagination_links.append("https://ameblo.jp/" + keyword + '/entrylist-' + str(x) + ".html")

    # Crawl pages as parallel
    dairy_url_list = joblib.Parallel(n_jobs=N_JOBS, backend="threading")(
        joblib.delayed(inspect_entry_list)(keyword) for keyword in pagination_links)

    pprint.pprint(dairy_url_list)
    # time.sleep(1600)
    # Return url array.(formatted)
    return itertools.chain.from_iterable(dairy_url_list)


def image_detector(url):
    page = safe_request_get_as_text(url)
    image_class = BeautifulSoup(page, 'html.parser').find('div', {'data-uranus-component': 'entryBody'}) \
        .find_all('img', class_='PhotoSwipeImage')

    image_url = []

    hashtag = str(re.search('"theme_name":".*?"', page)[0])
    if hashtag == "":
        hashtag = 'None'
    hashtag = hashtag[14:-1]
    iso_date = str(re.search('"dateModified":".*?"', page)[0])[16:-1]
    count = 0
    for images in image_class:
        count += 1
        if count % 2 == 0:
            continue
        bs4_img = BeautifulSoup(str(images), 'html.parser').find('img')
        if int(float(re.sub(r"[^\d.]", "", bs4_img['width']))) < 30:
            continue

        image_url.append(
            str(url).rsplit('/', 1)[0] + '/image-' + bs4_img['data-entry-id'] + '-' + bs4_img['data-image-id']
            + '.html' + '#' + hashtag + '#' + str(iso_date) + '#' + bs4_img['data-image-order'])

    print("image_url[" + str(int(len(image_url))) + "]: \n" + pprint.PrettyPrinter(indent=4).pformat(image_url) + '\n')
    sys.stderr.flush()
    sys.stdout.flush()
    return image_url


def image_downloader(image_link):
    if image_link is None:
        return 'None'

    # blog_idを取得
    blog_id = str(re.search(".*?image-(\d+)-.*?", str(image_link)).group(1))
    if blog_id is None:
        blog_id = 'no_blog_id'

    # ブログ内の画像番号を取得
    image_order = str(image_link).split('#')[3]
    if image_order is None:
        image_order = str(1)

    direct_image_link = ""
    get_error = 0
    while get_error == 0:
        try:
            direct_image_link = \
                BeautifulSoup(safe_request_get_as_text(image_link), 'html.parser').find('main') \
                    .find('img', {'aria-hidden': 'false'})['src']
            get_error += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(2) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            get_error = 0
        if get_error == 0:
            return 0

    print("direct_image_link: " + direct_image_link)
    sys.stderr.flush()
    sys.stdout.flush()

    filename = str(image_link).split('#')[1] + '=' + str(image_link).split('#')[0].split('/')[-2] + '=' + blog_id \
               + '-' + image_order + '.jpg'
    download_status = 0
    while download_status == 0:
        try:
            urllib.request.urlretrieve(direct_image_link, filename)
            download_status += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(3) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
        if download_status > 5:
            continue

    os.utime(path=filename,
             times=(os.stat(path=filename).st_atime,
                    datetime.datetime.fromisoformat(str(image_link).split('#')[2]).timestamp()))
    return 0


def sub_routine(id):
    for k in image_detector(id):
        time.sleep(5.0000000000000)
        image_downloader(k)
    # https://ameblo.jp/juicejuice-official/entry-12527683506.html でエラーが出る。(写真集へのリンクが悪さしてる)


for i in blog_list:
    _ = joblib.Parallel(n_jobs=N_JOBS, backend='threading')(
        joblib.delayed(sub_routine)(url) for url in diary_link_crawler(i))
    time.sleep(300)

# for i in blog_list:
#    for j in diary_link_crawler(i):
#        for k in image_detector(j):
#            image_downloader(k)
