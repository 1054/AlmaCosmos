#!/bin/bash

#source ~/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash
#source ~/Cloud/Github/AlmaCosmos/Pipeline/SETUP.bash

if [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"* ]] && [[ $(pwd) == *"PyBDSM"* ]]; then
    
    sim_rec_type="PHYS-PYBDSM"
    
    #$(dirname $(dirname ${BASH_SOURCE[0]}))/a3cosmos-MC-simulation-catalog-cross-match \
    #    -sim '/Users/dzliu/Work/AlmaCosmos/Simulations/Monte_Carlo_Simulation_Physically_Motivated/20171009/Simulated_Joined/datatable_Simulated_Concatenated_and_Filtered.fits' \
    #    -rec '/Users/dzliu/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/cat_pybdsm_concatenated_simulated_filtered.fits'
    
    # Requires input files:
    #    "cat_simulated_with_meta.fits"
    #    "cat_pybdsm_mJy.fits"
    
    cp '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20180102_on_Phys_MC_Simulated_Images/cat_pybdsm_concatenated_simulated_v300118.fits' .
    cp '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Simulations/Monte_Carlo_Simulation_Physically_Motivated/20180117/Output_catalogs.tar.gz' .
    tar -xzf "Output_catalogs.tar.gz"
    cp '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/20180102/fits_meta_table_for_dataset_v20180102_with_pbeam.fits' .
    topcat -stilts tmatchn nin=2 in1="Output_catalogs/Output_Prior_Simulation_Catalog.txt" ifmt1=ascii \
                   in2=fits_meta_table_for_dataset_v20180102_with_pbeam.fits \
                   icmd2="addcol Image \"replaceAll(image_file,\\\".cont.I.image.fits\\\",\\\"\\\")\"" \
                   multimode=pairs iref=1 join1=always suffix1="" suffix2="_meta" fixcols=dups \
                   matcher=exact values1="Image" values2="Image" \
                   ocmd="replacecol PA -units \"degree\" \"PA/PI*180.0\"" \
                   ocmd="delcols \"image_file\"" \
                   out="cat_simulated_with_meta.fits"
    topcat -stilts tpipe in="cat_pybdsm_concatenated_simulated_v300118.fits" \
                   cmd="replacecol Total_flux -units \"mJy\" \"Total_flux*1e3\"" \
                   cmd="replacecol E_Total_flux -units \"mJy\" \"E_Total_flux*1e3\"" \
                   cmd="replacecol Peak_flux -units \"mJy\" \"Peak_flux*1e3\"" \
                   cmd="replacecol E_Peak_flux -units \"mJy\" \"E_Peak_flux*1e3\"" \
                   cmd="replacecol Maj_deconv -units \"arcsec\" \"Maj_deconv*3600.0\"" \
                   cmd="replacecol E_Maj_deconv -units \"arcsec\" \"E_Maj_deconv*3600.0\"" \
                   cmd="replacecol Min_deconv -units \"arcsec\" \"Min_deconv*3600.0\"" \
                   cmd="replacecol E_Min_deconv -units \"arcsec\" \"E_Min_deconv*3600.0\"" \
                   cmd="replacecol PA -units \"degree\" \"PA\"" \
                   cmd="replacecol E_PA -units \"degree\" \"E_PA\"" \
                   cmd="delcols \"*Pbcor\"" \
                   cmd="select \"Source_id_in_image>=0\"" \
                   out=cat_pybdsm_mJy.fits
    $(dirname $(dirname ${BASH_SOURCE[0]}))/a3cosmos-MC-simulation-catalog-cross-match \
            -sim "cat_simulated_with_meta.fits" \
            -rec "cat_pybdsm_mJy.fits"



elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"* ]] && [[ $(pwd) == *"PyBDSM"* ]]; then
    
    sim_rec_type="FULL-PYBDSM"
    
    
    # The following indented step should be done in '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Simulations/Monte_Carlo_Simulation_Parameter_Sampled/for_dataset_v20180102/output_PyBDSM_dzliu/'
        # 
        # # must be run on aida machine
        # 
        # source ~/Softwares/Topcat/bin_setup.bash
        # 
        # if [[ -f concat_sim_rec_data_table.fits ]]; then
        #     mv concat_sim_rec_data_table.fits concat_sim_rec_data_table.fits.backup.$(date +"%Y%m%d.%Hh%Mm%Ss")
        # fi
        # 
        # ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-parameter-sampled/for_blind_extraction/step_4_go_concatenate.sh
        # 
        # ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-parameter-sampled/for_blind_extraction/step_5_go_filter.sh
        # 
        # # Outputs:
        # #     concat_sim_rec_data_table.fits
        # #     concat_sim_rec_data_table_filtered_outliers.fits
    
    # 
    
    cp "../output_PyBDSM_dzliu/concat_sim_rec_data_table.fits" .
    
    $(dirname ${BASH_SOURCE[0]})/a_dzliu_code_process_sim_rec_data_table_for_full_pybdsm_with_convolved_sizes.bash
    
    $(dirname ${BASH_SOURCE[0]})/a_dzliu_code_process_sim_rec_data_table_for_full_pybdsm_with_matching_flags.bash
    
    
fi



