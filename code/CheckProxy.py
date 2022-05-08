import requests
import socket
import struct
import sys
import json
import sqlite3
import time

print(sys.argv)
#pip install urllib3==1.25.11

checkDataUrl = sys.argv[1]
proxies=[]
jsondata={
  "token":sys.argv[2]
}

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def sendProxyStatus(status):
  print("--sendProxyStatus")
  global jsondata
  url="%s/%s/%s/%s/%s" % (jsondata["resp_url"],jsondata["token"],jsondata["proxy"]["ip"],jsondata["proxy"]["port"],status)
  response = requests.get(url)
  print("===========Send proxy status %s  responce code = %s" % (url,response.status_code))
  #exit()

def checkProxyByType(proxy_type,proxy):
  print("--checkProxyByType")
  global jsondata

  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
  }
  url = jsondata["trysite"]
  _proxies={"https": "%s://%s" % (proxy_type,proxy)}

  print(_proxies)
  try:
    resp_code = requests.get(url,proxies= _proxies,timeout=jsondata["timeout"],headers=headers).status_code
    print("status code %s" %resp_code)
    return True
  except requests.ConnectionError as erc:
    print("===ConnectionError %s" %erc)
  except requests.ReadTimeout:
    print("==ReadTimeout")
    return True
  except requests.RequestException as err:
    print("!!RequestException %s" %str(err))
  except Exception as e:
    print("error %s"%str(e))
  return False

def store_proxy(ip,ports_data):
  conn = sqlite3.connect('db.db')
  if(len(ports_data)==0):
    print("store die ip %s" %ip)
    conn.execute("INSERT INTO die_proxies (ip) VALUES (%s)"%ip)
  else:
    print("store works data")
    conn.execute("INSERT INTO working_proxies (ip,port, proxie_type) VALUES %s" %",".join([str((ip,p[0],p[1])) for p in ports_data]))
  while True:
    try:
      conn.commit()
      break
    except: 
      time.spleep(0.1) 
  conn.close()
  del conn

def loadProxyList():
  print("--loadProxyList")
  global checkDataUrl
  global jsondata
  url = "%s/getjob/%s/5" % (checkDataUrl,jsondata["token"])

  resp = requests.get(url=url) #, params=params)
  print ("---load proxie list check data")
  if(resp.status_code==200):
    jsondata = resp.json()
    print("=== loaded %s proxies and %s ports " % (len(jsondata["ip"]),len(jsondata["ports"])))
    
    #for ip in data["ip"]:
      #for port in data["ports"]:
        #proxies.append({"ip":ip,"port":int(port)})

loadProxyList()

for ip in jsondata["ip"]:
  _ip = int2ip(ip)
  print("ip = %s" %_ip)
  ports_aviables=[]
  for port in jsondata["ports"]:
    port=int(port)
    print("curr proxy  %s:%s " %  (_ip,port))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(jsondata["timeout"])
  
    try:
      s.connect((_ip, port))
    except Exception as e:
      #print("!!!error %s %s" % (jsondata["proxy"]["full"],str(e)))
      #sendProxyStatus("0")
      ports_aviables.append((port,0))
      continue

    proxy = "%s:%s" % (_ip,port)

    if(checkProxyByType("socks5",proxy)==True):
      ports_aviables.append((port,5))
      #sendProxyStatus("5")
    elif checkProxyByType("socks4",proxy)==True:
      ports_aviables.append((port,4))
      #sendProxyStatus("4")
    elif checkProxyByType("https",proxy)==True:
      ports_aviables.append((port,1))
      #sendProxyStatus("1")
    else:
      ports_aviables.append((port,0))
      #sendProxyStatus("0")
    continue

  print(ports_aviables)
  store_proxy(ip,[p for p in ports_aviables if p[1]>0])
  ports_aviables.clear()
  