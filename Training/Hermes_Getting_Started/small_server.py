from flask import Flask, request, jsonify
import json
import requests
import urllib.parse
import socket
import sched
import time
from time import sleep
import threading
import uuid
from datetime import timezone 
import datetime
#import connections
import processData
#from connections import mysql




app = Flask(__name__)
  
@app.route('/setcookie', methods = ['POST'])
def setcookie():
   request_json = json.dumps("")
   
   # Checcks is request is in JSON
   if not request.is_json:
        status = 415
        print("not json")
        response = jsonify({"message": "Request must be JSON", "status": status})



   #checks method
   if request.method == 'POST':
      request_json = json.dumps("")
      objProcessData = processData.processData()


      data = request.get_json()
      print(data)
      request_json = json.dumps(data)
      print(request_json)

      Origin = data["Country"]
      Pet = data["Animal"]
      print("The birth place of a", Pet," is in",Origin)

      result = objProcessData.postTelemetry(data)

      response = "Method is POST"



         

   return response

  

  
if __name__ == '__main__':
   app.run()
  