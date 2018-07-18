#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: 
#    ./almacosmos_cutouts_query_cosmos_cutouts_via_IRSA_Cutouts_Service.py
#

import os, sys, json, subprocess
import numpy
import astropy
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
from astropy.io.fits import Header
from copy import copy
from pprint import pprint

import requests

try:
    import xml.etree.cElementTree as ET
    #import elementtree.ElementTree as ET
except ImportError:
    raise ImportError('Failed to import xml ElementTree as ET')


# Initialize
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
Http_User_Name = ''
Http_User_Pass = ''
Image_Names = {
                'COSMOS_ACS_i':         'acs_mosaic_2.0', 
                'COSMOS_ACS_F814W':     'acs_mosaic_2.0', 
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
                Output_Name = ''.join(Output_Name.rsplit('.cutout.fits',1)) # replace the last pattern
            elif Output_Name.endswith('.fits'):
                Output_Name = ''.join(Output_Name.rsplit('.fits',1)) # replace the last pattern
            i = i + 1
    elif tmp_arg == '-field':
        if i+1 < len(sys.argv):
            Cutout_Field = sys.argv[i+1].replace('-','_')
            i = i + 1
    elif tmp_arg == '-band':
        if i+1 < len(sys.argv):
            Cutout_Band = sys.argv[i+1].replace('-','_')
            i = i + 1
    elif tmp_arg == '-http-username' or tmp_arg == '-http-user-name':
        if i+1 < len(sys.argv):
            Http_User_Name = sys.argv[i+1]
            i = i + 1
    elif tmp_arg == '-http-userpass' or tmp_arg == '-http-user-pass':
        if i+1 < len(sys.argv):
            Http_User_Pass = sys.argv[i+1]
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
if Cutout_Field+'_'+Cutout_Band in Image_Names:
    Image_Name = Image_Names[Cutout_Field+'_'+Cutout_Band]
elif Cutout_Field+'_'+Cutout_Band.upper() in Image_Names:
    Image_Name = Image_Names[Cutout_Field+'_'+Cutout_Band.upper()]
elif Cutout_Field.upper()+'_'+Cutout_Band.upper() in Image_Names:
    Image_Name = Image_Names[Cutout_Field.upper()+'_'+Cutout_Band.upper()]
else:
    print('Error! The input Field and Band "%s" is not in our Image Url list!'%(Cutout_Field+'_'+Cutout_Band))
    sys.exit()

if Output_Name == '':
    Output_Name = Image_Name.split("/")[-1]
if Output_Name.find('.fits') > 0:
    Output_Name = ''.join(Output_Name.rsplit('.fits',1)) # replace the last pattern
if not os.path.isdir(os.path.dirname(Output_Name)):
    os.makedirs(os.path.dirname(Output_Name))

# Print Settings
print('Image_Name = %s'%(Image_Name))
print('Source RA = %s [deg]'%(Source_Coordinate_Box['RA']))
print('Source Dec = %s [deg]'%(Source_Coordinate_Box['Dec']))
print('Source FoV = %s [arcsec]'%(Source_Coordinate_Box['FoV']))
print('Source PX = %s [pix]'%(Source_Coordinate_Box['PX']))
print('Source PY = %s [pix]'%(Source_Coordinate_Box['PY']))
print('Source DX = %s [pix]'%(Source_Coordinate_Box['DX']))
print('Source DY = %s [pix]'%(Source_Coordinate_Box['DY']))
print('Output_Name = %s'%(Output_Name))

with open(Output_Name+'.cutout.ds9.reg','w') as fp:
    fp.write('# Region file format: DS9\n')
    fp.write('fk5\n')
    fp.write('box(%s,%s,%s",%s")\n'%(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], Source_Coordinate_Box['FoV'], Source_Coordinate_Box['FoV']))


with requests.Session() as Http_Request_Session:
    
    Http_Request_Auth = None
    
    
    if not os.path.isfile(Output_Name+'.cutout.fits') or Overwrite_Level >= 1:
        # 
        if Http_Request_Auth is None:
            if Cutout_Field == 'COSMOS_INT':
                print('Cutout_Field is COSMOS_INT! We are logging in...')
                if Http_User_Name == '':
                    Http_User_Name = input("Please enter http user name: ")
                if Http_User_Pass == '':
                    Http_User_Pass = getpass("Please enter http user password: ")
                Http_Request_Auth = requests.auth.HTTPBasicAuth(Http_User_Name, Http_User_Pass) # see -- http://docs.python-requests.org/en/master/user/authentication/
                print('Http_Request_Auth = %s'%(Http_Request_Auth))
        # 
        # 
        print('')
        print('')
        print('Prepare to download '+Output_Name+'.cutout.fits')
        
        Http_Request_Param = 'https://irsa.ipac.caltech.edu/cgi-bin/Cutouts/nph-cutouts?mission=%s&min_size=1&max_size=180&units=arcsec&locstr=%0.10f+%0.10f+eq&sizeX=%0.3f&ntable_cutouts=1&cutouttbl1=%s&mode=PI'%(\
                                Cutout_Field, 
                                Source_Coordinate_Box['RA'], 
                                Source_Coordinate_Box['Dec'], 
                                Source_Coordinate_Box['FoV'], 
                                Image_Name)
        print(Http_Request_Param)
        
        Http_Request_Get = Http_Request_Session.get(Http_Request_Param)
        print(Http_Request_Get)
        print(Http_Request_Get.text)
        
        #Http_Request_Result_Tree = ET.parse('aaa.xml') # see -- 
        #Http_Request_Result_XML_Root = Http_Request_Result_Tree.getroot()
        Http_Request_Result_XML_Root = ET.fromstring(Http_Request_Get.content.decode("utf-8")) # see -- 
        print(Http_Request_Result_XML_Root)
        if 'status' in Http_Request_Result_XML_Root.attrib:
            if Http_Request_Result_XML_Root.attrib['status'].lower() == 'ok':
                Http_Request_Url2 = Http_Request_Result_XML_Root.find('images/cutouts/fits').text.strip()
                print(Http_Request_Url2)
                Http_Request_Get2 = Http_Request_Session.get(Http_Request_Url2)
                print(Http_Request_Get2)
                if Http_Request_Get2.status_code == 200:
                    with open(Output_Name+'.cutout.fits', 'wb') as fp:
                        for chunk in Http_Request_Get2.iter_content(chunk_size=1024):
                            if chunk: # filter out keep-alive new chunks, see -- https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
                                fp.write(chunk)
                                fp.flush()
                                os.fsync(fp.fileno())
                        # To read multi byte range request content, we need the help of requests_toolbelt.multipart.decoder.MultipartDecoder
                        #Http_Request_Content2 = MultipartDecoder.from_response(Http_Request_Get2) # see -- https://github.com/requests/toolbelt/blob/master/requests_toolbelt/multipart/decoder.py
                        #for part in Http_Request_Content2.parts:
                            #pprint(part.text())
                            #fp.write(part.content)
                print('')
                print('Output to "'+Output_Name+'.cutout.fits"!')





