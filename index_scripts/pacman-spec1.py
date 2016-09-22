import os, re, sys
import numpy as np
import time, math, string
from time import sleep
import matplotlib
from matplotlib import pyplot as plt

def hits_scrape(fid, diamond_dict):
    hits_dict = {}
    for i in range(11664):
        hits_dict[diamond_dict[i]] = 0
    f = open(fid)
    for line in f.readlines()[1:]:
        entry = line.split()
        i = int(entry[0])
        hits_dict[diamond_dict[i]] = 1 
    return hits_dict 

def pv_dict(normal_ordr_dict):
    wnpv_dict = {}
    i = 0
    block = 0
    for cross in range(9):
        for road in range(9):
            j = 0
            for vert in range(12):
                for horz in range(12):
                    windw = i%48
                    p = j/48
                    PV = 'ME14E-OP-BLOCK-%02d:P%d:B%d' %(block, p, windw)
                    wnpv_dict[normal_ordr_dict[i]] = PV
                    i += 1 
                    j += 1
            block += 1
    return wnpv_dict

def collect_dicts():
    road_list = ['A','B','C','D','E','F','G','H','I']
    daor_list = ['I','H','G','F','E','D','C','B','A']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    sorc_list = ['9','8','7','6','5','4','3','2','1']
    wind_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    dniw_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    ordr_list = []
    addr_dict = {}
    ordr_dict = {}
    i = 0
    for r in range(9):
        #print r 
        for c in range(9):
            #print c 
            for wc in range(12):
                #print
                for wr in range(12):
                    if (r % 2 == 0):
                        if (wc % 2 == 0):
                            addr = daor_list[r] + sorc_list[c] + '_' + dniw_list[wc] + dniw_list[wr]
                            ordr_list.append(addr)
                            #print addr,'1',
                        else:
                            addr = daor_list[r] + sorc_list[c] + '_' + dniw_list[wc] + wind_list[wr]
                            ordr_list.append(addr)
                            #print addr,'2',
                    else:
                        if (wc % 2 == 0):
                            addr = daor_list[r] + cros_list[c] + '_' + wind_list[wc] + dniw_list[wr]
                            ordr_list.append(addr)
                            #print addr,'3',
                        else:
                            addr = daor_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            ordr_list.append(addr)
                            #print addr,'4',
                    addr_dict[addr] = i
                    ordr_dict[i] = addr
                    #print i,
                    i += 1
    return addr_dict, ordr_dict

def normal_dicts():
    road_list = ['A','B','C','D','E','F','G','H','I']
    daor_list = ['I','H','G','F','E','D','C','B','A']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    sorc_list = ['9','8','7','6','5','4','3','2','1']
    wind_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    dniw_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    ordr_list = []
    ordr_dict = {}
    addr_dict = {}
    i = 0
    for c in range(9):
        #print
        for r in range(9):
            #print
            for wc in range(12):
                #print
                for wr in range(12):
                    if (r % 2 == 0):
                        if (wr % 2 == 0):
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            ordr_list.append(addr)
                            #print addr,
                        else:
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            ordr_list.append(addr)
                            #print addr,
                    else:
                        if (wr % 2 == 0):
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            ordr_list.append(addr)
                            #print addr,
                        else:
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            ordr_list.append(addr)
                            #print addr,
                    ordr_dict[i] = addr
                    addr_dict[addr] = i
                    #print i,
                    i += 1
    return addr_dict, ordr_dict

def clean_up(val = 0):
    for i in range(81):
        caput('ME14E-OP-BLOCK-%02d:FANOUT.J' %i, '%s' %str(val))
    return 1

