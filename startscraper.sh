#!/bin/bash
export CNX_STR="mongodb+srv://ricardo:fKPMEyujxm1HlFGh@carmarket.wk9kj.mongodb.net/carmarket?retryWrites=true&w=majority"
export DB_NAME="carmarket"
export COLL_NAME="autoscout"
export COLL_NAME_LOG="autoscoutlog"

service docker start
source /home/ec2-user/autoscoutscraper/virt/bin/activate 
while true; do
    python /home/ec2-user/autoscoutscraper/caravan.py
    if [ $? -ne 0 ]; then
        echo "Python-Skript abgebrochen, führe Docker-Befehle aus..."
        docker stop $(docker ps -a -q)
        docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
        sleep 30
    else
        echo "Python-Skript erfolgreich durchgelaufen, keine weiteren Aktionen erforderlich."
        # sudo shutdown
        break
    fi
done