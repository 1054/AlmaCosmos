#!/bin/bash
# 

#cd "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20170730_on_Phys_MC_Simulated_Images/"

almacosmos_cmd_args_script=$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Softwares/almacosmos_cmd_args
if [[ ! -f "$almacosmos_cmd_args_script" ]]; then
    echo "Error! \"$almacosmos_cmd_args_script\" was not found! Please make sure you have completely downloaded the codes from \"https://github.com/1054/AlmaCosmos.git\"!"
    exit 1
fi

source "$almacosmos_cmd_args_script" "$@"

if [[ ! -z "$arg_sim" ]]; then
    input_sim_cat="$arg_sim"
elif [[ ! -z "$arg_sim_cat" ]]; then
    input_sim_cat="$arg_sim_cat"
else
    input_sim_cat="../../../../Simulations/Physical_MC_sim/20170803/Simulated_Joined/datatable_Simulated_Concatenated_with_more_columns.fits"
fi

if [[ ! -z "$arg_rec" ]]; then
    input_rec_cat="$arg_rec"
elif [[ ! -z "$arg_rec_cat" ]]; then
    input_rec_cat="$arg_rec_cat"
else
    input_rec_cat="./Recovered_Joined/datatable_Recovered_Concatenated_galfit_Gaussian.fits"
fi

if [[ ! -z "$arg_out" ]]; then
    output_dir="$arg_out"
else
    output_dir="Statistics"
fi

check_input_file "$input_sim_cat"
check_input_file "$input_rec_cat"
create_output_dir "$output_dir"



# 
# Run topcat
# 
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
                ocmd="addcol Type_SED_STR -after Type_SED \"Type_SED\"" \
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
                ocmd="keepcols \"id S_in S_out e_S_out S_peak S_res noise Maj_in Min_in Maj_out Min_out Maj_beam Min_beam pb_corr ra dec z lgMstar lgSFR Type_SED_STR fit_alma_image_STR fit_repetition_STR sim_alma_image_STR sim_repetition_STR flag_matched flag_nonmatched_missed flag_nonmatched_spurious flag_null flag_size_lower_boundary flag_size_upper_boundary flag_size_initial_guess\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_all_entries.fits" \
                &>  "$output_dir/datatable_CrossMatched_all_entries.stilts.log"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn.html
                # multimode=group makes sure the cross-matching is one-to-one and unique
                # 
echo "Output to \"$output_dir/datatable_CrossMatched_all_entries.fits\"!"


topcat -stilts tpipe \
                in="$output_dir/datatable_CrossMatched_all_entries.fits" \
                cmd="select \"(flag_matched && Maj_beam>=0.1 && S_peak>2.0*noise && S_out>2.0*noise && S_res<1e6)\"" \
                out="$output_dir/datatable_CrossMatched_only_matches.fits" \
                &>  "$output_dir/datatable_CrossMatched_only_matches.stilts.log"
echo "Output to \"$output_dir/datatable_CrossMatched_only_matches.fits\"!"





