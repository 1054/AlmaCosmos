#!/usr/bin/env python2.7
# 
# Aim: 
#      Analyze Monte-Carlo simulation input and output flux
# 
# Input:
#        sys.argv[1]   simulation data table, which should contain at least input flux, output flux, input galaxy size (major axis FWHM), output galaxy size (major axis FWHM). 
# 
# 


import os, sys


# 
# Check user input
# 
if len(sys.argv) <= 1:
    print('Usage: ')
    print('    AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis.py "simu_data_input.txt"')
    print('')
    sys.exit()


# 
# Check python package dependencies
# 
try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy>=1.3")

import matplotlib
import platform
if platform.system() == 'Darwin':
    matplotlib.use('Qt5Agg')
else:
    matplotlib.use('TkAgg') # must before import pyplot
from matplotlib import pyplot
from matplotlib.colors import hex2color, rgb2hex
from matplotlib.patches import Ellipse, Circle, Rectangle, Polygon
from matplotlib.lines import Line2D
from astropy.visualization import astropy_mpl_style
from astropy.visualization import MinMaxInterval, PercentileInterval, AsymmetricPercentileInterval, SqrtStretch, PowerStretch, ImageNormalize
from astropy.wcs import WCS

import astropy.io.ascii as asciitable

import wcsaxes


# 
# Read user input - datatable_filepath
# 
datatable_filepath = sys.argv[1]
if os.dir.isfile(datatable_filepath):
    print('Error! "%s" was not found!'%(datatable_filepath))
    sys.exit()

datatable_content = asciitable.read(datatable_filepath)


for i in range(len(datatable_content.colnames)):
    print(datatable_content.colnames[i])

#datatable_columns = []
#datatable_columns.append('')











