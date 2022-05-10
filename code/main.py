#import sqlite3
import threading
#import requests
import psutil
import time
import sys, os

def createDB():
  conn = sqlite3.connect('db.db')
  with open('schema.sql', 'r') as f:
    schema = f.read()
    conn.executescript(schema)
    conn.close()

def getValues():
  while True:
    try:
      conn2 = sqlite3.connect('db.db')
      print(" ==== \nCount died proxies = %s \nCount live proxies = %s \n====== " % (conn2.cursor().execute("SELECT count(*) from die_proxies").fetchall(),conn2.cursor().execute("SELECT count(*) from working_proxies").fetchall()))
      conn2.close()
    except:
      print("!!!getValues error")
      time.sleep(0.1)
    time.sleep(20)

def sendDieData():
  conn3 = sqlite3.connect('db.db')
  while True:
    die_data = conn3.cursor().execute("SELECT  id,ip from die_proxies limit 100").fetchall()
    
    if(len(die_data)>0):
      die_proxies = ",".join([str(a[1]) for a in die_data])
      print("send die proxies %s" %die_proxies)
      ids = ",".join([str(a[0]) for a in die_data])

      while (requests.get(url).status_code !=200):
        time.sleep(0.4)

      conn3.execute("DELETE from die_proxies where id in (%s)" %ids)
      while True:
        try:
          conn3.commit()
          break
        except:
          time.sleep(0.1)
    else:
      time.sleep(10)
    del die_data

def sendLiveData():
  conn4 = sqlite3.connect('db.db')
  while True:
    live_data = conn3.cursor().execute("SELECT  id,ip,port, proxie_type working_proxies limit 100").fetchall()
    
    if(len(live_data)>0):
      live_proxies = ",".join([str((a[1],a[2],a[3])) for a in live_data])
      print("send live proxies %s" %live_proxies)
      ids = ",".join([str(a[0]) for a in live_data])

      while (requests.get(url).status_code !=200):
        time.sleep(0.4)

      conn4.execute("DELETE from working_proxies where id in (%s)" %ids)
      while True:
        try:
          conn4.commit()
          break
        except:
          time.sleep(0.1)
    else:
      time.sleep(10)
    del live_data
  

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
        if (proc.status()!="running" or (time.time()-proc._create_time)>700):
          print("---Status = %s" %proc.status())
          proc.kill()
      except Exception as e:
        print("==checkZombieProcesses ERROR \n%s" %str(e))

    time.sleep(60)

def startProcess(p,timeout_s):
  try:
      #p = subprocess.Popen(cmd, start_new_session=True)
      p.wait(timeout=timeout_s)
  except subprocess.TimeoutExpired:
      print("Terminate by timeout")
      p.terminate()

#createDB()

#threading.Thread(target=getValues, args=()).start()
#threading.Thread(target=checkZombieProcesses, args=()).start()
#threading.Thread(target=runSubprocess, args=("http://v562757.macloud.host", "ttt")).start()
#threading.Thread(target=sendDieData, args=()).start()
#threading.Thread(target=sendLiveData, args=()).start()

_args=["http://v562757.macloud.host","ttt"]

while (True):
  loud_cpu, loud_mem = psutil.cpu_percent(), psutil.virtual_memory().percent
  if (loud_cpu <50 and loud_mem<60):
    #subprocess.Popen(["python","CheckProxy.py",checkDataUrl,token], creationflags=subprocess.CREATE_NEW_CONSOLE)
    #os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, "CheckProxy.py", "http://v562757.macloud.host ttt")# os.P_DETACH P_NOWAIT
    #os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, "CheckProxy.py", *_args)# os.P_DETACH P_NOWAIT
    #os.spawnl(os.P_DETACH, sys.executable, sys.executable, "CheckProxy.py", *_args)# os.P_DETACH P_NOWAIT
    threading.Thread(target=startProcess, args=(subprocess.Popen(["python","CheckProxy.py","http://v562757.macloud.host", "ttt"]),500)).start()
  #else:
    #print("====System too low. Waiting... cpu = %s memory = %s" % (loud_cpu, loud_mem))

  time.sleep(0.5)  

