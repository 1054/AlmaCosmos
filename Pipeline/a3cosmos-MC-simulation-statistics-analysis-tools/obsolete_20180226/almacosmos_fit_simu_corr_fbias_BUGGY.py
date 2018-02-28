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
    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.py"!')
    sys.exit()


# 
# Read input arguments
# 
input_simu_data_table = ''
input_catalog_file = ''
column_x1 = 'cell_par1_median'
column_x2 = 'cell_par2_median'
column_fbias = 'cell_rel_median'
column_cell_size = 'cell_size'

input_simu_data_table = sys.argv[1]


# 
# Check input data file
# 
if not os.path.isfile(input_simu_data_table):
    print('Error! "%s" was not found!'%(input_simu_data_table))
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabcurvefit')
from CrabCurveFit import *


# 
# Read input data table file
# 
if input_simu_data_table.endswith('.fits'):
    data_table_struct = CrabTable(input_simu_data_table)
    data_table = data_table_struct.TableData
else:
    #data_table = asciitable.read(input_data_table_file)
    data_table_struct = CrabTable(input_simu_data_table)
    data_table = data_table_struct


# 
# Read X Y YErr XErr data array 
# 
data_x1 = []
data_x2 = []
data_fbias = []
data_x1 = data_table.getColumn(column_x1)
data_x2 = data_table.getColumn(column_x2)
data_fbias = data_table.getColumn(column_fbias)
data_cell_size = data_table.getColumn(column_cell_size)


# 
# Set data array
# 
nan_filter = (~numpy.isnan(data_fbias))
y_fbias = data_fbias[nan_filter]
x1 = data_x1[nan_filter]
x2 = data_x2[nan_filter]
y_obs = y_fbias
y_err = numpy.sqrt(10.0/data_cell_size[nan_filter]) * y_obs


# 
# Print data array
# 
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
# Make parameter grid
# 
x1_sparse = numpy.arange(numpy.log10(2.0), numpy.log10(500.0), 0.05)
x2_sparse = numpy.arange(0.0, 5.5, 0.5)
x1_interval = 0.05
x2_interval = 0.5
x1_grid, x2_grid = numpy.meshgrid(x1_sparse, x2_sparse)
x_grid = numpy.column_stack((x1_grid.flatten(),x2_grid.flatten()))



# 
# 2D interpolation
# 
from scipy import interpolate

x_arr = numpy.column_stack((numpy.log10(x1),x2))

fbias_array_extrapolated = interpolate.griddata(x_arr, y_fbias, x_grid, method='nearest')
fbias_array = interpolate.griddata(x_arr, y_fbias, x_grid, method='linear')
fbias_array_mask = numpy.isnan(fbias_array)
fbias_array[fbias_array_mask] = fbias_array_extrapolated[fbias_array_mask]
fbias_grid = fbias_array.reshape(x1_grid.shape)
fbias_grid_mask = fbias_array_mask.reshape(x1_grid.shape)






# 
# note that x1_grid is in log, but x1 is not in log. 
# 






# 
# Plot subplot and fit functions
# 
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
        ax.set_xlim([1.0,1e3])
        ax.set_ylim([-2.5,2.5])
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
        # fit observed data
        if len(iselect) > 1:
            p_fit = fit_func_gravity_energy_field(x1_for_plot, y_for_plot, initial_guess=(-3,3,3,3,-3,-4)) # note that x1_for_plot is linear. 
            y_fit = fit_func_gravity_energy_field_func(numpy.power(10,x1_sparse),*(p_fit['popt']))
            #asciitable.write(numpy.column_stack((numpy.log10(x1_for_plot), y_for_plot)), 'dump_fit_func_x_y_%0.2f.txt'%(numpy.mean(x2_for_plot)))
            pprint(p_fit)
            # 
            if p_fit['valid']:
                best_func_item = {}
                best_func_item['x2'] = numpy.mean(x2_for_plot)
                best_func_item['p_fit'] = p_fit
                best_func.append(best_func_item)
                plot_line(ax, numpy.power(10,x1_sparse), y_fit, color='red')
            else:
                plot_line(ax, numpy.power(10,x1_sparse), y_fit, color='darkgray')
        # 
        # spline observed data
        imask = (x2 >= x2_sparse[i2]-0.5*x2_interval) & (x2 < x2_sparse[i2]+0.5*x2_interval)
        iselect = numpy.argwhere(imask)
        if len(iselect) > 0:
        x1_for_plot = numpy.power(10,x1_grid[imask])
        y_for_plot = scipy.interpolate.spline(x1, y_obs, x1_for_plot, order='1')
        # 
        # plot text label x2
        plot_text(ax, 0, 0.5, r' %0.2f '%(x2_sparse[i2]), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        # 
        # plot interpolated data
        imask = (x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval)
        iselect = numpy.argwhere(imask)
        if len(iselect) > 0:
            x1_for_plot = numpy.power(10,x1_grid[imask])
            x2_for_plot = x2_grid[imask]
            y_for_plot = fbias_grid[imask]
            y_mask_for_plot = fbias_grid_mask[imask]
            #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
            ax.plot(x1_for_plot, y_for_plot, color='black', marker='x', ls='None', ms=3, mew=1.5, zorder=6)
            ax.plot(x1_for_plot[y_mask_for_plot], y_for_plot[y_mask_for_plot], color='darkgray', marker='x', ls='None', ms=3, mew=1.5, zorder=7)
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
# 
pyplot.savefig('Plot_simu_corr_fbias.pdf')
print('')
print('Output to "Plot_simu_corr_fbias.pdf"!')
# 
# zoom
for ax in fig.axes:
    ax.set_ylim([-0.05,0.05])
# 
# savefig
pyplot.savefig('Plot_simu_corr_fbias_zoomed.pdf')
print('')
print('Output to "Plot_simu_corr_fbias_zoomed.pdf"!')
pyplot.clf()


# 
# save best_fit_function
# 
import json
with open('best_fit_function_fbias.json', 'w') as fp:
    json.dump(best_func, fp)
print('Output to "best_fit_function_fbias.json"!')


base_interp = {}
base_interp['x'] = x_arr.tolist() # note that here x1 is in log. 
base_interp['fbias'] = y_fbias.tolist()
with open('base_interp_array_for_fbias.json', 'w') as fp:
    json.dump(base_interp, fp)
print('Output to "base_interp_array_for_fbias.json"!')


#os.system('echo "def best_fit_function_fbias(x1, x2):"  > best_fit_function_fbias.py'%(popt[0]))
#os.system('echo "    a0 = %0.20e"  > best_fit_function_fbias.py'%(popt[0]))
#os.system('echo "    a1 = %0.20e" >> best_fit_function_fbias.py'%(popt[1]))
#os.system('echo "    k1 = %0.20e" >> best_fit_function_fbias.py'%(popt[2]))
#os.system('echo "    n1 = %0.20e" >> best_fit_function_fbias.py'%(popt[3]))
#os.system('echo "    a2 = %0.20e" >> best_fit_function_fbias.py'%(popt[4]))
#os.system('echo "    k2 = %0.20e" >> best_fit_function_fbias.py'%(popt[5]))
#os.system('echo "    n2 = %0.20e" >> best_fit_function_fbias.py'%(popt[6]))
#os.system('echo "    y_fit = a0 * (numpy.exp(a1*numpy.log10(numpy.power((x1/k1),n1)))) * (numpy.exp(a2*(numpy.power((x2/k2),n2))))" >> best_fit_function_fbias.py')
#os.system('echo "    return y_fit" >> best_fit_function_fbias.py')
#os.system('echo "" >> best_fit_function_fbias.py')









