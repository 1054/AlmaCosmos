#!/bin/bash
# 

source ~/Cloud/Github/Crab.Toolkit.CAAP/SETUP.bash
source ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP


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
if [[ $(type caap-prior-extraction-photometry 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! \"caap-prior-extraction-photometry\" is not in the \$PATH! Please add its path to the \$PATH then re-run this code!"; exit 1
fi


# 
# Set Input and Output
# 
InputCat="master_catalog_single_entry_with_Flag_Outlier_with_Photoz_v20170504a.fits"
InputSci="../ALMA_Calibrated_Images_by_Magnelli/v20170604/fits_file_list_sorted_v20170724.txt"
OutputDir=$(echo "${BASH_SOURCE[0]}" | sed -e 's/\.sh//g' | sed -e 's%^./%%g')


# 
# Initialize
# 
if [[ ! -d "$OutputDir" ]]; then
    caap-prior-extraction-photometry \
        -start 0 -end 0 \
        -cat "$InputCat" \
        -sci "$InputSci" \
        -out "$OutputDir"
fi


# 
# Loop all sources
# 
#istart=1
#iend=20
#istep=10 # 300
istart=21
iend=17428
istep=200
if [[ $(uname) == "Darwin" ]]; then
    RunFolder=$(pwd)
else
    RunFolder=$(pwd -P)
fi
for (( i=$istart; i<=$iend; i+=$istep )); do
    echo "Current computer \"$(hostname)\""
    echo "Current directory \"$RunFolder\""
    echo "Counting screen task "$(screen -ls | grep "caap_" | wc -l)
    while       [[   12  -le    $(screen -ls | grep "caap_" | wc -l) ]]; do
    sleep            24
    echo "Counting screen task "$(screen -ls | grep "caap_" | wc -l)
    done
    RunScreen="caap_$(date +%s)_$i"
    echo "Adding screen task \"$RunScreen\" with command \"caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" | tee log_$RunScreen.txt\""
    screen -d -S "$RunScreen" -m bash -c "cd $RunFolder; caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" | tee log_$RunScreen.txt"
    echo "Current time "$(date +"%Y-%m-%d %H:%M:%S %Z")", sleeping for 5s"
    sleep 5
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"










