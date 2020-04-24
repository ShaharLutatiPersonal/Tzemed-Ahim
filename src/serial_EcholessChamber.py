import serial as ser
import sys
import argparse
import time 
import csv


if __name__ == '__main__':
    date = time.ctime()
    date = date.replace(':','_')
    date = date.replace(' ','_')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--port', type=str,
        help='Port of ESP32 ,default = ''ttyUSB''',
        default = 'ttyUSB')
    parser.add_argument(
        '-n','--name',type=str,
        help = 'file name to save default = {}.csv'.format(date),
        default= '{}.csv'.format(date)
    )
    args = parser.parse_args()
    filename = args.name
    port = args.port
    print('*'*80)
    print('RSSI Detector')
    print('*'*80)
    print('Start Listening to port : {}, writing to file {}'.format(port,filename))
    try:
        fieldsnames = ['rssi','timestmap_comp']
        f = open(filename,'w',newline = '')
        writer = csv.DictWriter(f,fieldnames = fieldsnames)
        writer.writeheader()
        s = ser.Serial()
        s.baudrate = 115200
        s.port = port
        s.open()
        while(True):
            line = s.readline()
            if b'rssi_detector' in line:
                print('-'*80)
                rssi = line.split(b'=')[1].decode().split('\n')[0]
                timestmap_comp = time.time()
                writer.writerow({'rssi':'{}'.format(rssi),'timestmap_comp':'{}'.format(timestmap_comp)})
                print('time = {}, rssi = {}'.format(timestmap_comp,rssi))
                print('-'*80)
    except KeyboardInterrupt:
        f.close()
        print('This work saved to {}'.format(filename))
        print('Lutati Vs Covid19')

