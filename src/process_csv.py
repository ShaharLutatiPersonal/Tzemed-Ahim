import numpy as np
import csv
import matplotlib.pyplot as plt
import time
import scipy.signal as dsp
from scipy import interpolate as interp

def find_idx(a,field):
    out = []
    for idx,elem in enumerate(a):
        if elem == field:
            out.append(idx)
    return out

def save_nested_dict(dict,filename):
    with open(r'{}.txt'.format(filename),'w+') as f:
        f.write(str(dict))

def read_nested_dict(filename):
    dic = ''
    with open(r'{}.txt'.format(filename),'r') as f:
        for i in f.readlines():
            dic=i #string
    dic = eval(dic) # this is orignal dict with instace dict
    return dic

def windowed_lpf(sig,t,time_span):
    b = np.ones([1,time_span])/time_span
    b = b[0,:]
    a = 1
    sig_f = dsp.lfilter(b,a,sig)
    sig_f = sig_f[time_span:-1]
    t_f = t[time_span:-1]
    return t_f,sig_f

def find_groups_in_time(t,max_diff):
    difference = np.diff(t)
    ix = []
    group_ix = []
    for idx,diff_item in enumerate(difference):
        if diff_item>max_diff:
            ix.append(idx)
    bef_ixx = 0
    for ixx in ix:
        group_ix.append(np.arange(bef_ixx,ixx))
        bef_ixx = ixx + 1
    return group_ix

def fix_non_uniform_sampling(x,y):
    flin = interp.interp1d(x,y)
    x = np.arange(x[0],x[-1] , 1)
    ylin = flin(x)
    return x,ylin

def windowd_statistics(sig,exposure_time = 100,method,q):
    med_w = np.zeros([1,len(sig)])
    med_w = med_w[0]
    if method != 'quantile':
        func = eval('lambda a : np.{}(a)'.format(method))
    else:
        func = lambda a: np.quantile(a,q)
    for ix in range(len(sig)-exposure_time):
        dec = func(sig[ix:ix+exposure_time])
        med_w[ix:ix+exposure_time] = dec
    med_w[-1] = med_w[-2]
    return med_w 

f = open('log_x.csv','r')
fieldsnames= ['DeviceId','uuid','time_packet','time_server','rssi']
reader = csv.DictReader(f,fieldnames = fieldsnames)
d = {}

for field in fieldsnames:
    d[field] = []

for row in reader:
    for field in fieldsnames:
        d[field].append(row[field])
for key in d:
    d[key] = d[key][1:-1]

unique_phones = np.unique(d['DeviceId'])
tble = {}
ttble = {}
t_start = np.double(d['time_packet'][0])

for phone in unique_phones:
    ix = np.array(find_idx(d['DeviceId'],phone))
    rssi = np.array(d['rssi'])[ix]
    uuid = np.array(d['uuid'])[ix]
    t = np.array(d['time_packet'])[ix]
    unique_uuid = np.unique(uuid)
    for uid in unique_uuid:
        dx = np.array(find_idx(uuid,uid))
        frssi = np.array(np.double(rssi[dx]))
        ft = np.array(np.double(t[dx]))
        group_ix = find_groups_in_time(ft,max_diff = 20)
        print('uid {} , phone {}'.format(uid,phone))
        print(frssi)
        print(ft)
        print('*'*80)
        #ax.scatter(ft,
        #        frssi, label='uid = {}'.format(uid))
        for tgroup in group_ix:
            fig, ax = plt.subplots()
            if len(tgroup) <= 100:
                continue
            t_s = ft[tgroup]
            sig_s = frssi[tgroup]
            t_u,sig_u = fix_non_uniform_sampling(t_s,sig_s)
            t_f,sig_f = windowed_lpf(sig_u,t_u,time_span = 10)
            med_w = windowd_statistics(sig_f,exposure_time = 100,stat = 'median')
            std_w = windowd_statistics(sig_f,exposure_time = 100,stat = 'std')
            mean_w = windowd_statistics(sig_f,exposure_time = 100,stat = 'mean')
            q9_w = windowd_statistics(sig_f,exposure_time = 100,stat = 'quantile',q = .9)
            ax.plot(t_s,sig_s,'.',label = 'raw rssi')
            ax.plot(t_f,sig_f,'.', label = 'windowed LPF')
            ax.plot(t_f,med_w,'.', label = 'windowed mdian')
            ax.plot(t_f,mean_w,'.', label = 'windowed mean')
            ax.plot(t_f,q9_w,'.', label = 'windowed quantile')
            ax.plot(t_f,std_w,'.', label = 'windowed std')
            ax.set_ylim(-90,-45)
            ax.legend()
            ax.set_title('{}'.format(phone))
            fig.show()
        tble[uid,phone] = [frssi,ft]
save_nested_dict(tble,'DB_extracted')
