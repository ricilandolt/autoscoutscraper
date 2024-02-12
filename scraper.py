
class scraper :
    def __init__(self, driver, wd, start_url, baseurl, dbconnection):
        self.driver = driver
        self.wd = wd
        self.start_url = start_url
        self.baseurl = baseurl
        self.dbconnection = dbconnection

    def setup(self):
        pass
    
    def get_main_pages(self):
        pass

    def get_sub_pages(self):
        pass

    def scrape_data(self):
        pass

    def write_to_log_file(self):
        pass