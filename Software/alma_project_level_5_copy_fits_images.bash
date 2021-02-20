#!/bin/bash
# 


# read input Project_code

if [[ $# -lt 2 ]]; then
    echo "Usage: "
    echo "    alma_project_level_5_copy_fits_images.bash Project_code Deploy_Directory"
    echo "Example: "
    echo "    alma_project_level_5_copy_fits_images.bash 2013.1.00034.S Deploy_Directory"
    echo "Notes: "
    echo "    This code will copy image files under Level_4_Data_Images to Deploy_Directory."
    exit
fi

Project_code="$1"
Deploy_dir="$2"
Script_dir=$(dirname $(perl -MCwd -e 'print Cwd::abs_path shift' "${BASH_SOURCE[0]}"))

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


# check wcstools gethead sethead
for check_command in gethead sethead; do
    if [[ $(type ${check_command} 2>/dev/null | wc -l) -eq 0 ]]; then
        # if not executable in the command line, try to find it in "$HOME/Cloud/Github/Crab.Toolkit.PdBI"
        if [[ -d "$HOME/Cloud/Github/Crab.Toolkit.PdBI" ]] && [[ -f "$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash" ]]; then
            source "$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash"
        else
            # if not executable in the command line, nor in "$HOME/Cloud/Github/Crab.Toolkit.PdBI", report error.
            echo_error "Error! \"${check_command}\" is not executable in the command line! Please install WCSTOOLS, or check your \$PATH!"
            exit 1
        fi
    fi
done


# check meta data table file
if [[ ! -f "meta_data_table.txt" ]]; then
    echo_error "Error! \"meta_data_table.txt\" was not found! Please run previous steps first!"
    exit 255
fi


# check Level_4_Data_uvt folder
if [[ ! -d Level_4_Data_Images ]]; then 
    echo_error "Error! \"Level_4_Data_Images\" does not exist! Please run previous steps first!"
    exit 255
fi


# make Deploy_dir and the "fits" subdirectory
if [[ "$Deploy_dir" == *"/" ]]; then
    Deploy_dir=$(echo "$Deploy_dir" | perl -p -e 's%/$%%g')
fi
if [[ ! -d "$Deploy_dir/fits" ]]; then
    echo_output "mkdir -p \"$Deploy_dir/fits\""
    mkdir -p "$Deploy_dir/fits"
fi
if [[ ! -d "$Deploy_dir/fits" ]]; then
    echo_error "Error! Could not create output directory \"$Deploy_dir/fits\"! Please check your permission!"
    exit 255
fi


# read meta table and list mem_oud_id
list_project_code=$(cat "meta_data_table.txt" | awk '{ if(substr($1,0,1)!="#") print $1; }')
list_mem_oud_id=$(cat "meta_data_table.txt" | awk '{ if(substr($1,0,1)!="#") print $2; }')
list_alma_band=$(cat "meta_data_table.txt" | awk '{ if(substr($1,0,1)!="#") print $6; }')
list_dataset_id=$(cat "meta_data_table.txt" | awk '{ if(substr($1,0,1)!="#") print $9; }')


# check alma_project_meta_table.txt
if [[ -f "${Deploy_dir}/alma_project_meta_table.txt" ]]; then
    echo_output "mv \"${Deploy_dir}/alma_project_meta_table.txt\" \"${Deploy_dir}/alma_project_meta_table.txt.backup\""
    mv "${Deploy_dir}/alma_project_meta_table.txt" "${Deploy_dir}/alma_project_meta_table.txt.backup"
fi
echo_output "Initializing \"${Deploy_dir}/alma_project_meta_table.txt\""
printf "# %-15s %-25s %15s %15s %10s   %-s\n" 'project' 'mem_ous_id' 'OBSRA' 'OBSDEC' 'band' 'image_file' \
    > "${Deploy_dir}/alma_project_meta_table.txt"


# list_dataset_dir
list_image_files=($(find Level_4_Data_Images -mindepth 3 -maxdepth 3 -type f -name "output_*.cont.I.image.fits"))
for (( i = 0; i < ${#list_image_files[@]}; i++ )); do
    image_path="${list_image_files[i]}"
    dataset_id=$(basename $(dirname "${image_path}"))
    project_code=""
    mem_oud_id=""
    for (( j = 0; j < ${#list_dataset_id[@]}; j++ )); do
        if [[ "${list_dataset_id[j]}" == "$dataset_id" ]]; then
            project_code="${list_project_code[j]}"
            mem_oud_id="${list_mem_oud_id[j]}"
            band="${list_alma_band[j]}"
            break
        fi
    done
    if [[ "${project_code}"x == ""x ]] || [[ "${mem_oud_id}"x == ""x ]]; then
        echo_error "Error! Could not find dataset_id ${dataset_id} in meta_data_table.txt!"
        exit 255
    fi
    mem_oud_id_str=$(echo "${mem_oud_id}" | perl -p -e 's/[^a-zA-Z0-9_+-]/_/g')
    image_name=$(basename "image_path" | sed -e 's/output_//g')
    image_file="${project_code}.member.${mem_oud_id_str}.${image_name}"
    
    # copy fits file
    echo_output "cp \"${image_path}\" \"${Deploy_dir}/fits/${image_file}\""
    cp "${image_path}" "${Deploy_dir}/fits/${image_file}"
    
    # cd into the directory
    Current_dir=$(pwd -P)
    echo_output "cd \"${Deploy_dir}/fits\""
    cd "${Deploy_dir}/fits"
    # write mem_ous_id into the fits header
    if [[ $(gethead "${image_file}" MEMBER 2>/dev/null | wc -l) -eq 0 ]]; then
        echo_output "sethead \"${image_file}\" MEMBER=\"${mem_oud_id}\""
        sethead "${image_file}" MEMBER="${mem_oud_id}"
    fi
    # compute rms
    if [[ ! -f "${image_file}.pixel.statistics.txt" ]]; then
        echo_output "\"${Script_dir}\"/almacosmos_get_fits_image_pixel_histogram.py \"${image_file}\""
        "${Script_dir}"/almacosmos_get_fits_image_pixel_histogram.py "${image_file}" 2>&1 > "${image_file}.get.pixel.histogram.log"
        if [[ ! -f "${image_file}.pixel.statistics.txt" ]]; then
            echo_error "Error! Could not compute pixel histogram and rms!"
            exit 255
        fi
    fi
    rms=$(cat "${image_file}.pixel.statistics.txt" | grep "^Gaussian_sigma" | cut -d '=' -f 2 | sed -e 's/^ //g')
    if [[ "$rms" == *"#"* ]]; then
        rms=$(echo "$rms" | cut -d '#' -f 1)
    fi
    # 
    OBSRA=$(gethead "${image_file}" OBSRA)
    OBSDEC=$(gethead "${image_file}" OBSDEC)
    if [[ "$OBSRA"x == ""x ]] || [[ "$OBSDEC"x == ""x ]]; then
        echo_error "Error! Could not get OBSRA and OBSDEC keys in the fits header of \"${image_file}\"!"
        exit 255
    fi
    # 
    echo_output "cd \"${Current_dir}\""
    cd "${Current_dir}"
    
    # write to alma_project_meta_table.txt
    printf "  %-15s %-25s %15.10f %+15.10f %10s   %-s\n" "${project_code}" "${mem_ous_id}" $OBSRA $OBSDEC "$band" "${image_file}" \
        >> "${Deploy_dir}/alma_project_meta_table.txt"
    echo_output "Written to \"${Deploy_dir}/alma_project_meta_table.txt\""
done










