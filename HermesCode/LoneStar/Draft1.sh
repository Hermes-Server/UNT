#!/bin/bash
# Post draft version of psuClient Operational intent
echo "Posting draft psu client OI, Expect success"
# read
uuidgen > /tmp/OIuuid.txt
#curl -X PUT http://127.0.0.1:4443/psu_client/v1/operational_intent_references/`cat /tmp/OIuuid.txt` -H 'Content-Type: application/json' -d @./req_draft_route_1_v1.json
curl -X PUT http://aam-ntcohort.eng.unt.edu:443/psu_client/v1/operational_intent_references/`cat /tmp/OIuuid.txt` -H 'Content-Type: application/json' -d @./req_draft_route_1_v1.json

# read
