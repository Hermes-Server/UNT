#!/bin/bash
# Post draft version of psuClient Operational intent
echo "Posting draft psu client OI, Expect success"
# read
#curl -X PUT http://aam-ntcohort.eng.unt.edu:443/psu_client/v1/operational_intent_references/`cat /tmp/OIuuid.txt` -H 'Content-Type: application/json' -d @./draft_req.json
curl -X PUT http://aam-ntcohort.eng.unt.edu:443/psu_client/v1/operational_intent_references/`cat /tmp/OIuuid.txt`/AkgckosgQHl9WgtT48IQlNKjx-1Rj7Tz82YJVU5LundTprWWxXvibJL1_iw3HqgH -H 'Content-Type: application/json' -d @./req_accept_route_1_v1.json

# read
