# coding: utf-8
from twitter_api import API_HANDLER as TW
import tweepy
from datetime import datetime
import json
from datetime import date, timedelta

from pymongo import MongoClient

MONGO_HOST= 'mongodb://localhost/twitterdata'

def fetch_tweets(db, hashtags, posicion, desde, hasta):
    coll = db.abortolegal
    query = ' OR '.join(hashtags[posicion])
    count = 0
    for status in tweepy.Cursor(TW.conn_.search,
                           q=query,
                           tweet_mode='extended',
                           count=100,
                           result_type="recent",
                           since=desde,
                           until=hasta, 
                           lang="es").items():
        data = status._json
        data['posicion'] = posicion

        if not coll.find({'id': data['id']}).count():
            coll.insert(data)

        count += 1
        if count % 500 == 0:
            print(count)
        if count % 10000 == 0:
            TW.get_fresh_connection()

hashtags = {
    "si": ["#abortolegal", "#abortolegalya", "#abortolegalesvida",
            "#AbortoLegalEsSalud", "#novotencontralasmujeres",
            "#quesealey", "#queelabortosealey",
            "#AbortoSeraLey" # desde 13/6
    ],
    "no": ["#elijamoslas2vidas", "#noalaborto", "#noalabortolegal",
           "#salvemoslasdosvidas", "#SalvemosLas2Vidas", "#ArgentinaEsProvida",
           "#CuidemoslasDosVidas", "#AbortoLegalEsMuerte",
           "#NoAlAbortoEnArgentina" # desde 13/6
    ]
}

if __name__ == '__main__':
    hasta = date.today().strftime("%Y-%m-%d")
    desde = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    client = MongoClient(MONGO_HOST)

    db = client.twitterdata

    hashtags = {
        "si": ["#abortolegal", "#abortolegalya", "#abortolegalesvida",
                "#AbortoLegalEsSalud", "#novotencontralasmujeres",
                "#quesealey", "#queelabortosealey",
                "#AbortoSeraLey" # desde 13/6
        ],
        "no": ["#elijamoslas2vidas", "#noalaborto", "#noalabortolegal",
               "#salvemoslasdosvidas", "#SalvemosLas2Vidas", "#ArgentinaEsProvida",
               "#CuidemoslasDosVidas", "#AbortoLegalEsMuerte",
               "#NoAlAbortoEnArgentina" # desde 13/6
        ]
    }

    TW.get_fresh_connection()
    fetch_tweets(db, hashtags, "si", desde, hasta)

    TW.get_fresh_connection()
    fetch_tweets(db, hashtags, "no", desde, hasta)
