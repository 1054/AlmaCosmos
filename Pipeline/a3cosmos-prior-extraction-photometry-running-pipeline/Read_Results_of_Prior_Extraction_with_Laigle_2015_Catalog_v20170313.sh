#!/bin/bash
# 

# 
# Set Input Catalog
# 
InputCat="Catalog_Laigle_2016_ID_RA_Dec_Photo-z.fits"
if [[ ! -f "$InputCat" ]]; then
    echo "Error! The input catalog \"$InputCat\" does not exist!"; exit 1
fi
InputCat=$(readlink -f "$InputCat")

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
IFS=$'\n' SciImages=($(<"$OutputDir/List_of_Input_Sci_Images.txt"))
IFS=$'\n' PsfImages=($(<"$OutputDir/List_of_Input_Psf_Images.txt"))
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
fi

if [[ -f "Read_Results_all_final_fluxes_fit_0.txt.backup" ]]; then
    mv "Read_Results_all_final_fluxes_fit_0.txt.backup" "Read_Results_all_final_fluxes_fit_0.txt.backup.backup"
fi
if [[ -f "Read_Results_all_final_fluxes_fit_0.txt" ]]; then
    mv "Read_Results_all_final_fluxes_fit_0.txt" "Read_Results_all_final_fluxes_fit_0.txt.backup"
fi
fi

if [[ -f "Read_Results_all_final_fluxes_fit_1.txt.backup" ]]; then
    mv "Read_Results_all_final_fluxes_fit_1.txt.backup" "Read_Results_all_final_fluxes_fit_1.txt.backup.backup"
fi
if [[ -f "Read_Results_all_final_fluxes_fit_1.txt" ]]; then
    mv "Read_Results_all_final_fluxes_fit_1.txt" "Read_Results_all_final_fluxes_fit_1.txt.backup"
fi
fi

if [[ -f "Read_Results_all_final_fluxes_fit_2.txt.backup" ]]; then
    mv "Read_Results_all_final_fluxes_fit_2.txt.backup" "Read_Results_all_final_fluxes_fit_2.txt.backup.backup"
fi
if [[ -f "Read_Results_all_final_fluxes_fit_2.txt" ]]; then
    mv "Read_Results_all_final_fluxes_fit_2.txt" "Read_Results_all_final_fluxes_fit_2.txt.backup"
fi



# 
# Loop and read the results of "getpix"
# 
for (( i=0; i<${#SciImages[@]}; i++ )); do
    # 
    SciImage="${SciImages[i]}"
    PsfImage="${PsfImages[i]}"
    SourceName=$(basename "$SciImage" | sed -e 's%\.fits%%g')   #<TODO># file name
    
    # print
    #echo ""
    #echo ""
    #echo "************"
    #echo "SourceName = $SourceName   ($(($i+1))/${#SciImages[@]})   ($(date +'%Y%m%d %Hh%Mm%Ss %Z'))"
    #echo "SciImage = \"$SciImage\""
    #echo "PsfImage = \"$PsfImage\""
    #echo "OutputDir = \"$(readlink -f $OutputDir)/astrodepth_prior_extraction_photometry/$SourceName\""
    #echo "***********"
    
    CurrentDir=$(pwd -P)
    cd "$OutputDir/astrodepth_prior_extraction_photometry/$SourceName/"
    
    if [[ -f "final.result" ]]; then
        if [[ ! -f "$CurrentDir/Read_Results_all_final_detections.txt" ]]; then
            head -n 1 "final.result" | xargs -d '\n' -I % echo "%    image_file" > "$CurrentDir/Read_Results_all_final_detections.txt"
        fi
        cat "final.result" | tail -n +3 | head -n 1 | xargs -d '\n' -I % echo "%    $SourceName" >> "$CurrentDir/Read_Results_all_final_detections.txt"
    fi
    
    if [[ -f "fit_0.result.ra.dec.detect.id" ]]; then
        if [[ ! -f "$CurrentDir/Read_Results_all_final_fluxes_fit_0.txt" ]]; then
            head -n 1 "fit_0.result.ra.dec.detect.id" | xargs -d '\n' -I % echo "%    image_file" > "$CurrentDir/Read_Results_all_final_fluxes_fit_0.txt"
        fi
        cat "fit_0.result.ra.dec.detect.id" | tail -n +3 | head -n 1 | xargs -d '\n' -I % echo "%    $SourceName" >> "$CurrentDir/Read_Results_all_final_fluxes_fit_0.txt"
    fi
    
    if [[ -f "fit_1.result.ra.dec.detect.id" ]]; then
        if [[ ! -f "$CurrentDir/Read_Results_all_final_fluxes_fit_1.txt" ]]; then
            head -n 1 "fit_1.result.ra.dec.detect.id" | xargs -d '\n' -I % echo "%    image_file" > "$CurrentDir/Read_Results_all_final_fluxes_fit_1.txt"
        fi
        cat "fit_1.result.ra.dec.detect.id" | tail -n +3 | head -n 1 | xargs -d '\n' -I % echo "%    $SourceName" >> "$CurrentDir/Read_Results_all_final_fluxes_fit_1.txt"
    fi
    
    if [[ -f "fit_2.result.ra.dec.detect.id" ]]; then
        if [[ ! -f "$CurrentDir/Read_Results_all_final_fluxes_fit_2.txt" ]]; then
            head -n 1 "fit_2.result.ra.dec.detect.id" | xargs -d '\n' -I % echo "%    image_file" > "$CurrentDir/Read_Results_all_final_fluxes_fit_2.txt"
        fi
        cat "fit_2.result.ra.dec.detect.id" | tail -n +3 | head -n 1 | xargs -d '\n' -I % echo "%    $SourceName" >> "$CurrentDir/Read_Results_all_final_fluxes_fit_2.txt"
    fi
    
    cd "$CurrentDir"
    #break
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"







