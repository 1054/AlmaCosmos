#!/bin/bash
# 

if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_archive_run_alma_pipeline_concat_ms_split_cal.sh /path/to/calibrated/"
    echo ""
    echo "Notes:"
    echo "    This code will cd into \"/path/to/calibrated/\" and find \"uid___*.ms.split.cal\" and concatenate them into \"calibrated.ms\" in that directory."
    echo ""
    exit
fi


script_dir=$(perl -MCwd -e 'print Cwd::abs_path shift' $(dirname "${BASH_SOURCE[0]}"))
script_name=$(basename "${BASH_SOURCE[0]}" | sed -e 's/\.sh$//g')


echo "cd \"$1\""
cd "$1"


# check existing "calibrated_final.ms"
if [[ -d "calibrated_final.ms" ]] || [[ -d "calibrated_final.ms" ]]; then
    echo "Found exisiting \"calibrated_final.ms\"! Can not continue! Exit!"
    exit 1
fi

# check existing "calibrated.ms"
if [[ -d "calibrated.ms" ]] || [[ -d "calibrated.ms" ]]; then
    echo "Found exisiting \"calibrated.ms\"! Can not continue! Exit!"
    exit 1
fi


# run CASA
echo casa -c "import sys; sys.path.append(\"$script_dir\"); from $script_name import $script_name; $script_name(locals())"
casa --nogui --nologger --log2term --nocrashreport -c "import sys; sys.path.append(\"$script_dir\"); from $script_name import $script_name; $script_name(locals())"


# check result
if [[ ! -d "calibrated.ms" ]]; then
    echo "Error! Failed to run CASA concat and produce \"calibrated.ms\"!"
    exit 1
fi


