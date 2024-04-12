#!/bin/bash
# Delete the database tables and rectrete them
echo Enter database password fot unt
mysql -uadmin -p < ./HermesDataHub.sql --host 129.120.151.252
