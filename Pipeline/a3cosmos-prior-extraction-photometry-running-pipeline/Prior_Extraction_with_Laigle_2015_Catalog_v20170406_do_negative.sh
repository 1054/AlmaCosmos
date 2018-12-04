#!/bin/bash
# 

# 
# readlink for Mac (because Mac readlink does not accept "-f" option)
# 
#if [[ $(uname) == *"Darwin"* ]]; then
#    function readlink() {
#        if [[ $# -gt 1 ]]; then if [[ "$1" == "-f" ]]; then shift; fi; fi
#        DIR="$1"; if [[ "$DIR" != *"/"* ]]; then DIR="./$DIR"; fi # 20170228: fixed bug: path without "/"
#        DIR=$(echo "${DIR%/*}") # 20160410: fixed bug: source SETUP just under the Softwares dir
#        if [[ -d "$DIR" ]]; then cd "$DIR" && echo "$(pwd -P)/$(basename ${1})"; 
#        else echo "$(pwd -P)/$(basename ${1})"; fi
#    }
#fi

source ~/Cloud/Github/Crab.Toolkit.CAAP/SETUP.bash
source ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP


# 
# Check software dependancies
# 
if [[ $(type sky2xy 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"sky2xy\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"
fi
if [[ $(type galfit 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"galfit\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"
fi
if [[ $(type astrodepth_prior_extraction_photometry 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"astrodepth_prior_extraction_photometry\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"
fi


# 
# Read user input
# 
UserFitStart=""
UserFitEnd=""
if [[ "$*" == *"-start "* ]]; then UserFitStart=$(echo "$*" | perl -p -e 's/.*-start *([0-9]*).*/\1/g'); fi
if [[ "$*" == *"-end "* ]]; then UserFitEnd=$(echo "$*" | perl -p -e 's/.*-end *([0-9]*).*/\1/g'); fi
echo "UserFitStart = $UserFitStart"
echo "UserFitEnd = $UserFitEnd"
#exit

UserOverwrite=""
if [[ "$*" == *"-overwrite "* ]]; then UserOverwrite=($(echo "$*" | perl -p -e 's/.*-overwrite *([^-]*).*/-overwrite \1/g')); fi
echo "UserOverwrite = ${UserOverwrite[@]}"


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
    mkdir "$OutputDir"
fi
if [[ ! -d "$OutputDir" ]]; then
    echo "Error! Failed to create output directory \"$OutputDir\"! Abort!"; exit 1
fi

# 
# Find input sci and psf fits files and output to OutputDir/List_of_Input_Images.txt
# Cut sci fits image to about 480 pixel size
# 
DoOverwrite=0
if [[ $DoOverwrite -eq 1 ]]; then
    mv "$OutputDir/List_of_Input_Sci_Images.txt" "$OutputDir/List_of_Input_Sci_Images.txt.backup" 2>/dev/null
    mv "$OutputDir/List_of_Input_Psf_Images.txt" "$OutputDir/List_of_Input_Psf_Images.txt.backup" 2>/dev/null
fi
if [[ ! -f "$OutputDir/List_of_Input_Sci_Images.txt" ]]; then
    SciImages=($(ls -1 ../ALMA_Calibrated_Images_by_Magnelli/v20170222/fits/*.cont.I.image.fits))   #<TODO># file name
    PsfImages=($(ls -1 ../ALMA_Calibrated_Images_by_Magnelli/v20170222/fits/*.cont.I.psf.fits))     #<TODO># file name
    if [[ ${#SciImages[@]} -eq 0 ]]; then
        echo "Error! No fits file found! Please check \"SciImages\" in the code!"; exit 1
    fi
    if [[ ${#PsfImages[@]} -eq 0 ]]; then
        echo "Error! No fits file found! Please check \"PsfImages\" in the code!"; exit 1
    fi
    echo "Checking input SciImages and PsfImages ..."
    for (( i=0; i<${#SciImages[@]}; i++ )); do
        # 
        # 
        # print progress
        if [[ $(awk "BEGIN {print (($i)%(${#SciImages[@]}/10))}") -eq 0 ]]; then
            echo -n $(awk "BEGIN {print (100.0*($i)/(${#SciImages[@]}))}")"% "
        elif [[ $(($i+1)) -eq ${#SciImages[@]} ]]; then
            echo "100%"
        fi
        # 
        # 
        # check SciImage and PsfImage name, make sure they are consistent
        SciImage="${SciImages[i]}"
        PsfImage="${PsfImages[i]}"
        SciImage_check=$(echo "$SciImage" | sed -e 's%.cont.I.image.fits%%g')   #<TODO># file name
        PsfImage_check=$(echo "$PsfImage" | sed -e 's%.cont.I.psf.fits%%g')     #<TODO># file name
        if [[ "$SciImage_check" != "$PsfImage_check" ]]; then 
            echo ""; echo "Error! The input SciImage \"${SciImages[i]}\" and PsfImage \"${PsfImages[i]}\" do not match!"; exit 1
        fi
        # 
        # 
        # check PsfImage dimension, make sure they have a size of about 120 pixel
        PsfImage_fullpath=$(readlink -f "$PsfImage")
        CutRect_fullpath=$(echo "$PsfImage_fullpath" | sed -e "s/\.fits$/.cut.rect.txt/g")
        PsfNAXIS1=$(gethead $PsfImage NAXIS1)
        PsfNAXIS2=$(gethead $PsfImage NAXIS2)
        if [[ ! -f "$CutRect_fullpath" ]]; then
            # cut psf image, make sure the sum is positive
            CutBuffer=60 # CutBuffer=150
            while [[ $CutBuffer -ge 20 ]]; do
                CutBuffer=$(($CutBuffer-2)) # $(awk "BEGIN {print ($CutBuffer - 5)}")
                CutPos1X=$(awk "BEGIN {print int(($PsfNAXIS1-1.0)/2.0)-($CutBuffer)+1}") #<TODO># +1 accounts for the small shift of the ALMA psf fits image produced by Benjamin
                CutPos1Y=$(awk "BEGIN {print int(($PsfNAXIS2-1.0)/2.0)-($CutBuffer)+1}") #<TODO># +1 accounts for the small shift of the ALMA psf fits image produced by Benjamin
                CutPos2X=$(awk "BEGIN {print int(($PsfNAXIS1-1.0)/2.0)+($CutBuffer)+1}") #<TODO># +1 accounts for the small shift of the ALMA psf fits image produced by Benjamin
                CutPos2Y=$(awk "BEGIN {print int(($PsfNAXIS2-1.0)/2.0)+($CutBuffer)+1}") #<TODO># +1 accounts for the small shift of the ALMA psf fits image produced by Benjamin
                CutImage_fullpath=$(echo "$PsfImage_fullpath" | sed -e "s/\.fits$/.cut_${CutPos1X}_${CutPos1Y}_${CutPos2X}_${CutPos2Y}.fits/g")
                CutScript_fullpath=$(echo "$PsfImage_fullpath" | sed -e "s/\.fits$/.cut_${CutPos1X}_${CutPos1Y}_${CutPos2X}_${CutPos2Y}.sh/g")
                CutScriptLog_fullpath=$(echo "$PsfImage_fullpath" | sed -e "s/\.fits$/.cut_${CutPos1X}_${CutPos1Y}_${CutPos2X}_${CutPos2Y}.sh.log/g")
                echo "#!/bin/bash" > "$CutScript_fullpath"
                echo "CrabFitsImageCrop \"$PsfImage_fullpath\" -rect $CutPos1X $CutPos1Y $CutPos2X $CutPos2Y -out \"$CutImage_fullpath\"" >> "$CutScript_fullpath"
                echo "$CutPos1X $CutPos1Y $CutPos2X $CutPos2Y" > "$CutRect_fullpath"
                chmod +x "$CutScript_fullpath"
                "$CutScript_fullpath" > "$CutScriptLog_fullpath"
                if [[ ! -f "$CutImage_fullpath" ]]; then
                    echo ""; echo "Error! Failed to run \"$CutScript_fullpath\" and create \"$CutImage_fullpath\"!"
                    echo ""; cat "$CutScriptLog_fullpath"
                    exit 1
                fi
                CutImage_sumpix=$(sumpix "$CutImage_fullpath")
                if [[ "$CutImage_sumpix" != "-"* ]]; then
                    PsfImage_fullpath="$CutImage_fullpath"
                    break
                else
                    rm "$CutScriptLog_fullpath"
                    rm "$CutScript_fullpath"
                    rm "$CutImage_fullpath"
                    rm "$CutRect_fullpath"
                fi
            done
        else
            CutRect=($(cat "$CutRect_fullpath"))
            PsfImage_fullpath=$(echo "$PsfImage_fullpath" | sed -e "s/\.fits$/.cut_${CutRect[0]}_${CutRect[1]}_${CutRect[2]}_${CutRect[3]}.fits/g")
            if [[ ! -f "$PsfImage_fullpath" ]]; then 
                echo ""; echo "Error! Failed to find the cut PSF image \"$PsfImage_fullpath\"!"
                exit 1
            fi
        fi
        # check PsfImage sumpix
        PsfImage_sumpix=$(sumpix "$PsfImage_fullpath")
        if [[ "$PsfImage_sumpix" == "-"* ]]; then
            echo ""; echo "Error! The PSF image \"$PsfImage_fullpath\" has a negative total pixel value!"
            exit 1
        fi
        # 
        # 
        # check SciImage dimension, make sure they have a size of about 300 pixel. 
        SciImage_fullpath=$(readlink -f "$SciImage")
        CutRect_fullpath=$(echo "$SciImage_fullpath" | sed -e "s/\.fits$/.cut.rect.txt/g")
        SciNAXIS1=$(gethead $SciImage NAXIS1)
        SciNAXIS2=$(gethead $SciImage NAXIS2)
        if [[ $(awk "BEGIN {if($SciNAXIS1>450) print 1; else print 0;}") -eq 1 ]]; then
            if [[ ! -f "$CutRect_fullpath" ]]; then
                CutNumbX=$(awk "BEGIN {print int(($SciNAXIS1)/300/2.0)*2+1}") # ~3
                CutNumbY=$(awk "BEGIN {print int(($SciNAXIS2)/300/2.0)*2+1}") # ~3
                CutSizeX=$(awk "BEGIN {print int(($SciNAXIS1)/$CutNumbX)}") # ~301
                CutSizeY=$(awk "BEGIN {print int(($SciNAXIS2)/$CutNumbY)}") # ~301
                CutBuffer=20
                for (( icut_y=0; icut_y<$CutNumbY; icut_y++ )); do
                    for (( icut_x=0; icut_x<$CutNumbX; icut_x++ )); do
                        # cut sci image
                        CutPos1X=$(awk "BEGIN {print ($CutSizeX)*($icut_x)-($CutBuffer)}")
                        CutPos1Y=$(awk "BEGIN {print ($CutSizeY)*($icut_y)-($CutBuffer)}")
                        CutPos2X=$(awk "BEGIN {print ($CutSizeX)*($icut_x+1)+($CutBuffer)}")
                        CutPos2Y=$(awk "BEGIN {print ($CutSizeY)*($icut_y+1)+($CutBuffer)}")
                        CutImage_fullpath=$(echo "$SciImage_fullpath" | sed -e "s/\.fits$/.cut_${CutPos1X}_${CutPos1Y}_${CutPos2X}_${CutPos2Y}.fits/g")
                        CutScript_fullpath=$(echo "$SciImage_fullpath" | sed -e "s/\.fits$/.cut_${CutPos1X}_${CutPos1Y}_${CutPos2X}_${CutPos2Y}.sh/g")
                        CutScriptLog_fullpath=$(echo "$SciImage_fullpath" | sed -e "s/\.fits$/.cut_${CutPos1X}_${CutPos1Y}_${CutPos2X}_${CutPos2Y}.sh.log/g")
                        echo "#!/bin/bash" > "$CutScript_fullpath"
                        echo "CrabFitsImageCrop \"$SciImage_fullpath\" -rect $CutPos1X $CutPos1Y $CutPos2X $CutPos2Y -out \"$CutImage_fullpath\"" >> "$CutScript_fullpath"
                        echo "$CutPos1X $CutPos1Y $CutPos2X $CutPos2Y" >> "$CutRect_fullpath"
                        chmod +x "$CutScript_fullpath"
                        "$CutScript_fullpath" > "$CutScriptLog_fullpath"
                        if [[ ! -f "$CutImage_fullpath" ]]; then
                            echo ""; echo "Error! Failed to run \"$CutScript_fullpath\" and create \"$CutImage_fullpath\"!"
                            echo ""; cat "$CutScriptLog_fullpath"
                            exit 1
                        fi
                        echo "$CutImage_fullpath" >> "$OutputDir/List_of_Input_Sci_Images.txt"
                        echo "$PsfImage_fullpath" >> "$OutputDir/List_of_Input_Psf_Images.txt"
                    done
                done
            else
                IFS=$'\n' CutRect_list=($(<"$CutRect_fullpath"))
                for (( icut=0; icut<${#CutRect_list}; icut++ )); do
                    CutRect=(${CutRect_list[icut]})
                    CutImage_fullpath=$(echo "$SciImage_fullpath" | sed -e "s/\.fits$/.cut_${CutRect[0]}_${CutRect[1]}_${CutRect[2]}_${CutRect[3]}.fits/g")
                    if [[ ! -f "$CutImage_fullpath" ]]; then 
                        echo ""; echo "Error! Failed to find the cut SCI image \"$CutImage_fullpath\"!"
                        exit 1
                    fi
                    echo "$CutImage_fullpath" >> "$OutputDir/List_of_Input_Sci_Images.txt"
                    echo "$PsfImage_fullpath" >> "$OutputDir/List_of_Input_Psf_Images.txt"
                done
            fi
            #break
        else
            echo "$SciImage_fullpath" >> "$OutputDir/List_of_Input_Sci_Images.txt"
            echo "$PsfImage_fullpath" >> "$OutputDir/List_of_Input_Psf_Images.txt"
        fi
        # 
        #SciImages[i]=$(readlink -f "$SciImage")
        #PsfImages[i]=$(readlink -f "$PsfImage")
    done
fi
IFS=$'\n' SciImages=($(<"$OutputDir/List_of_Input_Sci_Images.txt"))
IFS=$'\n' PsfImages=($(<"$OutputDir/List_of_Input_Psf_Images.txt"))
if [[ ${#SciImages[@]} -eq 0 || ${#PsfImages[@]} -eq 0 ]]; then
    echo "Error! Failed to read \"$OutputDir/List_of_Input_Sci_Images.txt\" and \"$OutputDir/List_of_Input_Psf_Images.txt\"!"
    exit 1
fi
#echo ${SciImages[0]}
#echo ${PsfImages[0]}
#exit

















# 
# fit ALMA calibrated images
# 

echo "Running astrodepth_prior_extraction_photometry ..."
#astrodepth_prior_extraction_photometry -cat "$InputCat" -sci "${SciImages[0]}" -psf "${PsfImages[0]}"
#astrodepth_prior_extraction_photometry -cat "$InputCat" -sci "${SciImages[@]}" -psf "${PsfImages[@]}"

for (( i=0; i<${#SciImages[@]}; i++ )); do
    # 
    # if [[ $i -lt 1086 ]]; then continue; fi
    # if [[ $i -lt 280 ]]; then continue; fi
    # if [[ $i -lt 432 ]]; then continue; fi
    # if [[ $i -lt 128 ]]; then continue; fi
    # if [[ $i -lt 8348 ]]; then continue; fi
    # if [[ $i -lt 9841 ]]; then continue; fi
    #if [[ $i -lt 1152 ]]; then continue; fi
    if [[ x"$UserFitStart" != x ]]; then
        if [[ $(($i+1)) -lt $UserFitStart ]]; then 
            continue
        fi
    fi
    if [[ x"$UserFitEnd" != x ]]; then
        if [[ $(($i+1)) -gt $UserFitEnd ]]; then 
            continue
        fi
    fi
    # 
    SciImage="${SciImages[i]}"
    PsfImage="${PsfImages[i]}"
    SourceName=$(basename "$SciImage" | sed -e 's%\.fits%%g')   #<TODO># file name
    
    
    CurrentDir=$(pwd -P)
    cd "$OutputDir/"
    
    #<fixed><20170305># use clean beam PSF
    PsfImage=$(echo "$PsfImage" | sed -e 's/\.psf.*\.fits/.clean-beam.fits/g')
    if [[ ! -f "$PsfImage" ]]; then
        echo "caap-generate-PSF-Gaussian-2D \"$SciImage\" \"$PsfImage\""
        caap-generate-PSF-Gaussian-2D "$SciImage" "$PsfImage"
    fi
    
    # print
    echo ""
    echo ""
    echo "************"
    echo "SourceName = $SourceName   ($(($i+1))/${#SciImages[@]})   ($(date +'%Y%m%d %Hh%Mm%Ss %Z'))"
    echo "SciImage = \"$(readlink -f $SciImage)\""
    echo "PsfImage = \"$(readlink -f $PsfImage)\""
    echo "OutputDir = \"$(pwd -P)/astrodepth_prior_extraction_photometry/$SourceName\""
    echo "***********"
    echo "Running astrodepth_prior_extraction_photometry"
    #echo "astrodepth_prior_extraction_photometry -cat \"$InputCat\" -sci \"$SciImage\" -psf \"$PsfImage\""
    #      astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "getpix"  -overwrite "go_getpix" "getpix"
    #      astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "galfit"  -overwrite "galfit"
    #      astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "getpix" "galfit" "gaussian" "negative"
    #      astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "gaussian"  -overwrite "gaussian"
    #      astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "getpix" "galfit" "gaussian"  -overwrite "galfit" "gaussian"
    #      astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "getpix" "galfit" "gaussian"  -overwrite "image_check" "galfit" "gaussian"
           #astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "galfit" "gaussian" "final"  -unlock "getpix" "galfit" "gaussian" "final"  -overwrite "galfit" "gaussian" "final" ${UserOverwrite[@]}
           astrodepth_prior_extraction_photometry -cat  "$InputCat"  -sci  "$SciImage"  -psf  "$PsfImage"  -output-name "$SourceName"  -steps "negative"  -unlock "negative"  -overwrite "negative" ${UserOverwrite[@]}
    #mv "astrodepth_prior_extraction_photometry/astrodepth_image_0_galfit" "astrodepth_prior_extraction_photometry/$SourceName" # -steps "getpix" # "galfit" "gaussian"
    rm "astrodepth_prior_extraction_photometry/astrodepth_image_0_catalog_0_sky2xy.txt" 2>/dev/null
    rm "astrodepth_prior_extraction_photometry/astrodepth_image_0_catalog_0_x_y.txt"    2>/dev/null
    cd "$CurrentDir"
    #break
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"










