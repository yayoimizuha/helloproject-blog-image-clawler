# def download_image(url):


blog_list = ["angerme-ss-shin", "angerme-amerika", "angerme-new"]

import time
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)


for i in blog_list:
    driver.get("https://ameblo.jp/"+i+"/entrylist.html")
    print(driver.title)
    time.sleep(5)
#    driver.quit()

#search_box = driver.find_element(By.NAME, "q")
#search_box.send_keys("ChromeDriver")
#search_box.submit()
#time.sleep(5)
driver.quit()
