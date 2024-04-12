################################################################################
## File:                                                                      ##
##     HermesDataHub.py                                                       ##
## Purpose:                                                                   ##
##     Handle HTTP requests for Data Hub                                      ##
##     Implements endpoints defined in                                        ##
##       github.com/nasa/uam-apis/blob/x4/openapi/psu/psu_api.yml             ##
## Author:                                                                    ##
##     Ravichandran Subramanian                                               ##
## Versions:                                                                  ##
##     Version      Comment                             Changed by   Date     ##
##     1.0.0        Initial                             Ravi Sub     20220504 ##
##     1.0.1        Add endpoints prefixed with /psu/v1 Ravi Sub     20220613 ##
##     1.0.2        Get token and subscriptions         Ravi Sub     20220616 ##
##     1.0.3        Removed endpoints without /psu/v1   Ravi Sub     20220621 ##
##                  Added forwarding of telemetry to FCI                      ##
##                  Added forwarding of OperationalIntent to FCI              ##
##                  Added forwarding of constraints to FCI                    ##
##                  Disabled FCI communications         Amila J      20230115 ##
##                  Implemented DSS subscriptions       Amila J      20230301 ##
##                  Added a loop for DSS subscriptions  Amila J      20230320 ##
##                  Added AAMTEX endpoint for Telemetry forwarding            ##
##                  Implemented Token System            Amila J      20230522 ##
##                  Added UNT Telemetry Endpoint        Amila J      20230522 ##
##                  Added AAMTEX token Verification     Amila J      20230604 ##
##                                                                            ##
## Copyright:                                                                 ##
##     (c) Hermes Autonomous Air Mobility 2022                                ##
################################################################################
from flask import Flask, request, jsonify
import processData
from datetime import timezone 
import datetime
import json
import requests
import connections
import endpoints
import urllib.parse
import socket
import sched
import time
from time import sleep
import threading
import uuid
from functools import wraps
import secrets
import base64
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

# Prevent jsonify from sorting keys
# This helps in comparing input and output jsons
app.config["JSON_SORT_KEYS"] = False

FMWKsched = 0

OAuthsched = 0
OAuth_token = ""
OAuthexpiresIn = 0

AAMsched = 0
AAMTEXaceessToken = ""
AAMexpiresIn = 0

DSSsched = 0
DSSexpiresIn = 0

AVIsched = 0
AVIaccessToken = ""
AVIrefreshToken = ""
AVIexpiresIn = 0

# Keep client Information
client_information = {
    's.nicoll@unmannedexperts.com': 'cR3MJ3owDoNI2UuIfpp1Sy2SeqQeds5a',
    'UNT': 'HLFOpidQcs9TxdGMVcu0UV9iNMXUYwSG',
    'client3': 'WtNVcv6NBOUBNgRgD5JesmjBULZQAyex',
}

# Token log (Saves the token and expiration time)
token_information = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        if token not in token_information:  
            
            jwks_url = 'https://accounts.aamtex.com/.well-known/psu/jwks.json'
            jwks = requests.get(jwks_url).json()

            for jwk in jwks['keys']:
                e_b64 = jwk['e']
                n_b64 = jwk['n']
    
            e_b64 = jwk['e']
            n_b64 = jwk['n']
            e = int.from_bytes(base64.urlsafe_b64decode(e_b64 + '=='), 'big')
            n = int.from_bytes(base64.urlsafe_b64decode(n_b64 + '=='), 'big')

            public_numbers = rsa.RSAPublicNumbers(e=e, n=n)
            public_key = public_numbers.public_key(default_backend())

            try:
                payload = jwt.decode(token,public_key, options={"verify_signature": True}, algorithms='RS256')

            except:
                return jsonify({'message': 'Invalid token!'}), 401
        
        if token in token_information:
            time = token_information.get(token)
            if time < str(datetime.datetime.now(timezone.utc)):
                return jsonify({'message': 'Token Expired'}), 401
            
        return f(*args, **kwargs)

    return decorated

