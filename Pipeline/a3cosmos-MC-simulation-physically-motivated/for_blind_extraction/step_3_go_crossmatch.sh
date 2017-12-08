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
                ocmd="addcol major \"Maj\"" \
                ocmd="addcol minor \"Min\"" \
                ocmd="delcols \"Maj Min\"" \
                ocmd="addcol Xf \"flux\"" \
                ocmd="addcol f \"Total_flux_fit*1e3\"" \
                ocmd="addcol snr_total \"Total_flux_fit/E_Total_flux_fit\"" \
                ocmd="addcol fpeak \"Peak_flux_fit*1e3\"" \
                ocmd="addcol noise \"rms\"" \
                ocmd="addcol Maj \"Maj_deconv_fit*3600.0\"" \
                ocmd="addcol Min \"Min_deconv_fit*3600.0\"" \
                ocmd="addcol pb_corr \"Pbcor_fit\"" \
                ocmd="addcol fit_alma_image_STR \"Image_fit\"" \
                ocmd="addcol fit_repetition_STR \"Simu_fit\"" \
                ocmd="addcol sim_alma_image_STR \"Image\"" \
                ocmd="addcol sim_repetition_STR \"Simu\"" \
                ocmd="addcol flag_matched \"(!NULL_Simu && !NULL_Simu_fit)\"" \
                ocmd="addcol flag_nonmatched_missed \"(!NULL_Simu && NULL_Simu_fit)\"" \
                ocmd="addcol flag_nonmatched_spurious \"(NULL_Simu && !NULL_Simu_fit)\"" \
                ocmd="addcol flag_null \"(NULL_Simu && NULL_Simu_fit)\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_all_entries.fits" \
                &>  "$output_dir/datatable_CrossMatched_all_entries.stilts.log"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn.html
                # multimode=group makes sure the cross-matching is one-to-one and unique
                # 
                # ocmd="keepcols \"id major minor Xf f snr_total fpeak noise ra dec ID_fit RA_fit DEC_fit Maj Min pb_corr z lgMstar lgSFR Type_SED fit_alma_image_STR fit_repetition_STR sim_alma_image_STR sim_repetition_STR flag_sim_at_nan\"" \





