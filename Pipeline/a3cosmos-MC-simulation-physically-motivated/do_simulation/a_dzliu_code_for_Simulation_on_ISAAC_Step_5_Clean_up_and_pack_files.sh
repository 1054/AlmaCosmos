#!/bin/bash
# 


# 
# Read Recovered catalog
# 
IFS=$'\n' read -d '' -r -a FitsNames < "list_projects.txt"

for (( i=0; i<${#FitsNames[@]}; i++ )); do
    
    FitsName="${FitsNames[i]}"
    echo "${FitsNames[i]} ($((i+1))/${#FitsNames[@]})"
    
    # check non-COSMOS fields
    if [[ "$FitsName" == *"2011.0.00539.S_SB1_GB1_MB1_ECDFS02_field3_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2011.0.00539.S_SB1_GB1_MB2_ELS01_field2_sci.spw0_1_2_3"* ]] ; then
        echo "Warning! \"$FitsName\" is a non-COSMOS field! Skip and continue!"
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
    
    # cd 
    cd "Recovered"
    
    # tar
    tar -czf "$FitsName.tar.gz" "$FitsName"
    
    # cd back
    cd "../"
    
    # cd 
    cd "Simulated"
    
    # tar
    tar -czf "$FitsName.tar.gz" "$FitsName"
    
    # cd back
    cd "../"
    
done









# dzliu@isaac1:~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Recovered> du -hs 2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3.tar.gz
# 7.9G    2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3.tar.gz
# dzliu@isaac1:~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Recovered> du -hs 2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3
# 20G 2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3



























