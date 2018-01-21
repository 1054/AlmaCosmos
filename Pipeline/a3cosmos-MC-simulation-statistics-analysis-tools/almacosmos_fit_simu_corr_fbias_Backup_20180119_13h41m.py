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

if len(sys.argv) < 2:
    print('Usage: almacosmos_fit_simu_corr_fbias.py datatable.txt -x column_number_1 -y column_number_2 -yerr column_number_3 equation_string')
    #sys.exit()


# 
# Read input arguments
input_data_table_file = ''
input_equation_string = ''
column_x1 = 'cell_par1_median' # column number starts from 1.
column_x2 = 'cell_par2_median' # column number starts from 1.
column_y = 'cell_rel_median' # column number starts from 1.
column_yerr = 'cell_rel_scatter_68' # column number starts from 1.
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
#input_data_table_file = 'datatable_correction.txt'


# 
# Check input data file
if not os.path.isfile(input_data_table_file):
    print('Error! "%s" was not found!'%(input_data_table_file))
    sys.exit()

# 
# Import python packages
import numpy
import astropy
import astropy.io.ascii as asciitable
import scipy.optimize
import matplotlib
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
y_obs = data_y.data
y_err = data_yerr.data
x1 = data_x1.data
x2 = data_x2.data
x1 = numpy.append(x1,1000)
x2 = numpy.append(x2,10.0)
y_obs = numpy.append(y_obs,0.0)
y_err = numpy.append(y_err,0.01)
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
def my_func((x1,x2), a0, a1, k1, n1, a2, k2, n2): 
    #return a0 * numpy.exp(a1 * x1) * numpy.exp(a2 * x2)
    #return a0 * pow(x1, a1) * pow(x2, a2)
    #return a0 * pow(x1, a1) * numpy.exp(-x1) * pow(x2, a2) * numpy.exp(-x2)
    #return a0 * pow(x1, a1) * numpy.exp(-x1) * numpy.exp(a2 * x2)
    #return a0 * numpy.exp(a1 * x1) * pow(x1, n1) * numpy.exp(a2 * x2) * pow(x2, n2)
    return a0 * (numpy.exp(a1*numpy.log10((x1/k1)**n1))) * (numpy.exp(a2*((x2/k2)**n2)))
    #return a0 * (numpy.exp(a1*pow(numpy.log10(x1/k1),n1))) * (numpy.exp(a2*pow((x2/k2),n2)))

# 
#                    a0     a1     k1     n1     a2     k2     n2
initial_guess = (-0.250, -1.00, +1.00, +1.00, -1.00, +1.00, +1.00)
#initial_guess = (-0.06010105,   0.13198369, -14.45676735,  -0.33198832, 0.85017692,  -0.39402407,  -0.6517596)
bound_range = ([-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf],
                [+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf])

try:
    popt, pcov = scipy.optimize.curve_fit(my_func, (x1,x2), y_obs, sigma=y_err, bounds=bound_range, p0=initial_guess, maxfev=10000)
except Exception,e:
    print str(e)
    popt = initial_guess
    pcov = []
    try:
        print('Retry fitting')
        #                    a0     a1     k1     n1     a2     k2     n2
        initial_guess = (+0.250, -1.00, +1.00, +0.50, -1.00, +1.00, +0.00)
        popt, pcov = scipy.optimize.curve_fit(my_func, (x1,x2), y_obs, sigma=y_err, bounds=bound_range, p0=initial_guess, maxfev=10000)
    except Exception,e:
        print str(e)
        popt = initial_guess
        pcov = []

pprint(popt)
pprint(pcov)


# extract and plot results
y_fit = my_func((x1,x2), *popt)

#fig = pyplot.figure()
#ax = pyplot.gca()
fig, (ax1, ax2) = pyplot.subplots(1, 2, sharey=True, figsize=(8,3.5))

ax1.plot(x1, y_obs, color='r', marker='.', ls='None', label='Observed')
ax1.errorbar(x1, y_obs, yerr=y_err, color='r', ls='None', lw=1.5, capthick=1.5, capsize=2.5, label='Observed Err')
ax1.plot(x1, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
ax1.legend()
ax1.set_xlabel('S_peak / rms noise')
ax1.set_ylabel('(S_in - S_out) / S_in')
ax1.set_xscale('log')

ax2.plot(x2, y_obs, color='r', marker='.', ls='None', label='Observed')
ax2.errorbar(x2, y_obs, yerr=y_err, color='r', ls='None', lw=1.5, capthick=1.5, capsize=2.5, label='Observed Err')
ax2.plot(x2, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
ax2.legend()
ax2.set_xlabel('FWHM_source / FWHM_beam')

fig.tight_layout()

#pyplot.show(block=True)
pyplot.savefig('best_fit_function_fbias.pdf')

if pcov == []:
    if os.path.isfile('best_fit_function_fbias.sm'):
        os.system('rm best_fit_function_fbias.sm')
    print('***********')
    print('rm best_fit_function_fbias.sm')
    sys.exit()

os.system('echo "set a0 = %0.20e" > best_fit_function_fbias.sm'%(popt[0]))
#os.system('echo "set a1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[1]))
#os.system('echo "set a2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[2]))
#os.system('echo "set y_fit = a0 * exp(a1 * x1) * exp(a2 * x2)" >> best_fit_function_fbias.sm'%(popt[2]))
#os.system('echo "set y_fit = a0 * x1**a1 * exp(-x1) * exp(a2 * x2)" >> best_fit_function_fbias.sm'%(popt[2]))
os.system('echo "set a1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[1]))
os.system('echo "set k1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[2]))
os.system('echo "set n1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[3]))
os.system('echo "set a2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[4]))
os.system('echo "set k2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[5]))
os.system('echo "set n2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[6]))
os.system('echo "set y_fit = a0 * (exp(a1*lg((x1/k1)**n1))) * (exp(a2*((x2/k2)**n2)))" >> best_fit_function_fbias.sm')