@app.route("/forwards/constraints", methods=["POST"])
@app.route("/forwards/operations", methods=["POST"])
def forwards():
    objProcessData = processData.processData()
    remote = request.environ['REMOTE_ADDR']
    request_method = request.environ['REQUEST_METHOD']
    request_uri = request.url
    request_args = request.args
    request_time = datetime.datetime.now(timezone.utc)
    request_json = json.dumps("")
    request_headers = ""
    status = 200
    # request type has to be json
    if not request.is_json:
        status = 415
        response = jsonify({"message": "Request must be JSON", "status": status})
    else:
        if request.method == "POST": 
            data = request.get_json()
            request_json = json.dumps(data)
            request_headers = json.dumps(str(request.headers))
            url = request_args["forward_url"]
            #headers={'x-access-token': AVIaccessToken, 'Content-Type':'application/json', 'x-api-key':'WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X', 'accept':'application/json'}
            headers={'Content-Type':'application/json', 'accept':'application/json'} # What todo with headers if needed?
            response, status = postExternal("POST", url, headers, data)

        # End - if request.method == "POST":
    # End - if not request.is_json:
    invalid = ""
    response_time = datetime.datetime.now(timezone.utc)
    response_json = json.dumps(response)
    objProcessData.logPut("IN", remote, request_uri, request_method, request_time, request_headers, request_json, response_time, response_json, invalid, status)
    return response, status
# End - def forwards():

@app.route("/psu_client/v1/flight/commandUAV", methods=["POST"])
def commandUAV():
    objProcessData = processData.processData()
    remote = request.environ['REMOTE_ADDR']
    request_method = request.environ['REQUEST_METHOD']
    request_uri = request.url
    request_time = datetime.datetime.now(timezone.utc)
    request_json = json.dumps("")
    request_headers = ""
    # request type has to be json
    if not request.is_json:
        status = 415
        response = jsonify({"message": "Request must be JSON", "status": status})
    else:
        if request.method == "POST": 
            data = request.get_json()
            request_json = json.dumps(data)
            request_headers = json.dumps(str(request.headers))
            print("************", flush = True)
            print("Request", flush=True)
            print(data, flush=True)
            print("************", flush = True)

            url = endpoints.avi_commandUAV_endpoint()
            headers={'x-access-token': AVIaccessToken, 'Content-Type':'application/json', 'x-api-key':'WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X', 'accept':'application/json'}
            response, status = postExternal("POST", url, headers, data)

            result = {"status":500}
            if (status < 400):
                try:
                    result = objProcessData.putCommandUAV(data)
                except:
                    pass
            # End - if (status < 400):
            print("Hermes status: " + str(result["status"]), flush = True)
        # End - if request.method == "PUT":
    # End - if not request.is_json:
    if "invalid" in result.keys():
        invalid = result["invalid"]
    else:
        invalid = ""
    # End - if "invalid" in result.keys():
    response_time = datetime.datetime.now(timezone.utc)
    response_json = json.dumps(response)
    objProcessData.logPut("IN", remote, request_uri, request_method, request_time, request_headers, request_json, response_time, response_json, invalid, status)
    return response, status
# End - def commandUAV():

# psu client operational_intents endpoint (PUT)
# Request Operational Intent
@app.route("/psu_client/v1/operational_intent_references/<string:entityID>", methods=["PUT"])
# Modify Operational Intent
@app.route("/psu_client/v1/operational_intent_references/<string:entityID>/<string:ovn>", methods=["PUT"])
@token_required
def psuClientOperationalIntents(entityID=None, ovn=None):
    objProcessData = processData.processData()
    remote = request.environ['REMOTE_ADDR']
    request_method = request.environ['REQUEST_METHOD']
    request_uri = request.url
    request_time = datetime.datetime.now(timezone.utc)
    request_json = json.dumps("")
    request_headers = ""
    # request type has to be json
    if not request.is_json:
        status = 415
        response = jsonify({"message": "Request must be JSON", "status": status})
    else:
        if request.method == "PUT": 
            data = request.get_json()
            request_json = json.dumps(data)
            request_headers = json.dumps(str(request.headers))
            parts = request.path.split("/")
            if (len(parts) == 5): # Initial
                if ovn is None:
                    ovn = ""
