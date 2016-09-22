import pv
import os, re, sys
import time, math, string
from time import sleep
from ca import caput, caget 
from Chip_Collect import scrape_dcparameters

def chip_sizes():
    w2w = 0.125
    b2b_horz = 0.825
    b2b_vert = 1.125
    cell_format = [9, 9, 12, 12]
    return w2w, b2b_horz, b2b_vert, cell_format

def get_xy(xtal_name):
    w2w, b2b_horz, b2b_vert, cell_format = chip_sizes()
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
    
    #print xtal_name, '--->', blockR, blockC, windowR, windowC, '\t', x, '\t', y 
    #print "X(%i * %1.3f) + (%i * %i * %1.3f) + (%i * %1.3f)" \
    #       %(blockC, b2b_horz, blockC, (cell_format[2]-1), w2w, windowC, w2w) 
    #print "Y(%i * %1.3f) + (%i * %i * %1.3f) + (%i * %1.3f)" \
    #       %(blockR, b2b_vert, blockR, (cell_format[3]-1), w2w, windowR, w2w) 
    #print '\n\n'
    return x, y 

def get_pythagoras(x, y, previous_x, previous_y):
    dist = math.sqrt((   (abs(x - previous_x))**2 + (abs(y - previous_y)**2)  ))
    return dist

def get_chip_dict(chip_fid):
    chip_dict = {}
    try:
        f = open(chip_fid, 'r')
    except IOError as e:
        print 'Total Fail', e.errno, e.strerror
    else:
        ############################################
        #for line in f.readlines()[6:40]:
        for line in f.readlines()[6:10]:
            xtal_dict = {}
            entry = line.rstrip('\n').split('\t')
            if '-----------' in entry[1]:
                continue
            else:
                xtal_name = entry[0]         
                xtal_dict['xtal_name'] = xtal_name         
                xtal_dict['xtal_pres'] = entry[1]
                xtal_dict['xtal_spec'] = entry[2]
                xtal_dict['xtal_dat1'] = entry[3]
                xtal_dict['xtal_dat2'] = entry[4]
                xtal_dict['xtal_fnsh'] = entry[5]
                chip_dict[xtal_name] = xtal_dict 
    return chip_dict 

def index11664():
    """
    These are the cross streets and block addresses for a city chip 
    with 9x9 Blocks and 12x12 Addresses
    """
    #Nine Rows
    road_list = ['Adams','Bush','Clinton','Dwight','Eisenhwr', 'Ford', 'Grant', 'Hoover', 'India']
    #Nine Columns
    cross_list = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th','9th']
    #Twelve Rows
    block_row_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    #Eight Columns
    block_col_list = ['a','b','c','d','e','f','g','h','i','j','k','l']

    return road_list, cross_list, block_row_list, block_col_list

