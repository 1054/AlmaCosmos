#!/usr/bin/env python2.7
# 
# 20190506: adjusted plotting range
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

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter, NullFormatter, LogLocator


# Print usage
#if len(sys.argv) <= 1:
#    print('Usage: almacosmos_fit_simu_corr_fbias_via_2D_interpolation.py simu_data_correction_table.txt')
#    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.py"!')
#    sys.exit()


# Read catalog
input_simu_data_table = 'datatable_param_grid_cell_statistics.txt' # sys.argv[1] # 'datatable_param_grid_cell_statistics.txt'
data_table = CrabTable(input_simu_data_table)
x1_obs = data_table.getColumn('cell_par1_median')
x2_obs = data_table.getColumn('cell_par2_median')
cell_size = data_table.getColumn('cell_size')
fbias_obs = data_table.getColumn('cell_rel_median') # 'cell_rel_median'
fbias_err = numpy.sqrt(10.0/cell_size) * fbias_obs
fbias2_obs = data_table.getColumn('cell_rel_mean') # 'cell_rel_median'
fbias2_err = numpy.sqrt(10.0/cell_size) * fbias2_obs
#fbias2_obs = data_table.getColumn('cell_noi_median') # 'cell_noi_median': fbias2 is defined as cell_noi_mean = (S_in-S_out)/noise
#fbias2_err = numpy.sqrt(10.0/cell_size) * fbias2_obs
ecorr_noi = data_table.getColumn('cell_noi_scatter')
ecorr_noi_L68 = data_table.getColumn('cell_noi_scatter_L68')
ecorr_noi_H68 = data_table.getColumn('cell_noi_scatter_H68')
ecorr_min = numpy.nanmin(numpy.column_stack((ecorr_noi,ecorr_noi_L68,ecorr_noi_H68)), axis=1)
asciitable.write(numpy.column_stack((x1_obs,x2_obs,ecorr_min,ecorr_noi,ecorr_noi_L68,ecorr_noi_H68)), sys.stdout, 
                    names=['x1_obs','x2_obs','ecorr_min','ecorr_noi','ecorr_noi_L68','ecorr_noi_H68'], 
                    Writer=asciitable.FixedWidthTwoLine, delimiter='|', delimiter_pad=' ', position_char='-', bookend=True)
ecorr_obs = ecorr_min # ecorr_noi
ecorr_err = numpy.sqrt(10.0/cell_size) * ecorr_obs


# Make x1 x2 grid
#x1_grid = numpy.arange(numpy.log10(2.0), numpy.log10(1000.0)+0.05, 0.01); x1_interval = 0.01
#x2_grid = numpy.arange(1.0, 4.0+0.5, 0.5); x2_interval = 0.5
x1_grid = numpy.array([2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0, 10., 20., 50., 100, 500, 1000.0])
x2_grid = numpy.array([1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00, +numpy.inf])
x1_interval = x1_grid[1:len(x1_grid)] - x1_grid[0:len(x1_grid)-1]
x2_interval = x2_grid[1:len(x2_grid)] - x2_grid[0:len(x2_grid)-1]


# set a SNRpeak limit
SNRpeak_limit = 3.0
SNRpeak_threshold = 5.40 # our photometry catalog to galaxy catalog SNRpeak threshold, determined in a3cosmos paper I Sect.~4.1


