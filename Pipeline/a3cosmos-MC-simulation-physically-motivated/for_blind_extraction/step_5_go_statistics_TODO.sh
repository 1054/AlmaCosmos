#!/bin/bash
# 

cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/check_simulated_image_fitting_statistics/

crossmatched_cat="CrossMatched/datatable_CrossMatched_all_entries.fits" # the output of step_1_*.sh
output_dir="check_MC_sim_statisitcs"
do_overwrite=1

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

check_input_file "$crossmatched_cat"

if [[ ! -f "$HOME/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros/run_simu_stats_almacosmos.sm" ]]; then
    echo "Error! \"$HOME/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros/run_simu_stats_almacosmos.sm\" was not found! Please install https://github.com/1054/Crab.Toolkit.CAAP!"
    exit 1
fi
if [[ ! -f "$HOME/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros/run_simu_stats_almacosmos_2D.sm" ]]; then
    echo "Error! \"$HOME/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros/run_simu_stats_almacosmos_2D.sm\" was not found! Please install https://github.com/1054/Crab.Toolkit.CAAP!"
    exit 1
fi

if [[ ! -d "$output_dir" ]]; then
    mkdir -p "$output_dir"
fi





# 
# make simu stat data table
# 
if [[ ! -f "$output_dir/simu_data_input.txt" ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_matched)\"" \
                cmd="addcol Area \"(PI/(4*ln(2))*Maj*Min)\"" \
                cmd="addcol fres \"f*0.0\"" \
                cmd="addcol S_Code_STR \"S_Code_fit\"" \
                cmd="keepcols \"id major minor Xf f snr_total fpeak noise ra dec ID_fit RA_fit DEC_fit Maj Min Area beam_maj beam_min fres pb_corr z lgMstar lgSFR Type_SED sim_alma_image_STR sim_repetition_STR S_Code_STR\"" \
                ofmt=ascii \
                out="$output_dir/simu_data_input.txt"
fi



# 
# cd output_dir and run Supermongo simu. stat. analyzing macros
# 
cd "$output_dir"

ln -fs "$HOME/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros/run_simu_stats_almacosmos.sm"

echo "macro read run_simu_stats_almacosmos.sm run_simu_stats_for_sim_data_input simu_data_input.txt" | sm | tee "run_simu_stats_almacosmos.log"

ln -fs "$HOME/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros/run_simu_stats_almacosmos_2D.sm"

echo "macro read run_simu_stats_almacosmos_2D.sm run_simu_stats_for_sim_data_input simu_data_input.txt" | sm | tee "run_simu_stats_almacosmos_2D.log"

#cat "run_simu_stats_almacosmos_2D.log" | grep -e " sig " -e " mean " -e "Current cell" > datatable_correction_table.1.txt
#perl -i -p -e 'undef $/; s/\n,/,/g' datatable_correction_table.1.txt
#perl -i -p -e 's/Current cell ([0-9]+):\s+Maj\s+([0-9.eE]+)[-]([0-9.eE]+)\s+fpeakSNR\s+([0-9.eE]+)[-]([0-9.eE]+),\s+([0-9]+)\s+dp$/\1 \2 \3 \4 \5 \6 0 0 0 0/g' "datatable_correction_table.1.txt"
#perl -i -p -e 's/Current cell ([0-9]+):\s+Maj\s+([0-9.eE]+)[-]([0-9.eE]+)\s+fpeakSNR\s+([0-9.eE]+)[-]([0-9.eE]+),\s+([0-9]+)\s+dp,.*mean\s+([0-9.+-eE]+)\s+med\s+([0-9.+-eE]+),.*sig\s+([0-9.+-eE]+)\s+([0-9.+-eE]+)/\1 \2 \3 \4 \5 \6 \7 \8 \9 ${10}/g' "datatable_correction_table.1.txt"
#echo '# cell_id Maj_lo Maj_hi SNR_peak_lo SNR_peak_hi n_dp bin_mean bin_med bin_sig_L68 bin_sig_H68' > "datatable_correction_table.2.txt"
#cat "datatable_correction_table.1.txt" >> "datatable_correction_table.2.txt"
#
#
#vim 
#
#sm
#data datatable_correction_table.1.txt read {cell_id 1 Maj_lo 2 Maj_hi 3 SNR_peak_lo 4 SNR_peak_hi 5 n_dp 6 bin_mean 7 bin_med 8 bin_sig_L68 9 bin_sig_H68 10}








