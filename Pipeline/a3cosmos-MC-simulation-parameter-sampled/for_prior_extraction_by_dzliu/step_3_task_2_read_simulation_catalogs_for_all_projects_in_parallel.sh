#!/bin/bash
# 

if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code can only be ran on aida42198!"
    exit
fi

cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/output_GALFIT_dzliu

if [[ ! -f list_of_commands_for_reading_simulation_catalogs.txt ]]; then
find . -mindepth 1 -maxdepth 1 -type d -name "*_SB*_GB*_MB*" -print0 | 
while IFS= read -r -d $'\0' line; do
echo "cd $line; $(dirname ${BASH_SOURCE[0]})/step_3_task_2_read_simulation_catalogs_for_each_project.sh" >> list_of_commands_for_reading_simulation_catalogs.txt
done
fi

if [[ $(type almacosmos_cmd_run_in_parallel 2>/dev/null | wc -l) -eq 0 ]]; then
    source $(dirname $(dirname $(dirname $(dirname "${BASH_SOURCE[0]}"))))/Softwares/SETUP.bash
fi

echo "Then, please run: "
echo "  almacosmos_cmd_run_in_parallel \"list_of_commands_for_reading_simulation_catalogs.txt\" 3 60 [start [end [step]]]"
echo ""


