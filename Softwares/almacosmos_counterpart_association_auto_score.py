#!/usr/bin/env python
# 
# 
# Last update:
#     20170302 numpy.sqrt()*background_sigma
#     20170308 (1) we find that the image pixel rms underestimates the flux error, as there are some background variation across images like ACS, so we decide to multiply a factor of 2 to the background_sigma. 
#              (2) for down-weighting the offset/Separation with the extended-parameter, we should only apply when image S/N > 3. And the way we calculate the extended-parameter changed from S/N_(largest_ellipse) / S/N_(smallest_ellipse) to S/N_(largest ellp. S/N>2) / S/N_(smallest ellip. S/N>2). 
#              (3) fixed "== numpy.nan" thing. Because "numpy.nan == numpy.nan" is False, if a value is nan, it does not equal to itself. 
#              (4) output "Source.Photometry['ALMA S/N']" to the output text file.
#              (5) measure peak pixel position within each ellipse -- this needs to modify "caap_python_lib_image.py" "elliptical_Photometry"
#     20170428 (1) now use Highz_Image class in 'caap_python_lib_highz.py', simplified code here
#              (2) now we do not directly use image S/N for P. Score, but use Source/RefSource flux ratio and only apply when image S/N >= 5.0, 
#              (3) now we do not apply a factor of 2 to the background_sigma. 
#              (4) now we do not measure a series of different size ellipses, but measure a series of ellipses distribution from Source position to RefSource position. 
#              (5) for computing ['Extended'], we do not use Outer/Inner ratio now, but use 'polyfit' 'Overall slope'. 
#     20180607 (1) renamed from '/Users/dzliu/Cloud/Github/Crab.Toolkit.CAAP/bin/caap_highz_galaxy_crossmatcher_v8.py' and moved to '/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/almacosmos_counterpart_association_auto_score_v8.py'
#              (2) updated from '/Users/dzliu/Cloud/Github/Crab.Toolkit.CAAP/bin/caap_highz_galaxy_crossmatcher_v9.py'
#              (3) 
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy>=1.3")
pkg_resources.require("matplotlib")
pkg_resources.require("wcsaxes") # http://wcsaxes.readthedocs.io/en/latest/getting_started.html

import os
import sys
import re
import glob
import json
import inspect
import subprocess
import math
import numpy
import astropy
from astropy import units
from astropy.io import fits
from astropy.wcs import WCS
from pprint import pprint
#from scipy import spatial
#from scipy.spatial import KDTree

import matplotlib
import platform

matplotlib.use('TkAgg')

#if platform.system() == 'Darwin':
#    matplotlib.use('Qt5Agg')
#else:
#    matplotlib.use('TkAgg')

from matplotlib import pyplot
from matplotlib.colors import hex2color, rgb2hex
from matplotlib.patches import Ellipse, Circle, Rectangle
from astropy.visualization import astropy_mpl_style
from astropy.visualization import MinMaxInterval, PercentileInterval, AsymmetricPercentileInterval, SqrtStretch, PowerStretch, ImageNormalize # ImageNormalize requires astropy>=1.3
import scipy
import skimage # pip-3.6 install --user scikit-image
from skimage.exposure import rescale_intensity
from skimage.feature import peak_local_max
from itertools import groupby
from operator import itemgetter
from copy import copy
import shutil
from datetime import datetime

sys_path_to_add = os.path.dirname(__file__) + os.sep + 'lib_python'
if not sys_path_to_add in sys.path:
    print('Adding sys.path "%s"'%(sys_path_to_add))
    sys.path.append(sys_path_to_add)

sys_path_to_add = os.path.dirname(__file__) + os.sep + 'lib_python_dzliu'
if not sys_path_to_add in sys.path:
    print('Adding sys.path "%s"'%(sys_path_to_add))
    sys.path.append(sys_path_to_add)

from almacosmos_python_lib_highz import *
from almacosmos_python_lib_image import *
from almacosmos_python_lib_telescopes import *
from crablogger.CrabLogger import *
from crabgaussian.CrabGaussian import *








#pyplot.rcParams['font.family'] = 'NGC'
pyplot.rcParams['font.size'] = 13
pyplot.rcParams['axes.labelsize'] = 'large'
#pyplot.rcParams['axes.labelpad'] = 5.0
#pyplot.rcParams['ytick.major.pad'] = 10 # padding between ticks and axis
pyplot.rcParams['xtick.minor.visible'] = True # 
pyplot.rcParams['ytick.minor.visible'] = True # 
pyplot.rcParams['figure.figsize'] = 20, 18
pyplot.style.use(astropy_mpl_style)


# stretch_sqrt = SqrtStretch()
# Image2 = stretch_sqrt(Image)

# from matplotlib.colors import LogNorm
# pyplot.imshow(image_data, cmap='gray', norm=LogNorm())

















