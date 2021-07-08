#!C:\\Users\\kaach\\OneDrive\\Documents\\scraping\\Scripts\\python.exe

import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

top_product_image = []
top_product_name = []
top_product_url = []
mall_shops_image = []
mall_shops_url = []
mall_shops_promo_text = []
banner_name = []
banner_image = []
banner_url = []

result = {}

headers = {
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
             'Referer': 'https://shopee.com.my'
          }


def scrape_shopee_top_products():
    shopee_top_products_url = "https://shopee.com.my/api/v4/recommend/recommend?bundle=top_sold_product_microsite&limit=20&offset=0"
    r = requests.get(shopee_top_products_url, headers=headers).json()

    top_products = r['data']['sections'][0]['data']['top_product']

    for t in top_products:
        image = t['images'][0]
        top_product_image.append("https://cf.shopee.com.my/file/" + image)
        top_product_name.append(t['name'])
        key = t['key']
        top_product_url.append("https://shopee.com.my/top_products?catId={}".format(key))

    data = pd.DataFrame(zip(top_product_image, top_product_name, top_product_url)
                        , columns=['image', 'name', 'url'])
    top_product = data.to_json(orient="index")
    top_product = json.loads(top_product)

    result['shopee_top_products'] = top_product

def scrape_shopee_mall_shops():
    scrape_shopee_mall_shops_url = "https://shopee.com.my/api/v4/homepage/mall_shops?limit=23"
    r = requests.get(scrape_shopee_mall_shops_url,headers).json()

    mall_shops = r['data']['shops']

    for m in mall_shops:
        mall_shops_url.append(m['url'])
        mall_shops_image.append("https://cf.shopee.com.my/file/" + m['image'])
        if(m['promo_text']!=None):
            mall_shops_promo_text.append(m['promo_text'])
        else:
            mall_shops_promo_text.append("")
        

    data = pd.DataFrame(zip(mall_shops_url, mall_shops_image, mall_shops_promo_text)
                        , columns=['url', 'image', 'promo_text'])
    mall_shop = data.to_json(orient="index")
    mall_shop = json.loads(mall_shop)

    result['shopee_mall_shops'] = mall_shop

def scrape_lazada():
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
    browser = webdriver.Chrome(
        executable_path=r'C:\Users\kaach\OneDrive\Documents\scraping\Scraping_codes\chromedriver.exe', options=options)

    browser.get(lazada_url)
    browser.implicitly_wait(5)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    banner_containers = soup.findAll("div", class_='card-banner-slider-main-span')

    for banner in banner_containers:
        for link in banner.find_all('a'):
            #print("https:" + link.get('href'))
            banner_url.append("https:" + link.get('href'))
            for image in link.find_all('img'):
                try:
                    #print("https:" + image.get('src'))
                    banner_image.append("https:" + image.get('src'))
                except:
                    #print("https://" + image.get('data-ks-lazyload'))  #lazada use lazy loading for the following banner image
                    banner_image.append("https:" + image.get('data-ks-lazyload'))

                #print(image.get('alt'))
                banner_name.append(image.get('alt'))

    data = pd.DataFrame(zip(banner_url, banner_image, banner_name)
                        , columns=['url', 'image', 'name'])
    banners = data.to_json(orient="index")
    banners = json.loads(banners)

    result['lazada_banners'] = banners
    browser.quit()

if __name__== '__main__':
    scrape_shopee_top_products()
    scrape_shopee_mall_shops()
    scrape_lazada()
    print(json.dumps(result, indent=4))