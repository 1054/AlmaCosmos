#!/bin/bash
# 

source ~/Softwares/CASA/SETUP.bash 5.4.0
source ~/Softwares/GILDAS/SETUP.bash
source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


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

if [[ ! -f "meta_data_table.txt" ]]; then
    echo "Error! \"meta_data_table.txt\" was not found! Please run previous steps first!"
fi


# read Level_2_Calib/DataSet_*
list_of_datasets=($(ls -1d Level_2_Calib/DataSet_* | sort -V))


# prepare Level_3_Split folder
if [[ ! -d Level_3_Split ]]; then 
    mkdir Level_3_Split
fi
echo cd Level_3_Split
cd Level_3_Split


# loop datasets and run CASA split then GILDAS importuvfits
for (( i = 0; i < ${#list_of_datasets[@]}; i++ )); do
    
    DataSet_ms="calibrated.ms"
    DataSet_dir=$(basename ${list_of_datasets[i]})
    
    # print message
    echo "Now running CASA split for \"${DataSet_dir}\""
    
    # check Level_2_Calib DataSet_dir
    if [[ ! -d ../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms ]]; then
        echo "Error! \"../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms\" was not found! Please run Level_2_Calib first! We will skip this dataset for now."
        continue
    fi
    
    # prepare Level_3_Split DataSet_dir
    if [[ ! -d $DataSet_dir ]]; then
        mkdir $DataSet_dir
    fi
    echo cd $DataSet_dir
    cd $DataSet_dir
    
    # link Level_2_Calib calibrated.ms to Level_3_Split calibrated.ms
    ln -fsT ../../Level_2_Calib/$DataSet_dir/calibrated/$DataSet_ms calibrated.ms
    
    # run CASA listobs
    if [[ ! -f calibrated.ms.listobs.txt ]]; then
        casa-ms-listobs -vis calibrated.ms
    fi
    
    # run CASA split
    if [[ $(find . -maxdepth 1 -type f -name "split_*_width2_SP.uvt" | wc -l) -eq 0 ]]; then
        casa-ms-split -vis calibrated.ms -width 2 -timebin 30 -step split exportuvfits gildas
    else
        echo "Warning! Found split_*_width2_SP.uvt files! Will not re-run casa-ms-split!"
    fi
    
    # cd back
    echo cd ../
    cd ../
    
    # print message
    if [[ $i -gt 0 ]]; then
        echo ""
        echo ""
    fi
    
done


echo cd ../
cd ../

echo ""
echo "Done!"


# 
# common data directory structure:
# Level_1_Raw
# Level_2_Calib
# Level_3_Split
# Level_4_uvt
# Level_5_uvfit
# Level_6_Sci
