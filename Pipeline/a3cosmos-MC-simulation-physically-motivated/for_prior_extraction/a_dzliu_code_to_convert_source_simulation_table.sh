#!/bin/bash
# 

if [[ $(type topcat | wc -l) -eq 0 ]]; then
    echo "Error! Topcat was not found!"
    exit
fi

if [[ ! -f "list_project_rms_for_v20170604.txt" ]]; then
    cp '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/v20170604_code/list_project_rms_for_v20170604.txt' \
        .
fi


if [[ 1 -eq 1 ]]; then
    topcat -stilts tmatchn \
                nin=2 \
                in1='Output_Prior_Simulation_Catalog.txt' \
                ifmt1=ascii \
                icmd1="addcol Image_file_fits \"Image+\\\".cont.I.image.fits\\\"\"" \
                values1="Image_file_fits" \
                in2='list_project_rms_for_v20170604.txt' \
                ifmt2=ascii \
                icmd2="keepcols \"beam_maj beam_min beam_PA rms image_file\"" \
                values2="image_file" \
                matcher=exact \
                multimode=pairs \
                iref=1 \
                out="Output_Prior_Simulation_Catalog.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # 
                # converts all units to Jy, Jy/beam.
                # 
                # note: rms = pixnoise * fluxconv
                # 
    # 
    echo "Output to \"Output_Prior_Simulation_Catalog.fits\"!"
    # 
    #topcat -stilts tpipe \
    #            in="Output_Prior_Simulation_Catalog.fits" \
    #            cmd="select (S_in/rms>=3.0)" \
    #            out="Output_Prior_Simulation_Catalog_SNR_GE_3.fits"
    ## 
    #echo "Output to \"Output_Prior_Simulation_Catalog_SNR_GE_3.fits\"!"
fi
