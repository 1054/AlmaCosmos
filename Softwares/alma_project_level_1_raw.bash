#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash 5.4.0
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code

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

if [[ ! -f "alma_archive_query_by_project_code_${Project_code}.txt" ]]; then
    $(dirname ${BASH_SOURCE[0]})/alma_archive_query_by_project_code.py "$Project_code" $@
fi

if [[ ! -f "meta_data_table.txt" ]]; then
    cp "alma_archive_query_by_project_code_${Project_code}.txt" \
       "meta_data_table.txt"
fi

# now creating data directory structure
echo "Now creating data directory structure"
echo $(dirname ${BASH_SOURCE[0]})/alma_archive_make_data_dirs_with_meta_table.py "meta_data_table.txt"
$(dirname ${BASH_SOURCE[0]})/alma_archive_make_data_dirs_with_meta_table.py "meta_data_table.txt"

# 
# common data directory structure:
# Level_1_Raw
# Level_2_Calib
# Level_3_Split
# Level_4_uvt
# Level_5_uvfit
# Level_6_Sci
