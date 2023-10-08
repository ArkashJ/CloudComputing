#!/bin/bash 
rnd_num=$((RANDOM % 10000))
rnd_invalid_num=$((RANDOM % 10001+10000))

echo "Random number is $rnd_num"
echo "Random invalid number is $rnd_invalid_num"


# Testing the get request locally
url="http://127.0.0.1:8080/hw2-arkjain-mini-internet/webdir/$rnd_num.html"
echo "$url"
echo "Testing GET request with valid file number"
curl -X GET $url -I

echo "Testing GET request with invalid file number"
curl -X GET "http://127.0.0.1:8080/hw2-arkjain-mini-internet/webdir/$rng_invalid_num.html" -I

echo "Running PUT, POST, DELETE, HEAD, OPTIONS, TRACE, CONNECT requests on the same file"
curl -X PUT $url -I
curl -X DELETE $url -I
curl -X POST $url -I
curl -X HEAD $url -I
curl -X OPTIONS $url -I
curl -X TRACE $url -I
curl -X CONNECT $url -I
