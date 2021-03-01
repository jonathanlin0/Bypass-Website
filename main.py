from flask import Flask, jsonify
import requests
import random
import json
import base64
import time


app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route("/")
def home():
    return "API is working fine"


@app.route("/<query>/<query2>")
def bypass(query,query2):

    bypassed = False
    times_tried = -1

    input_link = query + '/' + query2
    while bypassed == False and times_tried < 2:
        times_tried = times_tried + 1

        try:
            f = open('proxies.txt','r')
            proxies = f.read().splitlines()
            f.close()
            
            proxy_dict = {}
            while True:
                try:
                    proxy = random.choice(proxies)

                    http_proxy  = "http://" + proxy
                    https_proxy = "https://" + proxy
                    ftp_proxy   = "ftp://" + proxy

                    proxy_dict = { 
                        "http"  : http_proxy, 
                        "https" : https_proxy, 
                        "ftp"   : ftp_proxy
                    }

                    response = requests.get('https://www.google.com/', proxies = proxy_dict)
                    break
                except requests.exceptions.ProxyError:
                    print('Proxy error')
                except requests.exceptions.ConnectTimeout:
                    print('Connect error')
                
            first_link = 'https://publisher.linkvertise.com/api/v1/redirect/link/static/'

            second_link = 'https://publisher.linkvertise.com/api/v1/redirect/link/insert/linkvertise/path/here/target?serial=base64encodedjson'
            second_link_front = second_link[0:second_link.find('insert/linkvertise')]
            second_link_back = second_link[second_link.find('/target?serial'):second_link.find('base64encodedjson')]

            

            """
            if '.com/' in input_link:
                if '?o=' in input_link:
                    link = input_link[input_link.find('.com/')+5:input_link.find('?o=')]
                else:
                    link = input_link[input_link.find('.com/')+5:len(input_link)]
            if '.net/' in input_link:
                if '?o=' in input_link:
                    link = input_link[input_link.find('.net/')+5:input_link.find('?o=')]
                else:
                    link = input_link[input_link.find('.net/')+5:len(input_link)]
            """
                
            r = requests.get(first_link + input_link,proxies=proxy_dict,timeout=2)
            text = r.text
            link_id = text[text.find('"id":')+5:text.find(',"url":')]

            new_json = {"timestamp":int(time.time()), "random":"6548307", "link_id":int(link_id)}

            s = json.dumps(new_json)
            json_converted = base64.b64encode(s.encode('utf-8'))
            json_converted = str(json_converted)
            json_converted = json_converted[2:len(json_converted)-1]

            #r = proxy.scrape(second_link_front + link + second_link_back + json_converted)
            r = requests.get(second_link_front + input_link + second_link_back + json_converted,proxies=proxy_dict,timeout=4)
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

    return jsonify(new_json)


if __name__ == "__main__":
    #app.debug = True
    #app.run(debug = True)
    #app.run(host="0.0.0.0",port= 5000)
    app.run(debug=False, host = '0.0.0.0',port= 5000)
