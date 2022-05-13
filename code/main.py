#import sqlite3
import threading
import requests
import psutil
import time
import sys, os
import CheckProxy

load_data_url = "http://v562757.macloud.host"
token = "ttt"
run_work_thread_sleep=0.2
count_ips_per_thread = 6

system_loud_cpu_limit=80
system_loud_mem_limit=95

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

def checkZombieProcesses2():
  while True:
    print("total running threads %s" %len([t for t in threading.enumerate() if t.is_alive()]))
    time.sleep(5)

threading.Thread(target=checkZombieProcesses2, args=()).start()
#_args=["http://v562757.macloud.host","ttt"]


#jsondata = loadProxyList(load_data_url,token)

while (True):
  #break
  loud_cpu, loud_mem = psutil.cpu_percent(), psutil.virtual_memory().percent
  if (loud_cpu <system_loud_cpu_limit and loud_mem<system_loud_mem_limit):
    
    jsondata = loadProxyList(load_data_url,token)
    
    for ip in jsondata["ip"]:
      for port in jsondata["ports"]:
        t = threading.Thread(target=CheckProxy.startCheckProxy, args = (ip,port,jsondata["timeout"],jsondata["resp_url"],token))
        t.daemon = True
        t.start()
        #t.join(0.005)
        #t = threading.Thread(target=CheckProxy.startCheckProxy, args=(ip,jsondata["ports"],jsondata["timeout"],jsondata["trysite"],jsondata["resp_url"],token))
        #t.daemon = True
        #t.start()
        #t.join()
      time.sleep(0.005)
          #CheckProxy.startCheckProxy(ip,ports,timeout,trysite,resp_url,token)
      
  else:
    print("====System too low. Waiting... cpu = %s memory = %s" % (loud_cpu, loud_mem))

  #print("total running threads %s" %len([t for t in threading.enumerate() if t.is_alive()]))
  time.sleep(run_work_thread_sleep)  

