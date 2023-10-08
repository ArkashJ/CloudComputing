#!/bin/bash 
for i in {1..10}
do
    rnd_num=$((RANDOM % 25000))

    echo "Random number is $rnd_num, between 0 and 12000. We can get correct or incorrect file number"
    # Testing the get request locally
    url="http://127.0.0.1:8080/hw2-arkjain-mini-internet/webdir/$rnd_num.html"
    echo "$url"

    echo "Testing GET request with valid file number"
    curl -X GET $url -I
done
