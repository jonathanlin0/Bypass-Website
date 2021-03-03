from flask import Flask, jsonify
import requests
import random
import json
import base64
import time
from flask_cors import CORS
import ssl
from urllib3 import poolmanager
import socket
import struct

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False


@app.route("/")
def home():
    return "API is working fine"

@app.route("/<ip>/")
def visit(ip):

    ip = socket.inet_ntoa(struct.pack('!L', int(ip)))
    f = open('data.json','r')
    data = json.load(f)
    f.close()

    new_data = {
      'ip':ip,
      'unix_epoch_time': time.time()
    }

    data['visits'].append(new_data)
    f = open('data.json','w')
    json_object = json.dumps(data, indent = 4)
    f.write(json_object)
    f.close()

    return "Visit Logged"

def bypass_function(input_link, ip):
    bypassed = False
    times_tried = -1


    ip = socket.inet_ntoa(struct.pack('!L', int(ip)))
    print(ip)

    #add log
    f = open('data.json','r')
    data = json.load(f)
    f.close()

    new_data = {
        'ip':ip,
        'link':input_link,
        'unix_epoch_time': time.time()
    }

    data['commands'].append(new_data)
    f = open('data.json','w')
    json_object = json.dumps(data, indent = 4)
    f.write(json_object)
    f.close()
    


    new_link = "None"
    start_time = time.time()
    while bypassed == False and times_tried < 2:
        times_tried = times_tried + 1

        proxy_removed = False
        try:
            f = open('proxies.txt','r')
            proxies = f.read().splitlines()
            f.close()
            
            proxy_dict = {}
            while True:
                try:
                    proxy = random.choice(proxies)

                    http_proxy  = "http://" + proxy
                    https_proxy = "http://" + proxy
                    ftp_proxy   = "ftp://" + proxy

                    proxy_dict = { 
                        #"http"  : http_proxy, 
                        "https" : https_proxy, 
                        #"ftp"   : ftp_proxy
                    }


                    #response = requests.get('https://www.google.com/', proxies = proxy_dict)
                    session = requests.session()
                    session.mount('https://', TLSAdapter())
                    res = session.get('https://www.google.com/', proxies = proxy_dict,verify=False, timeout = 2)


                    break
                except requests.exceptions.ProxyError:
                    print('Proxy error')
                    proxies.remove(proxy)
                    proxy_removed = True
                except requests.exceptions.ConnectTimeout:
                    print('Connect error')
                    proxies.remove(proxy)
                    proxy_removed = True
                except requests.exceptions.Timeout:
                    print('Timeout error')
                    proxies.remove(proxy)
                    proxy_removed = True
                except Exception as e:
                    print(e)
                    proxies.remove(proxy)
                    proxy_removed = True

            if proxy_removed == True:
                out = ''

                last = proxies[len(proxies)-1]
                proxies.remove(last)
                for temp in proxies:
                    out = out + temp + '\n'
                out = out + last
                f = open('proxies.txt','w')
                f.write(out)
                f.close()
                
            first_link = 'https://publisher.linkvertise.com/api/v1/redirect/link/static/'

            second_link = 'https://publisher.linkvertise.com/api/v1/redirect/link/insert/linkvertise/path/here/target?serial=base64encodedjson'
            second_link_front = second_link[0:second_link.find('insert/linkvertise')]
            second_link_back = second_link[second_link.find('/target?serial'):second_link.find('base64encodedjson')]


                
            #r = requests.get(first_link + input_link,proxies=proxy_dict)
            session = requests.session()
            session.mount('https://', TLSAdapter())
            r = session.get(first_link + input_link, proxies = proxy_dict, timeout = 3)

            text = r.text
            link_id = text[text.find('"id":')+5:text.find(',"url":')]

            new_json = {"timestamp":int(time.time()), "random":"6548307", "link_id":int(link_id)}

            s = json.dumps(new_json)
            json_converted = base64.b64encode(s.encode('utf-8'))
            json_converted = str(json_converted)
            json_converted = json_converted[2:len(json_converted)-1]

        
            #r = requests.get(second_link_front + input_link + second_link_back + json_converted,proxies=proxy_dict,timeout=4)
            #r = requests.get(second_link_front + input_link + second_link_back + json_converted,proxies=proxy_dict)
            session = requests.session()
            session.mount('https://', TLSAdapter())
            r = session.get(second_link_front + input_link + second_link_back + json_converted, proxies = proxy_dict, timeout = 3)
            print(r)
            converted_json = json.loads(r.text)
            new_link = converted_json['data']['target']

            bypassed = True
        except:
            print('Try: ' + str(times_tried))

    new_json = {
        'input_link': input_link,
        'new_link': new_link,
        'times_tried':times_tried
    }

    return new_json

@app.route("/<query>/<query2>/<ip>/")
def bypass(query,query2,ip):

    input_link = query + '/' + query2
    

    return jsonify(bypass_function(input_link,ip))


if __name__ == "__main__":
    #app.debug = True
    #app.run(debug = True)
    #app.run(host="0.0.0.0",port= 5000)
    app.run(debug=False, host = '0.0.0.0',port= 5000)