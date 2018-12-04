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
#istart=1
#iend=17428
#istep=200
#istart=2601 # 1, updated Scoville method for getpix, need to overwite getpix
#iend=2800
#istart=3001 # fixed getpix read x_pix y_pix bug, added f_resabs in final result data tables
#iend=17428
#istart=2401 # 1 # update print_result_final, always print morph even if psf fitting
#iend=17428
#istep=200
#istart=2158 # 2013.1.00118.S_SB1_GB1_MB1_AzTECC100_sci.spw0_1_2_3.cont.I.image print_result_final was not updated?
#iend=2158
#istep=1
#istart=2500 # 2015.1.00137.S_SB2_GB1_MB1_z35_26_sci.spw0_1_2_3.cont.I.image print_result_final was not updated?
#iend=2500
#istep=1
#istart=2073 # 2013.1.00118.S_SB1_GB1_MB1_AzTECC15_sci.spw0_1_2_3.cont.I.image -- getpix.result pix_scale problem
#iend=2073
#istep=1
#istart=900 # 2011.0.00097.S_SB1_GB1_MB8_COSMOS4_field8_sci.spw0_1_2_3.cont.I.image.cut_-20_662_361_1043 -- no "fit_3.result"?? -- because of bad "fit_2.result", delete it and re-run this code
#iend=900
#istep=1
#istart=1997 # 2013.1.00034.S_SB3_GB1_MB1_highz_cell9_61357_sci.spw0_1_2_3.cont.I.image.cut_-20_-20_500_500 -- no "fit_3.result"?? -- because of bad "fit_2.result", delete it and re-run this code
#iend=1997
#istep=1
#istart=801 # 2011.0.00097.S_SB1_GB1_MB7_COSMOS3_field5_sci.spw0_1_2_3.cont.I.image.cut_-20_662_361_1043 -- no "fit_n2.result"?? -- strange, delete "fit_n*" and re-run this code
#iend=801
#istep=1
#istart=2378 # 2013.1.01258.S_SB2_GB1_MB1_aztec3_5_sci.spw0_1_2_3.cont.I.image.cut_330_680_720_1070 -- no "fit_n3.result.ra.dec.Maj.Min.*" -- because of "No_catalog_source_with_enough_getpix_SNR" -- now fixed this problem in "go_galfit.sm", re-run this code
#iend=2378
#istep=1
#istart=17213 # 2015.1.01345.S_SB2_GB1_MB1_AzTEC8_sci.spw0_1_2_3.cont.I.image.cut_6972_9404_7316_9748 -- no "fit_n3.result.ra.dec.Maj.Min.*" -- because of "No_catalog_source_with_enough_getpix_SNR" -- now fixed this problem in "go_galfit.sm", re-run this code
#iend=17213
#istep=1
#istart=17213
#iend=17213
#istep=1
istart=1
iend=17428
istep=300
if [[ $(uname) == "Darwin" ]]; then
    RunFolder=$(pwd)
else
    RunFolder=$(pwd -P)
fi
for (( i=$istart; i<=$iend; i+=$istep )); do
    echo "Current computer \"$(hostname)\""
    echo "Current directory \"$RunFolder\""
    echo "Counting screen task "$(screen -ls | grep "caap_" | wc -l)
    while       [[   16  -le    $(screen -ls | grep "caap_" | wc -l) ]]; do
    sleep            24
    echo "Counting screen task "$(screen -ls | grep "caap_" | wc -l)
    done
    RunScreen="caap_$(date +%s)_$i"
    ###echo "Adding screen task \"$RunScreen\" with command \"caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic -unlock image_check galfit gaussian sersic final -overwrite image_check galfit gaussian sersic final | tee log_$RunScreen.txt\""
    ###screen -d -S "$RunScreen" -m bash -c "cd $RunFolder; caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic -unlock image_check galfit gaussian sersic final -overwrite image_check galfit gaussian sersic final | tee log_$RunScreen.txt"
    ##echo "Adding screen task \"$RunScreen\" with command \"caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic negative final -unlock image_check getpix galfit gaussian sersic negative final -overwrite getpix final 2>&1 | tee log_$RunScreen.txt\""
    ##screen -d -S "$RunScreen" -m bash -c "cd $RunFolder; caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic negative final -unlock image_check getpix galfit gaussian sersic negative final -overwrite getpix final 2>&1 | tee log_$RunScreen.txt"
    ##echo "Adding screen task \"$RunScreen\" with command \"caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic negative final -unlock image_check getpix galfit gaussian sersic negative final -overwrite final 2>&1 | tee log_$RunScreen.txt\""
    ##screen -d -S "$RunScreen" -m bash -c "cd $RunFolder; caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic negative final -unlock image_check getpix galfit gaussian sersic negative final -overwrite final 2>&1 | tee log_$RunScreen.txt"
    echo "Adding screen task \"$RunScreen\" with command \"caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic galfit negative final -unlock image_check getpix galfit gaussian sersic negative final -overwrite final fit_2.result fit_3.result fit_n2.result fit_n3.result 2>&1 | tee log_$RunScreen.txt\""
    screen -d -S "$RunScreen" -m bash -c "cd $RunFolder; caap-prior-extraction-photometry -start $i -end $(($i+$istep-1)) -out \"$OutputDir\" -step sersic galfit negative final -unlock image_check getpix galfit gaussian sersic negative final -overwrite final fit_2.result fit_3.result fit_n2.result fit_n3.result 2>&1 | tee log_$RunScreen.txt"
    echo "Current time "$(date +"%Y-%m-%d %H:%M:%S %Z")", sleeping for 5s"
    sleep 5
done



echo ""
echo ""
echo ""
echo "Great! Finally! All done!"










