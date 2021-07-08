#!C:\\Users\\kaach\\OneDrive\\Documents\\scraping\\Scripts\\python.exe

from bs4 import BeautifulSoup, SoupStrainer
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import requests
import sys
import re
import time
import random
import statistics

name_list = []
productUrl_list = []
scrapeUrl_list = []
image_list = []
price_list = []
price_max_list = []  # it will be same as the price if there is no price range
price_before_discount_list = []
discount_list = []
rating_list = []
review_count_list = []
location_list = []
platform_list = []
shop_id_list = []
item_id_list = []
variation_list = []  # use to store variation list for that particular item
search_result_variation_price = {}  # use to store unique variation price
shopee_variation_statistics = {}  # use to store variation statistics to return to user
all_variation_statistics = {}
lazada_temp_price_list = []
lazada_variation_statistics = {}

# keyword_search = 'protex shower'
keyword_search = sys.argv[1]

# scrape from Shopee API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Referer': 'https://shopee.com.my/search?keyword={}'.format(keyword_search)
}

# shopee_url = 'https://shopee.com.my/api/v2/search_items/?by=relevancy&keyword={}&limit=15&newest=0&order=desc&page_type=search&version=2'.format(
#     keyword_search)  # this is old api

shopee_url = "https://shopee.com.my/api/v4/search/search_items?by=relevancy&keyword={}&limit=15&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2".format\
    (keyword_search) #this is latest api #code updated on 6/6/2021

r = requests.get(shopee_url, headers=headers).json()

for items in r['items']:

    item = items['item_basic'] #updated on 6/6/2021
                            #add one more branch named item_basic

    if all(x.lower() in item['name'].lower() for x in keyword_search.split()):  # to clean Shopee poor search result
        name_list.append(item['name'])
        scrapeUrl_list.append(
            "https://shopee.com.my/api/v2/item/get?itemid={}&shopid={}".format(item['itemid'], item['shopid']))
        productUrl_list.append("https://shopee.com.my/product/{}/{}".format(item['shopid'], item['itemid']))
        image_list.append("https://cf.shopee.com.my/file/" + item['image'])
        price_list.append("RM%.2f" % (item['price'] / 100000))
        price_max_list.append("RM%.2f" % (item['price_max'] / 100000))
        if item['price_before_discount'] != 0:
            price_before_discount_list.append("RM%.2f" % (item['price_before_discount'] / 100000))
        else:
            price_before_discount_list.append('null')
        if item['discount'] != None:
            discount_list.append("-" + item['discount'])
        else:
            discount_list.append("null")
        rating_list.append(str(item['item_rating']['rating_star']))
        review_count_list.append(str(item['item_rating']['rcount_with_context']))
        shop_id_list.append(str(item['shopid']))
        item_id_list.append(str(item['itemid']))
        location_list.append(item['shop_location'])
        platform_list.append('Shopee')

##end of scrape from Shopee API


##start scraping for variation for all the 10 items
for url in scrapeUrl_list:
    r = requests.get(url, headers=headers).json()
    item_variation_list = []  # use to store variation list
    if (len(r['item']['models']) > 1):  # if more than 1, only get the variation list
        for v in r['item']['models']:
            variation_name = v['name']
            variation_disc_price = "RM%.2f" % round(v['price'] / 100000, 2)
            item_variation_list.append((variation_name, variation_disc_price))

            # this is to save into the dict for later calculating the statistics (unique variation and its prices)
            if variation_name in search_result_variation_price.keys():
                search_result_variation_price["" + variation_name + ""].append(variation_disc_price)
            else:
                search_result_variation_price["" + variation_name + ""] = [variation_disc_price]

        variation_list.append(item_variation_list)  # this is for later return json
    else:
        variation_list.append([])
    time.sleep(1)
##end of scraping for variation for all the 10 items


##filter out those variation with one price
##calculate variation statistics for items in Shopee
variation_for_statistics_calc = {}

for name in search_result_variation_price.keys():
    if len(search_result_variation_price["" + name + ""]) > 2:
        variation_for_statistics_calc["" + name + ""] = search_result_variation_price["" + name + ""]

# print(variation_for_statistics_calc)


if len(variation_for_statistics_calc) > 0:
    for name in variation_for_statistics_calc.keys():
        temp = variation_for_statistics_calc["" + name + ""]
        temp_price_list = []
        temp_stat = {}
        for price in temp:
            temp_price_list.append(float(price.replace('RM', '')))

        temp_stat['median'] = round(statistics.median(temp_price_list), 2)
        temp_stat['min'] = min(temp_price_list)
        temp_stat['max'] = max(temp_price_list)

        shopee_variation_statistics["" + name + ""] = temp_stat

