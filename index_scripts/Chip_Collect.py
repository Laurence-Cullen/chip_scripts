import pv
import os, re, sys
import time, math, string
from time import sleep
from ca import caput, caget 
from shutil import copyfile

path_list1 = ['A1_aa','B1_aa','C1_aa','D1_aa','E1_aa','F1_aa','G1_aa','H1_aa','I1_aa',\
              'I2_la','H2_la','G2_la','F2_la','E2_la','D2_la','C2_la','B2_la','A2_la',\
              'A3_aa','B3_aa','C3_aa','D3_aa','E3_aa','F3_aa','G3_aa','H3_aa','I3_aa',\
              'I4_la','H4_la','G4_la','F4_la','E4_la','D4_la','C4_la','B4_la','A4_la',\
              'A5_aa','B5_aa','C5_aa','D5_aa','E5_aa','F5_aa','G5_aa','H5_aa','I5_aa',\
              'I6_la','H6_la','G6_la','F6_la','E6_la','D6_la','C6_la','B6_la','A6_la',\
              'A7_aa','B7_aa','C7_aa','D7_aa','E7_aa','F7_aa','G7_aa','H7_aa','I7_aa',\
              'I8_la','H8_la','G8_la','F8_la','E8_la','D8_la','C8_la','B8_la','A8_la',\
              'A9_aa','B9_aa','C9_aa','D9_aa','E9_aa','F9_aa','G9_aa','H9_aa','I9_aa'] 
path_list2 = ['A1_aa']
path_list3 = ['F2_la']
path_list4 = ['A1_aa','B1_aa']
path_list5 = ['A1_aa','A2_la','A3_aa','A4_la']
path_list6 = ['A1_aa','B1_aa','C1_aa','C2_la','B2_la','A2_la']
path_list7 = ['A1_aa','B1_aa','C1_aa','D1_aa','E1_aa','F1_aa','G1_aa','H1_aa','I1_aa']
path_list8 = ['H2_la','G2_la','F2_la','E2_la','D2_la','C2_la','B2_la',\
              'B3_aa','C3_aa','D3_aa','E3_aa','F3_aa','G3_aa','H3_aa',\
              'H4_la','G4_la','F4_la','E4_la','D4_la','C4_la','B4_la',\
              'B5_aa','C5_aa','D5_aa','E5_aa','F5_aa','G5_aa','H5_aa',\
              'H6_la','G6_la','F6_la','E6_la','D6_la','C6_la','B6_la',\
              'B7_aa','C7_aa','D7_aa','E7_aa','F7_aa','G7_aa','H7_aa',\
              'H8_la','G8_la','F8_la','E8_la','D8_la','C8_la','B8_la',]

def scrape_dcparameters():
    f = open('/dls_sw/i24/scripts/fastchips/parameter_files/setdcparams.txt', 'r').readlines()
    for line in f:
        entry = line.rstrip().split()
        if 'chipname' in entry[0].lower():
            chipname = entry[1]
        elif 'visit_id' in entry[0].lower():
            visit_id = entry[1]
        elif 'filepath' in entry[0].lower():
            filepath = entry[1]
        elif 'chipcapacity' in entry[0].lower():
            chipcapacity = entry[1]
        elif 'blockcapacity' in entry[0].lower():
            blockcapacity = entry[1]
        elif 'exposure' in entry[0].lower():
            exptime = entry[1]
        elif 'distance' in entry[0].lower():
            dcdetdist = entry[1]
    print chipname
    print visit_id
    print filepath
    print chipcapacity
    print blockcapacity
    print exptime
    print dcdetdist
    return chipname, visit_id, filepath, chipcapacity, blockcapacity, exptime, dcdetdist

def addr_scrape(fid):
    f = open(fid, 'r').readlines()
    chipname = fid.split('.')[0]
    for line in f:
        if line.startswith("#&diams"):
            entry = line.rstrip().split()
            if 'filepath' in entry[1].lower():
                filepath = str(entry[3])
            elif 'chipcapacity' in entry[1].lower():
                chipcapacity = int(entry[3])
            elif 'blockcapacity' in entry[1].lower():
                blockcapacity = int(entry[3])
            elif 'exptime' in entry[1].lower():
                exptime = float(entry[3])
            else:
                print line, entry
        else:
            pass
    if 'dls/i24/data' in filepath:
        filepath = filepath.replace('dls/i24/data','ramdisk')
        print 'Detector filepath:', filepath
    else:
        print 'Possible filepath error, expected /dls/i24/data/ in filepath'
        print '    -------------->', chipname, filepath, chipcapacity, blockcapacity, exptime
    return chipname, filepath, chipcapacity, blockcapacity, exptime

