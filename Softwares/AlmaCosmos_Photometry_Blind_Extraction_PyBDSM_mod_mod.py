#!/usr/bin/env python2.7
# 
# Aim: run the PyBDSM tool () to extract sources from FITS format images. 
# 
# Last update: 2017-11-08
#              2017-12-07 updated mac pybdsf to 1.8.13, no major updates in this version. 
#              2018-01-21 updated linux pybdsf (modified version) to 1.8.13. 
#              2018-03-28 added option "thresh = 'hard'" to let PyBDSM always use sigma-clipping instead of its "FDR"
# 

import os, sys, re
import logging

import platform
if platform.system() == 'Darwin':
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages')
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages'+os.sep+'bdsf-1.8.13-py2.7-macosx-10.12-x86_64.mod.by.dzliu.egg')
    print(sys.path)
    # -- 
    # -- https://github.com/nteract/nteract/issues/1523
    # -- New versions of OS X enable system integrity protection per default. Meaning that setting the DYLD_LIBRARY_PATH and LD_LIBRARY_PATH will have no effects. 
    # -- 
    # if 'DYLD_LIBRARY_PATH' not in os.environ:
    #     os.environ['DYLD_LIBRARY_PATH'] = os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'
    #     os.environ['PATH'] = os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'bin' + ':' + os.environ['PATH']
    #     #print(os.environ['DYLD_LIBRARY_PATH'])
    #     #os.system('echo $DYLD_LIBRARY_PATH')
    #     #print(sys.argv[0])
    #     try:
    #         print('/usr/bin/env PATH="%s" DYLD_LIBRARY_PATH="%s" python2.7 %s'%(os.environ['PATH'], os.environ['DYLD_LIBRARY_PATH'], sys.argv[0]))
    #         #os.execv('/usr/bin/env DYLD_LIBRARY_PATH="%s" python2.7 %s'%(os.environ['DYLD_LIBRARY_PATH'], sys.argv[0]), sys.argv)
    #         os.execv('/usr/bin/env', ['-v', 'PATH="%s"'%(os.environ['PATH']), 'DYLD_LIBRARY_PATH="%s"'%(os.environ['DYLD_LIBRARY_PATH']), 'python2.7'] + sys.argv)
    #     except Exception, exc:
    #         print 'Failed re-exec:', exc
    #         sys.exit(1)
    # #print('Success:', os.environ['DYLD_LIBRARY_PATH'])
    # #os.system('echo $DYLD_LIBRARY_PATH')
    # # 
    # from ctypes import *
    # #CDLL('libboost_python-mt.dylib')
    # #CDLL('libboost_python.dylib')
    # print('DYLD_LIBRARY_PATH:',             os.getenv('DYLD_LIBRARY_PATH'))
    # print('DYLD_FALLBACK_LIBRARY_PATH:',    os.getenv('DYLD_FALLBACK_LIBRARY_PATH'))
    # print('DYLD_FRAMEWORK_PATH:',           os.getenv('DYLD_FRAMEWORK_PATH'))
    # print('DYLD_FALLBACK_FRAMEWORK_PATH:',  os.getenv('DYLD_FALLBACK_FRAMEWORK_PATH'))
    # print('DYLD_IMAGE_SUFFIX:',             os.getenv('DYLD_IMAGE_SUFFIX'))
    # print('PATH:',                          os.getenv('PATH'))
    # import ctypes.util
    # print(ctypes.util.find_library("libboost_python-mt"))
    # print(CDLL(ctypes.util.find_library("libboost_python-mt")))
    # print(CDLL(os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'+os.sep+"libboost_python.dylib"))
    # print(CDLL(os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'+os.sep+"libboost_python-mt.dylib"))
    # 
    # DONE! WORKED!
    from ctypes import *
    CDLL(os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages'+os.sep+'bdsf-1.8.13-py2.7-macosx-10.12-x86_64.egg'+os.sep+'bdsf'+os.sep+'_pytesselate.so')
    CDLL(os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'mac_python2.7'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages'+os.sep+'bdsf-1.8.13-py2.7-macosx-10.12-x86_64.egg'+os.sep+'bdsf'+os.sep+'_cbdsm.so')
    # 
else:
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'linux_python2.7'+os.sep+'lib'+os.sep+'python2.7'+os.sep+'site-packages')
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'linux_python2.7'+os.sep+'lib64'+os.sep+'python2.7'+os.sep+'site-packages')
    sys.path.insert(1,os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+'3rd_pybdsf'+os.sep+'linux_python2.7'+os.sep+'lib64'+os.sep+'python2.7'+os.sep+'site-packages'+os.sep+'bdsf-1.8.13-py2.7-linux-x86_64.mod.by.dzliu.egg')
    print(sys.path)



