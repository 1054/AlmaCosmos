#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash 5.4.0
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code
if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_project_level_2_calib.bash Project_code"
    echo "Example: "
    echo "    alma_project_level_2_calib.bash 2013.1.00034.S"
    echo "Notes: "
    echo "    "
    exit
fi
Project_code="$1"

# define global variables
error_log_file=".$(basename ${BASH_SOURCE[0]}).err"
output_log_file=".$(basename ${BASH_SOURCE[0]}).log"
if [[ -f "$error_log_file" ]]; then mv "$error_log_file" "$error_log_file.2"; fi
if [[ -f "$output_log_file" ]]; then mv "$output_log_file" "$output_log_file.2"; fi

# define functions
echo_output()
{
    echo "$@"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$output_log_file"
}

echo_error()
{
    echo "*************************************************************"
    echo "$@"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$error_log_file"
    echo "*************************************************************"
}

# begin
echo_output "Began processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"

# check CASA
if [[ ! -d "$HOME/Softwares/CASA" ]]; then
    echo_error "Error! \"$HOME/Softwares/CASA\" was not found!" \
               "Sorry, we need to put all versions of CASA under \"$HOME/Softwares/CASA/Portable/\" directory!"
    exit 1
fi
if [[ ! -f "$HOME/Softwares/CASA/SETUP.bash" ]]; then
    echo_error "Error! \"$HOME/Softwares/CASA/SETUP.bash\" was not found!" \
               "Sorry, please ask Daizhong by emailing dzliu@mpia.de!"
    exit 1
fi
casa_setup_script_path="$HOME/Softwares/CASA/SETUP.bash"

# check meta table
if [[ ! -f "meta_data_table.txt" ]]; then
    echo_error "Error! \"meta_data_table.txt\" was not found! Please run previous steps first!"
    exit 255
fi

# check Level_2_Calib folder
if [[ ! -d Level_2_Calib ]]; then 
    echo_error "Error! \"Level_2_Calib\" does not exist! Please run previous steps first!"
    exit 255
fi

# read Level_2_Calib/DataSet_*
list_of_datasets=($(ls -1d Level_2_Calib/DataSet_* | sort -V))


# loop datasets and run ALMA calibration pipeline scriptForPI.py
for (( i = 0; i < ${#list_of_datasets[@]}; i++ )); do
    dataset_dir=${list_of_datasets[i]}
    
    # run pipelines
    echo_output "Now running ALMA calibration pipeline for \"${dataset_dir}\""
    echo_output "$(dirname ${BASH_SOURCE[0]})/alma_archive_run_alma_pipeline_scriptForPI.sh ${dataset_dir}"
    $(dirname ${BASH_SOURCE[0]})/alma_archive_run_alma_pipeline_scriptForPI.sh "${dataset_dir}"
    
    # check output
    if [[ ! -d "${dataset_dir}/calibrated" ]]; then
        echo_output "Successfully produced \"${dataset_dir}/calibrated\"!"
    else
        echo_error "Error! Failed to produce \"${dataset_dir}/calibrated\"!"
    fi
    
    if [[ $i -gt 0 ]]; then
        echo ""
        echo ""
    fi
    
done

# finish
echo_output "Finished processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"

# 
# common data directory structure:
# Level_1_Raw
# Level_2_Calib
# Level_3_Split
# Level_4_uvt
# Level_5_uvfit
# Level_6_Sci
