import pv
import os, re, sys
import time, math, string
from time import sleep
from ca import caput, caget 

##########################################
# NEW Chip_Manager for SACLA  experiment #
# This version last edited 04 Mar by DAS #
##########################################

def index11664_fiducials():
    corners_list = []
    for R in string.letters[26:35]:
        for C in [str(num) for num in range(1,10)]:
            for r in string.letters[:12]:
                for c in string.letters[:12]:
                    addr = '_'.join([R+C, r+c])
                    if r+c in ['aa', 'la', 'll']:
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
    return fiducial_list           

def get_xy(addr):
    w2w = 0.125
    b2b_horz = 0.825
    b2b_vert = 1.125
    cell_format = [9, 9, 12, 12]
    entry = addr.split('_')[-2:]
    R, C = entry[0][0], entry[0][1]
    r2, c2 = entry[1][0], entry[1][1]
    blockR = string.uppercase.index(R)
    blockC = int(C) - 1
    windowR = string.lowercase.index(r2)
    windowC = string.lowercase.index(c2)
    x = (blockC * b2b_horz) + (blockC * (cell_format[2]-1) * w2w) + (windowC * w2w)
    y = (blockR * b2b_vert) + (blockR * (cell_format[3]-1) * w2w) + (windowR * w2w)
    return x, y 

def make_path_dict():
    #path_dict[path_key] = [xstart, ystart, xblocks, yblocks, [path]]
    path_dict = {}
    list11 = ['A1_aa']
    list12 = ['A1_aa','B1_aa']
    list14 = ['A1_aa','B1_aa','C1_aa','D1_aa']
    list19 = ['A1_aa','B1_aa','C1_aa','D1_aa','E1_aa','F1_aa','G1_aa','H1_aa','I1_aa']
    list23 = ['A1_aa','B1_aa','C1_aa','C2_la','B2_la','A2_la']
    list33 = ['F4_la','E4_la','D4_la',\
              'D5_aa','E5_aa','F5_aa',\
              'F6_la','E6_la','D6_la',]
    list41 = ['A1_aa','A2_la','A3_aa','A4_la']
    list55 = ['C3_aa','D3_aa','E3_aa','F3_aa','G3_aa',\
              'G4_la','F4_la','E4_la','D4_la','C4_la',\
              'C5_aa','D5_aa','E5_aa','F5_aa','G5_aa',\
              'G6_la','F6_la','E6_la','D6_la','C6_la',\
              'C7_aa','D7_aa','E7_aa','F7_aa','G7_aa',]
    list77 = ['H2_la','G2_la','F2_la','E2_la','D2_la','C2_la','B2_la',\
              'B3_aa','C3_aa','D3_aa','E3_aa','F3_aa','G3_aa','H3_aa',\
              'H4_la','G4_la','F4_la','E4_la','D4_la','C4_la','B4_la',\
              'B5_aa','C5_aa','D5_aa','E5_aa','F5_aa','G5_aa','H5_aa',\
              'H6_la','G6_la','F6_la','E6_la','D6_la','C6_la','B6_la',\
              'B7_aa','C7_aa','D7_aa','E7_aa','F7_aa','G7_aa','H7_aa',\
              'H8_la','G8_la','F8_la','E8_la','D8_la','C8_la','B8_la',]
    list99 = ['A1_aa','B1_aa','C1_aa','D1_aa','E1_aa','F1_aa','G1_aa','H1_aa','I1_aa',\
              'I2_la','H2_la','G2_la','F2_la','E2_la','D2_la','C2_la','B2_la','A2_la',\
              'A3_aa','B3_aa','C3_aa','D3_aa','E3_aa','F3_aa','G3_aa','H3_aa','I3_aa',\
              'I4_la','H4_la','G4_la','F4_la','E4_la','D4_la','C4_la','B4_la','A4_la',\
              'A5_aa','B5_aa','C5_aa','D5_aa','E5_aa','F5_aa','G5_aa','H5_aa','I5_aa',\
              'I6_la','H6_la','G6_la','F6_la','E6_la','D6_la','C6_la','B6_la','A6_la',\
              'A7_aa','B7_aa','C7_aa','D7_aa','E7_aa','F7_aa','G7_aa','H7_aa','I7_aa',\
              'I8_la','H8_la','G8_la','F8_la','E8_la','D8_la','C8_la','B8_la','A8_la',\
              'A9_aa','B9_aa','C9_aa','D9_aa','E9_aa','F9_aa','G9_aa','H9_aa','I9_aa']
    meta_list = [list11, list12, list14, list19, list23, list33, list41, list55, list77, list99]
    for listy in meta_list:
        xstart, ystart = get_xy(listy[0])
        string_xstart = '%1.4f' %xstart
        string_ystart = '%1.4f' %ystart
        k =  [i[0] for i in listy]
        occurence = [k.count(x) for x in k]
        if len(set(occurence)) == 1:
            xblocks = int(occurence[0])
        else:
            print 'here'
        yblocks = int(len(set([x[0] for x in listy])))
        if listy[0][-2:] == 'aa':
            coltype = 41
        elif listy[0][-2:] == 'la':
            coltype = 42
        yy = int(str(xblocks) + str(yblocks))
        path_dict[yy]=[string_xstart, string_ystart, xblocks, yblocks, coltype, listy]
    return path_dict

