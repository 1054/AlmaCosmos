#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 


#import math
import numpy
import scipy
import astropy
from datetime import datetime
from astropy.modeling.models import Gaussian2D
from astropy.convolution import Gaussian2DKernel
from astropy.convolution import convolve, convolve_fft
from astropy.io import fits
from astropy.wcs import WCS





def generate_2D_Gaussian(FWHM, Centroid = [0.0, 0.0], Peak = 1.0, Norm = 0.0, pixscale = 1.0):
    if numpy.isscalar(FWHM):
        FWHM = [FWHM]
    if len(FWHM) == 1:
        stddev_major = FWHM[0] / (2.0*numpy.sqrt(2.0*numpy.log(2.0)))
        stddev_minor = FWHM[0] / (2.0*numpy.sqrt(2.0*numpy.log(2.0)))
        theta = 0.0
    elif len(FWHM) == 2:
        stddev_major = FWHM[0] / (2.0*numpy.sqrt(2.0*numpy.log(2.0)))
        stddev_minor = FWHM[1] / (2.0*numpy.sqrt(2.0*numpy.log(2.0)))
        theta = 0.0
    elif len(FWHM) >= 3:
        stddev_major = FWHM[0] / (2.0*numpy.sqrt(2.0*numpy.log(2.0)))
        stddev_minor = FWHM[1] / (2.0*numpy.sqrt(2.0*numpy.log(2.0)))
        theta = FWHM[2]
    # 
    print('psf major minor theta %.4f %.4f %.2f'%(stddev_major, stddev_minor, theta))
    PsfModel = Gaussian2D(Peak, Centroid[0], Centroid[1], stddev_major/pixscale, stddev_minor/pixscale, (theta+90.0)/180.0*numpy.pi) # amplitude, x_mean, y_mean, x_stddev, y_stddev, theta
    # 
    PsfNAXIS = numpy.max([stddev_major, stddev_minor]) / pixscale * 15.0
    PsfNAXIS = numpy.round((PsfNAXIS-1.0)/2.0)*2+1 # make it odd number
    PsfNAXIS = numpy.array([PsfNAXIS, PsfNAXIS])
    print('psf model model naxis %d %d'%(PsfNAXIS[0], PsfNAXIS[1]))
    PsfModel.bounding_box = ((-(PsfNAXIS[0]-1)/2, (PsfNAXIS[0]-1)/2), (-(PsfNAXIS[1]-1)/2, (PsfNAXIS[1]-1)/2))
    PsfImage = PsfModel.render()
    # 
    return PsfImage



def convolve_2D_Gaussian_FWHM(Intrinsic_FWHM, Beam_FWHM):
    Convolved_FWHM = [numpy.nan, numpy.nan, numpy.nan]
    if numpy.isscalar(Intrinsic_FWHM) or len(Intrinsic_FWHM) < 3:
        print('Error! The input Intrinsic_FWHM should contain three values for the major axis, minor axis and the position angle!')
    elif numpy.isscalar(Beam_FWHM) or len(Beam_FWHM) < 3:
        print('Error! The input Beam_FWHM should contain three values for the major axis, minor axis and the position angle!')
    else:
        Convolved_FWHM = convolve_2D_Gaussian_Maj_Min_PA(Intrinsic_FWHM[0], Intrinsic_FWHM[1], Intrinsic_FWHM[2], Beam_FWHM[0], Beam_FWHM[1], Beam_FWHM[2])
        print('Maj_convol = %s'%(Convolved_FWHM[0]))
        print('Min_convol = %s'%(Convolved_FWHM[1]))
        print('PA_convol = %s'%(Convolved_FWHM[2]))
    return Convolved_FWHM


def convolve_2D_Gaussian_Maj_Min_PA(Maj_deconv, Min_deconv, PA_deconv, Maj_beam, Min_beam, PA_beam):
    # see below 'deconvolve_2D_Gaussian_Maj_Min_PA'
    # 
    sigic2 = (((PA_deconv + 900.0) % 180.0) - ((PA_beam + 900.0) % 180.0)) * 2.0 / 180.0 * numpy.pi
    # 
    PA_diff = (((PA_deconv + 900.0) % 180.0) - ((PA_beam + 900.0) % 180.0))
    # 
    sconv = (Maj_deconv**2+Min_deconv**2) + (Maj_beam**2+Min_beam**2)
    sbeam = (Maj_beam**2+Min_beam**2)
    dbeam = (Maj_beam**2-Min_beam**2)
    dconv_times_dcos = (Maj_deconv**2-Min_deconv**2) * numpy.cos(sigic2) + dbeam
    dconv_times_dsin = numpy.tan(sigic2) * (dconv_times_dcos-dbeam)
    PA_diff = numpy.arctan2(dconv_times_dsin,dconv_times_dcos) / 2.0 / numpy.pi * 180.0
    dcos = numpy.cos(2*PA_diff/180.0*numpy.pi)
    dsin = numpy.sin(2*PA_diff/180.0*numpy.pi)
    dconv = dconv_times_dcos / dcos
    #if dcos != 0.0:
    #    dconv = dconv_times_dcos / dcos
    #else:
    #    dconv = dconv_times_dsin / dsin
    # 
    PA_convol = PA_diff + ((PA_beam + 900.0) % 180.0)
    Maj_convol = (sconv + dconv)/2.0 # dconv = (Maj_convol**2-Min_convol**2), sconv = (Maj_convol**2+Min_convol**2), so ...
    Min_convol = (sconv - dconv)/2.0 # dconv = (Maj_convol**2-Min_convol**2), sconv = (Maj_convol**2+Min_convol**2), so ...
    MajMin_convol = numpy.column_stack((Maj_convol,Min_convol))
    Maj_convol = numpy.sqrt(numpy.amax(MajMin_convol,axis=1))
    Min_convol = numpy.sqrt(numpy.amin(MajMin_convol,axis=1))
    # 
    return Maj_convol, Min_convol, PA_convol



