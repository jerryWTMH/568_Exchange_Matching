#!/bin/bash
find / -name pga_hba.conf
sed -i  '/^local all all peer/ s/peer/md5/' /etc/postgresql/12/main/pg_hba.conf
taskset --cpu-list 0-3 python3 server.py