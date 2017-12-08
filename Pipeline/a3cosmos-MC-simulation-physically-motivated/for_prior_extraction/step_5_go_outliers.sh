#!/bin/bash
# 

cd "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20170730_on_Phys_MC_Simulated_Images/"

# case 1: galfit kept initial Gaussian size and did not fit
sim_image_name="2012.1.00978.S_SB4_GB1_MB1_GISMO-AK03_sci.spw0_1_2_3"
sim_repetition="w_889.341_z_3.000_lgMstar_11.50_SB"

# case 2: input a bright source but could not recover it
sim_image_name="2015.1.00137.S_SB3_GB1_MB1_z12_99_sci.spw0_1_2_3"
sim_repetition="w_872.699_z_3.000_lgMstar_11.50_SB"

# 
remote_host="149.217.42.198"
remote_dir="/disk1/dzliu/AlmaCosmos/S03_Photometry/ALMA_full_archive_Source_Extraction_by_Daizhong_Liu/Source_Simulation_by_Daizhong_Liu/Prior_Simulation_in_Prior_Extraction_Residual_Images_v20170803"
overwrite=1

if [[ ! -d "Recovered/$sim_image_name/$sim_repetition/astrodepth_prior_extraction_photometry/" ]] || [[ $overwrite -eq 1 ]]; then
    mkdir -p "Recovered/$sim_image_name/$sim_repetition/astrodepth_prior_extraction_photometry/"
    rsync -avz --stats --progress -e ssh \
        --include '**/' \
        --include 'fit_2.fits' \
        --include 'fit_2.log' \
        --include 'fit_2.out' \
        --exclude '*' \
        "$remote_host":"$remote_dir/Recovered/$sim_image_name/$sim_repetition/astrodepth_prior_extraction_photometry/" \
        "Recovered/$sim_image_name/$sim_repetition/astrodepth_prior_extraction_photometry/"
    echo "Output to \"Recovered/$sim_image_name/$sim_repetition/astrodepth_prior_extraction_photometry/\"!"
fi

# if [[ ! -d "$HOME/Work/AlmaCosmos/Simulations/Physical_MC_sim/20170803/Simulated/$sim_image_name/$sim_repetition/" ]] || [[ $overwrite -eq 1 ]]; then
#     mkdir -p "$HOME/Work/AlmaCosmos/Simulations/Physical_MC_sim/20170803/Simulated/$sim_image_name/$sim_repetition/"
#     rsync -avz --stats --progress -e ssh \
#         --include '**/' \
#         "$remote_host":"$remote_dir/Simulated/$sim_image_name/$sim_repetition/" \
#         "$HOME/Work/AlmaCosmos/Simulations/Physical_MC_sim/20170803/Simulated/$sim_image_name/$sim_repetition/"
#     echo "Output to \"$HOME/Work/AlmaCosmos/Simulations/Physical_MC_sim/20170803/Simulated/$sim_image_name/$sim_repetition/\"!"
# fi





