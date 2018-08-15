#!/bin/bash
# 


#__DOCUMENTATION__  
#__DOCUMENTATION__  Description: 
#__DOCUMENTATION__      Run MAGPHYS SED fitting. 
#__DOCUMENTATION__  
#__DOCUMENTATION__  Usage Example: 
#__DOCUMENTATION__      
#__DOCUMENTATION__      
#__DOCUMENTATION__  Input Files:
#__DOCUMENTATION__      Multi-wavelength_SEDs/
#__DOCUMENTATION__      
#__DOCUMENTATION__  Output Files:
#__DOCUMENTATION__      Multi-wavelength_Plots/SED_fitting_magphys_photoz_with_upper_limits_with_24um_with_APER3/stage_1_before_examining_z/
#__DOCUMENTATION__  



# The aim of this code is to combine multi-wavelength photometry for all sources 
# into one datatable_for_photometry.txt
# and run DeepFields.SuperDeblending SED fitting
# 

set -e


# 
# Set Parameters
# 
SED_fitting_Type="SED_fitting_magphys_photoz_with_upper_limits_with_24um_with_APER3"
output_dir="Multi-wavelength_SED_Plots/${SED_fitting_Type}/stage_1_before_examining_z" #<TODO># Tune this!


# 
# Check software dependencies
# 
if [[ ! -f "$HOME/Cloud/Github/Crab.Toolkit.michi2/SETUP.bash" ]]; then
    echo "Error! \"$HOME/Cloud/Github/Crab.Toolkit.michi2/SETUP.bash\" was not found! Please clone from \"https://github.com/1054/Crab.Toolkit.michi2\"!"
    exit
fi
source "$HOME/Cloud/Github/Crab.Toolkit.michi2/SETUP.bash"

if [[ ! -d "$HOME/Softwares/magphys/magphys_photoz" ]]; then
    echo "Error! \"$HOME/Softwares/magphys/magphys_photoz\" does not exist!"
    exit
fi
#if [[ ! -f "$HOME/Softwares/magphys/magphys_photoz_go" ]]; then
#    cp "$HOME/Cloud/Github/Crab.Toolkit.michi2/bin/bin_magphys/magphys_photoz_go" "$HOME/Softwares/magphys/magphys_photoz_go"
#    chmod +x "$HOME/Softwares/magphys/magphys_photoz_go"
#elif [[ $(diff "$HOME/Softwares/magphys/magphys_photoz_go" "$HOME/Cloud/Github/Crab.Toolkit.michi2/bin/bin_magphys/magphys_photoz_go" | wc -l) -gt 0 ]]; then
#    cp "$HOME/Cloud/Github/Crab.Toolkit.michi2/bin/bin_magphys/magphys_photoz_go" "$HOME/Softwares/magphys/magphys_photoz_go"
#    chmod +x "$HOME/Softwares/magphys/magphys_photoz_go"
#fi


# 
# Check necessary files
# 
if [[ ! -d "Multi-wavelength_SEDs" ]]; then
    echo "Error! \"Multi-wavelength_SEDs\" directory was not found! Please run step_1 code first!"
    exit
fi
if [[ ! -f "Multi-wavelength_SEDs/list_of_source_names.txt" ]]; then
    echo "Error! \"Multi-wavelength_SEDs/list_of_source_names.txt\" file was not found! Please run step_1 code first!"
    exit
fi
#if [[ ! -f "Multi-wavelength_SEDs/list_of_source_zphot.txt" ]]; then
#    echo "Error! \"Multi-wavelength_SEDs/list_of_source_zphot.txt\" file was not found! Please run step_1 code first!"
#    exit
#fi
#if [[ ! -f "Multi-wavelength_SEDs/list_of_source_zspec.txt" ]]; then
#    echo "Error! \"Multi-wavelength_SEDs/list_of_source_zspec.txt\" file was not found! Please run step_1 code first!"
#    exit
#fi
if [[ ! -f "Multi-wavelength_SEDs/list_of_source_radec.txt" ]]; then
    echo "Error! \"Multi-wavelength_SEDs/list_of_source_radec.txt\" file was not found! Please run step_1 code first!"
    exit
fi
#if [[ ! -f "datatable_magphys_photoz_source_list.txt" ]]; then
#    echo "Error! \"datatable_magphys_photoz_source_list.txt\" file was not found! Please prepare it before running this code!"
#    exit
#fi

