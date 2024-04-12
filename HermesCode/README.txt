HermesDataHub
Contains Hermes Data Hub server code
connections.py		- Settings to connect to the mySql database
endpoints.py		- The endpoints of partners 
HermesDataHub.py	- The startup, Hermes endpoints to receive and forward messages
processData.py		- Validating the JSON payloads
 
HermesDataHub.sql	- SQL statements to delete and recreate the tables in the unt muSQL database
resetDB.sh		- Runs the contents of HermesDataHub.sql

The messages processed by HermesDataHub are
1) PSU Client Operational Intent:
These messages are received from LoneStar.
These are passed directly to Avianco for processing.
The response from Avianco is returned to LoneStar.
The OI is created in Draft state using the endpoint /psu_client/v1/operational_intent_references/<string:entityID> (PUT)
Changes to Accept, Activate and End states are done using the endpoint /psu_client/v1/operational_intent_references/<string:entityID>/<string:ovn> (PUT), where ovn is the Opaque Version Number received in the previous response.

2) PSU Operational Intent:
These endpoints are not currently used:
/psu/v1/operationalIntents (POST)
/psu/v1/operationalIntents/<string:entityID> (GET)
/psu/v1/operationalIntents/<string:entityID>/telemetry (GET)

3) Telemetry
Endpoint /psu/v1/telemetry (POST)
Message comes from Avianco. Hermes responds and forwards to CASA and LoneStar.

4) Constraints (Weather CC)
Endpoints:
/psu/v1/constraints (POST)
/psu/v1/constraints/<string:entityID> (GET)
Weather CC is posted by CASA to Hermes. Hermes responds to CASA and forwards to Frequentis, which forwards to Avianco.

5) Log
This endpoint is used internally to display log file.
