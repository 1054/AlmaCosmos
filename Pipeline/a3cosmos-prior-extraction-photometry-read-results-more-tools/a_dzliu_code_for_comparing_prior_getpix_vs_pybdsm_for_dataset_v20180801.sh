#!/bin/bash
# 

if [[ $(type topcat | wc -l) -eq 0 ]]; then
    echo "Error! Topcat was not found!"
    exit
fi

cat_prior="../more_files/A-COSMOS_prior_2018-09-28_Gaussian_All_columns_and_with_getpix.fits.gz"
cat_pybdsm="../../../Blind_Extraction_by_Daizhong/20180829/Output_Blind_Extraction_Photometry_PyBDSM_20180911_01h04m52s_with_meta.fits.gz"
output_dir="." # "compare_prior_vs_pybdsm"

# overwrites
#rm "$output_dir/Plot_comparison_Maj_deconv.pdf"

# mkdir
if [[ "$output_dir" != "." ]]; then if [[ ! -d "$output_dir" ]]; then mkdir "$output_dir"; fi; fi

# cross-match to select common sources
if [[ ! -f "$output_dir/datatable_CrossMatched.fits" ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1="$cat_prior" \
                ifmt1=fits \
                values1="RA Dec Image" \
                suffix1="_prior" \
                icmd1="addcol rms getpix_rms_noise" \
                icmd1="keepcols \"RA Dec Image rms getpix_peak_flux getpix_total_flux getpix_rms_noise getpix_pb_corr getpix_pixel_value getpix_aperture_radius getpix_pixel_scale cat_id_5 image_file_5\"" \
                icmd1="replacecol getpix_peak_flux -name \"Peak_flux\" getpix_peak_flux" \
                icmd1="addcol E_Peak_flux -after \"Peak_flux\" getpix_rms_noise" \
                icmd1="replacecol getpix_total_flux -name \"Total_flux\" getpix_total_flux" \
                icmd1="addcol E_Total_flux -after \"Total_flux\" \"getpix_rms_noise*sqrt(PI*pow(getpix_aperture_radius/getpix_pixel_scale,2))\"" \
                in2="$cat_pybdsm" \
                ifmt2=fits \
                values2="RA Dec Image" \
                suffix2="_pybdsm" \
                icmd2="select \"!contains(Image,\\\"2015.1.00026.S_SB1_GB1_MB1_SHIZELS-14_sci\\\")\"" \
                icmd2="select \"!contains(Image,\\\"2016.1.00735.S_SB1_GB1_MB1_CXID-360_sci\\\")\"" \
                matcher="sky+exact" \
                params=1.0 \
                fixcols=all \
                ocmd="select \"(Peak_flux_pybdsm/(rms_pybdsm/1000.0)>5 && Peak_flux_prior/(rms_prior/1000.0)>5 && Total_flux_pybdsm/(rms_pybdsm/1000.0)>3 && Total_flux_prior/(rms_prior/1000.0)>3)\"" \
                ocmd="select \"!startsWith(Image_pybdsm,\\\"2015.1.00568.S_SB1_GB1_MB1__DSFGS\\\")\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # converts all units to mJy, Jy/beam.
                # note: rms_pybdsm or rms_prior = pixnoise
                # note: we exclude "2015.1.00568.S_SB1_GB1_MB1__DSFGS" images because they are problematic. See Benjamin's email on 2018-02-19 with subject "image inspections".
echo "Output to \"$output_dir/datatable_CrossMatched.fits\"!"
fi



# 
# make plots
# 
margin=(80 50 88 20) # left, bottom, right, top
if [[ ! -f "$output_dir/Plot_comparison_Total_flux.pdf" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large Total \ flux \ from \ PyBDSM \ [mJy]" \
                ylabel="\large Total \ flux \ from \ prior \ getpix \ [mJy]" \
                xlog=true \
                ylog=true \
                xmin=0.05 xmax=30 ymin=0.05 ymax=30 \
                \
                auxvisible=true auxlabel="SNR \ peak \ (PyBDSM)" \
                auxfunc=log \
                aux="Peak_flux_pybdsm/(rms_pybdsm/1000.0)" \
                \
                layer1a=mark \
                shape1a=filled_circle \
                size1a=2 \
                shading1a=aux \
                in1a="$output_dir/datatable_CrossMatched.fits" \
                icmd1a="sort \"Peak_flux_pybdsm/(rms_pybdsm/1000.0)\"" \
                x1a="Total_flux_pybdsm*1e3" \
                y1a="Total_flux_prior*1e3" \
                \
                layer9=function \
                fexpr9='(x)' \
                color9=black \
                antialias9=true \
                thick9=1 \
                \
                legend=false \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_comparison_Total_flux.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_comparison_Total_flux.pdf\"!"
fi

if [[ ! -f "$output_dir/Plot_comparison_Peak_flux.pdf" ]]; then
topcat -stilts plot2plane \
                in="$output_dir/datatable_CrossMatched.fits" \
                icmd="sort \"Peak_flux_pybdsm/E_Peak_flux_pybdsm\"" \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large Peak \ flux \ from \ PyBDSM \ [mJy]" \
                ylabel="\large Peak \ flux \ from \ prior \ getpix \ [mJy]" \
                xlog=true \
                ylog=true \
                xmin=0.01 xmax=200 ymin=0.01 ymax=200 \
                \
                auxvisible=true auxlabel="SNR \ peak" \
                auxfunc=log \
                aux="Peak_flux_pybdsm/E_Peak_flux_pybdsm" \
                \
                layer1=mark \
                shape1=filled_circle \
                size1=2 \
                shading1=aux \
                leglabel1='\small Prior \ galfit \ vs \ PyBDSM' \
                x1="Peak_flux_pybdsm*1e3" \
                y1="Peak_flux_prior*1e3" \
                \
                layer9=function \
                fexpr9='(x)' \
                color9=black \
                antialias9=true \
                thick9=1 \
                leglabel9='1:1' \
                \
                legpos=0.08,0.94 \
                seq="9,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_comparison_Peak_flux.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_comparison_Peak_flux.pdf\"!"
fi

if [[ ! -f "$output_dir/Plot_histogram_Total_flux_ratio.pdf" ]]; then
topcat -stilts tpipe in="datatable_CrossMatched.fits" \
                cmd="addcol ratio \"Total_flux_prior/Total_flux_pybdsm\"" \
                cmd="select \"(getpix_pb_corr_prior < 4 && Peak_flux_pybdsm/E_Peak_flux_pybdsm > 3)\"" \
                omode=stats > "calc_ratio.txt"
topcat -stilts tpipe in="datatable_CrossMatched.fits" \
                cmd="addcol ratio \"log10(Total_flux_prior/Total_flux_pybdsm)\"" \
                cmd="select \"(getpix_pb_corr_prior < 4 && Peak_flux_pybdsm/E_Peak_flux_pybdsm > 3)\"" \
                omode=stats > "calc_ratio_log.txt"
topcat -stilts tpipe in="datatable_CrossMatched.fits" \
                cmd="addcol ratio \"log10(Total_flux_prior/Total_flux_pybdsm)\"" \
                cmd="select \"(getpix_pb_corr_prior < 4 && Peak_flux_pybdsm/E_Peak_flux_pybdsm > 3)\"" \
                cmd="keepcols \"ratio\"" \
                out="datatable_ratio_in_log.txt" ofmt=ascii
topcat -stilts tpipe in="datatable_CrossMatched.fits" \
                cmd="addcol ratio \"log10(Total_flux_prior/Total_flux_pybdsm)\"" \
                cmd="select \"(getpix_pb_corr_prior < 4 && Peak_flux_pybdsm/E_Peak_flux_pybdsm > 10)\"" \
                cmd="keepcols \"ratio\"" \
                out="datatable_ratio_in_log_SNR_GT_10.txt" ofmt=ascii
echo "# x y" > "label_ratio.txt"
mean_ratio=$(cat "calc_ratio.txt" | grep "^| ratio  " | tr -s ' ' | cut -d ' ' -f 4)
echo "$mean_ratio 900" >> "label_ratio.txt"
margin=(80 50 20 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=200 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large \ Total \ flux \ ratio \ getpix \, / \, PyBDSM" \
                ylabel="N" \
                xlog=true \
                ylog=true \
                xmin=0.1 xmax=10 \
                ymin=0.5 ymax=2e3 \
                \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="+1.105" \
                in1="datatable_CrossMatched.fits" \
                icmd1="sort \"Peak_flux_pybdsm/E_Peak_flux_pybdsm\"" \
                icmd1="select \"(getpix_pb_corr_prior < 4 && Peak_flux_pybdsm/E_Peak_flux_pybdsm > 3)\"" \
                x1="Total_flux_prior/Total_flux_pybdsm" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="+1.105" \
                in2="datatable_CrossMatched.fits" \
                icmd2="sort \"Peak_flux_pybdsm/E_Peak_flux_pybdsm\"" \
                icmd2="select \"(getpix_pb_corr_prior < 4 && Peak_flux_pybdsm/E_Peak_flux_pybdsm > 10)\"" \
                x2="Total_flux_prior/Total_flux_pybdsm" \
                \
                layer3=label \
                in3="label_ratio.txt" ifmt3=ascii \
                x3="x" \
                y3="y" \
                label3="\"ratio = \"+formatDecimal(x,3)" \
                color3=magenta \
                fontsize3=17 \
                \
                layer9=function \
                axis9=Vertical \
                fexpr9='(1)' \
                color9=black \
                antialias9=true \
                thick9=2 \
                dash9="dash" \
                \
                layer8=function \
                axis8=Vertical \
                fexpr8="($mean_ratio)" \
                color8=magenta \
                antialias8=true \
                thick8=2 \
                \
                legend=false \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out="$output_dir/Plot_histogram_Total_flux_ratio.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
                # leglabel1="S/N \ peak > 3"
                # leglabel2="S/N \ peak > 10"
                # leglabel9="ratio=1"
                # leglabel8="ratio=1.07"
                # legpos=0.97,0.97
                # legseq="9,8,1,2"
echo "Output to \"$output_dir/Plot_histogram_Total_flux_ratio.pdf\"!"
fi





