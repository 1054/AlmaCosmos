#!/bin/bash
# 

# check input argument
if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_archive_run_dzliu_pipeline_level123.sh -root root_directory -ms /path/to/calibrated.ms"
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
    echo "Sorry, please ask Daizhong by emailing astro.dzliu@gmail.com!"
    exit 1
fi
casa_setup_script_path="$HOME/Softwares/CASA/SETUP.bash"
gildas_setup_script_path="$HOME/Softwares/GILDAS/SETUP.bash"
crab_toolkit_pdbi_setup_script_path="$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash"


# read user inputs
root_directory=""
ms_directories=()
log_file=""
dry_run=0
i=1
while [[ $i -le $# ]]; do
    str_arg=$(echo "${!i}" | sed -e 's/^--/-/g' | awk '{print tolower($0)}')
    if [[ "$str_arg" == "-log" ]]; then
        if [[ $((i+1)) -le $# ]]; then
            i=$((i+1))
            log_file="${!i}"
        fi
    elif [[ "$str_arg" == "-root" ]]; then
        if [[ $((i+1)) -le $# ]]; then
            i=$((i+1))
            root_directory="${!i}"
        fi
    elif [[ "$str_arg" == "-ms" ]]; then
        if [[ $((i+1)) -le $# ]]; then
            i=$((i+1))
            ms_directories+=("${!i}")
        fi
    else
    elif [[ "$str_arg" == "-dry-run" ]]; then
        dry_run=1
    else
        ms_directories+=("${!i}")
    fi
    i=$((i+1))
done


# get current directory
current_dir=$(pwd)


# cd, but skip empty root_directory
if [[ x"$root_directory" != x"" ]]; then
    # check root_directory existance
    if [[ ! -d "$root_directory" ]] && [[ ! -L "$root_directory" ]]; then
        mkdir -p "$root_directory"
    fi
    # cd 
    cd "$root_directory"
fi


# create level dirs
if [[ ! -d "Level_1_Raw" ]]; then
    mkdir "Level_1_Raw"
fi
if [[ ! -d "Level_2_Calib" ]]; then
    mkdir "Level_2_Calib"
fi
if [[ ! -d "Level_3_Split" ]]; then
    mkdir "Level_3_Split"
fi


# deal with Level_2_Calib
echo cd "Level_2_Calib/"
cd "Level_2_Calib/"
datasets=()
for (( i = 0; i < ${#ms_directories[@]}; i++ )); do
    # ms_directory
    ms_directory="${ms_directories[i]}"
    # get a short name, take the mem_ous_id.
    ms_mem_id=$(echo "$ms_directory" | perl -p -e 's#.*/member.uid___A00[0-9]_([^./]+)/.*#\1#g')
    if [[ x"$ms_mem_id" == x ]]; then
        echo "Error! ms data path does not contain member.uid___*?"
        exit 1
    fi
    if [[ ! -d "DataSet_$ms_mem_id" ]]; then
        mkdir "DataSet_$ms_mem_id"
    fi
    if [[ ! -L "DataSet_$ms_mem_id/calibrated.ms" ]]; then
        ms_link=""
        if [[ x"$ms_directory" != x"/"* ]] && [[ x"$ms_directory" != x"~"* ]]; then
            # if $ms_directory is a relative path, it should be relative to $current_dir
            if [[ x"$root_directory" != x"" ]]; then
                ms_link="$current_dir/$ms_directory"
            else
                ms_link="../../$ms_directory"
            fi
        else
            # if $ms_directory is an absolute path, then no need to solve relative path
            ms_link="$ms_directory"
        fi
        # make links
        echo "#!/bin/bash" > "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
        echo "ln -fsT \"$ms_link\" \"DataSet_$ms_mem_id/calibrated.ms\"" >> "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
        ln -fsT "$ms_link" "DataSet_$ms_mem_id/calibrated.ms"
        # also copy readme
        if [[ -f $(dirname $(dirname "$ms_link"))/README ]] && [[ ! -f "DataSet_$ms_mem_id/README" ]]; then
            echo "cp \"$(dirname $(dirname "$ms_link"))/README\" \"DataSet_$ms_mem_id/README\"" >> "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
            cp $(dirname $(dirname "$ms_link"))/README "DataSet_$ms_mem_id/README"
        fi
        if [[ -f $(dirname $(dirname "$ms_link"))/README_CASA_VERSION ]] && [[ ! -f "DataSet_$ms_mem_id/README_CASA_VERSION" ]]; then
            echo "cp \"$(dirname $(dirname "$ms_link"))/README_CASA_VERSION\" \"DataSet_$ms_mem_id/README_CASA_VERSION\"" >> "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
            cp $(dirname $(dirname "$ms_link"))/README_CASA_VERSION "DataSet_$ms_mem_id/README_CASA_VERSION"
        fi
    fi
    datasets+=("DataSet_$ms_mem_id")
done
echo cd "../"
cd "../"


# deal with Level_3_Calib
echo cd "Level_3_Split/"
cd "Level_3_Split/"
for (( i = 0; i < ${#datasets[@]}; i++ )); do
    if [[ ! -f "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh" ]]; then
        echo "#!/bin/bash" > "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
        echo "ln -fsT \"../Level_2_Calib/${datasets[i]}/calibrated.ms\" \"calibrated.ms\"" >> "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
        ln -fsT "../Level_2_Calib/${datasets[i]}/calibrated.ms" "calibrated.ms"
        echo "cp \"../Level_2_Calib/${datasets[i]}/README\"* \"./${datasets[i]}/\"" >> "a_dzliu_code_make_links_for_DataSet_$ms_mem_id.sh"
        cp "../Level_2_Calib/${datasets[i]}/README"* "./${datasets[i]}/"
    fi
    if [[ ! -f "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh" ]]; then
        echo "#!/bin/bash" > "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "set -e" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "cd $(pwd)/ # pwd" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "cd ${datasets[i]}/" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "source \"$casa_setup_script_path\" README*" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "source \"$gildas_setup_script_path\"" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "source \"$crab_toolkit_pdbi_setup_script_path\"" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "casa-ms-split -vis calibrated.ms -width 25km/s -steps split exportuvfits" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        echo "date +\"%Y-%m-%d %Hh%Mm%Ss %Z\" > done_casa_split" >> "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        chmod +x "a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
    fi
    if [[ ! -f "done_casa_split" ]]; then
        if [[ $dry_run -eq 0 ]]; then
            ./"a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh"
        else
            echo "We are in dry run mode! Will not execute \"a_dzliu_code_run_casa_split_for_DataSet_$ms_mem_id.sh\"!"
        fi
    else
        echo "Found \"done_casa_split\" for DataSet_$ms_mem_id!"
    fi
    
done
echo cd "../"
cd "../"








