#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: 
#    ./almacosmos_cutouts_query_cosmos_cutouts_via_IRSA.py
#

import os, sys, json, subprocess
import numpy
import astropy
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
from astropy.io.fits import Header
from copy import copy
from pprint import pprint
import binascii
import requests_toolbelt # pip install --user requests-toolbelt
from requests_toolbelt.multipart.decoder import MultipartDecoder # https://pypi.org/project/requests-toolbelt/
#from regions import DS9Parser, read_ds9, write_ds9

import requests

Source_Coordinate_Box = {
                            'RA': numpy.nan, 
                            'Dec': numpy.nan, 
                            'FoV': numpy.nan, 
                            'PX': numpy.nan, 
                            'PY': numpy.nan, 
                            'DX': numpy.nan, 
                            'DY': numpy.nan, 
                            'Cutout_LowerX': numpy.nan, 
                            'Cutout_LowerY': numpy.nan, 
                            'Cutout_UpperX': numpy.nan, 
                            'Cutout_UpperY': numpy.nan, 
                        }

# Preset
Output_Name = ''
Cutout_Field = 'COSMOS'
Cutout_Band = ''
Image_Urls = {
                'COSMOS_UVISTA_J':  'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.H.UV_original_psf.v1.fits',  
                'COSMOS_UVISTA_H':  'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.H.UV_original_psf.v1.fits',  
                'COSMOS_UVISTA_K':  'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.H.UV_original_psf.v1.fits',  
                'COSMOS_UVISTA_Y':  'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.H.UV_original_psf.v1.fits',  
                'COSMOS_ACS_i':     'http://irsa.ipac.caltech.edu/data/COSMOS/images/acs_mosaic_2.0/mosaic_Shrink10.fits',  
                'COSMOS_ACS_F814W': 'http://irsa.ipac.caltech.edu/data/COSMOS/images/acs_mosaic_2.0/mosaic_Shrink10.fits',  
                'COSMOS_VLA_3GHz':  'https://irsa.ipac.caltech.edu/data/COSMOS/images/vla/vla_3ghz_msmf.fits', 
            }
Header_Caches = {
                'COSMOS_UVISTA_J':  os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_UVISTA_J.header',  
                'COSMOS_UVISTA_H':  os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_UVISTA_H.header',  
                'COSMOS_UVISTA_K':  os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_UVISTA_K.header',  
                'COSMOS_UVISTA_Y':  os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_UVISTA_Y.header',  
                'COSMOS_ACS_i':     os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_ACS_i.header',  
                'COSMOS_ACS_F814W': os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_ACS_F814W.header',  
                'COSMOS_VLA_3GHz':  os.path.dirname(os.path.dirname(__file__))+os.sep+'Data'+os.sep+'cosmos_image_fits_header_files'+os.sep+'COSMOS_VLA_3GHz.header', 
}
Overwrite_Level = 0

# Read User Input
i = 1
while i < len(sys.argv):
    tmp_arg = sys.argv[i].lower().replace('--','-')
    if tmp_arg == '-ra':
        if i+1 < len(sys.argv):
            Source_Coordinate_Box['RA'] = float(sys.argv[i+1])
            i = i + 1
    elif tmp_arg == '-dec':
        if i+1 < len(sys.argv):
            Source_Coordinate_Box['Dec'] = float(sys.argv[i+1])
            i = i + 1
    elif tmp_arg == '-fov':
        if i+1 < len(sys.argv):
            Source_Coordinate_Box['FoV'] = float(sys.argv[i+1])
            i = i + 1
    elif tmp_arg == '-out':
        if i+1 < len(sys.argv):
            Output_Name = sys.argv[i+1]
            if Output_Name.endswith('.cutout.fits'):
                Output_Name = Output_Name.replace('.cutout.fits','')
            elif Output_Name.endswith('.fits'):
                Output_Name = Output_Name.replace('.fits','')
            i = i + 1
    elif tmp_arg == '-field':
        if i+1 < len(sys.argv):
            Cutout_Field = sys.argv[i+1].replace('-','_')
            i = i + 1
    elif tmp_arg == '-band':
        if i+1 < len(sys.argv):
            Cutout_Band = sys.argv[i+1].replace('-','_')
            i = i + 1
    elif tmp_arg == '-overwrite':
        Overwrite_Level = Overwrite_Level + 1
    else:
        if numpy.isnan(Source_Coordinate_Box['RA']):
            Source_Coordinate_Box['RA'] = float(sys.argv[i])
        elif numpy.isnan(Source_Coordinate_Box['Dec']):
            Source_Coordinate_Box['Dec'] = float(sys.argv[i])
        elif numpy.isnan(Source_Coordinate_Box['FoV']):
            Source_Coordinate_Box['FoV'] = float(sys.argv[i])
    i = i + 1