#            elif (len(parts) == 6): # Change
            # End - if (len(parts) == 5) # Initial
            print("************", flush = True)
            print("Request", flush=True)
            print(data, flush=True)
            print("************", flush = True)

            url = endpoints.avi_psu_client_operationalIntents_endpoint(entityID, ovn)
            headers={'x-access-token': AVIaccessToken, 'Content-Type':'application/json', 'x-api-key':'WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X', 'accept':'application/json'}
            response, status = postExternal("PUT", url, headers, data)

            result = {"status":500}
            if (status < 400):
                try:
                    result = objProcessData.putPsuClientOperationalIntent(entityID, ovn, data)
                except:
                    pass
            # End - if (status < 400):
            print("Hermes status: " + str(result["status"]), flush = True)
        # End - if request.method == "PUT":
    # End - if not request.is_json:

    if "invalid" in result.keys():
        invalid = result["invalid"]
    else:
        invalid = ""
    # End - if "invalid" in result.keys():
    response_time = datetime.datetime.now(timezone.utc)
    response_json = json.dumps(response)
    if (status < 400):
        print("ËntityID: " + entityID, flush = True)
        rr = json.loads(response)
        #print("*******Uncomment next line before working with Avianco!********")
        print("ovn: " + rr["operational_intent_reference"]["ovn"], flush = True)
    objProcessData.logPut("IN", remote, request_uri, request_method, request_time, request_headers, request_json, response_time, response_json, invalid, status)
    return response, status
# End - def psuClientOperationalIntents(entityID=None, ovn=None):



# operational_intents endpoint (POST and GET)
# Notify of changed Operational Intent Details
@app.route("/psu/v1/operational_intents", methods=["POST"])
# Retrieve the specified Operational Intent Details
#####@app.route("/psu/v1/operationalIntents/<string:entityID>", methods=["GET"])
# Query detailed information on the position of an Operational Intent
#####@app.route("/psu/v1/operationalIntents/<string:entityID>/telemetry", methods=["GET"])
def operationalIntents(entityID=None):
    
    objProcessData = processData.processData()
    remote = request.environ['REMOTE_ADDR']
    request_method = request.environ['REQUEST_METHOD']
    request_uri = request.url
    request_time = datetime.datetime.now(timezone.utc)
    request_json = json.dumps("")
    request_headers = ""
    # request type has to be json
    if not request.is_json:
        status = 415
        response = jsonify({"message": "Request must be JSON", "status": status})
    else:
        if request.method == "POST":    # Notify of changed Operational Intent Details
            data = request.get_json()
            request_json = json.dumps(data)
            request_headers = json.dumps(str(request.headers))
            try:
                result = objProcessData.postOperationalIntent(data)
            except:
                result = {"status":500}
                pass
            status = result["status"]
            response = jsonify({"status": status})
            
        elif request.method == "GET":
            parts = request.path.split("/")
            if len(parts) == 5: # Retrieve the specified Operational Intent
                try:
                    result = objProcessData.postOperationalIntent(data)
                except:
                    result = {"status":500}
                    pass
                status = result["status"]
                if result["status"] == 200: # Operational Intent retrieved successfully
                    response = jsonify(result["operational_intent"])
                else:
                    response = jsonify({"status": status})
                # End - if result["status"] == 200: # Operational Intent retrieved successfully
            elif len(parts) == 6:
                if parts[5] == "telemetry": # Query detailed information on the position of an Operational Intent
                    try:
                        result = objProcessData.getTelemetry(entityID)
                    except:
                        result = {"status":500}
                        pass
                    status = result["status"]
                    if result["status"] == 200: # Telemetry retrieved successfully
                        response = jsonify(result["tel"])
                    else:
                        response = jsonify({"status": status})
                    # End - if result["status"] == 200: # Telemetry retrieved successfully
                else:
                    print("Third component of URI should be only telemetry")  # Should not get here
                # End - if parts[5] == "telemetry": # Query detailed information on the position of an Operational Intent
            else:
                print("URI should have only 2 or 3 components")  # Should not get here
            # End - if len(parts) == 5: # Retrieve the specified Operational Intent
        # End - if request.method == "POST":    # Notify of changed Operational Intent Details
    # End - if not request.is_json:

    if "invalid" in result.keys():
        invalid = result["invalid"]
    else:
        invalid = ""
    # End - if "invalid" in result.keys():
    response_time = datetime.datetime.now(timezone.utc)
    response_json = json.dumps(result)
    objProcessData.logPut("IN", remote, request_uri, request_method, request_time, request_headers, request_json, response_time, response_json, invalid, status)
    return response, status
# End - def operationalIntents(entityID=None):


