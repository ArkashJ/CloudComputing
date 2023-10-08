#!/bin/bash 
rnd_num=$((RANDOM % 10000))
rnd_invalid_num=$((RANDOM % 10001+10000))

echo "Random number is $rnd_num"
echo "Random invalid number is $rnd_invalid_num"


# Testing the get request on cloud
url="https://function-1-vpve2xlynq-uk.a.run.app/function-1/hw2-arkjain-mini-internet/mini_internet_test/$rnd_num.html"
curl -X GET $url -I

echo "Testing GET request with invalid file number"
curl -X GET "https://function-1-vpve2xlynq-uk.a.run.app/function-1/hw2-arkjain-mini-internet/mini_internet_test/$rng_invalid_num.html" -I

echo "Running PUT, POST, DELETE, HEAD, OPTIONS, TRACE, CONNECT requests on the same file"
curl -X PUT $url -I
curl -X DELETE $url -I
curl -X POST $url -I
curl -X HEAD $url -I
curl -X OPTIONS $url -I
curl -X TRACE $url -I
curl -X CONNECT $url -I