# Plot subplots
fig = pyplot.figure()
fig.set_size_inches(13.0,11.5)
font = { 'family': 'serif', 'weight': 'normal', 'size': 14 }
n2 = len(x2_grid)-1
n2 = n2 - 1 #<TODO># the last x2 bin is empty, so do not show it
for i2 in range(n2):
    
    
    
    
    i1 = 0 # panel column 0
    
    
    
    # 
    # add subplot (fbias)
    print('add_subplot(%d,%d,%d)', n2, 2, 2*i2+i1+1)
    ax = fig.add_subplot(n2, 2, 2*i2+i1+1)
    # 
    # set axis
    #ax.set_xlim([1,1000.0]) #<20190506>#
    ax.set_xlim([SNRpeak_limit,30.0]) #<20190506>#
    ax.set_xscale('log')
    ax.set_ylim([-2.5,2.5])
    ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1.0,2.0,3.0,4.0,5.0,6.0,7.0))) #<20190506>#
    ax.xaxis.set_major_formatter(ScalarFormatter()) #<20190506>#
    ax.xaxis.set_minor_formatter(NullFormatter()) #<20190506>#
    # 
    # print x2 value
    plot_text(ax, 0.96, 0.7, r' $\Theta_{beam}$: %0.2f - %0.2f '%(x2_grid[i2], x2_grid[i2]+x2_interval[i2]), 
                NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='right', zorder=4)
    #plot_text(ax, 0, 0.5, r' %0.2f - %0.2f '%(x2_grid[i2], x2_grid[i2]+x2_interval[i2]), 
    #            NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
    # 
    # print a line at Y=0
    plot_line(ax, ax.get_xlim()[0], 0.0, ax.get_xlim()[1], 0.0, NormalizedCoordinate=False, color='k', linestyle='dashed', lw=1, zorder=1)
    # 
    # plot a line at X=SNRpeak_threshold
    plot_line(ax, SNRpeak_threshold, -2.1, SNRpeak_threshold, 2.1, NormalizedCoordinate=False, color='k', linestyle='dashed', lw=1.5, zorder=2)
    # 
    # select data in x2 bin
    imask = (x1_obs>=SNRpeak_limit) & (x2_obs >= x2_grid[i2]) & (x2_obs < x2_grid[i2]+x2_interval[i2])
    iselect = numpy.argwhere(imask)
    if len(iselect) > 0:
        x1_bin = x1_obs[imask]
        x2_bin = x2_obs[imask]
        # 
        # plot observed data
        ax.scatter(x1_bin, fbias_obs[imask], marker='.', color='dodgerblue', s=100, zorder=5)
        ax.errorbar(x1_bin, fbias_obs[imask], yerr=fbias_err[imask], color='dodgerblue', linestyle='none', capsize=5, zorder=5)
        ax.scatter(x1_bin, fbias2_obs[imask], marker='o', edgecolor='orangered', facecolor='none', s=100, zorder=6)
        #ax.errorbar(x1_bin, fbias2_obs[imask], yerr=fbias2_err[imask], color='orangered', linestyle='--', capsize=5, zorder=6)
        #plot_text(ax, 0, 0.48, r' %0.2f '%(numpy.mean(x2_bin)), NormalizedCoordinate=True, fontdict=font, verticalalignment='top', horizontalalignment='left', color='dodgerblue', zorder=4)
    # 
    # plot splined data
    if os.path.isfile('spline_table_fbias.json'):
        handle = open('spline_table_fbias.json', 'r')
        spline_table = json.load(handle)
        spline_table_x = []
        spline_table_y = []
        for spline_table_i in range(len(spline_table['y'])):
            if (spline_table['x'][spline_table_i][0]) >= numpy.min(x1_bin) and \
               (spline_table['x'][spline_table_i][0]) <= numpy.max(x1_bin) and \
               (spline_table['x'][spline_table_i][1] >= x2_grid[i2]) and \
               (spline_table['x'][spline_table_i][1] < x2_grid[i2]+x2_interval[i2]):
                spline_table_x.append(spline_table['x'][spline_table_i][0])
                spline_table_y.append(spline_table['y'][spline_table_i])
        if len(spline_table_x)>0:
            ax.plot(spline_table_x, spline_table_y, color='green', marker='None', ls='solid')
    # 
    # plot interpolated data
    if os.path.isfile('interp_table_fbias.json'):
        handle = open('interp_table_fbias.json', 'r')
        interp_table = json.load(handle)
        interp_table_x = []
        interp_table_y = []
        for interp_table_i in range(len(interp_table['y'])):
            if (interp_table['x'][interp_table_i][1] >= x2_grid[i2]) and (interp_table['x'][interp_table_i][1] < x2_grid[i2]+x2_interval[i2]):
                interp_table_x.append(interp_table['x'][interp_table_i][0])
                interp_table_y.append(interp_table['y'][interp_table_i])
        #<20180524># if len(interp_table_x)>0:
        #<20180524>#     ax.plot(interp_table_x, interp_table_y, color='darkgray', marker='x', ls='None', ms=3, mew=1.5, zorder=7)
    # 
    # plot function-fitted data
    if os.path.isfile('fitfun_table_fbias.json'):
        handle = open('fitfun_table_fbias.json', 'r')
        fitfun_table = json.load(handle)
        fitfun_table_x = []
        fitfun_table_y = []
        for fitfun_table_i in range(len(fitfun_table['y'])):
            if (fitfun_table['x'][fitfun_table_i][1] >= x2_grid[i2]) and (fitfun_table['x'][fitfun_table_i][1] < x2_grid[i2]+x2_interval[i2]):
                fitfun_table_x.append(fitfun_table['x'][fitfun_table_i][0])
                fitfun_table_y.append(fitfun_table['y'][fitfun_table_i])
        if len(fitfun_table_x)>0:
            ax.plot(fitfun_table_x, fitfun_table_y, color='red', marker='None', ls='solid')
    # 
    # adjust tick font size
    pyplot.xticks(fontsize=14)
    pyplot.yticks(fontsize=14)
    # 
    # show or hide xylabel
    if i2==0:
        plot_text(ax, 0.5, 1.15, r'Flux Bias Analysis', NormalizedCoordinate=True, fontdict=font, fontsize=18, verticalalignment='bottom', horizontalalignment='center', color='black')
    elif i2==n2-1:
        ax.set_xlabel(r'$\mathrm{S/N_{peak}}$', fontdict=font, fontsize=18, labelpad=5)
    elif i2==int((n2-1)/2):
        ax.set_ylabel(r'Median (Mean) of  $(S_{sim.} - S_{rec.}) \,/\, S_{sim.}$', fontdict=font, fontsize=18, labelpad=15)
    # 
    # show or hide xyticks
    if i2!=n2-1:
        ax.set_xticks([])
    
    
    
    
    
    i1 = 1 # panel column 1
    
    
    
    # 
    # add subplot (ecorr)
    print('add_subplot(%d,%d,%d)', n2, 2, 2*i2+i1+1)
    ax = fig.add_subplot(n2, 2, 2*i2+i1+1)
    # 
    # set axis
    #ax.set_xlim([1,1000.0]) #<20190506>#
    ax.set_xlim([SNRpeak_limit,30.0]) #<20190506>#
    ax.set_xscale('log')
    ax.set_ylim([0.0,25.0])
    ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1.0,2.0,3.0,4.0,5.0,6.0,7.0))) #<20190506>#
    ax.xaxis.set_major_formatter(ScalarFormatter()) #<20190506>#
    ax.xaxis.set_minor_formatter(NullFormatter()) #<20190506>#
    # 
    # print x2 value
    plot_text(ax, 0.96, 0.7, r' $\Theta_{beam}$: %0.2f - %0.2f '%(x2_grid[i2], x2_grid[i2]+x2_interval[i2]), 
                NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='right', zorder=4)
    #plot_text(ax, 0, 0.5, r' %0.2f - %0.2f '%(x2_grid[i2], x2_grid[i2]+x2_interval[i2]), 
    #            NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
    # 
    # print a line at Y=1
    #plot_line(ax, 0, 1.0, 1000.0, 1.0, NormalizedCoordinate=False, color='k', linestyle='dashed', lw=1, zorder=1)
    # 
    # select data in x2 bin
    imask = (x1_obs>=SNRpeak_limit) & (x2_obs >= x2_grid[i2]) & (x2_obs < x2_grid[i2]+x2_interval[i2])
    iselect = numpy.argwhere(imask)
    if len(iselect) > 0:
        x1_bin = x1_obs[imask]
        x2_bin = x2_obs[imask]
        # 
        # plot observed data
        ax.scatter(x1_bin, ecorr_obs[imask], marker='.', color='dodgerblue', s=100, zorder=5)
        ax.scatter(x1_bin, ecorr_noi[imask], marker='o', edgecolor='orangered', facecolor='none', s=80, zorder=6)
        ax.errorbar(x1_bin, ecorr_obs[imask], yerr=ecorr_err[imask], color='dodgerblue', linestyle='none', capsize=5, zorder=5)
        #plot_text(ax, 0, 0.48, r' %0.2f '%(numpy.mean(x2_bin)), NormalizedCoordinate=True, fontdict=font, verticalalignment='top', horizontalalignment='left', color='dodgerblue', zorder=4)
    # 
    # plot splined data
    if os.path.isfile('spline_table_ecorr.json'):
        handle = open('spline_table_ecorr.json', 'r')
        spline_table = json.load(handle)
        spline_table_x = []
        spline_table_y = []
        for spline_table_i in range(len(spline_table['y'])):
            if (spline_table['x'][spline_table_i][1] >= x2_grid[i2]) and (spline_table['x'][spline_table_i][1] < x2_grid[i2]+x2_interval[i2]):
                spline_table_x.append(spline_table['x'][spline_table_i][0])
                spline_table_y.append(spline_table['y'][spline_table_i])
        if len(spline_table_x)>0:
            ax.plot(spline_table_x, spline_table_y, color='green', marker='None', ls='solid')
    # 
    # plot interpolated data
    if os.path.isfile('interp_table_ecorr.json'):
        handle = open('interp_table_ecorr.json', 'r')
        interp_table = json.load(handle)
        interp_table_x = []
        interp_table_y = []
        for interp_table_i in range(len(interp_table['y'])):
            if (interp_table['x'][interp_table_i][1] >= x2_grid[i2]) and (interp_table['x'][interp_table_i][1] < x2_grid[i2]+x2_interval[i2]):
                interp_table_x.append(interp_table['x'][interp_table_i][0])
                interp_table_y.append(interp_table['y'][interp_table_i])
        #<20180524># if len(interp_table_x)>0:
        #<20180524>#     ax.plot(interp_table_x, interp_table_y, color='darkgray', marker='x', ls='None', ms=3, mew=1.5, zorder=7)
    # 
    # plot function-fitted data
    if os.path.isfile('fitfun_table_ecorr.json'):
        handle = open('fitfun_table_ecorr.json', 'r')
        fitfun_table = json.load(handle)
        fitfun_table_x = []
        fitfun_table_y = []
        for fitfun_table_i in range(len(fitfun_table['y'])):
            if (fitfun_table['x'][fitfun_table_i][1] >= x2_grid[i2]) and (fitfun_table['x'][fitfun_table_i][1] < x2_grid[i2]+x2_interval[i2]):
                fitfun_table_x.append(fitfun_table['x'][fitfun_table_i][0])
                fitfun_table_y.append(fitfun_table['y'][fitfun_table_i])
        #<20180524># if len(fitfun_table_x)>0:
        #<20180524>#     ax.plot(fitfun_table_x, fitfun_table_y, color='red', marker='None', ls='solid')
    # 
    # adjust tick font size
    pyplot.xticks(fontsize=14)
    pyplot.yticks(fontsize=14)
    # 
    # show or hide xylabel
    if i2==0:
        plot_text(ax, 0.5, 1.15, r'Flux Error Analysis', NormalizedCoordinate=True, fontdict=font, fontsize=18, verticalalignment='bottom', horizontalalignment='center', color='black')
    elif i2==n2-1:
        ax.set_xlabel(r'$\mathrm{S/N_{peak}}$', fontdict=font, fontsize=18, labelpad=5)
    elif i2==int((n2-1)/2):
        ax.set_ylabel(r'Scatter (Percentile) of  $(S_{sim.} - S_{rec.}) \,/\, \mathrm{rms\,noise}$', fontdict=font, fontsize=18, labelpad=15)
    # 
    # show or hide xyticks
    if i2!=n2-1:
        ax.set_xticks([])




