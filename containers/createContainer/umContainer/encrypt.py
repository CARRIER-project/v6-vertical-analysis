import requests
import json

#send file to TTP service
res = requests.post(url='http://dockerhost:5001/addFile',
    files={"fileObj": open('/data/dms.csv', 'rb')})

#get the uuid of the stored file at TTP
resultJson = json.loads(res.text.encode("utf-8"))

#print output
print("Stored encrypted file as %s" % (resultJson["status"].encode("utf-8")))
print("UUID: %s" % resultJson["uuid"].encode("utf-8"))

with open('result.txt', 'w') as fp:
    json.dump(resultJson, fp)