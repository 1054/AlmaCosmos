#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash 5.4.0
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code

if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_project_level_5_make_images.bash Project_code [-dataset DataSet_01]"
    echo "Example: "
    echo "    alma_project_level_5_make_images.bash 2013.1.00034.S"
    echo "Notes: "
    echo "    This code will make clean cube images using ms data under \"Level_3_Split\" and store into \"Level_4_Data_Images\" classified by source names."
    exit
fi

Project_code="$1"; shift

# read user input
iarg=1
select_dataset=()
while [[ $iarg -le $# ]]; do
    istr=$(echo ${!iarg} | tr '[:upper:]' '[:lower:]')
    if [[ "$istr" == "-dataset" ]] && [[ $((iarg+1)) -le $# ]]; then
        iarg=$((iarg+1)); select_dataset+=("${!iarg}"); echo "Selecting \"${!iarg}\""
    fi
    iarg=$((iarg+1))
done

# define logging files and functions
error_log_file="$(pwd)/.$(basename ${BASH_SOURCE[0]}).err"
output_log_file="$(pwd)/.$(basename ${BASH_SOURCE[0]}).log"
if [[ -f "$error_log_file" ]]; then mv "$error_log_file" "$error_log_file.2"; fi
if [[ -f "$output_log_file" ]]; then mv "$output_log_file" "$output_log_file.2"; fi

echo_output()
{
    echo "$@"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$output_log_file"
}

echo_error()
{
    echo "*************************************************************"
    echo "$@"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$error_log_file"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$output_log_file"
    echo "*************************************************************"
}


# begin
echo_output "Began processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"


# check meta data table file
if [[ ! -f "meta_data_table.txt" ]]; then
    echo_error "Error! \"meta_data_table.txt\" was not found! Please run previous steps first!"
    exit 255
fi


# check Level_3_Split folder
if [[ ! -d Level_3_Split ]]; then 
    echo_error "Error! \"Level_3_Split\" does not exist! Please run previous steps first!"
    exit 255
fi


# read Level_3_Split/DataSet_*
if [[ ${#select_dataset[@]} -eq 0 ]]; then
    # if user has not input -dataset, then process all datasets
    list_of_datasets=($(ls -1d Level_3_Split/DataSet_* | sort -V))
else
    list_of_datasets=()
    for (( i = 0; i < ${#select_dataset[@]}; i++ )); do
        if [[ ! -d "Level_3_Split/${select_dataset[i]}" ]]; then
            echo "Error! \"Level_3_Split/${select_dataset[i]}\" was not found!"
            exit
        fi
        list_of_datasets+=($(ls -1d "Level_3_Split/${select_dataset[i]}"))
    done
fi


# check python casa lib dir
lib_python_dzliu_dir=$(dirname $(basename ${BASH_SOURCE[0]}))/lib_python_dzliu/crabcasa
if [[ ! -d "$lib_python_dzliu_dir" ]]; then
    echo "Error! lib_python_dzliu directory \"$lib_python_dzliu_dir\" was not found! It should be shipped with this code!"
    exit 255
fi


# prepare Level_4_Data_Images folder
if [[ ! -d Level_4_Data_Images ]]; then 
    mkdir Level_4_Data_Images
fi
echo_output cd Level_4_Data_Images
cd Level_4_Data_Images


# loop datasets and run CASA split then GILDAS importuvfits
for (( i = 0; i < ${#list_of_datasets[@]}; i++ )); do
    
    DataSet_dir=$(basename ${list_of_datasets[i]})
    
    # print message
    echo_output "Now sorting out unique sources in \"$DataSet_dir\" and linking *.ms"
    
    # check Level_3_Split DataSet_dir
    if [[ ! -d ../Level_3_Split/$DataSet_dir ]]; then
        echo_error "Error! \"../Level_3_Split/$DataSet_dir\" was not found! Please run Level_3_Split first! We will skip this dataset for now."
        continue
    fi
    
    # prepare Level_4_Data_Images DataSet_dir
    if [[ ! -d $DataSet_dir ]]; then
        mkdir $DataSet_dir
    fi
    echo_output cd $DataSet_dir
    cd $DataSet_dir
    
    # read source names
    list_of_unique_source_names=($(ls -1d ../../Level_3_Split/$DataSet_dir/split_*_spw*_width*.ms | perl -p -e 's%.*split_(.*?)_spw[0-9]+_width[0-9]+.ms$%\1%g' | sort -V | uniq ) )
    if [[ ${#list_of_unique_source_names[@]} -eq 0 ]]; then
        echo_error "Error! Failed to find \"../../Level_3_Split/$DataSet_dir/split_*_spw*_width*.ms\" and get unique source names!"
        exit 255
    fi
    
    # loop list_of_unique_source_names and make dir for each source and link ms files
    for (( j = 0; j < ${#list_of_unique_source_names[@]}; j++ )); do
        source_name=${list_of_unique_source_names[j]}
        if [[ ! -d "${source_name}" ]]; then
            echo_output mkdir "${source_name}"
            mkdir "${source_name}"
        fi
        
        # find each ms file
        list_of_ms_data=($(ls -1d ../../Level_3_Split/$DataSet_dir/split_*_spw*_width*.ms | sort -V | uniq ) )
        
        for (( k = 0; k < ${#list_of_ms_data[@]}; k++ )); do
            ms_data="${list_of_ms_data[k]}" # this includes the suffix ".ms"
            if [[ ! -L "${source_name}/${ms_data}" ]]; then
                echo_output ln -fsT ../../Level_3_Split/$DataSet_dir/${ms_data} "${source_name}/${ms_data}"
                ln -fsT ../../Level_3_Split/$DataSet_dir/${ms_data} "${source_name}/${ms_data}"
            fi
            
            echo_output "cd ${source_name}"
            cd "${source_name}"
            run_script="run_tclean_${ms_data}.bash"
            py_script="run_tclean_${ms_data}.py"
            log_script="run_tclean_${ms_data}.log"
            done_script="run_tclean_${ms_data}.done"
            if [[ ! -f "${run_script}" ]]; then
                if [[ -f "${done_script}" ]]; then
                    mv "${done_script}" "${done_script}.backup" # remove previous done_script
                fi
                # write bash script which will launch CASA and run the python script
                echo "#!/bin/bash"                                                    >> "${run_script}"
                echo "#"                                                              >> "${run_script}"
                echo "if [[ \$(type casa 2>/dev/null | wc -l) -eq 0 ]]; then"         >> "${run_script}"
                echo "    if [[ -f ~/Softwares/CASA/SETUP.bash ]]; then"              >> "${run_script}"
                echo "        source ~/Softwares/CASA/SETUP.bash"                     >> "${run_script}" # here I try to see if we have CASA
                echo "    else"                                                       >> "${run_script}"
                echo "        echo \"Error! casa command does not exist!\"; exit 255" >> "${run_script}"
                echo "    fi"                                                         >> "${run_script}"
                echo "fi"                                                             >> "${run_script}"
                echo ""                                                               >> "${run_script}"
                echo "casa --nogui --nologger --log2term -c \"${py_script}\" "        >> "${run_script}"
                echo ""                                                               >> "${run_script}"
                echo "if [[ $? -eq 0 ]]; then"                                        >> "${run_script}"
                echo "    date \"+%Y-%m-%d %Hh%Mm%Ss %Z\" > ${done_script}"           >> "${run_script}"
                echo "fi"                                                             >> "${run_script}"
                echo ""                                                               >> "${run_script}"
                chmod +x "${run_script}"
                # write the python script which will load the 'dzliu_clean.py' library and run cube clean
                echo "# run this in CASA"                                                                                   >> "${py_script}"
                echo "sys.path.append(\"${lib_python_dzliu_dir}\")"                                                         >> "${py_script}"
                echo "import dzliu_clean"                                                                                   >> "${py_script}"
                echo "reload(dzliu_clean)"                                                                                  >> "${py_script}"
                echo "dzliu_clean.dzliu_clean(\"${ms_data}\", line_name='cube', line_velocity=-1, line_velocity_width=-1)"  >> "${py_script}"
                echo ""                                                                                                     >> "${py_script}"
                chmod +x "${py_script}"
            fi
            if [[ ! -f "${done_script}" ]]; then
                chmod +x "${run_script}"
                echo_output "Running ${run_script} > ${log_script}"
                ./"${run_script}" > "${log_script}"
                if [[ ! -f "${done_script}" ]]; then
                    echo "Error! Failed to run the script \"${run_script}\"!"
                    exit 255
                fi
            fi
            echo_output "cd ../"
            cd ../
            
        done
        
    done
    
    # cd back
    echo_output "cd ../"
    cd ../
    
    # print message
    if [[ $i -gt 0 ]]; then
        echo ""
        echo ""
    fi
    
done


echo_output "cd ../"
cd ../


# finish
echo_output "Finished processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"
echo_output ""
echo_output ""


# 
# common data directory structure:
# Level_1_Raw
# Level_2_Calib
# Level_3_Split
# Level_4_Data_Images
# Level_4_Data_uvt
# Level_4_Run_clean
# Level_4_Run_uvfit
# Level_5_Sci
