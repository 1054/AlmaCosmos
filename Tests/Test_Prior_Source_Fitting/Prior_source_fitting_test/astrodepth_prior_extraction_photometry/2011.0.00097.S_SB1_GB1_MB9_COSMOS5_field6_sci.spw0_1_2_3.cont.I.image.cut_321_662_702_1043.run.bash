#!/bin/bash
# 
source /Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash
cd "/Users/dzliu/Cloud/Github/AlmaCosmos/Tests/Test_Prior_Source_Fitting/Prior_source_fitting_test/"
astrodepth_prior_extraction_photometry \
                                       -cat '/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20171107a.fits'  \
                                       -sci "/Users/dzliu/Cloud/Github/AlmaCosmos/Tests/Test_Prior_Source_Fitting/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.image.cut_321_662_702_1043.fits" \
                                       -psf "/Users/dzliu/Cloud/Github/AlmaCosmos/Tests/Test_Prior_Source_Fitting/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.clean-beam.fits" \
                                       -rms "/Users/dzliu/Cloud/Github/AlmaCosmos/Tests/Test_Prior_Source_Fitting/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.rms.cut_321_662_702_1043.fits" \
                                       -pba "/Users/dzliu/Cloud/Github/AlmaCosmos/Tests/Test_Prior_Source_Fitting/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.pb.cut_321_662_702_1043.fits" \
                                       -buffer 20 \
                                       -output-dir "astrodepth_prior_extraction_photometry" \
                                       -output-name "2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.image.cut_321_662_702_1043" \
                                       -steps getpix galfit gaussian sersic  final \
                                       -unlock none \
                                       -overwrite none


# do cleaning
if [[ -d "astrodepth_prior_extraction_photometry/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.image.cut_321_662_702_1043/" ]]; then
   cd "astrodepth_prior_extraction_photometry/2011.0.00097.S_SB1_GB1_MB9_COSMOS5_field6_sci.spw0_1_2_3.cont.I.image.cut_321_662_702_1043/"
   rm galfit.* getpix.radius.* aaa_* aaa.* *.sky2xy.* *.tmp *.backup 2>/dev/null
   #rm prior_id.txt prior_x_y.txt 2>/dev/null
fi