def scrape_dcparameters():
    f = open('setdcparams.txt', 'r').readlines()
    #f = open('/localhome/local/Documents/sacla/parameter_files/setdcparams.txt', 'r').readlines()
    for line in f:
        entry = line.rstrip().split()
        if 'chipname' in entry[0].lower():
            chipname = entry[1]
        elif 'visit_id' in entry[0].lower():
            visit_id = entry[1]
        elif 'proteinname' in entry[0].lower():
            proteinname = entry[1]
        elif 'chipcapacity' in entry[0].lower():
            chipcapacity = entry[1]
        elif 'blockcapacity' in entry[0].lower():
            blockcapacity = entry[1]
        elif 'path_key' in entry[0].lower():
            path_key = entry[1]
    return chipname, visit_id, proteinname, chipcapacity, blockcapacity, path_key

def shotLister_alpha(chipname):
    list_of_lines = []
    fiducial_list = index11664_fiducials()
    for R in string.letters[26:35]:
        for C in [str(num) for num in range(1,10)]:
            for r in string.letters[:12]:
                for c in string.letters[:12]:
                    addr = '_'.join([R+C, r+c])
                    xtal_name = '_'.join([chipname, addr])
                    (x, y) = get_xy(xtal_name)
                    if addr in fiducial_list:
                        pres = '0'
                    else:
                        pres = '-1'
                    line = '\t'.join([xtal_name, str(x), str(y), '0.0', pres]) + '\n'
                    list_of_lines.append(line)
    return list_of_lines

def shotLister_E_SnakeCols(chipname):
    road_list = ['A','B','C','D','E','F','G','H','I']
    daor_list = ['I','H','G','F','E','D','C','B','A']
    cros_list = ['1','2','3','4','5','6','7','8','9']
    wind_list = ['a','b','c','d','e','f','g','h','i','j','k','l']
    dniw_list = ['l','k','j','i','h','g','f','e','d','c','b','a']
    fiducial_list = index11664_fiducials()
    list_of_lines = []
    for C in range(9):
        for R in range(9):
            for c in range(12):
                for r in range(12):
                    if (C % 2 == 0):
                        if (c % 2 == 0):
                            addr = road_list[R] + cros_list[C] + '_' + wind_list[c] + wind_list[r]
                        else:
                            addr = road_list[R] + cros_list[C] + '_' + wind_list[c] + dniw_list[r]
                    else:
                        if (c % 2 == 0):
                            addr = daor_list[R] + cros_list[C] + '_' + dniw_list[c] + wind_list[r]
                        else:
                            addr = daor_list[R] + cros_list[C] + '_' + dniw_list[c] + dniw_list[r]
                    xtal_name = '_'.join([chipname, addr])
                    (x, y) = get_xy(xtal_name)
                    if addr in fiducial_list:
                        pres = '0'
                    else:
                        pres = '-1'
                    line = '\t'.join([xtal_name, str(x), str(y), '0.0', pres]) + '\n'
                    list_of_lines.append(line)
    return list_of_lines

def check_files(args):
    chipname, visit_id, proteinname, chipcapacity, blockcapacity, path_key = scrape_dcparameters()
    #file_path = '/localhome/local/Documents/sacla/chips/' + proteinname
    file_path = proteinname
    print file_path, '<--------------------------------\n'
    try:
        os.stat(file_path)
    except:
        os.makedirs(file_path)
    for suffix in args:
        full_file_path = file_path + '/' + chipname + suffix
        if os.path.isfile(full_file_path):
            timestr = time.strftime("%Y%m%d_%H%M%S_")
            timestamp_fid = file_path + '/' + timestr + chipname + suffix 
            os.rename(full_file_path, timestamp_fid)
            print '\n', 'already exists ... moving old file:'
            print full_file_path, '\n', timestamp_fid
    return 1

def write_headers(args):
    chipname, visit_id, proteinname, chipcapacity, blockcapacity, path_key = scrape_dcparameters()
    for suffix in ['.addr', '.spec', '.shot']:
        #full_file_path = visit_id+ '/chips/'+ proteinname+ '/'+ chipname+ suffix
        full_file_path = proteinname+ '/'+ chipname+ suffix
        g = open(full_file_path, 'w')
        g.write('#23456789012345678901234567890123456789012345678901234567890123456789012345678901234567890\n#\n')
        g.write('#&SACLA\tproteinname = %s\n'    %proteinname)
        g.write('#&SACLA\tlocalfolder = %s\n'    %visit_id)
        g.write('#&SACLA\tchipname = %s\n'       %chipname)
        g.write('#&SACLA\tchipcapacity = %s\n'   %chipcapacity)
        g.write('#&SACLA\tblockcapacity = %s\n'  %blockcapacity)
        g.write('#&SACLA\tpath_key = %s\n'       %path_key)
        g.write('#\n')
        g.write('#XtalAddr      XCoord  YCoord  ZCoord  Present Shot  Spare04 Spare03 Spare02 Spare01\n')
    g.close()

def write_file(suffix='.addr', order='Alphanumeric'):
    chipname, visit_id, proteinname, chipcapacity, blockcapacity, path_key = scrape_dcparameters()
    #file_path = '/localhome/local/Documents/sacla/chips/' + proteinname
    file_path = proteinname
    full_file_path = file_path + '/' + chipname + suffix
    g = open(full_file_path, 'a')

    if order == 'Alphanumeric':
        list_of_lines = shotLister_alpha(chipname)
    elif order == 'E_SnakeCols':
        list_of_lines = shotLister_E_SnakeCols(chipname)
    else:
        print 'Fail'

    for line in list_of_lines:
        g.write(line)
    g.close() 

def main():
    check_files(['.addr', '.spec', '.shot'])
    write_headers(['.addr', '.spec', '.shot'])
    write_file('.addr', 'Alphanumeric')
    write_file('.spec', 'E_SnakeCols')
    write_file('.shot', 'E_SnakeCols')

if __name__ == '__main__':
    main()
