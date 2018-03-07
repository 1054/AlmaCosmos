#!/usr/bin/env python2.7
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")
#pkg_resources.require("scipy")

import os, sys, json, numpy
from copy import copy

if len(sys.argv) <= 6:
    print('Usage: ')
    print('    almacosmos_convert_2D_Gaussian_deconvolved_Maj_Min_PA_to_convolved_values.py Maj Min PA beam_Maj beam_Min beam_PA')
    print('    # Note that Maj, Min, beam_Maj are the deconvolved (intrinsic) source size FWHM in arcsec unit, and beam_Maj, beam_Min are beam FWHM in arcsec unit.')
    print('')
    sys.exit()


# 
# Read input arguments
# 
Maj_out = numpy.array(float(sys.argv[1]))
Min_out = numpy.array(float(sys.argv[2]))
PA_out  = numpy.array(float(sys.argv[3]))
Maj_beam = numpy.array(float(sys.argv[4]))
Min_beam = numpy.array(float(sys.argv[5]))
PA_beam  = numpy.array(float(sys.argv[6]))



# 
# Import python packages
# 
import astropy
import astropy.io.ascii as asciitable
#import scipy.optimize
#import matplotlib
#from matplotlib import pyplot
#from pprint import pprint
#sys.path.insert(1,os.path.dirname(os.path.dirname(sys.argv[0]))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
#from CrabTable import *
#sys.path.insert(1,os.path.dirname(os.path.dirname(sys.argv[0]))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
#from CrabPlot import *
sys.path.insert(1,os.path.dirname(os.path.dirname(sys.argv[0]))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabgaussian')
from CrabGaussian import *
#sys.path.insert(1,os.path.dirname(os.path.dirname(sys.argv[0]))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabcurvefit')
#from CrabCurveFit import *



# 
# Compute
# 
Maj_out_convol, Min_out_convol, PA_out_convol = convolve_2D_Gaussian_Maj_Min_PA(Maj_out, Min_out, PA_out, Maj_beam, Min_beam, PA_beam)
#Maj_out, Min_out, PA_out = deconvolve_2D_Gaussian_Maj_Min_PA(Maj_out_convol, Min_out_convol, PA_out_convol, Maj_beam, Min_beam, PA_beam)



# 
# Print
# 
asciitable.write(numpy.column_stack((Maj_out_convol, Min_out_convol, PA_out_convol)), sys.stdout, 
                 Writer=asciitable.FixedWidth, delimiter='|', bookend=True, 
                 names = ['Maj_out_convolved', 'Min_out_convolved', 'PA_out_convolved'])













