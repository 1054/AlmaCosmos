#!/bin/bash
# 


# 
# Read Recovered catalog
# 
IFS=$'\n' read -d '' -r -a FitsNames < "list_projects.txt"

for (( i=0; i<${#FitsNames[@]}; i++ )); do
    
    FitsName=$(basename "${FitsNames[i]}" | sed -e 's/\.cont.I.image.fits$//g')
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
    
    # check already packed tar file
    if [[ -f "Recovered/$FitsName.tar.gz" ]]; then
        echo -n "Found existing \"Recovered/$FitsName.tar.gz\"! Checking integrity ... "
        if ! tar tf "Recovered/$FitsName.tar.gz" &> /dev/null; then 
            echo "Broken! Deleting it!"
            rm "Recovered/$FitsName.tar.gz"
        else
            echo -n "OK!" 
            if [[ -d "Recovered/$FitsName" ]]; then
                echo -n " Now let us delete the folder \"Recovered/$FitsName\"!"
                echo "rm -rf \"Recovered/$FitsName\""
                #rm -rf "Recovered/$FitsName"
            fi
            echo ""
        fi
    fi
    # 
    if [[ -f "Simulated/$FitsName.tar.gz" ]]; then
        echo -n "Found existing \"Simulated/$FitsName.tar.gz\"! Checking integrity ... "
        if ! tar tf "Simulated/$FitsName.tar.gz" &> /dev/null; then 
            echo "Broken! Deleting it!"
            rm "Simulated/$FitsName.tar.gz"
        else
            echo -n "OK!" 
            if [[ -d "Simulated/$FitsName" ]]; then
                echo -n " Now let us delete the folder \"Simulated/$FitsName\"!"
                echo "rm -rf \"Simulated/$FitsName\""
                #rm -rf "Simulated/$FitsName"
            fi
            echo ""
        fi
    fi
    
    # 
    if [[ ! -f "Simulated/$FitsName.tar.gz" ]]; then
        # check simulation directory and datatable
        if [[ ! -f "Simulated/$FitsName/datatable_Simulated.txt" ]]; then
            echo "Error! \"Simulated/$FitsName/datatable_Simulated.txt\" was not found!"
            exit
        fi
        # cd, tar, cd back
        cd "Simulated"
        tar -czf "$FitsName.tar.gz" "$FitsName"
        cd "../"
    fi
    
    # 
    if [[ ! -f "Recovered/$FitsName.tar.gz" ]]; then
        # check recovered directory
        if [[ ! -d "Recovered/$FitsName/" ]]; then
            echo "Error! \"Recovered/$FitsName/\" was not found!"
            exit
        fi
        # cd, tar, cd back
        cd "Recovered"
        tar -czf "$FitsName.tar.gz" "$FitsName"
        cd "../"
    fi
    
done









# dzliu@isaac1:~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Recovered> du -hs 2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3.tar.gz
# 7.9G    2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3.tar.gz
# dzliu@isaac1:~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Recovered> du -hs 2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3
# 20G 2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3



























