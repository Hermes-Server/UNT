#!/bin/bash
# Post draft version of psuClient Operational intent
echo "Posting draft psu client OI, Expect success"
# read
#curl -X PUT http://aam-ntcohort.eng.unt.edu:443/psu_client/v1/operational_intent_references/`cat /tmp/OIuuid.txt`/9d158f59-80b7-4c11-9c0c-8a2b4d936b2d_activate -H 'Content-Type: application/json' -d @./end_req.json
curl -X PUT http://aam-ntcohort.eng.unt.edu:443/psu_client/v1/operational_intent_references/`cat /tmp/OIuuid.txt`/EKebzYBjAOffVZvGqYyXsjTIXpuKDqDdsjAPAED8BMw_ -H 'Content-Type: application/json' -d @./req_end_route_2_v1.json


# read
