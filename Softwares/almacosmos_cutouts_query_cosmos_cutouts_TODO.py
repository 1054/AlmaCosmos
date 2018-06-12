#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# Usage: 
#    execfile('deepfields_cosmos_cutouts.py')
#

import urllib2
from BeautifulSoup import BeautifulSoup ## for now we are still using BS3
import re
import numpy
import numpy.lib.recfunctions as rec
import astropy
from datetime import datetime

cutoutServiceUrl = 'http://irsa.ipac.caltech.edu/cgi-bin/Cutouts/nph-cutouts?'
cutoutServiceUrl = cutoutServiceUrl + 'mission=COSMOS&'
cutoutServiceUrl = cutoutServiceUrl + 'min_size=0&'
cutoutServiceUrl = cutoutServiceUrl + 'max_size=180&'
cutoutServiceUrl = cutoutServiceUrl + 'locstr=150.3767541667+1.9034700000&'
cutoutServiceUrl = cutoutServiceUrl + 'sizeX=15&'
cutoutServiceUrl = cutoutServiceUrl + 'units=arcsec&'
cutoutServiceUrl = cutoutServiceUrl + 'mode=PI&'
cutoutServiceUrl = cutoutServiceUrl + 'ntable_cutouts=12&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl1=acs_mosaic_2.0&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl2=wfpc&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl3=nicmos_sci&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl4=subaru_mosaics&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl5=cfht_mosaics&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl6=kpno_mosaics&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl7=sdss_sci&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl8=irac_sci&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl9=mips_sci&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl10=galex_sci&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl11=vla_lg_dp&'
cutoutServiceUrl = cutoutServiceUrl + 'cutouttbl12=xmm_img'

if len(cutoutServiceUrl) > 0:
    print "++++++++++++"
    print "Opening Url:", cutoutServiceUrl
    cutoutServiceSite = urllib2.urlopen(cutoutServiceUrl)
    cutoutServiceMeta = cutoutServiceSite.info()
    cutoutServiceData = cutoutServiceSite.read()
    print "++++++++++++"
    print "Fetched Xml:"
    print cutoutServiceData




