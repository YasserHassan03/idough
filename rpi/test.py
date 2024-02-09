import requests as r
import time
import urllib3

urllib3.disable_warnings()


url = "https://ec2-34-207-250-127.compute-1.amazonaws.com:5000/"

while True:
    response = r.get(url + '/predict',verify=False)
    print(response.json())
    time.sleep(1)
    


