#!/bin/bash
# 

source ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP
source ~/Cloud/Github/Crab.Toolkit.CAAP/SETUP.bash


#Input_w=("1250")
Input_z=("1.000" "2.000" "3.000" "4.000" "5.000" "6.000")
Input_lgMstar=("09.00" "09.50" "10.00" "10.50" "11.00" "11.50" "12.00")
Input_Type_SED=("MS" "SB")


FitsNames=( \
   "2013.1.00171.S_SB1_GB1_MB1_X_5308_sci.spw0_1_2_3" \
   "2013.1.00171.S_SB2_GB1_MB1_C_97_sci.spw0_1_2_3" \
   "2013.1.00208.S_SB1_GB1_MB1_zC406690_sci.spw0_1_2_3" \
   "2013.1.00668.S_SB1_GB1_MB1_zC406690_sci.spw0_1_2_3" \
   "2013.1.00884.S_SB1_GB1_MB1_CS_AGN9_sci.spw0_1_2_3" \
   "2013.1.00884.S_SB2_GB1_MB1_CS_AGN38_sci.spw0_1_2_3" \
   "2013.1.00884.S_SB3_GB1_MB1_CS_AGN54_sci.spw0_1_2_3" \
   "2013.1.01292.S_SB1_GB1_MB1_2-9278_sci.spw0_1_2_3" \
   "2015.1.00137.S_SB1_GB1_MB1_z12_9_sci.spw0_1_2_3" \
   "2015.1.00137.S_SB3_GB1_MB1_z12_99_sci.spw0_1_2_3" \
   "2015.1.00260.S_SB1_GB1_MB1__9942__sci.spw0_1_2_3" \
   "2015.1.00260.S_SB2_GB1_MB1__860__sci.spw0_1_2_3" \
   "2015.1.00260.S_SB3_GB1_MB1__9478__sci.spw0_1_2_3" \
   "2015.1.00260.S_SB4_GB1_MB1__7427__sci.spw0_1_2_3" \
)


echo "FitsNames = ${FitsNames[@]}"

if [[ ! -d "Output_images" ]]; then
    mkdir "Output_images"
fi

for FitsName in ${FitsNames[@]}; do
    
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
                    
                    if [[ -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName.cont.I.image.fits" ]]; then
                        
                        mkdir -p "Output_images/Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/"
                        cp "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName.cont.I.image.fits" \
                            "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_"* \
                            "Output_images/Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/"
                        
                        echo "copying files for \"$FitsName\" \\"
                        echo "    -w \"$i_w\" -z \"${i_z}\" -lgMstar \"${i_lgMstar}\" -Type-SED \"${i_Type_SED}\""
                        
                    
                    else
                        
                        echo "Error! \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName.cont.I.image.fits\" was not found!"
                        exit
                    
                    fi
                    
                done
            done
        done
    done
    
    #<TODO><DBEUG># 
    #break
    
done

