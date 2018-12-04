#!/bin/bash
# 



# 
# Set Input dir
# 
InputDir="Prior_Extraction_with_Master_Catalog_v20170606" #<TODO>#


# 
# Set Output dir
# 
OutputDir="Read_Residual_Images_of_Prior_Extraction_with_Master_Catalog_v20170609" #<TODO>#

# 
# Check input dir
# 
if [[ ! -d "$InputDir" ]]; then
    echo "Error! The output directory \"$InputDir\" does not exist! Abort!"; exit 1
else
    InputDir=$(readlink -f "$InputDir") #<TODO># only works for Linux
fi

# 
# Check output dir
# 
if [[ ! -d "$OutputDir" ]]; then
    mkdir "$OutputDir"
fi

# 
# Read Sci Images
# 
Old_IFS=$IFS
IFS=$'\n' SciImages=($(<"$InputDir/List_of_Input_Sci_Images.txt"))
IFS=$'\n' PsfImages=($(<"$InputDir/List_of_Input_Psf_Images.txt"))
IFS="$Old_IFS"
if [[ ${#SciImages[@]} -eq 0 || ${#PsfImages[@]} -eq 0 ]]; then
    echo "Error! Failed to read \"$InputDir/List_of_Input_Sci_Images.txt\" and \"$InputDir/List_of_Input_Psf_Images.txt\"!"
    exit 1
fi

# 
# Change dir to OutputDir
# 
cd "$OutputDir"



# 
# Loop and read the results of "getpix"
# 
for (( i=0; i<${#SciImages[@]}; i++ )); do
    # 
    SciImage="${SciImages[i]}"
    PsfImage="${PsfImages[i]}"
    SourceName=$(basename "$SciImage" | sed -e 's%\.fits%%g')   #<TODO># file name
    SciImageName=$(basename "$SciImage" | perl -p -e 's%\.fits%%g')   #<TODO># file name
    SciImageCutRect=($(echo "$SciImage" | perl -p -e 's%.*\.cut_(.*)_(.*)_(.*)_(.*)\.fits$%\1 \2 \3 \4%g'))
    SciImageUncutPath=$(echo "$SciImage" | perl -p -e 's%\.cut_.*_.*_.*_.*\.fits$%.fits%g')
    SciImageUncutName=$(basename "$SciImageUncutPath" | perl -p -e 's%\.fits%%g')
    
    # print
    #echo ""
    #echo ""
    #echo "************"
    #echo "SourceName = $SourceName   ($(($i+1))/${#SciImages[@]})   ($(date +'%Y%m%d %Hh%Mm%Ss %Z'))"
    #echo "SciImage = \"$SciImage\""
    #echo "PsfImage = \"$PsfImage\""
    #echo "InputDir = \"$(readlink -f $InputDir)/astrodepth_prior_extraction_photometry/$SourceName\""
    #echo "***********"
    
    CurrentDir=$(pwd -P) #<TODO># only works for Linux
    
    if [[ ! -f "$SciImageUncutName.residual.fits" ]]; then
        cp "$SciImageUncutPath" "$SciImageUncutName.residual.fits"
    fi
    
    if [[ -f "$InputDir/astrodepth_prior_extraction_photometry/$SourceName/fit_2.fits" ]]; then
        #cp "$SciImage" "$SourceName.obs.fits"
        cp "$InputDir/astrodepth_prior_extraction_photometry/$SourceName/fit_2.fits" "$SourceName.fit_2.fits"
        if [[ ${#SciImageCutRect[@]} -eq 4 ]]; then
            cutrect=($(echo "${SciImageCutRect[@]}"))
            naxisA=($(gethead "$InputDir/astrodepth_prior_extraction_photometry/$SourceName/fit_2.fits" "NAXIS1" "NAXIS2"))
            naxisB=($(gethead "$SciImageUncutPath" "NAXIS1" "NAXIS2"))
            echo ${cutrect[@]}
            echo ${naxisA[@]}
            echo ${naxisB[@]}
            PAX1=1 # Position Image A Axis X of Coordinate 1,1
            PAY1=1 # Position Image A Axis Y of Coordinate 1,1
            PAX2=$(awk "BEGIN {print ${naxisA[0]};}")
            PAY2=$(awk "BEGIN {print ${naxisA[1]};}")
            PBX1=$(awk "BEGIN {print ${cutrect[0]}+1;}")
            PBY1=$(awk "BEGIN {print ${cutrect[1]}+1;}")
            PBX2=$(awk "BEGIN {print ${cutrect[2]}+1;}")
            PBY2=$(awk "BEGIN {print ${cutrect[3]}+1;}")
            if [[ $(awk "BEGIN {if(${cutrect[0]}<0) print 1; else print 0;}") -eq 1 ]]; then
                PBX1=$(awk "BEGIN {print $PBX1-(${cutrect[0]});}")
                PAX1=$(awk "BEGIN {print $PAX1-(${cutrect[0]});}")
            fi
            if [[ $(awk "BEGIN {if(${cutrect[1]}<0) print 1; else print 0;}") -eq 1 ]]; then
                PBY1=$(awk "BEGIN {print $PBY1-(${cutrect[1]});}")
                PAY1=$(awk "BEGIN {print $PAY1-(${cutrect[1]});}")
            fi
            if [[ $(awk "BEGIN {if(${cutrect[2]}>${naxisB[0]}-1) print 1; else print 0;}") -eq 1 ]]; then
                PBX2=$(awk "BEGIN {print $PBX2-(${cutrect[2]})+(${naxisB[0]}-1);}")
                PAX2=$(awk "BEGIN {print $PAX2-(${cutrect[2]})+(${naxisB[0]}-1);}")
            fi
            if [[ $(awk "BEGIN {if(${cutrect[3]}>${naxisB[1]}-1) print 1; else print 0;}") -eq 1 ]]; then
                PBY2=$(awk "BEGIN {print $PBY2-(${cutrect[3]})+(${naxisB[1]}-1);}")
                PAY2=$(awk "BEGIN {print $PAY2-(${cutrect[3]})+(${naxisB[1]}-1);}")
            fi
            #echo "images" > "$SciImageUncutName.residual.run.cl"
            ##echo "imcopy $SourceName.obs $SciImageUncutName.residual" >> "$SciImageUncutName.residual.run.cl"
            #echo "imcopy $SourceName.fit_2[3][$PAX1:$PAX2,$PAY1:$PAY2] $SciImageUncutName.residual[$PBX1:$PBX2,$PBY1:$PBY2]" >> "$SciImageUncutName.residual.run.cl"
            #echo "" >> "$SciImageUncutName.residual.run.cl"
            #echo "cl -old < \"$SciImageUncutName.residual.run.cl\""
            #echo "---"
            echo "!PATH = !PATH + '/usr/local2/misc/idl-8.5/idl85/astron/pro/fits/'" > "$SourceName.add.to.residual.run.pro"
            echo "resolve_routine, 'mrdfits', /either" >> "$SourceName.add.to.residual.run.pro"
            echo "resolve_routine, 'mrdfits', /either" >> "$SourceName.add.to.residual.run.pro"
            echo "imageA = mrdfits('$SourceName.fit_2.fits',3)" >> "$SourceName.add.to.residual.run.pro"
            echo "imageB = mrdfits('$SciImageUncutName.residual.fits',0,fitsHeader)" >> "$SourceName.add.to.residual.run.pro"
            echo "imageB[$PBX1-1:$PBX2-1,$PBY1-1:$PBY2-1] = imageA[$PAX1-1:$PAX2-1,$PAY1-1:$PAY2-1]" >> "$SourceName.add.to.residual.run.pro"
            echo "mwrfits, imageB, '$SciImageUncutName.residual.fits', fitsHeader, /Create" >> "$SourceName.add.to.residual.run.pro"
            echo ";END" >> "$SourceName.add.to.residual.run.pro"
            echo "idl < $SourceName.add.to.residual.run.pro"
            idl < "$SourceName.add.to.residual.run.pro" > "$SourceName.add.to.residual.run.log" 2>&1
            echo "---"
        else
            #echo "images" > "$SciImageUncutName.residual.run.cl"
            ##echo "imcopy $SourceName.obs $SciImageUncutName.residual" >> "$SciImageUncutName.residual.run.cl"
            #echo "imcopy $SourceName.fit_2[3] $SciImageUncutName.residual" >> "$SciImageUncutName.residual.run.cl"
            #echo "" >> "$SciImageUncutName.residual.run.cl"
            #echo "cl -old < \"$SciImageUncutName.residual.run.cl\""
            #echo "---"
            echo "!PATH = !PATH + '/usr/local2/misc/idl-8.5/idl85/astron/pro/fits/'" > "$SourceName.add.to.residual.run.pro"
            echo "resolve_routine, 'mrdfits', /either" >> "$SourceName.add.to.residual.run.pro"
            echo "resolve_routine, 'mrdfits', /either" >> "$SourceName.add.to.residual.run.pro"
            echo "imageA = mrdfits('$SourceName.fit_2.fits',3)" >> "$SourceName.add.to.residual.run.pro"
            echo "imageB = mrdfits('$SciImageUncutName.residual.fits',0,fitsHeader)" >> "$SourceName.add.to.residual.run.pro"
            echo "imageB = imageA" >> "$SourceName.add.to.residual.run.pro"
            echo "mwrfits, imageB, '$SciImageUncutName.residual.fits', fitsHeader, /Create" >> "$SourceName.add.to.residual.run.pro"
            echo ";END" >> "$SourceName.add.to.residual.run.pro"
            echo "idl < $SourceName.add.to.residual.run.pro"
            idl < "$SourceName.add.to.residual.run.pro" > "$SourceName.add.to.residual.run.log" 2>&1
            echo "---"
        fi
        #rm "$SourceName.obs.fits"
        rm "$SourceName.fit_2.fits"
    fi
    
    
    cd "$CurrentDir"
    
    
    #if [[ $i -gt 3 ]]; then break; fi
    
done


cd "../"


echo ""
echo ""
echo ""
echo "Great! Finally! All done!"