# Dummy endpoint to post Telemetry
# Post telemetry for an Operational Intent
@app.route("/psu/v1/telemetry", methods=["POST"])
@token_required
def telemetry():
    objProcessData = processData.processData()
    remote = request.environ['REMOTE_ADDR']
    request_method = request.environ['REQUEST_METHOD']
    request_uri = request.url
    request_time = datetime.datetime.now(timezone.utc)
    request_json = json.dumps("")
    request_headers = ""
    result = {"status":500}
    # request type has to be json
    if not request.is_json:
        status = 415
        response = jsonify({"message": "Request must be JSON", "status": status})
    else:
        data = request.get_json()
        print(data['operational_intent_id'])
        entityID = data['operational_intent_id']
        
        #Forwarding to Lonestar
        url = endpoints.lst_telemetry_endpoint ()
        headers = {'Authorization':'Bearer ' + "574DC72C-1AD5-4984-8306-50B372DEA15F", "AppName": "Hermes", 'Content-Type':'application/json'}
        postExternal("POST", url, headers, data)

        #Forwarding to AAMTEX
        url = endpoints.AAMTEX_telemetry_endpoint(entityID)
        headers = {'Authorization':'Bearer '+ AAMTEXaceessToken, 'Content-Type':'application/json'}
        postExternal("POST", url, headers, data)


        #Forwarding to Avianco
        url = endpoints.avi_psu_client_operationalIntents_telemetry(entityID)
        headers={'x-access-token': AVIaccessToken, 'Content-Type':'application/json', 'x-api-key':'WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X', 'accept':'application/json'}
        postExternal("POST", url, headers, data)

        #Forwarding to Resilienx
        url = endpoints.resilienx_telemetry_url()
        headers = {'Content-Type':'application/json'}
        postExternal("POST", url, headers, data)

        #Forwarding to UNT
        url = endpoints.UNT_Telemetry()
        headers = {'Content-Type':'application/json'}
        postExternal("POST", url, headers, data)

          

        request_json = json.dumps(data)
        request_headers = json.dumps(str(request.headers))
        print("************", flush = True)
        print("Request", flush=True)
        print(data, flush=True)
        print("************", flush = True)
        try:
            result = objProcessData.postTelemetry(data)
            print(data)
        except:
            pass
        print("Hermes status: " + str(result["status"]), flush = True)
        status = result["status"]
        response = jsonify({"status": status})
    # End - if not request.is_json:

    if "invalid" in result.keys():
        invalid = result["invalid"]
    else:
        invalid = ""
    # End - if "invalid" in result.keys():
    response_time = datetime.datetime.now(timezone.utc)
    response_json = json.dumps(result)
    objProcessData.logPut("IN", remote, request_uri, request_method, request_time, request_headers, request_json, response_time, response_json, invalid, status)
    return response, status
# End - def telemetry():



# constraints endpoint (POST and GET)
# Notify of changed Constraint Details (usually as a requirement of previous interactions with the DSS)
@app.route("/psu/v1/constraints", methods=["POST"])
# Retrieve the specified Constraint Details
@app.route("/psu/v1/constraints/<string:entityID>", methods=["GET"])
def constraints(entityID=None):
    
    objProcessData = processData.processData()
    remote = request.environ['REMOTE_ADDR']
    request_method = request.environ['REQUEST_METHOD']
    request_uri = request.url
    request_time = datetime.datetime.now(timezone.utc)
    request_json = json.dumps("")
    request_headers = ""
    # request type has to be json
    if not request.is_json:
        status = 415
        response = jsonify({"message": "Request must be JSON", "status": status})
    else:
        status = 404
        if request.method == "POST":
            data = request.get_json()
            request_json = json.dumps(data)
            request_headers = json.dumps(str(request.headers))
            print("************", flush = True)
            print("Request", flush=True)
            print(data, flush=True)
            print("************", flush = True)
            result = {"status":500}
            try:
                result = objProcessData.postConstraint(data)
            except:
                result = {"status":500}
                pass
            print("Hermes status: " + str(result["status"]), flush = True)
            status = result["status"]
            response = jsonify({"status": status})
            
        elif request.method == "GET":
                try:
                    result = objProcessData.getConstraint(entityID)
                except:
                    result = {"status":500}
                    pass
                if result["status"] == 200:
                    status = result["status"]
                    response = jsonify(result["constraint"])
                else:
                    status = result["status"]
                    response = jsonify({"status": status})
                # End - if result["status"] == 200:
        # End - if request.method == "POST":
    # End - if not request.is_json:

    if "invalid" in result.keys():
        invalid = result["invalid"]
    else:
        invalid = ""
    # End - if "invalid" in result.keys():
    response_time = datetime.datetime.now(timezone.utc)
    response_json = json.dumps(result)
    objProcessData.logPut("IN", remote, request_uri, request_method, request_time, request_headers, request_json, response_time, response_json, invalid, status)
    return response, status
