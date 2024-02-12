#!/bin/sh
sudo yum install -y git
sudo yum install -y docker 
sudo usermod -a -G docker ec2-user
sudo chmod 666 /var/run/docker.sock
sudo systemctl enable docker.service
docker run  -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
git clone https://github.com/ricilandolt/autoscoutscraper.git
cd autoscoutscraper
sudo python3 -m venv /home/ec2-user/alphabetapp/virt
source ./virt/bin/activate 
sudo chown -R ec2-user:ec2-user /home/ec2-user/alphabetapp/virt
pip install -r requirements.txt
docker stop $(docker ps -a -q)
python car.py
