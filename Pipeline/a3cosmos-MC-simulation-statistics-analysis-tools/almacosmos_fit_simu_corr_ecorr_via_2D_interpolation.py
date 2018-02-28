#!/usr/bin/env python2.7
# 

import os, sys, json, numpy, astropy, scipy
import astropy.io.ascii as asciitable
from scipy import interpolate, optimize
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabcurvefit')
from CrabCurveFit import *


# Print usage
#if len(sys.argv) <= 1:
#    print('Usage: almacosmos_fit_simu_corr_ecorr_via_2D_interpolation.py simu_data_correction_table.txt')
#    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.py"!')
#    sys.exit()


# Read catalog
input_simu_data_table = 'datatable_param_grid_cell_statistics.txt' # sys.argv[1] # 'datatable_param_grid_cell_statistics.txt'
data_table = CrabTable(input_simu_data_table)
x1_obs = data_table.getColumn('cell_par1_median')
x2_obs = data_table.getColumn('cell_par2_median')
#ecorr = data_table.getColumn('cell_noi_scatter')
ecorr_noi = data_table.getColumn('cell_noi_scatter')
ecorr_noi_L68 = data_table.getColumn('cell_noi_scatter_L68')
ecorr_noi_H68 = data_table.getColumn('cell_noi_scatter_H68')
ecorr_min = numpy.nanmin(numpy.column_stack((ecorr_noi,ecorr_noi_L68,ecorr_noi_H68)), axis=1)
asciitable.write(numpy.column_stack((x1_obs,x2_obs,ecorr_min,ecorr_noi,ecorr_noi_L68,ecorr_noi_H68)), sys.stdout, 
                    names=['x1_obs','x2_obs','ecorr_min','ecorr_noi','ecorr_noi_L68','ecorr_noi_H68'], 
                    Writer=asciitable.FixedWidthTwoLine, delimiter='|', delimiter_pad=' ', position_char='-', bookend=True)
y_obs = ecorr_min


# Mask NaN
nan_filter = (~numpy.isnan(y_obs))
x1_obs = x1_obs[nan_filter]
x2_obs = x2_obs[nan_filter]
y_obs = y_obs[nan_filter]


# Make x1 x2 grid
#x1_grid = numpy.arange(numpy.log10(2.0), numpy.log10(1000.0)+0.05, 0.01); x1_interval = 0.01
#x2_grid = numpy.arange(1.0, 4.0+0.5, 0.5); x2_interval = 0.5
x1_grid = numpy.power(10,numpy.arange(numpy.log10(2.5),numpy.log10(5e3),0.05))
x2_grid = numpy.array([1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 3.50, 4.00, 4.50, 5.00])
x1_interval = x1_grid[1:len(x1_grid)] - x1_grid[0:len(x1_grid)-1]
x2_interval = x2_grid[1:len(x2_grid)] - x2_grid[0:len(x2_grid)-1]


# Make x1 x2 mesh
x1_mesh, x2_mesh = numpy.meshgrid(numpy.log10(x1_grid), x2_grid)
x_mesh = numpy.column_stack((x1_mesh.flatten(),x2_mesh.flatten()))


# Make 2D interpolation
x_arr = numpy.column_stack((numpy.log10(x1_obs),x2_obs))
y_arr = y_obs
array_extrapolated = interpolate.griddata(x_arr, y_arr, x_mesh, method='nearest')
array_interpolated = interpolate.griddata(x_arr, y_arr, x_mesh, method='cubic')
array_mask = numpy.isnan(array_interpolated)
array_combined = array_interpolated
array_combined[array_mask] = array_extrapolated[array_mask]


# Save base_interp
base_interp = {}
base_interp['x'] = x_arr.tolist() # note that here x1 is in log. 
base_interp['y'] = y_arr.tolist()
table_content = json.dumps(base_interp, indent=4)
with open('base_interp_array_for_ecorr.json', 'w') as fp:
    fp.write(table_content)
print('Output to "base_interp_array_for_ecorr.json"!')


# Save interp_table
interp_table = {}
interp_table['x'] = numpy.column_stack((numpy.power(10,x1_mesh.flatten()),x2_mesh.flatten())).tolist() # note that here x1 is in log. 
interp_table['y'] = array_interpolated.tolist()
table_content = json.dumps(interp_table, indent=4)
with open('interp_table_ecorr.json', 'w') as fp:
    fp.write(table_content)
print('Output to "interp_table_ecorr.json"!')





