# End - def constraints(entityID=None):

# Token Endpoint (POST)
@app.route('/token', methods=['POST'])
def token():
    client_id = request.json.get('client_id')
    secret_key = request.json.get('secret_key')
    
    if not client_id or not secret_key:
        return jsonify({'message': 'Client ID or secret key is missing!'}), 400

    if client_information.get(client_id) != secret_key:
        return jsonify({'message': 'Invalid client credentials!'}), 401

    token = str(secrets.token_hex(64))
    expires_in = str(datetime.datetime.now(timezone.utc)+ datetime.timedelta(hours = 24))
    token_information[token] = expires_in
    
    print("Token Issued for",client_id,".Token is",token,"and expiration time",expires_in)
    
    with open('tokens.txt', 'w') as convert_file:
     convert_file.write(json.dumps(token_information))
    
    return jsonify({'token': token, 'expires_in':'86400'}), 200
# End - def token()

# log endpoint (POST and GET)
# Get logged data
@app.route("/psu/v1/logs", methods=["GET"])
def logGet():
    objProcessData = processData.processData()
    result, status = objProcessData.logGet()
    response = jsonify(result)
    return response, status
# End - def logGet():

@app.route("/")
def HermesHUB():
    return "Welcome to Hermes Data Hub"



def getAVItoken():
    # Get Token from Avianco
    global AVIaccessToken
    global AVIrefreshToken
    global AVIexpiresIn
    headers={'Content-Type':'application/json', 'x-api-key':'WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X', 'accept':'application/json'}
    data=json.dumps({'email':'ravisub@gmail.com', 'password':'Hermes@123'})
    try:
        tokenResponse = requests.post(endpoints.avi_token_endpoint(), headers = headers, data = data)
        if (tokenResponse.status_code != 200):
            print("Unable to get token")
            exit()
        # End - if (tokenResponse.status_code != 200):
        AVIaccessToken = tokenResponse.json()["access_token"]
        AVItokenType = tokenResponse.json()["token_type"]
        AVIexpiresIn = tokenResponse.json()["expires_in"]
        AVIrefreshToken = tokenResponse.json()["refresh_token"]
    except:
        AVIaccessToken = "123"
        AVIexpiresIn = 60
        pass
    print("Got AVI token, 2 expires in " + str(AVIexpiresIn) + " seconds")
# End - def getAVItoken():


def renewAVItoken():
    global AVIaccessToken
    global AVIrefreshToken
    global AVIexpiresIn
    headers={'Content-Type':'application/json', 'x-access-token':AVIaccessToken, 'x-api-key':'WTFKG69-KRG4PSS-JFXX8PV-N3WGT0X', 'accept':'application/json'}
    data=json.dumps({'refreshToken':AVIrefreshToken})
    try:
        tokenResponse = requests.post(endpoints.avi_refresh_endpoint(), headers = headers, data = data)
        if (tokenResponse.status_code != 200):
            print("Unable to get token")
            exit()
        # End - if (tokenResponse.status_code != 200):
        AVIaccessToken = tokenResponse.json()["access_token"]
        AVItokenType = tokenResponse.json()["token_type"]
        AVIexpiresIn = tokenResponse.json()["expires_in"]
        AVIrefreshToken = tokenResponse.json()["refresh_token"]
    except:
        AVIaccessToken = "123"
        AVIexpiresIn = 3600           #changed to prevent AVI looping (original value was 60)
        pass
    print("Got AVI token, 3 expires in " + str(AVIexpiresIn) + " seconds")
# End - def renewAVItoken():



def AVIloop(nextsch):
    global AVIsched
    global AVIexpiresIn
    renewAVItoken()
