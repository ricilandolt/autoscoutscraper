
from seleniumdriver import seleniumdriver
from scraper import scraper
import time 
import os
import pymongo
import psycopg2


PROXY_HOST = "191.101.125.8" 
PROXY_USER = "9443f36c1f" 
PROXY_PASS = os.environ['PROXY_PASS']
PROXY_PORT = 4444 

PROXY_HOST = "193.108.102.167" 
PROXY_USER = "14a9741190786" 
PROXY_PASS = os.environ['PROXY_PASS']
PROXY_PORT = 12323 

driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS).driver

time.sleep(5)
driver.get("https://www.autoscout24.ch/de/s/vc-utility?page=1&vehtyp=20")

print(driver.title)

params = {'page': 1, 'vehtype': 20}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s/vc-utility'

POSTGRES_STR = os.getenv("POSTGRES_STR")
if POSTGRES_STR:
    conn = psycopg2.connect(POSTGRES_STR)
    conn.autocommit = True
else :
    conn = ""
    
autoscoutscraper =  scraper(driver , start_url, baseurl,  params['page'] ,params['vehtype'], carsdb, logdb,conn)
autoscoutscraper.startscraper()
