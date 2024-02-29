import requests
import json
url = 'http://127.0.0.1:8000/api/register/'
data = {'username': 'mobiletester', 'email': 'mobiletester@testing.eu', 'password': 'mobiletester'}
response = requests.post(url, data=data)
response_data = json.loads(response.content)

print(response_data)