#    nextsch = AVIexpiresIn - (AVIexpiresIn - 15)
    nextsch = AVIexpiresIn - 60
    print("AVI Scheduling in " + str(nextsch) + " seconds.", flush=True)
    AVIsched.enter(nextsch, 1, AVIloop, argument = (AVIexpiresIn,))
# End - def AVIloop(nextsched)



def DSS_subscriptions():
    global AAMTEXaceessToken
    global DSSexpiresIn

    dsssubscriptionID = uuid.uuid4()
    timestart = datetime.datetime.now(timezone.utc)
    timestart = timestart.isoformat()
    timeend =  datetime.datetime.now(timezone.utc) + datetime.timedelta(hours = 24)
    timeend = timeend.isoformat()

    

    headers = {'Authorization':'Bearer '+ AAMTEXaceessToken, 'Content-Type':'application/json','accept': 'application/json'}
    data = {
                    "extents": {
                        "volume": {
                                  
                                    "outline_polygon": {
                                        "vertices": [
                                                        {"lng": -97.291, "lat": 33.496}, #{"lng": -97.197, "lat": 33.201},
                                                        {"lng": -96.746, "lat": 33.448}, #{"lng": -97.313, "lat": 32.985},
                                                        {"lng": -96.727, "lat": 32.948}, #{"lng": -97.152, "lat": 33.254}
                                                        {"lng": -97.312, "lat": 32.985}
                                                    ]
                                                        },
                                                                        "altitude_lower": {
                                                                        "value": 10,
                                                                        "reference": "W84",
                                                                        "units": "M"
                                                        },
                                                                        "altitude_upper": {
                                                                        "value": 1000,
                                                                        "reference": "W84",
                                                                        "units": "M"
                                                        }
                                                            },
                                                                        "time_start": {
                                                                        "value": timestart,
                                                                        "format": "RFC3339"
                                                            },
                                                                        "time_end": {
                                                                        "value": timeend,
                                                                        "format": "RFC3339"
                                                        }
                                                            },
                                                                    "uss_base_url": "http://aam-ntcohort.eng.unt.edu:443",
                                                                    "notify_for_operational_intents": True,
                                                                    "notify_for_constraints": True                  
                                                            }
                                                            
                                                            
    subscriptionResponse = requests.put(endpoints.DSS_constraint_subscription_endpoint() + "/" + str(dsssubscriptionID), headers=headers ,json= data)
    if (subscriptionResponse.status_code == 200):
        print("Subscribed to DSS")
        DSSexpiresIn = 86400
    elif (subscriptionResponse.status_code != 200):
        print("DSS subscription error : ",subscriptionResponse.status_code)
#End DSS_subscription

def DSSloop(nextsch):
    global DSSsched
    global DSSexpiresIn

    DSS_subscriptions()

    nextsch = DSSexpiresIn - 300
    print("DSS Subscription Renewing in " + str(nextsch) + " seconds.", flush=True)
    DSSsched.enter(nextsch, 1, DSSloop, argument = (DSSexpiresIn,))
# End - def DSSloop(nextsched)


def getOAuth_token():

    global OAuth_token


    auth_server_url = "https://unt.fraihmwork.resilienx.com/auth/realms/dev/protocol/openid-connect/token"
    client_id = 'hermes-client'
    client_secret = '67b70985-cad0-4a2d-8cbf-f6ad8480daf6'

    token_req_payload = {'grant_type': 'client_credentials'}

    try:
        token_response = requests.post(auth_server_url,
        data=token_req_payload, verify=False, allow_redirects=False,
        auth=(client_id, client_secret))

        if token_response.status_code == 200:
            print("Successfuly obtained OAuth token")
            token = json.loads(token_response.text)
            print("Renewing OAuth token in 86400 seconds.", flush=True)


    except:
        print("OAuth request failed")
			 
                

    try:
        OAuth_token = token['access_token']
        #print('OAuth Token: ',OAuth_token)
    except:
        print("OAuth token error")
# End - def getOAuth_token():


def OAuthloop(nextsch):
    global OAuthsched
    global OAuthexpiresIn
    getOAuth_token()
    nextsch = 86340
    OAuthsched.enter(nextsch, 1, OAuthloop, argument = (OAuthexpiresIn,))
# End - def OAuthloop(nextsch):