def get_xy(addr, chip_type=11664):
    w2w = 0.125
    b2b_horz = 0.825
    b2b_vert = 1.125
    cell_format = [9, 9, 12, 12]
    entry = addr.split('_')[-2:]
    R, C = entry[0][0], entry[0][1]
    r2, c2 = entry[1][0], entry[1][1]
    blockR = int(string.uppercase.index(R))
    blockC = int(C) - 1
    windowR = string.lowercase.index(r2)
    windowC = string.lowercase.index(c2)
    x = (blockC * b2b_horz) + (blockC * (cell_format[2]-1) * w2w) + (windowC * w2w)
    y = (blockR * b2b_vert) + (blockR * (cell_format[3]-1) * w2w) + (windowR * w2w)
    return x, y 

def setup_pilatus(chipname, visit_id, filepath, total_numb_imgs, exptime, dcdetdist):
    wavelength = caget(pv.wavelength + '.RBV')
    transm = caget(pv.filter_transm)
    acqtime = float(exptime) - 0.001
    pilatus_filepath = visit_id + '/' + filepath
    if 'dls/i24/data' in pilatus_filepath:
        ramdisk_filepath = pilatus_filepath.replace('dls/i24/data', 'ramdisk')
        print 'Detector Filepath', ramdisk_filepath
    else:
        print 'FILEPATH ERROR'
    caput(pv.pilat_file_path, ramdisk_filepath + '/' + chipname + '/')
    caput(pv.pilat_file_name, chipname)
    caput(pv.pilat_numb_imgs, str(total_numb_imgs))
    caput(pv.pilat_acq_time, str(acqtime))
    caput(pv.pilat_acq_period, exptime)
    caput(pv.pilat_trig_mode, 'Mult. Trigger')
    caput(pv.pilat_delay_time, 0)
    ##Image Header
    caput(pv.pilat_wavelength, wavelength)
    caput(pv.pilat_detdist, dcdetdist)
    caput(pv.pilat_transm, transm)
    caput(pv.pilat_beamx, 1232.7)
    caput(pv.pilat_beamy, 1322.3)
    ### for GDA replace waveforms as per the below 
    # caclient.caputStringAsWaveform("BL24I-EA-PILAT-01:cam1:FilePath", filepath)
    ### for GDA replace these lines as per the below
    # CAClient().caput(pv."BL19I-EA-PILAT-01:cam1:AcquireTime", exptime)
    # Must set some basic info in image header
    # Other detector things that need to be set (once per beamtime, not every run)
    # file names need to be properly defined. See BL24I-EA-PILAT-01:cam1:FileTemplate
    print 'Path set as', filepath
    print 'Filename set as', chipname 
    print 'Acquire time set as', acqtime, 's'
    print 'Exposure time set as', exptime, 's'
    return 0

def zebra1(action):
    if action == 'setup':
        # Set up zebra box
        # Gate trigger Source should be external (default is position)
        # Pulse trigger Source should be external (default is position)
        #Trigger to pilatus should be AND of these
        caput(pv.zebra1_soft_b0, '0')
        caput(pv.zebra1_gate_sel, 'External')
        caput(pv.zebra1_puls_sel, 'External')
        caput(pv.zebra1_and3_inp1, '61')
        caput(pv.zebra1_and3_inp2, '1')
        caput(pv.zebra1_out2_ttl, '34')
        caput(pv.zebra1_gate_inp, '61')
        caput(pv.zebra1_puls_inp, '1')
    elif action == 'return to normal':
        #Maybe we should get the Restore From File values here?
        caput(pv.zebra1_gate_sel, 'Position')
        caput(pv.zebra1_puls_sel, 'Position')
        caput(pv.zebra1_gate_inp, '0')
        caput(pv.zebra1_puls_inp, '0')
        caput(pv.zebra1_out2_ttl, '30')
    return 0

def get_chip_prog_values():
    chip_dict = \
    {'X_NUM_STEPS':    [11, 12],
     'Y_NUM_STEPS':    [12, 12],
     'X_STEP_SIZE':    [13, 0.125],
     'Y_STEP_SIZE':    [14, 0.125],
     'DWELL_TIME':     [15, 50],
     'Z_START':        [18, 0]}
    return chip_dict

