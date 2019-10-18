#!/usr/bin/env python
# 
# 20190503

import os, sys, re, copy, datetime
import warnings
warnings.simplefilter("ignore")
import numpy as np
import astropy
import astropy.io.fits as fits
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy import units as u
from astropy.coordinates import Angle
#import regions
#from regions import PointSkyRegion, PointPixelRegion, CircleSkyRegion, CirclePixelRegion, EllipseSkyRegion, EllipsePixelRegion, PolygonSkyRegion, PolygonPixelRegion # https://astropy-regions.readthedocs.io/en/latest/shapes.html
#from regions import DS9Parser, ds9_objects_to_string
#from regions import read_ds9, write_ds9


# Read user input
input_fits_file = ''
output_name = ''
input_crange = []
output_notes = []
overwrite = False
make_plot = False
arg_str = ''
arg_mode = ''
for i in range(1,len(sys.argv)):
    # 
    arg_str = sys.argv[i].lower().replace('--','-')
    # 
    # parse arg_str
    if arg_str.startswith('-out'):
        arg_mode = 'out'
        continue
    # 
    elif arg_str.startswith('-crange'):
        arg_mode = 'crange'
        continue
    # 
    elif arg_str.startswith('-plot'):
        arg_mode = 'plot'
    # 
    elif arg_str.startswith('-overwrite'):
        arg_mode = 'overwrite'
    # 
    elif arg_mode == '':
        arg_mode = 'in'
    # 
    # parse arg_mode
    if arg_mode == 'in':
        input_fits_file = sys.argv[i]
        arg_mode = '' # read once
    elif arg_mode == 'out':
        output_name = sys.argv[i]
        arg_mode = '' # read once
    elif arg_mode == 'crange':
        input_crange.append(int(sys.argv[i]))
        # read untill other args
    elif arg_mode == 'plot':
        make_plot = True
        arg_mode = '' # read once
    elif arg_mode == 'overwrite':
        overwrite = True
        arg_mode = '' # read once
    

# Check user input
if input_fits_file == '':
    print('Usage:')
    print('    alma_fits_image_cube_collapse_channels.py INPUT_FITS_IMAGE_CUBE.fits -crange 0 0 -out OUTPUT_NAME')
    print('Note:')
    print('    This code will collapse along the channel axis and produce an image.')
    print('    Notice that the input channel number is 1-based, same as ds9.')
    print('    Input crange 0 0 means collapsing all channels.')
    print('')
    sys.exit()

if len(input_crange) == 0:
    input_crange = [0, 0]

if len(input_crange) % 2 != 0:
    print('Error! The input -crange array size should be n times 2!')
    sys.exit()


# Set default output name
if output_name == '':
    output_name = re.sub(r'\.fits$', r'', os.path.basename(input_fits_file), re.IGNORECASE) + '_collapsed_channels_%d_%d'%(input_crange[0], input_crange[1])


#print('input_fits_file = "%s"'%(input_fits_file))
#print('output_name = "%s"'%(output_name))


# Open fits file and extract the spectrum
with fits.open(input_fits_file) as hdulist:
    # 
    print(hdulist.info())
    hdu0 = hdulist[0]
    # 
    # check dimension
    if len(hdu0.data.shape) < 3:
        print('Error! The input fits file "%s" is not a data cube! Exit!'%(input_fits_file))
        sys.exit()
    # 
    # trim to cube
    while len(hdu0.data.shape) > 3:
        hdu0.data = hdu0.data[0]
    # 
    # get wcs 2D
    wcs0 = WCS(hdu0.header, naxis=2)
    # 
    # get channels
    mask = np.full(hdu0.data.shape[0], False)
    for i in range(0, len(input_crange), 2):
        i0 = input_crange[i]
        i1 = input_crange[i+1]
        if i0 == 0 and i1 == 0:
            mask[:] = True
        elif i1 > i0:
            mask[i0+1:i1+1+1] = True
    # 
    # collapse along channel axis
    output_image = np.sum(hdu0.data[mask, :, :], naxis=0)
    # 
    # output fits image
    print('Writing fits file...')
    output_hdu = fits.PrimaryHDU(data = output_image, header = wcs0.to_header())
    output_hdu.writeto(output_name+'.fits', overwrite = overwrite)
    print('Output to "%s"!'%(output_name))
    
    
    # output readme file
    with open(output_name+'.readme.txt', 'w') as ofp:
        ofp.write('Collapsed the channels from the following fits cube file at %s:\n'%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')))
        ofp.write('    %s\n'%(input_fits_file))
        ofp.write('\n')
        ofp.write('with channel ranges:\n')
        ofp.write('    %s\n'%(', '.join(np.array(input_crange).astype(str))))
        ofp.write('\n')
        ofp.write('by the code:\n')
        ofp.write('    %s\n'%(os.path.abspath(__file__)))
        ofp.write('\n')
        if len(output_notes) > 0:
            ofp.write('\n')
            ofp.write('Notes: \n')
            for output_note in output_notes:
                ofp.write('    %s\n'%(output_note))
            ofp.write('\n')
    print('Output to "%s"!'%(output_name+'.readme.txt'))
    
    
    
    # make plot if the user said so
    #if make_plot:
    #    
    #    import matplotlib
    #    import matplotlib.pyplot as plt
    #    
    #    fig = plt.figure(figsize=(5.0, 4.0))
    #    ax = fig.add_subplot(1,1,1)
    #    ax.plot(skycoord3, skycoord3*0.0, linestyle='solid', linewidth=0.9, color='#555555')
    #    ax.step(skycoord3, extracted_spectrum)
    #    ax.tick_params(axis='both', which='major', direction='in', labelsize=13)
    #    for i in range(np.min([10,len(combined_sky_regions)])):
    #        ax.text(0.015, 0.915 - i*0.045, 'Region %s, radius %s'%(combined_sky_regions[i].center.to_string('hmsdms'), combined_sky_regions[i].radius), transform=ax.transAxes, fontsize=14)
    #    ax.xaxis.set_ticks_position('both')
    #    ax.yaxis.set_ticks_position('both')
    #    ax.set_xlabel(output_X_column_name, fontsize=15, labelpad=10)
    #    ax.set_ylabel(output_Y_column_name, fontsize=15, labelpad=10)
    #    fig.tight_layout()
    #    fig.savefig(output_name+'.pdf', dpi=250, overwrite=True)
    #    
    #    print('Output to "%s"!'%(output_name+'.pdf'))
    #    
    #    os.system('open "%s"'%(output_name+'.pdf'))
    









