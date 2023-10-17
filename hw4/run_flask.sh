#!/bin/bash


echo "installing python3"
sudo apt-get install python3-pip -y

echo "copying files from bucket"
sudo gsutil -m cp -r gs://ds-561-hw3/hw4-files /home/arkjain

echo "installing requirements"
sudo cd hw4-files

sudo pip3 install -r requirements.txt
echo "running flask app"
python3 -m flask --app main run --host=0.0.0.0 --port=5000 &
