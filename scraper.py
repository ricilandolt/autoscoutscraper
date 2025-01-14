import time 
from selenium.webdriver.common.by import By
from datetime import date, datetime
import json
import copy


vehtype_recoding = {'car':10  , 'motorcycle':  60,  'utility' :20, 'camper':70 }
fallback = {"10":8000, "60":1500,"70":300 , "20":700}
class scraper :
    def __init__(self, driver, start_url, baseurl, page,vehtypefilter,  logdb = {"10":{"startpage":1}, "20":{"startpage":1},"60":{"startpage":1}, "70":{"startpage":1}}, conn=None ):
        self.driver = driver
        self.start_url = start_url
        self.baseurl = baseurl
        self.page = page
        self.vehtypefilter = vehtypefilter
        currentweek = date.today().isocalendar()
        self.extractdate = datetime.strptime(str(currentweek[0]) + '-' + str(currentweek[1]) + '-1', "%Y-%W-%w").date().strftime("%Y-%m-%d")

        self.logdb = logdb
        if conn :
            self.conn = conn
            self.cur = conn.cursor()


    def startscraper(self):
        # self.write_to_log("Scraper Started for vehtype {}".format(self.vehtypefilter)  + " \n")
        
        while True:
            try:

                self.driver.set_window_size(1024, 600)
                self.driver.maximize_window()
                self.driver.get(self.start_url + '?page={page}&vehtyp={vehtyp}'.format(page = self.page, vehtyp = self.vehtypefilter))
                print(self.start_url + '?page={page}&vehtyp={vehtyp}'.format(page = self.page, vehtyp = self.vehtypefilter))
                time.sleep(1)
                cookie = self.driver.find_elements(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
                if(cookie):
                    cookie[0].click()
                time.sleep(0.3)

                pagebutton = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'next page')]/preceding-sibling::*[1]")
                try: 
                    pageamount = round(int(self.driver.find_elements(By.XPATH, "//h1/preceding-sibling::*[1]")[0].text.replace("'","")) /20)
                except:
                    pageamount = 0
                print(pagebutton)
                if  pagebutton:
                    pages = int(pagebutton[-1].text)
                    # self.write_to_log("ERROR Page Button is null for vehtype {}".format(self.vehtypefilter)  + " \n")
                elif pageamount:
                    pages = pageamount
                else : 
                    pages = fallback[str( self.vehtypefilter)]
               
                print("pages", pages)
                # startpage = 1
                self.cur.execute("select startpage from logs where vehtype = {}".format(self.vehtypefilter))
                rs = self.cur.fetchall()
                print("rs", rs)
                startpage = rs[0][0] if rs else 1 
                self.get_main_pages(startpage,pages)

            except Exception as e:
                print("An error occurred:", e)    
    
    def get_main_pages(self, startpage, pages):
        count_mainpages = 0
        for i in range(startpage,int(pages)+1):
            print("-"*10) 
            print("page: ",i)
    
            log = {'vehtype':self.vehtypefilter ,'startpage': i, 'extractdate':self.extractdate,'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'pages':pages}
            self.write_to_tracking_file(log)
            try :           
                print("start extracting data")
                start = time.time()
                self.driver.get(self.start_url + '?sort[0][type]=FIRST_REGISTRATION_DATE&sort[0][order]=ASC&pagination[page]={page}'.format(page = i))
                end = time.time()
                print("main page ",end-start)
                time.sleep(1)

                print("start scrape")
                self.scrape_data()
                start = time.time()
                print("write to db")
                self.write_to_db()
                end = time.time()
                print("finish to db ", end-start)

            except Exception as e:
                print("An error occurred:", e)
                count_mainpages += 1
                if count_mainpages == 50:
                    # self.write_to_log("ERROR Count Mainpages failed for Vehtype {}".format(self.vehtypefilter)  + " \n")
                    exit(1)
                continue
        

        # self.write_to_log("Scraper Finished for vehtype {}".format(self.vehtypefilter)  + " \n")

        log = {'vehtype':self.vehtypefilter ,'startpage': 1, 'extractdate':self.extractdate,'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'pages':pages}
        start = time.time()
        self.write_to_tracking_file(log)
        end = time.time()
        print("log file ",end-start)

    def scrape_data(self):
        #read json with the main data in order to not identify all values one by one
        start = time.time()
        self.read_json_data()
        end = time.time()
        print("scrape data ",end-start)



    def read_json_data(self):
        templatekeys = ["bodyColor", "listPrice", "bodyType", "cubicCapacity", "doors", "driveType" ]
        templatedata = { k:None for k in templatekeys }
        data = self.driver.find_elements(By.CSS_SELECTOR,"script[type='application/json']")
        jsonstring = data[0].get_attribute('innerHTML')
        jsonstring = jsonstring.replace('\n','').replace('\t','')
        datadict = json.loads(jsonstring)
        datadict =  datadict['props']['pageProps']['prefetchedListings']['content']
        keys = ['images','features','financing','insurance','leasing','qualiLogoId','logoKey', 'teaser']
        data = []
        for el  in datadict :
            templatedict = {}
            cardict = copy.deepcopy(templatedata)
            obj = {k:v  for k,v in el.items() if k not in keys }
            vehtype = vehtype_recoding.get(obj['vehicleCategory'])
            vehicledata = {k:v  for k,v in el.items() if k != 'seller' }
            cardict.update(vehicledata)
            templatedict['listing'] = cardict 
            templatedict['vehtype'] = vehtype
            templatedict['seller'] = obj['seller']
            templatedict['id'] = obj['id']
            data.append(templatedict)
        print(data[0])
        self.datadict = data


    
    def write_to_db(self):
        for el in self.datadict: 
            self.cur.execute("""INSERT INTO autoscout VALUES({},{},to_date('{}','YYYY-MM-DD'),'{}') ON CONFLICT (VEH_TYPE,VEH_ID,EXTRACT_DATE) DO NOTHING""".format(el['vehtype'], el['id'],  self.extractdate, json.dumps( el).replace('\n','').replace('\t','').replace("'","") ))


    def write_to_tracking_file(self, log):
        try:
            update_query = """
            UPDATE logs
            SET startpage = %s,
                extractdate = to_date(%s, 'YYYY-MM-DD'),
                timestamp = %s,
                pages = %s
            WHERE vehtype = %s;
            """
            print("Updating logs...")

            self.cur.execute("SET statement_timeout TO 5000;")
            self.cur.execute(update_query, (
                log['startpage'],
                self.extractdate,
                log['timestamp'],
                log['pages'],
                log['vehtype']
            ))

            print("Logs updated.")
        except Exception as e:
            print("An error occurred:", e)
            print("updated")
        finally:
            self.cur.execute("SET statement_timeout TO 0;")

    
    def write_to_log(self,msg):
        with open("/var/log/scraper.log", "a") as f : 
            f.write(msg)



