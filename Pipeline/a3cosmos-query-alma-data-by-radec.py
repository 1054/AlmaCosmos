#!/usr/bin/env python
# 

import os, sys, re
for i in range(len(sys.path)):
    if sys.path[i].find('GILDAS') >= 0:
        sys.path[i] = ''
    if sys.path[i].find('CASA') >= 0:
        sys.path[i] = ''

if len(sys.argv) <= 1:
    print('Usage: ')
    print('  ./a3cosmos-query-alma-data-by-radec.py ra dec # this will search for images containing the input ra dec')
    print('  ./a3cosmos-query-alma-data-by-radec.py ra dec -radius 15.0 # this will search for images whose center is within the given radius to the input ra dec')
    print('  ./a3cosmos-query-alma-data-by-radec.py ra1 dec1 ra2 dec2 # we can input multiple ra dec')
    print('')
    sys.exit()

import numpy as np, time, json
import astropy
from astropy.table import Table
#from astropy.coordinates import SkyCoord
#from astropy import units as u
#from astroquery import alma
#from astroquery.alma import Alma
#from datetime import datetime, timedelta
#from dateutil import parser



# 
# read user input
input_meta_table_file = os.path.dirname(os.path.dirname(__file__))+os.sep+os.path.join('Data','2018B','a3cosmos_meta_table.fits')
input_freq_support_file = os.path.dirname(os.path.dirname(__file__))+os.sep+os.path.join('Data','2018B','query_ALMA_archive_frequency_support.txt')
input_ra_list = []
input_dec_list = []
input_radius = []
iarg = 1
while iarg < len(sys.argv):
    arg_str = sys.argv[iarg].lower().replace('--','-')
    if arg_str == '-radius':
        if iarg+1 < len(sys.argv):
            iarg += 1
            input_radius.append(float(sys.argv[iarg]))
    else:
        if iarg+1 < len(sys.argv):
            input_ra_list.append(float(sys.argv[iarg]))
            iarg += 1
            input_dec_list.append(float(sys.argv[iarg]))
    iarg += 1

if len(input_radius) == 0:
    input_radius = [0.0] # arcsec
if len(input_radius) < len(input_ra_list):
    input_radius.extend([input_radius[-1]]*(len(input_ra_list)-len(input_radius)))

# 
# debug
debug = False # False #<TODO># 


# 
# read input_meta_table
meta_table = Table.read(input_meta_table_file)
#print(meta_table.columns)


# 
# read freq_support
freq_support = []
with open(input_freq_support_file, 'r') as fp:
    freq_support = json.load(fp)
if len(freq_support) != len(meta_table):
    print('Error! The input freq support file does not match the meta table! This is the software problem! Let the developer know and fix this!')
    sys.exit()
freq_support_simple = [re.findall(r'([0-9.]+)\.\.([0-9.]+)GHz', t) for t in freq_support]
#freq_support_simple = [np.array(re.findall(r'([0-9.]+)\.\.([0-9.]+)GHz', t)).astype(np.float) for t in freq_support]
meta_table['freq_support'] = freq_support_simple


# 
# load input list
for i in range(len(input_ra_list)):
    # 
    # use search radius or directly see if the input ra dec is in the fits image rectangle
    if input_radius[i] > 0.0:
        # use search radius
        mask_radius = np.logical_and( (np.abs(meta_table['OBSRA']-input_ra_list[i]))*np.cos(np.deg2rad(input_dec_list[i]))*3600.0 <= input_radius[i], 
                                      (np.abs(meta_table['OBSDEC']-input_dec_list[i]))*3600.0 <= input_radius[i] )
    else:
        mask_radius = np.logical_and( (np.minimum(meta_table['POS00_RA'],meta_table['POS11_RA'])) <= input_ra_list[i], 
                      np.logical_and( (np.maximum(meta_table['POS00_RA'],meta_table['POS11_RA'])) >= input_ra_list[i], 
                      np.logical_and( (np.minimum(meta_table['POS00_DEC'],meta_table['POS11_DEC'])) <= input_dec_list[i], 
                                      (np.maximum(meta_table['POS00_DEC'],meta_table['POS11_DEC'])) >= input_dec_list[i] ) ) )
    # 
    # then also look for source name constraint <TODO>
    #mask_source_name = 
    # 
    # then combine mask
    mask = mask_radius
    # 
    # then print the query result
    print('#'+'-'*100)
    if np.count_nonzero(mask) > 0:
        meta_table_output = meta_table[mask]
        print('# Found %d image(s) matching the input ra dec %s %s (%d/%d)'%(len(meta_table_output), input_ra_list[i], input_dec_list[i], i+1, len(input_ra_list)))
        print('#'+'-'*100)
        for k in range(len(meta_table_output)):
            #print(meta_table_output[['project','source','image_name','freq_support']])
            if k>0: print('')
            print('project = "%s"'%(meta_table_output['project'][k]))
            print('source = "%s"'%(meta_table_output['source'][k]))
            print('ra = %s'%(input_ra_list[i]))
            print('dec = %s'%(input_dec_list[i]))
            print('offset = %s # arcsec'%(np.sqrt(((input_ra_list[i]-float(meta_table_output['CENRA'][k]))*np.cos(np.deg2rad(float(meta_table_output['CENDEC'][k]))))**2 + (input_dec_list[i]-float(meta_table_output['CENDEC'][k]))**2)*3600.0))
            print('image_center_ra = "%s"'%(float(meta_table_output['CENRA'][k])))
            print('image_center_dec = "%s"'%(float(meta_table_output['CENDEC'][k])))
            print('image_name = "%s"'%(meta_table_output['image_name'][k]))
            print('freq_support = %s'%(meta_table_output['freq_support'][k]))
        print('')
    else:
        print('Sorry! No image found matching the input ra dec %s %s (%d/%d)!'%(input_ra_list[i], input_dec_list[i], i+1, len(input_ra_list)))
        print('')





