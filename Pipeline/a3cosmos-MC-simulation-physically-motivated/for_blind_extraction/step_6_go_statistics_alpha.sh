#!/bin/bash
# 

#cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/


crossmatched_cat="Statistics/datatable_CrossMatched_only_matches.fits" # the output of step_3_*.sh
output_dir="Statistics_alpha"

if [[ ! -f "$crossmatched_cat" ]]; then
    echo "Error! \"$crossmatched_cat\" was not found! Please run step_3 first!"
    exit 1
fi


# 
# Source AlmaCosmos/Software/SETUP.bash
# 
source_script="$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Pipeline/SETUP.bash"

if [[ ! -f "$source_script" ]]; then
    echo "Error! \"$source_script\" was not found! Please completely clone \"https://github.com/1054/AlmaCosmos\"!"
    exit 1
fi

source "$source_script"


# 
# run simu. stat. analyzing code
# 
a3cosmos-MC-simulation-statistics-analysis-alpha "$crossmatched_cat" "$output_dir"


