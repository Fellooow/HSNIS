import requests
import json

url = 'http://localhost:8000'

# Send a GET request
response = requests.get(url + '?name=John&age=30')
print(response.text)

# Send a POST request
data = {'name': 'John', 'age': 30}
headers = {'Content-type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=headers)
print(response.text)

# Send an OPTIONS request
response = requests.options(url)
print(response.headers)
