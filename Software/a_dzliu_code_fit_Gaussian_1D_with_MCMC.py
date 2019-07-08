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

# 
# Import python packages
import numpy
import pysd
import pymc
import pandas
import astropy
import scipy.optimize
from matplotlib import pyplot
from pprint import pprint


# 
# Read user input
if len(sys.argv)>1:
    input_data_table = sys.argv[1]
else:
    input_data_table = 'datatable_flux_1_2.txt'

if len(sys.argv)>2:
    output_figure_name = sys.argv[2]
else:
    output_figure_name = 'p_mcmcfit.pdf'


# 
# Read input data
import astropy.io.ascii as asciitable
data_table = asciitable.read(input_data_table) # see 'a_dzliu_code_plot_comparison_of_flux_between_superdeblend_and_ALMA_4.sh'
bin_centres = numpy.arange(-4.0,4.0,0.25) # 20180612: chaned bin step from 0.2 to 0.25.
bin_hists, bin_edges = numpy.histogram(data_table['normdiff_f850'], bins=bin_centres)
bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2.0
print(numpy.column_stack((bin_edges[0:-1],bin_edges[1:],bin_hists)))

# 
# Plot once
y_obs = bin_hists
y_err = bin_hists*0.0+0.05
x = bin_centres

# 
# Prepare fitting function 
def my_model(x, y_obs): 
    # priors
    p_A = pymc.Uniform('p_A', 0, 100, value=25)
    p_mu = pymc.Uniform('p_mu', -1.0, 1.0, value=0.12)
    p_sigma = pymc.Uniform('p_sigma', 0.0, 2.0, value=1.0)
    # model
    @pymc.deterministic(plot=False)
    def my_func(x=x, p_A=p_A, p_mu=p_mu, p_sigma=p_sigma):
        return p_A * numpy.exp(-(x-p_mu)**2/(2.0*(p_sigma)**2))
    # likelihood
    y = pymc.Normal('y', mu=my_func, tau=1.0/y_err**2, value=y_obs, observed=True)
    #print(locals())
    return locals()

# 
# Prepare fitting function 
def my_model_sigma_one(x, y_obs): 
    # priors
    p_A = pymc.Uniform('p_A', 0, 100, value=25)
    p_mu = pymc.Uniform('p_mu', -1.0, 1.0, value=0.12)
    # model
    @pymc.deterministic(plot=False)
    def my_func_sigma_one(x=x, p_A=p_A, p_mu=p_mu):
        return p_A * numpy.exp(-(x-p_mu)**2/(2.0*(1.0)**2))
    # likelihood
    y = pymc.Normal('y', mu=my_func_sigma_one, tau=1.0/y_err**2, value=y_obs, observed=True)
    #print(locals())
    return locals()

# 
# MCMC
MDL = pymc.MCMC(my_model(x, y_obs))
MDL.sample(1e4)
pprint(MDL.stats())

MDL = pymc.MCMC(my_model_sigma_one(x, y_obs))
MDL.sample(1e4)
pprint(MDL.stats())

# extract and plot results
y_min = MDL.stats()['my_func_sigma_one']['quantiles'][2.5]
y_max = MDL.stats()['my_func_sigma_one']['quantiles'][97.5]
y_fit = MDL.stats()['my_func_sigma_one']['mean']
#pyplot.plot(x, y_obs, color='r', marker='.', ls='None', label='Observed')
#pyplot.plot(x, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
pyplot.bar(x, y_obs, width=0.25, color='r', edgecolor='k', label='Observed')
pyplot.plot(x, y_fit, 'k', marker='+', ls='solid', ms=5, mew=2, label='Fit')
pyplot.fill_between(x, y_min, y_max, color='0.5', alpha=0.5)
pyplot.legend()
pyplot.savefig(output_figure_name)

pymc.Matplot.plot(MDL)
#pyplot.show(block=True)



# See 
# http://pysd-cookbook.readthedocs.io/en/latest/analyses/fitting/MCMC_for_fitting_models.html