# Check User Input
if (numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec']) or numpy.isnan(Source_Coordinate_Box['FoV'])) \
    and (numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY']) or numpy.isnan(Source_Coordinate_Box['DX']) or numpy.isnan(Source_Coordinate_Box['DY'])):
    print('Please input RA Dec and FoV, or PX PY and DX DY!')
    sys.exit()
if Cutout_Band == '':
    print('Please input Band!')
    sys.exit()


# Prepare Url for Image Data
if Cutout_Field+'_'+Cutout_Band in Image_Urls:
    Http_Request_Url = Image_Urls[Cutout_Field+'_'+Cutout_Band]
    Header_Cache_Txt = Header_Caches[Cutout_Field+'_'+Cutout_Band]+'.txt'
    Header_Cache_Json = Header_Caches[Cutout_Field+'_'+Cutout_Band]+'.json'
elif Cutout_Field+'_'+Cutout_Band.upper() in Image_Urls:
    Http_Request_Url = Image_Urls[Cutout_Field+'_'+Cutout_Band.upper()]
    Header_Cache_Txt = Header_Caches[Cutout_Field+'_'+Cutout_Band.upper()]+'.txt'
    Header_Cache_Json = Header_Caches[Cutout_Field+'_'+Cutout_Band.upper()]+'.json'
elif Cutout_Field.upper()+'_'+Cutout_Band.upper() in Image_Urls:
    Http_Request_Url = Image_Urls[Cutout_Field.upper()+'_'+Cutout_Band.upper()]
    Header_Cache_Txt = Header_Caches[Cutout_Field.upper()+'_'+Cutout_Band.upper()]+'.txt'
    Header_Cache_Json = Header_Caches[Cutout_Field.upper()+'_'+Cutout_Band.upper()]+'.json'
else:
    print('Error! The input Field and Band "%s" is not in our Image Url list!'%(Cutout_Field+'_'+Cutout_Band))
    sys.exit()

if Output_Name == '':
    Output_Name = Http_Request_Url.split("/")[-1].replace('.fits','')
elif Output_Name.find('.fits') > 0:
    Output_Name = Output_Name.replace('.fits','')

# Print Settings
print('Http_Request_Url = %s'%(Http_Request_Url))
print('Source RA = %s [deg]'%(Source_Coordinate_Box['RA']))
print('Source Dec = %s [deg]'%(Source_Coordinate_Box['Dec']))
print('Source FoV = %s [arcsec]'%(Source_Coordinate_Box['FoV']))
print('Source PX = %s [pix]'%(Source_Coordinate_Box['PX']))
print('Source PY = %s [pix]'%(Source_Coordinate_Box['PY']))
print('Source DX = %s [pix]'%(Source_Coordinate_Box['DX']))
print('Source DY = %s [pix]'%(Source_Coordinate_Box['DY']))
print('Output_Name = %s'%(Output_Name))
print('Header_Cache_Txt = %s'%(Header_Cache_Txt))
print('Header_Cache_Json = %s'%(Header_Cache_Json))