def get_block_prog_values():
    block_dict = \
    {'X_START':        [16, 0],
     'Y_START':        [17, 0],
     'PATHTYPE':       [19, 31]}
    return block_dict

def load_motion_program_data(motion_program_dict):
    print 'loading prog vars for chip'
    for k, v in motion_program_dict.items():
        pvar = 1000 + v[0]  
        value = str(v[1])
        s = 'P' + str(pvar) + '=' + str(value)
        caput(pv.me14e_pmac_str, s)
        sleep(0.01)
    print 'done'
    return 0 

def setup_beamline(hutch, dcdetdist):
    #################FIX#########################################
    if hutch == 'ready for data collection':
        caput(pv.det_z, dcdetdist)
        caput(pv.blighty_pos, 'Out')
        caput(pv.ap_pos, 'In')
        caput(pv.beamstop_pos, 'Data Collection')
        sleep(2)
        caput(pv.beamstop_rot, 6)
        """
        open main hutch shutter
        """

def main():
    run_num = caget(pv.pilat_file_num)
    print 80*'-', run_num
    caput(pv.me14e_pmac_str, '!x0y0z0')
    chipname, visit_id, filepath, chipcapacity, blockcapacity, exptime, dcdetdist = \
                                                                              scrape_dcparameters()
    print '\n\nChip name is', chipname
    print 'visit_id', visit_id
    print 'filepath', filepath
    print 'chipcapacity', chipcapacity
    print 'blockcapacity', blockcapacity
    print 'Exposure time (sec)', exptime
    print 'detector distance:', dcdetdist
    
    print '--------------'
    path = visit_id + '/processing/'
    copyfile('/dls_sw/i24/scripts/fastchips/parameter_files/setdcparams.txt', \
                      path + filepath + '-' + chipname + '-' + str(run_num) + '.dcparams')
    setup_beamline('ready for data collection', dcdetdist)
    print '--------------'

    starttime = time.ctime()
    print starttime
    path_type = path_list1
    total_numb_imgs = len(path_type*144)
    print 'total_numb_imgs' , total_numb_imgs, '\n\n\n' 
    setup_pilatus(chipname, visit_id, filepath, total_numb_imgs, exptime, dcdetdist)
    zebra1('setup')
    chip_prog_dict = get_chip_prog_values()
    chip_prog_dict['DWELL_TIME'][1] = 1000 * float(exptime)
    load_motion_program_data(chip_prog_dict)
    block_prog_dict = get_block_prog_values()
    caput(pv.pilat_acquire, '1')                                 # Arm pilatus
    caput(pv.zebra1_arm_out, '1')                                # Arm zebra
    caput(pv.zebra1_soft_b1, '1')                                # Open fast shutter (zebra gate)
    caput(pv.pilat_file_num, run_num)
    caput(pv.pilat_file_name, chipname)
    sleep(1.5)

    for addr in path_type:
        x, y = get_xy(addr)
        print x, y
        print 20*addr[:3], '\n', 20*addr[:3], '\n', 20*addr[:3]
        block_prog_dict['X_START'][1] = x
        block_prog_dict['Y_START'][1] = y
        if 'aa' in addr:
            block_prog_dict['PATHTYPE'][1] = 31
            print 31
        elif 'la' in addr:
            block_prog_dict['PATHTYPE'][1] = 32
            print 32
        sleep(0.01)
        load_motion_program_data(block_prog_dict)
        sleep(0.01)
        print 3*'--------------------------------\n'
        caput(pv.me14e_pmac_str, '&1b10r')                       # Run motion program 10
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        sleep((144 * (float(exptime) + 0.012)))            # 9 ms movetime 
        print 3*'--------------------------------\n'
  
    caput(pv.zebra1_soft_b1, '0')                                # Close the fast shutter
    caput(pv.zebra1_arm_out, '0')                                # Disarm the zebra
    zebra1('return to normal')
    caput(pv.pilat_trig_mode, 'Ext. Trigger')
    caput(pv.pilat_file_num, run_num + 1)
    endtime = time.ctime()
    caput(pv.me14e_pmac_str, '!x0y0z0')

    print 3*'\n'
    print 'Summary'
    print 'Chip name:', chipname
    print 'Filepath:', filepath
    print 'Number of images collected:', chipcapacity
    print 'Start time:', starttime
    print 'End time:', endtime
    print 3*'\n'

if __name__ == "__main__":
    main()
