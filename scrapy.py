
from scraper import scraper
import os
import time 
import psycopg2
from dotenv import load_dotenv


env_path = '/home/ec2-user/autoscoutscraper/.env'
load_dotenv(dotenv_path=env_path)

PROXY_HOST = "193.108.102.167" 
PROXY_USER = "14a9741190786" 
PROXY_PASS = os.getenv('PROXY_PASS')
PROXY_PORT = 12323 

debug = False

if not debug : 
    from seleniumdriver import seleniumdriver
    driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS).driver
# else : 
#     from selenium import webdriver
#     driver = webdriver.Chrome(executable_path="../chromedriver.exe")

time.sleep(5)

params = {'page': 1, 'vehtype': os.getenv("VEH_TYPE", 10)}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl +  os.getenv("URL_SUFFIX", '/de/s')


POSTGRES_STR = os.getenv("POSTGRES_STR")
if POSTGRES_STR:
    conn = psycopg2.connect(POSTGRES_STR)
    conn.autocommit = True
else :
    conn = ""

autoscoutscraper =  scraper(driver, start_url, baseurl,  params['page'] ,params['vehtype'],  conn = conn)
autoscoutscraper.startscraper()