def get_xy(xtal_name):
    w2w = 0.125
    b2b_horz = 0.825
    b2b_vert = 1.125
    #b2b_horz = 0.0
    #b2b_vert = 0.0
    cell_format = [9, 9, 12, 12]
    entry = xtal_name.split('_')[-2:]
    R, C = entry[0][0], entry[0][1]
    r2, c2 = entry[1][0], entry[1][1]
    #print R, C, r2, c2
    blockR = int(string.uppercase.index(R))
    blockC = int(C) - 1
    windowR = string.lowercase.index(r2)
    windowC = string.lowercase.index(c2)

    y = (blockC * b2b_horz) + (blockC * (11) * w2w) + (windowR * w2w)
    x = (blockR * b2b_vert) + (blockR * (11) * w2w) + (windowC * w2w)
    return x, y 

def fid_to_coords(fid, column_choice, collect_ordr_dict):
    ordr_num_list, some_val_list = [], [] 
    f = open(fid, 'r')
    for line in f.readlines()[1:]:
        e = line.split()
	ordr_num_list.append(int(e[0])-1)
	some_val_list.append(float(e[column_choice]))
    Z = np.array(some_val_list)

    x_list, y_list = [], []
    for num in ordr_num_list:
       addr = collect_ordr_dict[num] 
       x, y = get_xy(addr)
       x_list.append(x)
       y_list.append(y)
    
    X = np.array(x_list)
    Y = np.array(y_list)
    x = X.ravel()
    y = Y.ravel()
    z = Z.ravel()
    #return x[:144], y[:144], z[:144] 
    #return x[:1440], y[:1440], z[:1440] 
    return x, y, z 

def main(fid, column_choice):
    # [addr] = i, [i] = addr 
    normal_addr_dict, normal_ordr_dict = normal_dicts()
    # [addr] = pv
    pv_addr_dict = pv_dict(normal_ordr_dict)

    # [addr] = j, [j] = addr    
    collect_addr_dict, collect_ordr_dict = collect_dicts()
    # [addr] = yesno 
    hits_addr_dict = hits_scrape(fid, collect_ordr_dict)           

    #Plot attempt
    column_choice = int(column_choice)
    x, y, z = fid_to_coords(fid, column_choice, collect_ordr_dict)
    fig = plt.figure()
    fig = plt.figure(figsize=(10,10), facecolor='0.15', edgecolor='k')
    ax1 = fig.add_subplot(111, aspect=1, axisbg='0.05')
    fig.subplots_adjust(left=0.03,right=0.97,bottom=0.03,top=0.97)
    if fid.endswith('spots'):
        plt.scatter(x, y, c=z, s=5, alpha=1, marker='s', cmap='PuOr')
    else:
        z = (-1*z)
        plt.scatter(x, y, c=z, s=16, alpha=1, marker='s', cmap='Oranges')
        #plt.scatter(x, y, c=z, s=15, alpha=1, marker='s', cmap='PuOr')
        #plt.scatter(x, y, c=z, s=15, alpha=1, marker='s', cmap='Greys')

    #ax1.scatter(x, y, c=z, s=41, alpha=1, marker='s', cmap='Greys')
    ax1.invert_yaxis()

    plt.axis([-0.125, 21.6, 19.15, -0.125])
    plt.axis('off')
    #cb = plt.colorbar()
    #cb.set_label('value')
    output_fid = fid[:-4] + '-' + str(column_choice) + '.png' 
    plt.savefig(output_fid, dpi=600, facecolor='0.15', bbox_inches='tight', pad_inches=0)
    total_dict = {}
    for addr in normal_addr_dict.keys():
        total_dict[addr] = [normal_addr_dict[addr], \
                           collect_addr_dict[addr], \
                                pv_addr_dict[addr], \
                              hits_addr_dict[addr], \
                                      get_xy(addr)]


    #Clear pv area
    #clean_up()
    """
    #Fill with shot list
    for i in range(11663):
        addr = normal_ordr_dict[i]
        [i, j, pv, yesno, (x,y)] = total_dict[addr]
        print i, addr, j, pv, yesno, x, y
        caput(pv, yesno)

    """
    """
    for i in range(11663):
        addr = collect_ordr_dict[i]
        [i, j, pv, yesno, (x,y)] = total_dict[addr]
        print i, j, addr, pv, yesno, x, y
        #caput(pv, 1)
    """

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
plt.show()

