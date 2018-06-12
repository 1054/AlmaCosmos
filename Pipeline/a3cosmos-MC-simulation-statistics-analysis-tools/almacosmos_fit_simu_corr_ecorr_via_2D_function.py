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


# 
# Print usage
# 
#if len(sys.argv) <= 1:
#    print('Usage: almacosmos_fit_simu_corr_ecorr_via_2D_function.py simu_data_correction_table.txt')
#    print('# Note: simu_data_correction_table.txt is the output file of "almacosmos_calc_simu_stats.py"!')
#    sys.exit()


# 
# Read input arguments
# 
input_simu_data_table = 'datatable_param_grid_cell_statistics.txt' # sys.argv[1]


# 
# Read input data table file
# 
if input_simu_data_table.endswith('.fits'):
    data_table_struct = CrabTable(input_simu_data_table)
    data_table = data_table_struct.TableData
else:
    data_table_struct = CrabTable(input_simu_data_table)
    data_table = data_table_struct


# 
# Read X Y YErr XErr data array 
# 
data_x1 = data_table.getColumn('cell_par1_median')
data_x2 = data_table.getColumn('cell_par2_median')
data_fbias = data_table.getColumn('cell_rel_median')
data_ecorr = data_table.getColumn('cell_abs_scatter')
data_ecorr_noi = data_table.getColumn('cell_noi_scatter')
data_ecorr_L68 = data_table.getColumn('cell_rel_scatter_L68')
data_ecorr_H68 = data_table.getColumn('cell_rel_scatter_H68')
data_cell_size = data_table.getColumn('cell_size')
#ecorr = data_table.getColumn('cell_noi_scatter')
ecorr_noi = data_table.getColumn('cell_noi_scatter')
ecorr_noi_L68 = data_table.getColumn('cell_noi_scatter_L68')
ecorr_noi_H68 = data_table.getColumn('cell_noi_scatter_H68')
ecorr_min = numpy.nanmin(numpy.column_stack((ecorr_noi,ecorr_noi_L68,ecorr_noi_H68)), axis=1)
asciitable.write(numpy.column_stack((data_x1,data_x2,ecorr_min,ecorr_noi,ecorr_noi_L68,ecorr_noi_H68)), sys.stdout, 
                    names=['data_x1','data_x2','ecorr_min','ecorr_noi','ecorr_noi_L68','ecorr_noi_H68'], 
                    Writer=asciitable.FixedWidthTwoLine, delimiter='|', delimiter_pad=' ', position_char='-', bookend=True)
y_obs = ecorr_noi # ecorr_min #<TODO>#
y_err = numpy.sqrt(10.0/data_cell_size) * y_obs # <TODO> assign larger errors to larger x2


# Mask NaN
nan_filter = (~numpy.isnan(y_obs))
x1 = data_x1[nan_filter]
x2 = data_x2[nan_filter]
y_obs = y_obs[nan_filter]
y_err = y_err[nan_filter]
y_obs_log = numpy.log10(y_obs)
y_err_log = y_err/y_obs


# 
# Print data array
# 
col_names = ['x1 (S_peak/rms_noise)','x2 (Maj_convol/Maj_beam)','scatter of ((S_in-S_out) / noise)','1 / cell size']
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






# 
# Fit function
# 
def my_func((x1,x2), a1, k1, n1, a2, k2, n2): 
    #fx1k1 = numpy.log10(x1/k1) + numpy.exp(-(x2-k2)**n2)
    #f1 = numpy.log10(x1) - (a1 * numpy.exp(-numpy.log10(x1/k1 + x2/k2)**n1)) + a2 # + numpy.exp(-(x2/k2)**n2)
    #fs = f1 # numpy.power(10, f1) # now we do the fitting in log! Y is in log, but x1 and x2 are in linear. 
    # 
    #return fs
    #log_of_one_over_scatter = numpy.log10(x1) - (a1 * numpy.exp(-numpy.log10(x1/k1 + x2/k2)**n1)) + a2
    #f_poly = a1 + k1 * numpy.log10(x1) + n1 * numpy.log10(x1)**2 + a2 * numpy.log10(x1)**3 + k2 * numpy.log10(x1)**4
    #f1 = a1 + k1 * numpy.exp(numpy.log10(x1)**n1)
    #f_xmax = 
    #log_of_scatter_over_noise = (a1 + a2*x2 + k2*x2**2 + n2*x2**3)
    log_of_scatter_over_noise = (a1 + k1*numpy.log10(x1) + n1*numpy.log10(x1)**2 + k2*x2 + n2*x2**2) # + n1*x1**2 + n2*x2**2
    return log_of_scatter_over_noise


