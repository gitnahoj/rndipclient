import requests
import socket
import struct
import sys
import json

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

def int_to_bytes(x: int) -> bytes:
  return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def sendProxyStatus(status):
  print("--sendProxyStatus")
  global jsondata
  url="%s/%s/%s/%s/%s" % (jsondata["resp_url"],jsondata["token"],jsondata["proxy"]["ip"],jsondata["proxy"]["port"],status)
  response = requests.get(url)
  print("===========Send proxy status %s  responce code = %s" % (url,response.status_code))
  #exit()

def checkProxyByType(proxy_type):
  print("--checkProxyByType")
  global jsondata

  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
  }
  url = jsondata["check_url"]
  if proxy_type!="":
    _proxy="%s://%s" % (proxy_type,jsondata["proxy"]['full'])
    _proxies={"http": _proxy, "https": _proxy}
  else:
     _proxies={"http": "http://"+jsondata["proxy"]["full"], "https": "https://"+jsondata["proxy"]["full"]}   

  print(_proxies)
  try:
    response = requests.get(url,proxies= _proxies,timeout=jsondata["timeout"],headers=headers)
    print("status code %s" %response.status_code)
    return True
  except requests.Timeout as err:
    print("!!TimeoutException(10s)")
  except requests.RequestException as err:
    print("!!RequestException %s" %str(err))
  except Exception as e:
    s = str(e)
    print("error %s"%s)
  return False

def loadProxyList():
  print("--loadProxyList")
  global checkDataUrl
  global jsondata
  url = "%s/getjob/%s/10" % (checkDataUrl,jsondata["token"])

  resp = requests.get(url=url) #, params=params)
  print ("---load proxie list check data")
  if(resp.status_code==200):
    data = resp.json()
    print("=== loaded %s proxies and %s ports " % (len(data["ip"]),len(data["ports"])))
    jsondata["resp_url"] = checkDataUrl + data["resp_url"]
    jsondata["check_url"] = data["trysite"]
    jsondata["timeout"] = data["timeout"]
    for ip in data["ip"]:
      for port in data["ports"]:
        proxies.append({"ip":ip,"port":int(port)})


#///
i=0
while (i<100):
  i=i+1
  if (len(proxies)==0):
    loadProxyList()
  else:
    proxy = proxies.pop()
    jsondata["proxy"] = proxy

    port=proxy["port"]
    ip=int2ip(proxy["ip"])
    jsondata["proxy"]["full"]="%s:%s" % (ip,port)
    print("curr proxy = %s" %  jsondata["proxy"])

    #ip = socket.gethostbyname("nodesdirect.com")
    #payload_socks4 = b"\x04\x01"+int_to_bytes(443) +  socket.inet_aton(ip) + b"\x00"
    payload_socks5 = struct.pack('BBB',0x05, 0x01, 0x00)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(jsondata["timeout"])
  
    try:
      s.connect((ip, port))
    except Exception as e:
      print("!!!error %s %s" % (jsondata["proxy"]["full"],str(e)))
      sendProxyStatus("0")
      continue

    print("---------------Request #%s--------------------------"%jsondata["proxy"])
    try:
      s.sendall(payload_socks5)
      print("Payload 5 sended. Getting info..")
      _data = s.recv(100)
      print("socket sock5 received")
      print(_data)
      if(len(_data)==2):
        version, auth = struct.unpack('BB', _data)
        print("V=%s"%version)
        print("auth=%s"%auth)
        if (version==5 and auth==0):
          sendProxyStatus("5")
      s.close()
    except socket.error as e:
      print("socket socks4 error %s " %str(e))
    except Exception as e:
      print("fail socket socks5 %s" %str(e))

    if(checkProxyByType("")==True):
      sendProxyStatus("1")
      continue
    elif checkProxyByType("socks4")==True:
      sendProxyStatus("4")
      continue
    elif checkProxyByType("socks5")==True:
      sendProxyStatus("5")
      continue
    else:
      sendProxyStatus("0")
      continue