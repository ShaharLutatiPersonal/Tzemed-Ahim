from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi
import time
import colorama
import csv
from colorama import Fore, Style
last_seen = 0

class Server(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'world', 'received': 'ok'}))
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        global last_seen
        fieldsnames= ['DeviceId','uuid','time_packet','time_server','rssi']
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        time_packet = message['beacons'][0]['last_seen']
        if time_packet<= last_seen:
            return
        last_seen = time_packet
        uuid= message['beacons'][0]['ibeacon_data']['uuid']
        DeviceId = message['reader']
        rssi = message['beacons'][0]['rssi']
        time_server = time.time()*100
        print('DeviceId: {},uuid: {},time_pk: {},time_sv {},rssi {}'.format(DeviceId,uuid,time_packet,time_server,rssi))
        #print('new row')
        print('*'*80)
        with open('log.csv','a',newline ='') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames = fieldsnames)
            writer.writerow({'{}'.format(fieldsnames[0]):'{}'.format(DeviceId),
                '{}'.format(fieldsnames[1]):'{}'.format(uuid),'{}'.format(fieldsnames[2]):'{}'.format(time_packet),
                '{}'.format(fieldsnames[3]):'{}'.format(time_server),'{}'.format(fieldsnames[4]):'{}'.format(rssi)})
        csvfile.close()
        
def run(server_class=HTTPServer, handler_class=Server, port=8002):
    fieldsnames= ['DeviceId','uuid','time_packet','time_server','rssi']
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    file = open('log.csv','w',newline = '')
    writer = csv.DictWriter(file,fieldnames = fieldsnames)
    writer.writeheader()
    file.close()
    print('COVID-19 Proximity Server')
    print('By Shahar Lutati')
    print ('Starting httpd on port %d...' % port)
    print('*'*80)
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()