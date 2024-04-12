
#!/bin/bash

#
# Proxy test
#

. ./op_functions

curl -i -v -X POST -H "$(authHeader)" -H "$APP_JSON" --data "@test-data/putConstraintDetailsParam2.json" https://fcilabs.net/proxy/psu/v1/constraints?uss_base_url=http://aam-ntcohort.eng.unt.edu:443/ 

exitln $?
