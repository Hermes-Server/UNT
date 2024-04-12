#!/bin/bash
# Post first Telemetry
echo "Posting telemetry, Expect success"
#curl -X POST http://aam-ntcohort.eng.unt.edu:443/psu/v1/telemetry -H 'Content-Type: application/json' -d @./testTelemetry.json
curl -X POST http://aam-ntcohort.eng.unt.edu:443/psu/v1/telemetry -H 'Content-Type: application/json' -d \
'{
  "operational_intent_id": "'`cat /tmp/OIuuid.txt`'",
  "telemetry": {
    "time_measured": {
      "value": "2022-04-12T23:20:50.52Z",
      "format": "RFC3339"
    },
    "position": {
      "longitude": -118.456,
      "latitude": 34.123,
      "accuracy_h": "HAUnknown",
      "accuracy_v": "VAUnknown",
      "extrapolated": false,
      "altitude": {
        "value": 1000.5,
        "reference": "W84",
        "units": "M"
      }
    },
    "velocity": {
      "speed": 200.1,
      "units_speed": "MetersPerSecond",
      "track": 120.5,
      "speed_type": "GROUND"
    }
  },
  "next_telemetry_opportunity": {
    "value": "2022-04-12T23:20:50.52Z",
    "format": "RFC3339"
  },
  "aircraft_registration": "uam107"
}'

