#pip install psutil
#pip install urllib3==1.25.11
#pip install PySocks
import requests
import psutil
import time
import subprocess
import json
import sys

checkDataUrl = sys.argv[1]
proxies=[]
resp_data={
  "token":sys.argv[2]
}
#checkDataUrl = "http://v562757.macloud.host"

def loadProxyList():
  global checkDataUrl
  global resp_data
  url = "%s/getjob/%s/100" % (checkDataUrl,resp_data["token"])
  #params = dict(
   # token='rndtoken',
  #  count=300,
   #

  resp = requests.get(url=url) #, params=params)
  print ("---load proxie list check data")
  if(resp.status_code==200):
    data = resp.json()
    print("=== loaded %s proxies and %s ports " % (len(data["ip"]),len(data["ports"])))
    resp_data["resp_url"] = checkDataUrl + data["resp_url"]
    resp_data["check_url"] = data["trysite"]
    resp_data["timeout"] = data["timeout"]
    for ip in data["ip"]:
      for port in data["ports"]:
        proxies.append({"ip":ip,"port":int(port)})

while (True):
  loud_cpu, loud_mem = psutil.cpu_percent(), psutil.virtual_memory().percent
  if (len(proxies))==0:
    loadProxyList()
  elif (loud_cpu <50 and loud_mem<90):
    print("len(proxies) = %s"%len(proxies))
    #print("----run process")
    resp_data["proxy"]=proxies.pop()
    #subprocess.Popen(["python","CheckProxy.py",json.dumps(resp_data)], creationflags=subprocess.CREATE_NEW_CONSOLE)
    subprocess.Popen(["python3","CheckProxy.py",json.dumps(resp_data)])
  else:
    print("====System too low. Waiting... cpu = %s memory = %s" % (loud_cpu, loud_mem))
  time.sleep(0.1)  
