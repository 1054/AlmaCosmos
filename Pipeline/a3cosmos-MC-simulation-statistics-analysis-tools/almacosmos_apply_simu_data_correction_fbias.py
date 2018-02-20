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
apply_by_method = 'interpolation'

i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '-cat':
        if i+1 < len(sys.argv):
            input_catalog_file = sys.argv[i+1]
            i = i + 1
    elif sys.argv[i].lower() == '-by-function':
        apply_by_method = 'function'
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
elif 'RMS' in catalog_column_names:
    data_noise = catalog.getColumn('RMS') * 1e3 # convert to mJy
elif 'Isl_rms' in catalog_column_names:
    data_noise = catalog.getColumn('Isl_rms') * 1e3 # convert to mJy
else:
    print('Error! Could not find "noise" column!')
    sys.exit()
#---------------
if 'Maj_out' in catalog_column_names:
    data_Maj_out = catalog.getColumn('Maj_out')
elif 'Maj_deconv' in catalog_column_names and 'beam_maj' in catalog_column_names and 'beam_min' in catalog_column_names and 'beam_PA' in catalog_column_names:
    data_Maj_deconv = catalog.getColumn('Maj_deconv') * 3600.0 # convert to arcsec
    data_Maj_beam = catalog.getColumn('beam_maj')
    data_Min_beam = catalog.getColumn('beam_min')
    data_PA_beam = catalog.getColumn('beam_PA')
    data_Maj_out = numpy.sqrt(numpy.power(data_Maj_deconv,2) + numpy.power(data_Maj_beam,2)) #<TODO># do the source size convolution
elif 'Maj_deconv' in catalog_column_names and 'Beam_MAJ' in catalog_column_names and 'Beam_MIN' in catalog_column_names and 'Beam_PA' in catalog_column_names:
    data_Maj_deconv = catalog.getColumn('Maj_deconv') * 3600.0 # convert to arcsec
    data_Maj_beam = catalog.getColumn('Beam_MAJ') * 3600.0 # convert to arcsec
    data_Min_beam = catalog.getColumn('Beam_MIN') * 3600.0 # convert to arcsec
    data_PA_beam = catalog.getColumn('Beam_PA')
    data_Maj_out = numpy.sqrt(numpy.power(data_Maj_deconv,2) + numpy.power(data_Maj_beam,2)) #<TODO># do the source size convolution
else:
    print('Error! Could not find "Maj_out" column!')
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
x2 = data_Maj_out/data_Maj_beam


# 
# read best_fit_function
import json
with open('best_fit_function_fbias.json', 'r') as fp:
    best_func = json.load(fp)


# 
# read best_fit_function
with open('base_interp_array_for_fbias.json', 'r') as fp:
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

fbias_array_extrapolated = interpolate.griddata(numpy.array(base_interp['x']), numpy.array(base_interp['fbias']), x, method='nearest')
fbias_array_interpolated = interpolate.griddata(numpy.array(base_interp['x']), numpy.array(base_interp['fbias']), x, method='linear')
fbias_array_mask = numpy.isnan(fbias_array_interpolated)
fbias_array = fbias_array_interpolated
fbias_array[fbias_array_mask] = fbias_array_extrapolated[fbias_array_mask]
fbias_array[data_mask] = numpy.nan
#pprint(x1_grid)
#pprint(x2_grid)
#pprint(fbias_grid)

asciitable.write(numpy.column_stack((x2, x1, fbias_array_extrapolated, fbias_array_interpolated, fbias_array)), 
                    'datatable_applying_correction_fbias_by_interpolation.txt', Writer=asciitable.FixedWidth, delimiter=" ", 
                    names=['x2', 'x1', 'fbias_array_extrapolated', 'fbias_array_interpolated', 'fbias_array'], overwrite=True)

print('Output to "datatable_applying_correction_fbias_by_interpolation.txt"!')


# 
# or apply best fit functions. these functions are separated by x2 values. 
print('--------- best_func ---------')
for i in range(len(best_func)):
    print(best_func[i]['x2'], best_func[i]['p_fit']['popt'])
    # best_func[i]['x2'] MUST BE MONOCHROMATICALLY INCREASING!

func_i_lo = numpy.array([-1]*len(x2))
func_i_hi = numpy.array([len(best_func)]*len(x2))
print(len(func_i_lo))
print(len(func_i_hi))
for i in range(len(best_func)):
    # 
    # find the nearby lower and upper x2 from best_func['x2']
    temp_diff = (x2 - best_func[i]['x2'])
    temp_mask = (temp_diff >= 0)
    temp_argwhere = numpy.argwhere(temp_mask)
    #print('--------- %d ---------'%(i))
    #print(best_func[i]['x2'])
    #print(len(temp_argwhere))
    if len(temp_argwhere) > 0:
        func_i_lo[temp_mask] = func_i_lo[temp_mask]+1
    # 
    temp_diff = (best_func[i]['x2'] - x2)
    temp_mask = (temp_diff >= 0)
    temp_argwhere = numpy.argwhere(temp_mask)
    if len(temp_argwhere) > 0:
        func_i_hi[temp_mask] = func_i_hi[temp_mask]-1