def FRMWKloop(nextsch):
    global FMWKsched
    global OAuth_token
    global AAMTEXaceessToken
    FRMWK_timeout = 86400
    nextsch = 86400 - 60


    timestart = datetime.datetime.now(timezone.utc)
    timestart = timestart.isoformat()
    timeend =  datetime.datetime.now(timezone.utc) + datetime.timedelta(hours = 24)
    timeend = timeend.isoformat()

    token = AAMTEXaceessToken

    data = {

                        "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "Hermes",
                        "description": "System is responding to external requests",
                        "componentLibraryName": "unkown",
                                            "state": {
                                                "state": "ONLINE",
                                                "description": "System is responding to external requests"
                                            },
                                            "version": {
                                                "hardware": "Linux",
                                                "software": "Python",
                                                "firmware": "BIOS",
                                                "configuration": "Server"
                                            },
                                                                "physicalLocation": "UNT",
                                                                "networkAddress": "http://aam-ntcohort.eng.unt.edu:443/psu/v1/telemetry",
                                                                "manufacturer": "Hermes",
                                                                "model": "---",
                                                                "startupTime": timestart,
                                                                "timeOfValidity": timeend,
                                                                "timeout": 86400,
                                                                "extensions": {
                                                                    "additionalProp1": {}
                                                                }
                                                                }
    

    HermesID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    TelemID = "6f79fa9b-600e-46a8-8be5-a03b69db48fb"
    headers = {'Content-Type':'application/json','Authorization': 'Bearer ' + token}
    ping_fraihmwork = endpoints.resilienx_fraihmwork()
    Refresh_Hermes = endpoints.resilienx_fraihmwork_refresh(HermesID)
    Refresh_Telem = endpoints.resilienx_fraihmwork_refresh(TelemID)



    try:
        response = requests.post(ping_fraihmwork,  headers=headers, json=data)
        if(str(response.status_code)[0] == '2'):
            if response.status_code == 208:
                response1 = requests.post(Refresh_Telem,  headers=headers)
                response2 = requests.post(Refresh_Hermes,  headers=headers)

                if response1.status_code and response2.status_code == 200:
                    print("Refreshed FRAIHMWORK:", response1.status_code)
                    
                else:
                    print("One or more FRAIHMWORK ping is at fault. CHECK CONDITION!")
                    print("First ping response:", response1.status_code)
                    print("Second ping response:", response2.status_code)
            else:
                print("Pinged FRAIHMWORK:", response1.status_code)
                print(response.text)
    
        elif(str(response.status_code)[0] != '2'):
            print("Ping error towards FRAIHMWORK", response.status_code)
            print(response.text)
    except:
        print("FRAIHMWORK request failed:", response.status_code)

    print("FRAIHMWORK ping Scheduling in " + str(nextsch) + " seconds.", flush=True)
    FMWKsched.enter(nextsch, 2, FRMWKloop, argument = (FRMWK_timeout,))
# End - def FRMWKloop(nextsch):


def postExternal(method, url, headers, data):
    print("************", flush = True)
    print("Forwarding to: " + url, flush=True)
    request_time = datetime.datetime.now(timezone.utc)
    try:
        if (method == "PUT"):
            response = requests.put(url, headers = headers, json = data)
        elif (method == "POST"):
            response = requests.post(url, headers = headers, json = data)
        response_status_code = response.status_code
        response_text = response.text
    except:
        response_status_code = 500
        response_text = ""
        pass
    response_time = datetime.datetime.now(timezone.utc)
    print("Posted external, status: " + str(response_status_code), flush = True)
    print("Response: ", flush = True)
    print(response_text, flush = True)
    print("************", flush = True)

    parsed_url = urllib.parse.urlparse(url)
    hostname = parsed_url.netloc.split(':')[0]
    remote = socket.gethostbyname(hostname)

    objProcessData = processData.processData()
    request_json = json.dumps(data)
    request_headers = json.dumps(headers)
    if (response_text == ""):
        response_json = json.dumps("")
    else:
        response_json = json.dumps(response.json())
    objProcessData.logPut("OUT", remote, url, method, request_time, request_headers, request_json, response_time, response_json, "", response_status_code)
    return response_json, response_status_code

# End - def postExternal(url, headers, data):

def runAAMthread():
    global AAMsched
    global AAMexpiresIn
    AAMexpiresIn = 0
    AAMsched = sched.scheduler(time.time, time.sleep) 
    AAMsched.enter(0, 1, AAMloop, argument = (AAMexpiresIn,))
    AAMsched.run()
