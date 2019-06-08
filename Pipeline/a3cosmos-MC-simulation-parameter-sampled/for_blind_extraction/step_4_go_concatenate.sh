#!/bin/bash
# 
# Input files: output_*.txt
# Output file: concat_sim_rec_data_table.fits
# 

set -e 


if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code only works on aida42198!"
    exit
fi


echo ""
echo "This code will merge all the sim-rec-cross-matched catalogs into a big catalog"
echo ""
echo "Sleeping for 1 second then start ..."
sleep 1
echo ""



if [[ ! -f "concat_sim_rec_data_table.fits" ]]; then
    # 
    # Now concatenate all output_*.txt into a big data table "concat_sim_rec_data_table.txt"
    # 
    if [[ ! -f "concat_sim_rec_data_table.txt" ]]; then
        head -n 1 $(ls -1 output_*.txt | head -n 1) > "concat_sim_rec_data_table.txt"
        cat output_*.txt | grep -v "^#" >> "concat_sim_rec_data_table.txt"
        tar -czf output_txt.tar.gz # --remove-files output_*.txt done_output_*
    fi
    # 
    # Now convert flux units and save as a topcat fits format data tbale
    # 
    # Note that the 'sim_f' and 'rec_f' are the direct sum of all pixels in the source-convolved-PSF image, 
    # but in reality we should convert pixel flux into Jy/beam then sum. So there is a factor of 
    # pi/(4ln2)*beam_theta**2 / pixsc**2. See correction below. 
    # 
    # This can also be confirmed in Philipp's IDL code: "prepare_simulation.pro"
    # ...
    # source_norm = source_conv/max(source_conv) * source_flux ; this is the convolved source image 2D array
    # ...
    # peak_flux = source_flux
    # total_flux = total(source_norm)
    # 
    # Moreover, we convert total_flux from \int(Jy/pixel) to \int(Jy/beam).
    # 
    source ~/Softwares/Topcat/bin_setup.bash
    topcat -stilts tpipe \
                    in=concat_sim_rec_data_table.txt ifmt=ascii \
                    cmd="replacecol sim_rms -units \"mJy/beam\" \"sim_rms*1e3\"" \
                    cmd="replacecol sim_f -units \"mJy\" \"sim_f>0 ? sim_f*1e3/(PI/(4*ln(2))*(sim_beam_Maj*sim_beam_Min)/(sim_pixsc*sim_pixsc)) : sim_f\"" \
                    cmd="replacecol sim_fpeak -units \"mJy/beam\" \"sim_fpeak>0 ? sim_fpeak*1e3 : sim_fpeak\"" \
                    cmd="replacecol sim_beam_maj -units \"arcsec\" sim_beam_maj" \
                    cmd="replacecol sim_beam_min -units \"arcsec\" sim_beam_min" \
                    cmd="replacecol sim_beam_pa -units \"degree\" sim_beam_pa" \
                    cmd="replacecol sim_Maj -units \"arcsec\" sim_Maj" \
                    cmd="replacecol sim_Min -units \"arcsec\" sim_Min" \
                    cmd="replacecol sim_PA -units \"degree\" sim_PA" \
                    cmd="replacecol rec_f -units \"mJy\" \"rec_f>0 ? rec_f*1e3 : rec_f\"" \
                    cmd="replacecol rec_df -units \"mJy\" \"rec_df>0 ? rec_df*1e3 : rec_df\"" \
                    cmd="replacecol rec_fpeak -units \"mJy/beam\" \"rec_fpeak*1e3\"" \
                    cmd="replacecol rec_dfpeak -units \"mJy/beam\" \"rec_dfpeak*1e3\"" \
                    cmd="replacecol rec_Maj -units \"arcsec\" rec_Maj" \
                    cmd="replacecol rec_Min -units \"arcsec\" rec_Min" \
                    cmd="replacecol rec_PA -units \"degree\" rec_PA" \
                    cmd="replacecol rec_Maj_convol -units \"arcsec\" rec_Maj_convol" \
                    cmd="replacecol rec_Min_convol -units \"arcsec\" rec_Min_convol" \
                    cmd="replacecol rec_PA_convol -units \"degree\" rec_PA_convol" \
                    out=concat_sim_rec_data_table.fits
    
    #if [[ -f concat_sim_rec_data_table.fits ]]; then rm concat_sim_rec_data_table.txt; fi
fi

