# def download_image(url):


blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new"]

import time
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
from joblib import Parallel, delayed


dairy_url_list = []

def diary_link_clawler(keyword):
    driver.get(keyword)
    print(driver.title)
    dairy_list = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser')
    dairy_list = dairy_list.find('ul', {'class': 'skin-archiveList'})
    for dairy_list_html in dairy_list.find_all('h2', {'data-uranus-component': 'entryItemTitle'}):
        dairy_url_list.append(
            'https://ameblo.jp' + BeautifulSoup(str(dairy_list_html), 'html.parser').find('a')['href'])


options = webdriver.ChromeOptions()
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
for i in blog_list:
    diary_link_clawler("https://ameblo.jp/" + i + "/entrylist.html")
    pagenation_num = re.sub(r"\D", "", BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser').find('a', {
        'data-uranus-component': 'paginationEnd'})['href'])
    print("ページ数:"+pagenation_num)
    for x in range(2, int(pagenation_num) + 1):
        diary_link_clawler("https://ameblo.jp/" + i + '/entrylist-' + str(x) + ".html")

    print(dairy_url_list)
    time.sleep(5)
#    driver.quit()

# search_box = driver.find_element(By.NAME, "q")
# search_box.send_keys("ChromeDriver")
# search_box.submit()
# time.sleep(5)
driver.quit()
