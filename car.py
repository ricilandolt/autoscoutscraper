
from seleniumdriver import seleniumdriver
import time 

PROXY_HOST = '147.53.127.97'  
PROXY_PORT = 4444 
PROXY_USER = '9443f36c1f' 
PROXY_PASS = '3fBL1eFx' 

driver = seleniumdriver(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS)

time.sleep(5)
driver.get("https://www.autoscout24.ch/de/autos/alle-marken?page=1&vehtyp=10")

print(driver.title)

time.sleep(30)

driver.quit()