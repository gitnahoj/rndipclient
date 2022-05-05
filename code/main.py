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
token = sys.argv[2]

while (True):
  loud_cpu, loud_mem = psutil.cpu_percent(), psutil.virtual_memory().percent
  if (loud_cpu <60 and loud_mem<90):
    #subprocess.Popen(["python","CheckProxy.py",checkDataUrl,token], creationflags=subprocess.CREATE_NEW_CONSOLE)
    subprocess.Popen(["python","CheckProxy.py",checkDataUrl,token])
  else:
    print("====System too low. Waiting... cpu = %s memory = %s" % (loud_cpu, loud_mem))
  time.sleep(0.4)  
