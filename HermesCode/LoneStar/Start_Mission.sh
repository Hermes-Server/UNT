#!/bin/bash
echo "Posting UAV command"
# read
#curl -X PUT http://127.0.0.1:4443/v1/flight/commandUAV -H 'Content-Type: application/json' -d \
curl -X PUT http://aam-ntcohort.eng.unt.edu:443/v1/flight/commandUAV/ -H 'Content-Type: application/json' -d \
'{
  "flight_plan_id": "'`cat /tmp/OIuuid.txt`'",
  "type": "mav_command", 
  "command_id": 14,
  "drone_id": "LS101"
}'
# read
