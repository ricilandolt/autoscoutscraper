
from scraper import scraper
import os
import time 
import psycopg2


PROXY_HOST = "193.108.102.167" 
PROXY_USER = "14a9741190786" 
PROXY_PASS = os.getenv('PROXY_PASS')
PROXY_PORT = 12323 

debug = True

if debug : 
    from seleniumdriver import seleniumdriver
    driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS).driver
time.sleep(5)

params = {'page': 1, 'vehtype': 10}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s'


POSTGRES_STR = os.getenv("POSTGRES_STR")
if POSTGRES_STR:
    conn = psycopg2.connect(POSTGRES_STR)
    conn.autocommit = True
else :
    conn = ""

autoscoutscraper =  scraper(driver, start_url, baseurl,  params['page'] ,params['vehtype'],  conn = conn)
autoscoutscraper.startscraper()
