#!/usr/bin/env python2.7
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")
pkg_resources.require("scipy")

import os, sys, json

if len(sys.argv) <= 1:
    print('Usage: almacosmos_apply_simu_data_correction_ecorr.py catalog.txt')
    sys.exit()


# 
# Read input arguments
# 
input_catalog_file = ''
apply_by_method = 'interpolation'

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
import matplotlib
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
#---------------# e_S_out will also be updated
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
elif 'RMS' in catalog_column_names:
    data_noise = catalog.getColumn('RMS') # mJy
elif 'Isl_rms' in catalog_column_names:
    data_noise = catalog.getColumn('Isl_rms') * 1e3 # convert to mJy
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
col_Maj_beam = ''
mal_Maj_beam = 1.0 # multiplification factor
if 'Maj_beam' in catalog_column_names:
    data_Maj_beam = catalog.getColumn('Maj_beam')
elif 'beam_maj' in catalog_column_names:
    data_Maj_beam = catalog.getColumn('beam_maj')
elif 'Beam_MAJ' in catalog_column_names:
    data_Maj_beam = catalog.getColumn('Beam_MAJ') * 3600.0 # convert to arcsec
else:
    print('Error! Could not find "Maj_beam" column!')
    sys.exit()


# 
# prepare x1, x2
# 
x1 = data_S_peak/data_noise
x2 = data_Maj_out_convol/data_Maj_beam



# 
# read base_interp_array_for_ecorr
with open('base_interp_array_for_ecorr.json', 'r') as fp:
    base_interp = json.load(fp)



# 
# constrain data range
param_x1 = [t[0] for t in base_interp['x']]
param_x2 = [t[1] for t in base_interp['x']]
param_min_x1 = numpy.min(param_x1)
param_max_x1 = numpy.max(param_x1)
param_min_x2 = numpy.min(param_x2)
param_max_x2 = numpy.max(param_x2)
data_mask = (~numpy.isfinite(x1)) | (~numpy.isfinite(x2))
x1[data_mask] = param_min_x1
x2[data_mask] = param_min_x2
data_min_x1 = numpy.min(x1)
data_max_x1 = numpy.max(x1)
data_min_x2 = numpy.min(x2)
data_max_x2 = numpy.max(x2)
print('param_min_x1 = %s'%(param_min_x1))
print('param_min_x2 = %s'%(param_min_x2))
print('data_min_x1 = %s'%(data_min_x1))
print('data_min_x2 = %s'%(data_min_x2))
print('param_max_x1 = %s'%(param_max_x1))
print('param_max_x2 = %s'%(param_max_x2))
print('data_max_x1 = %s'%(data_max_x1))
print('data_max_x2 = %s'%(data_max_x2))
x2mask = (x2<param_min_x2)
x2[x2mask] = param_min_x2
x2mask = (x2>param_max_x2)
x2[x2mask] = param_max_x2



# 
# column_stack x1 x2
x = numpy.column_stack((numpy.log10(x1),x2))



# 
# 2D interpolation
from scipy import interpolate

ecorr_array_extrapolated = interpolate.griddata(numpy.array(base_interp['x']), numpy.array(base_interp['ecorr']), x, method='nearest')
ecorr_array_interpolated = interpolate.griddata(numpy.array(base_interp['x']), numpy.array(base_interp['ecorr']), x, method='linear')
ecorr_array_mask = numpy.isnan(ecorr_array_interpolated)
ecorr_array = ecorr_array_interpolated
ecorr_array[ecorr_array_mask] = ecorr_array_extrapolated[ecorr_array_mask]
ecorr_array[data_mask] = numpy.nan
#pprint(x1_grid)
#pprint(x2_grid)
#pprint(ecorr_grid)

ecorr_array_extrapolated = ecorr_array_extrapolated # numpy.power(10,ecorr_array_extrapolated)
ecorr_array_interpolated = ecorr_array_interpolated # numpy.power(10,ecorr_array_interpolated)
ecorr_array = ecorr_array # numpy.power(10,ecorr_array)

asciitable.write(numpy.column_stack((x2, x1, ecorr_array_extrapolated, ecorr_array_interpolated, ecorr_array)), 
                    'datatable_applying_correction_ecorr_by_interpolation.txt', Writer=asciitable.FixedWidth, delimiter=" ", 
                    names=['x2', 'x1', 'ecorr_array_extrapolated', 'ecorr_array_interpolated', 'ecorr_array'], overwrite=True)

print('Output to "datatable_applying_correction_ecorr_by_interpolation.txt"!')







# 
# combined ecorr
# 

ecorr_from_interpolation = ecorr_array

asciitable.write(numpy.column_stack((ecorr_from_interpolation, x2, x1)), 
                    'datatable_applying_correction_ecorr.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                    names=['ecorr_from_interpolation','x2','x1'], overwrite=True)
os.system('sed -i.bak -e "1s/^ /#/" "datatable_applying_correction_ecorr.txt"')

print('Output to "datatable_applying_correction_ecorr.txt"!')







# 
# final corrected ecorr
# 

e_S_out_uncorr = data_e_S_out
e_S_out_corr = data_noise * ecorr_from_interpolation

asciitable.write(numpy.column_stack((e_S_out_corr, e_S_out_uncorr, ecorr_from_interpolation, x2, x1)), 
                    'datatable_applied_correction_ecorr.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                    names=['e_S_out_corr','e_S_out_uncorr','ecorr_from_interpolation','x2','x1'], overwrite=True)
os.system('sed -i.bak -e "1s/^ /#/" "datatable_applied_correction_ecorr.txt"')

print('Output to "datatable_applied_correction_ecorr.txt"!')





# 
# output corrected 'input_catalog_file'
# 
input_catalog_file_name, input_catalog_file_ext = os.path.splitext(input_catalog_file)

catalog.TableData[col_e_S_out] = e_S_out_corr / mal_e_S_out

catalog.saveAs(input_catalog_file_name+'_corrected'+input_catalog_file_ext, overwrite=True)

#asciitable.write(catalog.TableData, input_catalog_file_name+'_corrected.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
#                    names=catalog_column_names, overwrite=True)
#os.system('sed -i.bak -e "1s/^ /#/" "%s"'%(input_catalog_file_name+'_corrected.txt'))
#
#print('Output to "%s"!'%(input_catalog_file_name+'_corrected.txt'))
print('Output to "%s"!'%(input_catalog_file_name+'_corrected'+input_catalog_file_ext))



















