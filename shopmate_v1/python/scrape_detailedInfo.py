#!C:\\Users\\kaach\\OneDrive\\Documents\\shopmate\\Scripts\\python.exe

import requests
import json
import sys

from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from fake_useragent import UserAgent

def scrape_shopee_detailed_info(url):
    # configuration for shopee
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Referer': 'https://shopee.com.my'
    }

    r = requests.get(url,headers=headers).json()

    item_image = []
    for i in r['item']['images']:
        item_image.append("https://cf.shopee.com.my/file/" + i)
    item_name = r['item']['name']
    item_description = r['item']['description']

    if(r['item']['price_before_discount']==0):
        item_ori_price = 0
    else:
        item_ori_price = "RM%.2f" % round(r['item']['price_before_discount'] / 100000,2) # item price is based on the price of the first variation, so the default is the first variation

    item_disc_price = "RM%.2f" % round(r['item']['price']/100000,2)

    variation_list = []
    if(len(r['item']['models'])>1): # if more than 1, only get the variation list
        for v in r['item']['models']:
            variation_name = v['name']
            if (v['price_before_discount'] == 0):
                variation_ori_price = 0
            else:
                variation_ori_price = "RM%.2f" % round(v['price_before_discount'] / 100000, 2)
            variation_disc_price = "RM%.2f" % round(v['price']/100000,2)
            variation_list.append((variation_name, variation_ori_price, variation_disc_price))


    review_count = r['item']['item_rating']['rcount_with_context']
    number_sold = r['item']['historical_sold']
    shop_location = r['item']['shop_location']

    item_id = r['item']['itemid']
    shop_id = r['item']['shopid']
    product_url = "https://shopee.com.my/product/{}/{}".format(shop_id,item_id)

    result = {
        "images" : item_image,
        "name" : item_name,
        "description" : item_description,
        "original_price" :  item_ori_price, # if none, is 0
        "discounted_price" : item_disc_price,
        "variation" : variation_list,
        "review_count" : review_count,
        "number_sold" : number_sold,
        "location" : shop_location,
        "item_id" : item_id,
        "shop_id" : shop_id,
        "product_url" : product_url
    }

    print(json.dumps(result))

