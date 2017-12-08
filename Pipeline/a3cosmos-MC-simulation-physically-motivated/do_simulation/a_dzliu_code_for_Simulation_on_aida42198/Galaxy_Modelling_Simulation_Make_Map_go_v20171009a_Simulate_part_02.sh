#!/bin/bash
# 

source ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/SETUP
source ~/Cloud/Github/Crab.Toolkit.CAAP/SETUP.bash


#Input_w=("1250")
Input_z=("1.000" "2.000" "3.000" "4.000" "5.000" "6.000")
Input_lgMstar=("09.00" "09.50" "10.00" "10.50" "11.00" "11.50" "12.00")
Input_Type_SED=("MS" "SB")


FitsNames=( \
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
    mkdir "Input_images"
fi

for FitsName in ${FitsNames[@]}; do
    
    # check previous output
    if [[ -f "Simulated/$FitsName/done" ]]; then
        continue
    fi
    
    # check input image
    if [[ ! -f "Input_images/$FitsName.cont.I.image.fits" ]]; then
        cd "Input_images/"
        # use dzliu prior extraction residual image
        #ln -fs "../../Source_Extraction_by_Daizhong_Liu/Read_Residual_Images_of_Prior_Extraction_with_Master_Catalog_v20170730/$FitsName.cont.I.image.residual.fits"
        # use benjamin blind extraction residual image
        ln -fs "/disk1/ALMA_COSMOS/A3COSMOS/blind_extraction/ALMA_full_archive_by_Benjamin/residual_images_061017/$FitsName.cont.I.residual.fits" "$FitsName.cont.I.image.residual.fits"
        # 
        ln -fs "../../../ALMA_Calibrated_Images_by_Magnelli/v20170604/fits/$FitsName.cont.I.image.fits"
        ln -fs "../../../ALMA_Calibrated_Images_by_Magnelli/v20170604/fits/$FitsName.cont.I.clean-beam.fits"
        cd "../"
    fi
    
    # get wavelength from fits header
    obsfreq=$(gethead "Input_images/$FitsName.cont.I.image.fits" CRVAL3)
    obswave=$(awk "BEGIN {print 2.99792458e5/($obsfreq/1e9);}")
    if [[ "$obswave"x == ""x ]]; then
        echo "Error! Failed to get observation frequency/wavelength from the fits header keyword CRVAL3 of input fits file \"Input_images/$FitsName.cont.I.image.fits\"!"
        exit 1
    fi
    
    # backup simulated data table
    if [[ -f "Simulated/$FitsName/datatable_Simulated.txt" ]]; then
        if [[ -f "Simulated/$FitsName/datatable_Simulated.txt.backup" ]]; then
            mv "Simulated/$FitsName/datatable_Simulated.txt.backup" "Simulated/$FitsName/datatable_Simulated.txt.backup.backup"
        fi
        mv "Simulated/$FitsName/datatable_Simulated.txt" "Simulated/$FitsName/datatable_Simulated.txt.backup"
    fi
    
    # loop
    for i_w in "${obswave}"; do
        for i_z in "${Input_z[@]}"; do
            for i_lgMstar in "${Input_lgMstar[@]}"; do
                for i_Type_SED in "${Input_Type_SED[@]}"; do
                    
                    if [[ ! -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" ]]; then
                        
                        echo "caap-full-galaxy-modelling-map-maker \\"
                        echo "    -w \"$i_w\" -z \"${i_z}\" -lgMstar \"${i_lgMstar}\" -Type-SED \"${i_Type_SED}\""
                        
                        caap-full-galaxy-modelling-map-maker \
                            -sci "Input_images/$FitsName.cont.I.image.fits" \
                            -psf "Input_images/$FitsName.cont.I.clean-beam.fits" \
                            -res "Input_images/$FitsName.cont.I.image.residual.fits" \
                            -gal '../../../../S06_Modelling/Cosmological_Galaxy_Modelling_for_COSMOS' \
                            -w "$i_w" -z "${i_z}" -lgMstar "${i_lgMstar}" -Type-SED "${i_Type_SED}" \
                            -out "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                        
                        if [[ ! -d "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]]; then
                            echo "Error! Failed to run \"caap-full-galaxy-modelling-map-maker\" and create \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\" directory!"
                            exit 1
                        fi
                        
                        cd "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/"
                        cp */galaxy_model_*.txt ./
                        cp */image_sim.fits ./
                        cd "../../../"
                        
                        if [[ ! -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" ]]; then
                            echo "Error! Failed to run \"caap-full-galaxy-modelling-map-maker\" and create \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits\" file!"
                            exit 1
                        fi
                    
                    else
                        
                        echo "Found existing \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits\", skip and continue!"
                    
                    fi
                    
                    # do bug fix - apply image_sci_mask to image_sim
                    if [[ 1 == 1 ]]; then
                        cd "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName.cont.I.image/"
                        echo CrabFitsImageArithmetic "image_res.fits" "adds" "image_mod.fits" "image_sim_nonan.fits" ">" "image_sim_nonan.log"
                             CrabFitsImageArithmetic "image_res.fits" "adds" "image_mod.fits" "image_sim_nonan.fits"  >  "image_sim_nonan.log"
                        echo CrabFitsImageArithmetic "image_sci.fits" "times" "0" "image_sci_maskzero.fits" ">" "image_sci_maskzero.log"
                             CrabFitsImageArithmetic "image_sci.fits" "times" "0" "image_sci_maskzero.fits"  >  "image_sci_maskzero.log"
                        echo CrabFitsImageArithmetic "image_sci_maskzero.fits" "adds" "1" "image_sci_mask.fits" ">" "image_sci_mask.log"
                             CrabFitsImageArithmetic "image_sci_maskzero.fits" "adds" "1" "image_sci_mask.fits"  >  "image_sci_mask.log"
                        echo CrabFitsImageArithmetic "image_sim_nonan.fits" "times" "image_sci_mask.fits" "image_sim.fits" ">" "image_sim.log"
                             CrabFitsImageArithmetic "image_sim_nonan.fits" "times" "image_sci_mask.fits" "image_sim.fits"  >  "image_sim.log"
                        #rm image_sci_maskzero.fits image_sim_nonan.fits
                        #rm ../*.log
                        cp image_sim.fits ../
                        cd "../../../../"
                    fi
                    
                    
                    # Concat simulated datatable
                    if [[ -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt" ]]; then
                        if [[ ! -f "Simulated/$FitsName/datatable_Simulated.txt" ]]; then
                            head -n 1 "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt" | xargs -d '\n' -I % echo "%    wavelength_um" \
                                    > "Simulated/$FitsName/datatable_Simulated.txt"
                        fi
                        cat "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt" | tail -n +3 | xargs -d '\n' -I % echo "%    $i_w" \
                                    >> "Simulated/$FitsName/datatable_Simulated.txt"
                        echo "Reading \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt\""
                    else
                        echo "Warning! \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt\" was not found! ******"
                    fi
                    
                done
            done
        done
    done
    
    #<TODO><DBEUG># 
    #break
    
done

