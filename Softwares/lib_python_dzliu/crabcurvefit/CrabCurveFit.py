#!/usr/bin/env python2.7
# 

#####################################
# 
# A bunch of function fitting
# 
#   Last update: 
#            20180102, initialized
# 
#####################################

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("scipy")
pkg_resources.require("astropy")

import numpy
import scipy
from scipy import optimize, interpolate
from pprint import pprint



# | X
# | X
# |  X
# |    X
# +-----X---------------------------XXXXXXXXXXXXXX--
# |      XXX                XXXXXXXX
# |         X          XXXXX
# |          XXX    XXXX
# |            XXXXX
# |
# |
# | http://asciiflow.com/
 
def fit_func_gravity_energy_field_func(x1, a1a, a1b, k1a, k1b, n1a, n1b): 
    y = a1a*((x1/k1a)**n1a) + a1b*((x1/k1b)**n1b)
    return y

def fit_func_gravity_energy_field(x, y_obs, y_err=None, initial_guess=None):
    if initial_guess is None:
        initial_guess = (-1.0,1.0,1.0,1.0,-1.0,-2.0) # a1a, a1b, k1a, k1b, n1a, n1b
    # 
    boundary = ( [-numpy.inf, 0, 0, 0, -numpy.inf, -numpy.inf], 
                 [0, +numpy.inf, +numpy.inf, +numpy.inf, -1, -2] )
    # 
    valid = False
    try:
        print('Fitting ...')
        if y_err is None:
            popt, pcov = scipy.optimize.curve_fit(fit_func_gravity_energy_field_func, x, y_obs, p0=initial_guess, bounds=boundary, max_nfev=100000)
        else:
            popt, pcov = scipy.optimize.curve_fit(fit_func_gravity_energy_field_func, x, y_obs, sigma=y_err, p0=initial_guess, bounds=boundary, max_nfev=100000)
        valid = True
    except Exception,e:
        print str(e)
        popt = initial_guess
        pcov = []
        try:
            print('Retry fitting ...')
            initial_guess = (-1.0,1.0,1.0,1.0,-1.0,-2.0) # a1a, a1b, k1a, k1b, n1a, n1b
            if y_err is None:
                popt, pcov = scipy.optimize.curve_fit(fit_func_gravity_energy_field_func, x, y_obs, sigma=y_err, p0=initial_guess, bounds=boundary)
            else:
                popt, pcov = scipy.optimize.curve_fit(fit_func_gravity_energy_field_func, x, y_obs, p0=initial_guess, bounds=boundary)
            valid = True
        except Exception,e:
            print str(e)
            popt = initial_guess
            pcov = []
    # 
    # check pcov
    #if not numpy.isfinite(pcov).all():
    #    valid = False
    # 
    y_fit = fit_func_gravity_energy_field_func(x, *popt)
    # 
    #print(popt)
    param = {}
    param['a1a'] = popt[0]
    param['a1b'] = popt[1]
    param['k1a'] = popt[2]
    param['k1b'] = popt[3]
    param['n1a'] = popt[4]
    param['n1b'] = popt[5]
    #pprint(param)
    #pprint(pcov)
    # 
    p_fit = {'x':x.tolist(), 'y_obs':y_obs.tolist(), 'y_fit':y_fit.tolist(), 'param':param, 'valid':valid, 
            'popt':popt.tolist(), 'pcov':pcov.tolist(), 'func':'fit_func_gravity_energy_field_func'}
    # 
    return p_fit






# +
# |                         XXX
# |                        X
# |                     XXX
# |                    XX
# |                  XX
# |                XXX
# |               XX
# |              XX
# |              X
# |             X
# |             X
# |           XX
# |          XX
# +---------XX--------------------+
# |        XX
# |      XX
# |    XX
# |XXX
# |
# | http://asciiflow.com/

def fit_func_polynomial_xylog_func(x, fit_param): 
    fit_model = numpy.poly1d(fit_param)
    return numpy.power(10,fit_model(numpy.log10(x)))