def index11664_fiducials():
    road_list, cross_list, block_row_list, block_col_list = index11664()
    corners_list = []
    for road in road_list:
        for cross in cross_list:
            for r2 in block_row_list:
                for c2 in block_col_list:
                    addr = road[0] + cross[:-2] + '_' + r2 + c2
                    if r2+c2 in ['aa', 'la', 'll']:
                        corners_list.append(addr)
    position_list = [\
    'A1_ag', 'A2_ag', 'A3_ag', 'A4_ag', 'A5_ag', 'A6_ag', 'A7_ag', 'A8_ag','A9_ag', \
    'A1_aj', 'A2_bj', 'A3_cj', 'A4_ak', 'A5_bk', 'A6_ck', 'A7_al', 'A8_bl','A9_cl', \
    'B1_bg', 'B2_bg', 'B3_bg', 'B4_bg', 'B5_bg', 'B6_bg', 'B7_bg', 'B8_bg','B9_bg', \
    'B1_aj', 'B2_bj', 'B3_cj', 'B4_ak', 'B5_bk', 'B6_ck', 'B7_al', 'B8_bl','B9_cl', \
    'C1_cg', 'C2_cg', 'C3_cg', 'C4_cg', 'C5_cg', 'C6_cg', 'C7_cg', 'C8_cg','C9_cg', \
    'C1_aj', 'C2_bj', 'C3_cj', 'C4_ak', 'C5_bk', 'C6_ck', 'C7_al', 'C8_bl','C9_cl', \
    'D1_ah', 'D2_ah', 'D3_ah', 'D4_ah', 'D5_ah', 'D6_ah', 'D7_ah', 'D8_ah','D9_ah', \
    'D1_aj', 'D2_bj', 'D3_cj', 'D4_ak', 'D5_bk', 'D6_ck', 'D7_al', 'D8_bl','D9_cl', \
    'E1_bh', 'E2_bh', 'E3_bh', 'E4_bh', 'E5_bh', 'E6_bh', 'E7_bh', 'E8_bh','E9_bh', \
    'E1_aj', 'E2_bj', 'E3_cj', 'E4_ak', 'E5_bk', 'E6_ck', 'E7_al', 'E8_bl','E9_cl', \
    'F1_ch', 'F2_ch', 'F3_ch', 'F4_ch', 'F5_ch', 'F6_ch', 'F7_ch', 'F8_ch','F9_ch', \
    'F1_aj', 'F2_bj', 'F3_cj', 'F4_ak', 'F5_bk', 'F6_ck', 'F7_al', 'F8_bl','F9_cl', \
    'G1_ai', 'G2_ai', 'G3_ai', 'G4_ai', 'G5_ai', 'G6_ai', 'G7_ai', 'G8_ai','G9_ai', \
    'G1_aj', 'G2_bj', 'G3_cj', 'G4_ak', 'G5_bk', 'G6_ck', 'G7_al', 'G8_bl','G9_cl', \
    'H1_bi', 'H2_bi', 'H3_bi', 'H4_bi', 'H5_bi', 'H6_bi', 'H7_bi', 'H8_bi','H9_bi', \
    'H1_aj', 'H2_bj', 'H3_cj', 'H4_ak', 'H5_bk', 'H6_ck', 'H7_al', 'H8_bl','H9_cl', \
    'I1_ci', 'I2_ci', 'I3_ci', 'I4_ci', 'I5_ci', 'I6_ci', 'I7_ci', 'I8_ci','I9_ci', \
    'I1_aj', 'I2_bj', 'I3_cj', 'I4_ak', 'I5_bk', 'I6_ck', 'I7_al', 'I8_bl','I9_cl']
    fiducial_list = sorted(corners_list + position_list)
    #fiducial_list = []
    return fiducial_list           

def CheckFile(path, fid):
    if os.path.isfile(path + '/' + fid):
        timestr = time.strftime("%Y%m%d_%H%M%S_")
        timestamp_fid = path + '/' + timestr + fid 
        os.rename(path + '/' + fid, timestamp_fid)
        print '\n', path + fid, 'already exists ... moving old file to:\n', timestamp_fid
    return 1

def SaveFile(tmp_fid, fid):
    if os.path.isfile(fid):
        timestr = time.strftime("%Y%m%d_%H%M%S_")
        timestamp_fid = timestr + fid 
        os.rename(fid, timestamp_fid)
        print '\n', fid, 'already exists ... moving old file to:', timestamp_fid
        print 'Saving', fid
        os.rename(tmp_fid, fid)
        if os.path.isfile(fid):
            print fid, 'Saved'
        else:
            print 'An Error Occured Saving', fid
    else:
        print '\nSaving', fid
        os.rename(tmp_fid, fid)
        if os.path.isfile(fid):
            print fid, 'Saved'
        else:
            print 'An Error Occured Saving', fid

def shotLister_W_SnakeRows(path, fid):
    f = open(path + '/' + fid, 'r')
    header = f.readlines()[:11]
    f.close()
    chip_dict = {}
    f = open(path + '/' + fid, 'r')
    for line in f.readlines()[11:]:
        entry = line.split('\t')
        addr = entry[0][-5:]
        chip_dict[addr] = entry
    f.close()
    road_list = ['A','B','C','D','E','F','G','H','I']
    daor_list = ['I','H','G','F','E','D','C','B','A']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    sorc_list = ['9','8','7','6','5','4','3','2','1']
    wind_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    dniw_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    shot_list = []
    for r in range(9):
        for c in range(9):
            for wr in range(12):
                for wc in range(12):
                    if (r % 2 == 0):
                        if (wr % 2 == 0):
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            shot_list.append(addr)
                            #print addr
                        else:
                            addr = road_list[r] + cros_list[c] + '_' + dniw_list[wc] + wind_list[wr]
                            shot_list.append(addr)
                            #print addr
                    else:
                        if (wr % 2 == 0):
                            addr = road_list[r] + sorc_list[c] + '_' + wind_list[wc] + dniw_list[wr]
                            shot_list.append(addr)
                            #print 't', addr
                        else:
                            addr = road_list[r] + sorc_list[c] + '_' + dniw_list[wc] + dniw_list[wr]
                            shot_list.append(addr)
                            #print 't', addr
    spec_fid = fid[:-4] + 'spec'
    print spec_fid
    g = open(path + '/' + spec_fid, 'w')
    for x in header:
        g.write(x)
    for x in shot_list:
        line = '\t'.join(chip_dict[x])
        g.write(line)
    g.close()
    return 0

