#!/bin/bash
# 

cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/check_simulated_image_fitting_statistics/

crossmatched_cat="CrossMatched/datatable_CrossMatched_only_matches.fits" # the output of step_3_*.sh
output_dir="check_MC_sim_statisitcs"
do_overwrite=1

if [[ ! -f "$crossmatched_cat" ]]; then
    echo "Error! \"$crossmatched_cat\" was not found! Please run step_3 first!"
    exit 1
fi

macro_dir="$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Softwares/AlmaCosmos_Photometry_Simulation_Recovery_Statistical_Analysis_Macros"

if [[ ! -f "$macro_dir/run_simu_stats_in_param_grid.sm" ]]; then
    echo "Error! \"$macro_dir/run_simu_stats_in_param_grid.sm\" was not found! Please install \"https://github.com/1054/AlmaCosmos\"!"
    exit 1
fi

if [[ ! -f "$macro_dir/plot_simu_stats_in_param_grid.sm" ]]; then
    echo "Error! \"$macro_dir/plot_simu_stats_in_param_grid.sm\" was not found! Please install \"https://github.com/1054/AlmaCosmos\"!"
    exit 1
fi

if [[ ! -d "$output_dir" ]]; then
    mkdir -p "$output_dir"
fi





# 
# make simu stat data table
# 
if [[ ! -f "$output_dir/simu_data_input.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="keepcols \"id S_in S_out e_S_out S_peak S_res noise Maj_in Min_in Maj_out Min_out Maj_beam Min_beam pb_corr z lgMstar lgSFR Type_SED sim_alma_image_STR sim_repetition_STR\"" \
                ofmt=ascii \
                out="$output_dir/simu_data_input.txt"
fi

exit

# 
# cd output_dir and run Supermongo simu. stat. analyzing macros
# 
cd "$output_dir"

ln -fs "$macro_dir/run_simu_stats_in_param_grid.sm"

echo "macro read run_simu_stats_in_param_grid.sm run_simu_stats_in_param_grid" | sm | tee "run_simu_stats_in_param_grid.log"

ln -fs "$macro_dir/plot_simu_stats_in_param_grid.sm"

echo "macro read plot_simu_stats_in_param_grid.sm plot_simu_stats_in_param_grid" | sm | tee "plot_simu_stats_in_param_grid.log"







