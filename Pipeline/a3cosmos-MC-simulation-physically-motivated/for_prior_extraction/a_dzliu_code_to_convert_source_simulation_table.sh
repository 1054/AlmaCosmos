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
    
    # First cross-match fits meta table
    topcat -stilts tmatchn \
                nin=2 \
                in1='Output_Prior_Simulation_Catalog.txt' \
                ifmt1=ascii \
                icmd1="addcol Image_file \"Image+\\\".cont.I.image.fits\\\"\"" \
                icmd1="replacecol sim_dir_str -name \"Simu\" \"sim_dir_str\"" \
                values1="Image_file" \
                in2='list_project_rms_for_v20170604.txt' \
                ifmt2=ascii \
                icmd2="replacecol image_file -name \"image_file_2\" \"image_file\"" \
                icmd2="replacecol wavelength -name \"Image_wavelength\" \"wavelength\"" \
                values2="image_file_2" \
                matcher=exact \
                multimode=pairs \
                iref=1 \
                ocmd="delcols \"image_file_2\"" \
                out="Output_Prior_Simulation_Catalog_tmp1.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # 
                # flux are mJy, rms are also mJy
                # 
    
    # Then we cross-match Getpix catalog, so as to filter out some sources which are simulated on NaN pixels
    topcat -stilts tmatchn \
                nin=2 \
                in1='Output_Prior_Simulation_Catalog_tmp1.fits' \
                ifmt1=fits \
                values1="id Image Simu" \
                in2='Output_Prior_Getpix_000.txt' \
                ifmt2=ascii \
                icmd2="keepcols \"pix_000 cat_id Simu Image\"" \
                icmd2="replacecol cat_id -name \"getpix_id\" \"cat_id\"" \
                icmd2="replacecol Image -name \"getpix_Image\" \"Image\"" \
                icmd2="replacecol Simu -name \"getpix_Simu\" \"Simu\"" \
                values2="getpix_id getpix_Image getpix_Simu" \
                matcher="exact+exact+exact" \
                multimode=pairs \
                iref=1 \
                ofmt=fits \
                ocmd="select \"(pix_000 != 0)\"" \
                out="Output_Prior_Simulation_Catalog.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
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