def shotLister_E_SnakeCols(path, fid):
    f = open(path + '/' + fid, 'r')
    header = f.readlines()[:11]
    f.close()
    chip_dict = {}
    f = open(path + '/' + fid, 'r')
    for line in f.readlines()[11:]:
        entry = line.split('\t')
        addr = entry[0][-5:]
        chip_dict[addr] = entry
    f.close()
    road_list = ['A','B','C','D','E','F','G','H','I']
    daor_list = ['I','H','G','F','E','D','C','B','A']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    sorc_list = ['9','8','7','6','5','4','3','2','1']
    wind_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    dniw_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    shot_list = []
    for c in range(9):
        print
        for r in range(9):
            print
            for wc in range(12):
                print
                for wr in range(12):
                    if (c % 2 == 0):
                        if (wc % 2 == 0):
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            shot_list.append(addr)
                            print addr,
                        else:
                            addr = road_list[r] + cros_list[c] + '_' + wind_list[wc] + dniw_list[wr]
                            shot_list.append(addr)
                            print addr,
                    else:
                        if (wc % 2 == 0):
                            addr = daor_list[r] + cros_list[c] + '_' + dniw_list[wc] + wind_list[wr]
                            shot_list.append(addr)
                            print addr,
                        else:
                            addr = daor_list[r] + cros_list[c] + '_' + dniw_list[wc] + dniw_list[wr]
                            shot_list.append(addr)
                            print addr
    spec_fid = fid[:-4] + 'shot'
    print spec_fid
    g = open(path + '/' + spec_fid, 'w')
    for x in header:
        g.write(x)
    for x in shot_list:
        line = '\t'.join(chip_dict[x])
        g.write(line)
    g.close()
    return 0

def shotLister_E_SnakeCols_reverse(path, fid):
    print 'Writing Shot'
    f = open(path + '/' + fid, 'r')
    header = f.readlines()[:11]
    f.close()
    chip_dict = {}
    f = open(path + '/' + fid, 'r')
    for line in f.readlines()[11:]:
        entry = line.split('\t')
        addr = entry[0][-5:]
        chip_dict[addr] = entry
    f.close()
    road_list = ['A','B','C','D','E','F','G','H','I']
    daor_list = ['I','H','G','F','E','D','C','B','A']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    sorc_list = ['9','8','7','6','5','4','3','2','1']
    wind_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    dniw_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    shot_list = []
    for c in range(9):
        #print 
        for r in range(9):
            #print 
            for wc in range(12):
                #print
                for wr in range(12):
                    if (c % 2 == 0):
                        if (wc % 2 == 0):
                            addr = daor_list[r] + sorc_list[c] + '_' + dniw_list[wc] + dniw_list[wr]
                            shot_list.append(addr)
                            #print addr,
                        else:
                            addr = daor_list[r] + sorc_list[c] + '_' + dniw_list[wc] + wind_list[wr]
                            shot_list.append(addr)
                            #print addr,
                    else:
                        if (wc % 2 == 0):
                            addr = road_list[r] + sorc_list[c] + '_' + wind_list[wc] + dniw_list[wr]
                            shot_list.append(addr)
                            #print addr,
                        else:
                            addr = road_list[r] + sorc_list[c] + '_' + wind_list[wc] + wind_list[wr]
                            shot_list.append(addr)
                            #print addr,
    spec_fid = fid[:-4] + 'shot'
    print spec_fid
    g = open(path + '/' + spec_fid, 'w')
    for x in header:
        g.write(x)
    for x in shot_list:
        line = '\t'.join(chip_dict[x])
        g.write(line)
    g.close()
    return 0