else:
    temp_price_list = []
    temp_stat = {}
    for price in price_list:
        temp_price_list.append(float(price.replace('RM', '')))

    temp_stat['median'] = round(statistics.median(temp_price_list), 2)
    temp_stat['min'] = min(temp_price_list)
    temp_stat['max'] = max(temp_price_list)
    shopee_variation_statistics["None"] = temp_stat



# scrape Lazada using Selenium webdriver
try:
    lazada_url = 'https://www.lazada.com.my'

    options = webdriver.ChromeOptions()
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument("--incognito")
    options.add_argument('--disable-blink-features=AutomationControlled')  # to remove the navigator flag
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    browser = webdriver.Chrome(executable_path=r'C:\xampp\htdocs\shopmate_v1\python\chromedriver.exe', options=options)

    browser.get(lazada_url)
    browser.implicitly_wait(5)

    search_bar = browser.find_element_by_id('q')
    search_bar.send_keys(keyword_search)
    search_bar.send_keys(Keys.ENTER)

    # get the page source and use bs4 to parse the content
    page = browser.page_source

    soup = BeautifulSoup(page, features="html.parser", parse_only=SoupStrainer('script'))
    scripts = soup.find_all('script')

    for a in scripts:
        if a.string is not None:
            if 'window.pageData=' in a.string or 'window.pageData =' in a.string:  # for <script>, using script.string instead of script text for newer version of bs4
                # updated on 14/5 because the syntax 'window.pageData=' changed
                jsonStr = a.string
                jsonStr = jsonStr.split("window.pageData = ")[1]  # changed on 14/5
                jsonStr = jsonStr.strip().strip(";")  # remove all the whitespaces and newline in the end and ; symbol
                jsonObj = json.loads(jsonStr)
                products = jsonObj['mods']['listItems']
                counter = 0
                for item in products:
                    if counter < 10:  # only get first 10 best match items
                        name_list.append(item['name'])
                        productUrl_list.append("https://" + item['productUrl'].strip('/'))
                        scrapeUrl_list.append("https://" + item['productUrl'].strip('/'))
                        image_list.append(item['image'])
                        try:
                            price_before_discount_list.append(item['originalPriceShow'])
                        except:
                            price_before_discount_list.append('null')
                        try:
                            discount_list.append(item['discount'])
                        except:
                            discount_list.append('null')
                        price_list.append(item['priceShow'])
                        lazada_temp_price_list.append(item['priceShow'])
                        price_max_list.append(item['priceShow'])  # for lazada, this is always same as the price
                        rating_list.append(item['ratingScore'])
                        if (item['review'] != ""):
                            review_count_list.append(item['review'])
                        else:
                            review_count_list.append("0")

                        location_list.append(item['location'])
                        platform_list.append('Lazada')
                        shop_id = item['clickTrace']
                        shop_id = re.sub(r'(.+)shop_id:(\d+)', "\\2", shop_id)
                        shop_id_list.append(shop_id)
                        item_id_list.append(item['itemId'])
                        variation_list.append([])
                        counter = counter + 1
                break
    browser.quit()

    # calculate statistics for lazada price
    temp_price_list = []
    temp_stat = {}
    for price in lazada_temp_price_list:
        temp_price_list.append(float(price.replace('RM', '')))

    temp_stat['median'] = round(statistics.median(temp_price_list), 2)
    temp_stat['min'] = min(temp_price_list)
    temp_stat['max'] = max(temp_price_list)
    lazada_variation_statistics["None"] = temp_stat
except:
    pass

# end of scrape Lazada using Selenium webdriver

# calculate statistics for all price
temp_price_list = []
temp_stat = {}
for price in price_list:
    temp_price_list.append(float(price.replace('RM', '')))

temp_stat['median'] = round(statistics.median(temp_price_list), 2)
temp_stat['min'] = min(temp_price_list)
temp_stat['max'] = max(temp_price_list)
all_variation_statistics["None"] = temp_stat


# store scrape data into the dataframe and then parse into json format
product_info = pd.DataFrame(
    zip(name_list, productUrl_list, scrapeUrl_list, image_list, price_list, price_max_list, price_before_discount_list,
        discount_list, rating_list, review_count_list, location_list, item_id_list, shop_id_list, platform_list,
        variation_list)
    , columns=['name', 'productUrl', 'scrapeUrl', 'image', 'price', 'price_max', 'price_before_discount', 'discount',
               'rating', 'review_count', 'location', 'item_id', 'shop_id', 'platform', 'variation_list'])

result = product_info.to_json(orient="index")
parsed = json.loads(result)

result_json = {}
result_json['items'] = parsed
result_json['all_statistics'] = all_variation_statistics
result_json['shopee_statistics'] = shopee_variation_statistics
result_json['lazada_statistics'] = lazada_variation_statistics

print(json.dumps(result_json, indent=4))



