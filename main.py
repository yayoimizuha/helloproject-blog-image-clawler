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

# blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new"]
blog_list = ["angerme-new"]

dairy_url_list = []
pagenation_links = []
N_JOBS = 40


def diary_link_clawler(keyword):
    print(" Processing: " + keyword)
    dairy_list = BeautifulSoup(requests.get(keyword).text, 'html.parser')
    dairy_list = dairy_list.find('ul', {'class': 'skin-archiveList'})

    for dairy_list_html in dairy_list.find_all('h2', {'data-uranus-component': 'entryItemTitle'}):
        dairy_url_list.append(
            'https://ameblo.jp' + BeautifulSoup(str(dairy_list_html), 'html.parser').find('a')['href'])


for i in blog_list:
    diary_link_clawler("https://ameblo.jp/" + i + "/entrylist.html")
    pagenation_num = re.sub(r'\D', "", BeautifulSoup(requests.get("https://ameblo.jp/" + i + "/entrylist.html").text,
                                                     'html.parser').find('a',
                                                                         {'data-uranus-component': 'paginationEnd'})[
        'href'])
    print("ページ数:" + pagenation_num)
    for x in range(2, int(pagenation_num) + 1):
        pagenation_links.append("https://ameblo.jp/" + i + '/entrylist-' + str(x) + ".html")

    _ = joblib.Parallel(n_jobs=N_JOBS, backend="threading")(
        joblib.delayed(diary_link_clawler)(keyword) for keyword in pagenation_links)

    # print(dairy_url_list)
    # time.sleep(5)

print(dairy_url_list)

# data-entry-id と data-image-id より、画像閲覧ページリンクを生成
print("url list length: " + str(len(dairy_url_list)))
json_pretty_printer = pprint.PrettyPrinter(indent=4)


def search_image_by_diary(url):
    # print("\n\tdairy_url: " + url)
    page = requests.get(url).text
    main_text = BeautifulSoup(page, 'html.parser').find('div', {'data-uranus-component': 'entryBody'})
    # print("main_text: " + str(main_text))

    photos = BeautifulSoup(str(main_text), 'html.parser').find_all('img', class_='PhotoSwipeImage')
    if photos is None:
        return None
    # print("photos: ")
    # print(repr(photos))
    photo_url = []

    hashtag = str(re.search('"theme_name":".*?"', page)[0])
    if hashtag == "":
        hashtag = 'None'
    hashtag = hashtag[14:-1]
    # print("hashtag: " + hashtag)
    iso_date = str(re.search('"dateModified":".*?"', page)[0])[16:-1]
    count = 0
    for images in photos:
        # print("images: " + str(images))
        count += 1
        if count % 2 == 0:
            continue

        photo_url.append(
            str(url).rsplit('/', 1)[0] + '/image-' + BeautifulSoup(str(images), 'html.parser').find('img')[
                'data-entry-id'] +
            '-' + BeautifulSoup(str(images), 'html.parser').find('img')['data-image-id'] + '.html' +
            '#' + hashtag + '#' + str(iso_date))

    print("photo_url[" + str(int(len(photo_url))) + "]: \n" + json_pretty_printer.pformat(photo_url) + '\n')
    return photo_url


photo_url_list = [joblib.Parallel(n_jobs=N_JOBS, backend='threading')(
    joblib.delayed(search_image_by_diary)(url) for url in dairy_url_list)]
# photo_url_list = [x for x in photo_url_list if x]  # remove null element
photo_url_list = list(itertools.chain.from_iterable(photo_url_list))
photo_url_list = list(itertools.chain.from_iterable(photo_url_list))

pprint.pprint(photo_url_list)


def download_image_link(url):
    body = BeautifulSoup(requests.get(url).text, 'html.parser').find('main')
    return str(BeautifulSoup(str(body), 'html.parser').find('img', {'aria-hidden': 'false'})['src'])


time.sleep(3)


# image_direct_link = joblib.Parallel(n_jobs=N_JOBS, backend='threading')(
#     joblib.delayed(download_image_link)(url) for url in photo_url_list)

# pprint.pprint(image_direct_link)


def download_image(url, filename, modified_date):
    urllib.request.urlretrieve(url, filename)
    os.utime(path=filename,
             times=(os.stat(path=filename).st_atime, datetime.datetime.fromisoformat(modified_date).timestamp()))


for i in photo_url_list:
    link = download_image_link(i)
    print("image url: " + str(i).split('#')[0] + '\n' + "image direct url: " + link)

    download_image(link,
                   str(i).split('#')[1] + '=' + str(i).split('#')[0].split('/')[-2] + '=' + re.sub(r'\D', "",
                                                                                                   str(i).split('#')[
                                                                                                       0]) + '.jpg',
                   str(i).split('#')[2])
