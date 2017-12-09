#!/bin/bash
# 

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
echo "cd $Script_Dir; pwd" > "Input_Script_Dir.txt"
echo "$HOME/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS" > "Input_Galaxy_Modeling_Dir.txt"

Data_Version="v20170604"
echo "$Data_Version" > "Input_Data_Version.txt"



# 
# download alma project list
# 
almacosmos_gdownload.py "list_project_rms_for_$Data_Version.sort_V.image_file.txt"

cat "list_project_rms_for_$Data_Version.sort_V.image_file.txt" | grep -v '^#' | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 8 | grep -v '^2011.0.00064.S' > "list_projects.txt"

if [[ ! -f "list_projects.txt" ]]; then
    echo "Error! Failed to get \"list_project_rms_for_$Data_Version.sort_V.image_file.txt\" from Google Drive and create \"list_projects.txt\"!"
    exit 1
fi

echo "Prepared \"$(pwd)/list_projects.txt\"!"
echo "Prepared \"$(pwd)/Input_*.txt\"!"





