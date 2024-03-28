from scraper import scraper
import time 
import os
import pymongo
from selenium import webdriver


driver = webdriver.Firefox()
time.sleep(5)
driver.get("https://www.motoscout24.ch/de/s/vc-camper?page=1&vehtyp=20")

print(driver.title)

params = {'page': 1, 'vehtype': 70}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s/vc-camper'

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

