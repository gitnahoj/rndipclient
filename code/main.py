import threading
import requests
import psutil
import time
import sys, os
import CheckProxy
import subprocess

isMainProcess=False

for i in sys.argv:
  print(i)
  if(i=="--main-process"):
    isMainProcess = True

load_data_url = "http://v562757.macloud.host"
token = "ttt"
run_work_thread_sleep=0.2

system_loud_cpu_limit=80
system_loud_mem_limit=95

def loadProxyList(data_url,data_token):
  jsondata = {}
  url = "%s/getjob/%s/200" % (data_url,data_token)
  try:

    resp = requests.get(url=url) #, params=params)

    if(resp.status_code==200):
      jsondata = resp.json()
      jsondata["token"]= data_token
      jsondata["resp_url"] = "%s%s" % (data_url,jsondata["resp_url"])
      return jsondata
    else:
      print("\n== loadProxyList request fail with status code = %s"%resp.status_code)
      return False
  except Exception as ex:
    print("\n====loadProxyList FAIL \n%s"%ex)
    return False
  
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
    time.sleep(30)
    if(isMainProcess==False):
      if(len([t for t in threading.enumerate() if t.is_alive()])<3):
        exit()
    elif(len([t for t in threading.enumerate() if t.is_alive()])>3 and psutil.cpu_percent()<system_loud_cpu_limit and psutil.virtual_memory().percent<system_loud_mem_limit):
      print("==run another not main process")
      subprocess.Popen(["python","main.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)

threading.Thread(target=checkZombieProcesses2, args=()).start()
#_args=["http://v562757.macloud.host","ttt"]

while (True):
  loud_cpu, loud_mem = psutil.cpu_percent(), psutil.virtual_memory().percent
  if (loud_cpu <system_loud_cpu_limit and loud_mem<system_loud_mem_limit):
    try:  
      jsondata = loadProxyList(load_data_url,token)
      if(jsondata==False):
        if(isMainProcess==False):
          break
        else:
          time.sleep(5)
          continue

      print("\n--Loaded IPs to check %s"%len(jsondata["ip"]))
      for ip in jsondata["ip"]:
        for port in jsondata["ports"]:
          t = threading.Thread(target=CheckProxy.startCheckProxy, args = (ip,port,jsondata["timeout"],jsondata["resp_url"],token))
          t.daemon = True
          t.start()
        time.sleep(0.005)
    except Exception as e:
      print("==While True ERROR \n%s" %str(e))
      
  else:
    print("====System too low. Waiting... cpu = %s memory = %s" % (loud_cpu, loud_mem))

  time.sleep(run_work_thread_sleep)  