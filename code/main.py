#import sqlite3
import threading
import requests
import psutil
import time
import sys, os
import CheckProxy

load_data_url = "http://v562757.macloud.host"
token = "ttt"
run_work_thread_sleep=0.5
count_ips_per_thread = 6

system_loud_cpu_limit=50
system_loud_mem_limit=50

def loadProxyList(data_url,data_token):
  jsondata = {}
  url = "%s/getjob/%s/200" % (data_url,data_token)
  resp = requests.get(url=url) #, params=params)

  if(resp.status_code==200):
    jsondata = resp.json()
    jsondata["token"]= data_token
    jsondata["resp_url"] = "%s%s" % (data_url,jsondata["resp_url"])
    return jsondata
  else:
    return false
  
def runSubprocess(_retunr_host,_token):
  subprocess.Popen(["python","CheckProxy.py",_retunr_host, _token]).communicate() #.poll()
  print ("==== end runSubprocess")

def checkZombieProcesses():
  while True:
    #getValues()
    childrens = psutil.Process().children()
    print("child process  = %s" % len(childrens))
    for proc in childrens :
      try:
        if (proc.status()=="zombie"):
          os.wait()
        elif (proc.status()!="running" or (time.time()-proc._create_time)>500):
          print("---Status = %s" %proc.status())
          proc.kill()
      except Exception as e:
        print("==checkZombieProcesses ERROR \n%s" %str(e))

    time.sleep(30)

#threading.Thread(target=runSubprocess, args=("http://v562757.macloud.host", "ttt")).start()
#_args=["http://v562757.macloud.host","ttt"]


jsondata = loadProxyList(load_data_url,token)
i = 0

while (True):
  #break
  loud_cpu, loud_mem = psutil.cpu_percent(), psutil.virtual_memory().percent
  if (loud_cpu <system_loud_cpu_limit and loud_mem<system_loud_mem_limit):
    #subprocess.Popen(["python","CheckProxy.py",checkDataUrl,token], creationflags=subprocess.CREATE_NEW_CONSOLE)
    #os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, "CheckProxy.py", *_args)# os.P_DETACH P_NOWAIT
    #os.spawnl(os.P_DETACH, sys.executable, sys.executable, "CheckProxy.py", *_args)# os.P_DETACH P_NOWAIT

    if(jsondata==False or i>=len(jsondata["ip"])):

      jsondata = loadProxyList(load_data_url,token)
      i=0
    else:
      ips=jsondata["ip"][i:i+count_ips_per_thread]
      i+=len(ips)
      
      t = threading.Thread(target=CheckProxy.StartMe, args=(ips,jsondata["ports"],jsondata["timeout"],jsondata["trysite"],jsondata["resp_url"] ,token))
      #t.daemon = True
      t.start()
      
  print("total running threads %s" %len([t for t in threading.enumerate() if t.is_alive()]))

  #else:
    #print("====System too low. Waiting... cpu = %s memory = %s" % (loud_cpu, loud_mem))

  time.sleep(run_work_thread_sleep)  