# 
# Initial guess
# 
initial_guess = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
bound_range = None


# 
# Try fitting
# 
try:
    popt, pcov = scipy.optimize.curve_fit(my_func, (x1,x2), y_obs_log, sigma=y_err_log, p0=initial_guess, maxfev=10000) #, bounds=bound_range, 
except Exception,e:
    print str(e)
    popt = initial_guess
    pcov = []
    try:
        print('Retry fitting')
        #                    a0     a1     k1     n1     a2     k2     n2     c2
        #initial_guess = (+0.250, -1.00, +1.00, +0.50, -1.00, +1.00, +0.00, +0.00)
        popt, pcov = scipy.optimize.curve_fit(my_func, (x1,x2), y_obs_log, sigma=y_err_log, p0=initial_guess, maxfev=10000) #, bounds=bound_range, 
    except Exception,e:
        print str(e)
        popt = initial_guess
        pcov = []

print('')
print('Fitted popt:')
print(numpy.column_stack((numpy.array(['a1','k1','n1','a2','k2','n2']),popt)))
print('')
#print(pcov)


if pcov == []:
    sys.exit()




do_MCMC = False

popt_mean = []

if do_MCMC:
    # 
    # Try fitting with pymc
    # 
    import pymc
    #from pymc.examples import disaster_model
    from pymc import MCMC
    def M_model(x1, x2, y_obs_log, y_err_log):
        # 
        # priors
        a1 = pymc.Uniform('a1',  -20.0,  +20.0, value = +0.5)
        k1 = pymc.Uniform('k1',  -20.0,  +20.0, value = +0.5)
        n1 = pymc.Uniform('n1',  -20.0,  +20.0, value = +0.5)
        a2 = pymc.Uniform('a2',  -20.0,  +20.0, value = +0.01)
        k2 = pymc.Uniform('k2',  -20.0,  +20.0, value = +0.01)
        n2 = pymc.Uniform('n2',  -20.0,  +20.0, value = -0.01)
        # 
        # M_func = pymc.deterministic(*kwargs)
        @pymc.deterministic(plot=False)
        def M_func(x1=x1, x2=x2, a1=a1, k1=k1, n1=n1, a2=a2, k2=k2, n2=n2):
            return my_func((x1, x2), a1, k1, n1, a2, k2, n2)
        # 
        # likelihood
        y_fit = pymc.Normal("y_fit", mu=M_func, tau=1.0/y_err_log**2, value=y_obs_log, observed=True)
        # 
        #print(locals())
        return locals()
    # 
    # MCMC
    MDL = pymc.MCMC(M_model(x1, x1, y_obs_log, y_err_log))
    MDL.sample(3e4)
    #MDL.sample(3e5)
    pprint(MDL.stats())
    # 
    #M.sample(iter=3000, burn=1000, thin=10)
    #M.trace('switchpoint')[:]
    #from pylab import hist, show
    #hist(MDL.trace('a0')[:])
    from pymc.Matplot import plot
    plot(MDL)
    ##
    ##print(MDL.stats()['M_func'])
    #y_fit_min = MDL.stats()['M_func']['quantiles'][2.5]
    #y_fit_max = MDL.stats()['M_func']['quantiles'][97.5]
    #y_fit_mean = MDL.stats()['M_func']['mean']
    from copy import copy
    popt_mean = copy(popt)
    popt_mean[0] = MDL.stats()['a1']['mean']
    popt_mean[1] = MDL.stats()['k1']['mean']
    popt_mean[2] = MDL.stats()['n1']['mean']
    popt_mean[3] = MDL.stats()['a2']['mean']
    popt_mean[4] = MDL.stats()['k2']['mean']
    popt_mean[5] = MDL.stats()['n2']['mean']
    popt_min = copy(popt)
    popt_min[0] = MDL.stats()['a1']['quantiles'][2.5]
    popt_min[1] = MDL.stats()['k1']['quantiles'][2.5]
    popt_min[2] = MDL.stats()['n1']['quantiles'][2.5]
    popt_min[3] = MDL.stats()['a2']['quantiles'][2.5]
    popt_min[4] = MDL.stats()['k2']['quantiles'][2.5]
    popt_min[5] = MDL.stats()['n2']['quantiles'][2.5]
    popt_max = copy(popt)
    popt_max[0] = MDL.stats()['a1']['quantiles'][97.5]
    popt_max[1] = MDL.stats()['k1']['quantiles'][97.5]
    popt_max[2] = MDL.stats()['n1']['quantiles'][97.5]
    popt_max[3] = MDL.stats()['a2']['quantiles'][97.5]
    popt_max[4] = MDL.stats()['k2']['quantiles'][97.5]
    popt_max[5] = MDL.stats()['n2']['quantiles'][97.5]
    # 
    print('')
    print('Fitted popt from MCMC:')
    print(numpy.column_stack((numpy.array(['a1','k1','n1','a2','k2','n2']),popt)))
    print('')
    # 
    print('')
    print('Fitted popt_mean from MCMC:')
    print(numpy.column_stack((numpy.array(['a1','k1','n1','a2','k2','n2']),popt_mean)))
    print('')



