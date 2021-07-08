#!C:\\Users\\kaach\\OneDrive\\Documents\\shopmate\\Scripts\\python.exe

import requests
import json
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from fake_useragent import UserAgent
import time
import sys

import re
import emoji
from googletrans import Translator
from textblob import TextBlob
import langid


import keras
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer

import numpy as np
import pandas as pd

# import tensorflow as tf



def scrape_reviews(item_id,shop_id, review_count, platform):
    # configuration for shopee
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Referer': 'https://shopee.com.my'
    }
    if(platform=="Shopee"):
        scraped_review_count = 1000 if int(review_count) >=1000 else int(review_count)
        # print("scrape review count: {}".format(scraped_review_count))

        offset = 0
        limit = 50      #shopee allow scraping up to 50 each time
        scraped_times = divmod(scraped_review_count,limit)[0]
        # print("scrape times: {}".format(scraped_times))
        remaining_scraped_times = divmod(scraped_review_count,limit)[1]
        # print("remaining: {}".format(remaining_scraped_times))

        review_list = []

        for i in range(0,scraped_times):
            review_url = "https://shopee.com.my/api/v2/item/get_ratings?filter=0&flag=1&itemid={}&limit={}&offset={}&shopid={}&type=0".format(item_id, limit,offset, shop_id)
            review_response = requests.get(review_url, headers=headers).json()

            for review in review_response['data']['ratings']:
                if review['comment'] != None and review['comment'] != "":
                    review_list.append(review['comment'])
            offset = offset + 50

        if(remaining_scraped_times>0):
            review_url = "https://shopee.com.my/api/v2/item/get_ratings?filter=0&flag=1&itemid={}&limit={}&offset={}&shopid={}&type=0".format(item_id, limit,offset, shop_id)
            review_response = requests.get(review_url, headers=headers).json()

            for review in review_response['data']['ratings']:
                if review['comment'] != None and review['comment'] != "":
                    review_list.append(review['comment'])


        #print("review list length: {}".format(len(review_list)))
        #print(review_list)
        # return review_list
        return np.array(review_list)

    else:

        #configuration for selenium browser
        options = webdriver.ChromeOptions()
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument("--incognito")
        options.add_argument('--disable-blink-features=AutomationControlled') #to remove the navigator flag
        ua = UserAgent()
        userAgent = ua.random
        options.add_argument(f'user-agent={userAgent}')
        browser = webdriver.Chrome(executable_path= r'C:\Users\kaach\OneDrive\Documents\scraping\Scraping_codes\chromedriver.exe', options= options)

        # browser.get(url)
        # browser.implicitly_wait(5)
        # page = browser.page_source
        # soup = BeautifulSoup(page,features="html.parser",parse_only=SoupStrainer('script'))
        # scripts = soup.find_all('script')
        #
        # for a in scripts:
        #     if a.string is not None:
        #         if 'window.__messages__' in a.string:  # for <script>, using script.string instead of script text for newer version of bs4
        #             jsonStr = a.string
        #             jsonStr = jsonStr.split("var __moduleData__ = ")[1]            #modified on 13/3/21 because the old one cannot worked
        #             jsonStr = jsonStr.rsplit("var __googleBot__ =")[0]
        #             jsonStr = jsonStr.rsplit(";",1)[0]
        #             print(jsonStr)
        #             jsonObj = json.loads(jsonStr)
        #             reviewCount = jsonObj['data']['root']['fields']['review']['ratings']['reviewCount']
        #             itemId = jsonObj['data']['root']['fields']['review']['params']['itemId']
        #             break
        #
        # print("scraped review count: {}".format(reviewCount))
    try:
        review_count = 1000 if int(review_count) >= 1000 else int(review_count)
        review_url = "https://my.lazada.com.my/pdp/review/getReviewList?itemId={}&pageSize={}&filter=0&sort=0&pageNo=1".format(item_id,review_count) #lazada limit 1000 reviews shown in 1 page
        browser.get(review_url)

        data=browser.find_element_by_tag_name("pre").text
        jsonObj = json.loads(data)

        review_list = []
        items = jsonObj['model']['items']

        for i in items:
            if i['reviewContent'] != None and i['reviewContent'] != "":
                review_list.append(i['reviewContent'])

        # print("review list count: {}".format(len(review_list)))
        # print(review_list)
        browser.quit()
        return np.array(review_list)
    except:
        return []


