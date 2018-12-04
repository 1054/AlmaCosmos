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
if [[ -f "Read_Results_all_getpix.txt.backup" ]]; then
    mv "Read_Results_all_getpix.txt.backup" "Read_Results_all_getpix.txt.backup.backup"
fi
if [[ -f "Read_Results_all_getpix.txt" ]]; then
    mv "Read_Results_all_getpix.txt" "Read_Results_all_getpix.txt.backup"
fi
printf "# %12s %12s %12s %12s %12s\n" "f_peak" "f_int" "snr_peak" "snr_int" "id" > "Read_Results_all_getpix.txt"
printf "# \n" >> "Read_Results_all_getpix.txt"

# 
# Loop and read the results of "getpix"
# 
for (( i=0; i<${#SciImages[@]}; i++ )); do
    # 
    SciImage="${SciImages[i]}"
    PsfImage="${PsfImages[i]}"
    SourceName=$(basename "$SciImage" | sed -e 's%\.fits%%g')   #<TODO># file name
    
    # print
    echo ""
    echo ""
    echo "************"
    echo "SourceName = $SourceName   ($(($i+1))/${#SciImages[@]})   ($(date +'%Y%m%d %Hh%Mm%Ss %Z'))"
    echo "SciImage = \"$SciImage\""
    echo "PsfImage = \"$PsfImage\""
    echo "OutputDir = \"$(readlink -f $OutputDir)/astrodepth_prior_extraction_photometry/$SourceName\""
    echo "***********"
    
    CurrentDir=$(pwd -P)
    cd "$OutputDir/astrodepth_prior_extraction_photometry/$SourceName/"
    
    if [[ -f "getpix.result" ]]; then
        echo "cat \"getpix.result\" | grep -v \"^#\" | grep -v \" 0 \" >> \"$CurrentDir/Read_Results_all_getpix.txt\""
        cat "getpix.result" | grep -v "^#" | grep -v " 0 " | sed -e "s%$%      \"$SourceName\"%g" >> "$CurrentDir/Read_Results_all_getpix.txt"
    else
        echo "Error! Failed to read \"getpix.result\" under current directory!"
        pwd
        #ls
        #sleep 2.0
    fi
    
    cd "$CurrentDir"
    #break
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"







