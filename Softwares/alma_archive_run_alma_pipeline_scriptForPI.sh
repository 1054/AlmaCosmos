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
i=1
while [[ $i -le $# ]]; do
    str_arg=$(echo "${!i}" | sed -e 's/^--/-/g' | awk '{print tolower($0)}')
    if [[ "$str_arg" == "-log" ]]; then
        if [[ $((i+1)) -le $# ]]; then
            i=$((i+1))
            log_file="${!i}"
        fi
    else
        list_of_input_dirs+=("${!i}")
    fi
    i=$((i+1))
done

# get current directory

current_dir=$(pwd)

# find "scriptForPI.py" files

for (( i=0; i<=${#list_of_input_dirs[@]}; i++ )); do
    # 
    # skip empty input dir
    if [[ x"${list_of_input_dirs[i]}" == x"" ]]; then
        continue
    fi
    # 
    # check input dir existance
    if [[ ! -d "${list_of_input_dirs[i]}" ]] && [[ ! -L "${list_of_input_dirs[i]}" ]]; then
        echo "Error! The input direcotry \"${list_of_input_dirs[i]}\" does not exist!"
        exit 1
    fi
    # 
    # find "scriptForPI.py" files
    list_of_script_files=($(find "${list_of_input_dirs[i]}" -type f -name "scriptForPI.py"))
    if [[ ${#list_of_script_files[@]} -eq 0 ]]; then
        list_of_script_files=($(find "${list_of_input_dirs[i]}" -type f -name "member*.scriptForPI.py"))
    fi
    # 
    # loop "scriptForPI.py" file 
    for (( j = 0; j < ${#list_of_script_files[@]}; j++ )); do
        # 
        # store script file name and dir path
        script_file="${list_of_script_files[j]}"
        script_name=$(basename "$script_file")
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
            if [[ ${#list_of_ms_split_cal_dirs[@]} -eq 0 ]]; then
                # 20180612 for CASA 5, ALMA Cycle 5 and later, file names are changed
                list_of_ms_split_cal_dirs=($(find "$script_dir/calibrated/" -mindepth 1 -maxdepth 1 -type d -name "uid___*.ms"))
            fi
            if [[ ${#list_of_ms_split_cal_dirs[@]} -eq 1 ]]; then
                echo "Found \"$script_dir/calibrated\" and one \"uid___*.ms.split.cal\" data therein but no \"calibrated_final.ms\" nor \"calibrated.ms\"! Will make a link."
                echo bash -c "cd \"$script_dir/calibrated\"; ln -fsT \"${list_of_ms_split_cal_dirs[0]}\" \"calibrated.ms\""
                bash -c "cd \"$script_dir/calibrated\"; ln -fsT \"${list_of_ms_split_cal_dirs[0]}\" \"calibrated.ms\""
                continue
            elif [[ ${#list_of_ms_split_cal_dirs[@]} -gt 1 ]]; then
                echo "Found \"$script_dir/calibrated\" and \"uid___*.ms.split.cal\" therein but no \"calibrated_final.ms\" nor \"calibrated.ms\"! Will try to concatenate them."
                # check README file which contains CASA version and source CASA version
                list_of_readme_files=($(find -L "${script_dir}" -name "README"))
                if [[ ${#list_of_readme_files[@]} -gt 0 ]]; then
                    source "$casa_setup_script_path" "${list_of_readme_files[0]}"
                else
                    list_of_readme_files=($(find -L "${script_dir}" -name "README_CASA_VERSION"))
                    if [[ ${#list_of_readme_files[@]} -gt 0 ]]; then
                        source "$casa_setup_script_path" "${list_of_readme_files[0]}"
                    else
                        echo "Error! Failed to find README file under ${script_dir}!"
                        exit 1
                    fi
                fi
                # run CASA concat
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
                #rm -r "$script_dir/calibrated" #<TODO><dry-run>#
            fi
        fi
        # 
        # if the above code has not yet been continued, it means the "calibrated" data directory is invalid, so we have to re-run the pipeline (scriptForPI.py)
        if [[ -d "$script_dir/calibrated" ]] || [[ -L "$script_dir/calibrated" ]]; then
            echo "rm -r \"$script_dir/calibrated\""
            #rm -r "$script_dir/calibrated" #<TODO><dry-run>#
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
        # 
        # check if pipeline mode, 
        # cd script dir, 
        # source CASA with the version in README file, 
        # then run CASA
        echo "cd \"$script_dir/script/\""
        cd "$script_dir/script/"
        if [[ -f "../README" ]] || [[ -L "../README" ]]; then
            source "$casa_setup_script_path" "../README"
        else
            if [[ -f "../README_CASA_VERSION" ]] || [[ -L "../README_CASA_VERSION" ]]; then
                source "$casa_setup_script_path" "../README_CASA_VERSION"
            else
                # if no REAME file then read "qa/*.tgz"
                if [[ -d "../qa" ]] || [[ -L "../qa" ]]; then
                    list_of_found_files=($(find -L "../qa" -name "*.tgz"))
                    if [[ ${#list_of_found_files[@]} -gt 0 ]]; then
                        $(dirname ${BASH_SOURCE[0]})/alma_archive_find_casa_version_in_qa_weblog.py "${list_of_found_files[0]}" > "../README_CASA_VERSION"
                        source "$casa_setup_script_path" "../README_CASA_VERSION"
                    else
                        echo "Error! Could not find \"$script_dir/qa/*.tgz\"!"
                        exit 1
                    fi
                else
                    echo "Error! Could not find either \"$script_dir/README\" or \"$script_dir/README_CASA_VERSION\" files or \"$script_dir/qa\" folder!"
                    exit 1
                fi
            fi
        fi
        if [[ $(type casa 2>/dev/null | wc -l) -eq 0 ]]; then
            echo "Error! CASA was not found!"
            exit 1
        fi
        if [[ $(find . -mindepth 1 -maxdepth 1 -type f -name "*_pipescript.py" | wc -l) -gt 0 ]] || \
            [[ $(find . -mindepth 1 -maxdepth 1 -type f -name "*_piperestorescript.py" | wc -l) -gt 0 ]]; then
            casa --pipeline -c "execfile('$script_name')"
        else
            casa -c "execfile('$script_name')"
        fi
        # 
        # cd back
        cd "$current_dir/"
    done
done





