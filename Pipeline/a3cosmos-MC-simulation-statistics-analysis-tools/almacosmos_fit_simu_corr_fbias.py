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
    print('Usage: almacosmos_plot_simu_data_correction_fbias.py simu_data_correction_table.txt')
    sys.exit()


# 
# Read input arguments
input_simu_data_table = ''
input_catalog_file = ''
column_x1 = 'cell_par1_median' # column number starts from 1.
column_x2 = 'cell_par2_median' # column number starts from 1.
column_fbias = 'cell_rel_median' # column number starts from 1.
column_ecorr = 'cell_rel_scatter_68' # column number starts from 1.
column_ecorr_L68 = 'cell_rel_scatter_L68' # column number starts from 1.
column_ecorr_H68 = 'cell_rel_scatter_H68' # column number starts from 1.

i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '-sim':
        if i+1 < len(sys.argv):
            input_simu_data_table = sys.argv[i+1]
            i = i + 1
    else:
        if input_simu_data_table == '':
            input_simu_data_table = sys.argv[i]
    i = i + 1


# 
# Check input data file
if not os.path.isfile(input_simu_data_table):
    print('Error! "%s" was not found!'%(input_simu_data_table))
    sys.exit()


# 
# Import python packages
import numpy
import astropy
import astropy.io.ascii as asciitable
import scipy.optimize
#import matplotlib
#from matplotlib import pyplot
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabcurvefit')
from CrabCurveFit import *


# 
# Read input data table file
if input_simu_data_table.endswith('.fits'):
    data_table_struct = CrabTable(input_simu_data_table)
    data_table = data_table_struct.TableData
else:
    #data_table = asciitable.read(input_data_table_file)
    data_table_struct = CrabTable(input_simu_data_table)
    data_table = data_table_struct


# 
# Read X Y YErr XErr data array 
data_x1 = []
data_x2 = []
data_fbias = []
data_ecorr = []
data_ecorr_L68 = []
data_ecorr_H68 = []
data_x1 = data_table.getColumn(int(column_x1)-1) if column_x1.isdigit() else data_table.getColumn(column_x1)
data_x2 = data_table.getColumn(int(column_x2)-1) if column_x2.isdigit() else data_table.getColumn(column_x2)
data_fbias = data_table.getColumn(int(column_fbias)-1) if column_fbias.isdigit() else data_table.getColumn(column_fbias)
data_ecorr = data_table.getColumn(int(column_ecorr)-1) if column_ecorr.isdigit() else data_table.getColumn(column_ecorr)
data_ecorr_L68 = data_table.getColumn(int(column_ecorr_L68)-1) if column_ecorr_L68.isdigit() else data_table.getColumn(column_ecorr_L68)
data_ecorr_H68 = data_table.getColumn(int(column_ecorr_H68)-1) if column_ecorr_H68.isdigit() else data_table.getColumn(column_ecorr_H68)
#if len(data_y) == 0: print('Error! Could not determine y!')
#if len(data_x) == 0: sys.exit()
#if len(data_y) == 0: sys.exit()


# 
# Read data array
# 
y_fbias = data_fbias
y_ecorr = data_ecorr
y_ecorr_L68 = data_ecorr_L68
y_ecorr_H68 = data_ecorr_H68
for i in range(len(y_ecorr)):
    if y_ecorr_L68[i] > 0 and y_ecorr_H68[i] > 0:
        if y_ecorr_L68[i] > y_ecorr_H68[i]:
            y_ecorr[i] = y_ecorr_L68[i] # choose the larger error one
        else:
            y_ecorr[i] = y_ecorr_H68[i] # choose the larger error one
#y_ecorr = numpy.log10(1/y_ecorr)


# 
# Filter out some data points (after several times of tuning)
# 
x1 = data_x1
x2 = data_x2
y_obs = y_fbias
y_err = y_ecorr
#imask = (data_x2<3.0)
#x1 = data_x1[imask]
#x2 = data_x2[imask]
#y_obs = y_fbias[imask]
#y_err = y_ecorr[imask]
col_names = ['x1 (S_peak/rms_noise)','x2 (Maj_convol/Maj_beam)','median (S_in-S_out)/S_in','sigma (S_in-S_out)/S_in']
col_width = len('| ' + ' | '.join(col_names) + ' |')
print('-'*col_width)
asciitable.write(numpy.column_stack((x1,x2,y_obs,y_err)), sys.stdout, 
                    names=col_names,
                    Writer=asciitable.FixedWidthTwoLine, delimiter='|', delimiter_pad=' ', position_char='-', bookend=True)
print('-'*col_width)


# 
# note that x1 is in linear, x2 is in linear, 
# 



