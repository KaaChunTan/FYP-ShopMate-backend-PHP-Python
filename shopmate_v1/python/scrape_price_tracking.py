#!C:\\Users\\kaach\\OneDrive\\Documents\\scraping\\Scripts\\python.exe
import sys

import requests
import json

from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from fake_useragent import UserAgent


headers = {
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
             'Referer': 'https://shopee.com.my'
          }


def scrape_shopee_price_tracking(url,variation):

    r = requests.get(url, headers = headers).json()

    price = "None" #if there is no variation matches due to some reason, return string None
                    #when compare the price in php, make sure the string is not None then only start comparing

    if(variation == ""):
        price = "%.2f" % round(r['item']['price'] / 100000, 2)

    else:
        for variant in r['item']['models']:
            if variant['name'].lower() == variation.lower():
                price = "%.2f" % round(variant['price'] / 100000, 2)

    print(price)



def scrape_lazada_price_tracking(url,variation):

    price = "None" #default value for price

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

    browser.get(url)
    browser.implicitly_wait(5)

#add try here
    page = browser.page_source

    soup = BeautifulSoup(page,features="html.parser",parse_only=SoupStrainer('script'))
    scripts = soup.find_all('script')

    for a in scripts:
        if a.string is not None:
            if '__moduleData__' in a.string:  # for <script>, using script.string instead of script text for newer version of bs4
                jsonStr = a.string
                jsonStr = jsonStr.split("var __moduleData__ = ")[1]
                jsonStr = jsonStr.rsplit("var __googleBot__ =")[0]
                jsonStr = jsonStr.rsplit(";", 1)[0]
                jsonObj = json.loads(jsonStr)
                if(variation==""):
                    price = jsonObj['data']['root']['fields']['skuInfos']['0']['price']['salePrice']['value']
                    price = "%.2f" % price
                    break
                else:
                    ##getting the variation list
                    sku_vid_list = []
                    skuId = ""
                    skuValues_array = []
                    skus = []
                    match_vid_list = []

                    try:
                        skuValues_array = jsonObj['data']['root']['fields']['productOption']['skuBase'][
                            'properties']  # return an array if exist
                        skus = jsonObj['data']['root']['fields']['productOption']['skuBase']['skus']  # return array

                    except:
                        pass

                    finally:
                        skuInfos = jsonObj['data']['root']['fields']['skuInfos']

                    if (len(skus) > 1):  # if more than 1 then only got variation list
                        for sku in skuValues_array:

                            pid = sku['pid']
                            values = sku['values']  # return an array
                            for v in values:  # get all the variation value
                                name = v['name']
                                vid = v['vid']
                                sku_dict = {
                                    "pid": pid,
                                    "name": name,
                                    "vid": vid
                                }
                                sku_vid_list.append(sku_dict)

                        #see which name is match with the variation, and thus get the vid for getting the skuId later
                        for sku_vid in sku_vid_list:
                            if(sku_vid['name'] in variation):
                                match_vid_list.append(sku_vid['vid'])

                        #use the vid to get the skuId
                        for sku in skus:
                            found = False
                            #must match every vid in the list
                            for match in match_vid_list:
                                found = False
                                if(match in sku['propPath']):
                                    found = True
                            if (found):
                                skuId = sku['skuId']

                        price = skuInfos[""+skuId+""]['price']['salePrice']['value']
                        price = "%.2f" % price


    print(price)
    browser.quit()


if __name__== '__main__':
    url = sys.argv[1]
    platform = sys.argv[2]
    try:
        variation = sys.argv[3]
    except:
        variation = ""
    
    if(platform == "Shopee"):
        scrape_shopee_price_tracking(url,variation)
    else:
        scrape_lazada_price_tracking(url,variation)

    # url = "https://shopee.com.my/api/v2/item/get?itemid=1629127248&shopid=73311046"
    # variation = "Asli,Old packing"

    # url = "https://shopee.com.my/api/v2/item/get?itemid=1831273291&shopid=12277135"
    # variation = "Enfa3(ORI)oldpack3.6"

    # url = "https://shopee.com.my/api/v2/item/get?itemid=1631022279&shopid=94327525"
    # variation = ""

    # url = "https://www.lazada.com.my/products/lazchoice-eliminates-999-bacteriaprotex-icy-cool-antibacterial-shower-gel-900ml-i437843228-s642793666.html?spm=a2o4k.searchlist.list.1.44c475e8YTevQj&search=1"
    # variation = ""

    # url = "https://www.lazada.com.my/products/sandisk-ultra-dual-drive-luxe-32gb-64gb-128gb-256gb-512gb-1tb-usb-type-c-otg-i956748270-s6530934758.html?spm=a2o4k.searchList.list.1.619b10beT87BDk&search=1"
    # variation = "512GB"

    # scrape_shopee_price_tracking(url,variation)
    #scrape_lazada_price_tracking(url, variation)