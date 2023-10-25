## TODO
    - Add cloud SQL db to project and make a schema obeying 2nd NF
    - Country, client Ip, gender, age, income, is_banned_, time of day and requested file
    - Modify code to add it to your 2nf db
    - Make a new VM
        - Add permissions for library
        - 200 should be logged in a new table
    - Use curl to test it out
    - Make the same random seed, 2 clients each making 50k requests each
        - Compute stats like number of successful and unsuccessful requests
        - banned countries reqs
        - male vs female
        - top 5 senders
        - age group with most reqs?
        - income group with most reqs?
    
    a) Modify code to make a 2NF table and add it to your cloud SQL db
        - Table 1: country, is_banned_, time of day and requested file
        - Table 2: client_ip, age, income

## Notes
    - Make sure to make a private IP
    - Make new VMs and give them permissions to access the database

### Useful commands
```
gcloud sql connect DATABASE_INSTANCE --user=root --quiet 
```

```
import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import socket, struct
import sqlalchemy
```

### Useful links
- https://github.com/GoogleCloudPlatform/cloud-sql-python-connector/blob/main/samples/notebooks/mysql_python_connector.ipynb
- https://dev.mysql.com/downloads/mysql/
- https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html#protocol_overview
- https://cloud.google.com/sql/docs/mysql/language-connectors
- https://docs.google.com/presentation/d/1u2EA9-9X_dNn8RBdBivoCuuxwGpdQV7YCcH6SClZCgY/edit#slide=id.g258da33442f_0_141
- https://docs.google.com/presentation/d/120uEEuhQNR984r-iGnGD5GELDZVFRm3RGC1N0gXTNrA/edit#slide=id.g27446ef6af8_0_70


- Information on cloud connectors - https://cloud.google.com/sql/docs/mysql/connect-connectors#python
- Github showing how to make a pool connection - https://github.com/GoogleCloudPlatform/cloud-sql-python-connector#how-to-use-this-connector


### Useful commands
1) Get the status of your VM

```
sudo journalctl -u google-startup-scripts.service -f
```

2) Find and Kill a busy server
```
lsof -i :8080
kill -9 $PID
```

3) 
