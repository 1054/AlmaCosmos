#!/bin/bash
# 

# 
# Backup
# 
if [[ -f "Output_Prior_Simulation_Catalog.txt" ]]; then
    mv "Output_Prior_Simulation_Catalog.txt" "Output_Prior_Simulation_Catalog.txt.backup"
fi
if [[ -f "Output_Prior_Galfit_Gaussian_main_result.txt" ]]; then
    mv "Output_Prior_Galfit_Gaussian_main_result.txt" "Output_Prior_Galfit_Gaussian_main_result.txt.backup"
fi
if [[ -f "Output_Prior_Galfit_Gaussian_Condon_errors.txt" ]]; then
    mv "Output_Prior_Galfit_Gaussian_Condon_errors.txt" "Output_Prior_Galfit_Gaussian_Condon_errors.txt.backup"
fi



# 
# Read Recovered catalog
# 
IFS=$'\n' read -d '' -r -a FitsNames < "list_projects.txt"

for (( i=0; i<${#FitsNames[@]}; i++ )); do
    
    FitsName="${FitsNames[i]}"
    echo "${FitsNames[i]} ($((i+1))/${#FitsNames[@]})"
    
    # check non-COSMOS fields
    if [[ "$FitsName" == "2011.0.00539.S_"*"_ECDFS02_"* ]] || \
        [[ "$FitsName" == "2011.0.00539.S_"*"_ELS01_"* ]] || \
        [[ "$FitsName" == "2011.0.00539.S_"*"_ADFS01_"* ]] || \
        [[ "$FitsName" == "2011.0.00539.S_"*"_XMM01_"* ]] || \
        [[ "$FitsName" == "2011.0.00742.S_"*"__RX_J094144.51+385434.8__"* ]] || \
        [[ "$FitsName" == "2012.1.00596.S_"*"_PKS0215+015_"* ]] ; then
        echo "Warning! \"$FitsName\" is a non-COSMOS field! Skip and continue!"
        continue
    fi
    
    # check very high-res. images
    if [[ "$FitsName" == *"2015.1.00607.S_SB1_GB1_MB1_AzTEC-3_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB1_GB1_MB1_COSMOS_824759_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB2_GB1_MB1_COSMOS_823380_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB3_GB1_MB1_COSMOS_822872_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB3_GB1_MB1_COSMOS_822965_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB4_GB1_MB1_COSMOS_810344_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB4_GB1_MB1_COSMOS_839268_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00928.S_SB3_GB1_MB1_LBG-1_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.01345.S_SB1_GB1_MB1_AzTEC1_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.01345.S_SB1_GB1_MB1_AzTEC4_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.01345.S_SB2_GB1_MB1_AzTEC8_sci.spw0_1_2_3"* ]] ; then
        echo "Warning! \"$FitsName\" is a very high-res. image! Skip and continue!"
        continue
    fi
    
    # check simulation directory and datatable
    if [[ ! -f "Simulated/$FitsName/datatable_Simulated.txt" ]]; then
        echo "Error! \"Simulated/$FitsName/datatable_Simulated.txt\" was not found!"
        exit
    fi
    
    # check recovered directory
    if [[ ! -d "Recovered/$FitsName/" ]]; then
        echo "Error! \"Recovered/$FitsName/\" was not found!"
        exit
    fi
    
    # combine datatable_Simulated.txt
    if [[ ! -f "Output_Prior_Simulation_Catalog.txt" ]]; then
        head -n 1 "Simulated/$FitsName/datatable_Simulated.txt" | sed -e "s/$/      Image/g" >> "Output_Prior_Simulation_Catalog.txt"
    fi
    tail -n +2 "Simulated/$FitsName/datatable_Simulated.txt" | sed -e "s/$/      $FitsName/g" >> "Output_Prior_Simulation_Catalog.txt"
    
    # cd recovered directory
    cd "Recovered/$FitsName/"
    
    # find
    IFS=$'\n' ResultFiles=($(find . -name "fit_2.result.all.txt"))
    echo "${#ResultFiles[@]}"
    
    # loop
    for (( k=0; k<${#ResultFiles[@]}; k++ )); do
        TempRect=$(echo $(basename $(dirname "${ResultFiles[k]}")))
        TempSimu=$(echo $(dirname $(dirname $(dirname "${ResultFiles[k]}"))) | sed -e 's%^\./%%g')
        TempImage="$FitsName"
        #echo "$TempImage $TempSimu (main_result)"
        if [[ ! -f "../../Output_Prior_Galfit_Gaussian_main_result.txt" ]]; then
            head -n 1 "${ResultFiles[k]}" | sed -e "s/$/      Rect      Simu      Image/g" >> "../../Output_Prior_Galfit_Gaussian_main_result.txt"
        fi
        tail -n +3 "${ResultFiles[k]}" | sed -e "s/$/      $TempRect      $TempSimu      $TempImage/g" >> "../../Output_Prior_Galfit_Gaussian_main_result.txt"
    done
    
    # find
    IFS=$'\n' ResultFiles=($(find . -name "fit_2.result.source_err.txt"))
    echo "${#ResultFiles[@]}"
    
    # loop
    for (( k=0; k<${#ResultFiles[@]}; k++ )); do
        TempRect=$(echo $(basename $(dirname "${ResultFiles[k]}")))
        TempSimu=$(echo $(dirname $(dirname $(dirname "${ResultFiles[k]}"))) | sed -e 's%^\./%%g')
        TempImage="$FitsName"
        #echo "$TempImage $TempSimu (Condon_errors)"
        if [[ ! -f "../../Output_Prior_Galfit_Gaussian_Condon_errors.txt" ]]; then
            head -n 1 "${ResultFiles[k]}" | sed -e "s/$/      Rect      Simu      Image/g" >> "../../Output_Prior_Galfit_Gaussian_Condon_errors.txt"
        fi
        tail -n +3 "${ResultFiles[k]}" | sed -e "s/$/      $TempRect      $TempSimu      $TempImage/g" >> "../../Output_Prior_Galfit_Gaussian_Condon_errors.txt"
    done
    
    # cd back
    cd "../../"
    
done




































