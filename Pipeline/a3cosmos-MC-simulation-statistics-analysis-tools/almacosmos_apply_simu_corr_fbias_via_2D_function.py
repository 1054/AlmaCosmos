#!/usr/bin/env python2.7
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")
pkg_resources.require("scipy")

import os, sys

if len(sys.argv) <= 1:
    print('Usage: almacosmos_apply_simu_data_correction_fbias.py catalog.txt')
    sys.exit()


# 
# Read input arguments
# 
input_catalog_file = ''

i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '-cat':
        if i+1 < len(sys.argv):
            input_catalog_file = sys.argv[i+1]
            i = i + 1
    else:
        if input_catalog_file == '':
            input_catalog_file = sys.argv[i]
        elif input_simu_data_table == '':
            input_simu_data_table = sys.argv[i]
    i = i + 1


# 
# Check input data file
# 
if not os.path.isfile(input_catalog_file):
    print('Error! "%s" was not found!'%(input_catalog_file))
    sys.exit()


# 
# Import python packages
# 
import numpy
import astropy
import astropy.io.ascii as asciitable
import scipy.optimize
#import matplotlib
#from matplotlib import pyplot
from pprint import pprint
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabgaussian')
from CrabGaussian import *
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabcurvefit')
from CrabCurveFit import *


# 
# Read input catalog file
# 
if input_catalog_file.endswith('.fits'):
    catalog_struct = CrabTable(input_catalog_file)
    catalog_column_names = catalog_struct.getColumnNames()
    catalog = catalog_struct
else:
    #catalog = asciitable.read(input_catalog_file)
    catalog_struct = CrabTable(input_catalog_file)
    catalog_column_names = catalog_struct.getColumnNames()
    catalog = catalog_struct


# 
# Read data
# 
#---------------# S_out will be updated after this code
col_S_out = ''
mal_S_out = 1.0 # multiplification factor
if 'S_out' in catalog_column_names:
    col_S_out = 'S_out'
    mal_S_out = 1.0
elif 'Total_flux' in catalog_column_names:
    col_S_out = 'Total_flux'
    mal_S_out = 1e3
else:
    print('Error! Could not find "S_out" column!')
    sys.exit()
data_S_out = catalog.getColumn(col_S_out) * mal_S_out # convert to mJy
#---------------# e_S_out will not be updated because this code only deals with fbias
col_e_S_out = ''
mal_e_S_out = 1.0 # multiplification factor
if 'e_S_out' in catalog_column_names:
    col_e_S_out = 'e_S_out'
    mal_e_S_out = 1.0
elif 'E_Total_flux' in catalog_column_names:
    col_e_S_out = 'E_Total_flux'
    mal_e_S_out = 1e3
else:
    print('Error! Could not find "e_S_out" column!')
    sys.exit()
data_e_S_out = catalog.getColumn(col_e_S_out) * mal_e_S_out # convert to mJy
#---------------
if 'S_peak' in catalog_column_names:
    data_S_peak = catalog.getColumn('S_peak')
elif 'Peak_flux' in catalog_column_names:
    data_S_peak = catalog.getColumn('Peak_flux') * 1e3 # convert to mJy
else:
    print('Error! Could not find "S_peak" column!')
    sys.exit()
#---------------
if 'noise' in catalog_column_names:
    data_noise = catalog.getColumn('noise') # mJy
elif 'rms' in catalog_column_names:
    data_noise = catalog.getColumn('rms') # mJy
else:
    print('Error! Could not find "noise" column!')
    sys.exit()
#---------------
if 'Maj_out' in catalog_column_names and \
   'Min_out' in catalog_column_names and \
   'PA_out' in catalog_column_names and \
   'Maj_beam' in catalog_column_names and \
   'Min_beam' in catalog_column_names and \
   'PA_beam' in catalog_column_names:
    data_Maj_out = catalog.getColumn('Maj_out') # assuming arcsec
    data_Min_out = catalog.getColumn('Min_out') # assuming arcsec
    data_PA_out = catalog.getColumn('PA_out') 
    data_Maj_beam = catalog.getColumn('Maj_beam') # assuming arcsec
    data_Min_beam = catalog.getColumn('Min_beam') # assuming arcsec
    data_PA_beam = catalog.getColumn('PA_beam') 
    print('Computing source sizes convolved with beam')
    data_Maj_out_convol, data_Min_out_convol, data_PA_out_convol = convolve_2D_Gaussian_Maj_Min_PA(data_Maj_out, data_Min_out, data_PA_out, data_Maj_beam, data_Min_beam, data_PA_beam)
