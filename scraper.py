import time 
from selenium.webdriver.common.by import By
from datetime import date, datetime
import json
import os 
import pymongo

class scraper :
    def __init__(self, driver, wd, start_url, baseurl, dbconnection,page,vehtypefilter ):
        self.driver = driver
        self.wd = wd
        self.start_url = start_url
        self.baseurl = baseurl
        self.dbconnection = dbconnection
        self.page = page
        self.vehtypefilter = vehtypefilter
        currentweek = date.today().isocalendar()
        self.extractdate = datetime.strptime(str(currentweek[0]) + '-' + str(currentweek[1]) + '-1', "%Y-%W-%w").date().strftime("%Y-%m-%d")
        CNX_STR = os.environ['CNX_STR']
        DB_NAME =  os.environ['DB_NAME']
        COLL_NAME = os.environ['COLL_NAME']

        client = pymongo.MongoClient(CNX_STR)
        db = client[DB_NAME]
        self.carsdb = db[COLL_NAME]


    def startscraper(self):

    
        self.driver.set_window_size(1024, 600)
        self.driver.maximize_window()
        self.driver.get(self.start_url + '?page={page}&vehtyp={vehtyp}'.format(page = self.page, vehtyp = self.vehtypefilter))
        print(self.start_url + '?page={page}&vehtyp={vehtyp}'.format(page = self.page, vehtyp = self.vehtypefilter))
        time.sleep(1)
        cookie = self.driver.find_elements(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
        if(cookie):
            cookie[0].click()

        pagebutton = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'next page')]/preceding-sibling::*[1]")
        print(pagebutton)
        # r = self.driver.page_source
        # f=open("autoscout.txt","w")
        # f.write(r)
        # f.close()
        pages = int(pagebutton[-1].text)

        print("pages", pages)
        self.get_main_pages(1000,pages)
    
    def get_main_pages(self, startpage, pages):
        count_mainpages = 0
        for i in range(startpage,int(pages)+1):
            print("-"*10) 
            print("page: ",i)
        
            tracking = {'startpage': i}
            log = {'startpage': i, 'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'pages':pages}
        
            with open(os.path.join(self.wd,'tracking.txt'), 'w') as f:
                f.write(json.dumps(tracking))
            with open(os.path.join(self.wd,'log.txt'), 'w') as f:
                f.write(json.dumps(log))
            try : 
                self.driver.get(self.start_url + '?sort[0][type]=FIRST_REGISTRATION_DATE&sort[0][order]=ASC&pagination[page]={page}'.format(page = i))
                time.sleep(1)
                #find sublinks
                articles = self.driver.find_elements(By.CSS_SELECTOR, 'article')
                sublinks = [ link.find_elements(By.CSS_SELECTOR, 'a')[0].get_attribute('href')  for link in articles]
                print("sublinks",sublinks)
                self.get_sub_pages(sublinks)

            except :
                count_mainpages += 1
                if count_mainpages == 50:
                    exit(1)
                continue

    def get_sub_pages(self,sublinks):
   
        count = 0
        for sublink in sublinks: 
            print("subpage:  ",count)
            print(sublink) 

            count +=1
            if count > 30 :
                break

            try : 
                print("-"*10)
                self.driver.get(sublink )
                time.sleep(0.2)
                self.scrape_data()
                self.write_to_db()

            except Exception as e:
                print(e)
                self.datadict = None
                self.vehid = None 
                self.vehtype = None
                file = open(os.path.join(self.wd, "sublinks.txt"), 'a')
                file.write('\n'+sublink )
                file.close()
                continue

    def scrape_data(self):
        #read json with the main data in order to not identify all values one by one
        self.read_json_data()


    def read_json_data(self):
        data = self.driver.find_elements(By.CSS_SELECTOR,"script[type='application/json']")
        jsonstring = data[0].get_attribute('innerHTML')
        jsonstring = jsonstring.replace('\n','').replace('\t','')
        datadict = json.loads(jsonstring)
        datadict = datadict['props']['pageProps']
        print("vehid")
        vehid = datadict['pageViewTracking']['listingId']
        print("vehtype")
        vehtype = datadict['pageViewTracking']['listing_vehType'] 
        vehtype = 10 if vehtype == 'car' else 60  if vehtype == 'motorcycle' else    20 if   vehtype == 'utility' else 70 if vehtype == 'camper' else 0
        self.datadict = datadict
        self.vehid = vehid 
        self.vehtype = vehtype



    
    def write_to_db(self):
        # print("datadict",self.datadict)
        # decoded_str = json.dumps(self.datadict,ensure_ascii=False)
        # decoded_str = decoded_str.replace("'", "")
        # chunks, chunk_size = len(decoded_str), len(decoded_str)//15
        # chunkstring = [ decoded_str[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
        # sqlstring = """Insert /*+ ignore_row_on_dupkey_index(TMP_AUTOSCOUT, TMP_AUTOSCOUT_PK) */  into TMP_AUTOSCOUT 
        # VALUES(%s,%s,"""%(self.vehid,self.vehtype ) +("TO_CLOB ('{}')|| "*len(chunkstring))[:-3].format(*chunkstring) + """,TO_DATE('%s','YY-MM-DD'));""" %( self.extractdate) 
        cars_json = {"VEH_TYPE":self.vehtype , "VEH_ID" : self.vehid,"EXTRACT_DATE":self.extractdate , "VEH_DATA":self.datadict}
        #cursor.execute(sqlstring)
        self.carsdb.insert_one(cars_json)

    def write_to_log_file(self):
        pass

    def read_car_specs(self):
        #right now not needed
        cardetails = self.driver.find_elements(By.CSS_SELECTOR,'div#detailsVehSpecs')
        carkeys = [ key.text for key in cardetails[0].find_elements(By.CSS_SELECTOR,'span[class*="key-value-key"]')]
        carvalues= [ value.text for value in cardetails[0].find_elements(By.CSS_SELECTOR,'span[class*="key-value-value"]')]
        carspecs = {k:v for k,v in zip(carkeys,carvalues)}
        return carspecs

    def read_options(self):
        #right now not needed
        equipmentsections = self.driver.find_elements(By.CSS_SELECTOR, 'section[class*="modal-equipment-group"]')
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
    
    def scrollintoview(self, el ):
        script = "var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);var elementTop = arguments[0].getBoundingClientRect().top;window.scrollBy(0, elementTop-(viewPortHeight/2));"
        self.driver.execute_script(script, el)
    
    def highlight(self, element):
        driver = element._parent
        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                element, s)
        original_style = element.get_attribute('style')
        apply_style("border: 2px solid red;")
        time.sleep(.3)
        apply_style(original_style)

