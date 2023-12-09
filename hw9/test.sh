if [ -d "/home/arkjain/hw8-files" ]; then
                  echo "found old files"
            else
              gsutil -m cp -r gs://ds-561-hw8/hw8-files /home/arkjain
            fi

            cd "/home/arkjain/hw8-files"
            sudo apt install python3-pip -y
            pip3 install -r requirements.txt
            export ZONE=us-central1-a
            waitress-serve --host 0.0.0.0 --port=80 main:app & 

