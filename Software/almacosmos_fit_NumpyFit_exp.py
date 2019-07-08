#!/usr/bin/env python2.7
# 

import os, sys
import numpy as np
import astropy
import astropy.io.ascii as asciitable

if os.path.isfile("datatable_for_NumpyFit.txt"):
    data = asciitable.read("datatable_for_NumpyFit.txt")
    fit_x = [t['x'] for t in data if (t['err']<0.5)]    # error in log
    fit_y = [t['y'] for t in data if (t['err']<0.5)]    # error in log
    fit_err = [t['err'] for t in data if (t['err']<0.5)]    # error in log
    fit_x = [t for t in fit_x if (fit_err>0)]
    fit_y = [t for t in fit_y if (fit_err>0)]
    fit_err = [t for t in fit_err if (fit_err>0)]
    print(fit_x, fit_y)
    fit_order = 3
    fit_param = np.polyfit(fit_x, fit_y, fit_order)
    fit_model = np.poly1d(fit_param)
    fit_curve = fit_model(fit_x)
    print(fit_x, fit_curve)
    asciitable.write((fit_x, fit_curve), "datatable_for_NumpyFit_fitted_order_%d.txt"%(fit_order), Writer=asciitable.FixedWidthTwoLine, overwrite=True)
    asciitable.write((fit_param), "datatable_for_NumpyFit_fitted_order_%d_params.txt"%(fit_order), Writer=asciitable.FixedWidthTwoLine, overwrite=True)


