#!/bin/bash
# Post of Constraint
echo "Posting Constraint, Expect success"
curl -X POST http://aam-ntcohort.eng.unt.edu:443/psu/v1/constraints -H 'Content-Type: application/json' -d @./constraint_fixed.json