with open(Output_Name+'.cutout.ds9.reg','w') as fp:
    fp.write('# Region file format: DS9\n')
    fp.write('fk5\n')
    fp.write('box(%s,%s,%s",%s")\n'%(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], Source_Coordinate_Box['FoV'], Source_Coordinate_Box['FoV']))

if not os.path.isfile(Header_Cache_Txt) or not os.path.isfile(Header_Cache_Json):
    Header_Cache_Txt = Output_Name+'.header.txt'
    Header_Cache_Json = Output_Name+'.header.json'
    # we need fits headers to determine how many bytes to shift 
    # if we have not downloaded the fits header files before, then download the into target directory.

if not os.path.isfile(Header_Cache_Txt) or Overwrite_Level >= 2:
    # 
    Http_Request_Head = requests.head(Http_Request_Url, allow_redirects=True)
    print(Http_Request_Head.headers)
    if not 'Accept-Ranges' in Http_Request_Head.headers:
        print('Error! The server does not support Http Range header! Exit!')
        sys.exit()
    # 
    Http_Request_Offset = 0
    Http_Request_Length = 2880 # 80*36, 36 lines of the FITS header
    Http_Request_Content = '' # to store FITS header
    Flag_END = False # whether we have read the END mark
    FITS_Header_Length1 = 0
    FITS_Header_Length2 = 0
    # 
    with open(Header_Cache_Txt, 'w') as fp:
        while Http_Request_Offset < int(Http_Request_Head.headers['Content-Length']):
            Http_Request_Range = {'Range': 'bytes=%d-%d'%(Http_Request_Offset, Http_Request_Offset+Http_Request_Length)}
            print(Http_Request_Range)
            Http_Request_Get = requests.get(Http_Request_Url, headers=Http_Request_Range)
            print(Http_Request_Get)
            if Http_Request_Get.status_code == 206:
                Http_Request_Content = Http_Request_Get.text
                for i in range(0,len(Http_Request_Content),80):
                    if ord(Http_Request_Content[i]) == 0 or ord(Http_Request_Content[i]) >= 128:
                        FITS_Header_Length2 = Http_Request_Offset + i
                        break
                    elif Http_Request_Content[i:i+80].rstrip() == 'END':
                        Flag_END = True
                        FITS_Header_Length1 = Http_Request_Offset + i + 80
                    fp.write(Http_Request_Content[i:i+80]+'\n')
            elif Http_Request_Get.status_code == 200:
                print('Error! Remote server does not support Http Range request!')
                with open(Output_Name+'.header.http.request.json', 'w') as jfp:
                    json.dump({'Http_Request_Offset': Http_Request_Offset, 'Http_Request_Length': Http_Request_Length}, jfp)
                sys.exit()
            else:
                print('Error! Connection broken!')
                with open(Output_Name+'.header.http.request.json', 'w') as jfp:
                    json.dump({'Http_Request_Offset': Http_Request_Offset, 'Http_Request_Length': Http_Request_Length}, jfp)
                sys.exit()
            # 
            if Flag_END:
                if os.path.isfile(Output_Name+'.header.http.request.json'):
                    os.remove(Output_Name+'.header.http.request.json')
                break
            # 
            Http_Request_Offset = Http_Request_Offset + Http_Request_Length
            Http_Request_Content = ''
    # 
    with open(Header_Cache_Json, 'w') as jfp:
        json.dump({'FITS_Header_Length': FITS_Header_Length2, 'FITS_Total_Length': int(Http_Request_Head.headers['Content-Length'])}, jfp)
    #print('FITS_Header_Length = %d'%(FITS_Header_Length2))