# 20170427
# The idea of this code is to make an auto-identification 
# of two sources being the same galaxy or not. 
# So we will base on 
#     (1) InputSource position
# 
# 
# 
class CrossMatch_Identifier(object):
    # 
    # 
    def __init__(self, Source, RefSource, RefImage, RefCatalog=None, MatchCatalog=None, Separation=numpy.nan):
        # 
        # Prepare variables
        self.Source = Source
        self.RefSource = RefSource
        self.RefImage = RefImage
        self.RefCatalog = RefCatalog # this is a big reference catalog for calculating Crowdedness and Clean_Index. 
        self.MatchCatalog = MatchCatalog # this is the cross-match catalog with Separation, ID_1, RA_1, Dec_1, ID_2, RA_2, Dec_2, in case no input Source and RefSource. <TODO>
        # 
        # Get RefImage.FitsImageFile
        if self.RefImage.isValid():
            self.FitsImageFile = self.RefImage.FitsImageFile
        else:
            self.FitsImageFile = ''
        # 
        # Calculate Crowdedness and Clean_Index
        if self.RefCatalog is not None:
            self.Crowdedness = self.RefCatalog.calc_crowdedness(self.Source.RA, self.Source.Dec, 3.0)
            self.Clean_Index = self.RefCatalog.calc_clean_index(self.Source.RA, self.Source.Dec, 1.5)
        else:
            self.Crowdedness = numpy.nan
            self.Clean_Index = numpy.nan
        # 
        # Read Separation
        self.MatchSeparation = Separation
        self.MatchScore = -99
        # 
        # Prepare more variables
        self.Morphology = {
                'Separation': numpy.nan, 
                'Angle': numpy.nan, 
                'SepDist': numpy.nan, 
                'SepAngle': numpy.nan, 
                'Projected_Source_Radius': numpy.nan, 
                'PosAngle': numpy.nan, 
                'Extended': 0.0, 
                'Crowdedness': self.Crowdedness, 
                'Clean_Index': self.Clean_Index, 
                'Score': 0.0, 
        }
        # 
        self.Photometry = {
                'Position': [], 
                'Centroid': [], 
                'Flux': 0.0, 
                'FluxError': 0.0, 
                'FluxBias': 0.0, 
                'S/N': 0.0, 
                'Source/RefSource': 0.0, 
                'EnclosedPower': [], 
                'GrowthCurve': [], 
                'Score': 0.0, 
        }
        # 
        self.World = {}
    # 
    # 
    def about(self):
        # 
        # get variable name 
        # -- see http://stackoverflow.com/questions/1690400/getting-an-instance-name-inside-class-init
        self.World['My Name'] = ""
        self.World['My Names'] = []
        tmp_frame = inspect.currentframe().f_back
        tmp_variables = dict(tmp_frame.f_globals.items() + tmp_frame.f_locals.items())
        for tmp_name, tmp_variable in tmp_variables.items():
            if isinstance(tmp_variable, self.__class__):
                if hash(self) == hash(tmp_variable):
                    self.World['My Names'].append(tmp_name)
        if len(self.World['My Names']) > 0:
            self.World['My Name'] = self.World['My Names'][0]
        # 
        # print crossmatcher info
        tmp_str_max_length = 0
        if tmp_str_max_length < len(self.World['My Name']+' '):
            tmp_str_max_length = len(self.World['My Name']+' ')
        tmp_str_source = self.Source.Field+'--'+self.Source.Name+'--'+str(self.Source.SubID)
        if tmp_str_max_length < len(self.FitsImageFile):
            tmp_str_max_length = len(self.FitsImageFile)
        if tmp_str_max_length < len(tmp_str_source):
            tmp_str_max_length = len(tmp_str_source)
        tmp_str_format_fixedwidth = '{0:<%d}'%(tmp_str_max_length)
        tmp_str_format_filleddash = '{0:-<%d}'%(tmp_str_max_length)
        print("")
        print(' |---------------- %s-|'%( tmp_str_format_filleddash.format(self.World['My Name']+' ')         ))
        print(' |        Source | %s |'%( tmp_str_format_fixedwidth.format(tmp_str_source)                    ))
        print(' | FitsImageFile | %s |'%( tmp_str_format_fixedwidth.format(self.FitsImageFile)                ))
        print(' |-----------------%s-|'%( tmp_str_format_filleddash.format('-')                               ))
        print("")
    # 
    # 
    def match_morphology(self, OutputDir='results', OutputName='', Overwrite=False, FoV=12.0):
        # 
        if self.Source and self.RefSource and self.RefImage:
            # 
            # check output directory
            if not os.path.isdir(OutputDir):
                os.mkdir(OutputDir)
            # 
            # check Source data structure
            if not self.Source.Field:
                print("Error! \"Source\" does not have \"Field\" info!")
                return
            if not self.Source.Name:
                print("Error! \"Source\" does not have \"Name\" info!")
                return
            #if not self.Source.ID:
            #    print("Error! \"Source\" does not have \"ID\" info!")
            #    return
            if not self.Source.SubID:
                print("Error! \"Source\" does not have \"SubID\" info!")
                return
            if not 'Major Axis' in self.Source.Morphology:
                print("Error! \"Source.Morphology\" does not have \"Major Axis\" info!")
                return
            if not 'Minor Axis' in self.Source.Morphology:
                print("Error! \"Source.Morphology\" does not have \"Minor Axis\" info!")
                return
            if not 'Pos Angle' in self.Source.Morphology:
                print("Error! \"Source.Morphology\" does not have \"Pos Angle\" info!")
                return
            # 
            # check FitsImageFile
            if not self.RefImage.isValid():
                print("Error! The RefImage is invalid!")
                return
            # 
            # recognize Instrument and Telescope from the fits image file name
            StrInstrument, StrTelescope = recognize_Instrument(self.FitsImageFile)
            if len(StrInstrument) == 0 or len(StrTelescope) == 0:
                print("Error! Failed to recognize Instrument and Telescope info from the input fits image file name: \"%s\"!"%(self.FitsImageFile))
                pyplot.pause(3.0)
                return
            # 
            # prepare output figure and text file names
            if OutputName == '':
                OutputName = self.Source.Field+'--'+str(self.Source.Name)+'--'+str(self.Source.SubID)
            PlotOutput = OutputDir+'/'+OutputName+'--'+StrTelescope+'--'+StrInstrument.replace(' ','-')+'.pdf'
            TextOutput = OutputDir+'/'+OutputName+'--'+StrTelescope+'--'+StrInstrument.replace(' ','-')+'.txt'
            LoggOutput = OutputDir+'/'+OutputName+'--'+StrTelescope+'--'+StrInstrument.replace(' ','-')+'.log'
            LockOutput = OutputDir+'/'+OutputName+'--'+StrTelescope+'--'+StrInstrument.replace(' ','-')+'.lock' #<TODO># 
            # 
            # check previous crossmatch results
            if os.path.isfile(TextOutput):
                # 
                # <20170224> added a check step to make sure our scores do not have nan
                with open(TextOutput, 'r') as fp:
                    temp_Score_Total = numpy.nan
                    temp_Score_Morph = numpy.nan
                    temp_Score_Photo = numpy.nan
                    temp_Score_Exten = numpy.nan
                    for lp in fp:
                        if lp.startswith('Match.Score'):
                            temp_Score_Total = (lp.split('=')[1]).split('#')[0]
                        elif lp.startswith('Match.Morphology.Score'):
                            temp_Score_Morph = (lp.split('=')[1]).split('#')[0]
                        elif lp.startswith('Match.Photometry.Score'):
                            temp_Score_Photo = (lp.split('=')[1]).split('#')[0]
                        elif lp.startswith('Match.Morphology.Extended'):
                            temp_Score_Exten = (lp.split('=')[1]).split('#')[0]
                    fp.close()
                    if math.isnan(float(temp_Score_Total)) or \
                       math.isnan(float(temp_Score_Morph)) or \
                       math.isnan(float(temp_Score_Photo)) or \
                       math.isnan(float(temp_Score_Exten)) :
                        print("Warning! Previous crossmatching result \"%s\" contains \"nan\"! Will redo the crossmatching due to NaN values found!"%(TextOutput))
                        Overwrite = True
                        pyplot.pause(2.0)
                #if(TextOutput.find('22721')>=0):
                #    pyplot.pause(2.0)
                if not Overwrite:
                    print("Found previous crossmatching result: \"%s\"! Will not redo the crossmatching unless the \"overwrite\" option are input!"%(TextOutput))
                    return
            # 
            # begin Logger
            if 'Output_Logger' in globals():
                Output_Logger.begin_log_file(filename=LoggOutput, mode='w')
            # 
            # do morphology check
            # -- we will create a series of ellipse from Source position to RefSource position
            # -- then check the morphological extent
            if True:
                # 
                # plot image
                self.RefImage.plot(
                        zoom_size = float(FoV)/self.RefImage.PixScale, 
                        zoom_center = self.RefImage.sky2xy(self.Source.RA, self.Source.Dec)
                    )
                # 
                # add annotation at top-left
                self.RefImage.text('%s %s'%(StrTelescope,StrInstrument), fontsize=15, color=hex2color('#00CC00'), align_top_left=True)
                self.RefImage.text('FoV %.1f arcsec'%(self.RefImage.ZoomSize[1]*self.RefImage.PixScale[1]), fontsize=14, color=hex2color('#00CC00'), align_top_left=True)
                # 
                # add annotation at top-right
                self.RefImage.text('%s--%s--%s'%(self.Source.Field,str(self.Source.Name),str(self.Source.SubID)), fontsize=15, align_top_right=True, horizontalalignment='right')
                for refname in self.RefSource.Names.keys():
                    self.RefImage.text('%s ID %s'%(refname,str(self.RefSource.Names.get(refname))), color=hex2color('#FF0000'), fontsize=15, align_top_right=True, horizontalalignment='right')
                self.RefImage.text('zp = %.3f'%(self.Source.Redshifts['zphot_1']), color=hex2color('#FF0000'), fontsize=14, align_top_right=True, horizontalalignment='right')
                # 
                # 
                # create source_aperture and refsource_aperture
                #diameters = numpy.array(range(1,10)) * 0.25 # x0.25 to x2.25 FWHM
                diameters = [1.0]
                for diameter in diameters:
                    if '%0.2fxFWHM'%(diameter) == '1.00xFWHM':
                        edgealpha = 1.00
                        facealpha = 0.05
                        linewidth = 2.5
                        zorder = 9
                    else:
                        edgealpha = numpy.min([diameter/1.0,1.0/diameter]) * 0.8
                        facealpha = 0.0
                        linewidth = 1.0
                        zorder = 11
                    # 
                    self.RefImage.aper(
                        radec = [ self.Source.RA, self.Source.Dec ], 
                        major = diameter * self.Source.Morphology['Major Axis'], 
                        minor = diameter * self.Source.Morphology['Minor Axis'], 
                        angle = self.Source.Morphology['Pos Angle'], 
                        edgecolor = hex2color('#00FF00'), 
                        facecolor = hex2color('#00FF00'), 
                        linewidth = linewidth, 
                        edgealpha = edgealpha, 
                        facealpha = facealpha, 
                        zorder = zorder, 
                        label = 'source position %0.2fxFWHM'%(diameter)
                    )
                # 
                # create refsource_aperture
                for diameter in diameters:
                    if '%0.2fxFWHM'%(diameter) == '1.00xFWHM':
                        linewidth = 2.5
                        color = hex2color('#FF0000')
                        draw_cross = True
                        zorder = 8
                    else:
                        linewidth = 1.0
                        color = 'none'
                        draw_cross = False
                        zorder = 12
                    # 
                    self.RefImage.aper(
                        radec = [ self.RefSource.RA, self.RefSource.Dec ], 
                        major = diameter * self.Source.Morphology['Major Axis'], 
                        minor = diameter * self.Source.Morphology['Minor Axis'], 
                        angle = self.Source.Morphology['Pos Angle'], 
                        linewidth = linewidth, 
                        color = color, 
                        draw_ellipse = False, 
                        draw_cross = draw_cross, 
                        zorder = zorder, 
                        label = 'refsource position %0.2fxFWHM'%(diameter)
                    )
                # 
                # 
                # store source_aperture and refsource_aperture
                source_aperture = self.RefImage.get_aperture_by_label('source position 1.00xFWHM')
                refsource_aperture = self.RefImage.get_aperture_by_label('refsource position 1.00xFWHM')
                # 
                # 
                # compute variables
                flux_ratio_source_to_refsource = numpy.nan
                signal_to_noise_ratio_source = numpy.nan
                signal_to_noise_ratio_refsource = numpy.nan
                surface_brightness_source = numpy.nan
                flux_ratio_source_to_refsource = (source_aperture['Flux']-source_aperture['Background']) / (refsource_aperture['Flux']-refsource_aperture['Background'])
                signal_to_noise_ratio_source = (source_aperture['Flux']-source_aperture['Background']) / (source_aperture['Noise'])
                signal_to_noise_ratio_refsource = (refsource_aperture['Flux']-refsource_aperture['Background']) / (refsource_aperture['Noise'])
                surface_brightness_source = (source_aperture['Flux']-source_aperture['Background']) / (source_aperture['Area']) # flux unit per arcsec-square
                # 
                # store into 'self.Photometry[]' data structure
                self.Photometry['Flux'] = (source_aperture['Flux']-source_aperture['Background'])
                self.Photometry['FluxError'] = source_aperture['Noise']
                self.Photometry['S/N'] = self.Photometry['Flux'] / self.Photometry['FluxError']
                self.Photometry['Position'] = [source_aperture['RA'], source_aperture['Dec']]
                self.Photometry['Centroid'] = source_aperture['Centroid']
                if signal_to_noise_ratio_source >= 3.0 or signal_to_noise_ratio_refsource >= 3.0:
                    self.Photometry['Source/RefSource'] = flux_ratio_source_to_refsource
                else:
                    self.Photometry['Source/RefSource'] = -99
                # 
                # 
                # calc the Separation between Source and RefSource
                sep_x = (refsource_aperture['X'] - source_aperture['X']) * self.RefImage.PixScale[0]
                sep_y = (refsource_aperture['Y'] - source_aperture['Y']) * self.RefImage.PixScale[1]
                SepDist = numpy.sqrt( sep_x**2 + sep_y**2 ) # in arcsec
                SepAngle = numpy.arctan2(sep_y, sep_x) / numpy.pi * 180.0
                PosAngle = self.Source.Morphology['Pos Angle']
                print("Source position %.3f %.3f"%(source_aperture['X'], source_aperture['Y']))
                print("RefSource position %.3f %.3f"%(refsource_aperture['X'], refsource_aperture['Y']))
                print("Separated distance x y %0.3f %0.3f"%(sep_x, sep_y))
                print("RefSource to Source has a SepDist=%.3f [arcsec] and SepAngle=%.1f [degree], comparing to Source Morphology PosAngle=%.1f [degree]."%(SepDist,SepAngle,self.Source.Morphology['Pos Angle']))
                if not numpy.isnan(self.MatchSeparation):
                    print("Comparing to the Catalog Separation=%.3f [arcsec]."%(self.MatchSeparation))
                # 
                # 
                # create a series of ellipses from Source position to RefSource position
                jiggle_number = 5
                self.Photometry['GrowthCurve'] = [ {
                        'PosX': source_aperture['X'], 
                        'PosY': source_aperture['Y'], 
                        'x': float(0.0)/float(jiggle_number+1), 
                        'y': (source_aperture['Flux']-source_aperture['Background']) / (source_aperture['Flux']-source_aperture['Background']), 
                        'err': (source_aperture['Noise']), 
                        'area': (source_aperture['Area'])
                } ]
                for jiggle_i in range(jiggle_number):
                    jiggle_pos_x = source_aperture['X'] + (refsource_aperture['X'] - source_aperture['X']) / (jiggle_number+1) * (jiggle_i+1)
                    jiggle_pos_y = source_aperture['Y'] + (refsource_aperture['Y'] - source_aperture['Y']) / (jiggle_number+1) * (jiggle_i+1)
                    # 
                    edgealpha = 0.8 / numpy.sqrt(jiggle_i+1)
                    facealpha = 0.0
                    linewidth = 1.0
                    zorder = 11
                    # 
                    self.RefImage.aper(
                        position = [ jiggle_pos_x, jiggle_pos_y ], 
                        major = source_aperture['Major'], 
                        minor = source_aperture['Minor'], 
                        angle = self.Source.Morphology['Pos Angle'], 
                        edgecolor = hex2color('#00FF00'), 
                        facecolor = hex2color('#00FF00'), 
                        linewidth = linewidth, 
                        edgealpha = edgealpha, 
                        facealpha = facealpha, 
                        zorder = zorder, 
                        label = 'jiggle position %d'%(jiggle_i+1)
                    )
                    # 
                    # get jiggle_aperture
                    jiggle_aperture = self.RefImage.get_aperture_by_label('jiggle position %d'%(jiggle_i+1))
                    # 
                    # store in to (self.Photometry['GrowthCurve'])
                    self.Photometry['GrowthCurve'].append( {
                        'PosX': jiggle_pos_x, 
                        'PosY': jiggle_pos_y, 
                        'x': float(jiggle_i+1)/float(jiggle_number+1), 
                        'y': (jiggle_aperture['Flux']-jiggle_aperture['Background']) / (source_aperture['Flux']-source_aperture['Background']), 
                        'err': (jiggle_aperture['Noise']), 
                        'area': (jiggle_aperture['Area'])
                    } )
                # 
                # append RefSource position photometry to the (self.Photometry['GrowthCurve'])
                self.Photometry['GrowthCurve'].append( {
                    'PosX': refsource_aperture['X'], 
                    'PosY': refsource_aperture['Y'], 
                    'x': float(jiggle_number+1)/float(jiggle_number+1), 
                    'y': (refsource_aperture['Flux']-refsource_aperture['Background']) / (source_aperture['Flux']-source_aperture['Background']), 
                    'err': (refsource_aperture['Noise']), 
                    'area': (refsource_aperture['Area'])
                } )
                # 
                # print source position photometry S/N info
                self.Photometry['EnclosedPower'] = []
                for dia in range(len(diameters)):
                    temp_aperture = self.RefImage.get_aperture_by_label('source position %0.2fxFWHM'%(diameters[dia]))
                    self.Photometry['EnclosedPower'].append( {
                        'x': diameters[dia], 
                        'y': (temp_aperture['Flux']-temp_aperture['Background']), 
                        'err': (temp_aperture['Noise']), 
                        'area': (temp_aperture['Area'])
                    } )
                    print('Source image source position major=%0.2fxFWHM aperture has flux = %0.6g +- %0.6g and S/N = %0.3f (area = %0.6g arcsec^2)'%(self.Photometry['EnclosedPower'][dia]['x'], self.Photometry['EnclosedPower'][dia]['y'], self.Photometry['EnclosedPower'][dia]['err'], self.Photometry['EnclosedPower'][dia]['y']/self.Photometry['EnclosedPower'][dia]['err'], self.Photometry['EnclosedPower'][dia]['area']))
                ## 
                ## print surface brightness S/N info, normalize (self.Photometry['GrowthCurve']) by 'surface_brightness_source'
                #for dia in range(len(diameters)):
                #    print('Source image annulus with diameter %0.2fxFWHM has surface brightness = %0.6g +- %0.6g and S/N = %0.3f (area = %0.6g)'%(self.Photometry['GrowthCurve'][dia]['x'], self.Photometry['GrowthCurve'][dia]['y'], self.Photometry['GrowthCurve'][dia]['err'], self.Photometry['GrowthCurve'][dia]['y']/self.Photometry['GrowthCurve'][dia]['err'], self.Photometry['GrowthCurve'][dia]['area']))
                # 
                # print jiggle position photometry info
                for dia in range(jiggle_number+2):
                    print('Source image jiggle position %0.2fxSep. aperture has flux = %0.6g +- %0.6g and S/N = %0.3f (area = %0.6g arcsec^2)'%(self.Photometry['GrowthCurve'][dia]['x'], self.Photometry['GrowthCurve'][dia]['y'], self.Photometry['GrowthCurve'][dia]['err'], self.Photometry['GrowthCurve'][dia]['y']/self.Photometry['GrowthCurve'][dia]['err'], self.Photometry['GrowthCurve'][dia]['area']))
                # 
                # 
                # 
                # calculate source mophological extension parameter (only when source S/N >= 3.0)
                source_extent_snr_limit = 3.0
                source_extent = {}
                source_extent['Inner slope'] = numpy.nan
                source_extent['Outer slope'] = numpy.nan
                source_extent['Middle slope'] = numpy.nan
                source_extent['Overall slope'] = numpy.nan
                if signal_to_noise_ratio_source >= source_extent_snr_limit:
                    # print info
                    print('Calculating source mophological extension parameter with surface brightness radial profile')
                    # linear regression
                    fitting_data_x = [ (t['x']) for t in self.Photometry['GrowthCurve'] ]
                    fitting_data_y = [ (t['y']) for t in self.Photometry['GrowthCurve'] ]
                    fitting_weights = [ 1.0/(t['err'])**2 for t in self.Photometry['GrowthCurve'] ]
                    fitting_poly_deg = 1
                    fitting_data_inner = numpy.array(range(long(len(fitting_data_x)/2)))
                    fitting_data_outer = numpy.array(range(long(len(fitting_data_x)/2)) + numpy.array(long(len(fitting_data_x)/2)))
                    fitting_data_middle = numpy.array(range(long(len(fitting_data_x)/2)) + numpy.array(long(len(fitting_data_x)/4)))
                    fitting_data_overall = numpy.array(range(long(len(fitting_data_x))))
                    fitting_data_inner = fitting_data_inner.astype(long)
                    fitting_data_outer = fitting_data_outer.astype(long)
                    fitting_data_middle = fitting_data_middle.astype(long)
                    fitting_data_overall = fitting_data_overall.astype(long)
                    fitting_data_x = numpy.array(fitting_data_x)
                    fitting_data_y = numpy.array(fitting_data_y)
                    fitting_weights = numpy.array(fitting_weights)
                    fitting_coeff_inner = numpy.polynomial.polynomial.polyfit(fitting_data_x[fitting_data_inner], fitting_data_y[fitting_data_inner], fitting_poly_deg, rcond=None, full=False, w=fitting_weights[fitting_data_inner])
                    fitting_coeff_outer = numpy.polynomial.polynomial.polyfit(fitting_data_x[fitting_data_outer], fitting_data_y[fitting_data_outer], fitting_poly_deg, rcond=None, full=False, w=fitting_weights[fitting_data_outer])
                    fitting_coeff_middle = numpy.polynomial.polynomial.polyfit(fitting_data_x[fitting_data_middle], fitting_data_y[fitting_data_middle], fitting_poly_deg, rcond=None, full=False, w=fitting_weights[fitting_data_middle])
                    fitting_coeff_overall = numpy.polynomial.polynomial.polyfit(fitting_data_x[fitting_data_overall], fitting_data_y[fitting_data_overall], fitting_poly_deg, rcond=None, full=False, w=fitting_weights[fitting_data_overall])
                    #pprint(self.Photometry['GrowthCurve'])
                    #pprint(fitting_coeff_inner)
                    #pprint(fitting_coeff_outer)
                    #pprint(fitting_coeff_middle)
                    #pprint(fitting_coeff_overall)
                    source_extent['Inner slope'] = fitting_coeff_inner[fitting_poly_deg] # [fitting_poly_deg] is the slope, see -- https://docs.scipy.org/doc/numpy-dev/reference/generated/numpy.polynomial.polynomial.polyfit.html
                    source_extent['Outer slope'] = fitting_coeff_outer[fitting_poly_deg]
                    source_extent['Middle slope'] = fitting_coeff_middle[fitting_poly_deg]
                    source_extent['Overall slope'] = fitting_coeff_overall[fitting_poly_deg]
                    print('Source mophological extent profile Inner slope = %0.3f, intercept = %0.6g'%(source_extent['Inner slope'],fitting_coeff_inner[0]))
                    print('Source mophological extent profile Outer slope = %0.3f, intercept = %0.6g'%(source_extent['Outer slope'],fitting_coeff_outer[0]))
                    print('Source mophological extent profile Middle slope = %0.3f, intercept = %0.6g'%(source_extent['Middle slope'],fitting_coeff_middle[0]))
                    print('Source mophological extent profile Overall slope = %0.3f, intercept = %0.6g'%(source_extent['Overall slope'],fitting_coeff_overall[0]))
                    # 
                    if fitting_poly_deg == 1:
                        #self.Morphology['Extended'] = (fitting_coeff_overall[0]+fitting_coeff_overall[1])/(fitting_coeff_overall[0]) * 100.0 # y[x=1]/y[x=0]
                        self.Morphology['Extended'] = (fitting_coeff_overall[0]+fitting_coeff_overall[1]) * 100.0 # y[x=1]/y[x=0] #<TODO># (fitting_coeff_overall[0]) sometimes is negative!
                    # 
                    print('Source mophological extent profile Aperture list: ')
                    pprint(self.Photometry['GrowthCurve'])
                    # 
                    #if False:
                    #    # 
                    #    # select only S/N>=3.0 surface brightness data points then compute the ratio between first annulus and last annulus (S/N>=3.0). 
                    #    fitting_data_x = [ (t['x'])   for t in self.Photometry['GrowthCurve'] if t['y']>=3.0*t['err'] ]
                    #    fitting_data_y = [ (t['y'])   for t in self.Photometry['GrowthCurve'] if t['y']>=3.0*t['err'] ]
                    #    fitting_errors = [ (t['err']) for t in self.Photometry['GrowthCurve'] if t['y']>=3.0*t['err'] ]
                    #    # 
                    #    if len(fitting_data_y) <= 1: 
                    #        self.Morphology['Extended'] = -99 # too low S/N in the image
                    #        print('Source mophological extent profile S/N>=3.0 Outer/Inner Aperture number is less than 2! Will not be able to do further calculation!')
                    #    else:
                    #        self.Morphology['Extended'] = fitting_data_y[-1] / fitting_data_y[0] * 100.0
                    #        print('Source mophological extent profile S/N>=3.0 Outer/Inner Aperture flux ratio = %0.3f (jiggle position %0.0f and %0.0f)'%(fitting_data_y[-1] / fitting_data_y[0], fitting_data_x[-1], fitting_data_x[0]))
                    #        print('Source mophological extent profile S/N>=3.0 Outer/Inner Aperture list: ')
                    #        pprint(self.Photometry['GrowthCurve'])
                else:
                    print('The source S/N is lower than %0.1f (undetected)! Will not be able to calcuate the source mophological extent parameter!'%(source_extent_snr_limit))
                # 
                # 
                #<20170304><dzliu><plang># down-weight the offset so as to improve the score
                offset_down_weighting = 1.0
                if signal_to_noise_ratio_source >= source_extent_snr_limit:
                    if self.Morphology['Extended'] > 0 and self.Morphology['Extended'] == self.Morphology['Extended']:
                        # -- <20170308> only down-weight if source image S/N>5.0
                        # -- <20170430> down-weight extended source Separation, so that when source is fully extended (Outer/Inner=100%), M. Score = 100. 
                        # -- <20170430> now the 'Extended' parameter is just the Outer/Inner flux ratio, 1.0 = 100% means we do not downweight the SepDist, otherwise we do the downweighting. 
                        offset_down_weighting = 1.0 / (self.Morphology['Extended']/100.0)
                        if offset_down_weighting < 0.0:
                            offset_down_weighting = 0.0
                        #if self.Morphology['Extended'] > 100.0:
                        #    offset_down_weighting = numpy.min([numpy.max([self.Morphology['Extended']/100.0, 1.0]), 3.0]) 
                        #    # <TODO> down weighting the offset (SepDist) by at most a factor of 3
                # 
                # 
                # 
                # 
                # 
                # 
                # 
                # calc match quality -- get a score
                self.Morphology['SepDist'] = SepDist # 
                self.Morphology['SepAngle'] = SepAngle # 
                self.Morphology['PosAngle'] = PosAngle # 
                self.Morphology['Separation'] = SepDist # value ranges from 0 to Major Axis and more
                self.Morphology['Angle'] = numpy.min( [ numpy.abs(SepAngle-PosAngle),numpy.abs(SepAngle-PosAngle-360), numpy.abs(SepAngle-PosAngle+360) ] ) # value ranges from 0 to 180.0
                #<DEBUG>#self.Morphology['Separation'] = self.Source.Morphology['Major Axis'] / 2.0
                #<DEBUG>#self.Morphology['Angle'] = 0.0
                self.Morphology['Projected_Source_Radius'] = numpy.abs( self.Source.Morphology['Major Axis'] * numpy.cos(numpy.deg2rad(self.Morphology['Angle'])) ) + \
                                                             numpy.abs( self.Source.Morphology['Minor Axis'] * numpy.sin(numpy.deg2rad(self.Morphology['Angle'])) )
                self.Morphology['Score'] = 100.0 * \
                                                    ( 1.0 - 
                                                      offset_down_weighting * (
                                                        self.Morphology['Separation'] / self.Morphology['Projected_Source_Radius']
                                                      )
                                                    )
                                                    # Separation projected relative to a*cos(theta) + b*sin(theta)
                                                    # 50% means that the SepDist equals the diameter of the ellipse at that SepAngle. 
                                                    # 
                print('Separation = %.3f, projected_source_radius = %.3f, offset_down_weighting = %.3f, M. Score = %.3f'%(self.Morphology['Separation'], self.Morphology['Projected_Source_Radius'], offset_down_weighting, self.Morphology['Score']))
                self.Morphology['Score'] = numpy.max([self.Morphology['Score'], 0])
                self.Morphology['Score'] = numpy.min([self.Morphology['Score'], 100])
                # 
                # 
                # 
                self.Photometry['Score'] = ( 0.85 * numpy.min( [ self.Source.Photometry['SNR_1']/12.0, 1.0 ] )
                                           ) * 100.0
                # 
                # 
                # also consider source image source position aperture photometry S/N
                if self.Photometry['Source/RefSource'] > -99 + 1e-6:
                    self.Photometry['Score'] = self.Photometry['Score'] + \
                                               ( 0.15 * numpy.min( [ self.Photometry['Source/RefSource'], 1.0 ] )
                                               ) * 100.0
                # 
                # 
                # 
                # 
                self.MatchScore = ( 0.5 * self.Morphology['Score'] + 
                                    0.5 * self.Photometry['Score'] )
                # 
                # 
                # 
                # 
                # 
                # plot annotation
                self.RefImage.text('Sep. = %.3f [arcsec]'%(self.Morphology['Separation']), 
                                    color=hex2color('#FF0000'), fontsize=13, align_top_right=True, horizontalalignment='right')
                #self.RefImage.text('Ang. = %.1f [degree]'%(self.Morphology['Angle']), 
                #                    color=hex2color('#FF0000'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # 
                # plot annotation
                self.RefImage.text('M. Score = %.1f [%%]'%(self.Morphology['Score']), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('P. Score = %.1f [%%]'%(self.Photometry['Score']), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('Extended = %.1f [%%]'%(self.Morphology['Extended']), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('Downweight = %.2f'%(offset_down_weighting), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('ALMA S/N = %.3f'%(self.Source.Photometry['SNR_1']), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('Image S/N = %.3f'%(self.Photometry['S/N']), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('Image S/Ref = %.2f'%(self.Photometry['Source/RefSource']), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # plot annotation
                self.RefImage.text('Score = %.1f [%%]'%(self.MatchScore), 
                                    color=hex2color('#00CC00'), fontsize=13, align_top_right=True, horizontalalignment='right')
                # 
                # 
                # 
                # show window and keep window open <DEBUG>
                #pyplot.ioff()
                #pyplot.show()
                #sys.exit()
                # 
                # 
                # 
                # show the image
                #pyplot.draw()
                #pyplot.pause(0.10)
                #print("Click anywhere on the figure to continue")
                # 
                # save the image to disk / output the image to disk
                self.RefImage.PlotDevice.savefig(PlotOutput)
                pyplot.close()
                print("")
                print("Saved as \"%s\"!"%(PlotOutput))
                # 
                # save to text file / output to text file
                #TextOutput = OutputDir+'/'+self.Source.Field+'--'+str(self.Source.Name)+'--'+str(self.Source.SubID)+'--'+StrTelescope+'--'+StrInstrument.replace(' ','-')+'.txt'
                TextFilePtr = open(TextOutput, 'w')
                TextFilePtr.write("# %s\n"%(str(datetime.now())))
                TextFilePtr.write("Source.Name = %s\n"%(self.Source.Name))
                #TextFilePtr.write("Source.ID = %ld\n"%(self.Source.ID))
                TextFilePtr.write("Source.SubID = %ld\n"%(self.Source.SubID))
                TextFilePtr.write("Source.ALMA.S/N = %.3f\n"%(self.Source.Photometry['SNR_1']))
                TextFilePtr.write("RefSource.ID = %ld\n"%(self.RefSource.ID))
                TextFilePtr.write("RefSource.Position = [%.10f, %.10f]\n"%(self.RefSource.RA, self.RefSource.Dec))
                TextFilePtr.write("Crowdedness = %.5f\n"%(self.Crowdedness))
                TextFilePtr.write("Clean_Index = %.0f\n"%(self.Clean_Index))
                TextFilePtr.write("Match.Score = %.1f\n"%(self.MatchScore))
                TextFilePtr.write("Match.Morphology.Score = %.1f\n"%(self.Morphology['Score']))
                TextFilePtr.write("Match.Morphology.Separation = %s # Source to RefSource Separation in arcsec\n"%(self.Morphology['Separation']))
                TextFilePtr.write("Match.Morphology.Angle = %s # Source to RefSource (PosAngle - SepAngle) in degree\n"%(self.Morphology['Angle']))
                TextFilePtr.write("Match.Morphology.Projected_Source_Radius = %s # Projected Source Radius at (PosAngle - SepAngle) direction in arcsec\n"%(self.Morphology['Projected_Source_Radius']))
                TextFilePtr.write("Match.Morphology.Extended = %.1f # Source morphological extent slope\n"%(self.Morphology['Extended']))
                TextFilePtr.write("Match.Photometry.Score = %s\n"%(str(self.Photometry['Score'])))
                TextFilePtr.write("Match.Photometry.Position = [%.10f, %.10f]\n"%(self.Photometry['Position'][0], self.Photometry['Position'][1]))
                TextFilePtr.write("Match.Photometry.Centroid = [%.10f, %.10f]\n"%(self.Photometry['Centroid'][0], self.Photometry['Centroid'][1]))
                TextFilePtr.write("Match.Photometry.S/N = %.3f\n"%(self.Photometry['S/N']))
                TextFilePtr.write("Match.Photometry.Flux = %.6g\n"%(self.Photometry['Flux']))
                TextFilePtr.write("Match.Photometry.FluxError = %.6g\n"%(self.Photometry['FluxError']))
                TextFilePtr.write("Match.Photometry.Source/RefSource = %.6g\n"%(self.Photometry['Source/RefSource']))
                TextFilePtr.write("Match.Photometry.GrowthCurve = %s\n"%(str(self.Photometry['GrowthCurve'])))
                TextFilePtr.close()
                print("Saved to \"%s\"!"%(TextOutput))
                print("")
            # 
            # end Logger
            if 'Output_Logger' in globals():
                Output_Logger.end_log_file()
            #temp_Logger.close()
            #del temp_Logger


















####################################################################
#                                                                  #
#                                                                  #
#                           MAIN PROGRAM                           #
#                                                                  #
#                                                                  #
####################################################################

# Preset 
Input_Catalog = ''
Input_Columns = {}
Input_Filters = []
Input_RefCat = ''
Input_Overwrite = False
Output_Dir = ''
Output_Prefix = 'Output_'
Output_Sep = '_'

# Print Usage
if len(sys.argv) <= 1:
    print("""
Usage:
    almacosmos_counterpart_association_auto_score.py \\
        -cat "ALMA_Photometry.fits" \\
        -col "{'ID':'ID_Photometry','RA':'RA_Photometry','Dec':'Dec_Photometry','RefRA':'RA_Counterpart','RefDec':'Dec_Counterpart'}" \\
        -sel "{'ID':841676}" \\
        -sel "{'ID':'999991~999999'}" \\
        -out "OutputDir"
        """)
    sys.exit()

# Read User Input
i = 1
while i < len(sys.argv):
    tmp_arg = sys.argv[i].lower().replace('--','-')
    if tmp_arg == '-cat' or tmp_arg == '-catalog':
        if i+1 < len(sys.argv):
            Input_Catalog = sys.argv[i+1]
            print('Setting catalog %s'%(Input_Catalog))
            i = i + 1
    elif tmp_arg == '-col' or tmp_arg == '-column' or tmp_arg == '-columns':
        # must be dict
        if i+1 < len(sys.argv):
            Input_Columns = json.loads(sys.argv[i+1].replace("\'", "\""))
            print('Defining columns %s'%(Input_Columns))
            if type(Input_Columns) is not dict:
                print('Error! Columns should be a Python dict object! For example: {"Field":"ALMA_Image","ID":"ID_prior","RA":"RA_prior","Dec":"Dec_prior","RefRA":"RA_Master","RefDec":"Dec_Master"}')
                sys.exit()
            i = i + 1
    if tmp_arg == '-ref' or tmp_arg == '-ref-cat' or tmp_arg == '-ref-catalog':
        if i+1 < len(sys.argv):
            Input_RefCat = sys.argv[i+1]
            print('Setting refcat %s'%(Input_RefCat))
            i = i + 1
    elif tmp_arg == '-filter' or tmp_arg == '-filters' or tmp_arg == '-select' or tmp_arg == '-sel':
        # must be dict
        if i+1 < len(sys.argv):
            Input_Filter = json.loads(sys.argv[i+1].replace("\'", "\""))
            Input_Filters.append(Input_Filter)
            print('Adding filter %s'%(Input_Filter))
            if type(Input_Filter) is not dict:
                print('Error! Filter should be a Python dict object! For example: {"ID":3,"ALMA_IMAGE":"aaaaa.fits"}')
                sys.exit()
            i = i + 1
    elif tmp_arg == '-out' or tmp_arg == '-output':
        # must be dict
        if i+1 < len(sys.argv):
            Output_Dir = sys.argv[i+1]
            if not os.path.isdir(Output_Dir):
                os.makedirs(Output_Dir)
            i = i + 1
    elif tmp_arg == '-output-prefix':
        # must be dict
        if i+1 < len(sys.argv):
            Output_Prefix = sys.argv[i+1]
            i = i + 1
    elif tmp_arg == '-output-sep':
        # must be dict
        if i+1 < len(sys.argv):
            Output_Sep = sys.argv[i+1]
            i = i + 1
    elif tmp_arg == '-overwrite':
        Input_Overwrite = True
    else:
        if Input_Catalog == '':
            Input_Catalog = sys.argv[i]
    i = i + 1

# Check User Input
if Input_Catalog == '':
    print('Please input valid catalog!')
    sys.exit()

# Read 'ref_catalog.fits'
if Input_RefCat != '':
    if os.path.isfile(Input_RefCat):
        print("")
        print("Found reference catalog \"%s\"! We will calculate the 'Crowdedness' and 'Clean_Index' parameters!")
        print("")
        RefCat = Highz_Catalogue(Input_RefCat)
        #refcatalog_KDTree = KDTree()
        #refcatalog_CAT = CrabFitsTable('ref_catalog.fits')
        #refcatalog_RA = refcatalog_CAT.getColumn('RA')
        #refcatalog_DEC = refcatalog_CAT.getColumn('Dec')
    else:
        print("")
        print("Warning! No reference catalog 'ref_catalog.fits' was found under current directory! Will not calculate 'Crowdedness' and 'Clean_Index'!")
        print("")
        RefCat = None

# 
# Prepare Logger
Output_Logger = CrabLogger()

# 
# Read Catalog
Cat = Highz_Catalogue(Input_Catalog)

# 
# Read Catalog Columns
if "ID" in Input_Columns:
    Cat_ID = Cat.TableData.field(Input_Columns["ID"])
else:
    Cat_ID = Cat.id() # guess an ID column

if "Name" in Input_Columns:
    Cat_Name = Cat.TableData.field(Input_Columns["Name"])
else:
    Cat_Name = Cat.col(ColName=['OBJECT','PROJECT'], ColSelect=1) # guess a Name column -- which is the source name

if len(Cat_Name) == 0:
    Cat_Name = Cat_ID.astype(str)

if "Image" in Input_Columns:
    Cat_Image = Cat.TableData.field(Input_Columns["Image"])
else:
    Cat_Image = Cat.col(ColName=['Image','ALMA_IMAGE','image_name'], ColSelect=1) # guess an Image column

if "RA" in Input_Columns:
    Cat_RA = Cat.TableData.field(Input_Columns["RA"])
else:
    Cat_RA = Cat.ra() # guess a RA column

if "Dec" in Input_Columns:
    Cat_Dec = Cat.TableData.field(Input_Columns["Dec"])
else:
    Cat_Dec = Cat.dec() # guess a Dec column

if "RefRA" in Input_Columns:
    Cat_RefRA = Cat.TableData.field(Input_Columns["RefRA"])
else:
    Cat_RefRA = Cat.ra_2() # guess a RefRA column

if "RefDec" in Input_Columns:
    Cat_RefDec = Cat.TableData.field(Input_Columns["RefDec"])
else:
    Cat_RefDec = Cat.dec_2() # guess a RefDec column

if 'SNR_FIT' in Cat.TableHeaders:
    Cat_SNR = numpy.array(Cat.TableData.field('SNR_FIT'))
    Cat_SNR_column = 'SNR_FIT'
elif 'FLUX_ALMA' in Cat.TableHeaders and 'FLUXERR_ALMA' in Cat.TableHeaders and 'WAVELENGTH_ALMA' in Cat.TableHeaders:
    Cat_SNR = numpy.array(Cat.TableData.field('FLUX_ALMA'))/numpy.array(Cat.TableData.field('FLUXERR_ALMA'))
    Cat_SNR_column = 'FLUX_ALMA / FLUXERR_ALMA at WAVELENGTH_ALMA'

if 'Separation' in Cat.TableHeaders:
    Cat_Sep = numpy.array(Cat.TableData.field('Separation'))
else:
    Cat_Sep = numpy.sqrt(numpy.power((Cat_RA-Cat_RefRA)*numpy.cos(Cat_RefDec/180.0*numpy.pi)*3600.0,2) + numpy.power((Cat_Dec-Cat_RefDec)*3600.0,2)) # arcsec

if "zphot" in Input_Columns:
    Cat_zphot = Cat.TableData.field(Input_Columns["zphot"])
    Cat_zphot_column = Input_Columns["zphot"]
else:
    Cat_zphot, Cat_zphot_column = Cat.zphot(ReturnColName=True) # guess a zphot column


#
#for Input_Filter in Input_Filters:
#    if "ID" in Input_Filter:
#        if type(Input_Filter["ID"]) is str:
#            Input_Filter_IDs = parseIntSet(Input_Filter["ID"])
#            print('Input_Filter["ID"] = %s'%(Input_Filter["ID"]))
#            print(Input_Filter_IDs)
#            print('')
#sys.exit()

# 
# Loop each source in the topcat cross-matched catalog
for i in range(len(Cat.TableData)):
    # 
    # Filter sources
    # which is like "index 3~50"
    # 
    Flag_Skip = False
    for Input_Filter in Input_Filters:
        if "Name" in Input_Filter:
            if type(Input_Filter["Name"]) is list:
                Input_Filter_Names = Input_Filter["Name"]
            else:
                Input_Filter_Names = [Input_Filter["Name"]]
            if len(Cat_Name) > i:
                if Cat_Name[i] not in Input_Filter_Names:
                    Flag_Skip = True
                    break
        if "Image" in Input_Filter:
            if type(Input_Filter["Image"]) is list:
                Input_Filter_Images = Input_Filter["Image"]
            else:
                Input_Filter_Images = [Input_Filter["Image"]]
            if len(Cat_Image) > i:
                if Cat_Image[i] not in Input_Filter_Images:
                    Flag_Skip = True
                    break
        if "ID" in Input_Filter:
            if type(Input_Filter["ID"]) is str:
                Input_Filter_IDs = parseIntSet(Input_Filter["ID"])
            elif type(Input_Filter["ID"]) is list:
                Input_Filter_IDs = Input_Filter["ID"]
            else:
                Input_Filter_IDs = [Input_Filter["ID"]]
            if len(Cat_ID) > i:
                if Cat_ID[i] not in Input_Filter_IDs:
                    Flag_Skip = True
                    break
    
    if Flag_Skip:
        continue
    
    
    
    
    Overwrite = Input_Overwrite
    
    
    
    # 
    # Read Source Morphology
    # 
    source_maj = numpy.nan
    source_min = numpy.nan
    source_pa = numpy.nan
    if 'FWHM_MAJ_FIT' in Cat.TableHeaders and \
       'FWHM_MIN_FIT' in Cat.TableHeaders and \
       'POSANG_FIT' in Cat.TableHeaders and \
       'MINAX_BEAM' in Cat.TableHeaders and \
       'AXRATIO_BEAM' in Cat.TableHeaders and \
       'POSANG_BEAM' in Cat.TableHeaders:
        source_maj = float(Cat.TableData[i].field('FWHM_MAJ_FIT'))
        source_min = float(Cat.TableData[i].field('FWHM_MIN_FIT'))
        source_pa = float(Cat.TableData[i].field('POSANG_FIT'))
        beam_maj = float(Cat.TableData[i].field('MINAX_BEAM')) * float(Cat.TableData[i].field('AXRATIO_BEAM'))
        beam_min = float(Cat.TableData[i].field('MINAX_BEAM'))
        beam_pa = float(Cat.TableData[i].field('POSANG_BEAM'))
        # prevent source size too small
        if source_maj*source_min < beam_maj*beam_min:
            source_maj = beam_maj
            source_min = beam_min
            source_pa = beam_pa
    else:
        source_maj_deconv, source_min_deconv, source_pa_deconv = Cat.source_morphology(i)
        beam_maj, beam_min, beam_pa = Cat.telescope_beam(i)
        print(type(source_maj_deconv))
        print(type(beam_maj))
        source_maj, source_min, source_pa = convolve_2D_Gaussian_Maj_Min_PA(source_maj_deconv, source_min_deconv, source_pa_deconv, beam_maj, beam_min, beam_pa)
    # 
    if source_maj != source_maj or source_min != source_min or source_pa != source_pa:
        print("")
        print("Error! Could not find appropriate columns in the input topcat cross-matched catalog!")
        print("We need 'FWHM_MAJ_FIT', 'FWHM_MIN_FIT', 'POSANG_FIT', 'MINAX_BEAM', 'AXRATIO_BEAM', 'POSANG_BEAM', etc.")
        print("Abort!")
        print("")
        sys.exit()
    
    
    
    # 
    # Read Source info from Alex Karim's Blind Extraction Catalog
    # 
    source_Name = Cat_Name[i]
    source_Image = Cat_Image[i]
    source_ID = Cat_ID[i]
    source_SubID = 0
    source_SNR = Cat_SNR[i].astype(float)
    source_ref_SNR = Cat_SNR_column
    source_separation = Cat_Sep[i].astype(float)
    source_RA = Cat_RA[i].astype(float)
    source_Dec = Cat_Dec[i].astype(float)
    Source_zphot = Cat_zphot[i].astype(float)
    Source_ref_zphot = Cat_zphot_column
    
    if 'PROJECT' in Cat.TableHeaders and 'OBJECT' in Cat.TableHeaders:
        source_Name = Cat.TableData[i].field('PROJECT').strip()+'--'+Cat.TableData[i].field('OBJECT').strip()
    if 'SUBID_TILE' in Cat.TableHeaders:
        source_SubID = Cat.TableData[i].field('SUBID_TILE')
    
    
    
    
    # 
    # Create ALMA Source
    # 
    Source = Highz_Galaxy(
        Field   = 'COSMOS', 
        Name    = source_Name, 
        ID      = source_ID, 
        SubID   = source_SubID, 
        RA      = source_RA, 
        Dec     = source_Dec, 
        Morphology = {
            'Major Axis': source_maj, 
            'Minor Axis': source_min, 
            'Pos Angle':  source_pa, 
        }, 
        Photometry = {
            'SNR_1': source_SNR, 
            'ref_SNR_1': source_SNR, 
        }, 
        Redshifts = {
            'zphot_1': Source_zphot, 
            'ref_zphot_1': Source_ref_zphot, 
        }, 
    )
    Source.about()
    
    
    # 
    # Read Counterpart Source info from the input catalog
    # 
    RefSource = Highz_Galaxy(
        Field = 'COSMOS', 
        Name  = source_Name, 
        ID    = source_ID, 
        RA    = Cat_RefRA[i], 
        Dec   = Cat_RefDec[i], 
    )
    
    
    
    # 
    # Prepare cutouts and copy to Cutout_Dir
    # 
    Cutout_Dir = Output_Dir + os.sep + Output_Prefix + '%d'%(i+1) + Output_Sep + source_Name + os.sep + 'cutouts'
    if not os.path.isdir(Cutout_Dir):
        os.makedirs(Cutout_Dir)
    
    Cutout_Files = []
    
    if not os.path.isfile(Cutout_Dir + os.sep + 'UVISTA_K.fits'):
        Cutout_downloading_subprocess = subprocess.Popen('almacosmos_cutouts_query_cosmos_cutouts_via_IRSA.py -RA %s -Dec %s -FoV 15.0 -Field "COSMOS" -Band "UVISTA_K" -out "%s"'%(source_RA, source_Dec, Cutout_Dir + os.sep + 'UVISTA_K.fits'), 
                                                            shell=True, stdout=open(Cutout_Dir + os.sep + 'UVISTA_K.fits.log', 'w'))
        Cutout_downloading_errcode = Cutout_downloading_subprocess.wait()
        #shutil.copy2()
    
    if os.path.isfile(Cutout_Dir + os.sep + 'UVISTA_K.fits'):
        Cutout_Files.append(Cutout_Dir + os.sep + 'UVISTA_K.fits')
    else:
        print('Error! Failed to run %s'%(Cutout_downloading_subprocess))
        sys.exit()
    
    #StrInstrument, StrTelescope = recognize_Instrument(Cutout_File)
    
    
    # 
    # 
    # Do CrossMatching on each cutout image (i.e. each band)
    # 
    # 
    for Cutout_File in Cutout_Files:
        # 
        # CrossMatch_Identifier can only process one fits image at a time. 
        # match_morphology() is the core function to do cross-matching. 
        # 
        RefImage = Highz_Image(Cutout_File)
        # 
        IDX = CrossMatch_Identifier(
            Source = Source, 
            RefSource = RefSource, 
            RefImage = RefImage, 
            RefCatalog = RefCat, 
            Separation = source_separation, 
        )
        IDX.about()
        IDX.match_morphology(Overwrite=Overwrite, OutputName=str(i))
        # 
        break
    
    break












