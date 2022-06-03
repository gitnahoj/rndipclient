import requests
import socket
import struct
import sys
#import json
#import sqlite3
#import time
#import threading
#import string,random

#print(sys.argv)
#pip install urllib3==1.25.11

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def checkProxyByType(proxy_type,proxy,timeout,resp_url):
  #print("%s %s" %(proxy_type,proxy));
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
  }

  _proxies=dict()
  _proxies["http"]="%s://%s" % (proxy_type,proxy)
  _proxies["https"]="%s://%s" % (proxy_type,proxy)
 
  try:
    resp = requests.get(resp_url, proxies=_proxies,headers=headers,timeout=timeout)
    #logToFile("code=%s\ntext=%s\nresp_url %s\n proxies= %s\ntimeout=%s"%(resp.status_code,resp.text,resp_url ,_proxies,timeout))
    #logToFile("YAY find proxy %s type %s" % (proxy,proxy_type))
    return True
  except Exception as e:
    #print("===error \n%s"%str(e))
    #a=1
    return False

#def logToFile(data):
#  fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(25))
#  with open("%s%s.log"%(time.time(),fname) , "w") as f:
#    f.write(str(data))

def startCheckProxy(ip,port,timeout,resp_url,token):
  
  _ip = int2ip(ip)
  port=int(port)
  proxy = "%s:%s" % (_ip,port)
  
  #print("curr proxy  %s" %proxy)

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(timeout)

  try:
    s.connect((_ip, port))
  except Exception as e:
    exit()

  if(checkProxyByType("socks5",proxy,timeout,"%s/%s/%s/%s/%s" % (resp_url,token,ip,port,5))==True):
    exit()
  elif (checkProxyByType("socks4",proxy,timeout,"%s/%s/%s/%s/%s" % (resp_url,token,ip,port,4))==True):
    exit()
  checkProxyByType("https",proxy,timeout,"%s/%s/%s/%s/%s" % (resp_url,token,ip,port,1))