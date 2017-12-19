#!/bin/bash
# 

#cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/check_simulated_image_fitting_statistics/

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
    input_sim_cat="../../../../Simulations/Physical_MC_sim/20171009/Simulated_Joined/datatable_Simulated_Concatenated_with_more_columns.fits"
fi

if [[ ! -z "$arg_rec" ]]; then
    input_rec_cat="$arg_rec"
elif [[ ! -z "$arg_rec_cat" ]]; then
    input_rec_cat="$arg_rec_cat"
else
    input_rec_cat="./cat_pybdsm_concatenated_simulated.fits"
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
# Run topcat, first extract 'noise' data table from simulated catalog
# 
if [[ ! -f "$output_dir/datatable_sim_noise_uniq.txt" ]]; then
topcat -stilts tpipe \
                in="$input_sim_cat" \
                cmd="addcol Image \"sim_data_dir_STR+\\\".cont.I.image.fits\\\"\"" \
                cmd="addcol Simu \"sim_dir_str\"" \
                cmd="addcol noise \"rms\"" \
                cmd="keepcols \"Image Simu noise\"" \
                ofmt=ascii \
                out="$output_dir/datatable_sim_noise.txt" \
                &>  "$output_dir/datatable_sim_noise.txt.stilts.log"
if [[ $(uname) == "Darwin" ]]; then
    head -n 1 "$output_dir/datatable_sim_noise.txt" > "$output_dir/datatable_sim_noise_uniq.txt"
    cat "$output_dir/datatable_sim_noise.txt" | grep -v "^#" | gsort -V | uniq >> "$output_dir/datatable_sim_noise_uniq.txt"
else
    head -n 1 "$output_dir/datatable_sim_noise.txt" > "$output_dir/datatable_sim_noise_uniq.txt"
    cat "$output_dir/datatable_sim_noise.txt" | grep -v "^#" | sort -V | uniq >> "$output_dir/datatable_sim_noise_uniq.txt"
fi
echo "Output to \"$output_dir/datatable_sim_noise_uniq.txt\"!"
fi


# 
# Then cross-match recovered catalog to the extracted 'noise' data table and get 'noise' for each row. 
# 
if [[ ! -f "$output_dir/datatable_Recovered_with_sim_noise.fits" ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1="$input_rec_cat" \
                ifmt1=fits \
                values1="Image Simu" \
                suffix1="" \
                in2="$output_dir/datatable_sim_noise_uniq.txt" \
                ifmt2=ascii \
                values2="Image Simu" \
                suffix2="_from_sim_cat" \
                fixcols=all \
                join1=always \
                matcher="exact+exact" \
                multimode=pairs \
                iref=1 \
                ofmt=fits \
                out="$output_dir/datatable_Recovered_with_sim_noise.fits" \
                &>  "$output_dir/datatable_Recovered_with_sim_noise.fits.stilts.log"
echo "Output to \"$output_dir/datatable_Recovered_with_sim_noise.fits\"!" 
fi


# 
# Then cross-match recovered catalog (which now contains the 'noise' column) and the simulated catalog
# 
if [[ ! -f "$output_dir/datatable_CrossMatched_all_entries.fits" ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1="$output_dir/datatable_Recovered_with_sim_noise.fits" \
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
                ocmd="addcol noise -after S_res \"(!NULL_rms ? rms : noise_from_sim_cat_fit)\"" \
                ocmd="addcol Maj_in -after noise \"sqrt(Maj*Maj/(beam_maj*beam_min))\"" \
                ocmd="addcol Min_in -after Maj_in \"sqrt(Min*Min/(beam_maj*beam_min))\"" \
                ocmd="addcol Maj_out -after Min_in \"sqrt((Maj_deconv_fit*3600.0*Maj_deconv_fit*3600.0)+(beam_maj*beam_min))\"" \
                ocmd="addcol Min_out -after Maj_out \"sqrt((Min_deconv_fit*3600.0*Min_deconv_fit*3600.0)+(beam_maj*beam_min))\"" \
                ocmd="addcol Maj_beam -after Min_out \"beam_maj\"" \
                ocmd="addcol Min_beam -after Maj_beam \"beam_min\"" \
                ocmd="delcols \"Maj Min\"" \
                ocmd="addcol pb_corr -after Min_beam \"1.0/Pbcor_fit\"" \
                ocmd="addcol Type_SED_STR -after Type_SED \"Type_SED\"" \
                ocmd="addcol fit_alma_image_STR \"Image_fit\"" \
                ocmd="addcol fit_repetition_STR \"Simu_fit\"" \
                ocmd="addcol sim_alma_image_STR \"Image\"" \
                ocmd="addcol sim_repetition_STR \"Simu\"" \
                ocmd="addcol flag_matched \"(!NULL_Simu && !NULL_Simu_fit)\"" \
                ocmd="addcol flag_nonmatched_missed \"(!NULL_Simu && NULL_Simu_fit)\"" \
                ocmd="addcol flag_nonmatched_spurious \"(NULL_Simu && !NULL_Simu_fit)\"" \
                ocmd="addcol flag_null \"(NULL_Simu && NULL_Simu_fit)\"" \
                ocmd="addcol flag_S_Code_STR \"(S_Code_fit)\"" \
                ocmd="keepcols \"id S_in S_out e_S_out S_peak S_res noise Maj_in Min_in Maj_out Min_out Maj_beam Min_beam pb_corr ra dec z lgMstar lgSFR Type_SED_STR fit_alma_image_STR fit_repetition_STR sim_alma_image_STR sim_repetition_STR flag_matched flag_nonmatched_missed flag_nonmatched_spurious flag_null flag_S_Code_STR\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_all_entries.fits" \
                &>  "$output_dir/datatable_CrossMatched_all_entries.stilts.log"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn.html
                # multimode=group makes sure the cross-matching is one-to-one and unique
                # 
echo "Output to \"$output_dir/datatable_CrossMatched_all_entries.fits\"!"
fi


# 
# Note that for 'flag_nonmatched_spurious' sources, they do not have 'noise' from the simulated catalog, 
# so we need to cross-match 'fit_alma_image_STR fit_repetition_STR' to 'sim_alma_image_STR sim_repetition_STR'
# and get 'noise' from there. 
# 



# 
# Select matched ones
# 
topcat -stilts tpipe \
                in="$output_dir/datatable_CrossMatched_all_entries.fits" \
                cmd="select \"(flag_matched && Maj_beam>=0.1 && id!=11601)\"" \
                out="$output_dir/datatable_CrossMatched_only_matches.fits" \
                &>  "$output_dir/datatable_CrossMatched_only_matches.stilts.log"
echo "Output to \"$output_dir/datatable_CrossMatched_only_matches.fits\"!"