# 
# adjust
# 
pyplot.subplots_adjust(wspace=0.28, hspace=0.00)







# 
# savefig
# 
pyplot.savefig('Plot_simu_corr.pdf')
print('\nOutput to "Plot_simu_corr.pdf"!')
for i in range(0,len(fig.axes),2): fig.axes[i].set_ylim([-2.0,2.0])
for i in range(1,len(fig.axes),2): fig.axes[i].set_ylim([0.5,10.0])
pyplot.savefig('Plot_simu_corr_zoomed.pdf')
print('\nOutput to "Plot_simu_corr_zoomed.pdf"!')
for i in range(0,len(fig.axes),2): fig.axes[i].set_ylim([-0.5,0.5])
for i in range(1,len(fig.axes),2): fig.axes[i].set_ylim([0.75,5.0])
pyplot.savefig('Plot_simu_corr_zoomed_zoomed.pdf')
print('\nOutput to "Plot_simu_corr_zoomed_zoomed.pdf"!')
for i in range(0,len(fig.axes),2): fig.axes[i].set_ylim([-0.05,0.05])
for i in range(1,len(fig.axes),2): fig.axes[i].set_ylim([1.0,2.5])
pyplot.savefig('Plot_simu_corr_zoomed_zoomed_zoomed.pdf')
print('\nOutput to "Plot_simu_corr_zoomed_zoomed_zoomed.pdf"!')
# 
# clear
pyplot.clf()





















