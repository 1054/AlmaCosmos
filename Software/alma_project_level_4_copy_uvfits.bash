#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash 5.4.0
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code

if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_project_level_4_copy_uvfits.bash Project_code"
    echo "Example: "
    echo "    alma_project_level_4_copy_uvfits.bash 2013.1.00034.S"
    echo "Notes: "
    echo "    This code will copy uvfits files from \"Level_3_Split\" to \"Level_4_Data_uvfits\" classified by source names."
    exit
fi

Project_code="$1"

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


# check meta data table file
if [[ ! -f "meta_data_table.txt" ]]; then
    echo_error "Error! \"meta_data_table.txt\" was not found! Please run previous steps first!"
    exit 255
fi


# check Level_3_Split folder
if [[ ! -d Level_3_Split ]]; then 
    echo_error "Error! \"Level_3_Split\" does not exist! Please run previous steps first!"
    exit 255
fi


# read Level_3_Split/DataSet_*
list_of_datasets=($(ls -1d Level_3_Split/DataSet_* | sort -V))


# prepare Level_4_Data_uvfits folder
if [[ ! -d Level_4_Data_uvfits ]]; then 
    mkdir Level_4_Data_uvfits
fi
echo_output cd Level_4_Data_uvfits
cd Level_4_Data_uvfits


# loop datasets and run CASA split then GILDAS importuvfits
for (( i = 0; i < ${#list_of_datasets[@]}; i++ )); do
    
    DataSet_dir=$(basename ${list_of_datasets[i]})
    
    # print message
    echo_output "Now sorting out unique sources in \"$DataSet_dir\" and copying *.uvfits"
    
    # check Level_3_Split DataSet_dir
    if [[ ! -d ../Level_3_Split/$DataSet_dir ]]; then
        echo_error "Error! \"../Level_3_Split/$DataSet_dir\" was not found! Please run Level_3_Split first! We will skip this dataset for now."
        continue
    fi
    
    # prepare Level_4_Data_uvfits DataSet_dir
    if [[ ! -d $DataSet_dir ]]; then
        mkdir $DataSet_dir
    fi
    echo_output cd $DataSet_dir
    cd $DataSet_dir
    
    # read source names
    list_of_unique_source_names=($(ls ../../Level_3_Split/$DataSet_dir/split_*_spw*_width*.uvfits | perl -p -e 's%.*split_(.*?)_spw[0-9]+_width[0-9]+.uvfits$%\1%g' | sort -V | uniq ) )
    if [[ ${#list_of_unique_source_names[@]} -eq 0 ]]; then
        echo_error "Error! Failed to find \"../../Level_3_Split/$DataSet_dir/split_*_spw*_width*.uvfits\" and get unique source names!"
        exit 255
    fi
    
    # loop list_of_unique_source_names and make dir for each source and copy uvfits files
    for (( j = 0; j < ${#list_of_unique_source_names[@]}; j++ )); do
        source_name=${list_of_unique_source_names[j]}
        if [[ ! -d "${source_name}" ]]; then
            echo_output mkdir "${source_name}"
            mkdir "${source_name}"
        fi
        echo_output cp ../../Level_3_Split/$DataSet_dir/split_"${source_name}"_spw*_width*.uvfits "${source_name}/"
        cp ../../Level_3_Split/$DataSet_dir/split_"${source_name}"_spw*_width*.uvfits "${source_name}/"
    done
    
    # cd back
    echo_output "cd ../"
    cd ../
    
    # print message
    if [[ $i -gt 0 ]]; then
        echo ""
        echo ""
    fi
    
done


echo_output "cd ../"
cd ../


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
