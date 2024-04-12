from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# Prevent jsonify from sorting keys
# This helps in comparing input and output jsons
app.config["JSON_SORT_KEYS"] = False

@app.route("/psu/v1/telemetry", methods = ["POST"])
@app.route("/coord/v1/vehicle_telemetry", methods = ["POST"])
@app.route("/psu/v1/constraints", methods = ["POST"])
@app.route('/psu_client/v1/psu/v1/vehicle_telemetry', methods = ['POST'])
@app.route("/psu_client/v1/operational_intent_references/<string:entityID>", methods = ["PUT"])
@app.route("/psu_client/v1/operational_intents/telemetry/<string:entityID>", methods = ["POST"])
@app.route("/psu_client/v1/operational_intents/telemetry/<string:entityID>/<string:ovn>", methods = ["PUT"])
def DummyListener(entityID = None, ovn = None):
    if not request.is_json:
        response = jsonify({"message": "Request must be JSON", "status": status})
        status = 415
    else:
            data = request.get_json()
            print ("Received")
            print (data)
            response = jsonify({"message":"Got it"})
            status = 200
    return response, status


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=4444)
