import pv
import os, re, sys
import math
import string
from time import sleep
from ca import caput, caget 

def setdcparameters():
    print 10*'set'
    visit_id = '/dls/i24/data/2016/nt11175-139'
    filepath = caget(pv.me14e_filepath)
    chipname = caget(pv.me14e_chipname)
    chipcapacity = caget(pv.me14e_chipcapacity)
    blockcapacity = caget(pv.me14e_blockcapacity)
    exptime = caget(pv.me14e_exptime)
    dcdetdist=caget(pv.me14e_dcdetdist)
    print '\n\nchipname:', chipname
    print 'visit_id:', visit_id
    print 'filepath:', filepath
    print 'chip capacity:', chipcapacity
    print 'block capacity:', blockcapacity
    print 'exposure time:', exptime
    print 'detector distance:', dcdetdist
    print '\n'
    f = open('/dls_sw/i24/scripts/fastchips/parameter_files/setdcparams.txt','w')
    f.write('chipname \t%s\n' %chipname)
    f.write('visit_id \t%s\n' %visit_id)
    f.write('filepath \t%s\n' %filepath)
    f.write('chipcapacity \t%s\n' %chipcapacity)
    f.write('blockcapacity \t%s\n' %blockcapacity)
    f.write('exposure \t%s\n' %exptime)
    f.write('distance \t%s\n' %dcdetdist)
    f.close()
    print 10*'set'
    return 0

def moveto(place):
    if place == 'zero':
        caput(pv.me14e_stage_x, 0.0)  
        caput(pv.me14e_stage_y, 0.0)

    elif place == 'A9_al':
        caput(pv.me14e_stage_x, 18.975)  
        caput(pv.me14e_stage_y, 0.0)

    elif place == 'I1_la':
        caput(pv.me14e_stage_x, 0.0)  
        caput(pv.me14e_stage_y, -21.375)

    elif place == 'I9_ll':
        caput(pv.me14e_stage_x, 18.975)  
        caput(pv.me14e_stage_y, -21.375)

    elif place == 'yag':
        caput(pv.me14e_stage_x, 43.0)  
        caput(pv.me14e_stage_y, -33.0)
        caput(pv.beamstop_pos, 'CheckBeam')
   
    elif place == 'chip':
        caput(pv.me14e_stage_x, 0.0)  
        caput(pv.me14e_stage_y, 0.0)
        caput(pv.beamstop_pos, 'Data Collection')
        caput(pv.ap_pos, 'In')

    elif place == 'exchange':
        caput(pv.me14e_stage_x, 43)  
        caput(pv.me14e_stage_y, -33)
        caput(pv.me14e_stage_z, 10)
        caput(pv.beamstop_pos, 'Robot')
        caput(pv.ap_pos, 'Out')
        caput(pv.det_z, 1499)
    else:
        print 'Unknown Argument In Method moveto'

def fiducial(point):
    f = open('/dls_sw/i24/scripts/fastchips/parameter_files/fiducial_%s.txt' %point,'w')
    print caget(pv.me14e_stage_x + '.RBV')
    print caget(pv.me14e_stage_y + '.RBV')
    print caget(pv.me14e_stage_z + '.RBV')
    f.write('%1.3f\n' %caget(pv.me14e_stage_x + '.RBV'))
    f.write('%1.3f\n' %caget(pv.me14e_stage_y + '.RBV'))
    f.write('%1.3f\n' %caget(pv.me14e_stage_z + '.RBV'))
    f.close() 
    return 0
     
def cs_maker():
    fiducial_dict = {}
    fiducial_dict['f1'] = {}
    fiducial_dict['f2'] = {}

    fiducial_dict['f1']['x'] = 18.975 
    fiducial_dict['f1']['y'] = 0 
    fiducial_dict['f1']['z'] = 0 

    fiducial_dict['f2']['x'] = 0 
    fiducial_dict['f2']['y'] = 21.375
    fiducial_dict['f2']['z'] = 0 
    
    #1mm / counts per nanometer (give cts/mm)
    scale = 10000
    #d1, d2 = fiducial_positions
    f1 = open('/dls_sw/i24/scripts/fastchips/parameter_files/fiducial_1.txt','r')    
    f1_lines = f1.readlines()
    f1_lines_x = f1_lines[0].rstrip('/n') 
    f1_lines_y = f1_lines[1].rstrip('/n') 
    f1_lines_z = f1_lines[2].rstrip('/n') 
    f1_x = float(f1_lines_x)
    f1_y = float(f1_lines_y)
    f1_z = float(f1_lines_z)

    f2 = open('/dls_sw/i24/scripts/fastchips/parameter_files/fiducial_2.txt','r')    
    f2_lines = f2.readlines()
    f2_lines_x = f2_lines[0].rstrip('/n') 
    f2_lines_y = f2_lines[1].rstrip('/n') 
    f2_lines_z = f2_lines[2].rstrip('/n') 
    f2_x = float(f2_lines_x)
    f2_y = float(f2_lines_y)
    f2_z = float(f2_lines_z)
    #Evaluate numbers
    x1factor = (f1_x / fiducial_dict['f1']['x']) *scale
    y1factor = (f1_y / f1_x)                     *scale
    z1factor = (f1_z / f1_x)                     *scale
    x2factor = (f2_x / f2_y)                     *scale
    y2factor = (f2_y / fiducial_dict['f2']['y']) *scale
    z2factor = (f2_z / f2_y)                     *scale
    z3factor = scale

    cs1 = "#1->%+1.5fX%+1.5fY%+1.5fZ" % (x1factor, y1factor, z1factor)
    cs2 = "#2->%+1.5fX%+1.5fY%+1.5fZ" % (-1*x2factor, y2factor, z2factor)
    cs3 = "#3->0X+0Y%+fZ"    % (z3factor)
    print cs1
    print cs2
    print cs3
    caput(pv.me14e_pmac_str, '!x0y0z0')
    sleep(2)
    caput(pv.me14e_pmac_str, cs1)
    sleep(2)
    caput(pv.me14e_pmac_str, cs2)
    sleep(2)
    caput(pv.me14e_pmac_str, cs3)
    sleep(2)
    print 'done'

def main(args):
    if args[1] == 'moveto':
        moveto(args[2])
    elif args[1] == 'fiducial':
        fiducial(args[2])
    elif args[1] == 'cs_maker':
        cs_maker()
    elif args[1] == 'setdcparameters':
        setdcparameters()
    else:
        print 'Unknown Command'
    pass

if  __name__ == '__main__':
    main(sys.argv)
