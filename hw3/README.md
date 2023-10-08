## Running on Cloud
Simply run 
```
chmod +x test_cloud.sh
./test_cloud.sh
```

## Running on Local
Start the virtual environment in 3 different terminals
```
source venv/bin/activate
```
or if you're using fish
```
source venv/bin/activate.fish
```

In the first terminal, run the following command to start the server
```
functions-framework --target=receive_http_request --debug
```

In the second terminal, run the following command to start the client for a random country
```
python3 http-client.py -d 127.0.0.1 -p 8080 -v -n 1 \                                                                                                                    (base)
      -i 9999 \
      -b hw2-arkjain-mini-internet 
```
or for a banned country
```
python3 http-client.py -d 127.0.0.1 -p 8080 -v -n 1 \                                                                                                                    (base)
      -i 9999 \
      -b hw2-arkjain-mini-internet \
      -c Syria
```

In the third terminal, run the following command to start the client for a random country
```
python3 banned_request.py
```

Otherwise you can simply start the server using functions framework and run either $test_local.sh$ or $test_multiple_reqs.sh$

