# -*- coding: utf-8 -*-
import os
import sys


wd = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(wd)
sys.path.insert(0, parentdir) 
from helper_functions import *


params = {'page': 1, 'vehtyp': 10}
baseurl = 'https://www.autoscout24.ch'
start_url = baseurl + '/de/s'
scraper(wd, start_url, baseurl, params = params)