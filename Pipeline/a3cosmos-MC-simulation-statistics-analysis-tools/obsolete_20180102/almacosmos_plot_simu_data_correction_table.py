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
    print('Usage: almacosmos_plot_simu_data_correction_table.py simu_data_correction_table.txt')
    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.sm"!')
    sys.exit()


# 
# Read input arguments
input_data_table_file = ''
column_x1 = 'cell_par1_median' # column number starts from 1.
column_x2 = 'cell_par2_median' # column number starts from 1.
column_fbias = 'cell_rel_median' # column number starts from 1.
column_ecorr = 'cell_rel_scatter_68' # column number starts from 1.
column_ecorr_L68 = 'cell_rel_scatter_L68' # column number starts from 1.
column_ecorr_H68 = 'cell_rel_scatter_H68' # column number starts from 1.

i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '-cat':
        if i+1 < len(sys.argv):
            input_catalog_file = sys.argv[i+1]
            i = i + 1
    elif sys.argv[i].lower() == '-sim':
        if i+1 < len(sys.argv):
            input_simu_data_table = sys.argv[i+1]
            i = i + 1
    else:
        if input_data_table_file == '':
            input_data_table_file = sys.argv[i]
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
sys.path.append(os.path.dirname(sys.argv[0])+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.append(os.path.dirname(sys.argv[0])+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *


# 
# Read input data table file
if input_data_table_file.endswith('.fits'):
    data_table_struct = CrabTable(input_data_table_file)
    data_table = data_table_struct.TableData
else:
    #data_table = asciitable.read(input_data_table_file)
    data_table_struct = CrabTable(input_data_table_file)
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


# 
# set data array
y_obs = data_fbias.data
y_err = data_ecorr.data
y_fbias = data_fbias.data
y_ecorr = data_ecorr.data
y_ecorr_L68 = data_ecorr_L68.data
y_ecorr_H68 = data_ecorr_H68.data
for i in range(len(y_ecorr)):
    if y_ecorr_L68[i] > 0 and y_ecorr_H68[i] > 0:
        if y_ecorr_L68[i] > y_ecorr_H68[i]:
            y_ecorr[i] = y_ecorr_L68[i]
        else:
            y_ecorr[i] = y_ecorr_H68[i]
y_ecorr = numpy.log10(1/y_ecorr)
x1 = data_x1.data
x2 = data_x2.data


# 
# Make x grid
x1_sparse = numpy.arange(numpy.log10(2.0), numpy.log10(500.0), 0.05)
x2_sparse = numpy.arange(0.0, 5.5, 0.5)
x1_interval = 0.05
x2_interval = 0.5
x1_grid, x2_grid = numpy.meshgrid(x1_sparse, x2_sparse)
x_grid = numpy.column_stack((x1_grid.flatten(),x2_grid.flatten()))


# 
# 2D interpolation
from scipy import interpolate

x_arr = numpy.column_stack((numpy.log10(x1),x2))

y_array_extrapolated = interpolate.griddata(x_arr, y_obs, x_grid, method='nearest')
y_array = interpolate.griddata(x_arr, y_obs, x_grid, method='linear')
y_array_mask = numpy.isnan(y_array)
y_array[y_array_mask] = y_array_extrapolated[y_array_mask]
y_grid = y_array.reshape(x1_grid.shape)
y_grid_mask = y_array_mask.reshape(x1_grid.shape)
#pprint(x1_grid)
#pprint(x2_grid)
#pprint(y_grid)

fbias_array_extrapolated = interpolate.griddata(x_arr, y_fbias, x_grid, method='nearest')
fbias_array = interpolate.griddata(x_arr, y_fbias, x_grid, method='linear')
fbias_array_mask = numpy.isnan(fbias_array)
fbias_array[fbias_array_mask] = fbias_array_extrapolated[fbias_array_mask]
fbias_grid = fbias_array.reshape(x1_grid.shape)
fbias_grid_mask = fbias_array_mask.reshape(x1_grid.shape)
#pprint(x1_grid)
#pprint(x2_grid)
#pprint(fbias_grid)

ecorr_array_extrapolated = interpolate.griddata(x_arr, y_ecorr, x_grid, method='nearest')
ecorr_array = interpolate.griddata(x_arr, y_ecorr, x_grid, method='linear')
ecorr_array_mask = numpy.isnan(ecorr_array)
ecorr_array[ecorr_array_mask] = ecorr_array_extrapolated[ecorr_array_mask]
ecorr_grid = ecorr_array.reshape(x1_grid.shape)
ecorr_grid_mask = ecorr_array_mask.reshape(x1_grid.shape)
#pprint(x1_grid)
#pprint(x2_grid)
#pprint(ecorr_grid)


# 
# note that x1_grid is in log, and ecorr_ is also in log, but x1 is not in log. 


# 
# Plot the surface.
#fig = pyplot.figure()
#ax = fig.gca(projection='3d')
#surf = ax.plot_surface(x1_grid, x2_grid, y_grid, cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)


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
        iselect = numpy.argwhere((x2 >= x2_sparse[i2]-0.5*x2_interval) & (x2 < x2_sparse[i2]+0.5*x2_interval))
        if len(iselect) > 0:
            imask = (x2 >= x2_sparse[i2]-0.5*x2_interval) & (x2 < x2_sparse[i2]+0.5*x2_interval)
            x1_for_plot = x1[imask]
            x2_for_plot = x2[imask]
            y_for_plot = y_fbias[imask]
            #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
            ax.scatter(x1_for_plot, y_for_plot, marker='.', color='dodgerblue', s=100, zorder=5)
            # 
            plot_text(ax, 0, 0.48, r' %0.2f '%(numpy.mean(x2_for_plot)), NormalizedCoordinate=True, fontdict=font, verticalalignment='top', horizontalalignment='left', color='dodgerblue', zorder=4)
        # 
        plot_text(ax, 0, 0.5, r' %0.2f '%(x2_sparse[i2]), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        #ax.text(0.0, 0.5, r' %0.2f-%0.2f '%(x2_sparse[i2],x2_sparse[i2+1]), transform=ax.transAxes, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        # 
        # plot interpolated data
        iselect = numpy.argwhere((x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval))
        if len(iselect) > 0:
            imask = (x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval)
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
pyplot.savefig('datatable_correction_interpolated_fbias.pdf')
pyplot.clf()








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
for i2 in range(n2):
    for i1 in range(n1):
        # 
        print('add_subplot(%d,%d,%d)', n2, n1, n1*i2+i1+1)
        ax = fig.add_subplot(n2, n1, n1*i2+i1+1)
        # 
        ax.set_xlim([1.0,200.0])
        ax.set_ylim([1.0,200.0])
        ax.set_xscale('log')
        ax.set_yscale('log')
        # 
        # plot observed data
        iselect = numpy.argwhere((x2 >= x2_sparse[i2]-0.5*x2_interval) & (x2 < x2_sparse[i2]+0.5*x2_interval))
        if len(iselect) > 0:
            imask = (x2 >= x2_sparse[i2]-0.5*x2_interval) & (x2 < x2_sparse[i2]+0.5*x2_interval)
            x1_for_plot = x1[imask]
            x2_for_plot = x2[imask]
            y_for_plot = numpy.power(10,y_ecorr[imask])
            #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
            ax.scatter(x1_for_plot, y_for_plot, marker='.', color='dodgerblue', s=100, zorder=5)
            # 
            plot_text(ax, 0, 0.48, r' %0.2f '%(numpy.mean(x2_for_plot)), NormalizedCoordinate=True, fontdict=font, verticalalignment='top', horizontalalignment='left', color='dodgerblue', zorder=4)
        # 
        plot_text(ax, 0, 0.5, r' %0.2f '%(x2_sparse[i2]), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        #ax.text(0.0, 0.5, r' %0.2f-%0.2f '%(x2_sparse[i2],x2_sparse[i2+1]), transform=ax.transAxes, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        # 
        # plot interpolated data
        iselect = numpy.argwhere((x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval))
        if len(iselect) > 0:
            imask = (x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval)
            x1_for_plot = numpy.power(10,x1_grid[imask])
            x2_for_plot = x2_grid[imask]
            y_for_plot = numpy.power(10,ecorr_grid[imask])
            y_mask_for_plot = ecorr_grid_mask[imask]
            #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
            ax.plot(x1_for_plot, y_for_plot, color='black', marker='x', ls='None', ms=3, mew=1.5, zorder=6)
            ax.plot(x1_for_plot[y_mask_for_plot], y_for_plot[y_mask_for_plot], color='darkgray', marker='x', ls='None', ms=3, mew=1.5, zorder=7)
        
        # 
        # plot a line of Y=X
        plot_line(ax, 0, 0, 1, 1, NormalizedCoordinate=True, color='k', linestyle='dashed', lw=1, zorder=1)
        # 
        # show or hide xylabel
        if i1==0 and i2==n2-1:
            ax.set_xlabel('peak flux / rms noise', fontdict=font)
        elif i1==0 and i2==int((n2-1)/2):
            ax.set_ylabel('$1/$scatter of $(S_{in} - S_{out}) / S_{in}$', fontdict=font)
        # 
        # show or hide xyticks
        if i1!=0:
            ax.set_yticks([])
        if i2!=n2-1:
            ax.set_xticks([])

# 
# savefig
pyplot.savefig('datatable_correction_interpolated_ecorr.pdf')
pyplot.clf()




print('Then please open "datatable_correction_interpolated_"*".pdf"')








