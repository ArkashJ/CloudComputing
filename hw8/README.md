1) Make 2 VMs in different zones and use a network load balancer
2) Modify web server code to return name of the zone server is running in
3) Modify client to extract and print new response header from the previous step
4) Kill the web server and note how fast the load balancer is able to detect and redirect traffic to the other server
5) After traffic is redirected, note how fast the load balancer is able to detect that the server is back up and redirect traffic back to it
