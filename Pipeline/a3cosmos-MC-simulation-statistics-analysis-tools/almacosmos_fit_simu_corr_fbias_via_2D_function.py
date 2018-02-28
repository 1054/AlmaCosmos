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
#    print('Usage: almacosmos_fit_simu_corr_fbias_via_2D_function.py simu_data_correction_table.txt')
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
data_fbias = data_table.getColumn('cell_rel_median') # 'cell_rel_median'
data_cell_size = data_table.getColumn('cell_size')
y_obs = data_fbias
y_err = numpy.sqrt(10.0/data_cell_size) * y_obs


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
col_names = ['x1 (S_peak/rms_noise)','x2 (Maj_convol/Maj_beam)','median (S_in-S_out)/S_in','1 / cell size']
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
# Fit function -- a0 * exp(a1 * x1) * exp(a2 * x2)
#              -- a0=-2000, a1=-1, a2=0
def my_func((x1,x2), a1, k1, n1, a2, k2, n2): 
    #return a0 * (numpy.exp(a1*numpy.log10((x1/k1)**n1))) * (numpy.exp(a2*((x2/k2)**n2)))
    #return a0 * numpy.exp( -numpy.log10((x1/k1)**n1) ) * (a1 + a2*(x2/k2) + n2*(x2/k2)**2 + c2*(x2/k2)**3)
    #return a1a*((numpy.log10(x1)/k1a)**n1a) + a1b*((numpy.log10(x1)/k1b)**n1b) * (a2 + (x2/k2)**n2)
    # 
    #f1 = -a1 * numpy.exp( -numpy.log10(x1/k1) * n1 )
    # 
    # construct (1/x-1/x^2) * 1/(1-exp(-x))
    # the first item likes an energy field versus radial curve
    # while the second item provides an additional curvetting
    fx1k1 = numpy.log10(x1/k1) * (1+n1*x2)
    fx1k2 = numpy.log10(x1/k2) * (1+n2*x2)
    f1 = a1 * ( 1.0/fx1k1 - 1.0/fx1k1**2 ) * a2 / ( 1.0 - numpy.exp( -fx1k2 ) )
    #f2 = numpy.array(list(map(lambda x: a2 if (x>=0.0) &(x<2.0) else \
    #                                    k2 if (x>=2.0) &(x<2.5) else \
    #                                    n2 if (x>=2.5) &(x<4.5) else \
    #                                    n2, x2)))
    #f2 = (1 + n2*x2)
    #f2 = (1 + a2*x2 + n2/x2)
    # 
    fsmask = (x1<k1) | (x1<k2)
    fs = f1
    fs[fsmask] = numpy.nan
    # 
    return fs


# 
# Initial guess
# 
initial_guess = (1.0, 1.0, 0.1, 1.0, 1.0, 0.1)
#initial_guess = (-0.06010105,   0.13198369, -14.45676735,  -0.33198832, 0.85017692,  -0.39402407,  -0.6517596)
#bound_range = ([-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf,-numpy.inf],
#               [       0.0,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf,+numpy.inf])
bound_range = None


# 
# Try fitting
# 
try:
    popt, pcov = scipy.optimize.curve_fit(my_func, (x1,x2), y_obs, sigma=y_err, p0=initial_guess, maxfev=10000) #, bounds=bound_range, 
except Exception,e:
    print str(e)
    popt = initial_guess
    pcov = []
    try:
        print('Retry fitting')
        initial_guess = (1.0, 10.0, 0.1, 1.0, 1.0, 0.1)
        popt, pcov = scipy.optimize.curve_fit(my_func, (x1,x2), y_obs, sigma=y_err, p0=initial_guess, maxfev=10000) #, bounds=bound_range, 
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
    def M_model(x1, x2, y_obs, y_err):
        # 
        # priors
        a1 = pymc.Uniform('a1',  +0.0, +10.0, value = +1.0)
        k1 = pymc.Uniform('k1',  +0.0, +10.0, value = +3.0)
        n1 = pymc.Uniform('n1', -10.0, +10.0, value = +0.1)
        a2 = pymc.Uniform('a2',  +0.0, +10.0, value = +1.0)
        k2 = pymc.Uniform('k2',  +0.0, +10.0, value = +3.0)
        n2 = pymc.Uniform('n2', -10.0, +10.0, value = +0.1)
        # 
        # M_func = pymc.deterministic(*kwargs)
        @pymc.deterministic(plot=False)
        def M_func(x1=x1, x2=x2, a1=a1, k1=k1, n1=n1, a2=a2, k2=k2, n2=n2):
            #f1 = -a1 * numpy.exp( -numpy.log10(x1/k1) * n1 )
            #f2 = (1 + a2*x2 + n2/x2)
            #f1 = a1 * ( 1.0/numpy.log10(x1/k1/f2) - 1.0/numpy.log10(x1/k1/f2)**2 ) * 1 / ( 1.0 - numpy.exp( -numpy.log10(x1/k2) * n1 ) )
            ##f2 = numpy.array(list(map(lambda x: a2 if (x>=0.0) &(x<2.0) else \
            ##                                    k2 if (x>=2.0) &(x<2.5) else \
            ##                                    n2 if (x>=2.5) &(x<4.5) else \
            ##                                    n2, x2)))
            ##f2 = (1 + a2*x2 + n2/x2)
            ## 
            #fsmask = (x1<k1) | (x1<k2)
            #fs = f1 # * f2
            #fs[fsmask] = numpy.nan
            # 
            return my_func((x1, x2), a1, k1, n1, a2, k2, n2)
        # 
        # likelihood
        y_fit = pymc.Normal("y_fit", mu=M_func, tau=1.0/y_err**2, value=y_obs, observed=True)
        # 
        #print(locals())
        return locals()
    # 
    # MCMC
    MDL = pymc.MCMC(M_model(x1, x1, y_obs, y_err))
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
x2_sparse = numpy.arange(1.0, 4.0+0.5, 0.5)
x1_interval = 0.01
x2_interval = 0.5
#x1_grid, x2_grid = numpy.meshgrid(x1_sparse, x2_sparse)
#x_grid = numpy.column_stack((x1_grid.flatten(),x2_grid.flatten()))






