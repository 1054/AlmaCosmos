#!/usr/bin/python
# -*- coding: utf-8 -*-
# 

################################
# 
# 
################################

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy>=1.3")

import os
import sys
import re
import math
import numpy
import astropy
from astropy.io import ascii as asciitable
from astropy.io import fits
from astropy.wcs import WCS
from pprint import pprint
from copy import copy
from astropy.utils.exceptions import AstropyWarning, AstropyUserWarning
import warnings
#warnings.simplefilter('ignore', category=AstropyUserWarning)
warnings.simplefilter('ignore', category=AstropyWarning)












class CrabImage(object):
    # 
    def __init__(self, FitsImageFile, FitsImageExtension=0):
        self.FitsImageFile = FitsImageFile
        print("Reading Fits Image: %s"%(self.FitsImageFile))
        self.FitsStruct = fits.open(self.FitsImageFile)
        self.Image = []
        self.Header = []
        self.Dimension = []
        self.WCS = []
        self.PixScale = [numpy.nan, numpy.nan]
        self.World = {}
        #print FitsImagePointer.info()
        # 
        ImageCount = 0
        for ImageId in range(len(self.FitsStruct)):
            if type(self.FitsStruct[ImageId]) is astropy.io.fits.hdu.image.PrimaryHDU:
                if ImageCount == FitsImageExtension:
                    # 
                    # read fits image and header
                    self.Image = self.FitsStruct[ImageId].data
                    self.Header = self.FitsStruct[ImageId].header
                    # 
                    # fix NAXIS to 2 if NAXIS>2, this is useful for VLA images
                    if(self.Header['NAXIS']>2):
                        while(self.Header['NAXIS']>2):
                            self.Image = self.Image[0]
                            for TempStr in ('NAXIS','CTYPE','CRVAL','CRPIX','CDELT','CUNIT','CROTA'):
                                TempKey = '%s%d'%(TempStr,self.Header['NAXIS'])
                                if TempKey in self.Header:
                                    del self.Header[TempKey]
                                    #print("del %s"%(TempKey))
                            for TempInt in range(int(self.Header['NAXIS'])):
                                TempKey = 'PC%02d_%02d'%(TempInt+1,self.Header['NAXIS'])
                                if TempKey in self.Header:
                                    del self.Header[TempKey]
                                    #print("del %s"%(TempKey))
                                TempKey = 'PC%02d_%02d'%(self.Header['NAXIS'],TempInt+1)
                                if TempKey in self.Header:
                                    del self.Header[TempKey]
                                    #print("del %s"%(TempKey))
                            self.Header['NAXIS'] = self.Header['NAXIS']-1
                        for TempStr in ('NAXIS','CTYPE','CRVAL','CRPIX','CDELT','CUNIT','CROTA'):
                            for TempInt in (3,4):
                                TempKey = '%s%d'%(TempStr,TempInt)
                                if TempKey in self.Header:
                                    del self.Header[TempKey]
                    # 
                    self.Dimension = [ numpy.int(self.Header['NAXIS1']), numpy.int(self.Header['NAXIS2']) ]
                    self.WCS = WCS(self.Header)
                    self.PixScale = astropy.wcs.utils.proj_plane_pixel_scales(self.WCS) * 3600.0 # arcsec
                    # 
                    ImageCount = ImageCount + 1
                    break
                else:
                    ImageCount = ImageCount + 1
                # 
        if(ImageCount==0):
            print("Error! The input FitsImageFile does not contain any data image!")
        # 
    # 
    def image(self):
        return self.Image
    # 
    def getImage(self):
        return self.Image
    # 
    def dimension(self):
        return self.Dimension
    # 
    def getDimension(self):
        return self.Dimension
    # 
    def wcs(self):
        return self.WCS
    # 
    def getWCS(self):
        return self.WCS
    # 
    def pixscale(self):
        return self.PixScale
    # 
    def getPixScale(self):
        return self.PixScale

















