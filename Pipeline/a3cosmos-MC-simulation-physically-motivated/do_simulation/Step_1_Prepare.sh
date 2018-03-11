#!/bin/bash
# 

#set -e

# 
# This script will download list_of_project.txt
# from "Google Drive"
# 

# 
# to run this script
# cd your working directory
# then run this script in terminal
# 
echo "Hostname: "$(/bin/hostname)
echo "PWD: "$(/bin/pwd)
Script_Path="${BASH_SOURCE[0]}"
Script_Dir=$(dirname $(dirname $(dirname $(dirname $Script_Path))))



# 
# check host and other dependencies
# 
if [[ ! -f "$Script_Dir/Softwares/SETUP.bash" ]]; then
    echo "Error! \"$Script_Dir/Softwares/SETUP.bash\" was not found! Please completely clone \"https://github.com/1054/AlmaCosmos.git\"!"
    exit 1
fi

if [[ ! -f "$Script_Dir/Pipeline/SETUP.bash" ]]; then
    echo "Error! \"$Script_Dir/Pipeline/SETUP.bash\" was not found! Please completely clone \"https://github.com/1054/AlmaCosmos.git\"!"
    exit 1
fi

source "$Script_Dir/Softwares/SETUP.bash"
source "$Script_Dir/Pipeline/SETUP.bash"

if [[ $(type pip 2>/dev/null | wc -l) -eq 0 ]]; then
    module load anaconda
fi

if [[ $(type sm 2>/dev/null | wc -l) -eq 0 ]]; then 
    echo "Error! Supermongo was not installed!"
    exit
fi

if [[ $(echo "load astroSfig.sm" | sm 2>&1 | wc -l) -ne 0 ]]; then 
    echo "Error! Supermongo does not contain necessary macros! Please contact liudz1054@gmail.com!"
    exit
fi



# 
# prepare config files
# 
pwd > "Input_Work_Dir.txt"

bash -c "cd $Script_Dir; pwd" > "Input_Script_Dir.txt"

if [[ -f "Input_Galaxy_Modeling_Dir.txt" ]]; then rm "Input_Galaxy_Modeling_Dir.txt"; fi
if [[ $(hostname) == "isaac"* ]]; then
    if [[ -d "/u/$USER/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS" ]]; then
        echo "/u/$USER/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS" > "Input_Galaxy_Modeling_Dir.txt"
    fi
elif [[ $(hostname) == "aida"* ]]; then
    if [[ -d "/disk1/$USER/Works/AlmaCosmos/Simulations/Cosmological_Galaxy_Modelling_for_COSMOS" ]]; then
        echo "/disk1/$USER/Works/AlmaCosmos/Simulations/Cosmological_Galaxy_Modelling_for_COSMOS" > "Input_Galaxy_Modeling_Dir.txt"
    fi
fi
if [[ ! -f "Input_Galaxy_Modeling_Dir.txt" ]]; then 
    echo "Error! \"Cosmological_Galaxy_Modelling_for_COSMOS\" was not found! Please contact liudz1054@gmail.com!"
    exit
fi


#echo "Google Drive A3COSMOS/Data/ALMA_full_archive/Calibrated_Images_by_Benjamin" > "Input_Data_Dir.txt"
echo "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli" > "Input_Data_Dir.txt"

#Data_Version="v20170604"
#Data_Version="v20180102"
#echo "$Data_Version" > "Input_Data_Version.txt"
echo "20180102" > "Input_Data_Version.txt"
echo "20180102_mod20180219" >> "Input_Data_Version.txt"

echo "20180102" >> "Input_Phot_Version.txt"



# 
# download alma project list
# 
if [[ ! -f "list_of_projects.txt" ]]; then
    almacosmos_gdownload.py 'A3COSMOS/Simulations/Monte_Carlo_Simulation_Physically_Motivated/20180311/list_of_projects.txt'
fi
# 
# list_projects.txt copied from 
# '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/20180102/fits_file_list_sorted_excluded_very_high-res_selected_unique_Mem_ous_id.txt'
# and 
# '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/20180102_mod20180219/fits_file_list_sorted_excluded_very_high_res_selected_unique_Mem_ous_id.txt'
# 
# then also excluded non-COSMOS images: 
# 2011.0.00539.S_*_ECDFS02_*
# 2011.0.00539.S_*_ELS01_*
# 2011.0.00539.S_*_ADFS01_*
# 2011.0.00539.S_*_XMM01_*
# 2011.0.00742.S_*__RX_J094144.51+385434.8__*
# 2012.1.00596.S_*_PKS0215+015_*

echo "Prepared \"$(pwd)/list_projects.txt\"!"
echo "Prepared \"$(pwd)/Input_*.txt\"!"




# 
# 
# 
if [[ $(hostname) == "aida"* ]]; then
    
    IFS=$'\n' read -d '' -r -a FitsNames < "list_of_projects.txt"
    echo "Read "${#FitsNames[@]}" ALMA projects/pointings from \"list_of_projects.txt\""
    
    mkdir "Input_images"
    cd "Input_images"
    
    for (( i=0; i<${#FitsNames[@]}; i++ )); do
        
        # check FitsName not empty
        if [[ x"${FitsNames[i]}" == x"" ]]; then
            continue
        fi
        
        # get FitsName without path and suffix
        FitsName=$(basename "${FitsNames[i]}" | sed -e 's/\.cont.I.image.fits//g')
        echo "$FitsName"
        
        # copy fits images
        ls "/disk1/$USER/Works/AlmaCosmos/Photometry/Source_Extraction_by_Benjamin/residual_images_020118/$FitsName.cont.I.residual.fits"
        ls "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/20180102/fits/$FitsName.cont.I.image.fits"
        ls "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/20180102/fits/$FitsName.cont.I.image.fits.pixel.statistics.txt"
        ls "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/20180102/fits/$FitsName.cont.I.clean-beam.fits"
        
        if [[ $? -ne 0 ]]; then break; fi
        
        ln -s "/disk1/$USER/Works/AlmaCosmos/Photometry/Source_Extraction_by_Benjamin/residual_images_020118/$FitsName.cont.I.residual.fits"
        ln -s "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/20180102/fits/$FitsName.cont.I.image.fits"
        ln -s "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/20180102/fits/$FitsName.cont.I.image.fits.pixel.statistics.txt"
        ln -s "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/20180102/fits/$FitsName.cont.I.clean-beam.fits"
        
    done
    
    cd ".."
fi






