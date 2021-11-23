# def download_image(url):
import joblib
import requests

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new"]

import time
from bs4 import BeautifulSoup
import re
import requests
import joblib

dairy_url_list = []
pagenation_links = []

def diary_link_clawler(keyword):
    print("Processing: " + keyword)
    dairy_list = BeautifulSoup(requests.get(keyword).text, 'html.parser')
    dairy_list = dairy_list.find('ul', {'class': 'skin-archiveList'})
    for dairy_list_html in dairy_list.find_all('h2', {'data-uranus-component': 'entryItemTitle'}):
        dairy_url_list.append(
            'https://ameblo.jp' + BeautifulSoup(str(dairy_list_html), 'html.parser').find('a')['href'])


for i in blog_list:
    diary_link_clawler("https://ameblo.jp/" + i + "/entrylist.html")
    pagenation_num = re.sub(r'\D', "", BeautifulSoup(requests.get("https://ameblo.jp/" + i + "/entrylist.html").text,
                                                     'html.parser').find('a', {
        'data-uranus-component': 'paginationEnd'})['href'])
    print("ページ数:" + pagenation_num)
    for x in range(2, int(pagenation_num) + 1):
        pagenation_links.append("https://ameblo.jp/" + i + '/entrylist-' + str(x) + ".html")

    _ = joblib.Parallel(n_jobs=8)(joblib.delayed(diary_link_clawler)(keyword) for keyword in pagenation_links)

    print(dairy_url_list)
    time.sleep(5)
