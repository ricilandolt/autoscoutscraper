#!/bin/bash

service docker start
source /home/ec2-user/autoscoutscraper/virt/bin/activate 
while true; do
    python /home/ec2-user/autoscoutscraper/$1
    if [ $? -ne 0 ]; then
        echo "Python-Skript abgebrochen, führe Docker-Befehle aus..."
        docker container prune -f
        docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
        sleep 30
    else
        echo "Python-Skript erfolgreich durchgelaufen, keine weiteren Aktionen erforderlich."
        sudo shutdown
        break
    fi
done