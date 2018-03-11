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

echo "FitsNames = ${FitsNames[@]}"

if [[ ! -d "Input_images" ]]; then
    echo "Error! Input_images was not found! Please run Galaxy_Modelling_Simulation_Make_Map_go_*_Simulate.sh first!"
fi

if [[ ! -d "Input_images_2" ]]; then
    echo "Error! Input_images_2 was not found! Please run Galaxy_Modelling_Simulation_Make_Map_go_*_Simulate.sh first!"
fi

for FitsName in ${FitsNames[@]}; do
    
    # check input image
    if [[ ! -f "Input_images/$FitsName.cont.I.image.fits" ]]; then
        echo "\"Input_images/$FitsName.cont.I.image.fits\" was not found!"
        exit 1
    fi
    
    # get wavelength from fits header
    obsfreq=$(gethead "Input_images/$FitsName.cont.I.image.fits" CRVAL3)
    obswave=$(awk "BEGIN {print 2.99792458e5/($obsfreq/1e9);}")
    if [[ "$obswave"x == ""x ]]; then
        echo "Error! Failed to get observation frequency/wavelength from the fits header keyword CRVAL3 of input fits file \"Input_images/$FitsName.cont.I.image.fits\"!"
        exit 1
    fi
    
    # check simulated directory
    if [[ ! -d "Simulated/$FitsName" ]]; then
        echo "\"Simulated/$FitsName\" was not found!"
        exit 1
    fi
    
    # make recovered directory
    if [[ ! -d "Recovered/$FitsName" ]]; then
        mkdir -p "Recovered/$FitsName"
    fi
    
    # cd recovered directory
    cd "Recovered/$FitsName/"
    
    # backup final data table
    if [[ -f "datatable_Recovered_getpix.txt" ]]; then
        if [[ -f "datatable_Recovered_getpix.txt.backup" ]]; then
            mv "datatable_Recovered_getpix.txt.backup" "datatable_Recovered_getpix.txt.backup.backup"
        fi
        mv "datatable_Recovered_getpix.txt" "datatable_Recovered_getpix.txt.backup"
    fi
    if [[ -f "datatable_Recovered_galfit.txt" ]]; then
        if [[ -f "datatable_Recovered_galfit.txt.backup" ]]; then
            mv "datatable_Recovered_galfit.txt.backup" "datatable_Recovered_galfit.txt.backup.backup"
        fi
        mv "datatable_Recovered_galfit.txt" "datatable_Recovered_galfit.txt.backup"
    fi
    
    # loop
    for i_w in "${obswave}"; do
        for i_z in "${Input_z[@]}"; do
            for i_lgMstar in "${Input_lgMstar[@]}"; do
                for i_Type_SED in "${Input_Type_SED[@]}"; do
                    
                    # Check output directory, delete failed runs
                    if [[ -d "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]]; then
                        if [[ ! -f "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/List_of_Input_Sci_Images.txt" ]]; then
                            echo ""
                            echo "rm -r \"w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\""
                            echo ""
                            rm -r "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                            echo ""
                            echo "rm -r \"Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\" 2>/dev/null"
                            echo ""
                            rm -r "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" 2>/dev/null
                        fi
                    fi
                    
                    # Run caap-prior-extraction-photometry
                    if [[ ! -d "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]]; then
                        # 
                        echo "caap-prior-extraction-photometry \\"
                        echo "    -out \"w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\""
                        # 
                        if [[ ! -d "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]]; then
                            caap-prior-extraction-photometry \
                                -cat "../../Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec.txt" \
                                -sci "../../Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" \
                                -out                           "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                        else
                            caap-prior-extraction-photometry \
                                -out                           "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                        fi
                    fi
                    
                    # Read results, output files are "Read_Results_of_XXX/{Output_getpix.txt,Output_galfit.txt}"
                    if [[ ! -d "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]] || \
                       [[ ! -f "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_getpix.txt" ]]; then
                        caap-prior-extraction-photometry-read-results \
                                                           "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                    fi
                    
                    # Concat results, output files are "Read_Results_of_XXX/{Output_getpix.txt,Output_galfit.txt}"
                    if [[ -f "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_getpix.txt" ]]; then
                        if [[ ! -f "datatable_Recovered_getpix.txt" ]]; then
                            head -n 1 "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_getpix.txt" \
                                | xargs -d '\n' -I % echo "%        image_dir" \
                                > "datatable_Recovered_getpix.txt"
                        fi
                        echo "Reading \"Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_getpix.txt\""
                        tail -n +3 "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_getpix.txt" \
                            | xargs -d '\n' -I % echo "%        w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" \
                            >> "datatable_Recovered_getpix.txt"
                    else
                        echo "Warning! \"Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_getpix.txt\" was not found! ******"
                    fi
                    if [[ -f "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_galfit.txt" ]]; then
                        if [[ ! -f "datatable_Recovered_galfit.txt" ]]; then
                            head -n 1 "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_galfit.txt" \
                                | xargs -d '\n' -I % echo "%        image_dir" \
                                > "datatable_Recovered_galfit.txt"
                        fi
                        echo "Reading \"Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_galfit.txt\""
                        tail -n +3 "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_galfit.txt" \
                            | xargs -d '\n' -I % echo "%        w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" \
                            >> "datatable_Recovered_galfit.txt"
                    else
                        echo "Warning! \"Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/Output_galfit.txt\" was not found! ******"
                    fi
                done
            done
        done
    done
    
    cd "../../"
    #break
done

