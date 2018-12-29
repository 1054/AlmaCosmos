#!/usr/bin/env python
# 

import os, sys, re
import numpy as np
import astropy
from astropy.table import Table

tb = Table.read('/Users/dzliu/Work/AlmaCosmos/Simulations/Monte_Carlo_Simulation_Physically_Motivated/Output_Prior_Simulation_Catalog_with_convolved_sizes.fits', format='fits')

print(tb.colnames)

tbgroups = tb.group_by('Image')

key_list = []
count_list = []
primary_beam_list = []
obs_wavelength_list = []

for key, group in zip(tbgroups.groups.keys, tbgroups.groups):
    key_list.append(key['Image'])
    count_list.append(len(group))
    primary_beam_list.append(group[0]['primary_beam'])
    obs_wavelength_list.append(group[0]['wavelength'])

for i in range(len(key_list)):
    print(key_list[i], count_list[i], primary_beam_list[i], obs_wavelength_list[i])


