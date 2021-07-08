#! C:\\Users\\kaach\\OneDrive\\Documents\\scraping\\Scripts\\python.exe

import requests
import sys
import json
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import time


###the argument list will be python file name, 1:productURL, 2:platform, 3:info that scrape, 4:variation(for price tracking, else null)

headers = {
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
             'Referer': 'https://shopee.com.my'
          }

#url = sys.argv[1]
url = "https://shopee.com.my/api/v2/item/get?itemid=6941407320&shopid=6970929" #for testing ---no variation
url2 = "https://shopee.com.my/api/v2/item/get?itemid=1629127248&shopid=73311046" #for testing ---got two variation



####start scrape --- price tracking
# r = requests.get(url2, headers = headers).json()
#
# # if there is no variation---null
# price = r['item']['price']/100000
# print(price)
#
# #if there is variation
# variation_chosen = "asli" ###for testing variation
# for variation in r['item']['models']:
#     if variation['name'].lower() == variation_chosen.lower():
#         price = variation['price'] / 100000
#         print(price)


#####start scraping the detailed information









##### start scraping the product review
r = requests.get(url2, headers = headers).json()
review_count = r['item']['item_rating']['rating_count'][0]
item_id = r['item']['itemid']
shop_id = r['item']['shopid']
review_url = "https://shopee.com.my/api/v2/item/get_ratings?filter=0&flag=1&itemid={}&limit={}&offset=0&shopid={}&type=0".format(item_id, review_count, shop_id)
review_response = requests.get(review_url, headers = headers).json()

review_list = []
for review in review_response['data']['ratings']:
    if review['comment'] != None and review['comment'] != "":
        review_list.append(review['comment'])

print(review_list)      #see whether need to serialize into json or not
if len(review_list):
    print("No reviews.")

print("test")



###for scraping lazada part
#for testing lazada , got variation
url3 = "https://www.lazada.com.my/products/sandisk-ultra-micro-sd-memory-card-128gb-120mbs-a1-class-10-uhs-i-microsdxc-sdsqua4-no-adapter-i138936145-s158681861.html"
#this is without reviews
#url3 = "https://www.lazada.com.my/products/official-adidas_men-shoes-zx750-running-sneaker-shoes-fashion-sport-shoes-blue-hot-global-sales-i1772312661-s6948630789.html?spm=a2o4k.searchlist.list.7.68cf7ac6rTLGar&search=1"

#apply to all lazada scraping
options = webdriver.ChromeOptions()
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--disable-blink-features=AutomationControlled') #to remove the navigator flag
ua = UserAgent()
userAgent = ua.random
options.add_argument(f'user-agent={userAgent}')
browser = webdriver.Chrome(executable_path= 'C:\xampp\htdocs\shopmate_v1\python\chromedriver.exe', options= options)

browser.get(url3)
browser.implicitly_wait(5)



##### scrape lazada price tracking
# a = '16GB'  #variation-chosen
# try:
#     locator = browser.find_element_by_xpath("//span[@class='sku-variable-name-selected' and @title='" + a + "']") #if the variation is selected currently
# except:
#     locator = browser.find_element_by_xpath("//span[@class='sku-variable-name' and @title='" + a + "']")
#     locator.click()
#     browser.get(browser.current_url)


# return a list of variation
# variation_list = []
# skuInfo = browser.find_elements_by_class_name("sku-variable-name-text")
# for s in skuInfo:
#     variation_list.append(s.text)
# print(variation_list)


# page = browser.page_source
#
# soup = BeautifulSoup(page,features="html.parser",parse_only=SoupStrainer('script'))
# scripts = soup.find_all('script')
#
# for a in scripts:
#     if a.string is not None:
#         if 'app.run(' in a.string:  # for <script>, using script.string instead of script text for newer version of bs4
#             jsonStr = a.string
#             jsonStr = jsonStr.split("app.run(")[1]
#             jsonStr = jsonStr.split(", function")[0]
#             jsonObj = json.loads(jsonStr)
#             price = jsonObj['data']['root']['fields']['skuInfos']['0']['price']['salePrice']['value']
#             print(price)
#             break
#
# browser.quit()





# ##### scrape lazada review---write basic, then add loop by finding the page number total count
# page = browser.page_source
#
# soup = BeautifulSoup(page,features="html.parser",parse_only=SoupStrainer('script'))
# scripts = soup.find_all('script')
#
# for a in scripts:
#     if a.string is not None:
#         if 'app.run(' in a.string:  # for <script>, using script.string instead of script text for newer version of bs4
#             jsonStr = a.string
#             jsonStr = jsonStr.split("app.run(")[1]
#             jsonStr = jsonStr.split(", function")[0]
#             jsonObj = json.loads(jsonStr)
#             totalItems = jsonObj['data']['root']['fields']['review']['paging']['totalItems']
#             itemId = jsonObj['data']['root']['fields']['review']['params']['itemId']
#             break
#
# review_url = "https://my.lazada.com.my/pdp/review/getReviewList?itemId={}&pageSize={}&filter=0&sort=0&pageNo=1".format(itemId,totalItems) #lazada limit 1000 reviews shown in 1 page
# browser.get(review_url)
#
# data=browser.find_element_by_tag_name("pre").text
# jsonObj = json.loads(data)
#
# review_list = []
# items = jsonObj['model']['items']
#
# for i in items:
#     if i['reviewContent'] != None and i['reviewContent'] != "":
#         review_list.append(i['reviewContent'])
#
# print(review_list)
# browser.quit()