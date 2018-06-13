#!/bin/bash
source /home/pablo/.virtualenvs/tesiscomp/bin/activate
cd /home/pablo/Proyectos/bsd_metrics/abortolegal/src/
python fetch_tweets.py >> fetch_tweets.log
