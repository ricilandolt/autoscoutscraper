import time 
import json
import os
import pyodbc
import requests 
from datetime import date, datetime
from config import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import win32com.client as win32
import time 

def highlight(element):
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)
    original_style = element.get_attribute('style')
    apply_style("border: 2px solid red;")
    time.sleep(.3)
    apply_style(original_style)

def scrollintoview(driver,el):
        script = "var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);var elementTop = arguments[0].getBoundingClientRect().top;window.scrollBy(0, elementTop-(viewPortHeight/2));"
        driver.execute_script(script, el)


def read_json_data(driver):
    data = driver.find_elements(By.CSS_SELECTOR,"script[type='application/json']")
    jsonstring = data[0].get_attribute('innerHTML')
    jsonstring = jsonstring.replace('\n','').replace('\t','')
    detaildict = json.loads(jsonstring)
    return detaildict


def read_car_specs(driver):
    cardetails = driver.find_elements(By.CSS_SELECTOR,'div#detailsVehSpecs')
    carkeys = [ key.text for key in cardetails[0].find_elements(By.CSS_SELECTOR,'span[class*="key-value-key"]')]
    carvalues= [ value.text for value in cardetails[0].find_elements(By.CSS_SELECTOR,'span[class*="key-value-value"]')]
    carspecs = {k:v for k,v in zip(carkeys,carvalues)}
    return carspecs

def read_options(driver):
    equipmentsections = driver.find_elements(By.CSS_SELECTOR, 'section[class*="modal-equipment-group"]')
    if equipmentsections:
        standardequip = [el.get_attribute('innerHTML') for el in equipmentsections[0].find_elements(By.CSS_SELECTOR,'span[class*="key-value-value"]')]
        optionalequip = [el.get_attribute('innerHTML') for el in equipmentsections[-1].find_elements(By.CSS_SELECTOR,'span[class*="key-value-value"]')]
        
        standardequip.sort()
        optionalequip.sort()
        if standardequip == optionalequip:
            optionalequip = []
    else: 
        optionalequip = []
        standardequip = []

    return {'standardequip' : standardequip, 'optionalequip' : optionalequip}


def scraper(driver, wd, start_url, baseurl, **kwargs):
    # cnxn = pyodbc.connect(db['connectionstring'],autocommit = True)
    # cursor = cnxn.cursor()
    currentweek = date.today().isocalendar()
    extractdate = datetime.strptime(str(currentweek[0]) + '-' + str(currentweek[1]) + '-1', "%Y-%W-%w").date().strftime("%Y-%m-%d")
    
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    driver.get(start_url + '?page={page}&vehtyp={vehtyp}'.format(**kwargs['params']))
    print(start_url + '?page={page}&vehtyp={vehtyp}'.format(**kwargs['params']))
    time.sleep(1)
    cookie = driver.find_elements(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
    if(cookie):
        cookie[0].click()
    time.sleep(1)
    pagebutton = driver.find_elements(By.CSS_SELECTOR, 'button.css-1e48l4x')
    pagebutton = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'next page')]/preceding-sibling::*[1]")
    pages = int(pagebutton[-1].text)

    print(pages)
    
    trackingfile = os.path.join(wd,'tracking.txt')
    if datetime.today().strftime("%Y-%m-%d") == extractdate:
        trackingdict = {"startpage": 1}
    elif os.path.exists(trackingfile) :
        with open(trackingfile, 'r') as f:
            trackingdict = json.load(f)
    else : 
        trackingdict = {"startpage": 1}
    
    loop_mainpages(wd,pages,driver,start_url,baseurl,cursor, extractdate, trackingdict['startpage'],  **kwargs)

    if os.path.exists(os.path.join(wd, "sublinks.txt")) :
        with open(os.path.join(wd, "sublinks.txt"), "r") as f: 
            sublinks = f.readlines()
        sublinks = [l for l in sublinks if l != "\n"]
        loop_subpages(wd,sublinks, driver, cursor , extractdate,  proxies = proxies, **kwargs)
    
    if os.path.exists(trackingfile) :
        with open(trackingfile, 'r') as f:
            trackingdict = json.load(f)
        print(trackingdict['startpage'])
        print(pages)
        print(type(pages))
        print(type(trackingdict['startpage']))
        if trackingdict['startpage'] >= int(pages) :
            os.remove(os.path.join(wd,trackingfile))
    
    try:
        os.remove(os.path.join(wd, "sublinks.txt"))

    except:
        pass

    

