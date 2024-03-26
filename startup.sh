#!/bin/bash
sudo yum install -y git
sudo yum install -y docker 
sudo systemctl start docker
sudo chmod 666 /var/run/docker.sock

#sudo systemctl enable docker.service
#sudo usermod -a -G docker ec2-user
export CNX_STR=""
export DB_NAME=""
export COLL_NAME=""
export COLL_NAME_LOG=""

git clone https://github.com/ricilandolt/autoscoutscraper.git /home/ec2-user/autoscoutscraper
sudo python3 -m venv /home/ec2-user/autoscoutscraper/virt
source /home/ec2-user/autoscoutscraper/virt/bin/activate 
sudo chown -R ec2-user:ec2-user /home/ec2-user/autoscoutscraper/virt
pip install -r /home/ec2-user/autoscoutscraper/requirements.txt
docker stop $(docker ps -a -q)
docker run  -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
cd /home/ec2-user/autoscoutscraper/
sleep 30
python /home/ec2-user/autoscoutscraper/car.py
