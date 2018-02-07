#!/usr/bin/env python
# 
# Aim:
#     check whether a galaxy is within some fits images
# 
# Last update:
#     20170323
#     20180206
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy>=1.3")
pkg_resources.require("shapely")
#pkg_resources.require("matplotlib")
#pkg_resources.require("wcsaxes") # http://wcsaxes.readthedocs.io/en/latest/getting_started.html

import os
import sys
import re
import glob
import inspect
import math
import numpy
import astropy
from astropy import units
from astropy.io import fits
import astropy.io.ascii as asciitable
from astropy.wcs import WCS
#import wcsaxes
from pprint import pprint

#import matplotlib

from astropy.coordinates import FK5, SkyCoord
from astropy.time import Time
from astropy import units as u




















####################################################################
#                                                                  #
#                                                                  #
#                           MAIN PROGRAM                           #
#                                                                  #
#                                                                  #
####################################################################

#Source = Highz_Galaxy(Field='COSMOS', ID=500030, SubID=1, Names={'Paper1':'Name1','Paper2':'Name2'})
#Source.about()

if len(sys.argv) <= 3:
    print("Usage: almacosmos_recognize_source_in_fits_meta_table.py Source_RA Source_Dec Fits_Meta_Table.txt")
    sys.exit()

# 
# Read first argument -- RADEC
RA = float(sys.argv[1])
DEC = float(sys.argv[2])
#print(RA, DEC)

# 
# Read second argument -- FITS_META_TABLE
FITS_META_TABLE = asciitable.read(sys.argv[len(sys.argv)-1]) # header_start=0, data_start=2
#print(FITS_META_TABLE)





# 
# 
#import matplotlib.pyplot as plt
#plt.figure(figsize=(8,4.2))
#plt.subplot(111, projection="aitoff") # aitoff projection
#plt.title("Aitoff projection")
#plt.grid(True)



# 
# Intersect


cen_ra = numpy.array(FITS_META_TABLE['cen_ra']).astype(numpy.float64)
cen_dec = numpy.array(FITS_META_TABLE['cen_dec']).astype(numpy.float64)
dist_ra = (cen_ra - RA) * numpy.cos(cen_dec/180.0*numpy.pi) * 3600.0 # arcsec
dist_dec = (cen_dec - DEC) * 3600.0 # arcsec
dist_sqrt = numpy.sqrt(dist_ra*dist_ra + dist_dec*dist_dec)
dist_thresh = numpy.array(FITS_META_TABLE['FoV_dec']).astype(numpy.float64) / 2.0 # arcsec, radius from image center
dist_mask = (dist_sqrt<dist_thresh)
dist_iarg = numpy.argwhere(dist_mask)

#print(FITS_META_TABLE['image_file'][dist_mask])
FITS_META_TABLE['offset_RA'] = dist_ra
FITS_META_TABLE['offset_Dec'] = dist_dec
SELECTED_META_TABLE = FITS_META_TABLE[dist_mask]
print('#-------------------------------------------------------------------------------')
print('# Input RA Dec: %0.10f %0.10f'%(RA, DEC))
#for i in dist_iarg:
#    print('%s %10.4f\n'%(FITS_META_TABLE['image_file'][i], float(FITS_META_TABLE['wavelength'][i])))
asciitable.write(SELECTED_META_TABLE['image_file','offset_RA','offset_Dec','wavelength'], sys.stdout, Writer=asciitable.FixedWidthNoHeader, 
                 delimiter='   ', delimiter_pad=None, bookend=False, 
                 formats={'image_file':'%-s', 'offset_RA':'%-8.3f', 'offset_Dec':'%-8.3f'}, 
                 )
print('')

#for i in range(len(dist_mask)):
#    if dist_mask[i] == True:
#        print(FITS_META_TABLE['image_file'][i])

#from shapely import geometry
#source_pos = geometry.Point(RA, DEC)
#for i in range(len(FITS_META_TABLE)):
#    # 
#    #circle_center = geometry.Point(cen_ra,cen_dec)
#    #circle_buffer = circle_center.buffer(float(FITS_META_TABLE['FoV_dec'][i])/2.0/3600.0).boundary
#    #if circle_buffer.contains(source_pos):
#    #    print(FITS_META_TABLE['image_file'])
#    # 
#    #time_now = 2457936.093235361390
#    #coord_j2000 = SkyCoord(ra*u.deg, dec*u.deg, frame=FK5)
#    #fk5_now = FK5(equinox=Time(time_now, format="jd", scale="utc"))
#    #coord_now = coord_j2000.transform_to(fk5_now)
#    #c_gal = SkyCoord(galaxy, representation='cartesian', frame='galactic')
#    #c_gal_icrs = c_gal.icrs
#    #plt.plot(c_gal_icrs.ra.wrap_at(180 * u.deg).radian, 
#    #         c_gal_icrs.dec.radian, 
#    #         'o', markersize=2, alpha=0.3)
#    c = SkyCoord(ra = circle_center.x * u.degree, dec = circle_center.y * u.degree, frame='icrs')
#    plt.plot(c.ra.wrap_at(180 * u.deg).radian, 
#             c.dec.radian, 
#             'o', markersize=2, alpha=0.3)
# 
##plt.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)
#plt.subplots_adjust(top=0.95,bottom=0.0)
#plt.show()






