# 
# Get fitted 'y_fit'
# 
#y_fit = my_func((x1,x2), *popt)






# 
# Make parameter grid
# 
x1_sparse = numpy.arange(numpy.log10(2.0), numpy.log10(1000.0)+0.05, 0.01)
x2_sparse = numpy.arange(0.0, 5.0+0.5, 0.5)
x1_interval = 0.01
x2_interval = 0.5
#x1_grid, x2_grid = numpy.meshgrid(x1_sparse, x2_sparse)
#x_grid = numpy.column_stack((x1_grid.flatten(),x2_grid.flatten()))






# 
# note that x1_grid is in log, and ecorr_ is also in log, but x1 is not in log. 
# 





# 
# Plot subplot
# 
fig = pyplot.figure()
fig.set_size_inches(6.5,11.5)
font = {'family': 'serif',
        'weight': 'normal',
        'size': 14,
        }
n2 = len(x2_sparse)-1
n1 = 1
best_func = []
for i2 in range(n2):
    for i1 in range(n1):
        # 
        print('add_subplot(%d,%d,%d)', n2, n1, n1*i2+i1+1)
        ax = fig.add_subplot(n2, n1, n1*i2+i1+1)
        # 
        ax.set_xlim([0.1,1000.0])
        ax.set_ylim([1e-2,1e2]) # we plot y as 
        ax.set_xscale('log')
        ax.set_yscale('log')
        # 
        # plot observed data
        imask = (x2 >= x2_sparse[i2]) & (x2 < x2_sparse[i2]+x2_interval)
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
            x2_for_plot = numpy.mean(x2_for_plot)
        else:
            x2_for_plot = x2_sparse[i2]+0.5*x2_interval
        # 
        # get fitted y_fit (always plot fitted y_fit even if no obs data point in that bin of parameter space)
        y_fit = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt ) # note that the function is fitted in log!
        plot_line(ax, numpy.power(10,x1_sparse), numpy.power(10,y_fit), color='red')
        if do_MCMC is True:
            y_fit_mean = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt_mean ) # note that the function is fitted in log!
            y_fit_min = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt_min ) # note that the function is fitted in log!
            y_fit_max = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt_max ) # note that the function is fitted in log!
            plot_line(ax, numpy.power(10,x1_sparse), numpy.power(10,y_fit_mean), color='k', lw=2)
            ax.fill_between(numpy.power(10,x1_sparse), numpy.power(10,y_fit_min), numpy.power(10,y_fit_max), color='0.5', alpha=0.5)
        # 
        # print x2 value
        plot_text(ax, 0, 0.5, r' %0.2f - %0.2f '%(x2_sparse[i2], x2_sparse[i2]+x2_interval), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
        # 
        # plot interpolated data
        #imask = (x2_grid >= x2_sparse[i2]-0.5*x2_interval) & (x2_grid < x2_sparse[i2]+0.5*x2_interval)
        #iselect = numpy.argwhere(imask)
        #if len(iselect) > 0:
        #    x1_for_plot = numpy.power(10,x1_grid[imask])
        #    x2_for_plot = x2_grid[imask]
        #    y_for_plot = numpy.power(10,ecorr_grid[imask])
        #    y_mask_for_plot = ecorr_grid_mask[imask]
        #    #pprint(numpy.column_stack((x1_for_plot,x2_for_plot,y_for_plot)))
        #    ax.plot(x1_for_plot, y_for_plot, color='black', marker='x', ls='None', ms=3, mew=1.5, zorder=6)
        #    ax.plot(x1_for_plot[y_mask_for_plot], y_for_plot[y_mask_for_plot], color='darkgray', marker='x', ls='None', ms=3, mew=1.5, zorder=7)
        
        # 
        # plot a line Y=0
        plot_line(ax, 0.1, 1, 1e3, 1, NormalizedCoordinate=False, color='k', linestyle='dashed', lw=1, zorder=1)
        # 
        # show or hide xylabel
        if i1==0 and i2==n2-1:
            ax.set_xlabel('peak flux / rms noise', fontdict=font)
        elif i1==0 and i2==int((n2-1)/2):
            ax.set_ylabel('scatter of ($(S_{in} - S_{out})$ / rms_noise)', fontdict=font)
        # 
        # show or hide xyticks
        if i1!=0:
            ax.set_yticks([])
        if i2!=n2-1:
            ax.set_xticks([])

# 
# savefig
for ax in fig.axes: ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y,pos: ('%.0f'%(y))))
for ax in fig.axes: ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
pyplot.savefig('best_fit_function_ecorr.pdf')
print('\nOutput to "best_fit_function_ecorr.pdf"!')
for ax in fig.axes: ax.set_ylim([0.5,10])
for ax in fig.axes: ax.set_yscale('linear')
for ax in fig.axes: ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y,pos: ('%.0f'%(y))))
for ax in fig.axes: ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
pyplot.savefig('best_fit_function_ecorr_zoomed.pdf')
print('\nOutput to "best_fit_function_ecorr_zoomed.pdf"!')
for ax in fig.axes: ax.set_ylim([1.0,2.5])
for ax in fig.axes: ax.set_yscale('linear')
for ax in fig.axes: ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y,pos: ('%.0f'%(y))))
for ax in fig.axes: ax.yaxis.set_minor_formatter(matplotlib.ticker.FuncFormatter(lambda y,pos: ('%.0f'%(y))))
pyplot.savefig('best_fit_function_ecorr_zoomed_zoomed.pdf')
print('\nOutput to "best_fit_function_ecorr_zoomed_zoomed.pdf"!')
# 
# clear
pyplot.clf()






