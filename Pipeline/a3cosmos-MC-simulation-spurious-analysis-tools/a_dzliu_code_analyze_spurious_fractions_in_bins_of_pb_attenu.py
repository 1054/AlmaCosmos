#!/usr/bin/env python
# 

import os, sys, re, copy
import numpy as np
import astropy
from astropy.table import Table


# Check "simu_data_input.txt"
if not os.path.isfile("simu_data_input.txt"):
     print('Error! "%s" was not found!'%("simu_data_input.txt"))
     sys.exit()


# Read "simu_data_input.txt"
tb = Table.read("simu_data_input.txt", format='ascii.commented_header')
#
# columns:
# ID S_in S_out e_S_out S_peak S_res noise 
# Maj_in Min_in PA_in Maj_out Min_out PA_out Maj_beam Min_beam PA_beam 
# pb_attenu image_file_STR simu_name_STR


# Bin by ln(pb_attenu)
ln_pb_attenu = np.log(tb['pb_attenu'])
ln_pb_attenu_bin_edges = np.linspace(np.log(0.2), np.log(1.0), num=14, endpoint=True)

for i in range(len(ln_pb_attenu_bin_edges)-1):
     ln_pb_attenu_bin_edge0 = ln_pb_attenu_bin_edges[i]
     ln_pb_attenu_bin_edge1 = ln_pb_attenu_bin_edges[i+1]
     mask = np.logical_and(ln_pb_attenu > ln_pb_attenu_bin_edge0, ln_pb_attenu <= ln_pb_attenu_bin_edge1)
     









