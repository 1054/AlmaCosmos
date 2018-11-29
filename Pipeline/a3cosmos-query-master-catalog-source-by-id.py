#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os, sys, json
import numpy as np
import astropy
from astropy.table import Table
from copy import copy
from pprint import pprint
from datetime import datetime

if sys.version_info.major >= 3:
    long = int

script_dir = os.path.dirname(os.path.abspath(__file__))
current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S %Z')



# 
# Usage
def Usage():
    print('Usage: ')
    print('  a3cosmos-query-master-catalog-source-by-id.py ID1 ID2 ID3 # we will print their ra dec')
    #print('  a3cosmos-query-master-catalog-source-by-id.py ID1 ID2 ID3 -radius 5.0 # we can also search for sources around it within a given radius')
    print('')


# 
# read user input
master_catalog_file = '/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits.gz'
input_IDs = []
input_radius = []
iarg = 1
while iarg < len(sys.argv):
    arg_str = sys.argv[iarg].lower().replace('--','-')
    if arg_str == '-radius':
        if iarg+1 < len(sys.argv):
            iarg += 1
            input_radius.append(float(sys.argv[iarg])) #<TODO># 
    else:
        input_IDs.append(float(sys.argv[iarg]))
    iarg += 1

if len(input_IDs) == 0:
    Usage()
    sys.exit()
if len(input_radius) == 0:
    input_radius = [0.0] # arcsec
if len(input_radius) < len(input_IDs):
    input_radius.extend([input_radius[-1]]*(len(input_IDs)-len(input_radius)))


# 
# read master catalog
cat = Table.read(master_catalog_file)


# 
# loop input_IDs
for i in range(len(input_IDs)):
    match_index = np.argwhere(cat['ID']==input_IDs[i]).flatten().tolist()
    if len(match_index) > 0:
        found_RA = cat['RA'][match_index[0]]
        found_Dec = cat['Dec'][match_index[0]]
        print('Master Catalog ID: %d; RA Dec: %s %s'%(input_IDs[i], found_RA, found_Dec))
    else:
        print('*'*30)
        print('Error! ID %d was not found in the Master Catalog "%s"!'%(input_IDs[i], master_catalog_file))
        print('*'*30)








