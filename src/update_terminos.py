# coding: utf-8
import json
import time
from datetime import date, datetime, timedelta
from fetch_tweets_agosto_streaming import load_terminos
from pymongo import MongoClient
import json
from collections import Counter

MONGO_HOST= 'mongodb://localhost/twitterdata'

DB = MongoClient(MONGO_HOST).twitterdata

COLLECTION = DB.abortolegal_agosto

HT_THRESHOLD = 0.01  #determina cuales hashtags se usaran para bajar y cuales no a partir de su frecuencia.

HT_UPDATE_INTERVAL = 60 * 60
# HT_UPDATE_INTERVAL = 0

HT_UPDATE_WINDOW_HOURS = 2

def update_terminos():
    start = time.time()
    hashtags_counts = Counter()
    limit =  datetime.now() - timedelta(hours=HT_UPDATE_WINDOW_HOURS)
    n_tweets = 0
    for t in COLLECTION.find():
        str_dt = t['created_at']
        str_dt = str_dt[:-11] + str_dt[-5:]
        created = datetime.strptime(str_dt, "%a %b %d %H:%M:%S %Y")
        if created < limit:
            continue

        n_tweets += 1
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


    print "Actualización de hashtags sobre %d tweets de las últimas %d horas" % (n_tweets, HT_UPDATE_WINDOW_HOURS)
    print "Tardamos %.1f segs" % (time.time() - start)    
    return terminos


if __name__ == '__main__':
    last_hashtag_update = time.time()
    i = 0        
    while True:
        time.sleep(5)
        if time.time() - last_hashtag_update > HT_UPDATE_INTERVAL:
            i += 1
            print "Round %04d %s" % (i, datetime.now().strftime("%d/%m: %H:%M"))    

            print "Actualizando lista de hashtags"
            update_terminos()
            terminos = load_terminos()
            print terminos
            last_hashtag_update = time.time()
