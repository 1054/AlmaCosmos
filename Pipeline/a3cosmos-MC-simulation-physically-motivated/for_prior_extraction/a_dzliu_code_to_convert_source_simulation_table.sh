#!/bin/bash
# 

set -e

if [[ $(type topcat | wc -l) -eq 0 ]]; then
    echo "Error! Topcat was not found!"
    exit
fi

if [[ ! -f "Input_Data_Dir.txt" ]]; then
    echo "Error! \"Input_Data_Dir.txt\" was not found under current directory!"
    exit
fi

if [[ ! -f "Input_Data_Version.txt" ]]; then
    echo "Error! \"Input_Data_Version.txt\" was not found under current directory!"
    exit
fi

Input_Data_Dir=$(cat Input_Data_Dir.txt | grep -v "^#" | head -n 1)
Input_Data_Version=$(cat Input_Data_Version.txt | grep -v "^#" | head -n 1)

if [[ ! -d "Output_catalogs" ]]; then
    echo "Error! \"Output_catalogs\" was not found under current directory!"
    exit
fi

OutputDir="Output_catalogs"


# 
# Copy fits_meta_file.txt
# 
if [[ -f "$Input_Data_Dir/$Input_Data_Version/list_project_rms_for_v20170604.txt" ]]; then
    cp "$Input_Data_Dir/list_project_rms_for_v20170604.txt" "$OutputDir/"
    Fits_Meta_Table="list_project_rms_for_v20170604.txt"
    Fits_Meta_Table_Format="ascii"
    #cp '/Volumes/GoogleDrive/Team Drives/A3COSMOS/Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/v20170604_code/list_project_rms_for_v20170604.txt' \
    #    .
fi

if [[ -f "$Input_Data_Dir/$Input_Data_Version/fits_meta_table.fits" ]] || \
    [[ -L "$Input_Data_Dir/$Input_Data_Version/fits_meta_table.fits" ]]; then
    cp -L "$Input_Data_Dir/$Input_Data_Version/fits_meta_table.fits" "$OutputDir/"
    Fits_Meta_Table="fits_meta_table.fits"
    Fits_Meta_Table_Format="fits"
fi


# 
# cd "$OutputDir"
# 
cd "$OutputDir"


# 
# First cross-match fits meta table
# 
topcat -stilts tmatchn \
                nin=2 \
                in1='Output_Prior_Simulation_Catalog.txt' \
                ifmt1=ascii \
                icmd1="addcol Image_file \"Image+\\\".cont.I.image.fits\\\"\"" \
                icmd1="replacecol sim_dir_str -name \"Simu\" \"sim_dir_str\"" \
                values1="Image_file" \
                in2="$Fits_Meta_Table" \
                ifmt2="$Fits_Meta_Table_Format" \
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


# 
# Then we cross-match Getpix catalog, so as to filter out some sources which are simulated on NaN pixels
# 
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
# Done
# 
echo "Output to \"$OutputDir/Output_Prior_Simulation_Catalog.fits\"!"
# 
#topcat -stilts tpipe \
#            in="Output_Prior_Simulation_Catalog.fits" \
#            cmd="select (S_in/rms>=3.0)" \
#            out="Output_Prior_Simulation_Catalog_SNR_GE_3.fits"
## 
#echo "Output to \"Output_Prior_Simulation_Catalog_SNR_GE_3.fits\"!"

if [[ -f "Output_Prior_Galfit_Gaussian_Catalog.fits" ]]; then
      rm "Output_Prior_Simulation_Catalog_tmp1.fits"
      gzip "Output_Prior_Simulation_Catalog.txt"
      gzip "Output_Prior_Simulation_Catalog.fits"
fi





