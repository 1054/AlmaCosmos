#!/bin/bash
# 


# Source

source "../../Softwares/SETUP.bash"


cd "test_3"


if [[ ! -f "prior_source_catalog.fits" ]]; then
almacosmos_topcat_query_catalog_sources_within_fits_image_field_of_view \
    ~/Work/AlmaCosmos/Works/Combined_Master_Catalog_for_COSMOS/v20170504/master_catalog_single_entry_with_Flag_Outlier_with_Photoz_v20170504a.fits \
    2012.1.00523.S_SB1_GB1_MB1_hz3_sci.spw0_1_2_3.cont.I.image.fits \
    "prior_source_catalog.fits"
fi





astrodepth_prior_extraction_photometry \
                                       -cat "prior_source_catalog.fits" \
                                       -sci "2012.1.00523.S_SB1_GB1_MB1_hz3_sci.spw0_1_2_3.cont.I.image.fits" \
                                       -psf "2012.1.00523.S_SB1_GB1_MB1_hz3_sci.spw0_1_2_3.cont.I.clean-beam.fits" \
                                       -rms "2012.1.00523.S_SB1_GB1_MB1_hz3_sci.spw0_1_2_3.cont.I.rms.fits" \
                                       -pba "2012.1.00523.S_SB1_GB1_MB1_hz3_sci.spw0_1_2_3.cont.I.pb.fits" \
                                       -steps getpix galfit gaussian sersic final