# 
# Output "best_fit_function_ecorr.sm"
# 
#if pcov == []:
#    if os.path.isfile('best_fit_function_ecorr.sm'):
#        os.system('rm best_fit_function_ecorr.sm')
#    print('***********')
#    print('rm best_fit_function_ecorr.sm')
#    sys.exit()
#
#os.system('echo "set a1 = %0.20e"                                                                    > best_fit_function_ecorr.sm'%(popt[0]))
#os.system('echo "set k1 = %0.20e"                                                                   >> best_fit_function_ecorr.sm'%(popt[1]))
#os.system('echo "set n1 = %0.20e"                                                                   >> best_fit_function_ecorr.sm'%(popt[2]))
#os.system('echo "set a2 = %0.20e"                                                                   >> best_fit_function_ecorr.sm'%(popt[3]))
#os.system('echo "set k2 = %0.20e"                                                                   >> best_fit_function_ecorr.sm'%(popt[4]))
#os.system('echo "set n2 = %0.20e"                                                                   >> best_fit_function_ecorr.sm'%(popt[5]))
#os.system('echo "set log_of_scatter_over_noise = (a1 + k1*numpy.log10(x1) + n1*numpy.log10(x1)**2 + k2*x2 + n2*x2**2)"                >> best_fit_function_ecorr.sm')
#os.system('echo "set y_fit = log_of_scatter_over_noise"                                             >> best_fit_function_ecorr.sm')
#os.system('echo ""                                                                                  >> best_fit_function_ecorr.sm')
#print('')
#print('Output to "best_fit_function_ecorr.sm"!')