def deconvolve_2D_Gaussian_FWHM(Convolved_FWHM, Beam_FWHM):
    Deconvolved_FWHM = [numpy.nan, numpy.nan, numpy.nan]
    if numpy.isscalar(Convolved_FWHM) or len(Convolved_FWHM) < 3:
        print('Error! The input Convolved_FWHM should contain three values for the major axis, minor axis and the position angle!')
    elif numpy.isscalar(Beam_FWHM) or len(Beam_FWHM) < 3:
        print('Error! The input Beam_FWHM should contain three values for the major axis, minor axis and the position angle!')
    else:
        Deconvolved_FWHM = deconvolve_2D_Gaussian_Maj_Min_PA(Convolved_FWHM[0], Convolved_FWHM[1], Convolved_FWHM[2], Beam_FWHM[0], Beam_FWHM[1], Beam_FWHM[2])
        print('Maj_deconv = %s'%(Deconvolved_FWHM[0]))
        print('Min_deconv = %s'%(Deconvolved_FWHM[1]))
        print('PA_deconv = %s'%(Deconvolved_FWHM[2]))
    return Deconvolved_FWHM


def deconvolve_2D_Gaussian_Maj_Min_PA(Maj_convol, Min_convol, PA_convol, Maj_beam, Min_beam, PA_beam):
    # inputs: maj_convol, min_convol, PA_convol, maj_beam, min_beam, PA_beam
    # based on the ForTran code from Eva, see email on 2018-01-09, subject "deconvolution".
    # <20180118><20180226>
    # 
    # Assuming beam FWHM: B_maj, B_min, B_PA
    #     intrinsic FWHM: H_maj, H_min, H_PA
    #     convolved FWHM: C_maj, C_min, C_PA
    # We have
    #     (B_maj**2 + B_min**2) + (H_maj**2 + H_min**2) = (C_maj**2 + C_min**2)   --> verified by '/Users/dzliu/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-calc-Gaussian-convolved-sizes/calc_Gaussian_convolved_sizes_Test_2_PA_diff_90.pro'
    #                                                                                         and '/Users/dzliu/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-calc-Gaussian-convolved-sizes/calc_Gaussian_convolved_sizes_Test_3_PA_diff_45.pro'
    # and
    #     
    # 
    PA_diff = (((PA_convol + 900.0) % 180.0) - ((PA_beam + 900.0) % 180.0))
    # 
    dconv = (Maj_convol**2-Min_convol**2)
    dbeam = (Maj_beam**2-Min_beam**2)
    sconv = (Maj_convol**2+Min_convol**2)
    sbeam = (Maj_beam**2+Min_beam**2)
    dcos = numpy.cos(2*PA_diff/180.0*numpy.pi)
    dsin = numpy.sin(2*PA_diff/180.0*numpy.pi)
    sigic2 = numpy.arctan2(dconv*dsin,dconv*dcos-dbeam) # The result is between -pi and pi . 
    # 
    PA_deconv = sigic2/2.0 * 180.0 / numpy.pi + ((PA_beam + 900.0) % 180.0)
    Maj_deconv = (sconv-sbeam)/2.0 + (dconv*dcos-dbeam)/(2.0*numpy.cos(sigic2))
    Min_deconv = (sconv-sbeam)/2.0 - (dconv*dcos-dbeam)/(2.0*numpy.cos(sigic2))
    MajMin_deconv = numpy.column_stack((Maj_deconv,Min_deconv))
    Maj_deconv = numpy.sqrt(numpy.amax(MajMin_deconv,axis=1))
    Min_deconv = numpy.sqrt(numpy.amin(MajMin_deconv,axis=1))
    # 
    return Maj_deconv, Min_deconv, PA_deconv





























import sys

try:
    import numpy
except ImportError:
    print("Error! Could not import numpy!")
    sys.exit()









