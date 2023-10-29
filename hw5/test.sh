#!/bin/bash

echo "installing python3"
sudo apt-get install python3-pip -y

if [ -d "/home/arkjain/hw5" ]
then
    echo "found old files"
else
    gsutil -m cp -r gs://hw5-ds561/hw5 /home/arkjain
fi

curr_path="/home/arkjain/hw5-files"
echo "installing requirements"
echo "copying files from bucket"
cd $curr_path 

sudo pip3 install -r requirements.txt
echo "running flask app"
waitress-serve --host 0.0.0.0 --port=5000 main:app &
