import os, re, sys
import numpy as np
import time, math, string

def hits_scrape(fid, diamond_dict):
    hits_dict = {}
    for i in range(11664):
        hits_dict[diamond_dict[i]] = 0
    f = open(fid)
    for line in f.readlines()[1:]:
        entry = line.split()
        i = int(entry[0])
        yesno = 1
        #yesno = int(entry[1])
        hits_dict[diamond_dict[i]] = yesno 
    return hits_dict 

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

def get_xy(xtal_name):
    w2w = 0.125
    b2b_horz = 0.825
    b2b_vert = 1.125
    cell_format = [9, 9, 12, 12]
    entry = xtal_name.split('_')[-2:]
    R, C = entry[0][0], entry[0][1]
    r2, c2 = entry[1][0], entry[1][1]
    blockR = int(string.uppercase.index(R))
    blockC = int(C) - 1
    windowR = string.lowercase.index(r2)
    windowC = string.lowercase.index(c2)
    y = (blockC * b2b_horz) + (blockC * (11) * w2w) + (windowR * w2w)
    x = (blockR * b2b_vert) + (blockR * (11) * w2w) + (windowC * w2w)
    return x, y 

def main():
    # [addr] = i, [i] = addr 
    normal_addr_dict, normal_ordr_dict = normal_dicts()
    # [addr] = j, [j] = addr    
    collect_addr_dict, collect_ordr_dict = collect_dicts()
    
    for j in sorted(collect_ordr_dict.keys()):
        print j, get_xy(collect_ordr_dict[j])


if __name__ == '__main__':
    main()
