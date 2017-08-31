import requests
import shutil
import json

#read input file
with open('input.txt') as data_file:    
    inputJson = json.load(data_file)

url = 'http://dockerhost:5001/file/%s' % inputJson["umData"]
response = requests.get(url, stream=True)
with open('/data/umData.csv', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response

url = 'http://dockerhost:5001/file/%s' % inputJson["cbsData"]
response = requests.get(url, stream=True)
with open('/data/cbsData.csv', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response
