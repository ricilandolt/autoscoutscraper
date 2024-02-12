#!/bin/sh
git clone https://github.com/ricilandolt/autoscoutscraper.git
docker run  -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
cd autoscout
source ./virt/bin/activate 
pip install -r requirements.txt
python car.py
