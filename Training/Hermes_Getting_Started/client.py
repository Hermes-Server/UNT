import requests
import json


data = {

    "Country":"Africa",
    "Animal": "Lion"

}

headers = {'Content-Type':'application/json'}



response = requests.post("http://127.0.0.1:5000/setcookie", headers=headers, json=data)


#response = requests.get("http://127.0.0.1:5000/setcookie", headers=headers, json=data)


#data =response.json()

#json_object = json.loads(data)

print(response.text)
print(response.status_code)

