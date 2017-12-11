#!/bin/bash
# 

cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/check_simulated_image_fitting_statistics/

input_sim_cat="../../../../../Simulations/Physical_MC_sim/20171009/Simulated_Joined/datatable_Simulated_Concatenated_with_more_columns.fits"
input_rec_cat="../cat_pybdsm_concatenated_simulated.fits"
output_dir="CrossMatched"

function check_input_dir() {
    local i=1
    for (( i=1; i<=$#; i++ )); do
        if [[ ! -d "${!i}" ]] && [[ ! -L "${!i}" ]]; then
            echo "Error! \"${!i}\" was not found!"
            exit 1
        fi
    done
}
function check_input_file() {
    local i=1
    for (( i=1; i<=$#; i++ )); do
        if [[ ! -f "${!i}" ]] && [[ ! -L "${!i}" ]]; then
            echo "Error! \"${!i}\" was not found!"
            exit 1
        fi
    done
}

check_input_file "$input_sim_cat"
check_input_file "$input_rec_cat"

if [[ ! -d "$output_dir" ]]; then
    mkdir -p "$output_dir"
fi


# Run topcat

topcat -stilts tmatchn \
                nin=2 \
                in1="$input_rec_cat" \
                ifmt1=fits \
                icmd1="addcol -before RA ID \"index\"" \
                icmd1="select \"(Source_id_in_image>=0)\"" \
                values1="RA DEC Image Simu" \
                suffix1="_fit" \
                in2="$input_sim_cat" \
                ifmt2=fits \
                icmd2="select \"(!NULL_flag_sim_at_nan)\"" \
                icmd2="sort -down lgSFR" \
                icmd2="addcol Image \"sim_data_dir_STR+\\\".cont.I.image.fits\\\"\"" \
                icmd2="addcol Simu \"sim_dir_str\"" \
                values2="ra dec Image Simu" \
                suffix2="" \
                fixcols=all \
                join1=always \
                join2=always \
                matcher="sky+exact+exact" \
                params=1.0 \
                multimode=group \
                ocmd="addcol S_in -after id \"flux\"" \
                ocmd="addcol S_out -after S_in \"Total_flux_fit*1e3\"" \
                ocmd="addcol e_S_out -after S_out \"E_Total_flux_fit*1e3\"" \
                ocmd="addcol S_peak -after e_S_out \"Peak_flux_fit*1e3\"" \
                ocmd="addcol S_res -after S_peak \"S_peak*0.0\"" \
                ocmd="addcol noise -after S_res \"rms\"" \
                ocmd="addcol Maj_in -after noise \"Maj\"" \
                ocmd="addcol Min_in -after Maj_in \"Min\"" \
                ocmd="addcol Maj_out -after Min_in \"Maj_deconv_fit*3600.0\"" \
                ocmd="addcol Min_out -after Maj_out \"Min_deconv_fit*3600.0\"" \
                ocmd="addcol Maj_beam -after Min_out \"beam_maj\"" \
                ocmd="addcol Min_beam -after Maj_beam \"beam_min\"" \
                ocmd="delcols \"Maj Min\"" \
                ocmd="addcol pb_corr -after Min_beam \"Pbcor_fit\"" \
                ocmd="addcol fit_alma_image_STR \"Image_fit\"" \
                ocmd="addcol fit_repetition_STR \"Simu_fit\"" \
                ocmd="addcol sim_alma_image_STR \"Image\"" \
                ocmd="addcol sim_repetition_STR \"Simu\"" \
                ocmd="addcol flag_matched \"(!NULL_Simu && !NULL_Simu_fit)\"" \
                ocmd="addcol flag_nonmatched_missed \"(!NULL_Simu && NULL_Simu_fit)\"" \
                ocmd="addcol flag_nonmatched_spurious \"(NULL_Simu && !NULL_Simu_fit)\"" \
                ocmd="addcol flag_null \"(NULL_Simu && NULL_Simu_fit)\"" \
                ocmd="addcol flag_S_Code_STR \"(S_Code_fit)\"" \
                ocmd="keepcols \"id S_in S_out e_S_out S_peak S_res noise Maj_in Min_in Maj_out Min_out Maj_beam Min_beam pb_corr z lgMstar lgSFR Type_SED fit_alma_image_STR fit_repetition_STR sim_alma_image_STR sim_repetition_STR flag_matched flag_nonmatched_missed flag_nonmatched_spurious flag_null flag_S_Code_STR\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_all_entries.fits" \
                &>  "$output_dir/datatable_CrossMatched_all_entries.stilts.log"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn.html
                # multimode=group makes sure the cross-matching is one-to-one and unique
                # 
echo "Output to \"$output_dir/datatable_CrossMatched_all_entries.fits\"!"


topcat -stilts tpipe \
                in="$output_dir/datatable_CrossMatched_all_entries.fits" \
                cmd="select \"(flag_matched && Maj_beam>=0.1)\"" \
                out="$output_dir/datatable_CrossMatched_only_matches.fits" \
                &>  "$output_dir/datatable_CrossMatched_only_matches.stilts.log"
echo "Output to \"$output_dir/datatable_CrossMatched_only_matches.fits\"!"








