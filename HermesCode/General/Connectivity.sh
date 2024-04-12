#!/bin/bash
echo Hit Enter to test connectivity with Avianco
read
curl -X POST \
	'https://app.avianco.io:2002/oauth/v1/token' \
	-H 'accept: application/json' \
        -H 'x-api-key: WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X' \
	-H 'Content-type: application/json' \
	-d '{"email": "ravisub@gmail.com", "password": "Hermes@123"}'
echo

echo Hit Enter to test connectivity with Frequentis
read
. ./op_functions
echo "$(authHeader)"
echo

# Test connectivity with LoneStar

# TEst connectivity with CASA
echo Hit Enter to test connectivity with CASA
read
curl -X POST \
	'https://emmy8.casa.umass.edu:8046/telemetry' \
	-H 'accept: application/json' \
	-H 'Content-type: application/json' \
	-d '{"telemetry": "yrtemelet"}'
