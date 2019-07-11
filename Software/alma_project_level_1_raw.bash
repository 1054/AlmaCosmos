#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash 5.4.0
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code and meta user info (see usage)
if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_project_level_1_raw.bash Project_code"
    echo "Example: "
    echo "    alma_project_level_1_raw.bash 2013.1.00034.S"
    echo "Notes: "
    echo "    If the data is proprietary, please input --user XXX"
    exit
fi
Project_code="$1"

shift

if [[ $# -gt 0 ]]; then
    echo "$@" >> "meta_user_info.txt"
fi

# define logging files and functions
error_log_file=".$(basename ${BASH_SOURCE[0]}).err"
output_log_file=".$(basename ${BASH_SOURCE[0]}).log"
if [[ -f "$error_log_file" ]]; then mv "$error_log_file" "$error_log_file.2"; fi
if [[ -f "$output_log_file" ]]; then mv "$output_log_file" "$output_log_file.2"; fi

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
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$output_log_file"
    echo "*************************************************************"
}


# begin
echo_output "Began processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"


# query ALMA archive and prepare meta data table
if [[ ! -f "alma_archive_query_by_project_code_${Project_code}.txt" ]]; then
    echo_output "Querying ALMA archive by running following command: "
    echo_output "alma_archive_query_by_project_code.py $Project_code $@"
    $(dirname ${BASH_SOURCE[0]})/alma_archive_query_by_project_code.py "$Project_code" $@
fi

if [[ ! -f "alma_archive_query_by_project_code_${Project_code}.txt" ]]; then
    echo_error "Error! Sorry! Failed to run the code! Maybe you do not have the Python package \"astroquery\" or \"keyrings.alt\"?"
    exit 255
fi

if [[ ! -f "meta_data_table.txt" ]]; then
    cp "alma_archive_query_by_project_code_${Project_code}.txt" \
       "meta_data_table.txt"
fi


# now creating data directory structure
echo_output "Now creating data directory structure"
echo $(dirname ${BASH_SOURCE[0]})/alma_archive_make_data_dirs_with_meta_table.py "meta_data_table.txt"
$(dirname ${BASH_SOURCE[0]})/alma_archive_make_data_dirs_with_meta_table.py "meta_data_table.txt"


# finish
echo_output "Finished processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"
echo_output ""
echo_output ""


# 
# common data directory structure:
# Level_1_Raw
# Level_2_Calib
# Level_3_Split
# Level_4_Data_uvfits
# Level_4_Data_uvt
# Level_4_Run_clean
# Level_4_Run_uvfit
# Level_5_Sci
