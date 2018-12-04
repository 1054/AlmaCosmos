#!/bin/bash
# 


# Now we updated getpix code to report number of NaN pixels within aperture, and also excluded NaN pixels. Previously I was counting NaN pixels as zero-value pixels. 
# Now we also output "fit_2.result.flux_origin.txt"



source ~/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash
source ~/Cloud/Github/AlmaCosmos/Pipeline/SETUP.bash


# 
# Check software dependancies
# 
if [[ $(type sky2xy 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"sky2xy\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"; exit 1
fi
if [[ $(type galfit 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"galfit\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"; exit 1
fi
if [[ $(type astrodepth_prior_extraction_photometry 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"astrodepth_prior_extraction_photometry\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"; exit 1
fi
if [[ $(type a3cosmos-prior-extraction-photometry 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"a3cosmos-prior-extraction-photometry\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"; exit 1
fi


# 
# Set Input and Output
# 
InputCat="master_catalog_single_entry_with_Flag_Outlier_with_Photoz_v20170504a.fits"
InputSci="../ALMA_Calibrated_Images_by_Magnelli/v20180102_mod20180219/fits_file_list_sorted_excluded_very_high_res.txt"
OutputDir=$(echo "${BASH_SOURCE[0]}" | sed -e 's/\.sh//g' | sed -e 's%^./%%g')


# 
# Initialize
# 
if [[ ! -d "$OutputDir" ]]; then
    a3cosmos-prior-extraction-photometry \
        -start 0 -end 0 \
        -cat "$InputCat" \
        -sci "$InputSci" \
        -out "$OutputDir"
fi


# 
# Loop all sources
# 
istart=1
iend=125
istep=30
RunFolder=$(pwd)
for (( i=$istart; i<=$iend; i+=$istep )); do
    echo "Current computer \"$(hostname)\""
    echo "Current directory \"$RunFolder\""
    echo "Counting screen task "$(screen -ls | grep "caap_" | wc -l)
    while       [[   20  -le    $(screen -ls | grep "caap_" | wc -l) ]]; do
    sleep            24
    echo "Counting screen task "$(screen -ls | grep "caap_" | wc -l)
    done
    RunScreen="caap_$(date +%Y%m%d)_$(date +%s)_$i"
    echo "Adding screen task \"$RunScreen\" with command \"a3cosmos-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step getpix galfit gaussian sersic final negative -unlock image_check getpix galfit gaussian sersic negative final -overwrite negative final 2>&1 | tee log_$RunScreen.txt\""
    screen -d -S "$RunScreen" -m bash -c "cd $RunFolder; a3cosmos-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step getpix galfit gaussian sersic final negative -unlock image_check getpix galfit gaussian sersic negative final -overwrite negative final 2>&1 | tee log_$RunScreen.txt"
    echo "Current time "$(date +"%Y-%m-%d %H:%M:%S %Z")", sleeping for 5s"
    sleep 5
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"