#print('echo $DYLD_LIBRARY_PATH')
#os.system('echo $DYLD_LIBRARY_PATH')

import numpy
import scipy
import bdsf_mod_by_dzliu
from bdsf_mod_by_dzliu import process_image


# 
# print usage if no input argument
# 
if len(sys.argv) <= 1:
    print('Usage: ')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Images.fits"                              # providing a FITS image')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Images.fits" "ALMA_Image_List.txt"        # or providing text file which contains a list of FITS images')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" --rms-value 0.00015       # we can also input a constant rms value for all input FITS images')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -rms 0.00015              # (same as above)')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" --max-gaussian-number 1   # we can also constrain the maximum number of fitted Gaussian to one Island')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -ngmax 1                  # (same as above)')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" --max-gaussian-area 1     # we can also set the maximum area of a Gaussian in unit of beam area, above which the Gaussian will be flagged/discarded.')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -agmax 1                  # (same as above)')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" --include-empty-islands   # we can also specify that we want to output empty islands which do not contain any valid Gaussian and have negative Source_id.')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -incl-empty               # (same as above)')
    print('    ')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -thresh_pix               # (new parameter to tune, default 3.0)')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -thresh_rms               # (new parameter to tune, default 4.0)')
    print('    ')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -start 1 -end 100         # (input a list of fits files then process only a range of them)')
    print('    AlmaCosmos_Photometry_Blind_Extraction_PyBDSM.py "ALMA_Image_List.txt" -start 101 -end 200       # (input a list of fits files then process only a range of them)')
    print('    ')
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
input_rms_image = '' #<TODO><20180910><dzliu># can we input an rms fits image? currently PyBDSM does not support this.
input_rms_value = -99
input_ini_gausfit = 'default'
input_peak_fit = True # whether to find and fit peaks of large islands before fitting entire island
input_verbose_fitting = False
input_incl_empty = False
input_flag_maxsize_bm = 25.0 # flag (discard) a Gaussian if its area is larger than 25.0 times the beam area. <20171109><NOTE><DZLIU> THIS IS NOT GAUSSIAN_SIZE/BEAM_SIZE BUT GAUSSIAN_AREA/BEAM_AREA!!!
input_flag_maxsize_fwhm = 0.5 # flag (discard) a Gaussian if ... -- see -- http://www.astron.nl/citt/pybdsm/process_image.html#flagging-options
                              # DOCUMENTATION IS WRONG! THE DEFAULT VALUE IS 0.5.
input_thresh_rms = 3.0
input_thresh_pix = 4.0
input_group_by_isl = True
output_root = 'Output_Blind_Extraction_Photometry_PyBDSM'