# End - def runAAMthread()

def runDSSthread():
    global DSSsched
    global DSSexpiresIn
    DSSexpiresIn = 0
    DSSsched = sched.scheduler(time.time, time.sleep) 
    DSSsched.enter(0, 1, DSSloop, argument = (DSSexpiresIn,))
    DSSsched.run()
# End - def runDSSthread()


def runAVIthread():
    global AVIsched
    global AVIexpiresIn
    AVIexpiresIn = 0
    AVIsched = sched.scheduler(time.time, time.sleep) # Arguments are function handles for time and sleep functions
#    nextsch = AVIexpiresIn - (AVIexpiresIn - 15)
    nextsch = AVIexpiresIn - 60
    print("AVI Init Scheduling in " + str(nextsch) + " seconds.", flush=True)
    AVIsched.enter(nextsch, 1, AVIloop, argument = (AVIexpiresIn,))
    AVIsched.run()
# End - def runAVIthread()


def runFRMWKping():
    global FMWKsched
    global FRMWK_timeout
    FRMWK_timeout = 0
    FMWKsched = sched.scheduler(time.time, time.sleep) 
    FMWKsched.enter(2, 2, FRMWKloop, argument = (FRMWK_timeout,))
    FMWKsched.run()
# End - def runFRMWKping()

def runOAuth_thread():
    global OAuthsched
    global OAuthexpiresIn

    OAuthexpiresIn = 0
    OAuthsched = sched.scheduler(time.time, time.sleep) # Arguments are function handles for time and sleep functions
    OAuthsched.enter(1, 1, OAuthloop, argument = (OAuthexpiresIn,))
    OAuthsched.run()
# End - def runOAuth_thread():

# Load previous tokens
def PreviousTokens():
    global token_information
    with open('tokens.txt') as f:
     past_tokens = f.read().strip()
     if past_tokens:
        token_information = json.loads(past_tokens)
     else:
        pass


def getAAMtoken(): 
    # Get token from AAMTEX
    global AAMTEXaceessToken
    global AAMexpiresIn
    data={'grant_type' :'client_credentials','client_id':'kamesh.namuduri@unt.edu','client_secret':'eEUiivjNHodubBKMWRPrYGjaXgXDkaGBPyoaKcAgIIIStXoCqvTLkhMsLGUpFazjmGpfALgKszDcnqqufSQDzkmVntjqDJbstuAJkYtCGHNJHtKFuHJzCFoLurERSWLq'}
    Response = requests.post(endpoints.AAMTEX_token_endpoint(), data = data)
    if (Response.status_code != 200):
        print("Unable to get token")
        exit()
    AAMTEXaceessToken = Response.json()["access_token"]
    AAMexpiresIn = Response.json ()["expires_in"]
    print("Got AAMTEX token, 1 expires in " + str(AAMexpiresIn) + " seconds")
#End - def getAAMtoken():

def AAMloop(nextsch):
    global AAMsched
    global AAMexpiresIn
    getAAMtoken()
    nextsch = AAMexpiresIn - 60
    print("AAMTEX Scheduling in " + str(nextsch) + " seconds.", flush=True)
    AAMsched.enter(nextsch, 1, AAMloop, argument = (AAMexpiresIn,))
#End - def AAMloop



if __name__ == "__main__":
    
    

    PreviousTokens()
    AAMthread = threading.Thread(target=runAAMthread, daemon=True)
    AAMthread.start()
    while (AAMTEXaceessToken == ""):
        print("Waiting for AAMTEX token...", flush=True)
        sleep(5)
    

    
    
    DSSthread = threading.Thread(target=runDSSthread, daemon=True)
    DSSthread.start()
        
    getAVItoken()
    AVIthread = threading.Thread(target=runAVIthread, daemon=True)
    AVIthread.start()


    FMWKping = threading.Thread(target=runFRMWKping, daemon=True)
    FMWKping.start()

    OAuthread = threading.Thread(target=runOAuth_thread, daemon=True)
    OAuthread.start()

    host = endpoints.getHost()
    port = endpoints.getPort()
    print("Starting HermesDataHub on " + host + " with port " + port)
    app.run(debug=False, host=host, port=port)
