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
fi
# 
if [[ -f "Read_Results_all_final_detections_on_negative_image.txt.backup" ]]; then
    mv "Read_Results_all_final_detections_on_negative_image.txt.backup" "Read_Results_all_final_detections_on_negative_image.txt.backup.backup"
fi
if [[ -f "Read_Results_all_final_detections_on_negative_image.txt" ]]; then
    mv "Read_Results_all_final_detections_on_negative_image.txt" "Read_Results_all_final_detections_on_negative_image.txt.backup"
fi
# 
for fit_step in getpix fit_0 fit_1 fit_2 getpix_on_negative_image fit_n0 fit_n1 fit_n2; do
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
            head -n 1 "final.result" | xargs -d '\n' -I % echo "%    image_file" \
            > "$CurrentDir/Read_Results_all_final_detections.txt"
        fi
        cat "final.result" | tail -n +3 | head -n 1 | xargs -d '\n' -I % echo "%    $SourceName" \
        >> "$CurrentDir/Read_Results_all_final_detections.txt"
    fi
    
    if [[ -f "final_on_negative_image.result" ]]; then
        if [[ ! -f "$CurrentDir/Read_Results_all_final_detections_on_negative_image.txt" ]]; then
            head -n 1 "final_on_negative_image.result" | xargs -d '\n' -I % echo "%    image_file" \
            > "$CurrentDir/Read_Results_all_final_detections_on_negative_image.txt"
        fi
        cat "final_on_negative_image.result" | tail -n +3 | head -n 1 | xargs -d '\n' -I % echo "%    $SourceName" \
        >> "$CurrentDir/Read_Results_all_final_detections_on_negative_image.txt"
    fi
    
    for fit_step in getpix getpix_on_negative_image; do
        if [[ -f "${fit_step}.result" ]]; then
            if [[ ! -f "$CurrentDir/Read_Results_all_final_detections_${fit_step}.txt" ]]; then
                head -n 1 "${fit_step}.result" | xargs -d '\n' -I % echo "%    image_file" \
                > "$CurrentDir/Read_Results_all_final_detections_${fit_step}.txt"
            fi
            cat "${fit_step}.result" | tail -n +3 | xargs -d '\n' -I % echo "%    $SourceName" \
            >> "$CurrentDir/Read_Results_all_final_detections_${fit_step}.txt"
        fi
    done
    
    for fit_step in fit_0 fit_1 fit_2 fit_n0 fit_n1 fit_n2; do
        if [[ -f "${fit_step}.result.ra.dec.detect.id" ]]; then
            if [[ ! -f "$CurrentDir/Read_Results_all_final_detections_${fit_step}.txt" ]]; then
                head -n 1 "${fit_step}.result.ra.dec.detect.id" | xargs -d '\n' -I % echo "%    image_file" \
                > "$CurrentDir/Read_Results_all_final_detections_${fit_step}.txt"
            fi
            cat "${fit_step}.result.ra.dec.detect.id" | tail -n +3 | xargs -d '\n' -I % echo "%    $SourceName" \
            >> "$CurrentDir/Read_Results_all_final_detections_${fit_step}.txt"
        fi
    done
    
    for fit_step in getpix fit_0 fit_1 fit_2 getpix_on_negative_image fit_n0 fit_n1 fit_n2; do
        if [[ -f "${fit_step}.result.ra.dec.f.df.snr.id" ]]; then
            if [[ ! -f "$CurrentDir/Read_Results_all_final_fluxes_${fit_step}.txt" ]]; then
                head -n 1 "${fit_step}.result.ra.dec.f.df.snr.id" | xargs -d '\n' -I % echo "%    image_file" \
                > "$CurrentDir/Read_Results_all_final_fluxes_${fit_step}.txt"
            fi
            cat "${fit_step}.result.ra.dec.f.df.snr.id" | tail -n +3 | xargs -d '\n' -I % echo "%    $SourceName" \
            >> "$CurrentDir/Read_Results_all_final_fluxes_${fit_step}.txt"
        fi
    done
    
    
    cd "$CurrentDir"
    #break
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"

