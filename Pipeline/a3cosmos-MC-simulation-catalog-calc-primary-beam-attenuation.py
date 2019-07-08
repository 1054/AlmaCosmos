#!/usr/bin/env python
# 

import os, sys, re, shutil
import numpy as np

import astropy
from astropy.table import Table

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import ScalarFormatter, FuncFormatter, FormatStrFormatter, NullFormatter, LogLocator



# prepare function
def calc_primary_beam_attenuation(primary_beam_dist, sky_frequency, verbose=False):
    # primary_beam_dist # arcsec
    primary_beam_disq = primary_beam_dist**2
    sky_wavelength = 2.99792458e5/sky_frequency # um
    primary_beam_diam = 12.0 # ALMA 12m
    #primary_beam_tape = 10.0 # https://safe.nrao.edu/wiki/bin/view/ALMA/AlmaPrimaryBeamCorrection
    #primary_beam_bpar = 1.243 - 0.343 * primary_beam_tape + 0.12 * primary_beam_tape**2 # http://legacy.nrao.edu/alma/memos/html-memos/alma456/memo456.pdf -- Eq(18)
    primary_beam_bpar = 1.13
    primary_beam_fwhm = primary_beam_disq*0.0 + primary_beam_bpar * sky_wavelength / (primary_beam_diam*1e6) / np.pi * 180.0 * 3600.0 # arcsec
    primary_beam_sigm = primary_beam_disq*0.0 + primary_beam_fwhm/(2.0*np.sqrt(2.0*np.log(2)))
    primary_beam_attenuation = np.exp((-primary_beam_disq) / (2.0*((primary_beam_sigm)**2)) ) #<TODO><20170613># 
    if verbose == True:
        print('primary_beam_dist', primary_beam_dist, 'arcsec')
        print('primary_beam_fwhm', primary_beam_fwhm, 'arcsec')
        print('primary_beam_sigm', primary_beam_sigm, 'arcsec')
        print('ratio_of_dist_to_pb_rad', primary_beam_dist/primary_beam_fwhm*2)
        print('primary_beam_attenuation', primary_beam_attenuation)
    return primary_beam_attenuation

# prepare function
def calc_primary_beam_dist(primary_beam_attenuation, sky_frequency):
    # inversed process of calc_primary_beam_attenuation
    sky_wavelength = 2.99792458e5/sky_frequency # um
    primary_beam_diam = 12.0 # ALMA 12m
    primary_beam_bpar = 1.13
    primary_beam_fwhm = primary_beam_attenuation*0.0 + primary_beam_bpar * sky_wavelength / (primary_beam_diam*1e6) / np.pi * 180.0 * 3600.0 # arcsec
    primary_beam_sigm = primary_beam_attenuation*0.0 + primary_beam_fwhm/(2.0*np.sqrt(2.0*np.log(2)))
    primary_beam_disq = - np.log(primary_beam_attenuation) * (2.0*((primary_beam_sigm)**2))
    primary_beam_dist = np.sqrt(primary_beam_disq)
    return primary_beam_dist/primary_beam_fwhm # return normalized value






if __name__ == '__main__':
    
    # check user input
    if len(sys.argv) <= 1:
        print('Usage: ')
        print('    a_dzliu_code_calc_primary_beam_attenuation_for_input_catalog.py input_catalog.fits')
        print('')
        sys.exit()
    
    # 
    input_catalog_file = sys.argv[1]
    print('Reading input catalog "%s"'%(input_catalog_file))
    #print(re.match(r'.*\.fits$', input_catalog_file, re.IGNORECASE))
    
    # 
    if re.match(r'.*\.fits$', input_catalog_file, re.IGNORECASE):
        output_catalog_name = re.sub(r'\.fits$', r'', input_catalog_file, re.IGNORECASE)
        output_format = 'fits'
        tb = Table.read(sys.argv[1])
    elif re.match(r'.*\.[^\.]+$', input_catalog_file, re.IGNORECASE):
        output_catalog_name = re.sub(r'\.[^\.]+$', r'', input_catalog_file, re.IGNORECASE)
        output_format = 'ascii'
        tb = Table.read(sys.argv[1], format='ascii.commented_header')
    else:
        output_catalog_name = input_catalog_file
        output_format = 'ascii'
        tb = Table.read(sys.argv[1], format='ascii.commented_header')
    
    # read user input
    primary_beam_dist = np.sqrt( ((tb['ra'] - tb['cen_ra'])*np.cos(np.deg2rad(tb['cen_dec']))*3600.0)**2 + ((tb['dec'] - tb['cen_dec'])*3600.0)**2 )
    sky_frequency = 2.99792458e5 / tb['wavelength']
    
    tb['pb_attenu'] = calc_primary_beam_attenuation(primary_beam_dist, sky_frequency, verbose=False)
    
    if output_format == 'ascii':
        output_catalog_file = output_catalog_name+'_with_pb_attenu.txt'
        if os.path.isfile(output_catalog_file):
            print('Backing-up "%s" as "%s"'%(output_catalog_file, output_catalog_file+'.backup'))
            shutil.move(output_catalog_file, output_catalog_file+'.backup')
        tb.write(output_catalog_file, format='ascii.fixed_width')
        with open(output_catalog_file, 'r+') as fp:
            fp.seek(0)
            fp.write('#')
        print('Output to "%s"'%(output_catalog_file))
    else:
        output_catalog_file = output_catalog_name+'_with_pb_attenu.fits'
        if os.path.isfile(output_catalog_file):
            print('Backing-up "%s" as "%s"'%(output_catalog_file, output_catalog_file+'.backup'))
            shutil.move(output_catalog_file, output_catalog_file+'.backup')
        tb.write(output_catalog_file, format='fits')
        print('Output to "%s"'%(output_catalog_file))
    
    #./a_dzliu_code_calc_primary_beam_attenuation.py 19.288 230
    #primary_beam_dist 19.288 arcsec
    #primary_beam_fwhm 25.31717231449028 arcsec
    #primary_beam_sigm 10.751213184172439 arcsec
    #ratio_of_dist_to_pb_rad 1.5237088692531842 # ratio of distance to half of the primary beam FWHM, when it is 1.0, pb attenuation is 0.5.
    #primary_beam_attenuation 0.20003318740273365