elif 'Maj_deconv' in catalog_column_names and \
     'Min_deconv' in catalog_column_names and \
     'PA_deconv' in catalog_column_names and \
     'beam_maj' in catalog_column_names and \
     'beam_min' in catalog_column_names and \
     'beam_PA' in catalog_column_names:
    data_Maj_out = catalog.getColumn('Maj_deconv') * 3600.0 # convert to arcsec
    data_Min_out = catalog.getColumn('Min_deconv') * 3600.0 # convert to arcsec
    data_PA_out = catalog.getColumn('PA_deconv')
    data_Maj_beam = catalog.getColumn('beam_maj') # assuming arcsec
    data_Min_beam = catalog.getColumn('beam_min') # assuming arcsec
    data_PA_beam = catalog.getColumn('beam_PA')
    print('Computing source sizes convolved with beam')
    data_Maj_out_convol, data_Min_out_convol, data_PA_out_convol = convolve_2D_Gaussian_Maj_Min_PA(data_Maj_out, data_Min_out, data_PA_out, data_Maj_beam, data_Min_beam, data_PA_beam)
elif 'Maj_deconv' in catalog_column_names and \
     'Min_deconv' in catalog_column_names and \
     'PA_deconv' in catalog_column_names and \
     'Beam_MAJ' in catalog_column_names and \
     'Beam_MIN' in catalog_column_names and \
     'Beam_PA' in catalog_column_names:
    data_Maj_out = catalog.getColumn('Maj_deconv') * 3600.0 # assuming degree, converting to arcsec
    data_Min_out = catalog.getColumn('Min_deconv') * 3600.0 # assuming degree, converting to arcsec
    data_PA_out = catalog.getColumn('PA_deconv')
    data_Maj_beam = catalog.getColumn('Beam_MAJ') * 3600.0 # assuming degree, converting to arcsec
    data_Min_beam = catalog.getColumn('Beam_MIN') * 3600.0 # assuming degree, converting to arcsec
    data_PA_beam = catalog.getColumn('Beam_PA')
    print('Computing source sizes convolved with beam')
    data_Maj_out_convol, data_Min_out_convol, data_PA_out_convol = convolve_2D_Gaussian_Maj_Min_PA(data_Maj_out, data_Min_out, data_PA_out, data_Maj_beam, data_Min_beam, data_PA_beam)
else:
    print('Error! Could not compute "Maj_out_convol" data!')
    sys.exit()
#---------------
#col_Maj_beam = ''
#mal_Maj_beam = 1.0 # multiplification factor
if 'Maj_beam' in catalog_column_names:
    data_Maj_beam = catalog.getColumn('Maj_beam') # assuming arcsec
elif 'beam_maj' in catalog_column_names:
    data_Maj_beam = catalog.getColumn('beam_maj') # assuming arcsec
elif 'Beam_MAJ' in catalog_column_names:
    data_Maj_beam = catalog.getColumn('Beam_MAJ') * 3600.0 # assuming degree, converting to arcsec
else:
    print('Error! Could not find "Maj_beam" column!')
    sys.exit()


# 
# prepare x1, x2
# 
x1 = data_S_peak/data_noise
x2 = data_Maj_out_convol/data_Maj_beam
x = numpy.column_stack((numpy.log10(x1),x2))


# 
# read best_fit_function
# 
if not os.path.isfile('best_fit_function_fbias.py'):
    print('Error! "best_fit_function_fbias.py" was not found! Please first run "almacosmos_fit_simu_corr_fbias_via_2D_function.py"!')
    sys.exit()

from best_fit_function_fbias import best_fit_function_fbias


# 
# apply 2D function
# 
fbias_from_function = best_fit_function_fbias(x1, x2)
print(fbias_from_function)




# 
# save file
# 
asciitable.write(numpy.column_stack((fbias_from_function, x1, x2)), 
                    'datatable_applying_correction_fbias.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                    names=['fbias_from_function','x1','x2'], overwrite=True)
os.system('sed -i.bak -e "1s/^ /#/" "datatable_applying_correction_fbias.txt"')

print('Output to "datatable_applying_correction_fbias.txt"!')





# 
# final corrected fbias
# 
S_out_uncorr = data_S_out
S_out_corr = S_out_uncorr
fbias_valid_mask = (fbias_from_function==fbias_from_function)
S_out_corr[fbias_valid_mask] = S_out_uncorr[fbias_valid_mask] / (1.0 - fbias_from_function[fbias_valid_mask])

asciitable.write(numpy.column_stack((S_out_corr, S_out_uncorr, x1, x2)), 
                    'datatable_applied_correction_fbias.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                    names=['S_out_corr','S_out_uncorr','x1','x2'], overwrite=True)
os.system('sed -i.bak -e "1s/^ /#/" "datatable_applied_correction_fbias.txt"')

print('Output to "datatable_applied_correction_fbias.txt"!')





# 
# output corrected 'input_catalog_file'
# 
input_catalog_file_name, input_catalog_file_ext = os.path.splitext(input_catalog_file)

catalog.TableData[col_S_out] = S_out_corr / mal_S_out

if input_catalog_file_ext == '.fits':
    catalog.saveAs(input_catalog_file_name+'_corrected.fits')
else :
    asciitable.write(catalog.TableData, input_catalog_file_name+'_corrected.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                        names=catalog_column_names, overwrite=True)
    os.system('sed -i.bak -e "1s/^ /#/" "%s"'%(input_catalog_file_name+'_corrected.txt'))
    print('Output to "%s"!'%(input_catalog_file_name+'_corrected.txt'))



















