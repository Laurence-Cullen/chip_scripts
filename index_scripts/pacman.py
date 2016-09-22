import pv
import os, re, sys
import time, math, string
from time import sleep
from ca import caput, caget 

def hits_scrape(fid, diamond_dict):
    hits_dict = {}
    for i in range(11664):
        hits_dict[diamond_dict[i]] = 0
    f = open(fid)
    for line in f.readlines():
        entry = line.split()
        i = int(entry[0]) - 1
        yesno = int(entry[1])
        hits_dict[diamond_dict[i]] = yesno 
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
    cell_format = [9, 9, 12, 12]
    entry = xtal_name.split('_')[-2:]
    R, C = entry[0][0], entry[0][1]
    r2, c2 = entry[1][0], entry[1][1]
    #print R, C, r2, c2
    blockR = int(string.uppercase.index(R))
    blockC = int(C) - 1
    windowR = string.lowercase.index(r2)
    windowC = string.lowercase.index(c2)

    x = (blockC * b2b_horz) + (blockC * (cell_format[2]-1) * w2w) + (windowC * w2w)
    y = (blockR * b2b_vert) + (blockR * (cell_format[3]-1) * w2w) + (windowR * w2w)
    return x, y 

def main(fid):
    # [addr] = i, [i] = addr 
    normal_addr_dict, normal_ordr_dict = normal_dicts()
    # [addr] = pv
    pv_addr_dict = pv_dict(normal_ordr_dict)

    # [addr] = j, [j] = addr    
    collect_addr_dict, collect_ordr_dict = collect_dicts()
    # [addr] = yesno 
    hits_addr_dict = hits_scrape(fid, collect_ordr_dict)           

    total_dict = {}
    for addr in normal_addr_dict.keys():
        total_dict[addr] = [normal_addr_dict[addr], \
                           collect_addr_dict[addr], \
                                pv_addr_dict[addr], \
                              hits_addr_dict[addr], \
                                      get_xy(addr)]
    #Clear pv area
    clean_up()

    #Fill with shot list
    for i in range(11663):
        addr = normal_ordr_dict[i]
        [i, j, pv, yesno, (x,y)] = total_dict[addr]
        print i, addr, j, pv, yesno, x, y
        caput(pv, yesno)
    """
    for i in range(288):
        addr = collect_ordr_dict[i]
        [i, j, pv, yesno, (x,y)] = total_dict[addr]
        caput(pv, 1)
    """
         
if __name__ == '__main__':
    main(sys.argv[1])

