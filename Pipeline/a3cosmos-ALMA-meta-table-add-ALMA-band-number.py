#!/usr/bin/env python
# 

import os, sys, re, shutil, time, datetime
import numpy as np
import astropy
from astropy.table import Table, Column


# Check user input
if len(sys.argv) <= 2:
    print('Usage: ')
    print('  %s \\'%(os.path.basename(__file__)))
    print('  %s \\'%('input_meta_table_file.fits'))
    print('  %s'%('output_meta_table_file.fits'))
    sys.exit()


# Read user input
input_meta_table_file = sys.argv[1]
output_meta_table_file = sys.argv[2]


# Determine input file format
if re.match(r'.*\.fits', input_meta_table_file, re.IGNORECASE):
    input_meta_table_format = 'fits'
    input_meta_table_basename = re.sub(r'^(.*)\.fits', r'\1', input_meta_table_file, re.IGNORECASE)
else:
    input_meta_table_format = 'ascii'
    input_meta_table_basename = re.sub(r'^(.*)\.[^.]+', r'\1', input_meta_table_file, re.IGNORECASE)

if re.match(r'.*\.fits', output_meta_table_file, re.IGNORECASE):
    output_meta_table_format = 'fits'
    output_meta_table_basename = re.sub(r'^(.*)\.fits', r'\1', output_meta_table_file, re.IGNORECASE)
else:
    output_meta_table_format = 'ascii'
    output_meta_table_basename = re.sub(r'^(.*)\.[^.]+', r'\1', output_meta_table_file, re.IGNORECASE)


# Read meta data table
meta_table = Table.read(input_meta_table_file, format=input_meta_table_format)
#print(meta_table.columns)


# Read wavelength column
if 'wavelength' in meta_table.columns:
    data_wavelength = meta_table['wavelength'] # output wavelength in units of um.
elif 'Obs_wavelength' in meta_table.columns:
    data_wavelength = meta_table['Obs_wavelength'] # output wavelength in units of um.
elif 'frequency' in meta_table.columns:
    data_wavelength = 2.99792458e5 / meta_table['frequency'] # assuming 'frequency' is in units of GHz, output wavelength in units of um.
elif 'Obs_frequency' in meta_table.columns:
    data_wavelength = 2.99792458e5 / meta_table['Obs_frequency'] # assuming 'frequency' is in units of GHz, output wavelength in units of um.
else:
    print('Error! Could not determine which column is the observing wavelength column!')


# Setup ALMA band dict (https://www.eso.org/public/teles-instr/alma/receiver-bands/)
ALMA_Band_Dict = {}
ALMA_Band_Dict['Band 3'] = (2.6e3, 3.6e3)
ALMA_Band_Dict['Band 4'] = (1.8e3, 2.4e3)
ALMA_Band_Dict['Band 5'] = (1.4e3, 1.8e3)
ALMA_Band_Dict['Band 6'] = (1.1e3, 1.4e3)
ALMA_Band_Dict['Band 7'] = (0.8e3, 1.1e3)
ALMA_Band_Dict['Band 8'] = (0.6e3, 0.8e3)
ALMA_Band_Dict['Band 9'] = (0.4e3, 0.5e3)
#ALMA_Band_Dict['Band 10'] = (0.3e3, 0.4e3)

meta_table.add_column(Column((np.zeros(len(meta_table))*0-1).astype(int)), name='ALMA_band')
#print(meta_table.colnames)


# loop to match wavelength and set ALMA_band
for ALMA_Band_Name in ALMA_Band_Dict:
    w1, w2 = ALMA_Band_Dict[ALMA_Band_Name]
    mask = np.logical_and(data_wavelength>=w1, data_wavelength<w2)
    meta_table['ALMA_band'][mask] = int(re.sub(r'^Band ', r'', ALMA_Band_Name))


# Save to disk
if os.path.isfile(output_meta_table_file):
    print('Backing-up "%s" as "%s"'%(output_meta_table_file, output_meta_table_file+'.backup'))
    shutil.move(output_meta_table_file, output_meta_table_file+'.backup')
    
if output_meta_table_format == 'fits':
    meta_table.write(output_meta_table_file, format=output_meta_table_format)
else:
    meta_table.write(output_meta_table_file, format='ascii.fixed_width', delimiter='  ', bookend=True)
    with open(output_meta_table_file, 'r+') as fp:
        fp.seek(0)
        fp.write('#')

print('Output to "%s"!'%(output_meta_table_file))


# Save readme file 
with open(output_meta_table_basename+'.readme.txt', 'w') as fp:
    fp.write('created by:\n\n')
    fp.write(os.path.abspath(__file__)+'\n\n')
    fp.write('at:\n\n')
    fp.write(datetime.datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss')+' '+time.localtime().tm_zone+'\n\n')

print('Output to "%s"!'%(output_meta_table_basename+'.readme.txt'))





