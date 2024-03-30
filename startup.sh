#!/bin/bash
sudo yum install -y git
sudo yum install -y docker 
sudo yum install -y amazon-cloudwatch-agent
sudo systemctl start docker
sudo chmod 666 /var/run/docker.sock
sudo touch /var/log/scraper.log
sudo chown -R ec2-user:ec2-user /var/log/scraper.log

git clone https://ricilandolt:<passoword>@github.com/ricilandolt/autoscoutscraper /home/ec2-user/autoscoutscraper
sudo python3 -m venv /home/ec2-user/autoscoutscraper/virt
source /home/ec2-user/autoscoutscraper/virt/bin/activate 
sudo chown -R ec2-user:ec2-user /home/ec2-user/autoscoutscraper/virt
pip install -r /home/ec2-user/autoscoutscraper/requirements.txt
sudo chmod +x /home/ec2-user/autoscoutscraper/startscraper.sh
sudo cp /home/ec2-user/autoscoutscraper/scraperservice.service /etc/systemd/system/scraperservice.service
SCRIPTNAME="moto.py"
SERVICE_FILE="/etc/systemd/system/scraperservice.service"
PROXY_HOST = '' 
PROXY_USER = '' 
PROXY_PASS = '' 
CNX_STR=""

sed -i "/\[Service\]/a Environment=\"scriptname=$SCRIPTNAME\"" $SERVICE_FILE
sed -i "/\[Service\]/a Environment=\"CNX_STR=$CNX_STR\"" $SERVICE_FILE
sed -i "/\[Service\]/a Environment=\"PROXY_HOST=$PROXY_HOST\"" $SERVICE_FILE
sed -i "/\[Service\]/a Environment=\"PROXY_USER=$PROXY_USER\"" $SERVICE_FILE
sed -i "/\[Service\]/a Environment=\"PROXY_PASS=$PROXY_PASS\"" $SERVICE_FILE
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file://home/ec2-user/autoscoutscraper/cloudwatchconf.json -s

systemctl daemon-reload
systemctl enable scraperservice.service
systemctl start scraperservice.service
