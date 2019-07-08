#!/usr/bin/env python2.7
# 


try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")
pkg_resources.require("pysd")
pkg_resources.require("pymc")
pkg_resources.require("pandas")
pkg_resources.require("scipy")

import os, sys

if len(sys.argv) <= 2:
    print('Usage: almacosmos_fit_MCMC.py datatable.txt -x column_number_1 -y column_number_2 -yerr column_number_3 equation_string')
    #sys.exit()

# 
# Read input arguments
input_data_table_file = ''
input_equation_string = ''
column_x1 = 'cell_par1_median' # column number starts from 1.
column_x2 = 'cell_par2_median' # column number starts from 1.
column_y = 'cell_rel_median' # column number starts from 1.
column_yerr = '' # column number starts from 1.
column_xerr = '' # column number starts from 1.

i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '-x':
        if i+1 < len(sys.argv):
            column_x = sys.argv[i+1]
            i = i + 1
    elif sys.argv[i].lower() == '-y':
        if i+1 < len(sys.argv):
            column_y = sys.argv[i+1]
            i = i + 1
    elif sys.argv[i].lower() == '-xerr':
        if i+1 < len(sys.argv):
            column_xerr = sys.argv[i+1]
            i = i + 1
    elif sys.argv[i].lower() == '-yerr':
        if i+1 < len(sys.argv):
            column_yerr = sys.argv[i+1]
            i = i + 1
    else:
        if input_data_table_file == '':
            input_data_table_file = sys.argv[i]
        elif input_equation_string == '':
            input_equation_string = sys.argv[i]
    i = i + 1

# 
# TODO
input_data_table_file = 'datatable_correction.txt'


# 
# Check input data file
if not os.path.isfile(input_data_table_file):
    print('Error! "%s" was not found!'%(input_data_table_file))
    sys.exit()

# 
# Import python packages
import numpy
import pysd
import pymc
import pandas
import astropy
import astropy.io.ascii as asciitable
import scipy.optimize
from matplotlib import pyplot
from pprint import pprint


# 
# Read input data table file
if input_data_table_file.endswith('.fits'):
    sys.path.append(os.path.dirname(sys.argv[0])+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
    from CrabTable import *
    data_table_struct = CrabTable(input_data_table_file)
    data_table = data_table_struct.TableData
else:
    #data_table = asciitable.read(input_data_table_file)
    sys.path.append(os.path.dirname(sys.argv[0])+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
    from CrabTable import *
    data_table_struct = CrabTable(input_data_table_file)
    data_table = data_table_struct

# 
# Read X Y YErr XErr data array 
data_x1 = []
data_x2 = []
data_y = []
data_xerr = []
data_yerr = []
data_x1 = data_table.getColumn(int(column_x1)-1) if column_x1.isdigit() else data_table.getColumn(column_x1)
data_x2 = data_table.getColumn(int(column_x2)-1) if column_x2.isdigit() else data_table.getColumn(column_x2)
data_y = data_table.getColumn(int(column_y)-1) if column_y.isdigit() else data_table.getColumn(column_y)
if column_xerr != '': data_xerr = data_table.getColumn(int(column_xerr)-1) if column_xerr.isdigit() else data_table.getColumn(column_xerr)
if column_yerr != '': data_yerr = data_table.getColumn(int(column_yerr)-1) if column_yerr.isdigit() else data_table.getColumn(column_yerr)
#if len(data_x) == 0: print('Error! Could not determine x!')
#if len(data_y) == 0: print('Error! Could not determine y!')
#if len(data_x) == 0: sys.exit()
#if len(data_y) == 0: sys.exit()

# 
# Plot x y
#sys.path.append(os.path.dirname(sys.argv[0])+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
#from CrabPlot import *
#crab_plot = CrabPlot(x = data_x, y = data_y)
#pyplot.show(block=True)

# 
# Plot once
y_obs = data_y
y_err = data_yerr
x1 = data_x1
x2 = data_x2
#a0 = -2000.0
#a1 = -2.0
#y_fit = a0 * numpy.exp(a1 * x1)
#pyplot.plot(x1, y_obs, color='r', marker='.', ls='None', label='Observed')
#pyplot.plot(x1, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
#pyplot.legend()
#pyplot.show(block=True)

#pymc.test()

# 
# Fit function -- a0 * exp(a1 * x1) * exp(a2 * x2)
#              -- a0=-2000, a1=-1, a2=0
def my_model((x1,x2), y_obs): 
    # priors
    ##sig = pymc.Uniform('sig', 0.0, 100.0, value=1.0)
    #a0 = pymc.Uniform('a0', -5000, 0, value= -2000)
    #a1 = pymc.Uniform('a1', -10, 0, value= -2)
    a0 = pymc.Uniform('a0', -5000, 0, value= -2000)
    a1 = pymc.Uniform('a1', -10.0, 0.0, value= -5.5)
    a2 = pymc.Uniform('a1', -10.0, 0.0, value= -5.5)
    # model
    @pymc.deterministic(plot=False)
    def my_func((x1,x2)=(x1,x2), a0=a0, a1=a1, a2=a2):
        #return a0 * numpy.exp(a1 * x1)
        return a0 * pow(x1, a1) * pow(x2, a2)
    # likelihood
    y = pymc.Normal("y", mu=my_func, tau=1.0, value=y_obs, observed=True)
    #print(locals())
    return locals()

# 
# MCMC
MDL = pymc.MCMC(my_model((x1,x2), y_obs))
MDL.sample(1e4)
pprint(MDL.stats())

# extract and plot results
y_min = MDL.stats()['my_func']['quantiles'][2.5]
y_max = MDL.stats()['my_func']['quantiles'][97.5]
y_fit = MDL.stats()['my_func']['mean']
pyplot.plot(x1, y_obs, color='r', marker='.', ls='None', label='Observed')
pyplot.plot(x1, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
pyplot.fill_between(x1, y_min, y_max, color='0.5', alpha=0.5)
pyplot.legend()

pymc.Matplot.plot(MDL)
pyplot.show(block=True)



# See 
# http://pysd-cookbook.readthedocs.io/en/latest/analyses/fitting/MCMC_for_fitting_models.html


