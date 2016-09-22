import os, re, sys

def scrape_inp_fid(fid):
    f = open(fid, 'r').readlines()
    filepath, pattern, spots_xml_fid, spot_count_min = 4 * (False, )
    for line in f:
        entry = line.rstrip().split('=')
        if 'filepath' in entry[0].lower():
            filepath = str(entry[1]).strip()
        elif 'pattern' in entry[0].lower():
            pattern = str(entry[1]).strip()
        elif 'spots_xml_fid' in entry[0].lower():
            spots_xml_fid = str(entry[1]).strip()
        elif 'spot_count_min' in entry[0].lower():
            spot_count_min = int(entry[1])
        else:
            pass
    if not filepath.endswith('/'):
        filepath += '/'
        if not os.path.isdir(filepath):
            filepath = define_filepath()
    print '\nFrom Input file', fid
    if spots_xml_fid:
        filepath, pattern = 2 * (False, )
        print 'spots_xml_fid:  ', spots_xml_fid
    else:
        print 'filepath ;  ', filepath
        print 'pattern  :  ', pattern
    print 'spot_count_min    :  ', spot_count_min
    return filepath, pattern, spots_xml_fid, spot_count_min 

def locate_xml_file(spots_xml_fid):
    if not os.path.isfile(spots_xml_fid):
        print 'Cannot Locate Spots XML file', spots_xml_fid
        xml_path = raw_input('Type xml_path \n/dls/i24/data/2015/nt11175-131/')
        xml_path = '/dls/i24/data/2015/nt11175-131/' + xml_path
        if os.path.isdir(xml_path):
            if os.path.isfile(xml_path + '/' + spots_xml_fid):
                return xml_path
            else:
                print 'Cannot find file'
                pass
    else:
        xml_path = os.path.realpath('.')
    return xml_path 

def read_xml(spots_xml_fid):
    f = open(spots_xml_fid)
    dict = {}
    ff = f.readlines()
    for i, line in enumerate(ff):
        entry = re.split('<|>', line)
        #print i, entry
        if '-------------' in entry[0]:
            return dict
        if 'image' in entry[1]:
            cbf = entry[2].split('/')[-1]
            image_num = cbf.split('.')[0][-5:]
            spot_count    = re.split('<|>', ff[i+1])[2]
            spot_count_ni = re.split('<|>', ff[i+2])[2]
            total_inten   = re.split('<|>', ff[i+6])[2]
            if 'index' in ff[i+8]:
                n_index = re.split('<|>', ff[i+8])[2]
                frac_index = re.split('<|>', ff[i+9])[2]
            else:
                n_index = '0'
                frac_index = '0'
            dict[image_num] = cbf, spot_count, spot_count_ni, \
                    total_inten, n_index, frac_index
    f.close()
    return dict

def main(xml_fid):
    print 80*'-'

    xml_dict = read_xml(xml_fid)
    print len(xml_dict)

    f = open(xml_fid[:-3] + 'col', 'w')
    for k in sorted(xml_dict.keys()):
        v = xml_dict[k]
        line = k + '\t' + '\t'.join(v) + '\n' 
        f.write(line)
    f.close()

    print 80*'-'

if  __name__ == '__main__':
    main(sys.argv[1])





    
