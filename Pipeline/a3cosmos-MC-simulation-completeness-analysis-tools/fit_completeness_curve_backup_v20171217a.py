#!/usr/bin/env python
# 

import os, sys
import numpy
import astropy
import astropy.io.ascii as asciitable

import numpy.polynomial.polynomial as poly # https://stackoverflow.com/questions/18767523/fitting-data-with-numpy

from pprint import pprint

datatable = asciitable.read('datatable_MC_sim_completeness.txt')
deg = 5
xin = numpy.log10(datatable['snr_value_cumulative']) # TODO: note that x is in log(S/N), while y is in linear
yin = (1.0-datatable['fake_rate_cumulative']) # TODO: y is 1-fake_rate_cumulative
asciitable.write({'xin': xin, 'yin': yin}, sys.stdout, Writer=asciitable.FixedWidthTwoLine)


# 
# Fit the data points with polynominal
# 
#par = numpy.polyfit(xin, yin, deg)
#par = poly.polyfit(xin, yin, deg) # https://stackoverflow.com/questions/18767523/fitting-data-with-numpy



# 
# Fit the data points with Sigmoid function
# 




os.system('echo "# $(date +\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\")" > %s'%('function_MC_sim_completeness.txt'))

#os.system('echo "set a%d = %0.20e" >> %s'%(0, par[deg], 'function_MC_sim_completeness.txt'))
#
#for i in range(deg):
#    os.system('echo "set a%d = %0.20e" >> %s'%(i+1, par[deg-(i+1)], 'function_MC_sim_completeness.txt'))
#
#func_str = 'set y_fit = a0'
#for i in range(deg):
#    func_str = func_str + ' + a%d * x**%d'%(i+1,i+1)

os.system('echo "set a%d = %0.20e" >> %s'%(0, par[0], 'function_MC_sim_completeness.txt'))

for i in range(deg):
    os.system('echo "set a%d = %0.20e" >> %s'%(i+1, par[(i+1)], 'function_MC_sim_completeness.txt'))

func_str = 'set y_fit = a0'
for i in range(deg):
    func_str = func_str + ' + a%d * x**%d'%(i+1,i+1)

os.system('echo "%s" >> %s'%(func_str, 'function_MC_sim_completeness.txt'))

#func_model = numpy.poly1d(par)
func_model = poly.Polynomial(par)

xfit = numpy.linspace(numpy.min(xin), numpy.max(xin), 1000)
yfit = func_model(xfit)

asciitable.write({'xfit': xfit, 'yfit': yfit}, 'function_MC_sim_completeness.xyfit.txt', Writer=asciitable.FixedWidthTwoLine, overwrite=True)


