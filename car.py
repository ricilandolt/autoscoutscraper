from seleniumdriver import seleniumdriver
from scraper import scraper
import os
import pymongo
import time 
import psycopg2

PROXY_HOST = "191.101.125.8" 
PROXY_USER = "9443f36c1f" 
PROXY_PASS = os.environ['PROXY_PASS']
PROXY_PORT = 4444 

driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS).driver

time.sleep(5)

params = {'page': 1, 'vehtype': 10}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s'

CNX_STR = os.environ['CNX_STR']
DB_NAME =  'carmarket'
COLL_NAME = 'autoscout'
COLL_NAME_LOG = 'autoscoutlog'
POSTGRES_STR = os.environ['POSTGRES_STR']
if POSTGRES_STR:
    conn = psycopg2.connect(POSTGRES_STR)


client = pymongo.MongoClient(CNX_STR)
db = client[DB_NAME]
carsdb = db[COLL_NAME]
logdb = db[COLL_NAME_LOG]
autoscoutscraper =  scraper(driver, start_url, baseurl,  params['page'] ,params['vehtype'], carsdb, logdb , conn)
autoscoutscraper.startscraper()
