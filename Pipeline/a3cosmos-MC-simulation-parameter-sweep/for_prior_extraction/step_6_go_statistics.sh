#!/bin/bash
# 

cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20171210_on_Param_MC_Simulated_Images/

if [[ ! -f "statistics_GALFIT/concat_sim_data_table.txt" ]]; then
    echo "Error! \"statistics_GALFIT/concat_sim_data_table.txt\" was not found!"
    exit 1
fi

topcat -stilts tpipe \
                in="statistics_GALFIT/concat_sim_data_table.txt" \
                ifmt=ascii \
                cmd="addcol id \"sim_id\"" \
                cmd="addcol S_in \"sim_f*1e3\"" \
                cmd="addcol S_out \"rec_f*1e3\"" \
                cmd="addcol e_S_out \"rec_df*1e3\"" \
                cmd="addcol S_peak \"sim_fpeak*1e3\"" \
                cmd="addcol S_res \"sim_fpeak*1e3*0.0\"" \
                cmd="addcol noise \"sim_rms*1e3\"" \
                cmd="addcol Maj_in \"sim_Maj\"" \
                cmd="addcol Min_in \"sim_Min\"" \
                cmd="addcol Maj_out \"rec_Maj\"" \
                cmd="addcol Min_out \"rec_Min\"" \
                cmd="addcol Maj_beam \"sim_beam_maj\"" \
                cmd="addcol Min_beam \"sim_beam_min\"" \
                cmd="addcol pb_corr \"rec_f*1e3*0.0+1.0\"" \
                cmd="addcol sim_alma_image_STR \"sim_image_dir\"" \
                cmd="addcol sim_repetition_STR \"sim_image_name\"" \
                cmd="addcol flux_conv \"rec_S_Code\"" \
                cmd="keepcols \"id S_in S_out e_S_out S_peak S_res noise Maj_in Min_in Maj_out Min_out Maj_beam Min_beam pb_corr sim_alma_image_STR sim_repetition_STR flux_conv\"" \
                ofmt=fits \
                out="statistics_GALFIT/concat_sim_data_table.fits"
echo "Output to \"statistics_GALFIT/concat_sim_data_table.fits\"!"

topcat -stilts tpipe \
                in="statistics_GALFIT/concat_sim_data_table.fits" \
                ifmt=fits \
                cmd="select \"(S_peak>2.0*noise)\"" \
                ofmt=fits \
                out="statistics_GALFIT/concat_sim_data_table_only_matches.fits"
echo "Output to \"statistics_GALFIT/concat_sim_data_table_only_matches.fits\"!"







crossmatched_cat="statistics_GALFIT/concat_sim_data_table_only_matches.fits"
do_overwrite=1

if [[ ! -f "$crossmatched_cat" ]]; then
    echo "Error! \"$crossmatched_cat\" was not found!"
    exit 1
fi

source_script="$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Pipeline/SETUP.bash"

if [[ ! -f "$source_script" ]]; then
    echo "Error! \"$source_script\" was not found! Please completely clone \"https://github.com/1054/AlmaCosmos\"!"
    exit 1
fi

source "$source_script"



# 
# run simu. stat. analyzing code
# 
a3cosmos-MC-simulation-statistics-analysis "$crossmatched_cat"







