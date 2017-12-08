#!/bin/bash
# 


# Source

source "../../Softwares/SETUP.bash"


# Prepare python

# pip-3.6 install --user scipy astropy astroquery PyQt5 PySide2


# Prepare one ALMA image

image_version="v20170604"
image_name="2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3"
image_sci="$image_name.cont.I.image.fits"
image_pba="$image_name.cont.I.pb.fits"
image_psf="$image_name.cont.I.clean-beam.fits"

if [[ ! -d "$image_name" ]]; then

    mkdir "$image_name"
    cd "$image_name/"
    almacosmos_gdownload.py "$image_version/*/$image_sci" "$image_version/*/$image_pba" "$image_version/*/$image_psf"
    cd "../"

fi


# Prepare prior source catalog

prior_cat="/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20171107a.fits"


# Run fitting!

../../Pipeline/a3cosmos-prior-extraction-photometry \
    -catalog "$prior_cat" \
    -sci "$image_name/$image_sci" \
    -psf "$image_name/$image_psf" \
    -pba "$image_name/$image_pba" \
    -out "Prior_source_fitting_test"
    



