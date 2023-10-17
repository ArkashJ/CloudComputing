#!/bin/bash


echo "installing python3"
sudo apt-get install python3-pip -y

echo "copying files from bucket"
sudo gsutil -m cp -r gs://ds-561-hw3/hw4-files /home/arkjain

echo "installing requirements"
sudo cd /home/arkjain/hw4-files

sudo pip3 install -r requirements.txt
echo "running flask app"
waitress-serve --host 127.0.0.1 --port=5001 main:app