def shotLister_L2RWs_TypewriterRows(fid):
    f = open(fid, 'r')
    header = f.readlines()[:6]
    f.close()
    
    chip_dict = {}
    f = open(fid, 'r')
    for line in f.readlines()[6:]:
        entry = line.split('\t')
        addr = entry[0][-5:]
        chip_dict[addr] = entry
    f.close()
    
    road_list = ['A','B','C','D','E','F','G','H','I']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    wndw_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    rvrs_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    
    shot_list = []
    for r in range(9):
        for c in range(9):
            for wr in range(12):
                for wc in range(12):
                    if (wr % 2 == 0):
                        addr = road_list[r] + cros_list[c] + '_' + wndw_list[wc] + wndw_list[wr]
                        shot_list.append(addr)
                        #print addr
                    else:
                        addr = road_list[r] + cros_list[c] + '_' + rvrs_list[wc] + wndw_list[wr]
                        shot_list.append(addr)
                        #print addr
            #print
    tmp_spec_fid = 'Oxfile.spec'
    g = open(tmp_spec_fid, 'w')
    for x in header: g.write(x)
    for x in shot_list:
        line = '\t'.join(chip_dict[x])
        g.write(line)
    g.close()

    spec_fid = fid[:-4] + 'spec'
    print spec_fid
    SaveFile(tmp_spec_fid, spec_fid)
    return 0

def main():
    road_list, cross_list, block_row_list, block_col_list = index11664()
    fiducial_list = index11664_fiducials()
    for road in road_list:
        for cross in cross_list:
            city_block_short = road[0] + cross[:-2]
            print city_block_short + '  ',
        print
    #
    chipname, visit_id, filepath, chipcapacity, blockcapacity, exptime, dcdetdist  = scrape_dcparameters()
    path = visit_id + '/processing/' + filepath
    try:
        os.stat(path)
    except:
        os.makedirs(path)
    fid = chipname + '.addr'
    CheckFile(path, fid)
    g = open(path + '/' + fid, 'w')
    # 
    line1 = '#23456789012345678901234567890123456789012345678901234567890123456789012345678901234567890\n#\n'
    line2 = '#&diams\tfilepath = %s\n'       %filepath
    line3 = '#&diams\tvisit_id = %s\n'       %visit_id
    line4 = '#&diams\tchipname = %s\n'       %chipname
    line5 = '#&diams\tchipcapacity = %s\n'   %chipcapacity
    line6 = '#&diams\tblockcapacity = %s\n'  %blockcapacity
    line7 = '#&diams\texptime = %s\n'        %exptime
    line8 = '#&diams\tdcdetdist = %s\n'      %dcdetdist
    line9 = '#\n'    
    line10 = '#XtalAddr      XCoord  YCoord  ZCoord  Present Shot  Spare04 Spare03 Spare02 Spare01\n'    
    g.write(line1)
    g.write(line2)
    g.write(line3)
    g.write(line4)
    g.write(line5)
    g.write(line6)
    g.write(line7)
    g.write(line8)
    g.write(line9)
    g.write(line10)
    previous_x, previous_y = 0.0, 0.0
    available_addr_list = []
    for road in road_list:
        for cross in cross_list:
            city_block = road + ' & ' + cross
            city_block_short = road[0] + cross[:-2]
            #print '\n', city_block
            for r2 in block_row_list:
                for c2 in block_col_list:
                    block_addr = r2 + c2
                    addr = '_'.join([city_block_short, block_addr])
                    xtal_name = '_'.join([chipname, city_block_short, block_addr])
                    (x, y) = get_xy(xtal_name)
                    dist = get_pythagoras(x, y, previous_x, previous_y)
                    #if dist > 1.0:
                    #    print addr, dist, '-----', x, y, previous_x, previous_y
                    #print (x, y)
                    if addr in fiducial_list:
                        #print '  +   ',
                        xtal_xcrd = str(x) 
                        xtal_ycrd = str(y)
                        xtal_zcrd = '0.0'
                        xtal_pres = '0'
                        line = '\t'.join([xtal_name, xtal_xcrd, xtal_ycrd, xtal_zcrd, xtal_pres]) + '\n'
                        g.write(line)
                    else:
                        available_addr_list.append(addr)
                        #print city_block_short + '_' + r2 + c2, '', 
                        xtal_xcrd = str(x) 
                        xtal_ycrd = str(y)
                        xtal_zcrd = '0.0'
                        xtal_pres = '1'
                        #if road[0] in ['A','B']:
                        #    xtal_dlay = '0'
                        #else:
                        #    xtal_dlay = time_delay
                        line = '\t'.join([xtal_name, xtal_xcrd, xtal_ycrd, xtal_zcrd, xtal_pres]) + '\n'
                        g.write(line)
                    previous_x = x
                    previous_y = y
                #print
    g.close() 
    x = shotLister_W_SnakeRows(path, fid)
    y = shotLister_E_SnakeCols_reverse(path, fid)
    print '\nThere are', len(fiducial_list), 'fiducials in this chip.'

if __name__ == '__main__':
    main()
