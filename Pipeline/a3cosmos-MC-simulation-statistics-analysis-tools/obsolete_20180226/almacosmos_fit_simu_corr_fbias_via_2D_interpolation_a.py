#!/usr/bin/env python2.7
# 

import os, sys, json
import numpy
import astropy
import astropy.io.ascii as asciitable
from scipy import interpolate
import scipy.optimize
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabcurvefit')
from CrabCurveFit import *



if len(sys.argv) <= 1:
    print('Usage: almacosmos_fit_simu_corr_fbias_via_2D_interpolation.py simu_data_correction_table.txt')
    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.py"!')
    sys.exit()



input_simu_data_table = sys.argv[1] # 'datatable_param_grid_cell_statistics.txt'
data_table_struct = CrabTable(input_simu_data_table)
data_table = data_table_struct
x1 = data_table.getColumn('cell_par1_median')
x2 = data_table.getColumn('cell_par2_median')
fbias = data_table.getColumn('cell_rel_median') # 'cell_rel_median'
cell_size = data_table.getColumn('cell_size')
fbias_err = numpy.sqrt(10.0/cell_size) * fbias



# 
# Make x1 x2 grid
# 
x1_sparse = numpy.arange(numpy.log10(2.0), numpy.log10(1000.0)+0.05, 0.05)
x2_sparse = numpy.arange(1.0, 4.0+0.5, 0.5)
x1_interval = 0.05
x2_interval = 0.5
x1_grid, x2_grid = numpy.meshgrid(x1_sparse, x2_sparse)
x_grid = numpy.column_stack((x1_grid.flatten(),x2_grid.flatten()))



# 
# 2D interpolation
# 
x_arr = numpy.column_stack((numpy.log10(x1),x2))
fbias_array_extrapolated = interpolate.griddata(x_arr, fbias, x_grid, method='nearest')
fbias_array = interpolate.griddata(x_arr, fbias, x_grid, method='linear')
fbias_array_mask = numpy.isnan(fbias_array)
fbias_array[fbias_array_mask] = fbias_array_extrapolated[fbias_array_mask]
fbias_grid = fbias_array.reshape(x1_grid.shape)
fbias_grid_mask = fbias_array_mask.reshape(x1_grid.shape)



# 
# Spline table
# 
fbias_spline_table = {}
fbias_spline_table['log_x1_grid'] = x1_sparse.flatten().tolist()
fbias_spline_table['x1_grid'] = numpy.power(10,x1_sparse).flatten().tolist()
fbias_spline_table['x2_grid'] = x2_sparse.flatten().tolist()
fbias_spline_table['x2_median'] = []
fbias_spline_table['x'] = []
fbias_spline_table['fbias'] = []



# 
# note that x1_grid is in log, but x1 is not in log. 
# 



# 
# Plot subplot and fit functions
# 
fig = pyplot.figure()
fig.set_size_inches(6.5,11.5)
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
        ax.set_xlim([0.1,1000.0])
        ax.set_xscale('log')
        # 
        # plot observed data
        imask = (x2 >= x2_sparse[i2]) & (x2 < x2_sparse[i2]+x2_interval)
        iselect = numpy.argwhere(imask)
        if len(iselect) > 0:
            x1_for_plot = x1[imask]
            x2_for_plot = x2[imask]
            y_for_plot = fbias[imask]
            yerr_for_plot = fbias_err[imask]
            ax.scatter(x1_for_plot, y_for_plot, marker='.', color='dodgerblue', s=100, zorder=5)
            ax.errorbar(x1_for_plot, y_for_plot, yerr=yerr_for_plot, color='dodgerblue', linestyle='none', capsize=5, zorder=5)
            plot_text(ax, 0, 0.48, r' %0.2f '%(numpy.mean(x2_for_plot)), NormalizedCoordinate=True, fontdict=font, verticalalignment='top', horizontalalignment='left', color='dodgerblue', zorder=4)
            # 
            # spline observed data
            x1_argsort = numpy.argsort(x1_for_plot)
            spline_from_x = x1_for_plot[x1_argsort]
            spline_from_y = y_for_plot[x1_argsort]
            spline_to_x = numpy.array(fbias_spline_table['x1_grid'])
            spline_to_y = scipy.interpolate.spline(spline_from_x, spline_from_y, spline_to_x, order='1')
            ax.plot(spline_to_x, spline_to_y, color='green', marker='None', ls='solid')
            fbias_spline_table['fbias'].append(spline_to_y.flatten().tolist())
            fbias_spline_table['x2_median'].append(numpy.mean(x2_for_plot))
            for i3 in range(len(spline_to_y.flatten().tolist())):
                fbias_spline_table['x'].append([spline_to_x[i3],numpy.mean(x2_for_plot)])
        else:
            spline_to_x = numpy.array(fbias_spline_table['x1_grid'])
            spline_to_y = spline_to_x*0.0 + numpy.nan
            fbias_spline_table['fbias'].append(spline_to_y.flatten().tolist())
            fbias_spline_table['x2_median'].append(numpy.nan)
            for i3 in range(len(spline_to_y.flatten().tolist())):
                fbias_spline_table['x'].append([spline_to_x[i3],numpy.mean(x2_for_plot)])
            
        # 
        # print x2 value
        #plot_text(ax, 0, 0.5, r' %0.2f '%(x2_sparse[i2]), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        plot_text(ax, 0, 0.5, r' %0.2f - %0.2f '%(x2_sparse[i2], x2_sparse[i2]+x2_interval), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        # 
        # plot interpolated data
        imask = (x2_grid >= x2_sparse[i2]) & (x2_grid < x2_sparse[i2]+x2_interval)
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
        plot_line(ax, 0, 0.0, 1000.0, 0.0, NormalizedCoordinate=False, color='k', linestyle='dashed', lw=1, zorder=1)
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
print('\nOutput to "Plot_simu_corr_fbias.pdf"!')
for ax in fig.axes: ax.set_ylim([-2.0,2.0])
pyplot.savefig('Plot_simu_corr_fbias_zoomed.pdf')
print('\nOutput to "Plot_simu_corr_fbias_zoomed.pdf"!')
for ax in fig.axes: ax.set_ylim([-0.05,0.05])
pyplot.savefig('Plot_simu_corr_fbias_zoomed_zoomed.pdf')
print('\nOutput to "Plot_simu_corr_fbias_zoomed_zoomed.pdf"!')
# 
# clear
pyplot.clf()


# 
# save base_interp
# 
base_interp = {}
base_interp['x'] = x_arr.tolist() # note that here x1 is in log. 
base_interp['fbias'] = fbias.tolist()
with open('base_interp_array_for_fbias.json', 'w') as fp:
    json.dump(base_interp, fp)
print('\nOutput to "base_interp_array_for_fbias.json"!')


# 
# save fbias_spline_table
# 
spline_table_content = json.dumps(fbias_spline_table, indent=4)
with open('spline_table_fbias.json', 'w') as fp:
    fp.write(spline_table_content)
print('\nOutput to "spline_table_fbias.json"!')





