# 
# Output "best_fit_function_ecorr.py"
# to use the best fit function in another python code, 
# just call it as:
#     from best_fit_function_ecorr import best_fit_function_ecorr
#     y_fit = best_fit_function_ecorr(x1, x2)
# 
if pcov == []:
    if os.path.isfile('best_fit_function_ecorr_via_CurveFit.py'):
        os.system('rm best_fit_function_ecorr_via_CurveFit.py')
    print('***********')
    print('rm best_fit_function_ecorr_via_CurveFit.py')
    #sys.exit()
else:
    os.system('echo "import numpy"                                                                                               > best_fit_function_ecorr_via_CurveFit.py')
    os.system('echo "def best_fit_function_ecorr(x1, x2):"                                                                      >> best_fit_function_ecorr_via_CurveFit.py')
    os.system('echo "    a1 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_CurveFit.py'%(popt[0]))
    os.system('echo "    k1 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_CurveFit.py'%(popt[1]))
    os.system('echo "    n1 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_CurveFit.py'%(popt[2]))
    os.system('echo "    a2 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_CurveFit.py'%(popt[3]))
    os.system('echo "    k2 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_CurveFit.py'%(popt[4]))
    os.system('echo "    n2 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_CurveFit.py'%(popt[5]))
    os.system('echo "    log_of_scatter_over_noise = (a1 + k1*numpy.log10(x1) + n1*numpy.log10(x1)**2 + k2*x2 + n2*x2**2)"                                        >> best_fit_function_ecorr_via_CurveFit.py')
    os.system('echo "    return log_of_scatter_over_noise"                                                                      >> best_fit_function_ecorr_via_CurveFit.py')
    os.system('echo ""                                                                                                          >> best_fit_function_ecorr_via_CurveFit.py')
    print('')
    print('Output to "best_fit_function_ecorr_via_CurveFit.py"!')


# 
# Also output MCMC best-fit
# 
if popt_mean == []:
    if os.path.isfile('best_fit_function_ecorr_via_MCMC.py'):
        os.system('rm best_fit_function_ecorr_via_MCMC.py')
    print('***********')
    print('rm best_fit_function_ecorr_via_MCMC.py')
    #sys.exit()
else:
    os.system('echo "import numpy"                                                                                               > best_fit_function_ecorr_via_MCMC.py')
    os.system('echo "def best_fit_function_ecorr(x1, x2):"                                                                      >> best_fit_function_ecorr_via_MCMC.py')
    os.system('echo "    a1 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_MCMC.py'%(popt_mean[0]))
    os.system('echo "    k1 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_MCMC.py'%(popt_mean[1]))
    os.system('echo "    n1 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_MCMC.py'%(popt_mean[2]))
    os.system('echo "    a2 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_MCMC.py'%(popt_mean[3]))
    os.system('echo "    k2 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_MCMC.py'%(popt_mean[4]))
    os.system('echo "    n2 = %0.20e"                                                                                           >> best_fit_function_ecorr_via_MCMC.py'%(popt_mean[5]))
    os.system('echo "    log_of_scatter_over_noise = (a1 + k1*numpy.log10(x1) + n1*numpy.log10(x1)**2 + k2*x2 + n2*x2**2)"                                        >> best_fit_function_ecorr_via_MCMC.py')
    os.system('echo "    return log_of_scatter_over_noise"                                                                      >> best_fit_function_ecorr_via_MCMC.py')
    os.system('echo ""                                                                                                          >> best_fit_function_ecorr_via_MCMC.py')
    print('')
    print('Output to "best_fit_function_ecorr_via_MCMC.py"!')





# 
# Copy final output python script
# 
if os.path.isfile('best_fit_function_ecorr_via_CurveFit.py'):
    print('cp best_fit_function_ecorr_via_CurveFit.py best_fit_function_ecorr.py')
    os.system('cp best_fit_function_ecorr_via_CurveFit.py best_fit_function_ecorr.py')






















