#!/bin/bash
# 

if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code only works on aida42198!"
    exit
fi


source ~/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash


cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/output_PyBDSM_dzliu/


if [[ ! -f list_of_pyBDSM.txt ]]; then
    cat ../output_PyBDSM/list_of_pyBDSM.txt | sed -e 's%^.*\.py%/home/dzliu/Cloud/Github/AlmaCosmos/Softwares/AlmaCosmos_Photometry_Blind_Extraction_PyBDSM_mod_mod.py%g'
fi


almacosmos_cmd_run_in_parallel list_of_pyBDSM.txt 5 60 # run 5 processes simultaneously, 30 seconds interval for each checking of number of processes


