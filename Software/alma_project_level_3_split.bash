#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash 5.4.0
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code

if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_project_level_3_split.bash Project_code"
    echo "Example: "
    echo "    alma_project_level_3_split.bash 2013.1.00034.S"
    echo "Notes: "
    echo "    This code will call CASA to split each observing source into an individual measurement set for all datasets in the meta data table."
    exit
fi

Project_code="$1"

# define logging files and functions
error_log_file="$(pwd)/.$(basename ${BASH_SOURCE[0]}).err"
output_log_file="$(pwd)/.$(basename ${BASH_SOURCE[0]}).log"
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


# check GNU coreutils
if [[ $(uname -s) == "Darwin" ]]; then
    if [[ $(type gln 2>/dev/null | wc -l) -eq 0 ]]; then
        echo_error "Error! We need GNU ln! Please install \"coreutils\" via MacPorts or HomeBrew!"
        exit 1
    fi
    cmd_ln=gln
else
    cmd_ln=ln
fi


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


# check GILDAS
if [[ $(type mapping 2>/dev/null | wc -l) -eq 0 ]]; then
    # if not executable in the command line, try to find it in "$HOME/Softwares/GILDAS/"
    if [[ -d "$HOME/Softwares/GILDAS" ]] && [[ -f "$HOME/Softwares/GILDAS/SETUP.bash" ]]; then
        source "$HOME/Softwares/GILDAS/SETUP.bash"
    else
        # if not executable in the command line, nor in "$HOME/Softwares/GILDAS/", report error.
        echo_error "Error! \"mapping\" is not executable in the command line! Please check your \$PATH!"
        exit 1
    fi
fi


# check Crab.Toolkit.PdBI
if [[ $(type casa-ms-split 2>/dev/null | wc -l) -eq 0 ]]; then
    # if not executable in the command line, try to find it in "$HOME/Softwares/GILDAS/"
    if [[ -d "$HOME/Cloud/Github/Crab.Toolkit.PdBI" ]] && [[ -f "$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash" ]]; then
        source "$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash"
    else
        # if not executable in the command line, nor in "$HOME/Softwares/GILDAS/", report error.
        echo_error "Error! \"casa-ms-split\" is not executable in the command line! Please check your \$PATH!"
        exit 1
    fi
fi


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


# prepare Level_3_Split folder
if [[ ! -d Level_3_Split ]]; then 
    echo_output "mkdir Level_3_Split"
    mkdir Level_3_Split
fi
echo_output "cd Level_3_Split"
cd Level_3_Split


# loop datasets and run CASA split then GILDAS importuvfits
for (( i = 0; i < ${#list_of_datasets[@]}; i++ )); do
    
    DataSet_ms="calibrated.ms"
    DataSet_dir=$(basename ${list_of_datasets[i]})
    
    # print message
    echo_output "Now running CASA split for \"${DataSet_dir}\""
    
    # check Level_2_Calib DataSet_dir calibrated calibrated.ms
    if [[ ! -f ../Level_2_Calib/$DataSet_dir/README_CASA_VERSION ]]; then
        echo_error "Error! \"../Level_2_Calib/$DataSet_dir/README_CASA_VERSION\" was not found! Please run Level_2_Calib first! We will skip this dataset for now."
        continue
    fi
    
    # check Level_2_Calib DataSet_dir
    if [[ ! -d ../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms ]]; then
        echo_error "Error! \"../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms\" was not found! Please run Level_2_Calib first! We will skip this dataset for now."
        continue
    fi
    
    # prepare Level_3_Split DataSet_dir
    if [[ ! -d $DataSet_dir ]]; then
        echo_output "mkdir $DataSet_dir"
        mkdir $DataSet_dir
    fi
    echo_output "cd $DataSet_dir"
    cd $DataSet_dir
    
    # link Level_2_Calib calibrated.ms to Level_3_Split calibrated.ms
    echo_output "$cmd_ln -fsT ../../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms calibrated.ms"
    $cmd_ln -fsT ../../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms calibrated.ms
    
    # copy CASA version readme file
    echo_output "cp ../../Level_2_Calib/$DataSet_dir/README_CASA_VERSION README_CASA_VERSION"
    cp ../../Level_2_Calib/$DataSet_dir/README_CASA_VERSION README_CASA_VERSION
    
    # source CASA version
    echo_output "source \"$casa_setup_script_path\" \"README_CASA_VERSION\""
    source "$casa_setup_script_path" "README_CASA_VERSION"
    
    # run CASA listobs
    if [[ ! -f calibrated.ms.listobs.txt ]]; then
        echo_output "casa-ms-listobs -vis calibrated.ms"
        casa-ms-listobs -vis calibrated.ms
    fi
    if [[ ! -f calibrated.ms.listobs.txt ]]; then
        echo_error "Error! casa-ms-listobs -vis calibrated.ms FAILED!"
        exit 255
    fi
    
    # run CASA split, this will split each spw for all sources in the data (calibrated measurement set)
    if [[ $(find . -maxdepth 1 -type f -name "split_*_width2_SP.uvt" | wc -l) -eq 0 ]]; then
        echo_output "casa-ms-split -vis calibrated.ms -width 2 -timebin 30 -step split exportuvfits gildas | tee .casa-ms-split.log"
        casa-ms-split -vis calibrated.ms -width 2 -timebin 30 -step split exportuvfits gildas | tee .casa-ms-split.log
    else
        echo_output "Warning! Found split_*_width2_SP.uvt files! Will not re-run casa-ms-split!"
    fi
    if [[ $(find . -maxdepth 1 -type f -name "split_*_width2_SP.uvt" | wc -l) -eq 0 ]]; then
        echo_error "Error! casa-ms-split -vis calibrated.ms -width 2 -timebin 30 -step split exportuvfits gildas FAILED!"
    fi
    
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
