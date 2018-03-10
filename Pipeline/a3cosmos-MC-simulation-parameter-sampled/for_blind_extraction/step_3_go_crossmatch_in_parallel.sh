#!/bin/bash
# 

set -e 


if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code only works on aida42198!"
    exit
fi


echo ""
echo "This code will produce a list of commands into a \"list_of_commands.txt\" file, "
echo "then execute the commands with the tool \"almacosmos_cmd_run_in_parallel\". "
echo ""
echo "Sleeping for 5 seconds then start ..."
sleep 5
echo ""


source $(dirname $(dirname $(dirname $(dirname "${BASH_SOURCE[0]}"))))/Softwares/SETUP.bash


cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/

if [[ ! -d statistics_PyBDSM ]]; then mkdir statistics_PyBDSM; fi

if [[ -f "statistics_PyBDSM/list_of_commands.txt" ]]; then rm "statistics_PyBDSM/list_of_commands.txt"; fi

number_of_sources=$(cat ../list_for_pyBDSM.txt | wc -l)

for (( i=1; i<=$number_of_sources; i++ )); do
    
    echo $(dirname "${BASH_SOURCE[0]}")/step_3_go_crossmatch.py "$i" >> "statistics_PyBDSM/list_of_commands.txt"
    
done

echo ""
echo "Then, please run"
echo "  almacosmos_cmd_run_in_parallel \"statistics_PyBDSM/list_of_commands.txt\""
echo ""





