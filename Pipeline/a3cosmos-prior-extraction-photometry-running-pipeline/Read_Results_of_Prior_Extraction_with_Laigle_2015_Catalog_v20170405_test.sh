#!/bin/bash
# 






# 
# Set Output dir
# 
OutputDir="Prior_Extraction_with_Laigle_2015_Catalog_v20170222" #<TODO>#

# 
# Check output dir
# 
if [[ ! -d "$OutputDir" ]]; then
    echo "Error! The output directory \"$OutputDir\" does not exist! Abort!"; exit 1
fi

# 
# Read Sci Images
# 
Old_IFS=$IFS
IFS=$'\n' SciImages=($(<"$OutputDir/List_of_Input_Sci_Images.txt"))
IFS=$'\n' PsfImages=($(<"$OutputDir/List_of_Input_Psf_Images.txt"))
IFS="$Old_IFS"
if [[ ${#SciImages[@]} -eq 0 || ${#PsfImages[@]} -eq 0 ]]; then
    echo "Error! Failed to read \"$OutputDir/List_of_Input_Sci_Images.txt\" and \"$OutputDir/List_of_Input_Psf_Images.txt\"!"
    exit 1
fi





# 
# Prepare ouput file
# 
if [[ -f "Read_Results_all_final_detections.txt.backup" ]]; then
    mv "Read_Results_all_final_detections.txt.backup" "Read_Results_all_final_detections.txt.backup.backup"
fi
if [[ -f "Read_Results_all_final_detections.txt" ]]; then
    mv "Read_Results_all_final_detections.txt" "Read_Results_all_final_detections.txt.backup"

for fit_step in get_pix fit_0 fit_1 fit_2; do
    if [[ -f "Read_Results_all_final_detections_${fit_step}.txt.backup" ]]; then
        mv "Read_Results_all_final_detections_${fit_step}.txt.backup" "Read_Results_all_final_detections_${fit_step}.txt.backup.backup"
    fi
    if [[ -f "Read_Results_all_final_detections_${fit_step}.txt" ]]; then
        mv "Read_Results_all_final_detections_${fit_step}.txt" "Read_Results_all_final_detections_${fit_step}.txt.backup"
    fi
    
    if [[ -f "Read_Results_all_final_fluxes_${fit_step}.txt.backup" ]]; then
        mv "Read_Results_all_final_fluxes_${fit_step}.txt.backup" "Read_Results_all_final_fluxes_${fit_step}.txt.backup.backup"
    fi
    if [[ -f "Read_Results_all_final_fluxes_${fit_step}.txt" ]]; then
        mv "Read_Results_all_final_fluxes_${fit_step}.txt" "Read_Results_all_final_fluxes_${fit_step}.txt.backup"
    fi
done

echo ""
echo ""
echo ""
echo "Great! Finally! All done!"


