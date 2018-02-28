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
#    print('Usage: almacosmos_fit_simu_corr_ecorr_via_spline.py simu_data_correction_table.txt')
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
x2_grid = numpy.array([1.00, 1.25, 1.50, 2.00, 2.50, 3.00, +numpy.inf])
x1_interval = x1_grid[1:len(x1_grid)] - x1_grid[0:len(x1_grid)-1]
x2_interval = x2_grid[1:len(x2_grid)] - x2_grid[0:len(x2_grid)-1]


# Prepare spline table
spline_table = {}
spline_table['x'] = []
spline_table['y'] = []


# Loop x2_grid
for i2 in range(len(x2_grid)-1):
    # prepare spline to arrays
    spline_to_x = x1_grid
    # select data in x2 bin
    imask = (x2_obs >= x2_grid[i2]) & (x2_obs < x2_grid[i2]+x2_interval[i2])
    iselect = numpy.argwhere(imask)
    if len(iselect) > 0:
        x1_bin = x1_obs[imask]
        x2_bin = x2_obs[imask]
        y_bin = y_obs[imask]
        # sort observed data
        isort = numpy.argsort(x1_bin)
        spline_from_x = x1_bin[isort]
        spline_from_y = y_bin[isort]
        # spline observed data
        spline_to_y = scipy.interpolate.spline(spline_from_x, spline_from_y, spline_to_x, order='1')
        # filter data out of parameter range
        spline_to_y[(spline_to_x<numpy.min(spline_from_x))] = spline_from_y[numpy.argwhere((spline_from_x==numpy.min(spline_from_x))).flatten()] # <TODO> extrapolate to lower and higher x1
        spline_to_y[(spline_to_x>numpy.max(spline_from_x))] = spline_from_y[numpy.argwhere((spline_from_x==numpy.max(spline_from_x))).flatten()] # <TODO> extrapolate to lower and higher x1
    else:
        x2_bin = x2_grid[i2]+0.5*x2_interval[i2]
        spline_to_y = spline_to_x*0.0 + numpy.nan
    # store splined data
    for i3 in range(len(spline_to_x)):
        spline_table['x'].append([spline_to_x[i3],numpy.mean(x2_bin)])
        spline_table['y'].append(spline_to_y[i3])


# Save spline_table
spline_table_content = json.dumps(spline_table, indent=4)
with open('spline_table_ecorr.json', 'w') as fp:
    fp.write(spline_table_content)
print('Output to "spline_table_ecorr.json"!')





















