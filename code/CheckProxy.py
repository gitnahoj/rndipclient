import requests
import socket
import struct
import sys
#import json
#import sqlite3
import time
import threading
import string,random

#print(sys.argv)
#pip install urllib3==1.25.11

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def checkProxyByType(proxy_type,proxy,timeout,trysite):
  #print("--checkProxyByType")

  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
  }
  url = trysite
  _proxies={"https": "%s://%s" % (proxy_type,proxy)}

  #print(_proxies)
  try:
    resp_code = requests.get(url,proxies= _proxies,timeout=timeout,headers=headers).status_code
    print("!!!YAY find proxy %s" %proxy)
    logToFile("YAY find proxy %s type %s" % (proxy,proxy_type))
    return True
  except requests.ConnectionError as erc:
    print("\n===ConnectionError %s %s \n%s" %(proxy_type,proxy,str(erc)))
    #logToFile("checkProxyByType proxy %s type %s ConnectionError exception \n%s" % (proxy,proxy_type,erc))
  except requests.ReadTimeout:
    print("!!!YAY find proxy %s" %proxy)
    logToFile("YAY find proxy %s type %s" % (proxy,proxy_type))
    return True
  except requests.RequestException as err:
    print("!!RequestException \n%s" %str(err))
    #logToFile("checkProxyByType proxy %s type %s RequestException \n%s" % (proxy,proxy_type,str(err)))
  except Exception as e:
    print("===error \n%s"%str(e))
    #logToFile("checkProxyByType proxy %s type %s other exception \n%s" % (proxy,proxy_type,str(e)))
  return False

def logToFile(data):
  fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(25))
  with open("%s%s.log"%(time.time(),fname) , "w") as f:
    f.write(str(data))

def sendProxyStatus(proxy_ip,proxy_port,status,resp_url,token):
  url="%s/%s/%s/%s/%s" % (resp_url,token,proxy_ip,proxy_port,status)
  print("--sendProxyStatus\n%s"%url)
  logToFile("sendProxyStatus %s" %url)
  while True:
    try:
      resp = requests.get(url)
      if (resp.status_code==200):
        break
      else:
        time.sleep(0.2)
    except:
      time.sleep(0.2)
  #print("===========Send proxy status %s  responce code = %s" % (url,response.status_code))
  #exit()

def startCheckProxy(ip,ports,timeout,trysite,resp_url,token):
  _ip = int2ip(ip)
  ports_aviables=[]
  for port in ports:
    port=int(port)
    proxy = "%s:%s" % (_ip,port)
    #print("curr proxy  %s" %proxy)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
  
    try:
      s.connect((_ip, port))
    except Exception as e:
      #print("--socks error\n%s" %str(e))
      #ports_aviables.append((port,0))
      continue

    if(checkProxyByType("socks5",proxy,timeout,trysite)==True):
      #ports_aviables.append((port,5))
      sendProxyStatus(ip,port,5,resp_url,token)
    elif checkProxyByType("socks4",proxy,timeout,trysite)==True:
      #ports_aviables.append((port,4))
      sendProxyStatus(ip,port,4,resp_url,token)
    elif checkProxyByType("https",proxy,timeout,trysite)==True:
      sendProxyStatus(ip,port,1,resp_url,token)
      #ports_aviables.append((port,1))
    #else:
      #ports_aviables.append((port,0))
    #continue

  sys.exit()

def StartMe(ips,ports,timeout,trysite,resp_url,data_token):
  threads = []

  for ip in ips:
    threads.append(threading.Thread(target=startCheckProxy, args=(ip,ports,timeout,trysite,resp_url,data_token)))#.start()

  for x in threads:
    x.start()

  for x in threads:
    try:
      x.join()
    except:
      print("x.join() error")
  #print("!!!!!Closed process")

  sys.exit()
#python CheckProxy.py "http://v562757.macloud.host" "ttt"

  