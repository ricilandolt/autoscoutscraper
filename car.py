
from seleniumdriver import seleniumdriver
from scraper import scraper
import time 
import os
import sys


wd = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(wd)
sys.path.insert(0, parentdir) 

PROXY_HOST = '147.53.127.97'  
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
dbconnection = ""
autoscoutscraper =  scraper(driver , wd, start_url, baseurl, dbconnection, params['page'] ,params['vehtype'])
autoscoutscraper.setup()
