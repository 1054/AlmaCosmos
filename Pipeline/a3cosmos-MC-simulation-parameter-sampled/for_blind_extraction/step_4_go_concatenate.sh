#!/bin/bash
# 

set -e 


if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code only works on aida42198!"
    exit
fi


echo ""
echo "This code will merge all the sim-rec-cross-matched catalogs into a big catalog"
echo ""
echo "Sleeping for 5 seconds then start ..."
sleep 5
echo ""


#source $(dirname $(dirname $(dirname $(dirname "${BASH_SOURCE[0]}"))))/Softwares/SETUP.bash
#
#
#cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/
#
#if [[ ! -d statistics_PyBDSM ]]; then echo "Error! \"statistics_PyBDSM\" does not exist!"; exit 255; fi
#
#cd statistics_PyBDSM

if [[ ! -f "concat_sim_rec_data_table.txt" ]]; then
    head -n 1 $(ls -1 output_*.txt | head -n 1) > "concat_sim_rec_data_table.txt"
    cat output_*.txt | grep -v "^#" >> "concat_sim_rec_data_table.txt"
    tar -czf output_txt.tar.gz --remove-files output_*.txt done_output_*
fi

source ~/Softwares/Topcat/bin_setup.bash
topcat -stilts tpipe \
                in=concat_sim_rec_data_table.txt ifmt=ascii \
                cmd="replacecol sim_rms -units \"mJy/beam\" \"sim_rms*1e3\"" \
                cmd="replacecol sim_f -units \"mJy\" \"sim_f*1e3/(PI/(4*ln(2))*(sim_beam_Maj*sim_beam_Min)/(sim_pixsc*sim_pixsc))\"" \
                cmd="replacecol sim_fpeak -units \"mJy/beam\" sim_fpeak" \
                cmd="replacecol sim_beam_maj -units \"arcsec\" sim_beam_maj" \
                cmd="replacecol sim_beam_min -units \"arcsec\" sim_beam_min" \
                cmd="replacecol sim_beam_pa -units \"degree\" sim_beam_pa" \
                cmd="replacecol sim_Maj -units \"arcsec\" sim_Maj" \
                cmd="replacecol sim_Min -units \"arcsec\" sim_Min" \
                cmd="replacecol sim_PA -units \"degree\" sim_PA" \
                cmd="replacecol rec_f -units \"mJy\" \"rec_f*1e3\"" \
                cmd="replacecol rec_df -units \"mJy\" \"rec_df*1e3\"" \
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


