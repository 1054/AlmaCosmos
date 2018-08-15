#!/bin/bash
# 
# The aim of this code is to combine multi-wavelength photometry for all sources 
# into one datatable_for_photometry.txt
# and run DeepFields.SuperDeblending SED fitting
# 

set -e 


# 
# Setup
# 
SED_fitting_Type="SED_fitting_magphys_priorz_with_upper_limits"
Input_Dir="Multi-wavelength_SEDs"
Output_Dir="Multi-wavelength_SED_Results/${SED_fitting_Type}/stage_2_read_results"
Do_Overwrite=1



# 
# Check necessary folders
# 
if [[ ! -d "$Input_Dir" ]]; then
    echo "Error! \"$Input_Dir\" directory was not found! Please run step_1 code first!"
    exit
fi



# 
# Read data tables
# 
source_list=($(cat "$Input_Dir/list_of_source_names.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 1))



# 
# Loop each source, prepare SED data file
# 

# make output dir
if [[ ! -d "$Output_Dir" ]]; then
    mkdir -p "$Output_Dir"
fi


# backup output
for item_name in \
"best-fit.param" \
"best-fit.res" \
"best-fit.rf"
do
    if [[ -f "$Output_Dir/${item_name}" ]]; then
        mv "$Output_Dir/${item_name}" \
           "$Output_Dir/${item_name}.backup"
    fi
done


# store current dir
Current_Dir=$(pwd)


# loop sources
for (( i=0; i<${#source_list[@]}; i++ )); do
    
    source_id=$(echo ${source_list[i]} | sed -e 's/^ID_//g')
    source_name=$(echo ${source_list[i]} | sed -e 's/^ID_//g')
    source_alias=""
    
    echo "ID_${source_name}  ($((i+1))/${#source_list[@]})"
    
    if [[ ! -d "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/" ]]; then
        echo "Error! \"$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/\" directory was not found! Please run step_3 code first!"
        #exit
        continue
    fi
    if [[ ! -f "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/best-fit_SED.sed" ]]; then
        echo "Error! \"$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/best-fit_SED.sed\" file was not found! Please run step_3 code first!"
        #exit
        continue
    fi
    if [[ ! -f "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/fit_chisq_z_sorted.out" ]]; then
        echo "Error! \"$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/fit_chisq_z_sorted.out\" file was not found! Please run step_3 code first!"
        #exit
        continue
    fi
    
    
    list_fit_name=($(cat $Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/fit_chisq_z_sorted.out | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 5))
    list_fit_z=($(cat $Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/fit_chisq_z_sorted.out | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 4))
    list_ref_z=($(cat $Input_Dir/ID_${source_name}/${SED_fitting_Type}/datatable_id_ra_dec_zprior.txt | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 5))
    
    
    # process magphys results
    if [[ ! -f "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/best-fit.param" ]] || [[ $Do_Overwrite -eq 1 ]]; then
        echo "cd \"$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/\""
        cd "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/"
        if [[ $Do_Overwrite -ge 2 ]]; then
            ~/Cloud/Github/Crab.Toolkit.michi2/bin/bin_magphys/magphys_highz/plot_sed_dzliu.bash > /dev/null 2>&1
        fi
        
        echo "~/Cloud/Github/Crab.Toolkit.michi2/bin/bin_magphys/magphys_highz/read_sed_results.py $(ls 1*.sed | tr '\n' ' ' | sed -e 's/ $//g') -obj-name ${source_name}"
        ~/Cloud/Github/Crab.Toolkit.michi2/bin/bin_magphys/magphys_highz/read_sed_results.py 1*.sed -obj-name ${source_name}
        
        
        best_fit_name="${list_fit_name[0]}"
        best_fit_rchi2=$(cat ${list_fit_name[0]}.param | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 9)
        if [[ "${list_ref_z[0]}" == *"specz"* ]]; then best_fit_is_specz=1; else best_fit_is_specz=0; fi
        echo "best_fit_name = $best_fit_name"
        echo "best_fit_rchi2 = $best_fit_rchi2"
        echo "best_fit_is_specz = $best_fit_is_specz"
        
        for (( j = 1; j < ${#list_fit_name[@]}; j++ )); do
            if [[ $best_fit_is_specz -eq 1 ]]; then
                threshold=2.0
                # if the first z_prior is a spec-z, then we must be careful: 
                # we keep the spec-z unless it is much worse, i.e., worse than a factor of threshold=1.5
            else
                threshold=1.0
            fi
            # compare rchi2
            read_fit_rchi2=$(cat ${list_fit_name[j]}.param | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 9)
            if [[ $(awk "BEGIN {if (($read_fit_rchi2)<($best_fit_rchi2)/($threshold)) print 1; else print 0;}") -eq 1 ]]; then
                # DEBUG
                if [[ $best_fit_is_specz -eq 1 ]]; then
                    echo "******"
                    echo "DEBUG: Found ${source_name} specz SED fitting worse than photoz SED fitting by a factor of ${threshold}!"
                    echo "******"
                    sleep 2.0
                fi
                # choose the least rchi2 fit as the best-fit
                best_fit_name="${list_fit_name[j]}"
                best_fit_rchi2="$read_fit_rchi2"
                if [[ "${list_ref_z[j]}" == *"specz"* ]]; then best_fit_is_specz=1; else best_fit_is_specz=0; fi
                echo "best_fit_name = $best_fit_name"
                echo "best_fit_rchi2 = $best_fit_rchi2"
                echo "best_fit_is_specz = $best_fit_is_specz"
            fi
        done
        
        
        for copy_type in sed fit ps pdf sed.um.mJy.txt res rf param; do
            echo cp "${best_fit_name}.${copy_type}" "best-fit.${copy_type}"
            cp "${best_fit_name}.${copy_type}" "best-fit.${copy_type}"
        done
        
        
        cd "$Current_Dir/"
    fi
    
    
    # combine magphys files
    for item_name in \
    "best-fit.param" \
    "best-fit.res" \
    "best-fit.rf"
    do
        if [[ ! -f "$Output_Dir/${item_name}" ]]; then
            cat "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/${item_name}" | head -n 1 > "$Output_Dir/${item_name}"
        fi
        cat "$Input_Dir/ID_${source_name}/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/${item_name}" | grep -v '^#' >> "$Output_Dir/${item_name}"
    done
    
done




# 
# DZLIU 20180618
# There is a bug in MAGPHYS
# The output "SFR(1e8)" in *.sed should be "sSFR(1e8)"!
# 