def loop_subpages(wd,sublinks,driver, cursor, extractdate, **kwargs):
    
    count = 0
    for sublink in sublinks: 
        print("subpage:  ",count)
        print(sublink) 

        count +=1
        if count > 30 :
            break

 

        try : 
            print("-"*10)
            driver.get(sublink )
            time.sleep(0.2)
            #read json with the main data in order to not identify all values one by one
            datadict = read_json_data(driver)
            datadict = datadict['props']['pageProps']
            
            # #read all car specifications because listprice is missing in json
            # carspecsdict = read_car_specs(driver)
            
            # #read standard and optional equipments
            # optionsdict = read_options(driver)

            # datadict.update(carspecsdict)
            # datadict.update(optionsdict)

            # if len(car_docs):
            #     for col in to_delete:
            #         if col in car_docs.keys():
            #             car_docs.pop(col)

            print("vehid")
            vehid = datadict['pageViewTracking']['listingId']
            print("vehtype")
            vehtype = datadict['pageViewTracking']['listing_vehType'] 
            vehtype = 10 if vehtype == 'car' else 60  if vehtype == 'motorcycle' else    20 if   vehtype == 'utility' else 70 if vehtype == 'camper' else 0

            print(vehtype)
            decoded_str = json.dumps(datadict,ensure_ascii=False)
            decoded_str = decoded_str.replace("'", "")
            chunks, chunk_size = len(decoded_str), len(decoded_str)//15
            chunkstring = [ decoded_str[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
            sqlstring = """Insert /*+ ignore_row_on_dupkey_index(TMP_AUTOSCOUT, TMP_AUTOSCOUT_PK) */  into TMP_AUTOSCOUT 
            VALUES(%s,%s,"""%(vehid,vehtype ) +("TO_CLOB ('{}')|| "*len(chunkstring))[:-3].format(*chunkstring) + """,TO_DATE('%s','YY-MM-DD'));""" %(  extractdate) 
            cursor.execute(sqlstring)

        except Exception as e:
            print(e)

            #outlook = win32.Dispatch('outlook.application')
            #mail = outlook.CreateItem(0)
            #mail.To = 'ricardo.landolt@bmw.ch'
            #mail.Subject = 'Autoscout Error'
            #mail.HTMLBody = """Autoscout Error"""
            #mail.Send()
            file = open(os.path.join(wd, "sublinks.txt"), 'a')
            file.write('\n'+sublink )
            file.close()
            continue

def loop_mainpages(wd,pages,driver, start_url, baseurl, cursor, extractdate,startpage,**kwargs):
    count_mainpages = 0
    for i in range(startpage,int(pages)+1):
        print("-"*10) 
        print("page: ",i)
        print("-"*10) 
       
        tracking = {'startpage': i}
        log = {'startpage': i, 'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'pages':pages}
       
        with open(os.path.join(wd,'tracking.txt'), 'w') as f:
            f.write(json.dumps(tracking))
        with open(os.path.join(wd,'log.txt'), 'w') as f:
            f.write(json.dumps(log))
        try :
          kwargs['params'] = {'page':i}  
          
          driver.get(start_url + '?sort[0][type]=FIRST_REGISTRATION_DATE&sort[0][order]=ASC&pagination[page]={page}'.format(**kwargs['params']))
          time.sleep(1)
          #find sublinks
          articles = driver.find_elements(By.CSS_SELECTOR, 'article')
          sublinks = [ link.find_elements(By.CSS_SELECTOR, 'a')[0].get_attribute('href')  for link in articles]

        except :
            file = open( os.path.join(wd, 'url.txt'), 'a')
            file.write('\n'+start_url+str(i))
            file.close()
            count_mainpages += 1
            if count_mainpages == 50:
                exit(1)
                
            continue
        loop_subpages(wd,sublinks, driver, cursor , extractdate, **kwargs)
   








