from seleniumdriver import seleniumdriver
from scraper import scraper
import time 
import os
import sys
import pymongo


wd = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(wd)
sys.path.insert(0, parentdir) 

PROXY_HOST = '191.101.125.8'  
PROXY_PORT = 4444 
PROXY_USER = '9443f36c1f' 
PROXY_PASS = '3fBL1eFx' 

driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS).driver

time.sleep(5)
driver.get("https://www.autoscout24.ch/de/autos/alle-marken?page=1&vehtyp=10")

print(driver.title)

params = {'page': 1, 'vehtype': 10}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s'

CNX_STR = os.environ['CNX_STR']
DB_NAME =  os.environ['DB_NAME']
COLL_NAME = os.environ['COLL_NAME']
COLL_NAME_LOG = os.environ['COLL_NAME_LOG']

client = pymongo.MongoClient(CNX_STR)
db = client[DB_NAME]
carsdb = db[COLL_NAME]
logdb = db[COLL_NAME_LOG]
autoscoutscraper =  scraper(driver , wd, start_url, baseurl,  params['page'] ,params['vehtype'], carsdb, logdb)
autoscoutscraper.startscraper()
