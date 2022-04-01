sudo -u user_name postgres "MARKET"
ALTER USER user_name WITH PASSWORD 'passw0rd';
\q
exit
sudo service postgresql restart
psql -U postgres



taskset --cpu-list 0-3 python3 server.py