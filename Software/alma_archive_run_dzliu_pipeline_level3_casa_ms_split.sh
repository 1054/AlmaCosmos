#!/bin/bash
# 

# 
# print usage
# 
if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_archive_run_dzliu_pipeline_level3.sh root_directory [-no-gildas]"
    echo ""
    echo "Notes:"
    echo "    This code will find Level_2_Calib/DataSet_* directories under the input root directory, "
    echo "    Then run casa-ms-split inside it to split data for each source. "
    echo "    Then will make Level_3_uvfits and Level_3_uvt directories."
    echo ""
    exit
fi


# 
# check CASA
# 
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

if [[ $(type casa-ms-split 2>/dev/null | wc -l) -eq 0 ]]; then
    if [[ ! -f "$HOME/Softwares/GILDAS/SETUP.bash" ]]; then
        source "$HOME/Softwares/GILDAS/SETUP.bash"
    fi
fi
if [[ $(type casa-ms-split 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! Crab.Toolkit.PdBI \"casa-ms-split\" command was not found!"
    echo "Please download Crab.Toolkit.PdBI from http://github.com/1054/Crab.Toolkit.PdBI, then source the SETUP.bash under the downloaded directory."
    exit 1
fi
crab_toolkit_pdbi_setup_script_path=$(dirname $(dirname $(type casa-ms-split | sed -e 's%casa-ms-split is %%g')))/SETUP.bash



# 
# read user inputs
# 
root_directory=""
log_file=""
no_gildas=0
dry_run=0
unknown_options=()
i=1
while [[ $i -le $# ]]; do
    str_arg=$(echo "${!i}" | sed -e 's/^--/-/g' | awk '{print tolower($0)}')
    if [[ "$str_arg" == "-log" ]]; then
        if [[ $((i+1)) -le $# ]]; then
            i=$((i+1))
            log_file="${!i}"
        fi
    elif [[ "$str_arg" == "-no-gildas" ]]; then
        no_gildas=1
    elif [[ "$str_arg" == "-dry-run" ]]; then
        dry_run=1
    elif [[ "$str_arg" == "-"* ]]; then
        unknown_options+=("${!i}")
    else
        root_directory="${!i}"
    fi
    i=$((i+1))
done



# 
# Check GILDAS mapping
# 
if [[ $(type mapping 2>/dev/null | wc -l) -eq 0 ]] && [[ $no_gildas -eq 0 ]]; then
    if [[ ! -f "$HOME/Softwares/GILDAS/SETUP.bash" ]]; then
        source "$HOME/Softwares/GILDAS/SETUP.bash"
    fi
fi
if [[ $(type mapping 2>/dev/null | wc -l) -eq 0 ]] && [[ $no_gildas -eq 0 ]]; then
    echo "Error! GILDAS \"mapping\" command was not found!"
    echo "Please install GILDAS unless -no-gildas is given."
    exit 1
fi
#gildas_setup_script_path="$HOME/Softwares/GILDAS/SETUP.bash"



# 
# Get current directory
# 
current_dir=$(pwd)



# Check root_directory existance
if [[ x"$root_directory" != x"" ]] && [[ x"$root_directory" != x"." ]]; then
    if [[ ! -d "$root_directory" ]] && [[ ! -L "$root_directory" ]]; then
        echo "Error! The root directory \"$root_directory\" was not found!"
    fi
fi


# cd root_directory
if [[ x"$root_directory" != x"." ]]; then
    echo cd "$root_directory"
    cd "$root_directory"
fi


# Check Level_2_Calib
if [[ ! -d "Level_2_Calib" ]]; then
    echo "Error! \"Level_2_Calib\" was not found under \"$(pwd)\"! Please run \"alma_archive_run_dzliu_pipeline_level2_calib.sh\" first!"
    exit 255
fi


# Find datasets under Level_2_Calib
echo cd "Level_2_Calib/"
cd "Level_2_Calib/"
dataset_dirnames=($(ls -1d DataSet_*))


# Loop datasets and run casa-ms-split
for (( i = 0; i < ${#dataset_dirnames[@]}; i++ )); do
    
    dataset_dirname=${dataset_dirnames[i]}
    
    echo cd "$dataset_dirname"
    cd "$dataset_dirname"
    
    # source CASA version
    if [[ ! -f "README_CASA_VERSION" ]]; then
        echo "Error! The CASA version file \"$(pwd)/README_CASA_VERSION\" was not found! Please run \"alma_archive_run_dzliu_pipeline_level2_calib.sh\" first!"
        exit 255
    fi
    source "$casa_setup_script_path" README_CASA_VERSION
    
    # cd "calibrated" directory
    if [[ ! -d "calibrated" ]]; then
        echo "Error! The calibrated directory \"$(pwd)/calibrated\" was not found!"
        exit 255
    fi
    echo cd "calibrated"
    cd "calibrated"
    
    # check "calibrated.ms" datadir
    if [[ ! -d "calibrated.ms" ]] && [[ ! -L "calibrated.ms" ]]; then
        echo "Error! The calibrated data measurementset \"$(pwd)/calibrated.ms\" was not found!"
        exit 255
    fi
    
    # cd "run_casa_ms_split"
    if [[ ! -d "run_casa_ms_split" ]]; then 
        mkdir "run_casa_ms_split"
    fi
    echo cd "run_casa_ms_split"
    cd "run_casa_ms_split"
    ln -fs "../calibrated.ms"
    
    if [[ ! -f "done_casa_ms_split" ]]; then
        
        run_steps=(split exportuvfits)
        if [[ $no_gildas -eq 0 ]]; then
            run_steps+=(gildas)
        fi
        
        log_file="log_casa_ms_split_"$(date +"%Y%m%d_%Hh%Mm%Ss_%Z")".txt"
        
        # run casa-ms-split
        casa-ms-split -vis calibrated.ms -width 10km/s -timebin 30s -steps ${run_steps[@]} > "$log_file" 2>&1
        
        # check output files
        output_measurementsets=($(find . -maxdepth 1 -type d -name "split_*_spw*_width*.ms"))
        output_uvfits=($(find . -maxdepth 1 -type f -name "split_*_spw*_width*.uvfits"))
        output_uvtables=($(find . -maxdepth 1 -type f -name "split_*_spw*_width*_SP.uvt"))
        
        
        # mark it done
        if [[ ${#output_measurementsets[@]} -gt 0 ]] && [[ ${#output_uvfits[@]} -gt 0 ]] && [[ ${#output_uvtables[@]} -gt 0 ]]; then
            date +"%Y%m%d_%Hh%Mm%Ss_%Z" > "done_casa_ms_split"
        fi
        
    else
        
        echo "Found \"done_casa_ms_split\" for ${dataset_dirname}! Which means CASA split and exportuvfits are already done!"
        
    fi
    
    
    # if casa-ms-split was successful, move results to ../../../../Level_3_uvfits and ../../../../Level_3_uvt (current dir: Level_2_Calib/DataSet_*/calibrated/run_casa_ms_split/)
    if [[ -f "done_casa_ms_split" ]]; then
        output_measurementsets=($(find . -maxdepth 1 -type d -name "split_*_spw*_width*.ms"))
        output_uvfits=($(find . -maxdepth 1 -type f -name "split_*_spw*_width*.uvfits"))
        output_uvtables=($(find . -maxdepth 1 -type f -name "split_*_spw*_width*_SP.uvt"))
        split_galaxy_names=()
        for (( i = 0; i < ${#output_measurementsets[@]}; i++ )); do
            split_galaxy_names+=($(basename "${output_measurementsets[i]}" | perl -p -e 's/split_(.*)_spw([0-9]+)_width([0-9]+).ms/\1/g'))
        done
        unique_galaxy_names=($(echo "${split_galaxy_names[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
        echo "unique_galaxy_names: ${unique_galaxy_names[@]} (${#unique_galaxy_names[@]})"
        for (( i = 0; i < ${#unique_galaxy_names[@]}; i++ )); do
            # create galaxy_name dir
            galaxy_name=${unique_galaxy_names[i]}
            if [[ ! -d "../../../../Level_3_uvfits/${galaxy_name}/${dataset_dirname}" ]]; then
                echo mkdir -p "../../../../Level_3_uvfits/${galaxy_name}/${dataset_dirname}"
                mkdir -p "../../../../Level_3_uvfits/${galaxy_name}/${dataset_dirname}"
            fi
            if [[ ! -d "../../../../Level_3_uvt/${galaxy_name}/${dataset_dirname}" ]]; then
                echo mkdir -p "../../../../Level_3_uvt/${galaxy_name}/${dataset_dirname}"
                mkdir -p "../../../../Level_3_uvt/${galaxy_name}/${dataset_dirname}"
            fi
            # move results to ../../../../Level_3_uvfits and ../../../../Level_3_uvt (current dir: Level_2_Calib/DataSet_*/calibrated/run_casa_ms_split/)
            galaxy_uvfits=($(find . -maxdepth 1 -type f -name "split_${galaxy_name}_spw*_width*.uvfits"))
            galaxy_uvtables=($(find . -maxdepth 1 -type f -name "split_${galaxy_name}_spw*_width*_SP.uvt"))
            for (( j = 0; j < ${#galaxy_uvfits[@]}; j++ )); do
                echo cp "${galaxy_uvfits[j]}" "../../../../Level_3_uvfits/${galaxy_name}/${dataset_dirname}/"
                cp "${galaxy_uvfits[j]}" "../../../../Level_3_uvfits/${galaxy_name}/${dataset_dirname}/"
            done
            for (( j = 0; j < ${#galaxy_uvtables[@]}; j++ )); do
                echo cp "${galaxy_uvtables[j]}" "../../../../Level_3_uvt/${galaxy_name}/${dataset_dirname}/"
                cp "${galaxy_uvtables[j]}" "../../../../Level_3_uvt/${galaxy_name}/${dataset_dirname}/"
            done
        done
    fi
    
    
    # jump out "run_casa_ms_split"
    echo "cd ../"
    cd ../
    
    # jump out "calibrated"
    echo "cd ../"
    cd ../
    
    # jump out "DataSet_*"
    echo "cd ../"
    cd ../
    
    
    # print a separator line
    seq -s "-" 100 | tr -d '[:digit:]'; echo ""
    
done

# jump out "Level_2"
echo cd "../"
cd "../"








