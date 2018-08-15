#!/bin/bash
# 


#__DOCUMENTATION__  
#__DOCUMENTATION__  Description: 
#__DOCUMENTATION__      Prepare folders and files for the SED fitting.
#__DOCUMENTATION__      This includes the extraction of photometry and prior redshifts from catalog into each galaxy folder. 
#__DOCUMENTATION__  
#__DOCUMENTATION__  Usage Example: 
#__DOCUMENTATION__      
#__DOCUMENTATION__      
#__DOCUMENTATION__  Input Files:
#__DOCUMENTATION__      Selected_Sample_v20180720c.photometry_with_prior_redshifts.fits
#__DOCUMENTATION__      
#__DOCUMENTATION__  Output Files:
#__DOCUMENTATION__      Multi-wavelength_SEDs/
#__DOCUMENTATION__  


# 
# The aim of this code is to get multi-wavelength photometry 
# from Laigle+2015 catalog 
# for each source in the input id catalog 
# 


set -e


source ~/Cloud/Github/Crab.Toolkit.michi2/SETUP.bash


# apply patch
if [[ ! -f "Selected_Sample_v20180720c.photometry_with_prior_redshifts.patched_20180414_18h53m.fits" ]]; then
     if [[ ! -f $(dirname "${BASH_SOURCE[0]}")/a_dzliu_patch_code_fix_catalog_flux_errors_20180814_18h53m.bash ]]; then
          echo "Error! Patch code \"$(dirname "${BASH_SOURCE[0]}")/a_dzliu_patch_code_fix_catalog_flux_errors_20180814_18h53m.bash\" was not found!"
          exit
     fi
fi


#input_cat="Selected_Sample_v20180720c.photometry_with_prior_redshifts.fits"
input_cat="Selected_Sample_v20180720c.photometry_with_prior_redshifts.patched_20180414_18h53m.fits" # 20180814 20h38m


overwrite=1


if [[ ! -d "Multi-wavelength_SEDs" ]]; then 
    mkdir "Multi-wavelength_SEDs"
fi

cd "Multi-wavelength_SEDs"

if [[ ! -f "extracted_flux.log" ]] || [[ $overwrite -ge 1 ]]; then
     michi2-extract-flux -catalog "../$input_cat"
fi
if [[ ! -f "extracted_wavelength.txt" ]] || [[ $overwrite -ge 1 ]]; then
     topcat -stilts tpipe in="../$input_cat" cmd="keepcols \"WAVELENGTH_ALMA\"" out="extracted_wavelength.txt" ofmt=ascii
fi
if [[ ! -f "extracted_zphot.txt" ]] || [[ $overwrite -ge 1 ]]; then
     topcat -stilts tpipe in="../$input_cat" cmd="keepcols \"z_phot Ref_z_phot ID_Master IMAGE_ALMA\"" out="extracted_zphot.txt" ofmt=CSV
fi
if [[ ! -f "extracted_zspec.txt" ]] || [[ $overwrite -ge 1 ]]; then
     topcat -stilts tpipe in="../$input_cat" cmd="keepcols \"z_spec Ref_z_spec ID_Master IMAGE_ALMA\"" out="extracted_zspec.txt" ofmt=CSV
fi
if [[ ! -f "extracted_zprior.txt" ]] || [[ $overwrite -ge 1 ]]; then
     topcat -stilts tpipe in="../$input_cat" cmd="keepcols \"z_prior Ref_z_prior ID_Master IMAGE_ALMA\"" out="extracted_zprior.txt" ofmt=CSV
fi
if [[ ! -f "extracted_ra.txt" ]] || [[ $overwrite -ge 1 ]]; then
     topcat -stilts tpipe in="../$input_cat" cmd="keepcols \"RA_Master\"" out="extracted_ra.txt" ofmt=ascii
fi
if [[ ! -f "extracted_dec.txt" ]] || [[ $overwrite -ge 1 ]]; then
     topcat -stilts tpipe in="../$input_cat" cmd="keepcols \"Dec_Master\"" out="extracted_dec.txt" ofmt=ascii
fi


if [[ -f "list_of_source_names.txt" ]] && [[ $overwrite -ge 1 ]]; then
     mv "list_of_source_names.txt" "list_of_source_names.txt.backup."$(date "+%Y%m%d.%H%M%S.%Z")
     mv "list_of_source_zphot.txt" "list_of_source_zphot.txt.backup."$(date "+%Y%m%d.%H%M%S.%Z")
     mv "list_of_source_zspec.txt" "list_of_source_zspec.txt.backup."$(date "+%Y%m%d.%H%M%S.%Z")
     mv "list_of_source_radec.txt" "list_of_source_radec.txt.backup."$(date "+%Y%m%d.%H%M%S.%Z")
fi