overwrite = False

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
        # strip input arg str
        temp_arg_str = sys.argv[i].lower().replace('--','-').replace('_','-')
        # check input arg str
        if temp_arg_str == '-start':
            if i+1 <= len(sys.argv)-1:
                input_loop_start = long(sys.argv[i+1])
                i = i + 1
        elif temp_arg_str == '-end':
            if i+1 <= len(sys.argv)-1:
                input_loop_end = long(sys.argv[i+1])
                i = i + 1
        elif temp_arg_str == '-rms' or temp_arg_str == '-rms-value':
            if i+1 <= len(sys.argv)-1:
                input_rms_value = float(sys.argv[i+1])
                i = i + 1
        elif temp_arg_str == '-rms-map' or temp_arg_str == '-rms-image':
            if i+1 <= len(sys.argv)-1:
                input_rms_image = sys.argv[i+1] #<TODO><20180910><dzliu># can we input an rms fits image? currently PyBDSM does not support this.
                i = i + 1
        elif temp_arg_str == '-out' or temp_arg_str == '-output-dir':
            if i+1 <= len(sys.argv)-1:
                output_root = str(sys.argv[i+1])
                i = i + 1
        elif temp_arg_str == '-max-gaussian-number' or \
            temp_arg_str == '-ngmax' or \
            temp_arg_str == '-number-gaussian' or \
            temp_arg_str == '-numb-gauss' or \
            temp_arg_str == '-max-numb-gaussian' or \
            temp_arg_str == '-max-numb-gauss' or \
            temp_arg_str == '-max-gaussian-numb':
            if i+1 <= len(sys.argv)-1:
                input_ini_gausfit = 'ngmax'+' '+(sys.argv[i+1])
                input_peak_fit = False
                print('Setting ini_gausfit to %s'%(input_ini_gausfit))
                i = i + 1
        elif temp_arg_str == '-max-gaussian-area' or \
            temp_arg_str == '-agmax' or \
            temp_arg_str == '-maxarea' or \
            temp_arg_str == '-maxsize' or \
            temp_arg_str == '-flag-maxsize' or \
            temp_arg_str == '-flag-maxsize-bm':
            if i+1 <= len(sys.argv)-1:
                input_flag_maxsize_bm = float(sys.argv[i+1])
                print('Setting flag_maxsize_bm to %s'%(input_flag_maxsize_bm))
                i = i + 1
        elif temp_arg_str == '-igmin' or \
            temp_arg_str == '-flag-maxsize-fwhm':
            if i+1 <= len(sys.argv)-1:
                input_flag_maxsize_fwhm = float(sys.argv[i+1])
                print('Setting flag_maxsize_fwhm to %s'%(input_flag_maxsize_fwhm))
                i = i + 1
        elif temp_arg_str == '-thresh-pix' or \
            temp_arg_str == '-threshold-pixel' or \
            temp_arg_str == '-threshold-pixels':
            if i+1 <= len(sys.argv)-1:
                input_thresh_pix = float(sys.argv[i+1])
                print('Setting thresh_pix to %s'%(input_thresh_pix))
                i = i + 1
        elif temp_arg_str == '-thresh-rms' or \
            temp_arg_str == '-threshold-rms' or \
            temp_arg_str == '-threshold-detection':
            if i+1 <= len(sys.argv)-1:
                input_thresh_rms = float(sys.argv[i+1])
                print('Setting thresh_rms to %s'%(input_thresh_rms))
                i = i + 1
        elif temp_arg_str == '-verbose' or \
            temp_arg_str == '-verbose-fitting':
            input_verbose_fitting = True
            print('Setting verbose_fitting to %s'%(input_verbose_fitting))
        elif temp_arg_str == '-incl-empty' or \
            temp_arg_str == '-include-empty-island' or \
            temp_arg_str == '-include-empty-islands':
            input_incl_empty = True
            print('Setting incl_empty to %s'%(input_incl_empty))
        elif temp_arg_str == '-group-by-isl' or \
            temp_arg_str == '-group-by-islands':
            input_group_by_isl = True
            print('Setting group_by_isl to %s'%(input_group_by_isl))
        elif temp_arg_str == '-group-by-gauss' or \
            temp_arg_str == '-group-by-gaussian':
            input_group_by_isl = False
            print('Setting group_by_isl to %s'%(input_group_by_isl))
        elif temp_arg_str == '-overwrite':
            overwrite = True
            print('Setting overwrite to %s'%(overwrite))
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
    os.makedirs(output_root)

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
    # 
    # check overwriting (20180910)
    if os.path.isfile(output_log) and not overwrite:
        print('%s'%('*'*80))
        print('Warning! Found existing log file "%s"! Will not overwrite unless the option "-overwrite" is given!'%(output_log))
        print('')
        continue
    # 
    # prepare logger
    sys_stdout = sys.stdout
    sys.stdout = Logger(output_log)
    print('%s'%('*'*80))
    print('Processing "%s" and output to "%s".'%(input_fits_file, output_dir))
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    # 
    # process fits image
    if input_rms_value > 0.0:
        # fix input rms value
        fit_result = process_image(input_fits_file, thresh = 'hard', thresh_isl = input_thresh_rms, thresh_pix = input_thresh_pix, \
                                        group_by_isl = input_group_by_isl, \
                                        ini_gausfit = input_ini_gausfit, peak_fit = input_peak_fit, \
                                        rms_map = False, rms_value = input_rms_value, mean_map = 'zero', \
                                        flag_maxsize_bm = input_flag_maxsize_bm, \
                                        flag_maxsize_fwhm = input_flag_maxsize_fwhm, \
                                        verbose_fitting = input_verbose_fitting) # <20171105> allow input rms value
    else:
        # let PyBDSM to determine rms value, which might be not uniform.
        fit_result = process_image(input_fits_file, thresh = 'hard', thresh_isl = input_thresh_rms, thresh_pix = input_thresh_pix, \
                                        group_by_isl = input_group_by_isl, \
                                        ini_gausfit = input_ini_gausfit, peak_fit = input_peak_fit, \
                                        mean_map = 'zero', \
                                        flag_maxsize_bm = input_flag_maxsize_bm, \
                                        flag_maxsize_fwhm = input_flag_maxsize_fwhm, \
                                        verbose_fitting = input_verbose_fitting) # rms_map=False, rms_value=1e-5, 
    # 
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat0.fits', format = 'fits', clobber = True) # clobber = True means overwrite existing file. 
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat0.ds9.reg', format = 'ds9', clobber = True)
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat.fits', catalog_type = 'srl', incl_empty = input_incl_empty, format = 'fits', clobber = True) # 
    fit_result.write_catalog(outfile = output_dir + os.sep + 'pybdsm_cat.ds9.reg', catalog_type = 'srl', incl_empty = input_incl_empty, format = 'ds9', clobber = True)
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
    os.system('echo "cd \\$(dirname \\\"\\${BASH_SOURCE[0]}\\\")" >> "%s"'%(output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    os.system('echo "ds9 -lock frame image -mecube pybdsm_img_*.fits -frame 2 -regions load pybdsm_cat0.ds9.reg -regions showtext no -zoom to fit -saveimage eps pybdsm_cat0.ds9.eps" >> "%s"'%(output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    os.system('chmod +x "%s"'%(output_dir + os.sep + 'pybdsm_cat0.ds9.sh'))
    # 
    os.system('echo "#!/bin/bash" > "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    os.system('echo "cd \\$(dirname \\\"\\${BASH_SOURCE[0]}\\\")" >> "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    os.system('echo "ds9 -lock frame image -mecube pybdsm_img_*.fits -frame 2 -regions load pybdsm_cat.ds9.reg -regions showtext no -zoom to fit -saveimage eps pybdsm_cat.ds9.eps" >> "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    os.system('chmod +x "%s"'%(output_dir + os.sep + 'pybdsm_cat.ds9.sh'))
    # 
    print('\n')
    sys.stdout = sys_stdout
    # 
    # in default 'bdsf' will create a '*.pybdsf.log' at the input fits file directory
    if os.access(os.path.dirname(input_fits_file), os.W_OK):
        os.system('mv "%s" "%s"'%(input_fits_file+'.pybdsf.log', output_log.replace('.log','.pybdsf.log')))
    else:
        logfilepath2 = input_fits_file
        os.system('mv "%s" "%s"'%(logfilepath2.replace(os.sep,'.')+'.pybdsf.log', output_log.replace('.log','.pybdsf.log')))