# 
# Add some constraint data points?
# 
#y_err = numpy.append(y_err,0.01)
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
# Initial guess
#                    a0     a1     k1     n1     a2     k2     n2
initial_guess = (-0.250, -1.00, +1.00, +1.00, 0.00, +1.00, +1.00)
#initial_guess = (-0.06010105,   0.13198369, -14.45676735,  -0.33198832, 0.85017692,  -0.39402407,  -0.6517596)
bound_range = ([-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf],
                [+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf])

# 
# Try fitting
# 
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

print('')
print('Fitted popt:')
print(numpy.column_stack((numpy.arange(len(popt))+1,popt)))
print('')
#print(pcov)



# 
# Get fitted 'y_fit'
# 
#y_fit = my_func((x1,x2), *popt)



# 
# Make parameter grid
# 
x1_sparse = numpy.arange(numpy.log10(2.0), numpy.log10(500.0), 0.05)
x2_sparse = numpy.arange(0.0, 5.5, 0.5)
x1_interval = 0.05
x2_interval = 0.5
#x1_grid, x2_grid = numpy.meshgrid(x1_sparse, x2_sparse)
#x_grid = numpy.column_stack((x1_grid.flatten(),x2_grid.flatten()))






# 
# note that x1_grid is in log, and ecorr_ is also in log, but x1 is not in log. 
# 



# 
# Plot subplot
fig = pyplot.figure()
fig.set_size_inches(6.5,13.5)
font = {'family': 'serif',
        'weight': 'normal',
        'size': 14,
        }
