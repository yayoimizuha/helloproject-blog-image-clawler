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

now_time = time.time()

N_JOBS = 40
# print(os.listdir(os.path.join(os.getcwd(), 'images')))
# time.sleep(10)
exist_file = [f for f in os.listdir(os.path.join(os.getcwd(), 'images')) if
              os.path.isfile(os.path.join(os.getcwd(), 'images', f))]
# only image file
exist_file = [f for f in exist_file if '.jpg' in f]

downloaded_key = []
for file_name in exist_file:
    downloaded_key.append(int((file_name.split('=')[-1].split('-')[0])))
downloaded_key = list(set(downloaded_key))
# print(downloaded_key)

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds", "ocha-norma"]
# blog_list = ["juicejuice-official"]

request_header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'
}

added_file = []


def safe_request_get_as_text(url):
    err_num = 0
    get_error = 0
    text = ""
    while get_error == 0:
        try:
            page = requests.get(url, headers=request_header)
            text = page.text
            if page.status_code == 404:
                return None
            get_error += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(1) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            err_num += 1
        if err_num > 5:
            continue

    return text


def inspect_entry_list(url):
    print(" Processing: " + url)
    sys.stderr.flush()
    sys.stdout.flush()
    item_tags_html = safe_request_get_as_text(url)
    if item_tags_html is None:
        return []
    item_tags = BeautifulSoup(item_tags_html, 'html.parser').find('ul', {
        'class': 'skin-archiveList'}).find_all('h2', {'data-uranus-component': 'entryItemTitle'})
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

    # Generating each page links
    pagination_links = ["https://ameblo.jp/" + keyword + "/entrylist.html"]
    for x in range(2, int(pagination_num) + 1):
        pagination_links.append("https://ameblo.jp/" + keyword + '/entrylist-' + str(x) + ".html")

    # Crawl pages as parallel
    dairy_url_list = joblib.Parallel(n_jobs=N_JOBS, backend="threading")(
        joblib.delayed(inspect_entry_list)(keyword) for keyword in pagination_links)
    dairy_url_list = list(itertools.chain.from_iterable(dairy_url_list))
    dairy_url_list = [s for s in dairy_url_list if 'amember' not in s]

    # delete existed photo
    exist_file_url = []
    for url_num in downloaded_key:
        exist_file_url.append("https://ameblo.jp/" + keyword + "/entry-" + str(url_num) + ".html")
    dairy_url_list = list(set(dairy_url_list) - set(exist_file_url))

    pprint.pprint(dairy_url_list)
    # time.sleep(1600)
    # Return url array.(formatted)
    return dairy_url_list


def image_detector(url):
    err_num = 0
    get_error = 0
    page = ""
    image_class = ""
    while get_error == 0:
        try:
            page = safe_request_get_as_text(url)
            if page is None:
                return []
            image_class = BeautifulSoup(page, 'html.parser').find('div',
                                                                  {'data-uranus-component': 'entryBody'}).find_all(
                'img', class_='PhotoSwipeImage')
            get_error += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(2) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            err_num += 1
        if err_num > 5:
            return None
    image_url = []

    hashtag = str(re.search('"theme_name":".*?"', page)[0])
    if hashtag == "":
        hashtag = 'None'
    hashtag = hashtag[14:-1]
    iso_date = str(re.search('"dateModified":".*?"', page)[0])[16:-1]
    count = 0
    for images in image_class:
        count += 1
        # if count % 2 == 0:
        #     continue
        bs4_img = BeautifulSoup(str(images), 'html.parser').find('img')
        if int(float(re.sub(r"[^\d.]", "", bs4_img['width']))) < 30:
            continue

        image_url.append(
            str(url).rsplit('/', 1)[0] + '/image-' + bs4_img['data-entry-id'] + '-' + bs4_img['data-image-id']
            + '.html' + '#' + hashtag + '#' + str(iso_date) + '#' + bs4_img['data-image-order'])
    if int(len(image_url)) == 0:
        print("Any image is not found in url: " + url)
        return []
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
    err_num = 0
    get_error = 0
    while get_error == 0:
        try:
            image_link_html = safe_request_get_as_text(image_link)
            if image_link_html is None:
                return 0
            direct_image_link = \
                BeautifulSoup(image_link_html, 'html.parser').find('main') \
                    .find('img', {'aria-hidden': 'false'})['src']
            get_error += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(3) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            err_num += 1
        if err_num > 5:
            return 0

    print("direct_image_link: " + direct_image_link)
    sys.stderr.flush()
    sys.stdout.flush()

    filename = str(image_link).split('#')[1] + '=' + str(image_link).split('#')[0].split('/')[
        -2] + '=' + blog_id + '-' + image_order + '.jpg'
    filename = os.path.join(os.getcwd(), 'images', filename)
    err_num = 0
    download_status = 0
    while download_status == 0:
        try:
            urllib.request.urlretrieve(direct_image_link, filename)
            download_status += 1
        except BaseException as error:
            print("\n\n\n" + "Error occurred:(4) " + str(error) + "\n\n\n")
            sys.stderr.flush()
            sys.stdout.flush()
            err_num += 1
        if err_num > 5:
            return 0

    os.utime(path=filename,
             times=(os.stat(path=filename).st_atime,
                    datetime.datetime.fromisoformat(str(image_link).split('#')[2]).timestamp()))
    added_file.append([image_link.split('#')[0], direct_image_link, os.path.basename(filename)])
    return 0


def sub_routine(url):
    for k in image_detector(url):
        if k is None:
            continue
        time.sleep(5.0000000000000)
        image_downloader(k)


for i in blog_list:
    _ = joblib.Parallel(n_jobs=N_JOBS, backend='threading')(
        joblib.delayed(sub_routine)(url) for url in diary_link_crawler(i))

print("Added all new files:")
pprint.pprint(added_file)
print("Add " + str(len(added_file)) + " files.")
print(str(time.time() - now_time) + " sec")
