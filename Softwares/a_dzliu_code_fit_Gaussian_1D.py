#!/usr/bin/env python
# 
# -- from http://stackoverflow.com/questions/11507028/fit-a-gaussian-function
# 


import os, sys, numpy
from scipy.optimize import curve_fit


# Usage
if len(sys.argv) <= 1:
    print('Usage: ')
    print('Usage: a_dzliu_code_fit_Gaussian_1D.py datatable_with_two_columns.txt output_basename')
    sys.exit()




# Define model function to be used to fit to the data above:
def Func_Gaussian_1D(x, *p):
    A, mu, sigma = p
    return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))

def Func_Gaussian_1D_sigma_one(x, *p):
    A, mu = p
    return A*numpy.exp(-(x-mu)**2/(2.*1.0**2))


# Do Gaussian 1D fitting
def fit_Gaussian_1D(x, y, *p): 
    
    # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
    if p:
        p0 = p
    else:
        p0 = [numpy.max(y), numpy.mean(x), numpy.std(x)]
    
    # Check input, x is BinEdges (or BinCentres), y is BinHistogram
    if len(x) == len(y)+1:
        bin_edges = x
        bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    else:
        bin_centres = x
    
    fit_params, fit_matrix = curve_fit(Func_Gaussian_1D, bin_centres, y, p0=p0)
    
    # Get the fitted curve
    fit_curve = Func_Gaussian_1D(bin_centres, *fit_params)
    
    # Fix negative sigma problem
    fit_params[2] = numpy.sqrt(fit_params[2]**2)
    
    # Return the best-fit curve and parameters
    return fit_curve, {'A':fit_params[0], 'mu':fit_params[1], 'sigma':fit_params[2]}


# Do Gaussian 1D fitting
def fit_Gaussian_1D_sigma_one(x, y, *p): 
    
    # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
    if p:
        p0 = p
    else:
        p0 = [numpy.max(y), numpy.mean(x)]
    
    # Check input, x is BinEdges (or BinCentres), y is BinHistogram
    if len(x) == len(y)+1:
        bin_edges = x
        bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    else:
        bin_centres = x
    
    fit_params, fit_matrix = curve_fit(Func_Gaussian_1D_sigma_one, bin_centres, y, p0=p0)
    
    # Get the fitted curve
    fit_curve = Func_Gaussian_1D_sigma_one(bin_centres, *fit_params)
    
    # Fix negative sigma problem
    #fit_params[2] = numpy.sqrt(fit_params[2]**2)
    
    # Return the best-fit curve and parameters
    return fit_curve, {'A':fit_params[0], 'mu':fit_params[1], 'sigma':1.0}



# 
# Read user input
input_bin_width = 0.1
input_range_min = -4.0
input_range_max = 4.0
input_data_table = ''
output_figure_name = ''
i = 1
while i < len(sys.argv):
    tmp_arg = sys.argv[i].lower().replace('-','')
    if tmp_arg == 'binsize' or tmp_arg == 'binwidth' or tmp_arg == 'width':
        if i+1 < len(sys.argv):
            i=i+1
            input_bin_width = float(sys.argv[i])
    elif tmp_arg == 'min':
        if i+1 < len(sys.argv):
            i=i+1
            input_range_min = float(sys.argv[i])
    elif tmp_arg == 'max':
        if i+1 < len(sys.argv):
            i=i+1
            input_range_max = float(sys.argv[i])
    elif tmp_arg == 'out':
        if i+1 < len(sys.argv):
            i=i+1
            output_figure_name = float(sys.argv[i])
    elif input_data_table == '':
        input_data_table = sys.argv[i]
    elif output_figure_name == '':
        output_figure_name = sys.argv[i]
    i=i+1
if input_data_table == '':
    input_data_table = 'datatable_flux_1_2.txt'
if output_figure_name == '':
    output_figure_name = 'p_curvefit'
if output_figure_name.endswith('.pdf'):
    output_figure_name = output_figure_name[0:-4]


# 
# Read input data
import astropy.io.ascii as asciitable
data_table = asciitable.read(input_data_table) # any data table with two columns 
bin_centres = numpy.arange(input_range_min,input_range_max,input_bin_width) # <TODO> tune the bin width
bin_hists, bin_edges = numpy.histogram(data_table.field(data_table.colnames[0]) - data_table.field(data_table.colnames[1]), bins=bin_centres)
bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2.0
print(numpy.column_stack((bin_edges[0:-1],bin_edges[1:],bin_hists)))


# 
# do the fit
fit_curve, fit_params = fit_Gaussian_1D(bin_centres, bin_hists)
sys.stdout.write('fit_params = ')
print(fit_params)

fit_curve_sigma_one, fit_params_sigma_one = fit_Gaussian_1D_sigma_one(bin_centres, bin_hists)
sys.stdout.write('fit_params_sigma_one = ')
print(fit_params_sigma_one)

with open(output_figure_name+'.params.txt', 'w') as fp:
    # line 1
    fp.write('# \n')
    # line 2
    fp.write('# Fitted 1D Gaussian parameters for data table "%s"\n'%(input_data_table))
    # line 3
    fp.write('# \n')
    # line 4
    fp.write('# %-20s'%('fit_type'))
    for fit_quantity in fit_params:
        fp.write(' %20s'%(fit_quantity))
    fp.write('\n')
    # line 5
    fp.write('  %-20s'%('varied_sigma'))
    for fit_quantity in fit_params:
        fp.write(' %20g'%(fit_params[fit_quantity]))
    fp.write('\n')
    # line 6
    fp.write('  %-20s'%('fixed_sigma_one'))
    for fit_quantity in fit_params_sigma_one:
        fp.write(' %20g'%(fit_params_sigma_one[fit_quantity]))
    fp.write('\n')


import matplotlib.pyplot as plt
plt.bar(bin_centres, bin_hists, width=input_bin_width*0.8, color='r', edgecolor='k', label='$(S_{input\;1}-S_{input\;2})$', lw=0.5)
plt.plot(bin_centres, fit_curve, '-o', color='orange', label='varied sigma')
plt.plot(bin_centres, fit_curve_sigma_one, '-o', color='k', label='fixed sigma = 1')
#plt.yscale('log')
#plt.ylim([0.6,max()])
plt.legend(bbox_to_anchor=(0.0,1.0), loc='upper left', fontsize=12.0, handletextpad=0.20)
plt.savefig(output_figure_name+'.pdf')
#plt.show(block=True)




