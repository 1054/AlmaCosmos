#!/bin/bash
# 

source $(dirname $(dirname $(dirname $(dirname "${BASH_SOURCE[0]}"))))/Softwares/SETUP.bash


if [[ $(hostname) != "aida42198" ]]; then
    exit
fi



cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/

mkdir statistics_PyBDSM

if [[ -f "statistics_PyBDSM/list_of_commands.txt" ]]; then rm "statistics_PyBDSM/list_of_commands.txt"; fi

for (( i=1; i<=101; i++ )); do
    
    echo $(dirname "${BASH_SOURCE[0]}")/step_3_go_crossmatch.py "$i" >> "statistics_PyBDSM/list_of_commands.txt"
    
done

#almacosmos_cmd_run_in_parallel "statistics_PyBDSM/list_of_commands.txt"





