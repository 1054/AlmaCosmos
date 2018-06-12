#!/bin/bash
# 

# 2018-01-21

# 
# This code read the MC sim recovery results and do some outlier source filtering. 
# Run this code like follows:
#   cd datatable_CrossMatched_by_ID
#   ../a_dzliu_code_to_filter_outliers.sh
# 


# 
# Select only matched sources
# Select Pb_corr_pb_image_from_rec_cat>0, so that the source is within the valid pixel circular area.
# Select Pb_corr_pb_image_from_rec_cat<5, so that the source is within the valid pixel circular area.
# Select Pb_corr_equation_from_rec_cat<5, so that the source is within the valid pixel circular area.
# Select Galfit_reduced_chi_square_from_rec_cat<100, so that the source is not too close to the edge of the valid pixel circular area.
# 

topcat -stilts tpipe in="datatable_CrossMatched_all_entries.fits" ifmt=fits \
                    cmd="select \"(flag_matched)\"" \
                    cmd="select \"(Pb_corr_pb_image_from_rec_cat>0)\"" \
                    cmd="select \"(Pb_corr_pb_image_from_rec_cat<4.2)\"" \
                    cmd="select \"(Pb_corr_equation_from_rec_cat<4.2)\"" \
                    cmd="select \"S_peak/noise>=2.5\"" \
                    cmd="keepcols \"ID S_in S_out e_S_out S_peak S_res noise Maj_in Min_in PA_in Maj_out Min_out PA_out Maj_beam Min_beam PA_beam image_file_STR simu_name_STR\"" \
                    out="datatable_CrossMatched_only_matches_filtered_nonphysical.fits" ofmt=fits
                    
                    # cmd="select \"(Galfit_reduced_chi_square_from_rec_cat<20)\"" \
                    # cmd="select \"(S_peak/noise<1e6)\"" \
                    # out="datatable_CrossMatched_only_matches.txt" ofmt=ascii


# 
# We should apply these selections so as to match real photometry catalog, 
# see "/Volumes/GoogleDrive/Team Drives/A3COSMOS/Simulations/Monte_Carlo_Simulation_Parameter_Sampled/20171222/exclude_2_*/Screen*.png"
# see "/Volumes/GoogleDrive/Team Drives/A3COSMOS/Simulations/Monte_Carlo_Simulation_Parameter_Sampled/20171222/exclude_3_*/Screen*.png"
# see "/Volumes/GoogleDrive/Team Drives/A3COSMOS/Simulations/Monte_Carlo_Simulation_Parameter_Sampled/20171222/exclude_4_*/Screen*.png"
# 
#topcat -stilts tpipe in="datatable_CrossMatched_only_matches.txt" ifmt=ascii \
#                    cmd="select \"(Maj_in/Maj_beam<3.99 && Maj_in<=3.0 && Maj_out>0.05 && Maj_out/Maj_beam>=0.1)\"" \
#                    out="datatable_CrossMatched_only_matches_filtered_outliers.txt" ofmt=ascii












