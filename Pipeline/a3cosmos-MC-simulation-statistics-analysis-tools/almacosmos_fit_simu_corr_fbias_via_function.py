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
#    print('Usage: almacosmos_fit_simu_corr_fbias_via_function.py simu_data_correction_table.txt')
#    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.py"!')
#    sys.exit()


# Read catalog
input_simu_data_table = 'datatable_param_grid_cell_statistics.txt' # sys.argv[1] # 'datatable_param_grid_cell_statistics.txt'
data_table = CrabTable(input_simu_data_table)
x1_obs = data_table.getColumn('cell_par1_median')
x2_obs = data_table.getColumn('cell_par2_median')
y_obs = data_table.getColumn('cell_rel_median') # 'cell_rel_median'
y_err = numpy.sqrt(10.0/data_table.getColumn('cell_size')) * y_obs


# Make x1 x2 grid
#x1_grid = numpy.arange(numpy.log10(2.0), numpy.log10(1000.0)+0.05, 0.01); x1_interval = 0.01
#x2_grid = numpy.arange(1.0, 4.0+0.5, 0.5); x2_interval = 0.5
x1_grid = numpy.power(10,numpy.arange(numpy.log10(2.5),numpy.log10(5e3),0.05))
x2_grid = numpy.array([1.00, 1.25, 1.50, 2.00, 2.50, 3.00, +numpy.inf])
x1_interval = x1_grid[1:len(x1_grid)] - x1_grid[0:len(x1_grid)-1]
x2_interval = x2_grid[1:len(x2_grid)] - x2_grid[0:len(x2_grid)-1]


# Prepare fitfun table
fitfun_table = {}
fitfun_table['x'] = []
fitfun_table['y'] = []


# Loop x2_grid
for i2 in range(len(x2_grid)-1):
    # prepare fitfun to arrays
    fitfun_x = x1_grid # numpy.power(10,x1_grid)
    # select data in x2 bin
    imask = (x2_obs >= x2_grid[i2]) & (x2_obs < x2_grid[i2]+x2_interval[i2])
    iselect = numpy.argwhere(imask)
    if len(iselect) > 0:
        x1_bin = x1_obs[imask]
        x2_bin = x2_obs[imask]
        y_bin = y_obs[imask]
        y_err_bin = y_err[imask]
        # sort observed data
        isort = numpy.argsort(x1_bin)
        # fit function to the observed data
        fitfun_result = fit_func_gravity_energy_field(x1_bin[isort], y_bin[isort], y_err=y_err_bin[isort])
        fitfun_y = fit_func_gravity_energy_field_func(fitfun_x, *(fitfun_result['popt']))
        # filter data out of parameter range
        fitfun_y[(fitfun_x<numpy.min(x1_bin[isort]))] = numpy.nan
    else:
        x2_bin = x2_grid[i2]+0.5*x2_interval[i2]
        fitfun_y = fitfun_x*0.0 + numpy.nan
    # store fitfund data
    for i3 in range(len(fitfun_x)):
        fitfun_table['x'].append([fitfun_x[i3],numpy.mean(x2_bin)])
        fitfun_table['y'].append(fitfun_y[i3])


# Save fitfun_table
fitfun_table_content = json.dumps(fitfun_table, indent=4)
with open('fitfun_table_fbias.json', 'w') as fp:
    fp.write(fitfun_table_content)
print('Output to "fitfun_table_fbias.json"!')





















