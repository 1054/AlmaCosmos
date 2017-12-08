#!/bin/bash
source "/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash"
CrabFitsImageArithmetic image_sci_input.fits times '+1.0' image_sci.fits      -remove-nan
CrabFitsImageArithmetic image_sci_input.fits times '-1.0' image_negative.fits -remove-nan
CrabFitsImageArithmetic image_rms_input.fits times 1.0 image_rms.fits -replace-nan '1e30'
CrabFitsImageArithmetic image_psf_input.fits times 1.0 image_psf.fits -remove-nan

