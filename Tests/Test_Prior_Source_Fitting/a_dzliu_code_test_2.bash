#!/bin/bash
# 


# Source

source "../../Softwares/SETUP.bash"


# Prepare python

# pip-3.6 install --user scipy astropy astroquery PyQt5 PySide2


# Prepare one ALMA image

image_version="v20170604"
#image_name="2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3"
image_name="2012.1.00978.S_SB4_GB1_MB1_GISMO-AK03_sci.spw0_1_2_3"
image_sci="image_sim.fits"
image_psf="image_sim.clean-beam.fits"

if [[ ! -d "Input_alma_images_2/Simulated/$image_name" ]]; then
    exit
fi


# Prepare prior source catalog

prior_cat="Input_alma_images_2/Simulated/$image_name/w_889.341_z_3.000_lgMstar_11.50_SB/galaxy_model_id_ra_dec.txt"


# Run fitting!

../../Pipeline/a3cosmos-prior-extraction-photometry \
    -catalog "$prior_cat" \
    -sci "Input_alma_images_2/Simulated/$image_name/w_889.341_z_3.000_lgMstar_11.50_SB/$image_sci" \
    -psf "Input_alma_images_2/Simulated/$image_name/w_889.341_z_3.000_lgMstar_11.50_SB/$image_psf" \
    -out "Output_prior_fitting_2"


../../Softwares/AlmaCosmos_Photometry_Blind_Extraction_PyBDSM_mod.py \
    "Input_alma_images_2/Simulated/$image_name/w_889.341_z_3.000_lgMstar_11.50_SB/$image_sci" \
    -out "Output_pybdsm_fitting_2"











