# coding: utf-8
import json
import time
from datetime import date, datetime, timedelta

import tweepy
from pymongo import MongoClient
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
from twitter_api_streaming import API_HANDLER as TW
from collections import Counter

MONGO_HOST= 'mongodb://localhost/twitterdata'

DB = MongoClient(MONGO_HOST).twitterdata

COLLECTION = DB.abortolegal_agosto

HT_THRESHOLD = 0.01  #determina cuales hashtags se usaran para bajar y cuales no a partir de su frecuencia.

HT_UPDATE_INTERVAL = 60 * 60
# HT_UPDATE_INTERVAL = 0

def update_terminos():
    hashtags_counts = Counter()
    for t in COLLECTION.find():
        if "retweeted_status" in t:
            t = t["retweeted_status"]
            if "extended_tweet" in t:
               t = t["extended_tweet"]
        if "entities" in t:
            for ht in t["entities"]["hashtags"]:
                hashtags_counts[ht['text']] += 1
    
    n_hashtags = sum(hashtags_counts.values())

    terminos = [t for t, c in hashtags_counts.items() if c * (1.0 / n_hashtags) > HT_THRESHOLD]

    with open('terminos.json','w') as f:
        json.dump(terminos,f,indent=2)

    return terminos

def load_terminos():
    with open('terminos_start.json') as f:
        terminos = json.load(f)
    
    try:
        with open('terminos.json') as f:
            return list(set(terminos + json.load(f)))
    except Exception as e:
        return terminos

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, collection, time_limit=60):
        self.start_time = time.time()
        self.limit = time_limit
        self.coll = collection
        super(MyStreamListener, self).__init__()

    def on_data(self, data):
        data = json.loads(data)
        if not self.coll.find({'id': data['id']}).count():
            self.coll.insert(data)
            return True
        else:
            return False

    def on_status(self, status):
        if (time.time() - self.start_time) >= self.limit:
            print('time is over')
            return False

    def on_error(self, status):
        if (time.time() - self.start_time) >= self.limit:
            print('time is over')
            return False
        else:
            print(status)
            return True


if __name__ == '__main__':
    last_hashtag_update = time.time()
    terminos = load_terminos()

    i = 0        
    # for i in range(1,11):
    while True:
        i += 1
        print "Round %04d %s" % (i, datetime.now().strftime("%d/%m: %H:%M"))    

        if time.time() - last_hashtag_update > HT_UPDATE_INTERVAL:
            print "Actualizando lista de hashtags"
            update_terminos()
            terminos = load_terminos()    
            print terminos
            last_hashtag_update = time.time()

        TW.get_fresh_connection()
        print(TW.conn_.auth.consumer_key)

        listener = MyStreamListener(collection=COLLECTION, time_limit=60) 
        myStream = tweepy.Stream(auth=TW.conn_.auth, listener=listener)
        myStream.filter(languages=['es'], track=terminos)
