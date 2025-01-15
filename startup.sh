#!/bin/bash
sudo yum update -y
sudo yum install -y git docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
git clone https://ricilandolt:@github.com/ricilandolt/autoscoutscraper /home/ec2-user/autoscoutscraper
sudo chown -R ec2-user:ec2-user /home/ec2-user/autoscoutscraper
sudo chmod -R 755 /home/ec2-user/autoscoutscraper
sudo chown ec2-user:ec2-user /home/ec2-user/autoscoutscraper/proxy_auth_plugin.zip
sudo chmod 644 /home/ec2-user/autoscoutscraper/proxy_auth_plugin.zip
echo "clone done"
PROXY_PASS=""
POSTGRES_STR=""
URL_SUFFIX="/de/s"
VEH_TYPE=10
echo "PROXY_PASS=$PROXY_PASS" > /home/ec2-user/autoscoutscraper/.env
echo "POSTGRES_STR=$POSTGRES_STR" >> /home/ec2-user/autoscoutscraper/.env
echo "URL_SUFFIX=$URL_SUFFIX" > /home/ec2-user/autoscoutscraper/.env
echo "VEH_TYPE=$VEH_TYPE" >> /home/ec2-user/autoscoutscraper/.env
chown ec2-user:ec2-user /home/ec2-user/autoscoutscraper/.env
sudo chmod +x /home/ec2-user/autoscoutscraper/startscraper.sh
sudo python3 -m venv /home/ec2-user/autoscoutscraper/virt
source /home/ec2-user/autoscoutscraper/virt/bin/activate
pip install -r /home/ec2-user/autoscoutscraper/requirements.txt
echo "pip install done"
cd /home/ec2-user/autoscoutscraper
su - ec2-user -c "/bin/bash /home/ec2-user/autoscoutscraper/startscraper.sh scrapy.py"