if not os.path.isfile(Output_Name+'.cutout.fits') or Overwrite_Level >= 1:
    # 
    print('Prepare to download '+Output_Name+'.cutout.fits')
    with open(Header_Cache_Json, 'r') as jfp:
        # 
        # Read FITS header length in (bytes)
        jdict = json.load(jfp)
        FITS_Header_Length = jdict['FITS_Header_Length']
        print('FITS_Header_Length = %s'%(FITS_Header_Length))
        
        # 
        # Generate FITS header object
        FITS_Header_Object = Header.fromfile(Header_Cache_Txt, sep='\n', endcard=False, padding=False) # , output_verify='ignore'
        FITS_Data_Unit_Byte = 4 # float/float16 type 
        if str(FITS_Header_Object['BITPIX']).strip() == '-64':
            FITS_Data_Unit_Byte = 8 # double/float32 type 
        print('FITS_Data_Unit_Byte = %s'%(FITS_Data_Unit_Byte))
        
        # 
        # Fix NAXIS
        #if FITS_Header_Object['NAXIS']
        
        # 
        # Generate FITS header WCS
        FITS_Header_WCS = WCS(FITS_Header_Object, naxis=2)
        print(FITS_Header_WCS.printwcs())
        print('')
        
        # 
        # convert sky2xy or xy2sky
        if (numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY'])) \
            and ~(numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec'])):
            Source_Coordinate_Box['PX'], Source_Coordinate_Box['PY'] = FITS_Header_WCS.wcs_world2pix(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], 1)
        elif ~(numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY'])) \
            and (numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec'])):
            Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'] = FITS_Header_WCS.wcs_pix2world(Source_Coordinate_Box['PX'], Source_Coordinate_Box['PY'], 1)
        else:
            print('Error! Either both RA Dec are invalid or both PX PY are invalid!')
            sys.exit()
        
        # 
        # check x y
        if Source_Coordinate_Box['PX']<1:
            print('Error! Source x coordinate < 1!')
            sys.exit()
        elif Source_Coordinate_Box['PX']>int(FITS_Header_Object['NAXIS1']):
            print('Error! Source x coordinate > NAXIS1 (%d)!'%(int(FITS_Header_Object['NAXIS1'])))
            sys.exit()
        elif Source_Coordinate_Box['PY']<1:
            print('Error! Source y coordinate < 1!')
            sys.exit()
        elif Source_Coordinate_Box['PY']>int(FITS_Header_Object['NAXIS2']):
            print('Error! Source y coordinate > NAXIS2 (%d)!'%(int(FITS_Header_Object['NAXIS2'])))
            sys.exit()
        
        # 
        # convert pixscale
        FITS_Pixel_Scale = astropy.wcs.utils.proj_plane_pixel_scales(FITS_Header_WCS)
        FITS_Pixel_Scale = numpy.array(FITS_Pixel_Scale) * 3600.0
        print('FITS_Pixel_Scale = %s arcsec'%(FITS_Pixel_Scale))
        
        # 
        # convert FoV to DX DY
        if (numpy.isnan(Source_Coordinate_Box['DX']) or numpy.isnan(Source_Coordinate_Box['DY'])) \
            and ~(numpy.isnan(Source_Coordinate_Box['FoV'])):
            Source_Coordinate_Box['DX'] = numpy.abs(Source_Coordinate_Box['FoV'] / FITS_Pixel_Scale[0])
            Source_Coordinate_Box['DY'] = numpy.abs(Source_Coordinate_Box['FoV'] / FITS_Pixel_Scale[1])
        
        # 
        # check x y
        if Source_Coordinate_Box['PX']-Source_Coordinate_Box['DX']<1:
            print('Error! Cutout lower x coordinate < 1!')
            sys.exit()
        elif Source_Coordinate_Box['PX']+Source_Coordinate_Box['DX']>int(FITS_Header_Object['NAXIS1']):
            print('Error! Cutout upper x coordinate > NAXIS1 (%d)!'%(int(FITS_Header_Object['NAXIS1'])))
            sys.exit()
        elif Source_Coordinate_Box['PY']-Source_Coordinate_Box['DY']<1:
            print('Error! Cutout lower y coordinate < 1!')
            sys.exit()
        elif Source_Coordinate_Box['PY']+Source_Coordinate_Box['DY']>int(FITS_Header_Object['NAXIS2']):
            print('Error! Cutout upper y coordinate > NAXIS2 (%d)!'%(int(FITS_Header_Object['NAXIS2'])))
            sys.exit()
        
        # 
        # define cutout box
        Source_Coordinate_Box['Cutout_LowerX'] = int(Source_Coordinate_Box['PX'] - Source_Coordinate_Box['DX']/2.0)
        Source_Coordinate_Box['Cutout_UpperX'] = int(Source_Coordinate_Box['PX'] + Source_Coordinate_Box['DX']/2.0)
        Source_Coordinate_Box['Cutout_LowerY'] = int(Source_Coordinate_Box['PY'] - Source_Coordinate_Box['DY']/2.0)
        Source_Coordinate_Box['Cutout_UpperY'] = int(Source_Coordinate_Box['PY'] + Source_Coordinate_Box['DY']/2.0)
        pprint(FITS_Header_WCS.calc_footprint())
        FITS_Header_WCS.footprint_to_file(Output_Name+'.cutout.footprint.ds9.reg', color='green', width=2)
        #with open(Output_Name+'.cutout.footprint.json', 'w') as jfp:
        #    json.dump(FITS_Header_WCS.calc_footprint().tolist(), jfp)
        #print(FITS_Header_Object['NAXIS1'])
        #cutout = Cutout2D(pf[0].data, position, size, wcs=wcs)
        pprint('Source_Coordinate_Box = %s'%(Source_Coordinate_Box))
            
        # 
        # Prepare new fits header and write to fits file
        FITS_Header_Object2 = copy(FITS_Header_Object)
        FITS_Header_Object2['NAXIS1'] = Source_Coordinate_Box['Cutout_UpperX'] - Source_Coordinate_Box['Cutout_LowerX'] + 1
        FITS_Header_Object2['NAXIS2'] = Source_Coordinate_Box['Cutout_UpperY'] - Source_Coordinate_Box['Cutout_LowerY'] + 1
        FITS_Header_Object2['CRPIX1'] = FITS_Header_Object2['CRPIX1'] - (Source_Coordinate_Box['Cutout_LowerX']-1)
        FITS_Header_Object2['CRPIX2'] = FITS_Header_Object2['CRPIX2'] - (Source_Coordinate_Box['Cutout_LowerY']-1)
        FITS_Header_Object2.tofile(Output_Name+'.cutout.fits', sep='', endcard=True, padding=True, overwrite=True)
        Cutout_Data_Length = FITS_Header_Object2['NAXIS1'] * FITS_Header_Object2['NAXIS2'] * FITS_Data_Unit_Byte
        
        # 
        # Http request range
        Download_loop = Source_Coordinate_Box['Cutout_LowerY']
        Download_step = Source_Coordinate_Box['Cutout_UpperY'] - Source_Coordinate_Box['Cutout_LowerY']
        if Download_step > 50:
            Download_step = 50 # must devide into multiple loops, because each request should not be too long
        while Download_loop <= Source_Coordinate_Box['Cutout_UpperY']:
            
            Http_Request_Range = {'Range': 'bytes=', 'Content-Type': 'multipart/byteranges'}
            
            if Download_loop+Download_step > Source_Coordinate_Box['Cutout_UpperY']:
                Download_step = Source_Coordinate_Box['Cutout_UpperY'] - Download_loop
            
            for y in numpy.arange(Download_loop, Download_loop+Download_step+1, 1):
                Http_Request_Offset_1 = FITS_Header_Length + FITS_Data_Unit_Byte * ((y-1) * int(FITS_Header_Object['NAXIS1']) + (Source_Coordinate_Box['Cutout_LowerX']-1))
                Http_Request_Offset_2 = FITS_Header_Length + FITS_Data_Unit_Byte * ((y-1) * int(FITS_Header_Object['NAXIS1']) + (Source_Coordinate_Box['Cutout_UpperX']-1)) + FITS_Data_Unit_Byte-1
                #if Http_Request_Offset_2>int(Http_Request_Head.headers['Content-Length']):
                #    print('Error! Requested range too large!')
                print('Http_Request_Offset = %d-%d (X:%d-%d, Y:%d)'%(Http_Request_Offset_1, Http_Request_Offset_2, Source_Coordinate_Box['Cutout_LowerX'], Source_Coordinate_Box['Cutout_UpperX'], y))
                if Http_Request_Range['Range'] == 'bytes=':
                    Http_Request_Range['Range'] = Http_Request_Range['Range'] + '%d-%d'%(Http_Request_Offset_1, Http_Request_Offset_2)
                else:
                    Http_Request_Range['Range'] = Http_Request_Range['Range'] + ',%d-%d'%(Http_Request_Offset_1, Http_Request_Offset_2)
            
            Download_loop = Download_loop+Download_step+1
            
            #Http_Request_Range['Transfer-Length'] = '%d'%(Cutout_Data_Length)
            
            pprint(Http_Request_Range)
            
            # 
            # Http request get -- partially get byte ranges -- then append to fits file
            with open(Output_Name+'.cutout.fits', 'ab') as fp:
                Http_Request_Get = requests.get(Http_Request_Url, headers=Http_Request_Range, stream=True)
                print(Http_Request_Get)
                if Http_Request_Get.status_code == 206:
                    #Http_Request_Content = Http_Request_Get.content
                    # To read multi byte range request content, we need the help of requests_toolbelt.multipart.decoder.MultipartDecoder
                    Http_Request_Content = MultipartDecoder.from_response(Http_Request_Get) # see -- https://github.com/requests/toolbelt/blob/master/requests_toolbelt/multipart/decoder.py
                    for part in Http_Request_Content.parts:
                        #pprint(part.text())
                        fp.write(part.content)
                    #if len(Http_Request_Content) > Cutout_Data_Length:
                    #    Http_Request_Content_Cutoff = 0
                    #    j = 0
                    #    #while j < len(Http_Request_Content):
                    #    #    if Http_Request_Content[j:j+4] == bytes.fromhex('0d0a2d2d'):
                    #    #        Http_Request_Content_Cutoff = 1
                    #    #    k = j+101
                    #    #    while k < len(Http_Request_Content):
                    #    #        if Http_Request_Content[k:k+4] == bytes.fromhex('0d0a0d0a'):
                    #    #        
                    #    #    j = j + 1
                    #fp.write(Http_Request_Content)
                    #for chunk in Http_Request_Get.iter_content(chunk_size=128):
                    #    fp.write(chunk)
                    #print(binascii.hexlify(copy(Http_Request_Content)))
                elif Http_Request_Get.status_code == 200:
                    print('Error! Remote server does not support Http Range request!')
                    with open(Output_Name+'.cutout.http.request.json', 'w') as jfp:
                        json.dump(Http_Request_Range, jfp)
                    os.system('rm '+Output_Name+'.cutout.fits')
                    sys.exit()
                elif Http_Request_Get.status_code == 416:
                    print('Error! Requested range out of limit!')
                    with open(Output_Name+'.cutout.http.request.json', 'w') as jfp:
                        json.dump(Http_Request_Range, jfp)
                    os.system('rm '+Output_Name+'.cutout.fits')
                    sys.exit()
                else:
                    print('Error! Connection broken!')
                    with open(Output_Name+'.cutout.http.request.json', 'w') as jfp:
                        json.dump(Http_Request_Range, jfp)
                    os.system('rm '+Output_Name+'.cutout.fits')
                    sys.exit()
    
    





