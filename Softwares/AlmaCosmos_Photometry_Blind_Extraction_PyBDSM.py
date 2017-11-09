#!/usr/bin/env python2.7
# 
# Aim: run the PyBDSM tool () to extract sources from FITS format images. 
# 
# Last update: 2017-11-08
# 

import os, sys, re
import logging

import platform
if platform.system() == 'Darwin':
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_mac'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages')
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_mac'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages'+os.sep+'bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg')
else:
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_linux'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages')
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_linux'+os.sep+'lib64'+os.sep+'python2.7'+os.sep+'site-packages')
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_linux'+os.sep+'lib64'+os.sep+'python2.7'+os.sep+'site-packages'+os.sep+'bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg')
#print sys.path

import numpy
import scipy
import bdsf


# 
# print usage if no input argument
# 
if len(sys.argv) <= 1:
    print('Usage: ')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Images.fits"                              # providing a FITS image')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Images.fits" "ALMA_Image_List.txt"        # or providing text file which contains a list of FITS images')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" --rms-value 0.00015       # we can also input a constant rms value for all input FITS images')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" --max-numb-gaussian 1     # we can also constrain the maximum number of fitted Gaussian to one Island')
    sys.exit()


# 
# setup logger
# -- https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
# 
class Logger(object):
    def __init__(self, logfile = 'logfile.log'):
        self.terminal = sys.stdout
        self.log = open(logfile, 'a')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

#sys.stdout = Logger()



# 
# setup parameters to read from command line arguments
# 
input_fits_files = []
input_list_files = []
input_loop_start = -1
input_loop_end = -1
input_rms_value = -99
input_ini_gausfit = 'default'
input_peak_fit = True # whether to find and fit peaks of large islands before fitting entire island
output_root = 'Output_Blind_Extraction_Photometry_PyBDSM'

i = 1
while i < len(sys.argv):
    if sys.argv[i].endswith('.fits') or sys.argv[i].endswith('.FITS') or \
        sys.argv[i].endswith('.fits.gz') or sys.argv[i].endswith('.FITS.GZ'):
        if os.path.isfile(sys.argv[i]):
            input_fits_files.append(sys.argv[i])
        else:
            print('%s'%('*'*80))
            print('Warning! "%s" was not found!'%(sys.argv[i]))
            print('')
    elif sys.argv[i].startswith('-'):
        if sys.argv[i].lower() == '-start':
            if i+1 <= len(sys.argv)-1:
                input_loop_start = long(sys.argv[i+1])
                i = i + 1
        elif sys.argv[i].lower() == '-end':
            if i+1 <= len(sys.argv)-1:
                input_loop_end = long(sys.argv[i+1])
                i = i + 1
        elif sys.argv[i].lower() == '-rms' or sys.argv[i].lower() == '--rms-value':
            if i+1 <= len(sys.argv)-1:
                input_rms_value = float(sys.argv[i+1])
                i = i + 1
        elif sys.argv[i].lower() == '-out' or sys.argv[i].lower() == '--output-dir':
            if i+1 <= len(sys.argv)-1:
                output_root = str(sys.argv[i+1])
                i = i + 1
        elif sys.argv[i].lower() == '-ngmax' or sys.argv[i].lower() == '--number-gaussian' or sys.argv[i].lower() == '--numb-gauss' or sys.argv[i].lower() == '--max-numb-gaussian' or sys.argv[i].lower() == '--max-numb-gauss':
            if i+1 <= len(sys.argv)-1:
                input_ini_gausfit = 'ngmax'+' '+(sys.argv[i+1])
                input_peak_fit = False
                print('Setting ini_gausfit to %s'%(input_ini_gausfit))
                i = i + 1
    else:
        if os.path.isfile(sys.argv[i]):
            with open(sys.argv[i]) as fp:
                input_list_files = fp.readlines()
                for lp in input_list_files:
                    input_fits_file = lp.strip()
                    if input_fits_file.endswith('.fits') or input_fits_file.endswith('.FITS') or \
                        input_fits_file.endswith('.fits.gz') or input_fits_file.endswith('.FITS.GZ'):
                        if lp.find('/')==0 or lp.find('~')==0 or lp.find('$')==0:
                            input_fits_file = input_fits_file
                        else:
                            input_fits_file = os.path.abspath(os.path.dirname(sys.argv[i])) + os.sep + input_fits_file
                        input_fits_files.append(input_fits_file)
                    else:
                        print('%s'%('*'*80))
                        print('Warning! "%s" is not a FITS file!'%(input_fits_file))
                        print('')
        else:
            print('%s'%('*'*80))
            print('Warning! "%s" was not found!'%(sys.argv[i]))
            print('')
    # 
    i = i + 1


# create output directory if it does not exist
if not os.path.isdir(output_root):
    os.mkdir(output_root)

