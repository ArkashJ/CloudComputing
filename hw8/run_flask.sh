#!/bin/bash
echo "installing python3"
sudo apt-get install python3-pip -y
echo "copying files from bucket"
sudo gsutil -m cp -r gs://ds-561-hw8/hw8-files /home/arkjain
curr_path="/home/arkjain/hw8-files"
echo "installing requirements"
cd $curr_path
sudo pip3 install -r requirements.txt
echo "running flask app"
export ZONE=us-central1-a
waitress-serve --host 0.0.0.0 --port=5000 main:app &
