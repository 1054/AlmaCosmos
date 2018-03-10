#!/bin/bash
# 

# 
# This code filters some outlier sources. 
# Run this code like follows:
#   cd statistics_PyBDSM
#   ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-parameter-sampled/for_blind_extraction/step_5_go_filter.sh
# 

# 
# We should apply these selections so as to match real photometry catalog, 
# see exclude_2_*/Screen*.png
# see exclude_3_*/Screen*.png
# see exclude_4_*/Screen*.png
# 
topcat -stilts tpipe in="concat_sim_rec_data_table.fits" \
                    cmd="select \"(sim_Maj/sim_beam_maj<3.99 && sim_Maj<=3.0 && sim_Maj>0.05 && rec_Maj>0.05 && sim_Maj/sim_beam_maj>=0.1 && rec_Maj/sim_beam_maj>=0.1)\"" \
                    out="concat_sim_rec_data_table_filtered_outliers.fits"




# 
# Then select only matches
# 
$(dirname $(dirname $(dirname $(dirname "${BASH_SOURCE[0]}"))))/Softwares/a3cosmos-MC-simulation-catalog-reformat \
        "concat_sim_rec_data_table_filtered_outliers.fits"
#--> output concat_sim_data_table_fixed_bug_filtered_outliers_all_entries.fits
#       and concat_sim_data_table_fixed_bug_filtered_outliers_only_matches.fits
#       and concat_sim_data_table_fixed_bug_filtered_outliers_only_matches.txt
# 












