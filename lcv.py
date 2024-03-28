
from seleniumdriver import seleniumdriver
from scraper import scraper
import time 
import os
import pymongo


PROXY_HOST = '191.101.67.218'  
PROXY_PORT = 4444 
PROXY_USER = '9443f36c1f' 
PROXY_PASS = '3fBL1eFx' 

driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS).driver

time.sleep(5)
driver.get("https://www.autoscout24.ch/de/s/vc-utility?page=1&vehtyp=20")

print(driver.title)

params = {'page': 1, 'vehtype': 20}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s/vc-utility'

CNX_STR = os.environ['CNX_STR']
DB_NAME =  os.environ['DB_NAME']
COLL_NAME = os.environ['COLL_NAME']
COLL_NAME_LOG = os.environ['COLL_NAME_LOG']

client = pymongo.MongoClient(CNX_STR)
db = client[DB_NAME]
carsdb = db[COLL_NAME]
logdb = db[COLL_NAME_LOG]
autoscoutscraper =  scraper(driver , start_url, baseurl,  params['page'] ,params['vehtype'], carsdb, logdb)
autoscoutscraper.startscraper()
