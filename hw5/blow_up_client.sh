#!/bin/bash

# Set the number of clients to run
NUM_CLIENTS=2

# Start the clients
for i in $(seq 1 $NUM_CLIENTS); do
    python3 http-client.py -d 35.208.125.55  -p 5000 -n 50000 -i 9999 -b /hw2-arkjain-mini-internet -w mini_internet_test -r 137 &
done

# Wait for all the clients to finish
wait

# Print the results
echo "All clients finished running."
