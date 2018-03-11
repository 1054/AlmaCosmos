#!/bin/bash
# 

source ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP
source ~/Cloud/Github/Crab.Toolkit.CAAP/SETUP.bash


#Input_w=("1250")
Input_z=("1.000" "2.000" "3.000" "4.000" "5.000" "6.000")
Input_lgMstar=("09.00" "09.50" "10.00" "10.50" "11.00" "11.50" "12.00")
Input_Type_SED=("MS" "SB")


FitsNames=( \
    "2011.0.00097.S_SB1_GB1_MB1_COSMOS7_field5_sci.spw0_1_2_3" \
    "2012.1.00952.S_SB2_GB1_MB1_PACS-299_sci.spw0_1" \
    "2013.1.00151.S_SB1_GB1_MB1__187663__sci.spw0_1_2_3" \
    "2015.1.00137.S_SB2_GB1_MB1_z35_12_sci.spw0_1_2_3" \
    "2011.0.00097.S_SB1_GB1_MB6_COSMOS2_field6_sci.spw0_1_2_3" \
    "2012.1.00076.S_SB1_GB1_MB1_ID143_sci.spw0_1_2_3" \
    "2012.1.00323.S_SB2_GB1_MB1__113083__sci.spw0" \
    "2012.1.00523.S_SB6_GB1_MB1_hz4_sci.spw0_1_2_3" \
    "2012.1.00978.S_SB2_GB1_MB1_AzTEC-1_sci.spw0_1_2_3" \
    "2012.1.00978.S_SB4_GB1_MB1_GISMO-AK03_sci.spw0_1_2_3" \
    "2013.1.00034.S_SB1_GB1_MB1_midz_cell6_76189_sci.spw0_1_2_3" \
    "2013.1.00034.S_SB2_GB1_MB1_lowz_cell6_120018_sci.spw0_1_2_3" \
    "2013.1.00034.S_SB3_GB2_MB1_highz_cell6_148445_sci.spw0_1_2_3" \
    "2013.1.00034.S_SB3_GB3_MB1_hz_cell5_302528_sci.spw0_1_2_3" \
    "2013.1.00092.S_SB1_GB1_MB1_KMOS3D_COS3_5587_sci.spw0_1_2_3" \
    "2013.1.00092.S_SB2_GB1_MB1_CosDeep400528_sci.spw2_3" \
    "2013.1.00118.S_SB1_GB1_MB1_AzTECC116_sci.spw0_1_2_3" \
    "2015.1.00379.S_SB1_GB1_MB1_VUDS5170072382_sci.spw0_1_2_3" \
    "2015.1.00379.S_SB2_GB1_MB1_VUDS5101228764_sci.spw0_1_2_3" \
    "2015.1.00388.S_SB1_GB1_MB1_HZ4_sci.spw0_1_2_3" \
    "2015.1.00388.S_SB2_GB1_MB1_HZ9_sci.spw0_1_2_3" \
    "2015.1.00540.S_SB1_GB1_MB1_UVISTA-65666_sci.spw0_1_2_3" \
    "2015.1.00664.S_SB1_GB1_MB1_KMOS3DCOS4-24763_sci.spw0_1_2_3" \
    "2015.1.00704.S_SB1_GB1_MB4_az4-cosmos-6_sci.spw0_1_2_3" \
    "2015.1.00704.S_SB2_GB1_MB3_az4-cosmos-6_sci.spw0_1_2_3" \
    "2015.1.00853.S_SB1_GB1_MB1_C21434_sci.spw0_1_2" \
    "2015.1.00862.S_SB1_GB1_MB1__COS-z1.47-30__sci.spw0_1_2_3" \
    "2015.1.00928.S_SB2_GB1_MB1_HZ10_sci.spw0_1_2_3" \
    "2015.1.01105.S_SB1_GB1_MB1_COSMOS13679_sci.spw0_1_2_3" \
    "2015.1.01212.S_SB1_GB1_MB1__824759__sci.spw0_1_2_3" \
    "2015.1.01495.S_SB1_GB1_MB1_COSMOS-16199_sci.spw0_1_2_3" \
)

# TODO
#   "2013.1.00171.S_SB1_GB1_MB1_X_5308_sci.spw0_1_2_3" \
#   "2013.1.00171.S_SB2_GB1_MB1_C_97_sci.spw0_1_2_3" \
#   "2013.1.00208.S_SB1_GB1_MB1_zC406690_sci.spw0_1_2_3" \
#   "2013.1.00668.S_SB1_GB1_MB1_zC406690_sci.spw0_1_2_3" \
#   "2013.1.00884.S_SB1_GB1_MB1_CS_AGN9_sci.spw0_1_2_3" \
#   "2013.1.00884.S_SB2_GB1_MB1_CS_AGN38_sci.spw0_1_2_3" \
#   "2013.1.00884.S_SB3_GB1_MB1_CS_AGN54_sci.spw0_1_2_3" \
#   "2013.1.01292.S_SB1_GB1_MB1_2-9278_sci.spw0_1_2_3" \
#   "2015.1.00137.S_SB1_GB1_MB1_z12_9_sci.spw0_1_2_3" \
#   "2015.1.00137.S_SB3_GB1_MB1_z12_99_sci.spw0_1_2_3" \
#   "2015.1.00260.S_SB1_GB1_MB1__9942__sci.spw0_1_2_3" \
#   "2015.1.00260.S_SB2_GB1_MB1__860__sci.spw0_1_2_3" \
#   "2015.1.00260.S_SB3_GB1_MB1__9478__sci.spw0_1_2_3" \
#   "2015.1.00260.S_SB4_GB1_MB1__7427__sci.spw0_1_2_3" \


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

