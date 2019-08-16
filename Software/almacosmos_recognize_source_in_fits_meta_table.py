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
from astropy.table import Column, Table




















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
#<20180314>#if sys.argv[len(sys.argv)-1].lower().endswith('.fits'):
#<20180314>#    FITS_META_TABLE_HDU = fits.open(sys.argv[len(sys.argv)-1])
#<20180314>#    i = 0
#<20180314>#    while i < len(FITS_META_TABLE_HDU) and type(FITS_META_TABLE_HDU[i]) != fits.hdu.table.BinTableHDU:
#<20180314>#        i = i+1
#<20180314>#    if i < len(FITS_META_TABLE_HDU):
#<20180314>#        FITS_META_TABLE = Table(FITS_META_TABLE_HDU[i].data)
#<20180314>#        FITS_META_TABLE_COLNAMES = FITS_META_TABLE_HDU[i].columns.names
#<20180314>#    else:
#<20180314>#        print("Error! Could not find fits.hdu.table.BinTableHDU in the input fits file \"%s\"!"%(sys.argv[len(sys.argv)-1]))
#<20180314>#        sys.exit()
#<20180314>#else:
#<20180314>#    FITS_META_TABLE = asciitable.read(sys.argv[len(sys.argv)-1]) # header_start=0, data_start=2
#<20180314>#    FITS_META_TABLE_COLNAMES = FITS_META_TABLE.colnames
sys.path.append(os.path.dirname(os.path.abspath(__file__))+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import CrabTable
FITS_META_TABLE_STRUCT = CrabTable(sys.argv[len(sys.argv)-1])
FITS_META_TABLE = FITS_META_TABLE_STRUCT.TableData
FITS_META_TABLE_COLNAMES = FITS_META_TABLE_STRUCT.TableHeaders
#print(FITS_META_TABLE)
#print(type(FITS_META_TABLE))
#print(FITS_META_TABLE.dtype.descr)
#print(FITS_META_TABLE_COLNAMES)





# 
# 
#import matplotlib.pyplot as plt
#plt.figure(figsize=(8,4.2))
#plt.subplot(111, projection="aitoff") # aitoff projection
#plt.title("Aitoff projection")
#plt.grid(True)



# 
# Intersect

if (not ('cen_ra' in FITS_META_TABLE.colnames)) and ('CENRA' in FITS_META_TABLE.colnames):
    FITS_META_TABLE['cen_ra'] = FITS_META_TABLE['CENRA']
if (not ('cen_dec' in FITS_META_TABLE.colnames)) and ('CENDEC' in FITS_META_TABLE.colnames):
    FITS_META_TABLE['cen_dec'] = FITS_META_TABLE['CENDEC']
if (not ('FoV_ra' in FITS_META_TABLE.colnames)) and ('FoV_RA' in FITS_META_TABLE.colnames):
    FITS_META_TABLE['FoV_ra'] = FITS_META_TABLE['FoV_RA']
if (not ('FoV_dec' in FITS_META_TABLE.colnames)) and ('FoV_DEC' in FITS_META_TABLE.colnames):
    FITS_META_TABLE['FoV_dec'] = FITS_META_TABLE['FoV_DEC']

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
print('# Found %d ALMA images'%(len(SELECTED_META_TABLE)))
print('# ')
#for i in dist_iarg:
#    print('%s %10.4f\n'%(FITS_META_TABLE['image_file'][i], float(FITS_META_TABLE['wavelength'][i])))
#<20180314>#asciitable.write(SELECTED_META_TABLE['image_file','offset_RA','offset_Dec','wavelength'], sys.stdout, Writer=asciitable.FixedWidthNoHeader, 
#<20180314>#                 delimiter='   ', delimiter_pad=None, bookend=False, 
#<20180314>#                 formats={'image_file':'%-s', 'offset_RA':'%-8.3f', 'offset_Dec':'%-8.3f'}, 
#<20180314>#                 )
#asciitable.write(SELECTED_META_TABLE['image_file','offset_RA','offset_Dec','wavelength'], sys.stdout, Writer=asciitable.FixedWidthTwoLine, 
#                 delimiter='|', delimiter_pad=' ', bookend=True, 
#                 formats={'image_file':'%s', 'offset_RA':'%-8.3f', 'offset_Dec':'%-8.3f'}, 
#                 )
if len(SELECTED_META_TABLE) > 0:
    print_max_len_image_file = len(max(SELECTED_META_TABLE['image_file'], key=len))
    for i in range(len(SELECTED_META_TABLE)):
        print_headers = []
        print_values = []
        for print_col in ['image_file','offset_RA','offset_Dec','wavelength']:
            print_values.append(SELECTED_META_TABLE[i][print_col])
            print_headers.append(print_col)
        if i == 0:
            exec('print("# %%-%ds %%-8s %%-8s %%-10s"%%(tuple(print_headers)))'%(print_max_len_image_file), locals())
        exec('print("%%-%ds %%-8.3f %%-8.3f %%-10.3f"%%(tuple(print_values)))'%(print_max_len_image_file+2), locals())
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






























