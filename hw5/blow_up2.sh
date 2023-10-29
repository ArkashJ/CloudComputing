#!/bin/bash

# Set the number of clients to run
NUM_CLIENTS=2

# Start the clients
for i in $(seq 1 $NUM_CLIENTS); do
    python3 http-client.py -d 127.0.0.1 -p 8000  -n 100 -i 13999 -b /hw2-arkjain-mini-internet -w mini_internet_test -r 1337 &
done

# Wait for all the clients to finish
wait

# Print the results
echo "All clients finished running."