def fit_func_polynomial_xylog(x, y_obs, y_err=None, initial_guess=None, fit_order=3):
    #fit_order = 3
    fit_param = numpy.polyfit(numpy.log10(x), numpy.log10(y_obs), fit_order)
    fit_model = numpy.poly1d(fit_param)
    fit_curve = fit_model(numpy.log10(x))
    y_fit = numpy.power(10,fit_curve)
    valid = True
    # 
    param = {}
    param['a0'] = fit_param[fit_order]
    for iparam in range(fit_order):
            param['a%d'%(iparam+1)] = fit_param[fit_order-iparam-1]
    # 
    p_fit = {'x':x.tolist(), 'y_obs':y_obs.tolist(), 'y_fit':y_fit.tolist(), 'param':param, 'valid':valid, 
            'fit_param':fit_param.tolist(), 'func':'numpy.poly1d(fit_param)'}
    # 
    return p_fit












def fit_func_spoon_shape_45_degree_func(x, *fit_param): 
    #fit_model = numpy.poly1d(fit_param)
    #fit_curve = fit_model(numpy.log10(x)) * (1+numpy.exp(-numpy.log10(x)))
    ##fit_curve = 0.0 # fit_param[len(fit_param)-1]
    ##for i in range(len(fit_param)-1):
    ##    fit_model = fit_param[i] / numpy.power(numpy.log10(x), len(fit_param)-1-i)
    ##    fit_curve = fit_curve + fit_model
    ##fit_curve = fit_curve + numpy.log10(x)
    ###fit_curve = numpy.log10(x) / (1 + fit_param[0]*numpy.exp(-numpy.log10(x/fit_param[1]))) * (1 + fit_param[2]*numpy.power(numpy.log10(x),fit_param[3]))
    ######a1a = fit_param[0]
    ######a1b = fit_param[1]
    ######k1a = fit_param[2]
    ######k1b = fit_param[3]
    ######n1a = -1.0 # fit_param[4]
    ######n1b = -2.0 # fit_param[5]
    ######x1 = numpy.log10(x)
    ######y = a1a*((x1/k1a)**n1a) + a1b*((x1/k1b)**n1b)
    ######fit_curve = x1 * y
    # 
    #[ok]# y = x * (1 + fit_param[1]*numpy.exp(-x/fit_param[0]))
    a0 = fit_param[1]
    a1 = fit_param[0]
    y = x + (a0/numpy.power(x,a1))
    return y

def fit_func_spoon_shape_45_degree_xylog_func(x, *fit_param): 
    return numpy.power(10,fit_func_spoon_shape_45_degree_func(numpy.log10(x),*fit_param))

def fit_func_spoon_shape_45_degree_xylog(x, y_obs, y_err=None, initial_guess=None):
    if initial_guess is None:
        #initial_guess = (0.0,0.0,1.0,1.0) # fit_order = 3
        ##initial_guess = (0.0,1.0,1.0) # fit_order = 2
        #initial_guess = (1.0,1.0,-1.0,-1.0)
        #initial_guess = (-1.0,1.0,1.0,1.0) # a1a, a1b, k1a, k1b, n1a, n1b
        initial_guess = (1.0,1.0)
    # 
    valid = False
    try:
        print('Fitting ...')
        if y_err is None:
            popt, pcov = scipy.optimize.curve_fit(fit_func_spoon_shape_45_degree_func, numpy.log10(x), numpy.log10(y_obs), p0=initial_guess, maxfev=100000)
        else:
            popt, pcov = scipy.optimize.curve_fit(fit_func_spoon_shape_45_degree_func, numpy.log10(x), numpy.log10(y_obs), sigma=y_err/y_obs, p0=initial_guess, maxfev=100000)
        valid = True
    except Exception,e:
        print str(e)
        popt = initial_guess
        pcov = []
    # 
    y_fit = fit_func_spoon_shape_45_degree_xylog_func(x, *popt)
    # 
    #print(popt)
    fit_param = popt
    fit_order = len(initial_guess)-1
    param = {}
    param['a0'] = fit_param[fit_order]
    for iparam in range(fit_order):
            param['a%d'%(iparam+1)] = fit_param[fit_order-iparam-1]
    #pprint(param)
    #pprint(pcov)
    # 
    p_fit = {'x':x.tolist(), 'y_obs':y_obs.tolist(), 'y_fit':y_fit.tolist(), 'param':param, 'valid':valid, 
            'fit_param':fit_param.tolist(), 'popt':popt.tolist(), 'pcov':pcov.tolist(), 'func':'fit_func_gravity_energy_field_func'}
    # 
    return p_fit


















