#!/usr/bin/env python
# 
# Usage: 
#   cd /disk1/dzliu/../Calibrated_Images_by_Benjamin
#   get-meta-table.py "fits"
# 
# 

import os, sys, re, json, time, datetime, numpy as np, pkg_resources
pkg_resources.require('astropy')
#pkg_resources.require('PyYAML')
import astropy
from glob import glob
from astropy.table import Table
from astropy.table import unique
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy import constants as const
import subprocess
from threading import Thread
try: from queue import Queue
except ImportError:
    from Queue import Queue # Python 2.x # see https://stackoverflow.com/questions/9808714/control-the-number-of-subprocesses-using-to-call-external-commands-in-python


# see catalog cross-matching by sky coordinate -- http://docs.astropy.org/en/stable/coordinates/matchsep.html


script_to_get_pixel_histogram = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+os.sep+'Softwares'+os.sep+'a3cosmos_get_fits_image_pixel_histogram.py'



# 
# define functions
def Usage():
    print("Usage: ")
    print("    a3cosmos-ALMA-image-print-meta-table.py input_fits_directory [output_meta_table_file_name]")
    print("Input: ")
    print("    A directory containing the A3COSMOS fits images.")
    print("    For example, a \"fits/\" directory which contains:")
    print("    \"*_SB*_GB*_MB*.spw*.cont.I.image.fits\"")
    print("Output: ")
    print("    If the second argument is given, then an ASCII table named \"output_meta_table_file_name\" will be written.")
    print("")

def worker(queue):
    for cmd in iter(queue.get, None):
        print('cmd:', cmd)
        subprocess.check_call(cmd) # , stdout=outputfile, stderr=subprocess.STDOUT





