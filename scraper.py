import time 
from selenium.webdriver.common.by import By

class scraper :
    def __init__(self, driver, wd, start_url, baseurl, dbconnection,page,vehtype ):
        self.driver = driver
        self.wd = wd
        self.start_url = start_url
        self.baseurl = baseurl
        self.dbconnection = dbconnection
        self.page = page
        self.vehtype = vehtype

    def setup(self):
        self.driver.set_window_size(1024, 600)
        self.driver.maximize_window()
        self.driver.get(self.start_url + '?page={page}&vehtyp={vehtyp}'.format(page = self.page, vehtyp = self.vehtype))
        print(self.start_url + '?page={page}&vehtyp={vehtyp}'.format(page = self.page, vehtyp = self.vehtype))
        time.sleep(1)
        cookie = self.driver.find_elements(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
        if(cookie):
            cookie[0].click()
        time.sleep(1)
        pagebutton = self.driver.find_elements(By.CSS_SELECTOR, 'button.css-1e48l4x')
        pagebutton = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'next page')]/preceding-sibling::*[1]")
        pages = int(pagebutton[-1].text)

        print(pages)
    
    def get_main_pages(self):
        pass

    def get_sub_pages(self):
        pass

    def scrape_data(self):
        pass

    def write_to_log_file(self):
        pass