#!/bin/bash
# 

cd "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20170730_on_Phys_MC_Simulated_Images/"

input_sim_cat="../../../../Simulations/Physical_MC_sim/20170803/Simulated_Joined/datatable_Simulated_Concatenated_with_more_columns.fits"
input_rec_cat="./Recovered_Joined/datatable_Recovered_Concatenated_galfit_Gaussian.fits"
output_dir="Statistics"

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
                icmd1="select \"(flag_buffer==0)\"" \
                values1="id sim_alma_image_STR sim_repetition_STR" \
                suffix1="_fit" \
                in2="$input_sim_cat" \
                ifmt2=fits \
                icmd2="select \"(!NULL_flag_sim_at_nan)\"" \
                values2="id sim_data_dir_STR sim_dir_str" \
                suffix2="" \
                fixcols=all \
                join1=always \
                join2=always \
                matcher="exact+exact+exact" \
                multimode=group \
                ocmd="addcol S_in -after id \"flux\"" \
                ocmd="addcol S_out -after S_in \"f_total_fit\"" \
                ocmd="addcol e_S_out -after S_out \"f_total_fit/snr_total_fit\"" \
                ocmd="addcol S_peak -after e_S_out \"fpeak_fit\"" \
                ocmd="addcol S_res -after S_peak \"fres_fit\"" \
                ocmd="addcol noise -after S_res \"rms_fit\"" \
                ocmd="addcol Maj_in -after noise \"Maj\"" \
                ocmd="addcol Min_in -after Maj_in \"Min\"" \
                ocmd="addcol Maj_out -after Min_in \"Maj_fit\"" \
                ocmd="addcol Min_out -after Maj_out \"Min_fit\"" \
                ocmd="addcol Maj_beam -after Min_out \"(beam_maj)\"" \
                ocmd="addcol Min_beam -after Maj_beam \"(beam_min)\"" \
                ocmd="delcols \"Maj Min\"" \
                ocmd="addcol pb_corr -after Min_beam \"pb_corr_fit\"" \
                ocmd="addcol fit_alma_image_STR \"sim_alma_image_STR_fit\"" \
                ocmd="addcol fit_repetition_STR \"sim_repetition_STR_fit\"" \
                ocmd="addcol sim_alma_image_STR \"sim_data_dir_STR\"" \
                ocmd="addcol sim_repetition_STR \"sim_dir_str\"" \
                ocmd="addcol flag_matched \"(!NULL_sim_alma_image_STR && !NULL_fit_alma_image_STR)\"" \
                ocmd="addcol flag_nonmatched_missed \"(!NULL_sim_alma_image_STR && NULL_fit_alma_image_STR)\"" \
                ocmd="addcol flag_nonmatched_spurious \"(NULL_sim_alma_image_STR && !NULL_fit_alma_image_STR)\"" \
                ocmd="addcol flag_null \"(NULL_sim_alma_image_STR && NULL_fit_alma_image_STR)\"" \
                ocmd="addcol flag_size_lower_boundary \"(flag_size_lower_boundary_fit)\"" \
                ocmd="addcol flag_size_upper_boundary \"(flag_size_upper_boundary_fit)\"" \
                ocmd="addcol flag_size_initial_guess \"(flag_size_initial_guess_fit)\"" \
                ocmd="keepcols \"id S_in S_out e_S_out S_peak S_res noise Maj_in Min_in Maj_out Min_out Maj_beam Min_beam pb_corr z lgMstar lgSFR Type_SED fit_alma_image_STR fit_repetition_STR sim_alma_image_STR sim_repetition_STR flag_matched flag_nonmatched_missed flag_nonmatched_spurious flag_null flag_size_lower_boundary flag_size_upper_boundary flag_size_initial_guess\"" \
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





