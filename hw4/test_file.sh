#!/bin/bash

BUCKET_NAME=ds://ds-561-hw3
gcloud storage buckets create gs://ds-561-hw3  --location=US-EAST4
gsutil -m cp -r .  gs://ds-561-hw3/


gcloud compute instances create main-vm --project=cloudcomputingcourse-398918 --zone=us-central1-c 
--machine-type=f1-micro --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default 
--maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=homework3-work@cloudcomputingcourse-398918.iam.gserviceaccount.com 
--scopes=https://www.googleapis.com/auth/cloud-platform --create-disk=auto-delete=yes,boot=yes,device-name=main-vm,image=projects/debian-cloud/global/images/debian-11-bullseye-v20231010,mode=rw,size=10,type=projects/cloudcomputingcourse-398918/zones/us-central1-a/diskTypes/pd-balanced 
--no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud 
--reservation-affinity=any

gsutil cp gs://ds-561-hw3/main.py main-vm