def preprocess_text(texts):
    preprocessed_texts = []
    for text in texts:
        text = text.lower() #lower the text
        emoji.demojize(text,delimiters=("","")) #convert emoji to text
        text = re.sub(r"\n","",text) # remove newline
        text = re.sub("(\w+\s)\\1{2,}","\\1 ",text)  #remove repeating words
        text = re.sub(r'([a-z])\1{2,}', r'\1\1', text) #remove repeating characters #gooooooooood
        text = re.sub(r'[^a-zA-Z_\s]','',str(text)) #remove punctuation and numbers
        text = re.sub(r'\b\w{20,}\b','',text) #remove super long words that cause noise to the prediction #goodgoodgoodgoodgood
        if(bool(re.match(r"\w+", text))): #only get the review with characters so that later does not confuse the language detector, because there is case where the review become whitespace after preprocessing
            preprocessed_texts.append(text)
    #print("length of preprocessed text: {}".format(len(preprocessed_texts)))
    # print(preprocessed_texts)
    return np.array(preprocessed_texts)

def remove_non_english_text(texts):
    english_reviews = []

    for text in texts:
        # print(text)
        # print(langid.classify(text))
        if(langid.classify(text)[0]=="en" or langid.classify(text)[0]=="ca"):       #decide to use langid for its fast and accurate about 3s to process 180 texts
            english_reviews.append(text)

    #print("length of eng reviews: {}".format(len(english_reviews)))
    # print(english_reviews)
    return np.array(english_reviews)

def tokenize(texts):
    dataset = pd.read_csv(r"C:\xampp\htdocs\shopmate_v1\python\sentiment_dataset.csv")
    data_to_list = dataset['review'].values.tolist()
    data = np.array(data_to_list)

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(data)

    sequence = tokenizer.texts_to_sequences(texts)
    pad_seq = pad_sequences(sequence, maxlen=200)
    return pad_seq

def predict(texts):
    best_model = keras.models.load_model(r"C:\xampp\htdocs\shopmate_v1\python\sentiment_best_model4.h5")
    prediction = best_model.predict(texts)
    sentiment = [1 if p>=0.5 else 0 for p in prediction]
    return np.array(sentiment)

def calculate_sentiment_score(sentiment):
    total_reviews = sentiment.size
    positive = np.count_nonzero(sentiment==1)
    negative = np.count_nonzero(sentiment==0)
    sentiment_score = round((positive/total_reviews)*5.0,1)
    return total_reviews, positive,negative,sentiment_score

# #url = "https://shopee.com.my/api/v2/item/get?itemid=6941407320&shopid=6970929"
# url = "https://shopee.com.my/api/v2/item/get?itemid=1663619414&shopid=98570405"  #more review
# url3 = "https://www.lazada.com.my/products/sandisk-ultra-micro-sd-memory-card-128gb-120mbs-a1-class-10-uhs-i-microsdxc-sdsqua4-no-adapter-i138936145-s158681861.html"
# platform = "Shopee"
# reviews_list = scrape_reviews(url,platform)
# preprocess_texts = preprocess_text(reviews_list)
# english_reviews = remove_non_english_text(preprocess_texts)
#
# if(english_reviews.size!=0):
#     pad_seq = tokenize(english_reviews)
#     sentiment = predict(pad_seq)
#     total_reviews, positive, negative, sentiment_score = calculate_sentiment_score(sentiment)
#     print(positive, negative, sentiment_score)
#     positive_review, negative_review =[],[]
#
#     review_sentiment = list(zip(english_reviews,sentiment))
#     for item in review_sentiment:
#         if(item[1]==1):
#             positive_review.append(item[0])
#         else:
#             negative_review.append(item[0])
#
#     result = {
#         "error": 0,
#         "total_review": total_reviews,
#         "positive_review_count": positive,
#         "positive_review": positive_review,
#         "negative_review_count": negative,
#         "negative_review": negative_review,
#         "sentiment_score": sentiment_score,
#     }
#     print(json.dumps(result))
#
# else:
#     print("no reviews")
#     result = {
#         "error": 1,
#         "error_msg": "No reviews"
#     }

if __name__ == '__main__':

    item_id = sys.argv[1]
    shop_id = sys.argv[2]
    review_count = sys.argv[3]
    platform = sys.argv[4]

    reviews_list = scrape_reviews(item_id,shop_id,review_count,platform)
    
    preprocess_texts = preprocess_text(reviews_list)
    english_reviews = remove_non_english_text(preprocess_texts)

    if (english_reviews.size != 0):
        pad_seq = tokenize(english_reviews)
        sentiment = predict(pad_seq)
        total_reviews, positive, negative, sentiment_score = calculate_sentiment_score(sentiment)
        # print(positive, negative, sentiment_score)
        positive_review, negative_review = [], []

        review_sentiment = list(zip(english_reviews, sentiment))
        for item in review_sentiment:
            if (item[1] == 1):
                positive_review.append(item[0])
            else:
                negative_review.append(item[0])

        result = {
            "error": False,
            "total_review": total_reviews,
            "positive_review_count": positive,
            "positive_review": positive_review,
            "negative_review_count": negative,
            "negative_review": negative_review,
            "sentiment_score": sentiment_score,
        }
        print(json.dumps(result))

    else:
        
        result = {
            "error": True,
            "error_msg": "No reviews"
        }
        print(json.dumps(result))


