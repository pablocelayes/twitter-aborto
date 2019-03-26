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

HASHTAG = "hayotrocamino"

COLLECTION = DB["tweets_%s" % HASHTAG]

def load_terminos():
    with open('terminos_start_discurso1m.json') as f:
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
    i = 0        
    # for i in range(1,11):
    while True:
        i += 1
        print ("Round %04d %s" % (i, datetime.now().strftime("%d/%m: %H:%M")))

        terminos = load_terminos()
        # terminos = [HASHTAG]   

        TW.get_fresh_connection()
        print(TW.conn_.auth.consumer_key)

        listener = MyStreamListener(collection=COLLECTION, time_limit=60) 
        myStream = tweepy.Stream(auth=TW.conn_.auth, listener=listener)
        try:
            myStream.filter(languages=['es'], track=terminos)
        except Exception as e:
            print(e)