# 
# main
if __name__ == '__main__':
    # 
    # Prepare arguments
    input_fits_directory = 'fits'
    output_meta_table_file_name = 'a3cosmos_meta_table'
    # 
    # Check user input
    if len(sys.argv) <= 0:
        Usage()
        sys.exit()
    # 
    # Read user input
    i = 1
    while i < len(sys.argv):
        tmp_str = sys.argv[i].lower().replace('--','-')
        if tmp_str != '':
            if input_fits_directory == '':
                input_fits_directory = sys.argv[i]
            elif output_meta_table_file_name == '':
                output_meta_table_file_name = sys.argv[i]
        i += 1
    # 
    # Check output_dir
    output_dir = os.path.dirname(output_meta_table_file_name)
    if output_dir != '.' and output_dir != '':
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
    # 
    # Prepare regex pattern
    regex_pattern_for_fits_file = re.compile(r'(.*?)_SB_(.*?)_GB_(.*?)_MB_(.*?)_(.*?)_sci\.spw(.*?)\.cont\.I\.image\.fits')
    # 
    # Process each ALMA image
    search_wildcard = '**_SB*_GB*_MB*.spw*.cont.I.image.fits'
    print('Searching "%s"' % (input_fits_directory+os.sep+search_wildcard) )
    if (sys.version_info.major == 3 and sys.version_info.minor >= 5) or (sys.version_info.major > 3):
        list_of_fits_files = glob(input_fits_directory+os.sep+search_wildcard, recursive=True)
    else:
        list_of_fits_files = glob(input_fits_directory+os.sep+search_wildcard)
    if len(list_of_fits_files) == 0:
        print('Error! Nothing found!')
        time.sleep(1.0)
        sys.exit()
    # 
    # Sort found fits files
    list_of_fits_files.sort()
    # 
    # loop found fits files to run the command to get pixel histogram
    i = 0
    commands = []
    for fits_file in list_of_fits_files:
        print(fits_file, '(%d/%d~%0.2f%%)'%(i+1,len(list_of_fits_files), float(i+1)/len(list_of_fits_files)*100.0) )
        i += 1
        # 
        # get pixel histogram
        if not os.path.isfile(fits_file+'.pixel.statistics.txt'):
            p = subprocess.Popen((script_to_get_pixel_histogram, fits_file) )
            (p_out, p_err) = p.communicate()
            if p.wait() !=0:
                print('Error occurred while running `%s %s`!' % (script_to_get_pixel_histogram, fits_file) )
                sys.exit()
            # 
            # multi-thread
            # see -- https://stackoverflow.com/questions/9808714/control-the-number-of-subprocesses-using-to-call-external-commands-in-python
            commands.append('%s %s' % (script_to_get_pixel_histogram, os.path.abspath(fits_file)) )
    ##if len(commands) > 0:
    ##    q = Queue()
    ##    limit = 2
    ##    threads = [Thread(target=worker, args=(q,)) for _ in range(limit)]
    ##    for t in threads: # start workers
    ##        t.daemon = True
    ##        t.start()
    ##    for cmd in commands: q.put_nowait(cmd) # feed commands to threads
    ##    for _ in threads: q.put(None) # signal no more commands
    ##    for t in threads: t.join()    # wait for completion
    # 
    # loop found fits files to get output_dict
    i = 0
    output_dicts = []
    for fits_file in list_of_fits_files:
        print(fits_file, '(%d/%d~%0.2f%%)'%(i+1,len(list_of_fits_files), float(i+1)/len(list_of_fits_files)*100.0))
        fits_name = os.path.basename(fits_file)
        # 
        # prepare output_dict
        output_dict = {}
        output_dict['image_dir'] = os.path.dirname(fits_file)
        output_dict['image_file'] = os.path.basename(fits_file)
        output_dict['image_name'] = re.sub(r'\.fits$', r'', output_dict['image_file'])
        # 
        # parse fits file name
        regex_match = regex_pattern_for_fits_file.match(output_dict['image_file'])
        output_dict['project'], \
        output_dict['SB'], \
        output_dict['GB'], \
        output_dict['MB'], \
        output_dict['source'], \
        output_dict['spw'] = regex_match.groups()
        # 
        # get pixel histogram
        if not os.path.isfile(fits_file+'.pixel.statistics.txt'):
            print('Error! "%s" was not found!' % (fits_file+'.pixel.statistics.txt') )
            sys.exit()
        with open(fits_file+'.pixel.statistics.txt', 'r') as fp:
            for line in fp:
                if re.match(r'^Gaussian_sigma *= *.+', line):
                    output_dict['rms'] = float(re.sub(r'Gaussian_sigma *= *([0-9eE.+-]+)', r'\1', line)) * 1e3 # mJy
        # 
        # get fits image headers
        fits_header = fits.getheader(fits_file)
        fits_wcs = WCS(fits_header, naxis=2)
        output_dict['beam_major'] = float(fits_header['BMAJ']) * 3600.0 # arcsec
        output_dict['beam_minor'] = float(fits_header['BMIN']) * 3600.0 # arcsec
        output_dict['beam_angle'] = float(fits_header['BPA']) # degree
        output_dict['frequency'] = float(fits_header['CRVAL3']) / 1e9 # GHz
        output_dict['wavelength'] = const.c.to('km/s').value/output_dict['frequency'] # um
        output_dict['OBJECT'] = fits_header['OBJECT']
        output_dict['OBSDATE'] = fits_header['DATE-OBS']
        output_dict['BMAJ'] = float(fits_header['BMAJ'])
        output_dict['BMIN'] = float(fits_header['BMIN'])
        output_dict['BPA'] = float(fits_header['BPA'])
        output_dict['primary_beam'] = 1.13 * output_dict['wavelength'] / (12.0*1e6) / np.pi * 180.0 * 3600.0 # ALMA 12m antenna primary beam FWHM, 1.13*w/D/pi*180*3600
        try: output_dict['mem_ous_id'] = fits_header['MEMBER']
        except: output_dict['mem_ous_id'] = 'N/A'
        try: output_dict['RMS_QA2'] = float(fits_header['RMS']) * 1e3 # mJy/beam
        except: output_dict['RMS_QA2'] = -99.0
        try: output_dict['ALMABAND'] = int(fits_header['ALMABAND'])
        except: output_dict['ALMABAND'] = int(-99)
        try: output_dict['BANDWIDTH'] = float(fits_header['BNDWDTH']) / 1e9 # GHz
        except: output_dict['BANDWIDTH'] = -99.0
        try: output_dict['SKYFREQ'] = float(fits_header['CRVAL3']) # Hz
        except: output_dict['SKYFREQ'] = -99.0
        try: output_dict['RESTFREQ'] = float(fits_header['RESTFREQ'])
        except: output_dict['RESTFREQ'] = -99.0
        try: output_dict['ROBUST'] = float(fits_header['ROBUST'])
        except: output_dict['ROBUST'] = -99.0
        output_dict['NAXIS1'] = float(fits_header['NAXIS1'])
        output_dict['NAXIS2'] = float(fits_header['NAXIS2'])
        output_dict['CENX'] = (float(fits_header['NAXIS1'])+1.0)/2.0
        output_dict['CENY'] = (float(fits_header['NAXIS2'])+1.0)/2.0
        output_dict['OBSRA'] = float(fits_header['OBSRA'])
        output_dict['OBSDEC'] = float(fits_header['OBSDEC'])
        tmppoints = np.array([ [output_dict['CENX'], output_dict['CENY']], 
                               [1,1],
                               [output_dict['NAXIS1'], 1],
                               [output_dict['NAXIS1'], output_dict['NAXIS2']],
                               [1, output_dict['NAXIS2']],
                             ])
        tmpRADECs = fits_wcs.wcs_pix2world(tmppoints, 1)
        output_dict['CENRA'],    \
        output_dict['CENDEC']    = tmpRADECs[0][0], tmpRADECs[0][1]
        output_dict['POS00_RA'], \
        output_dict['POS00_DEC'] = tmpRADECs[1][0], tmpRADECs[1][1]
        output_dict['POS10_RA'], \
        output_dict['POS10_DEC'] = tmpRADECs[2][0], tmpRADECs[2][1]
        output_dict['POS11_RA'], \
        output_dict['POS11_DEC'] = tmpRADECs[3][0], tmpRADECs[3][1]
        output_dict['POS01_RA'], \
        output_dict['POS01_DEC'] = tmpRADECs[4][0], tmpRADECs[4][1]
        POS00 = SkyCoord(output_dict['POS00_RA'], output_dict['POS00_DEC'], unit='deg') # defaults to ICRS frame
        POS11 = SkyCoord(output_dict['POS11_RA'], output_dict['POS11_DEC'], unit='deg') # defaults to ICRS frame
        dRA, dDEC = POS11.spherical_offsets_to(POS00) # see -- http://docs.astropy.org/en/stable/coordinates/matchsep.html
        output_dict['FoV_RA'] = np.abs(dRA.to(u.arcsec).value) # arcsec
        output_dict['FoV_DEC'] = np.abs(dDEC.to(u.arcsec).value) # arcsec
        output_dict['PIXSC1'] = proj_plane_pixel_scales(fits_wcs)[0] * 3600.0 # arcsec
        output_dict['PIXSC2'] = proj_plane_pixel_scales(fits_wcs)[1] * 3600.0 # arcsec
        # 
        #print(output_dict)
        output_dicts.append(output_dict)
        # 
        # debug
        #break
        i += 1
    # 
    # output_table
    output_table = Table()
    output_table
    k='project'     ; output_table[k] = [t[k] for t in output_dicts]
    k='SB'          ; output_table[k] = [t[k] for t in output_dicts]
    k='GB'          ; output_table[k] = [t[k] for t in output_dicts]
    k='MB'          ; output_table[k] = [t[k] for t in output_dicts]
    k='source'      ; output_table[k] = [t[k] for t in output_dicts]
    k='spw'         ; output_table[k] = [t[k] for t in output_dicts]
    k='rms'         ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'mJy/beam'; output_table[k].format = '%0.8f'
    k='beam_major'  ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'arcsec'; output_table[k].format = '%0.6f'
    k='beam_minor'  ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'arcsec'; output_table[k].format = '%0.6f'
    k='beam_angle'  ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.6f'
    k='frequency'   ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'GHz';    output_table[k].format = '%0.6f'
    k='wavelength'  ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'um';     output_table[k].format = '%0.6f'
    k='primary_beam'; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'arcmin^2'; output_table[k].format = '%0.6f'
    k='mem_ous_id'  ; output_table[k] = [t[k] for t in output_dicts]
    k='image_dir'   ; output_table[k] = [t[k] for t in output_dicts]
    k='image_file'  ; output_table[k] = [t[k] for t in output_dicts]
    k='image_name'  ; output_table[k] = [t[k] for t in output_dicts]
    k='OBJECT'      ; output_table[k] = [t[k] for t in output_dicts]
    k='OBSDATE'     ; output_table[k] = [t[k] for t in output_dicts]
    k='BMAJ'        ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.6e'
    k='BMIN'        ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.6e'
    k='BPA'         ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.6e'
    k='RMS_QA2'     ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'mJy/beam'; output_table[k].format = '%0.8f'
    k='ALMABAND'    ; output_table[k] = [t[k] for t in output_dicts]
    k='BANDWIDTH'   ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'GHz';    output_table[k].format = '%0.6f'
    k='SKYFREQ'     ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'GHz';    output_table[k].format = '%0.6f'
    k='ROBUST'      ; output_table[k] = [t[k] for t in output_dicts]
    k='NAXIS1'      ; output_table[k] = [t[k] for t in output_dicts]
    k='NAXIS2'      ; output_table[k] = [t[k] for t in output_dicts]
    k='CENX'        ; output_table[k] = [t[k] for t in output_dicts]
    k='CENY'        ; output_table[k] = [t[k] for t in output_dicts]
    k='OBSRA'       ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='OBSDEC'      ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='CENRA'       ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='CENDEC'      ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS00_RA'    ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS00_DEC'   ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS10_RA'    ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS10_DEC'   ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS11_RA'    ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS11_DEC'   ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS01_RA'    ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='POS01_DEC'   ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='FoV_RA'      ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='FoV_DEC'     ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'degree'; output_table[k].format = '%0.8f'
    k='PIXSC1'      ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'arcsec'; output_table[k].format = '%0.4f'
    k='PIXSC2'      ; output_table[k] = [t[k] for t in output_dicts]; output_table[k].unit = 'arcsec'; output_table[k].format = '%0.4f'
    print(output_table[['project','source','beam_major','beam_minor','beam_angle']])
    output_table.write(output_meta_table_file_name+'.fits', overwrite=True)
    output_table.write(output_meta_table_file_name+'.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'.fits') )
    print('Output to "%s"!' % (output_meta_table_file_name+'.txt') )
    
    output_table_uniq_projects = Table()
    output_table_uniq_projects['project'] = list(set(output_table['project']))
    output_table_uniq_projects.write(output_meta_table_file_name+'.uniq.projects.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'.uniq.projects.txt') )
    
    output_table_uniq_SB_GB_MB = astropy.table.unique(output_table, keys=['project','SB','GB','MB'])
    output_table_uniq_SB_GB_MB.write(output_meta_table_file_name+'.uniq.SB.GB.MB.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'.uniq.SB.GB.MB.txt') )
    
    
    
    
    
    
    # 
    # 
    # remove high-res beam<0.1
    output_table_without_highres = output_table[output_table['beam_major']>=0.1]
    output_table_without_highres.write(output_meta_table_file_name+'_beam_GE_0.1arcsec.fits', format='fits', overwrite=True)
    output_table_without_highres.write(output_meta_table_file_name+'_beam_GE_0.1arcsec.ipac', format='ipac', overwrite=True)
    output_table_without_highres.write(output_meta_table_file_name+'_beam_GE_0.1arcsec.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec.fits') )
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec.txt') )
    
    # unique
    output_table_uniq_projects = Table()
    output_table_uniq_projects['project'] = list(set(output_table_without_highres['project']))
    output_table_uniq_projects.write(output_meta_table_file_name+'_beam_GE_0.1arcsec.uniq.projects.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec.uniq.projects.txt') )
    
    # unique
    output_table_uniq_SB_GB_MB = astropy.table.unique(output_table_without_highres, keys=['project','SB','GB','MB'])
    output_table_uniq_SB_GB_MB.write(output_meta_table_file_name+'_beam_GE_0.1arcsec.uniq.SB.GB.MB.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec.uniq.SB.GB.MB.txt') )
    
    # also remove non-COSMOS sources
    COSMOS_SkyCoord = SkyCoord([150.1191666667]*u.deg, [2.2058333333]*u.deg) # TODO COSMOS field center coordinate
    output_table_without_highres_within_COSMOS = output_table_without_highres
    catalog_SkyCoord = SkyCoord(output_table_without_highres_within_COSMOS['CENRA'], output_table_without_highres_within_COSMOS['CENDEC'])
    idxc, idxcatalog, d2d, d3d = catalog_SkyCoord.search_around_sky(COSMOS_SkyCoord, 1.5*u.deg)
    output_table_without_highres_within_COSMOS = output_table_without_highres_within_COSMOS[idxcatalog]
    output_table_without_highres_within_COSMOS['Distance_to_COSMOS_field_center'] = d2d
    output_table_without_highres_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.fits', format='fits', overwrite=True)
    output_table_without_highres_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.ipac', format='ipac', overwrite=True)
    output_table_without_highres_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.fits') )
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.txt') )
    
    # unique
    output_table_uniq_projects_within_COSMOS = Table()
    output_table_uniq_projects_within_COSMOS['project'] = list(set(output_table_without_highres_within_COSMOS['project']))
    output_table_uniq_projects_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.uniq.projects.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.uniq.projects.txt') )
    
    # unique
    output_table_uniq_SB_GB_MB_within_COSMOS = astropy.table.unique(output_table_without_highres_within_COSMOS, keys=['project','SB','GB','MB'])
    output_table_uniq_SB_GB_MB_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.uniq.SB.GB.MB.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.1arcsec_within_COSMOS.uniq.SB.GB.MB.txt') )
    
    
    
    
    # 
    # 
    # remove high-res beam<0.2
    output_table_without_highres = output_table[output_table['beam_major']>=0.2]
    output_table_without_highres.write(output_meta_table_file_name+'_beam_GE_0.2arcsec.fits', format='fits', overwrite=True)
    output_table_without_highres.write(output_meta_table_file_name+'_beam_GE_0.2arcsec.ipac', format='ipac', overwrite=True)
    output_table_without_highres.write(output_meta_table_file_name+'_beam_GE_0.2arcsec.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec.fits') )
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec.txt') )
    
    # unique
    output_table_uniq_projects = Table()
    output_table_uniq_projects['project'] = list(set(output_table_without_highres['project']))
    output_table_uniq_projects.write(output_meta_table_file_name+'_beam_GE_0.2arcsec.uniq.projects.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec.uniq.projects.txt') )
    
    # unique
    output_table_uniq_SB_GB_MB = astropy.table.unique(output_table_without_highres, keys=['project','SB','GB','MB'])
    output_table_uniq_SB_GB_MB.write(output_meta_table_file_name+'_beam_GE_0.2arcsec.uniq.SB.GB.MB.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec.uniq.SB.GB.MB.txt') )
    
    # also non-COSMOS sources
    output_table_without_highres_within_COSMOS = output_table_without_highres
    catalog_SkyCoord = SkyCoord(output_table_without_highres_within_COSMOS['CENRA'], output_table_without_highres_within_COSMOS['CENDEC'])
    idxc, idxcatalog, d2d, d3d = catalog_SkyCoord.search_around_sky(COSMOS_SkyCoord, 1.5*u.deg)
    output_table_without_highres_within_COSMOS = output_table_without_highres_within_COSMOS[idxcatalog]
    output_table_without_highres_within_COSMOS['Distance_to_COSMOS_field_center'] = d2d
    output_table_without_highres_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.fits', format='fits', overwrite=True)
    output_table_without_highres_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.ipac', format='ipac', overwrite=True)
    output_table_without_highres_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.fits') )
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.txt') )
    
    # unique
    output_table_uniq_projects_within_COSMOS = Table()
    output_table_uniq_projects_within_COSMOS['project'] = list(set(output_table_without_highres_within_COSMOS['project']))
    output_table_uniq_projects_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.uniq.projects.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.uniq.projects.txt') )
    
    # unique
    output_table_uniq_SB_GB_MB_within_COSMOS = astropy.table.unique(output_table_without_highres_within_COSMOS, keys=['project','SB','GB','MB'])
    output_table_uniq_SB_GB_MB_within_COSMOS.write(output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.uniq.SB.GB.MB.txt', format='ascii.fixed_width_two_line', overwrite=True)
    print('Output to "%s"!' % (output_meta_table_file_name+'_beam_GE_0.2arcsec_within_COSMOS.uniq.SB.GB.MB.txt') )
    
    
    
    
    
    
    
    
    