n2 = len(x2_sparse)
n1 = 1
best_func = []
for i2 in range(n2):
    for i1 in range(n1):
        # 
        print('add_subplot(%d,%d,%d)', n2, n1, n1*i2+i1+1)
        ax = fig.add_subplot(n2, n1, n1*i2+i1+1)
        # 
        ax.set_xlim([1.0,200.0])
        ax.set_ylim([-1.5,1.5])
        ax.set_xscale('log')
        # 
        # plot observed data
        imask = (x2 >= x2_sparse[i2]-0.5*x2_interval) & (x2 < x2_sparse[i2]+0.5*x2_interval)
        iselect = numpy.argwhere(imask)
        if len(iselect) > 0:
            x1_for_plot = x1[imask]
            x2_for_plot = x2[imask]
            y_for_plot = y_obs[imask]
            yerr_for_plot = y_err[imask]
            #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
            ax.scatter(x1_for_plot, y_for_plot, marker='.', color='dodgerblue', s=100, zorder=5)
            ax.errorbar(x1_for_plot, y_for_plot, yerr=yerr_for_plot, color='dodgerblue', linestyle='none', capsize=5, zorder=5)
            # 
            plot_text(ax, 0, 0.48, r' %0.2f '%(numpy.mean(x2_for_plot)), NormalizedCoordinate=True, fontdict=font, verticalalignment='top', horizontalalignment='left', color='dodgerblue', zorder=4)
        # 
        # get fitted y_fit (always plot fitted y_fit even if no obs data point in that bin of parameter space)
        if len(iselect) > -1:
            p_fit = {'popt':popt, 'valid':True}
            y_fit = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+x2_sparse[i2]), *(p_fit['popt']) ) # fit_func_gravity_energy_field_func(numpy.power(10,x1_sparse),*(p_fit['popt']))
            #asciitable.write(numpy.column_stack((numpy.log10(x1_for_plot), y_for_plot)), 'dump_fit_func_x_y_%0.2f.txt'%(numpy.mean(x2_for_plot)))
            #pprint(p_fit)
            # 
            if p_fit['valid']:
                #best_func_item = {}
                #best_func_item['x2'] = numpy.mean(x2_for_plot)
                #best_func_item['p_fit'] = p_fit
                #best_func.append(best_func_item)
                plot_line(ax, numpy.power(10,x1_sparse), y_fit, color='red')
            else:
                plot_line(ax, numpy.power(10,x1_sparse), y_fit, color='darkgray')
        # 
        # plot x2
        plot_text(ax, 0, 0.5, r' %0.2f '%(x2_sparse[i2]), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        # 
        # plot interpolated data
        #imask = (x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval)
        #iselect = numpy.argwhere(imask)
        #if len(iselect) > 0:
        #    x1_for_plot = numpy.power(10,x1_grid[imask])
        #    x2_for_plot = x2_grid[imask]
        #    y_for_plot = fbias_grid[imask]
        #    y_mask_for_plot = fbias_grid_mask[imask]
        #    #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
        #    ax.plot(x1_for_plot, y_for_plot, color='black', marker='x', ls='None', ms=3, mew=1.5, zorder=6)
        #    ax.plot(x1_for_plot[y_mask_for_plot], y_for_plot[y_mask_for_plot], color='darkgray', marker='x', ls='None', ms=3, mew=1.5, zorder=7)
        
        # 
        # plot a line at Y=0
        plot_line(ax, 0, 0.5, 1, 0.5, NormalizedCoordinate=True, color='k', linestyle='dashed', lw=1, zorder=1)
        # 
        # show or hide xylabel
        if i1==0 and i2==n2-1:
            ax.set_xlabel('peak flux / rms noise', fontdict=font)
        elif i1==0 and i2==int((n2-1)/2):
            ax.set_ylabel('median of $(S_{in} - S_{out}) / S_{in}$', fontdict=font)
        # 
        # show or hide xyticks
        if i1!=0:
            ax.set_yticks([])
        if i2!=n2-1:
            ax.set_xticks([])

# 
# savefig
pyplot.savefig('Plot_simu_datatable_correction_fbias.pdf')
pyplot.clf()
print('Output to "Plot_simu_datatable_correction_fbias.pdf"!')








# 
# Plot subplot
# (Obsolete code, after 20180119)
# 
#fig = pyplot.figure()
#ax = pyplot.gca()
#fig, (ax1, ax2) = pyplot.subplots(1, 2, sharey=True, figsize=(8,3.5))
#
#ax1.plot(x1, y_obs, color='r', marker='.', ls='None', label='Observed')
#ax1.errorbar(x1, y_obs, yerr=y_err, color='r', ls='None', lw=1.5, capthick=1.5, capsize=2.5, label='Observed Err')
#ax1.plot(x1, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
#ax1.legend()
#ax1.set_xlabel('S_peak / rms noise')
#ax1.set_ylabel('(S_in - S_out) / S_in')
#ax1.set_xscale('log')
#
#ax2.plot(x2, y_obs, color='r', marker='.', ls='None', label='Observed')
#ax2.errorbar(x2, y_obs, yerr=y_err, color='r', ls='None', lw=1.5, capthick=1.5, capsize=2.5, label='Observed Err')
#ax2.plot(x2, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
#ax2.legend()
#ax2.set_xlabel('FWHM_source / FWHM_beam')
#
#fig.tight_layout()

#pyplot.show(block=True)
#pyplot.savefig('best_fit_function_fbias.pdf')

if pcov == []:
    if os.path.isfile('best_fit_function_fbias.sm'):
        os.system('rm best_fit_function_fbias.sm')
    print('***********')
    print('rm best_fit_function_fbias.sm')
    sys.exit()

os.system('echo "set a0 = %0.20e" > best_fit_function_fbias.sm'%(popt[0]))
os.system('echo "set a1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[1]))
os.system('echo "set k1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[2]))
os.system('echo "set n1 = %0.20e" >> best_fit_function_fbias.sm'%(popt[3]))
os.system('echo "set a2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[4]))
os.system('echo "set k2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[5]))
os.system('echo "set n2 = %0.20e" >> best_fit_function_fbias.sm'%(popt[6]))
os.system('echo "set y_fit = a0 * (exp(a1*lg((x1/k1)**n1))) * (exp(a2*((x2/k2)**n2)))" >> best_fit_function_fbias.sm')
os.system('echo "" >> best_fit_function_fbias.sm')





if pcov == []:
    if os.path.isfile('best_fit_function_fbias.py'):
        os.system('rm best_fit_function_fbias.py')
    print('***********')
    print('rm best_fit_function_fbias.py')
    sys.exit()

os.system('echo "def best_fit_function_fbias(x1, x2):"  > best_fit_function_fbias.py'%(popt[0]))
os.system('echo "    a0 = %0.20e"  > best_fit_function_fbias.py'%(popt[0]))
os.system('echo "    a1 = %0.20e" >> best_fit_function_fbias.py'%(popt[1]))
os.system('echo "    k1 = %0.20e" >> best_fit_function_fbias.py'%(popt[2]))
os.system('echo "    n1 = %0.20e" >> best_fit_function_fbias.py'%(popt[3]))
os.system('echo "    a2 = %0.20e" >> best_fit_function_fbias.py'%(popt[4]))
os.system('echo "    k2 = %0.20e" >> best_fit_function_fbias.py'%(popt[5]))
os.system('echo "    n2 = %0.20e" >> best_fit_function_fbias.py'%(popt[6]))
os.system('echo "    y_fit = a0 * (numpy.exp(a1*numpy.log10(numpy.power((x1/k1),n1)))) * (numpy.exp(a2*(numpy.power((x2/k2),n2))))" >> best_fit_function_fbias.py')
os.system('echo "    return y_fit" >> best_fit_function_fbias.py')
os.system('echo "" >> best_fit_function_fbias.py')









