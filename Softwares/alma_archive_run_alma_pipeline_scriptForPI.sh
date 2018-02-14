#!/bin/bash
# 

# check input argument

if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_archive_run_alma_pipeline_scriptForPI.sh root_directory"
    echo ""
    exit
fi

# check CASA

if [[ ! -d "$HOME/Softwares/CASA" ]]; then
    echo "Error! \"$HOME/Softwares/CASA\" was not found!"
    echo "Sorry, we need to put all versions of CASA under \"$HOME/Softwares/CASA/Portable/\" directory!"
    exit 1
fi
if [[ ! -f "$HOME/Softwares/CASA/SETUP.bash" ]]; then
    echo "Error! \"$HOME/Softwares/CASA/SETUP.bash\" was not found!"
    echo "Sorry, please ask Daizhong by emailing dzliu@mpia.de!"
    exit 1
fi
casa_setup_script_path="$HOME/Softwares/CASA/SETUP.bash"

# read user inputs

list_of_input_dirs=()
log_file=""
i=0
while [[ $i -le $# ]]; do
    str_arg=$(echo "${!i}" | sed -e 's/^--/-/g' | awk '{print tolower($0)}')
done
    if [[ "$str_arg" == "-log" ]]; then
        if [[ $((i+1)) -le $# ]]; then
            i=$((i+1))
            log_file="${!i}"
        fi
    else
        list_of_input_dirs+=("${!i}")
    fi
done

# get current directory

current_dir=$(pwd)

# find "scriptForPI.py" files

for (( i=0; i<=${#list_of_input_dirs[@]}; i++ )); do
    list_of_script_files=(find "${list_of_input_dirs[i]}" -type f -name "scriptForPI.py")
    for (( j = 0; j < ${#list_of_script_files[@]}; j++ )); do
        # 
        # store script file name and dir path
        script_file="${list_of_script_files[j]}"
        script_dir=$(dirname $(dirname "$script_file"))
        echo ""
        echo ""
        echo "********************************************************************************"
        echo "script_file = $script_file"
        echo "script_dir = $script_dir"
        echo "********************************************************************************"
        # 
        # check if "calibrated" dir already exists
        if [[ -d "$script_dir/calibrated" ]] || [[ -L "$script_dir/calibrated" ]]; then
            # if "calibrated" dir exists, check if it contains "calibrated_final.ms"
            if [[ -d "$script_dir/calibrated/calibrated_final.ms" ]] || [[ -L "$script_dir/calibrated/calibrated_final.ms" ]]; then
                if [[ $(find "$script_dir/calibrated/calibrated_final.ms/" -mindepth 1 -maxdepth 1 | wc -l) -eq 0 ]]; then
                    echo "Warning! \"$script_dir/calibrated/calibrated_final.ms\" is empty! Deleting it!"
                    echo "rm -r \"$script_dir/calibrated/calibrated_final.ms\""
                    rm -r "$script_dir/calibrated/calibrated_final.ms"
                fi
            fi
            if [[ -d "$script_dir/calibrated/calibrated_final.ms" ]] || [[ -L "$script_dir/calibrated/calibrated_final.ms" ]]; then
                echo "Found existing non-empty \"$script_dir/calibrated/calibrated_final.ms\"! Will not re-run the pipeline! Skip and continue!"
                continue
            fi
            # if "calibrated" dir exists, check if it contains "calibrated.ms"
            if [[ -d "$script_dir/calibrated/calibrated.ms" ]] || [[ -L "$script_dir/calibrated/calibrated.ms" ]]; then
                if [[ $(find "$script_dir/calibrated/calibrated.ms/" -mindepth 1 -maxdepth 1 | wc -l) -eq 0 ]]; then
                    echo "Warning! \"$script_dir/calibrated/calibrated.ms\" is empty! Deleting it!"
                    echo "rm -r \"$script_dir/calibrated/calibrated.ms\""
                    rm -r "$script_dir/calibrated/calibrated.ms"
                fi
            fi
            if [[ -d "$script_dir/calibrated/calibrated.ms" ]] || [[ -L "$script_dir/calibrated/calibrated.ms" ]]; then
                echo "Found existing non-empty \"$script_dir/calibrated/calibrated.ms\"! Will not re-run the pipeline! Skip and continue!"
                continue
            fi
            # if "calibrated" dir exists, but no "calibrated*.ms", then check if "uid___*.ms.split.cal" dirs exist or not
            list_of_ms_split_cal_dirs=($(find "$script_dir/calibrated/" -mindepth 1 -maxdepth 1 -type d -name "uid___*.ms.split.cal"))
            if [[ ${#list_of_ms_split_cal_dirs[@]} -gt 0 ]]; then
                echo "Found \"$script_dir/calibrated\" and \"uid___*.ms.split.cal\" therein but no \"calibrated_final.ms\" nor \"calibrated.ms\"! Will try to concatenate them."
                if [[ $(type alma_archive_run_alma_pipeline_concat_ms_split_cal.sh 2>/dev/null | wc -l) -ge 1 ]]; then
                    alma_archive_run_alma_pipeline_concat_ms_split_cal.sh "$script_dir/calibrated"
                    if [[ ! -d "$script_dir/calibrated/calibrated.ms" ]]; then
                        echo "Error! Failed to run alma_archive_run_alma_pipeline_concat_ms_split_cal.sh and produce \"calibrated.ms\"!"
                        exit 1
                    else
                        echo "Successfully concatenated \"uid___*.ms.split.cal\" into \"calibrated.ms\"! No need to re-run the pipeline! Continue!"
                        continue
                    fi
                else
                    if [[ -f $(dirname ${BASH_SOURCE[0]})"/alma_archive_run_alma_pipeline_concat_ms_split_cal.sh" ]]; then
                        $(dirname ${BASH_SOURCE[0]})/alma_archive_run_alma_pipeline_concat_ms_split_cal.sh "$script_dir/calibrated"
                        if [[ ! -d "$script_dir/calibrated/calibrated.ms" ]]; then
                            echo "Error! Failed to run alma_archive_run_alma_pipeline_concat_ms_split_cal.sh and produce \"calibrated.ms\"!"
                            exit 1
                        else
                            echo "Successfully concatenated \"uid___*.ms.split.cal\" into \"calibrated.ms\"! No need to re-run the pipeline! Continue!"
                            continue
                        fi
                    else
                        echo "Error! Could not find command \"alma_archive_run_alma_pipeline_concat_ms_split_cal.sh\", which should be shipped together with this code!"
                        exit 1
                    fi
                fi
            else
                # if not, then detele the whole "calibrated" directory
                echo "Found \"$script_dir/calibrated\" but no \"calibrated_final.ms\", \"calibrated.ms\" or \"uid___*.ms.split.cal\"! Will delete this \"calibrated\" directory!"
                echo "rm -r \"$script_dir/calibrated\""
                #rm -r "$script_dir/calibrated"
            fi
        fi
        # 
        # if the above code has not yet been continued, it means the "calibrated" data directory is invalid, so we have to re-run the pipeline (scriptForPI.py)
        if [[ -d "$script_dir/calibrated" ]] || [[ -L "$script_dir/calibrated" ]]; then
            echo "rm -r \"$script_dir/calibrated\""
            #rm -r "$script_dir/calibrated"
        fi
        # 
        # check directories
        if [[ ! -d "$script_dir/raw" ]] && [[ ! -L "$script_dir/raw" ]]; then
            echo "Error! Direcotry \"$script_dir/raw\" was not found!"
            exit 1
        fi
        if [[ ! -d "$script_dir/script" ]] && [[ ! -L "$script_dir/script" ]]; then
            echo "Error! Direcotry \"$script_dir/script\" was not found!"
            exit 1
        fi
        if [[ ! -f "$script_dir/README" ]] && [[ ! -L "$script_dir/README" ]]; then
            echo "Error! File \"$script_dir/README\" was not found!"
            exit 1
        fi
        # 
        # check if pipeline mode, 
        # cd script dir, 
        # source CASA with the version in README file, 
        # then run CASA
        echo "cd \"$script_dir/script/\""
        cd "$script_dir/script/"
        source "$casa_setup_script_path" "../README"
        if [[ $(type casa 2>/dev/null | wc -l) -eq 0 ]]; then
            echo "Error! CASA was not found!"
            exit 1
        fi
        if [[ $(find "$script_dir/script" -mindepth 1 -maxdepth 1 -type f -name "*_pipescript.py" | wc -l) -gt 0 ]] || \
            [[ $(find "$script_dir/script" -mindepth 1 -maxdepth 1 -type f -name "*_piperestorescript.py" | wc -l) -gt 0 ]]; then
            casa --pipeline -c "execfile('scriptForPI.py')"
        else
            casa -c "execfile('scriptForPI.py')"
        fi
        # 
        # cd back
        cd "$current_dir/"
    done
done