def scrape_lazada_detailed_info(url):

    #configuration for selenium browser
    options = webdriver.ChromeOptions()
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument("--incognito")
    options.add_argument('--disable-blink-features=AutomationControlled')  # to remove the navigator flag
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    browser = webdriver.Chrome(executable_path=r'C:\Users\kaach\OneDrive\Documents\scraping\Scraping_codes\chromedriver.exe', options=options)


    try:
        browser.get(url)
        browser.implicitly_wait(5)
        page = browser.page_source
        #print(page)
        soup = BeautifulSoup(page, features="html.parser",parse_only=SoupStrainer('script'))
        scripts = soup.find_all('script')

        for a in scripts:
            if a.string is not None:
                if '__moduleData__' in a.string:  # for <script>, using script.string instead of script text for newer version of bs4
                    #print(a.string)
                    jsonStr = a.string
                    jsonStr = jsonStr.split("var __moduleData__ = ")[1]
                    jsonStr = jsonStr.rsplit("var __googleBot__ =")[0]
                    jsonStr = jsonStr.rsplit(";", 1)[0]
                    #print(jsonStr)
                    jsonObj = json.loads(jsonStr)

                    item_image = []
                    skuGalleries = jsonObj['data']['root']['fields']['skuGalleries']["0"]
                    for gallery in skuGalleries:
                        if(gallery["type"]=="img"):
                            item_image.append("http:"+ gallery['src'])

                    item_name = jsonObj['data']['root']['fields']['product']['title']

                    product_url = jsonObj['data']['root']['fields']['product']['link']
                    item_id = jsonObj['data']['root']['fields']['primaryKey']['itemId']
                    review_count = jsonObj['data']['root']['fields']['review']['ratings']['reviewCount']
                    shop_id = jsonObj['data']['root']['fields']['seller']['shopId']
                    # print(review_count)

                    ##getting the variation list
                    variation_name_list = []
                    sku_vid_list = []
                    skuId_list = []
                    variation_ori_price_list = []
                    variation_disc_price_list = []
                    skuValues_array = []
                    skus = []

                    #modified on 17/4 because of the more than one category

                    try:
                        skuValues_array = jsonObj['data']['root']['fields']['productOption']['skuBase']['properties']  # return an array if exist
                        skus = jsonObj['data']['root']['fields']['productOption']['skuBase']['skus'] #return array

                    except:
                        skuValues = {} #apply to not exist

                    finally:
                        skuInfos = jsonObj['data']['root']['fields']['skuInfos']

                    if(len(skus)>1): #if more than 1 then only got variation list
                        for sku in skuValues_array:

                            pid = sku['pid']
                            values = sku['values'] #return an array
                            for v in values: #get all the variation value
                                name = v['name']
                                vid = v['vid']
                                sku_dict = {
                                    "pid": pid,
                                    "name": name,
                                    "vid": vid
                                }
                                sku_vid_list.append(sku_dict)


                        # print(variation_name_list)

                        # print(skuId_list)

                        for sku in skus:
                            variation_name_temp = ""
                            for sku_vid in sku_vid_list:
                                if sku_vid['pid'] in sku['propPath'] and sku_vid['vid'] in sku['propPath']:
                                    variation_name_temp = variation_name_temp + sku_vid["name"] + ", " #append variation name when there is more than one category


                            skuId_list.append(sku['skuId'])
                            variation_name_temp = variation_name_temp[:-2]
                            variation_name_list.append(variation_name_temp)

                        for skuId in skuId_list:
                            try:
                                variation_ori_price_list.append(skuInfos[""+skuId+""]['price']['originalPrice']['text'])  #use variable as key
                            except:
                                variation_ori_price_list.append("0")
                            variation_disc_price_list.append(skuInfos[""+skuId+""]['price']['salePrice']['text'])

                        variation_list = list(zip(variation_name_list,variation_ori_price_list,variation_disc_price_list))
                        # print(variation_list)

                    else:
                        skuId_list.append(skuInfos["0"]["skuId"])  #this is to get the only one skuId for extracting description later
                        variation_list = []

                    price = jsonObj['data']['root']['fields']['skuInfos']["0"]['price']
                    try: #because the tag is absent if there is no original price
                        item_ori_price = price['originalPrice']['text']
                    except:
                        item_ori_price = 0

                    item_disc_price = price['salePrice']['text']

                    #has two conditions: one is normal page and one is in mobile mode
                    try:
                        description = jsonObj['data']['root']['fields']['specifications']["" + skuId_list[0] + ""]['features']  # return a dict object
                        item_description = ""
                        for k, v in description.items():  # get the key and value of the dict object
                            temp = k + ": " + v + "\n"
                            item_description = item_description + temp
                    except:
                        try:
                            description = jsonObj['data']['root']['fields']['specifications']["" + skuId_list[0] + ""]['popItems']  # return an array of dict object
                            item_description = ""
                            for desc in description:
                                k = desc["title"]
                                v = desc["content"]
                                temp = k + ": " + v + "\n"
                                item_description = item_description + temp

                        except:
                            item_description = ""

                    result = {
                        "images": item_image,
                        "name": item_name,
                        "description": item_description,
                        "original_price": item_ori_price,  # if none, is 0
                        "discounted_price": item_disc_price,
                        "variation": variation_list,
                        "review_count": review_count,
                        "item_id": item_id,
                        "shop_id": shop_id,
                        "product_url": product_url
                    }

                    print(json.dumps(result))

                    break


        browser.quit()
    except:
        pass
 

if __name__ == '__main__':
    url = sys.argv[1]
    #url = "https://www.lazada.com.my/products/sandisk-ultra-micro-sd-memory-card-128gb-120mbs-a1-class-10-uhs-i-microsdxc-sdsqua4-no-adapter-i138936145-s158681861.html"

    platform = sys.argv[2]

    if (platform == "Shopee"):
        scrape_shopee_detailed_info(url)
    else:
        scrape_lazada_detailed_info(url)


    # url = "https://shopee.com.my/api/v2/item/get?itemid=1629127248&shopid=73311046"
    # url2 = "https://www.lazada.com.my/products/local-stockkingston-sd-card-micro-sd-card-memory-card-class-10-80mbs-64g256gb128gb512gb-tf-card-for-cctv-dashcam-4-i1641612345-s5665132640.html?"
    # url2 = "https://www.lazada.com.my/products/sandisk-ultra-micro-sd-memory-card-128gb-120mbs-a1-class-10-uhs-i-microsdxc-sdsqua4-no-adapter-i138936145-s158681861.html"
    # scrape_shopee_detailed_info(url)
    # scrape_lazada_detailed_info(url2)