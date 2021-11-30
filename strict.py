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

blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new", "juicejuice-official", "tsubaki-factory",
             "morningmusume-10ki", "morningm-13ki", "morningmusume15ki", "morningmusume-9ki", "beyooooonds-rfro",
             "beyooooonds-chicatetsu", "beyooooonds"]


def diary_link_crawler(keyword):
    dairy_url_list = []
    print(" Processing: " + keyword)
    dairy_list = BeautifulSoup(requests.get(keyword).text, 'html.parser').find('ul', {'class': 'skin-archiveList'})

    for dairy_list_html in dairy_list.find_all('h2', {'data-uranus-component': 'entryItemTitle'}):
        dairy_url_list.append(
            'https://ameblo.jp' + BeautifulSoup(str(dairy_list_html), 'html.parser').find('a')['href'])
    return dairy_url_list

# for i in blog_list:
#     for j in diary_link_crawler(i):
#         for k in
