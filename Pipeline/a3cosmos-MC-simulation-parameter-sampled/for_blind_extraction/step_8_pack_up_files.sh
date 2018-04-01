#!/bin/bash
# 

set -e 


if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code only works on aida42198!"
    exit
fi


cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/output_PyBDSM_dzliu/

list_of_projects=($(cat list_for_pyBDSM.txt | grep -v "^#" | sed -e 's/.* -out *//g'))


echo ""
echo "This code will pack up files"


if [[ " $* " != *" go "* ]]; then
    echo ""
    echo "In default we will only show the commands but not execute them!"
    echo "Please give a \"go\" argument when calling this script to actually execute the commands!"
fi


echo ""
echo "Sleeping for 2 second then start ..."
sleep 2


for (( i = 0; i < ${#list_of_projects[@]}; i++ )); do
    echo ""
    echo "${list_of_projects[i]}"
    if [[ -f "../statistics_PyBDSM_dzliu/output_sim_data_table_${list_of_projects[i]}.txt" ]] && \
        [[ -f "../statistics_PyBDSM_dzliu/done_output_sim_data_table_${list_of_projects[i]}" ]]; then
        if [[ $(cat "../statistics_PyBDSM_dzliu/output_sim_data_table_${list_of_projects[i]}.txt" | wc -l) -gt 3000 ]]; then
            # seems OK, pack up this data dir
            echo "tar -czf --remove-files \"${list_of_projects[i]}.tar.gz\" \"${list_of_projects[i]}\""
            if [[ " $* " == *" go "* ]]; then
                tar -czf --remove-files "${list_of_projects[i]}.tar.gz" "${list_of_projects[i]}"
            fi
        fi
    fi
done








