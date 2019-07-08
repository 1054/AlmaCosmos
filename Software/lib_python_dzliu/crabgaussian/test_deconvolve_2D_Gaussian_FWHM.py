#!/usr/bin/env python
# 

import os, sys

sys.path.append(os.path.dirname(sys.argv[0]))

from CrabGaussian import *

deconvolve_2D_Gaussian_FWHM([37.202131, 30.413801, 180.00000], [30, 5, 0.0])


# 
# Expecting:
# 
# Input intrinsic Maj FWHM =      30
# Input intrinsic Min FWHM =      22
# Input intrinsic PA =     -90.0000
# Input PSF Maj FWHM =      30
# Input PSF Min FWHM =       5
# Input PSF PA =      0.00000
# Fitted convolved Maj FWHM =       37.202131
# Fitted convolved Min FWHM =       30.413801
# Fitted convolved PA =       180.00000
# 
# Fitted intri+PSF Maj^2+Min^2 =     2309
# Fitted convolved Maj^2+Min^2 =        2308.9978




def deconv(gaus_bm, gaus_c):
    """ Deconvolves gaus_bm from gaus_c to give gaus_dc.
        Stolen shamelessly from aips DECONV.FOR.
        All PA is in degrees."""
    from math import pi, cos, sin, atan, sqrt

    rad = 180.0/pi
    gaus_d = [0.0, 0.0, 0.0]

    phi_c = gaus_c[2]+900.0 % 180
    phi_bm = gaus_bm[2]+900.0 % 180
    maj2_bm = gaus_bm[0]*gaus_bm[0]; min2_bm = gaus_bm[1]*gaus_bm[1]
    maj2_c = gaus_c[0]*gaus_c[0]; min2_c = gaus_c[1]*gaus_c[1]
    theta=2.0*(phi_c-phi_bm)/rad
    cost = cos(theta)
    sint = sin(theta)

    rhoc = (maj2_c-min2_c)*cost-(maj2_bm-min2_bm)
    if rhoc == 0.0:
      sigic = 0.0
      rhoa = 0.0
    else:
      sigic = atan((maj2_c-min2_c)*sint/rhoc)   # in radians
      rhoa = ((maj2_bm-min2_bm)-(maj2_c-min2_c)*cost)/(2.0*cos(sigic))

    gaus_d[2] = sigic*rad/2.0+phi_bm
    dumr = ((maj2_c+min2_c)-(maj2_bm+min2_bm))/2.0
    gaus_d[0] = dumr-rhoa
    gaus_d[1] = dumr+rhoa
    error = 0
    if gaus_d[0] < 0.0: error += 1
    if gaus_d[1] < 0.0: error += 1

    gaus_d[0] = max(0.0,gaus_d[0])
    gaus_d[1] = max(0.0,gaus_d[1])
    gaus_d[0] = sqrt(abs(gaus_d[0]))
    gaus_d[1] = sqrt(abs(gaus_d[1]))
    if gaus_d[0] < gaus_d[1]:
      sint = gaus_d[0]
      gaus_d[0] = gaus_d[1]
      gaus_d[1] = sint
      gaus_d[2] = gaus_d[2]+90.0

    gaus_d[2] = gaus_d[2]+900.0 % 180
    if gaus_d[0] == 0.0:
      gaus_d[2] = 0.0
    else:
      if gaus_d[1] == 0.0:
        if (abs(gaus_d[2]-phi_c) > 45.0) and (abs(gaus_d[2]-phi_c) < 135.0):
          gaus_d[2] = gaus_d[2]+450.0 % 180
    # 
    print(gaus_d)
    return gaus_d



deconv([30, 5, 0.0], [37.202131, 30.413801, 180.0])








convolve_2D_Gaussian_FWHM([30.0,22.0,-90.0], [30, 5, 0.0])