# 
# note that x1_grid is in log, but x1 is not in log. 
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
        ax.set_xlim([0.1,1e3]) # (numpy.power(10,[numpy.min(x1_sparse),numpy.max(x1_sparse)]))
        ax.set_xscale('log')
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
        y_fit = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt )
        plot_line(ax, numpy.power(10,x1_sparse), y_fit, color='red')
        if do_MCMC:
            y_fit_mean = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt_mean )
            y_fit_min = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt_min )
            y_fit_max = my_func( (numpy.power(10,x1_sparse), numpy.power(10,x1_sparse)*0.0+(x2_for_plot)), *popt_max )
            plot_line(ax, numpy.power(10,x1_sparse), y_fit_mean, color='k', lw=2)
            ax.fill_between(numpy.power(10,x1_sparse), y_fit_min, y_fit_max, color='0.5', alpha=0.5)
        # 
        # plot x2
        plot_text(ax, 0, 0.5, r' %0.2f - %0.2f '%(x2_sparse[i2], x2_sparse[i2]+x2_interval), NormalizedCoordinate=True, fontdict=font, verticalalignment='bottom', horizontalalignment='left', zorder=4)
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
        plot_line(ax, 0, 0.0, 1000, 0.0, NormalizedCoordinate=False, color='k', linestyle='dashed', lw=1, zorder=1)
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
pyplot.savefig('best_fit_function_fbias.pdf')
print('\nOutput to "best_fit_function_fbias.pdf"!')
for ax in fig.axes: ax.set_ylim([-2.0,2.0])
pyplot.savefig('best_fit_function_fbias_zoomed.pdf')
print('\nOutput to "best_fit_function_fbias_zoomed.pdf"!')
for ax in fig.axes: ax.set_ylim([-0.05,0.05])
pyplot.savefig('best_fit_function_fbias_zoomed_zoomed.pdf')
print('\nOutput to "best_fit_function_fbias_zoomed_zoomed.pdf"!')
# 
# clear
pyplot.clf()






# 
# Output "best_fit_function_fbias.sm"
# 
#if pcov == []:
#    if os.path.isfile('best_fit_function_fbias.sm'):
#        os.system('rm best_fit_function_fbias.sm')
#    print('***********')
#    print('rm best_fit_function_fbias.sm')
#    sys.exit()
#
#os.system('echo "set a1 = %0.20e"                                                                    > best_fit_function_fbias.sm'%(popt[0]))
#os.system('echo "set k1 = %0.20e"                                                                   >> best_fit_function_fbias.sm'%(popt[1]))
#os.system('echo "set n1 = %0.20e"                                                                   >> best_fit_function_fbias.sm'%(popt[2]))
#os.system('echo "set a2 = %0.20e"                                                                   >> best_fit_function_fbias.sm'%(popt[3]))
#os.system('echo "set k2 = %0.20e"                                                                   >> best_fit_function_fbias.sm'%(popt[4]))
#os.system('echo "set n2 = %0.20e"                                                                   >> best_fit_function_fbias.sm'%(popt[5]))
#os.system('echo "set fx1k1 = lg(x1/k1) * (1+n1*x2)"                                                 >> best_fit_function_fbias.sm')
#os.system('echo "set fx1k2 = lg(x1/k2) * (1+n2*x2)"                                                 >> best_fit_function_fbias.sm')
#os.system('echo "set f1 = a1 * ( 1.0/fx1k1 - 1.0/fx1k1**2 ) * a2 / ( 1.0 - exp( -fx1k2 ) )"         >> best_fit_function_fbias.sm')
#os.system('echo "set y_fit = (x1<k1 || x1<k2) ? -99 : f1"                                           >> best_fit_function_fbias.sm')
#os.system('echo ""                                                                                  >> best_fit_function_fbias.sm')
#print('')
#print('Output to "best_fit_function_fbias.sm"!')