if [[ ! -f "list_of_source_names.txt" ]]; then
     echo "# SourceName" > "list_of_source_names.txt"
     echo "# zphot   SourceName" > "list_of_source_zphot.txt"
     echo "# zspec   SourceName" > "list_of_source_zspec.txt"
     echo "# RA   Dec   SourceName" > "list_of_source_radec.txt"
     i=1
     while [[ -f "extracted_flux_for_obj_at_row_${i}.txt" ]]; do
          ID_Master=$(cat "extracted_flux_for_obj_at_row_${i}.info" | grep "^ID_Master = " | sed -e 's/ID_Master = //g')
          ALMA_Wavelength=$(printf "%-20.6f" $(cat "extracted_wavelength.txt" | grep -v "^#" | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 1))
          Source_ra=$(cat "extracted_ra.txt" | grep -v "^#" | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 1)
          Source_dec=$(cat "extracted_dec.txt" | grep -v "^#" | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 1)
          # 
          Source_zphot=$(cat "extracted_zphot.txt" | tail -n +2 | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ',' -f 1); if [[ x$(echo "${Source_zphot}" | sed -e 's/[^0-9.+-eE]//g') == x ]]; then Source_zphot="-99"; fi
          Source_zspec=$(cat "extracted_zspec.txt" | tail -n +2 | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ',' -f 1); if [[ x$(echo "${Source_zspec}" | sed -e 's/[^0-9.+-eE]//g') == x ]]; then Source_zspec="-99"; fi; if [[ $(awk "BEGIN {if(${Source_zspec}>=10.0) print 1; else print 0;}") -eq 1 ]]; then Source_zspec="-100"; fi
          Source_zpriors=($(cat "extracted_zprior.txt" | tail -n +2 | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ',' -f 1))
          Source_refzpriors=($(cat "extracted_zprior.txt" | tail -n +2 | head -n $i | tail -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ',' -f 2))
          # tail -n +2 means skip the first line, which is the header line of CSV format 
          # 
          # check folder
          if [[ ! -d "ID_${ID_Master}" ]]; then 
               mkdir "ID_${ID_Master}"
          fi
          # 
          # check overwritting
          if [[ -f "ID_${ID_Master}/extracted_flux_for_obj_at_row_${i}.txt" ]]; then
               if [[ $overwrite -ge 1 ]]; then
                    echo "Overwritting! rm \"ID_${ID_Master}/extracted_flux_for_obj_at_row_\"*\".txt\""
                    rm "ID_${ID_Master}/extracted_flux_for_obj_at_row_"*".txt"
               else
                    echo "Error! Found existing \"ID_${ID_Master}/extracted_flux_for_obj_at_row_${i}.txt\"! We will not overwrite unless set in the script!"
                    echo "Exit!"
                    exit
               fi
          fi
          # 
          # check duplicated photometry
          # 
          dupl=$(find "ID_${ID_Master}" -maxdepth 1 -name "extracted_flux_for_obj_at_row_*.txt" | wc -l)
          # 
          if [[ $dupl -eq 0 ]]; then 
               echo "ID_${ID_Master}"
               echo "ID_${ID_Master}" >> "list_of_source_names.txt"
               echo "${Source_zphot}   ID_${ID_Master}" >> "list_of_source_zphot.txt"
               echo "${Source_zspec}   ID_${ID_Master}" >> "list_of_source_zspec.txt"
               echo "${Source_ra}   ${Source_dec}   ID_${ID_Master}" >> "list_of_source_radec.txt"
               # z_phot, z_spec (obsolete since 20180723)
               echo "# ID  RA  Dec  zphot" > "ID_${ID_Master}/datatable_id_ra_dec_zphot.txt"
               echo "# ID  RA  Dec  zspec" > "ID_${ID_Master}/datatable_id_ra_dec_zspec.txt"
               echo "${ID_Master}  ${Source_ra}  ${Source_dec}  ${Source_zphot}" >> "ID_${ID_Master}/datatable_id_ra_dec_zphot.txt"
               echo "${ID_Master}  ${Source_ra}  ${Source_dec}  ${Source_zspec}" >> "ID_${ID_Master}/datatable_id_ra_dec_zspec.txt"
               # z_prior (20180723)
               printf "# %-13s %15s %15s  %15s   %s\n" "ID" "RA" "Dec" "z_prior" "ref_z_prior" > "ID_${ID_Master}/datatable_id_ra_dec_zprior.txt"
               if [[ ${#Source_zpriors[@]} -gt 0 ]]; then
                    for (( j = 0; j < ${#Source_zpriors[@]}; j++ )); do
                         printf "%-15d %15.8f %15.8f  %15g   %s\n" "${ID_Master}" "${Source_ra}" "${Source_dec}" "${Source_zpriors[j]}" "${Source_refzpriors[j]}" >> "ID_${ID_Master}/datatable_id_ra_dec_zprior.txt"
                    done
               fi
          else
               dupl=$((dupl+1))
               echo "ID_${ID_Master} (dupl $dupl)"
          fi
          if [[ ! -f "ID_${ID_Master}/datatable_photometry.txt" ]]; then
               head -n 1 "extracted_flux_for_obj_at_row_${i}.txt" > "ID_${ID_Master}/datatable_photometry.txt"
          fi
          # set A3COSMOS photometry data points
          cat "extracted_flux_for_obj_at_row_${i}.txt" | grep -v "^#" | perl -p -e "s/([ ]+)nan([ ]+)([0-9.+-eE]+)([ ]+)([0-9.+-eE]+)([ ]+)(mJy)([ ]+)unknown_input_str_FLUX_ALMA/  $ALMA_Wavelength \3\4\5\6\7\8ALMA_A3COSMOS/g" >> "ID_${ID_Master}/datatable_photometry.txt"
          mv "extracted_flux_for_obj_at_row_${i}.info" "ID_${ID_Master}/"
          mv "extracted_flux_for_obj_at_row_${i}.txt" "ID_${ID_Master}/"
          i=$((i+1))
     done
     # 
     #mv "list_of_source_names.txt" "list_of_source_names_unsorted.txt"
     #cat "list_of_source_names_unsorted.txt" | grep -v "^#" | sort -V >  "list_of_source_names.txt"
fi



# Note that datatable_photometry.txt still contains duplicated wavelengths, 
# see "a_dzliu_code_step_3_run_sed_fitting_spdb.bash" for solving this.