temp_mask = (func_i_lo < 0)
temp_argwhere = numpy.argwhere(temp_mask)
if len(temp_argwhere) > 0:
    func_i_lo[temp_mask] = 0

temp_mask = (func_i_hi > len(best_func)-1)
temp_argwhere = numpy.argwhere(temp_mask)
if len(temp_argwhere) > 0:
    func_i_hi[temp_mask] = len(best_func)-1

func_y_lo = []
func_y_hi = []
func_a_lo = []
func_a_hi = []
for i in range(len(x2)):
    func_y = fit_func_gravity_energy_field_func(x1[i], *(best_func[func_i_lo[i]]['p_fit']['popt']))
    func_y_lo.append(func_y)
    func_y = fit_func_gravity_energy_field_func(x1[i], *(best_func[func_i_hi[i]]['p_fit']['popt']))
    func_y_hi.append(func_y)
    # 
    if (best_func[func_i_hi[i]]['x2'] - best_func[func_i_lo[i]]['x2']) > 0:
        func_a_lo.append((best_func[func_i_hi[i]]['x2'] - x2[i]) / (best_func[func_i_hi[i]]['x2'] - best_func[func_i_lo[i]]['x2']))
        func_a_hi.append((x2[i] - best_func[func_i_lo[i]]['x2']) / (best_func[func_i_hi[i]]['x2'] - best_func[func_i_lo[i]]['x2']))
    else:
        func_a_lo.append(0.5)
        func_a_hi.append(0.5)

func_y_array = numpy.array(func_a_lo) * numpy.array(func_y_lo) + numpy.array(func_a_hi) * numpy.array(func_y_hi) # do an interpolation for the functions which are calibrated at each x2 (Maj_source_convol/Maj_beam) parameter grid.

asciitable.write(numpy.column_stack((func_i_lo, func_i_hi, x2, x1, func_y_lo, func_y_hi, func_a_lo, func_a_hi, func_y_array)), 
                    'datatable_applying_correction_fbias_by_function.txt', Writer=asciitable.FixedWidth, delimiter=" ", 
                    names=['func_i_lo','func_i_hi','x2','x1','func_y_lo','func_y_hi','func_a_lo','func_a_hi', 'func_y_array'], overwrite=True)

print('Output to "datatable_applying_correction_fbias_by_function.txt"!')





# 
# combined fbias
# 

fbias_from_interpolation = fbias_array
fbias_from_function = func_y_array

asciitable.write(numpy.column_stack((fbias_from_function, fbias_from_interpolation, x2, x1)), 
                    'datatable_applying_correction_fbias.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                    names=['fbias_from_function','fbias_from_interpolation','x2','x1'], overwrite=True)
os.system('sed -i.bak -e "1s/^ /#/" "datatable_applying_correction_fbias.txt"')

print('Output to "datatable_applying_correction_fbias.txt"!')



# choose which method to use
if apply_by_method == 'function':
    fbias_used = fbias_from_function
else:
    fbias_used = fbias_from_interpolation





# 
# final corrected fbias
# 

S_out_uncorr = data_S_out
S_out_corr = S_out_uncorr / (1.0 - fbias_used) # (1.0 - fbias_from_function)

asciitable.write(numpy.column_stack((S_out_corr, S_out_uncorr, fbias_used, x2, x1)), 
                    'datatable_applied_correction_fbias.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
                    names=['S_out_corr','S_out_uncorr','fbias_used','x2','x1'], overwrite=True)
os.system('sed -i.bak -e "1s/^ /#/" "datatable_applied_correction_fbias.txt"')

print('Output to "datatable_applied_correction_fbias.txt"!')





# 
# output corrected 'input_catalog_file'
# 
input_catalog_file_name, input_catalog_file_ext = os.path.splitext(input_catalog_file)

catalog.TableData[col_S_out] = S_out_corr / mal_S_out

catalog.saveAs(input_catalog_file_name+'_corrected'+input_catalog_file_ext, overwrite=True)

#asciitable.write(catalog.TableData, input_catalog_file_name+'_corrected.txt', Writer=asciitable.FixedWidth, delimiter=" ", bookend=True, 
#                    names=catalog_column_names, overwrite=True)
#os.system('sed -i.bak -e "1s/^ /#/" "%s"'%(input_catalog_file_name+'_corrected.txt'))
#
#print('Output to "%s"!'%(input_catalog_file_name+'_corrected.txt'))
print('Output to "%s"!'%(input_catalog_file_name+'_corrected'+input_catalog_file_ext))



