if [[ ! -d "$output_dir" ]]; then
    mkdir -p "$output_dir"
fi


# 
# cd data dir
# 
cd "Multi-wavelength_SEDs/"



# 
# Read data tables
# 
source_list=($(cat "list_of_source_names.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 1))
source_ra=($(cat "list_of_source_radec.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 1))
source_dec=($(cat "list_of_source_radec.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 2))

#known_zspec_sou=($(cat "../datatable_known_zspec.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 1))
#known_zspec_val=($(cat "../datatable_known_zspec.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 2))
known_alias_sou=($(cat "../datatable_known_alias.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 1))
known_alias_val=($(cat "../datatable_known_alias.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 2))

magphys_photoz_source_list=()
#magphys_photoz_source_list=($(cat "../datatable_magphys_photoz_source_list.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 1))

#suspicious_zspec_sou=($(cat "../datatable_suspicious_zspec.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 1))
#suspicious_zphot_sou=($(cat "../datatable_suspicious_zphot.txt" | grep -v "^#" | sed -e 's/^ *//g' | tr -s ' ' | sed -e 's/ *$/ #/g' | cut -d ' ' -f 1))



# 
# Prepare parallel running scripts
# 
#magphys_parallel=9
magphys_parallel=16
for (( k = 0; k <= $magphys_parallel; k++ )); do
    echo "#!/bin/bash" > "run_${SED_fitting_Type}_for_all_magphys${k}.sh"
    echo "export PATH=\"\$HOME/Softwares/magphys${k}:\$PATH\"" >> "run_${SED_fitting_Type}_for_all_magphys${k}.sh"
    
    if [[ $k == 0 ]]; then
        echo "#!/bin/bash" > "batch_run_${SED_fitting_Type}_for_all.sh"
    fi
    echo "screen -d -S magphys${k} -m bash -c \"./run_${SED_fitting_Type}_for_all_magphys${k}.sh\"; sleep 30" >> "batch_run_${SED_fitting_Type}_for_all.sh"
done



# 
# Loop each source, prepare SED data file
# 
for (( i=0; i<${#source_list[@]}; i++ )); do
    
    source_name=$(echo ${source_list[i]} | sed -e 's/^ID_//g')
    source_alias=""
    
    # 
    # we only fit sources in the 'magphys_photoz_source_list' with magphys_photoz
    if [[ ${#magphys_photoz_source_list[@]} -gt 0 ]]; then
        magphys_photoz_source_check=0
        for (( k = 0; k < ${#magphys_photoz_source_list[@]}; k++ )); do
            if [[ "$source_name" == "${magphys_photoz_source_list[k]}" ]] || [[ "ID_$source_name" == "${magphys_photoz_source_list[k]}" ]]; then
                magphys_photoz_source_check=1
                break
            fi
        done
        if [[ $magphys_photoz_source_check -eq 0 ]]; then
            continue
        fi
    fi
    
    
    echo "ID_$source_name  ($((i+1))/${#source_list[@]})"
    
    if [[ ! -d "ID_$source_name" ]]; then
        echo "Error! \"ID_$source_name\" directory was not found! Please run step_1 code first!"
        exit
    fi
    
    # apply known alias
    for (( k=0; k<${#known_alias_sou[@]}; k++ )); do
        if [[ "$source_name" == "${known_alias_sou[k]}" ]]; then
            source_alias="_${known_alias_val[k]}"
        fi
    done
    
    # apply known spec-z
    #source_zspec=()
    #for (( k=0; k<${#known_zspec_sou[@]}; k++ )); do
    #    if [[ "$source_name" == "${known_zspec_sou[k]}" ]]; then
    #        source_zspec+=("${known_zspec_val[k]}")
    #    fi
    #done
    
    
    
    cd "ID_$source_name/"
    
    
    
    # remove wavelength dupl, do average
    if [[ ! -f "datatable_photometry_dupl.txt" ]]; then
        cp "datatable_photometry.txt" "datatable_photometry_dupl.txt"
        #mv "datatable_photometry.txt" "datatable_photometry_dupl.txt"
        #michi2_filter_flux_0sigma.py "datatable_photometry_dupl.txt" "datatable_photometry.txt"
    fi
    
    
    
    # prepare SED fitting files
    if [[ ! -d "${SED_fitting_Type}" ]]; then 
        mkdir "${SED_fitting_Type}"
    fi
    if [[ ! -f "${SED_fitting_Type}/datatable_id_ra_dec_zprior.txt" ]] && [[ ! -L "${SED_fitting_Type}/datatable_id_ra_dec_zprior.txt" ]]; then
        if [[ ! -f "datatable_id_ra_dec_zprior.txt" ]] && [[ ! -L "datatable_id_ra_dec_zprior.txt" ]]; then
            echo "Error! \"datatable_id_ra_dec_zphot.txt\" was not found for ID_$source_name! Please make sure step_3 code is run successfully!"
            exit
        else
            cp "datatable_id_ra_dec_zprior.txt" "${SED_fitting_Type}/"
        fi
    fi
    if [[ ! -f "${SED_fitting_Type}/datatable_photometry_magphys.txt" ]] && [[ ! -L "${SED_fitting_Type}/datatable_photometry_magphys.txt" ]]; then
        if [[ ! -f "datatable_photometry_dupl.txt" ]] && [[ ! -L "datatable_photometry_dupl.txt" ]]; then
            echo "Error! \"datatable_photometry_dupl.txt\" was not found for ID_$source_name! Please make sure step_3 code is run successfully!"
            exit
        else
            cd "${SED_fitting_Type}"
            #michi2_filter_flux_0sigma.py "../datatable_photometry_dupl.txt" "datatable_photometry_magphys.txt" #20180603#
            #michi2_filter_flux_0sigma_no_SNR_limit.py "../datatable_photometry_dupl.txt" "datatable_photometry_magphys.txt"
            michi2_filter_flux_2sigma_fit_infrared_upper_limits.py "../datatable_photometry_dupl.txt" "datatable_photometry_magphys.txt"
            cd "../"
        fi
    fi
    
    
    
    # cd back
    cd "../"
    
    
    
    # run SED fitting
    echo "#!/bin/bash" > "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "#source \"\$HOME/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP.bash\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "#export PATH=\"\$PATH:\$HOME/Softwares/magphys/magphys_photoz\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "cd \"ID_$source_name/${SED_fitting_Type}/\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "if [[ ! -f \"magphys_fitting/fit_1_with_datatable_photometry_magphys/1_crop.pdf\" ]]; then" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "magphys_highz_photoz_go_a3cosmos \"datatable_photometry_magphys.txt\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "date +\"%Y-%m-%d %H:%M:%S %Z\" > \"magphys_fitting/fit_1_with_datatable_photometry_magphys/fit_with_zscan_by_magphys_photoz\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "else" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "echo \"Found \\\"ID_$source_name/${SED_fitting_Type}/magphys_fitting/fit_1_with_datatable_photometry_magphys/1_crop.pdf\\\"! Will not overwrite!\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "fi" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "cp \"magphys_fitting/fit_1_with_datatable_photometry_magphys/1_crop.pdf\" \"../../../$output_dir/Plot_SED_Magphys_${source_name}${source_alias}.pdf\"" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    echo "" >> "run_${SED_fitting_Type}_for_ID_${source_name}.sh"
    
    # break
    #break
    
    # write into parallel running scripts
    
    magphys_parallel_plus_one=$(awk "BEGIN {print (${magphys_parallel}+1);}")
    k=$(awk "BEGIN {print ($i%${magphys_parallel_plus_one})}")
    echo "./run_${SED_fitting_Type}_for_ID_${source_name}.sh" >> "run_${SED_fitting_Type}_for_all_magphys${k}.sh"
    
done
    





# Then
# 
#if [[ ! -f "run_${SED_fitting_Type}_for_all.sh" ]]; then
#ls -1 "run_${SED_fitting_Type}_for_ID_"*".sh" | sort -V > "run_${SED_fitting_Type}_for_all.sh"
#chmod +x *.sh
#fi
#echo "Then please run \"almacosmos_cmd_run_in_parallel run_${SED_fitting_Type}_for_all.sh\" under \"Multi-wavelength_SEDs/\"!"
chmod +x *.sh
echo "Then please run \"batch_run_${SED_fitting_Type}_for_all.sh\" under \"Multi-wavelength_SEDs/\", "
echo "or run each parallized MAGPHYS \"run_${SED_fitting_Type}_for_all_magphys*.sh\" under \"Multi-wavelength_SEDs/\" separately, "
echo "or run each individual SED fitting \"run_${SED_fitting_Type}_for_ID_*.sh\" under \"Multi-wavelength_SEDs/\" but remember to first add MAGPHYS source code directory into \$PATH!"














