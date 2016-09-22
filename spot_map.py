import numpy as np
import visual_map
import os, re, sys
import time, math, string
from matplotlib import pyplot as plt

print('in python script')

f = open('filter_list.tmp')

num_lines = sum(1 for line in open('filter_list.tmp'))

info_log = np.zeros(11664)

# reading input file line by line to get ID of cell and spot number
for line in xrange(0, num_lines):

    line_content = f.readline()

    line_content = line_content.split()

    filename = line_content[0]

    i = int(filename[-9:-4])

    if(sys.argv[1] == '-s'):
        info_log[i] = int(line_content[1])

    if(sys.argv[1] == '-i'):
        info_log[i] = line_content[1]

#for i in xrange(0,num_lines):
#    print(spot_log[i])

x_list, y_list, z_list = [], [], []
# [addr] = i, [i] = addr 
collect_addr_dict, collect_ordr_dict = visual_map.collect_dicts()
#normal_addr_dict, normal_ordr_dict = visual_map.normal_dicts()
fid_list, corners_list = visual_map.index11664_fiducials()

for j in range(0, 11664):
    addr = collect_ordr_dict[j]
    #addr = normal_ordr_dict[j]
    x, y = visual_map.get_xy(addr)
    
    if(sys.argv[1] == '-s'):
        z = info_log[j]
        """"
        if(info_log[j] > 50):
            z = 100
        else:
            z = 0
        """

    if(sys.argv[1] == '-i'):
        if(info_log[j] > 0.1):
            z = 100
        else:
            z = 0


    x_list.append(float(x))
    y_list.append(float(y))
    z_list.append(float(z))

X = np.array(x_list)
Y = np.array(y_list)
Z = np.array(z_list)
xr = X.ravel()
yr = Y.ravel()
zr = Z.ravel()

print('before plot')

fig = plt.figure(num=None, figsize=(9,9), facecolor='0.6', edgecolor='k')
fig.subplots_adjust(left=0.03,bottom=0.03,right=0.97,top=0.97,wspace=0,hspace=0)
ax1 = fig.add_subplot(111, aspect='equal', axisbg='0.7')
ax1.scatter(xr, yr, c=zr, s=16, alpha=1, marker='s', linewidth=0.1)#,cmap='PuOr')
ax1.set_xticks([2.2*x for x in range(11)])
ax1.set_yticks([2.5*x for x in range(11)])
ax1.set_xlim(xr.min()-0.2, xr.max()+0.2)
ax1.set_ylim(yr.min()-0.2, yr.max()+0.2)
ax1.invert_yaxis()

if(sys.argv[1] == '-s'):
    plt.savefig('spot_plot.png', dpi=600, bbox_inches='tight', pad_inches=0.05)

if(sys.argv[1] == '-i'):
    plt.savefig('index_plot.png', dpi=600, bbox_inches='tight', pad_inches=0.05)

print('after plot')

np.save('info_log.npy', info_log)
