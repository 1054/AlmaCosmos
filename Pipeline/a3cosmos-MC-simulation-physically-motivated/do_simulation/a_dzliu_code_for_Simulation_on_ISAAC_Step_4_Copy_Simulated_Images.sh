#!/bin/bash
# 

source ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP
source ~/Cloud/Github/Crab.Toolkit.CAAP/SETUP.bash


#Input_w=("1250")
Input_z=("1.000" "2.000" "3.000" "4.000" "5.000" "6.000")
Input_lgMstar=("09.00" "09.50" "10.00" "10.50" "11.00" "11.50" "12.00")
Input_Type_SED=("MS" "SB")


IFS=$'\n' read -d '' -r -a FitsNames < "list_projects.txt"


echo "FitsNames = ${FitsNames[@]}"


if [[ ! -d "Output_images" ]]; then
    mkdir "Output_images"
fi


for (( i=0; i<${#FitsNames[@]}; i++ )); do
    
    # check FitsName not empty
    if [[ x"${FitsNames[i]}" == x"" ]]; then
        continue
    fi
    
    # get FitsName without path and suffix
    FitsName=$(basename "${FitsNames[i]}" | sed -e 's/\.cont.I.image.fits//g')
    echo "${FitsNames[i]} ($((i+1))/${#FitsNames[@]})"
    
    # get wavelength from fits header
    obsfreq=$(gethead "Input_images/$FitsName.cont.I.image.fits" CRVAL3)
    obswave=$(awk "BEGIN {print 2.99792458e5/($obsfreq/1e9);}")
    if [[ "$obswave"x == ""x ]]; then
        echo "Error! Failed to get observation frequency/wavelength from the fits header keyword CRVAL3 of input fits file \"Input_images/$FitsName.cont.I.image.fits\"!"
        exit 1
    fi
    
    # loop
    for i_w in "${obswave}"; do
        for i_z in "${Input_z[@]}"; do
            for i_lgMstar in "${Input_lgMstar[@]}"; do
                for i_Type_SED in "${Input_Type_SED[@]}"; do
                    
                    if [[ -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" ]]; then
                        
                        mkdir -p "Output_images/Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/"
                        cp "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" \
                            "Output_images/Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName.cont.I.image.fits"
                        cp "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_"* \
                            "Output_images/Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/"
                        
                        echo "copying files for \"$FitsName\" \\"
                        echo "    -w \"$i_w\" -z \"${i_z}\" -lgMstar \"${i_lgMstar}\" -Type-SED \"${i_Type_SED}\""
                        
                    else
                        
                        echo "Error! \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits\" was not found!"
                        exit
                    
                    fi
                    
                done
            done
        done
    done
    
    #<TODO><DBEUG># 
    #break
    
done

