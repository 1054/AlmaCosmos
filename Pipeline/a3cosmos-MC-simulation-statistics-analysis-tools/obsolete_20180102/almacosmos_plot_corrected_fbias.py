#!/usr/bin/env python2.7
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")
pkg_resources.require("scipy")

import os, sys

if len(sys.argv) <= 0:
    print('Usage: almacosmos_plot_corrected_fbias.py simu_data_correction_table.txt')
    sys.exit()


# 
# Read input arguments
if not os.path.isfile('datatable_applied_correction_fbias.txt'):
    print('Error! "datatable_applied_correction_fbias.txt" was not found!')
    sys.exit()

import astropy.io.ascii as asciitable
data_table = asciitable.read('datatable_applied_correction_fbias.txt')
#print(data_table)




# 
# load CrabPlot
#sys.path.append(os.path.dirname(sys.argv[0])+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
#from CrabPlot import *
sys.path.insert(1,'/Users/dzliu/Softwares/Python/lib/crab/crabplot')
from CrabPlot import *


crab_plot = CrabPlot()
data_color = crab_plot.get_color_by_value(data_table['x2'])
crab_plot.plot_xy(data_table['x1'],data_table['fbias_from_function'], color = data_color, ylog=True)
crab_plot.show()



















