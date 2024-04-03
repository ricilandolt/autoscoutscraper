import time 
from selenium.webdriver.common.by import By
from datetime import date, datetime
import json

class scraper :
    def __init__(self, driver, start_url, baseurl, page,vehtypefilter, carsdb, logdb ):
        self.driver = driver
        self.start_url = start_url
        self.baseurl = baseurl
        self.page = page
        self.vehtypefilter = vehtypefilter
        currentweek = date.today().isocalendar()
        self.extractdate = datetime.strptime(str(currentweek[0]) + '-' + str(currentweek[1]) + '-1', "%Y-%W-%w").date().strftime("%Y-%m-%d")
        self.carsdb = carsdb
        self.logdb = logdb


    def startscraper(self):
        with open("/var/log/scraper.log", "a") as f : 
            f.write("Scraper Started for vehtype {}".format(self.vehtypefilter)  + " \n")
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
        if not pagebutton:
            with open("/var/log/scraper.log", "a") as f : 
                f.write("ERROR Page Button is null for vehtype {}".format(self.vehtypefilter)  + " \n")

        pages = int(pagebutton[-1].text)

        print("pages", pages)
        logdata = self.logdb.find_one({'vehtype':self.vehtypefilter })
        self.get_main_pages(logdata['startpage'],pages)
    
    def get_main_pages(self, startpage, pages):
        count_mainpages = 0
        for i in range(startpage,int(pages)+1):
            print("-"*10) 
            print("page: ",i)
    
            log = {'vehtype':self.vehtypefilter ,'startpage': i, 'extractdate':self.extractdate,'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'pages':pages}
            self.write_to_log_file(log)
            try :           
                start = time.time()
                self.driver.get(self.start_url + '?sort[0][type]=FIRST_REGISTRATION_DATE&sort[0][order]=ASC&pagination[page]={page}'.format(page = i))
                end = time.time()
                print("main page ",end-start)
                time.sleep(1)
                #find sublinks
                articles = self.driver.find_elements(By.CSS_SELECTOR, 'article')
                sublinks = [ link.find_elements(By.CSS_SELECTOR, 'a')[0].get_attribute('href')  for link in articles]
                print("sublinks",sublinks)
                self.get_sub_pages(sublinks)

            except :
                count_mainpages += 1
                if count_mainpages == 50:
                    with open("/var/log/scraper.log", "a") as f : 
                        f.write("ERROR Count Mainpages failed for Vehtype {}".format(self.vehtypefilter)  + " \n")
                    exit(1)
                continue

        with open("/var/log/scraper.log", "a") as f : 
            f.write("Scraper Finished for vehtype {}".format(self.vehtypefilter)  + " \n")
        log = {'vehtype':self.vehtypefilter ,'startpage': 1, 'extractdate':self.extractdate,'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'pages':pages}
        start = time.time()
        self.write_to_log_file(log)
        end = time.time()
        print("log file ",end-start)

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
                start = time.time()
                self.driver.get(sublink )
                end = time.time()
                print("subpage ", end-start)
                time.sleep(0.2)
                self.scrape_data()
                start = time.time()
                self.write_to_db()
                end = time.time()
                print("write to db ", end-start)

            except Exception as e:
                print(e)
                self.datadict = None
                self.vehid = None 
                self.vehtype = None
                continue

    def scrape_data(self):
        #read json with the main data in order to not identify all values one by one
        start = time.time()
        self.read_json_data()
        end = time.time()
        print("scrape data ",end-start)


    def read_json_data(self):
        data = self.driver.find_elements(By.CSS_SELECTOR,"script[type='application/json']")
        jsonstring = data[0].get_attribute('innerHTML')
        jsonstring = jsonstring.replace('\n','').replace('\t','')
        datadict = json.loads(jsonstring)
        datadict = datadict['props']['pageProps']
        vehid = datadict['pageViewTracking']['listingId']
        print("vehid",vehid)
        vehtype = datadict['pageViewTracking']['listing_vehType'] 
        print("vehtype", vehtype)
        vehtype = 10 if vehtype == 'car' else 60  if vehtype == 'motorcycle' else    20 if   vehtype == 'utility' else 70 if vehtype == 'camper' else 0
        self.datadict = datadict
        self.vehid = vehid 
        self.vehtype = vehtype

    
    def write_to_db(self):
        cars_json = {"VEH_TYPE":self.vehtype , "vehicleTypeId" : self.vehid,"ExtractionDate":self.extractdate , "VEH_DATA":self.datadict}
        self.carsdb.insert_one(cars_json)

    def write_to_log_file(self, log):
        vehtypequery = { "vehtype": self.vehtypefilter }
        newlogvalues = { "$set": log }
        self.logdb.update_one(vehtypequery, newlogvalues)



