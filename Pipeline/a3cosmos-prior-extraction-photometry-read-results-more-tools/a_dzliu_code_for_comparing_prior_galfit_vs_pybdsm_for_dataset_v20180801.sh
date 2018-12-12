#!/bin/bash
# 

set -e

if [[ $(type topcat | wc -l) -eq 0 ]]; then
    echo "Error! Topcat was not found!"
    exit
fi

cat_prior="../A-COSMOS_prior_2018-09-28_Gaussian_with_meta.fits.gz"
cat_pybdsm="../../../Blind_Extraction_by_Daizhong/20180829/Output_Blind_Extraction_Photometry_PyBDSM_20180911_01h04m52s_with_meta.fits.gz"
output_dir="." # "compare_prior_vs_pybdsm"

# overwrites
#rm "$output_dir/Plot_comparison_Maj_deconv.pdf"

# mkdir
if [[ "$output_dir" != "." ]]; then if [[ ! -d "$output_dir" ]]; then mkdir "$output_dir"; fi; fi

# cross-match to select common sources
if [[ ! -f "$output_dir/datatable_CrossMatched_prior_to_pybdsm.fits" ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1="$cat_prior" \
                ifmt1=fits \
                icmd1="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                values1="RA Dec Image" \
                suffix1="_prior" \
                in2="$cat_pybdsm" \
                ifmt2=fits \
                icmd2="replacecol DC_Maj -name Maj_deconv DC_Maj" \
                icmd2="replacecol DC_Min -name Min_deconv DC_Min" \
                icmd2="replacecol DC_PA -name PA_deconv DC_PA" \
                icmd2="replacecol E_DC_Maj -name E_Maj_deconv E_DC_Maj" \
                icmd2="replacecol E_DC_Min -name E_Min_deconv E_DC_Min" \
                icmd2="replacecol E_DC_PA -name E_PA_deconv E_DC_PA" \
                values2="RA Dec Image" \
                suffix2="_pybdsm" \
                matcher="sky+exact" \
                params=1.0 \
                fixcols=all \
                ocmd="select \"!startsWith(Image_pybdsm,\\\"2015.1.00568.S_SB1_GB1_MB1__DSFGS\\\")\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_prior_to_pybdsm.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # converts all units to mJy, Jy/beam.
                # note: rms_pybdsm or rms_prior = pixnoise
                # note: we exclude "2015.1.00568.S_SB1_GB1_MB1__DSFGS" images because they are problematic. See Benjamin's email on 2018-02-19 with subject "image inspections".
                # ocmd="select \"(Peak_flux_pybdsm/(Isl_rms_pybdsm)>5 && Peak_flux_prior/(rms_prior/1000.0)>5 && Total_flux_pybdsm/(Isl_rms_pybdsm)>3 && Total_flux_prior/(rms_prior/1000.0)>3)\"" \
echo "Output to \"$output_dir/datatable_CrossMatched_prior_to_pybdsm.fits\"!"
fi


# cross-match to select common sources
if [[ ! -f "$output_dir/datatable_CrossMatched_pybdsm_to_prior.fits" ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1="$cat_pybdsm" \
                ifmt1=fits \
                icmd1="replacecol DC_Maj -name Maj_deconv DC_Maj" \
                icmd1="replacecol DC_Min -name Min_deconv DC_Min" \
                icmd1="replacecol DC_PA -name PA_deconv DC_PA" \
                icmd1="replacecol E_DC_Maj -name E_Maj_deconv E_DC_Maj" \
                icmd1="replacecol E_DC_Min -name E_Min_deconv E_DC_Min" \
                icmd1="replacecol E_DC_PA -name E_PA_deconv E_DC_PA" \
                values1="RA Dec Image" \
                suffix1="_pybdsm" \
                in2="$cat_prior" \
                ifmt2=fits \
                icmd2="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                values2="RA Dec Image" \
                suffix2="_prior" \
                matcher="sky+exact" \
                params=1.0 \
                fixcols=all \
                ocmd="select \"!startsWith(Image_pybdsm,\\\"2015.1.00568.S_SB1_GB1_MB1__DSFGS\\\")\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_pybdsm_to_prior.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # converts all units to mJy, Jy/beam.
                # note: rms_pybdsm or rms_prior = pixnoise
                # note: we exclude "2015.1.00568.S_SB1_GB1_MB1__DSFGS" images because they are problematic. See Benjamin's email on 2018-02-19 with subject "image inspections".
echo "Output to \"$output_dir/datatable_CrossMatched_pybdsm_to_prior.fits\"!"
fi


# cross-match to select common sources
if [[ ! -f "$output_dir/datatable_CrossMatched_prior_to_pybdsm_best.fits" ]]; then
topcat -stilts tmatch2 \
                in1="$cat_prior" \
                ifmt1=fits \
                icmd1="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                values1="RA Dec Image" \
                suffix1="_prior" \
                in2="$cat_pybdsm" \
                ifmt2=fits \
                icmd2="replacecol DC_Maj -name Maj_deconv DC_Maj" \
                icmd2="replacecol DC_Min -name Min_deconv DC_Min" \
                icmd2="replacecol DC_PA -name PA_deconv DC_PA" \
                icmd2="replacecol E_DC_Maj -name E_Maj_deconv E_DC_Maj" \
                icmd2="replacecol E_DC_Min -name E_Min_deconv E_DC_Min" \
                icmd2="replacecol E_DC_PA -name E_PA_deconv E_DC_PA" \
                values2="RA Dec Image" \
                suffix2="_pybdsm" \
                matcher="sky+exact" \
                params=1.0 \
                fixcols=all \
                join=1and2 \
                find=best \
                ocmd="select \"!startsWith(Image_pybdsm,\\\"2015.1.00568.S_SB1_GB1_MB1__DSFGS\\\")\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_prior_to_pybdsm_best.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # converts all units to mJy, Jy/beam.
                # note: rms_pybdsm or rms_prior = pixnoise
                # note: we exclude "2015.1.00568.S_SB1_GB1_MB1__DSFGS" images because they are problematic. See Benjamin's email on 2018-02-19 with subject "image inspections".
                # ocmd="select \"(Peak_flux_pybdsm/(Isl_rms_pybdsm)>5 && Peak_flux_prior/(rms_prior/1000.0)>5 && Total_flux_pybdsm/(Isl_rms_pybdsm)>3 && Total_flux_prior/(rms_prior/1000.0)>3)\"" \
echo "Output to \"$output_dir/datatable_CrossMatched_prior_to_pybdsm_best.fits\"!"
fi


# cross-match to select common sources
if [[ ! -f "$output_dir/datatable_CrossMatched_pybdsm_to_prior_best.fits" ]]; then
topcat -stilts tmatch2 \
                in1="$cat_pybdsm" \
                ifmt1=fits \
                icmd1="replacecol DC_Maj -name Maj_deconv DC_Maj" \
                icmd1="replacecol DC_Min -name Min_deconv DC_Min" \
                icmd1="replacecol DC_PA -name PA_deconv DC_PA" \
                icmd1="replacecol E_DC_Maj -name E_Maj_deconv E_DC_Maj" \
                icmd1="replacecol E_DC_Min -name E_Min_deconv E_DC_Min" \
                icmd1="replacecol E_DC_PA -name E_PA_deconv E_DC_PA" \
                values1="RA Dec Image" \
                suffix1="_pybdsm" \
                in2="$cat_prior" \
                ifmt2=fits \
                icmd2="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                values2="RA Dec Image" \
                suffix2="_prior" \
                matcher="sky+exact" \
                params=1.0 \
                fixcols=all \
                join=1and2 \
                find=best \
                ocmd="select \"!startsWith(Image_pybdsm,\\\"2015.1.00568.S_SB1_GB1_MB1__DSFGS\\\")\"" \
                ofmt=fits \
                out="$output_dir/datatable_CrossMatched_pybdsm_to_prior_best.fits"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
                # converts all units to mJy, Jy/beam.
                # note: rms_pybdsm or rms_prior = pixnoise
                # note: we exclude "2015.1.00568.S_SB1_GB1_MB1__DSFGS" images because they are problematic. See Benjamin's email on 2018-02-19 with subject "image inspections".
echo "Output to \"$output_dir/datatable_CrossMatched_pybdsm_to_prior_best.fits\"!"
fi










plot() {

# 
# make plots
# 
margin=(100 70 100 20) # left, bottom, right, top
if [[ ! -f "$output_dir/Plot_comparison_Total_flux.pdf" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large Total \ flux \ from \ PyBDSM \ [mJy]" \
                ylabel="\large Total \ flux \ from \ prior \ fitting \ [mJy]" \
                xlog=true \
                ylog=true \
                xmin=0.05 xmax=50 ymin=0.05 ymax=50 \
                \
                auxvisible=true auxlabel="SNR \ peak \ (PyBDSM)" \
                auxfunc=log \
                aux="Peak_flux_pybdsm/(Isl_rms_pybdsm)" \
                \
                layer1a=mark \
                shape1a=filled_circle \
                size1a=2 \
                shading1a=aux \
                in1a="$output_dir/datatable_CrossMatched.fits" \
                icmd1a="sort \"Peak_flux_pybdsm/(Isl_rms_pybdsm)\"" \
                icmd1a="select \"(Total_flux_prior-Total_flux_pybdsm)/abs(Total_flux_pybdsm)<1.0 && (Total_flux_pybdsm-Total_flux_prior)/abs(Total_flux_prior)<1.0\"" \
                x1a="Total_flux_pybdsm*1e3" \
                y1a="Total_flux_prior*1e3" \
                leglabel1a="\footnotesize Prior \ galfit \ vs \ PyBDSM" \
                \
                layer1b=mark \
                shape1b=open_circle \
                size1b=2 \
                shading1b=aux \
                in1b="$output_dir/datatable_CrossMatched.fits" \
                icmd1b="sort -down \"(Total_flux_prior-Total_flux_pybdsm)/abs(Total_flux_pybdsm)\"" \
                icmd1b="select \"(Total_flux_prior-Total_flux_pybdsm)/abs(Total_flux_pybdsm)>1.0\"" \
                x1b="Total_flux_pybdsm*1e3" \
                y1b="Total_flux_prior*1e3" \
                leglabel1b="\footnotesize galfit>PyBDSM \ outliers" \
                \
                layer1c=mark \
                shape1c=x \
                size1c=2 \
                shading1c=aux \
                in1c="$output_dir/datatable_CrossMatched.fits" \
                icmd1c="sort -down \"(Total_flux_pybdsm-Total_flux_prior)/abs(Total_flux_prior)\"" \
                icmd1c="select \"(Total_flux_pybdsm-Total_flux_prior)/abs(Total_flux_prior)>1.0\"" \
                x1c="Total_flux_pybdsm*1e3" \
                y1c="Total_flux_prior*1e3" \
                leglabel1c="\footnotesize galfit<PyBDSM \ outliers" \
                \
                layer2b=label \
                in2b="$output_dir/datatable_CrossMatched.fits" \
                icmd2b="sort -down \"(Total_flux_prior-Total_flux_pybdsm)/abs(Total_flux_pybdsm)\"" \
                icmd2b="select \"(Total_flux_prior-Total_flux_pybdsm)/abs(Total_flux_pybdsm)>1.0\"" \
                x2b="Total_flux_pybdsm*1e3" \
                y2b="Total_flux_prior*1e3" \
                label2b="toHex(index+9)" \
                leglabel2b="\footnotesize galfit>PyBDSM \ outliers" \
                fontsize2b=11 \
                \
                layer2c=label \
                in2c="$output_dir/datatable_CrossMatched.fits" \
                icmd2c="sort -down \"(Total_flux_pybdsm-Total_flux_prior)/abs(Total_flux_prior)\"" \
                icmd2c="select \"(Total_flux_pybdsm-Total_flux_prior)/abs(Total_flux_prior)>1.0\"" \
                x2c="Total_flux_pybdsm*1e3" \
                y2c="Total_flux_prior*1e3" \
                label2c="index" \
                leglabel2c="\footnotesize galfit<PyBDSM \ outliers" \
                fontsize2c=11 \
                \
                layer9=function \
                fexpr9='(x)' \
                color9=black \
                antialias9=true \
                thick9=1 \
                leglabel9='\footnotesize 1:1' \
                \
                legend=true \
                legpos=0.01,0.99 \
                legborder=false \
                legopaque=false \
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
                ylabel="\large Peak \ flux \ from \ prior \ fitting \ [mJy]" \
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

if [[ ! -f "$output_dir/Plot_comparison_Maj_deconv.pdf" ]]; then
topcat -stilts plot2plane \
                in="$output_dir/datatable_CrossMatched.fits" \
                icmd="sort \"Peak_flux_pybdsm/E_Peak_flux_pybdsm\"" \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="Major \ axis \ FWHM \ from \ PyBDSM \ [arcsec]" \
                ylabel="Major \ axis \ FWHM \ from \ prior \ fitting \ [arcsec]" \
                xlog=true \
                ylog=true \
                xmin=0.01 xmax=20 ymin=0.01 ymax=20 \
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
                x1="Maj_deconv_pybdsm*3600.0" \
                y1="Maj_deconv_prior*3600.0" \
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
                out="$output_dir/Plot_comparison_Maj_deconv.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_comparison_Maj_deconv.pdf\"!"
fi

if [[ ! -f "$output_dir/Plot_comparison_Maj_deconv_normalized.pdf" ]]; then
topcat -stilts plot2plane \
                in="$output_dir/datatable_CrossMatched.fits" \
                icmd="sort \"Peak_flux_pybdsm/E_Peak_flux_pybdsm\"" \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="(Major \ axis / Beam \ size) \ from \ PyBDSM \ [arcsec]" \
                ylabel="(Major \ axis / Beam \ size) \ from \ prior \ fitting \ [arcsec]" \
                xlog=true \
                ylog=true \
                xmin=0.01 xmax=20 ymin=0.01 ymax=20 \
                \
                auxvisible=true auxlabel="Beam \ size" \
                auxfunc=log \
                aux="beam_major_pybdsm" \
                \
                layer1=mark \
                shape1=filled_circle \
                size1=2 \
                shading1=aux \
                leglabel1='\small Prior \ galfit \ vs \ PyBDSM' \
                x1="Maj_deconv_pybdsm*3600.0/beam_major_pybdsm" \
                y1="Maj_deconv_prior*3600.0/beam_major_prior" \
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
                out="$output_dir/Plot_comparison_Maj_deconv_normalized.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_comparison_Maj_deconv_normalized.pdf\"!"
fi

# 
# Histograms
# 
margin=(100 70 20 20) # left, bottom, right, top
if [[ ! -f "$output_dir/Plot_histogram_SNR_Peak_flux.pdf" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large S/N \ Peak \ flux" \
                ylabel="N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=7e3 \
                \
                in1="$cat_pybdsm" \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="+1.15" \
                leglabel1='PyBDSM' \
                x1="Peak_flux/E_Peak_flux" \
                \
                in2="$cat_prior" \
                icmd2="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="+1.15" \
                leglabel2='Prior \ fitting' \
                x2="Peak_flux/E_Peak_flux" \
                \
                legpos=0.08,0.94 \
                seq="2,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_histogram_SNR_Peak_flux.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_histogram_SNR_Peak_flux.pdf\"!"
fi

if [[ ! -f "$output_dir/Plot_histogram_Total_flux.pdf" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large Total \ flux \ [mJy]" \
                ylabel="N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=7e3 \
                \
                in1="$cat_pybdsm" \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="+1.15" \
                leglabel1='PyBDSM' \
                x1="Total_flux*1e3" \
                \
                in2="$cat_prior" \
                icmd2="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="+1.15" \
                leglabel2='Prior \ fitting' \
                x2="Total_flux*1e3" \
                \
                legpos=0.08,0.94 \
                seq="2,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_histogram_Total_flux.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_histogram_Total_flux.pdf\"!"
fi

if [[ ! -f "$output_dir/Plot_histogram_E_Total_flux.pdf" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large \sigma \ Total \ flux \ [mJy]" \
                ylabel="N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=7e3 \
                \
                in1="$cat_pybdsm" \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="+1.15" \
                leglabel1='PyBDSM' \
                x1="E_total_flux*1e3" \
                \
                in2="$cat_prior" \
                icmd2="select \"(Peak_flux>3.0*E_Peak_flux)\"" \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="+1.15" \
                leglabel2='Prior \ fitting' \
                x2="E_total_flux*1e3" \
                \
                legpos=0.08,0.94 \
                seq="2,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_histogram_E_Total_flux.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_histogram_E_Total_flux.pdf\"!"
fi

if [[ ! -f "$output_dir/Plot_histogram_Total_flux_common_sources.pdf" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\large Total \ flux \ [mJy]" \
                ylabel="N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=7e3 \
                \
                in1="datatable_CrossMatched.fits" \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="+1.15" \
                leglabel1='PyBDSM' \
                x1="Total_flux_pybdsm*1e3" \
                \
                in2="datatable_CrossMatched.fits" \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="+1.15" \
                leglabel2='Prior \ galfit' \
                x2="Total_flux_prior*1e3" \
                \
                legpos=0.08,0.94 \
                seq="2,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_histogram_Total_flux_common_sources.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"$output_dir/Plot_histogram_Total_flux_common_sources.pdf\"!"
fi

}


















# 20180925


if [[ ! -d "$output_dir/Plot_by_crossmatching_prior_to_pybdsm" ]]; then mkdir "$output_dir/Plot_by_crossmatching_prior_to_pybdsm"; fi
cp $output_dir/datatable_CrossMatched_prior_to_pybdsm.fits $output_dir/datatable_CrossMatched.fits
plot
mv *.pdf $output_dir/Plot_by_crossmatching_prior_to_pybdsm/



if [[ ! -d "$output_dir/Plot_by_crossmatching_pybdsm_to_prior" ]]; then mkdir "$output_dir/Plot_by_crossmatching_pybdsm_to_prior"; fi
cp $output_dir/datatable_CrossMatched_pybdsm_to_prior.fits $output_dir/datatable_CrossMatched.fits
plot
mv *.pdf $output_dir/Plot_by_crossmatching_pybdsm_to_prior/



if [[ ! -d "$output_dir/Plot_by_crossmatching_prior_to_pybdsm_best" ]]; then mkdir "$output_dir/Plot_by_crossmatching_prior_to_pybdsm_best"; fi
cp $output_dir/datatable_CrossMatched_prior_to_pybdsm_best.fits $output_dir/datatable_CrossMatched.fits
plot
mv *.pdf $output_dir/Plot_by_crossmatching_prior_to_pybdsm_best/



if [[ ! -d "$output_dir/Plot_by_crossmatching_pybdsm_to_prior_best" ]]; then mkdir "$output_dir/Plot_by_crossmatching_pybdsm_to_prior_best"; fi
cp $output_dir/datatable_CrossMatched_pybdsm_to_prior_best.fits $output_dir/datatable_CrossMatched.fits
plot
mv *.pdf $output_dir/Plot_by_crossmatching_pybdsm_to_prior_best/











