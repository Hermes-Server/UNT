from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# Prevent jsonify from sorting keys
# This helps in comparing input and output jsons
app.config["JSON_SORT_KEYS"] = False

@app.route("/v1/flight/commandUAV", methods=["PUT"])
def commandUAV():
    if not request.is_json:
        response = jsonify({"message": "Request must be JSON", "status": status})
        status = 415
    else:
        if request.method == "PUT": 
            data = request.get_json()
            print ("Received")
            print (data)
            print ("Responded")
            resp_data = {"status":"Ok"}
            response = jsonify(resp_data)
            status = 200
    return response, status

# psu client operational_intents endpoint (PUT)
# Request Operational Intent
@app.route("/psu_client/v1/operational_intent_references/<string:entityID>", methods=["PUT"])
# Modify Operational Intent
@app.route("/psu_client/v1/operational_intent_references/<string:entityID>/<string:ovn>", methods=["PUT"])
def psuClientOperationalIntents(entityID=None, ovn=None):
    # request type has to be json
    ovn = "9d158f59-80b7-4c11-9c0c-8a2b4d936b2d"
    if not request.is_json:
        response = jsonify({"message": "Request must be JSON", "status": status})
        status = 415
    else:
        if request.method == "PUT": 
            data = request.get_json()
            print ("Received")
            print (data)
            print ("Responded")
            resp_data =  {
                  "operational_intent_reference": {
                    "id": "2f8343be-6482-4d1b-a474-16847e01af1e",
                    "version": 1,
                    "ovn": "9d158f59-80b7-4c11-9c0c-8a2b4d936b2d",
                    "aircraft_registration": "AVI001",
                    "operator_name": "AVI",
                    "trajectory": [
                      {
                        "point_designator_uuid": "9d158f59-80b7-4c11-9c0c-8a2b4d936b20",
                        "point_designator": "ee123",
                        "point_type": "Vertiport",
                        "speed_type": "Vertiport",
                        "lat_lng_point": {
                          "lng": -118.456,
                          "lat": 34.123
                        },
                        "altitude": {
                          "value": -8000,
                          "reference": "W84",
                          "units": "M"
                        },
                        "time": {
                          "value": "1985-04-12T23:20:50.52Z",
                          "format": "RFC3339"
                        },
                        "speed": {
                          "speed": 200.1,
                          "units_speed": "MetersPerSecond",
                          "track": 120,
                          "speed_type": "GROUND"
                        },
                        "trajectory_property_array": [
                        {
                          "property_type": "WHEELS_OFF"
                        },
                        {
                          "property_type": "AIRPORT_REFERENCE_LOCATION"
                        }
                        ]
                      },
                      {
                        "point_designator_uuid": "9d158f59-80b7-4c11-9c0c-8a2b4d936b21",
                        "point_designator": "ee123",
                        "point_type": "Vertiport",
                        "speed_type": "Vertiport",
                        "lat_lng_point": {
                          "lng": -118.456,
                          "lat": 34.123
                        },
                        "altitude": {
                          "value": -8000,
                          "reference": "W84",
                          "units": "M"
                        },
                        "time": {
                          "value": "1985-04-12T23:20:50.52Z",
                          "format": "RFC3339"
                        },
                        "speed": {
                          "speed": 200.1,
                          "units_speed": "MetersPerSecond",
                          "track": 120,
                          "speed_type": "GROUND"
                        },
                        "trajectory_property_array": [
                        {
                          "property_type": "WHEELS_ON"
                        },
                        {
                          "property_type": "AIRPORT_REFERENCE_LOCATION"
                        }
                        ]
                      }
                    ],
                    "time_start": {
                      "value": "1985-04-12T23:20:50.52Z",
                      "format": "RFC3339"
                    },
                    "time_end": {
                      "value": "1985-04-12T23:20:50.52Z",
                      "format": "RFC3339"
                    },
                    "adaptation_id": "9d158f59-80b7-4c11-9c0c-8a2b4d936b22",
                    "state": "Draft",
                    "subscription_id": "string"
                  }
                }
            resp_data["operational_intent_reference"]["id"] = entityID
            state = data["state"]
            if (state == "Draft"):
                resp_data["operational_intent_reference"]["version"] = 1
                resp_data["operational_intent_reference"]["ovn"] = ovn + "_draft"
            elif (state == "Accept"):
                resp_data["operational_intent_reference"]["version"] = 1
                resp_data["operational_intent_reference"]["ovn"] = ovn + "_accept"
            elif (state == "Activate"):
                resp_data["operational_intent_reference"]["version"] = 1
                resp_data["operational_intent_reference"]["ovn"] = ovn + "_activate"
            elif (state == "End"):
                resp_data["operational_intent_reference"]["version"] = 1
                resp_data["operational_intent_reference"]["ovn"] = ovn + "_end"
            resp_data["operational_intent_reference"]["aircraft_registration"] = data["aircraft_registration"]
            resp_data["operational_intent_reference"]["operator_name"] = data["operator_name"]
            resp_data["operational_intent_reference"]["trajectory"] = data["trajectory"]
            resp_data["operational_intent_reference"]["time_start"] = data["time_start"]
            resp_data["operational_intent_reference"]["time_end"] = data["time_end"]
            resp_data["operational_intent_reference"]["adaptation_id"] = data["adaptation_id"]
            resp_data["operational_intent_reference"]["state"] = data["state"]

            response = jsonify(resp_data)
            status = 200
    return response, status


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=4445)
