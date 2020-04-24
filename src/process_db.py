import sqlite3 as sql
import os
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from tabulate import tabulate as tbl




folder_path = r'C:\Users\User\Google Drive\jsonserv\data\phone_data'
file_array = []
max_x_array = []
base_file = r"C:\Users\User\Google Drive\jsonserv\data\base_data\Pocket 270 5m.sqlite"
for filename in os.listdir(folder_path):
    if filename.endswith(".sqlite"):
        insql = sql.connect(folder_path+r"\\"+filename)
        sql_cursor = insql.cursor()
        sql_cursor.execute('SELECT timestamp FROM locations WHERE device_id = 43;')
        data = sql_cursor.fetchall()
        data_x = [x[0] for x in data]
        max_x_array.append(max(data_x))
        file_array.append(filename)
file_array_sorted = [x for _,x in sorted(zip(max_x_array,file_array))]
max_sorted = [x for x in sorted(max_x_array)]
insql = sql.connect(base_file)
sql_cursor = insql.cursor()
sql_cursor.execute('SELECT timestamp,rssi FROM locations WHERE device_id = 43;')
data = sql_cursor.fetchall()
time = [x[0] for x in data]
rssi = [x[1] for x in data]
curr_max = 0
meas = {}
for filename,max_val in zip(file_array_sorted,max_sorted):
    final_ix = time.index(max_val)
    curr_rssi = rssi[curr_max:final_ix]
    meas[filename] = curr_rssi
    #fig,ax = plt.subplots()
    #ax.plot(curr_rssi,'.')
    #ax.set_title('{}'.format(filename))
    #fig.show()
    curr_max = final_ix + 1
rssi_5m = []
rssi_2m = []
rssi_ant = []
count = 0
for key in meas:
    if '_' in key and 'free' not in key:
        if count == 0:
            count = 1
            continue
        rssi_ant += meas[key]
    if '5' in key:
        rssi_5m += meas[key]
    elif 'free' not in filename:
        rssi_2m += meas[key]
_2m_minmax = [min(rssi_2m),max(rssi_2m)]
_ant_minmax = [min(rssi_ant),max(rssi_ant)]
_5m_minmax = [min(rssi_5m),max(rssi_5m)]
_2x = np.linspace(_2m_minmax[0],_2m_minmax[1],1000)
_5x = np.linspace(_5m_minmax[0],_5m_minmax[1],1000)
_ant= np.linspace(_ant_minmax[0],_ant_minmax[1],1000)
kernel_ant = stats.gaussian_kde(_ant)
kernel_5m = stats.gaussian_kde(rssi_5m)
kernel_2m = stats.gaussian_kde(rssi_2m)
cdf_2m = np.vectorize(lambda r: kernel_2m.integrate_box_1d(-np.inf, r))
cdf_5m = np.vectorize(lambda r: kernel_5m.integrate_box_1d(-np.inf, r))
z2m = kernel_2m(_2x)
z5m = kernel_5m(_5x)
cdf2m = cdf_2m(_2x)
cdf5m = cdf_5m(_5x)
ant_z = kernel_ant(_ant)

qunatile_perc = [.1, .5, .8, .9]
qunatile_5m = [np.quantile(rssi_5m,x) for x in qunatile_perc]
qunatile_2m = [np.quantile(rssi_2m,x) for x in qunatile_perc]
qunatile_ant = [np.quantile(rssi_ant,x) for x in qunatile_perc]
cov_2m = kernel_2m.covariance[0][0]
cov_5m = kernel_5m.covariance[0][0]
cov_ant = kernel_ant.covariance[0][0]
linear_mean = lambda v: 10*np.log10(np.mean(np.power(10.0,np.array(v)/10)))
headers = ['Distance [m]']
headers += ['{} quantile [dBm] '.format(x) for x in qunatile_perc]
headers += ['covariance']
headers += ['Linear mean [dBm]']
row_0 = [2]
row_1 = [5]
row_2 = [3.4]
for x,y,z in zip(qunatile_2m,qunatile_5m,qunatile_ant):
    row_0.append(x)
    row_1.append(y)
    row_2.append(z)
row_0.append(cov_2m)
row_1.append(cov_5m)
row_0.append(linear_mean(rssi_2m))
row_1.append(linear_mean(rssi_5m))
row_2.append(cov_ant)
tble = [row_0,row_1]
table = tbl(tble,headers = headers,tablefmt = 'github')
print('*'*150)
print(table)
print('*'*150)
fig,ax = plt.subplots()
ax.plot(_2x,z2m,label = 'RSSI - 2m pdf')
ax.plot(_5x,z5m, label = 'RSSI - 5m pdf')
ax.set_title('PDF 2m, 5m')
ax.legend()
ax.grid()
plt.xlabel('power [dBm]')
fig.show()
fig,ax = plt.subplots()
ax.plot(_2x,cdf2m,label = 'RSSI - 2m CDF')
ax.plot(_5x,cdf5m, label = 'RSSI - 5m CDF')
ax.set_title('CDF 2m, 5m')
ax.legend()
ax.grid()
plt.xlabel('power [dBm]')
fig.show()
fig,ax = plt.subplots()
ax.plot(_ant,ant_z,label = 'RSSI - Echoless Chamber pdf')
ax.set_title('Echoless Chamber pdf')
ax.grid()
plt.xlabel('power [dBm]')
fig.show()
