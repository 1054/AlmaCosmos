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
import numpy
import pysd
import pymc
import pandas
import astropy
import astropy.io.ascii as asciitable
import scipy.optimize
from matplotlib import pyplot
from pprint import pprint

datatable = asciitable.read('datatable_MC_sim_completeness_cumulative.txt')
x_in = (datatable['snr_value_cumulative']) # TODO: note that x is in log(S/N), while y is in linear
y_in = (1.0-datatable['fake_rate_cumulative']) # TODO: y is 1-fake_rate_cumulative
y_err = y_in*0.05 # y_in*0.0+0.05 #+ 0.1 # 1.0/(datatable['recovered_count']+datatable['missed_count'])
asciitable.write({'x_in': x_in, 'y_in': y_in}, sys.stdout, Writer=asciitable.FixedWidthTwoLine)



# 
# Fit the data points with Sigmoid function
# 
def my_model(x, y, y_err): 
    # priors
    a = pymc.Uniform('a', -50.0, +50.0, value=1.0)
    b = pymc.Uniform('b', -50.0, +50.0, value=1.0)
    c = pymc.Uniform('c', -50.0, +50.0, value=5.0)
    # model
    @pymc.deterministic(plot=False)
    def my_func(x=x, a=a, b=b, c=c):
        return 1 / (1 + numpy.exp(-numpy.power(b*numpy.log10(x)+c,a)))
    # likelihood
    y = pymc.Normal("y", mu=my_func, tau=1.0/y_err**2, value=y, observed=True)
    #print(locals())
    return locals()


# 
# MCMC
# 
MDL = pymc.MCMC(my_model(x_in, y_in, y_err))
MDL.sample(10000)
pprint(MDL.stats())


# 
# extract and plot results
y_min = MDL.stats()['my_func']['quantiles'][2.5]
y_max = MDL.stats()['my_func']['quantiles'][97.5]
y_fit = MDL.stats()['my_func']['mean']
fig, ax = pyplot.subplots()
ax.plot(x_in, y_in, color='r', marker='.', ls='None', label='Observed')
ax.plot(x_in, y_fit, 'k', marker='+', ls='None', ms=5, mew=2, label='Fit')
ax.fill_between(x_in, y_min, y_max, color='0.5', alpha=0.5)
ax.set_xscale('log')
ax.legend()
fig.tight_layout()
pyplot.savefig('plot_pymc_1.pdf')

pymc.Matplot.plot(MDL)
#pyplot.show(block=True)


# See 
# http://pysd-cookbook.readthedocs.io/en/latest/analyses/fitting/MCMC_for_fitting_models.html


a = MDL.stats()['a']['mean']
b = MDL.stats()['b']['mean']
c = MDL.stats()['c']['mean']

os.system('echo "# $(date +\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\")" > %s'%('function_MC_sim_completeness_cumulative.txt'))

os.system('echo "set a = %0.20e" >> %s'%(a, 'function_MC_sim_completeness_cumulative.txt'))
os.system('echo "set b = %0.20e" >> %s'%(b, 'function_MC_sim_completeness_cumulative.txt'))
os.system('echo "set c = %0.20e" >> %s'%(c, 'function_MC_sim_completeness_cumulative.txt'))
os.system('echo "set y_fit = 1 / (1 + exp(-(b*lg(x)+c)**a))" >> %s'%('function_MC_sim_completeness_cumulative.txt'))

x_fit = numpy.linspace(numpy.min(x_in), numpy.max(x_in), 1000)
y_fit = 1 / (1 + a*numpy.exp(-(b*x_fit+c)))

asciitable.write({'x_fit': x_fit, 'y_fit': y_fit}, 'function_MC_sim_completeness_cumulative.xyfit.txt', Writer=asciitable.FixedWidthTwoLine, overwrite=True)


