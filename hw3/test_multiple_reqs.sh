#!/bin/bash 
for i in {1..100}
do
    rnd_num=$((RANDOM % 12000))

    echo "Random number is $rnd_num, between 0 and 12000. We can get correct or incorrect file number"
    url="http://34.134.24.55:5000/hw2-arkjain-mini-internet/mini_internet_test/$rnd_num.html"
    echo "$url"

    echo "Testing GET request with valid file number"
    curl -X GET $url -I
done