# 
# Output "best_fit_function_fbias_via_CurveFit.py"
# to use the best fit function in another python code, 
# just call it as:
#     from best_fit_function_fbias import best_fit_function_fbias
#     y_fit = best_fit_function_fbias(x1, x2)
# 
if pcov == []:
    if os.path.isfile('best_fit_function_fbias_via_CurveFit.py'):
        os.system('rm best_fit_function_fbias_via_CurveFit.py')
    print('***********')
    print('rm best_fit_function_fbias_via_CurveFit.py')
    #sys.exit()
else:
    os.system('echo "import numpy"                                                                      > best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "def best_fit_function_fbias(x1, x2):"                                             >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    a1 = %0.20e"                                                                  >> best_fit_function_fbias_via_CurveFit.py'%(popt[0]))
    os.system('echo "    k1 = %0.20e"                                                                  >> best_fit_function_fbias_via_CurveFit.py'%(popt[1]))
    os.system('echo "    n1 = %0.20e"                                                                  >> best_fit_function_fbias_via_CurveFit.py'%(popt[2]))
    os.system('echo "    a2 = %0.20e"                                                                  >> best_fit_function_fbias_via_CurveFit.py'%(popt[3]))
    os.system('echo "    k2 = %0.20e"                                                                  >> best_fit_function_fbias_via_CurveFit.py'%(popt[4]))
    os.system('echo "    n2 = %0.20e"                                                                  >> best_fit_function_fbias_via_CurveFit.py'%(popt[5]))
    os.system('echo "    fx1k1 = numpy.log10(x1/k1) * (1+n1*x2)"                                       >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    fx1k2 = numpy.log10(x1/k2) * (1+n2*x2)"                                       >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    f1 = a1 * ( 1.0/fx1k1 - 1.0/fx1k1**2 ) * a2 / ( 1.0 - numpy.exp( -fx1k2 ) )"  >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    fsmask = (x1<k1) | (x1<k2)"                                                   >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    fs = f1"                                                                      >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    fs[fsmask] = numpy.nan"                                                       >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo "    return fs"                                                                    >> best_fit_function_fbias_via_CurveFit.py')
    os.system('echo ""                                                                                 >> best_fit_function_fbias_via_CurveFit.py')
    print('')
    print('Output to "best_fit_function_fbias_via_CurveFit.py"!')


# 
# Also output MCMC best-fit
# 
if popt_mean == []:
    if os.path.isfile('best_fit_function_fbias_via_MCMC.py'):
        os.system('rm best_fit_function_fbias_via_MCMC.py')
    print('***********')
    print('rm best_fit_function_fbias_via_MCMC.py')
    #sys.exit()
else:
    os.system('echo "import numpy"                                                                      > best_fit_function_fbias_via_MCMC.py')
    os.system('echo "def best_fit_function_fbias(x1, x2):"                                             >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    a1 = %0.20e"                                                                  >> best_fit_function_fbias_via_MCMC.py'%(popt_mean[0]))
    os.system('echo "    k1 = %0.20e"                                                                  >> best_fit_function_fbias_via_MCMC.py'%(popt_mean[1]))
    os.system('echo "    n1 = %0.20e"                                                                  >> best_fit_function_fbias_via_MCMC.py'%(popt_mean[2]))
    os.system('echo "    a2 = %0.20e"                                                                  >> best_fit_function_fbias_via_MCMC.py'%(popt_mean[3]))
    os.system('echo "    k2 = %0.20e"                                                                  >> best_fit_function_fbias_via_MCMC.py'%(popt_mean[4]))
    os.system('echo "    n2 = %0.20e"                                                                  >> best_fit_function_fbias_via_MCMC.py'%(popt_mean[5]))
    os.system('echo "    fx1k1 = numpy.log10(x1/k1) * (1+n1*x2)"                                       >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    fx1k2 = numpy.log10(x1/k2) * (1+n2*x2)"                                       >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    f1 = a1 * ( 1.0/fx1k1 - 1.0/fx1k1**2 ) * a2 / ( 1.0 - numpy.exp( -fx1k2 ) )"  >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    fsmask = (x1<k1) | (x1<k2)"                                                   >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    fs = f1"                                                                      >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    fs[fsmask] = numpy.nan"                                                       >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo "    return fs"                                                                    >> best_fit_function_fbias_via_MCMC.py')
    os.system('echo ""                                                                                 >> best_fit_function_fbias_via_MCMC.py')
    print('')
    print('Output to "best_fit_function_fbias_via_MCMC.py"!')





# 
# Copy final output python script
# 
if os.path.isfile('best_fit_function_fbias_via_CurveFit.py'):
    print('cp best_fit_function_fbias_via_CurveFit.py best_fit_function_ecorr.py')
    os.system('cp best_fit_function_fbias_via_CurveFit.py best_fit_function_fbias.py')






