output_list_of_catalog = output_root + os.sep + 'output_list_of_catalog.txt'
if os.path.isfile(output_list_of_catalog):
    os.system('mv "%s" "%s.backup"'%(output_list_of_catalog, output_list_of_catalog))

for i in range(len(input_fits_files)):
    # 
    # loop control
    if input_loop_start >=0:
        if i < input_loop_start:
            continue
    if input_loop_end >=0:
        if i > input_loop_end:
            break
    # 
    # get fits file name and prepare logging
    input_fits_file = input_fits_files[i]
    input_fits_name = os.path.basename(input_fits_file)
    if input_fits_name.endswith('.fits') or input_fits_name.endswith('.FITS'):
        input_fits_base = (input_fits_name.rsplit('.', 1))[0] # If you want to split on the last period, use rsplit -- https://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
    elif input_fits_name.endswith('.fits.gz') or input_fits_name.endswith('.FITS.GZ'):
        input_fits_base = (input_fits_name.rsplit('.', 2))[0] # If you want to split on the last period, use rsplit -- https://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
    else:
        print('%s'%('*'*80))
        print('Warning! "%s" is not a FITS image! It must have a suffix of .fits or .FITS or .fits.gz or .FITS.GZ! Skip and continue!'%(input_fits_name))
        print('')
        continue
    output_dir = output_root + os.sep + input_fits_base
    output_log = output_root + os.sep + input_fits_base + '.log'
    sys_stdout = sys.stdout
    sys.stdout = Logger(output_log)
    print('%s'%('*'*80))
    print('Processing "%s" and output to "%s".'%(input_fits_file, output_dir))
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    # 
    # process fits image
    if input_rms_value > 0.0:
        fit_result = bdsf.process_image(input_fits_file, thresh_isl = 2.0, thresh_pix = 3.5, \
                                        group_by_isl = True, \
                                        ini_gausfit = input_ini_gausfit, peak_fit = input_peak_fit, \
                                        rms_map = False, rms_value = input_rms_value, mean_map = 'zero') # <20171105> allow input rms value
    else:
        fit_result = bdsf.process_image(input_fits_file, thresh_isl = 2.0, thresh_pix = 3.5) # rms_map=False, rms_value=1e-5, 
    # 
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat0.fits', format = 'fits', clobber = True) # clobber = True means overwrite existing file. 
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat0.ds9.reg', format = 'ds9', clobber = True)
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat.fits', catalog_type = 'srl', format = 'fits', clobber = True) # 
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat.ds9.reg', catalog_type = 'srl', format = 'ds9', clobber = True)
    fit_result.export_image(outfile = output_dir + os.sep + 'pybdsm_img_gaus_resid.fits',        img_type = 'gaus_resid',       clobber = True) # Gaussian model residual image
    fit_result.export_image(outfile = output_dir + os.sep + 'pybdsm_img_rms.fits',               img_type = 'rms',              clobber = True)
    fit_result.export_image(outfile = output_dir + os.sep + 'pybdsm_img_mean.fits',              img_type = 'mean',             clobber = True)
    fit_result.export_image(outfile = output_dir + os.sep + 'pybdsm_img_gaus_model.fits',        img_type = 'gaus_model',       clobber = True) # Gaussian model image
    fit_result.export_image(outfile = output_dir + os.sep + 'pybdsm_img_island_mask.fits',       img_type = 'island_mask',      clobber = True) # Island mask image (0 = outside island, 1 = inside island)
    fit_result.export_image(outfile = output_dir + os.sep + 'pybdsm_img_ch0.fits',               img_type = 'ch0',              clobber = True) # image used for source detection
    # 
    os.system('echo "%s" >> "%s"'%(input_fits_base + os.sep + 'pybdsm_cat.fits', output_list_of_catalog))
    # 
    os.system('echo "#!/bin/bash" > "%s"'%(output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    os.system('echo "cd \\\"%s\\\"" >> "%s"'%(os.path.abspath(output_dir), output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    os.system('echo "ds9 -lock frame image -mecube pybdsm_img_*.fits -frame 2 -regions load pybdsm_cat0.ds9.reg -regions showtext no -zoom to fit -saveimage eps pybdsm_cat0.ds9.eps" >> "%s"'%(output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    os.system('chmod +x "%s"'%(output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    # 
    os.system('echo "#!/bin/bash" > "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    os.system('echo "cd \\\"%s\\\"" >> "%s"'%(os.path.abspath(output_dir), output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    os.system('echo "ds9 -lock frame image -mecube pybdsm_img_*.fits -frame 2 -regions load pybdsm_cat.ds9.reg -regions showtext no -zoom to fit -saveimage eps pybdsm_cat.ds9.eps" >> "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    os.system('chmod +x "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    # 
    print('\n')
    sys.stdout = sys_stdout
    # 
    # in default 'bdsf' will create a '*.pybdsf.log' at the input fits file directory
    os.system('mv "%s" "%s"'%(input_fits_file+'.pybdsf.log', output_log.replace('.log','.pybdsf.log')))






