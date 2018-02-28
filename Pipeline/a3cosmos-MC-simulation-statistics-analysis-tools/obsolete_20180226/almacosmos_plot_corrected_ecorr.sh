#!/bin/bash
# 

margin=(80 60 80 20) # left, bottom, right, top

topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak} / rms\;noise" \
                ylabel="\Large 1/Scatter \ of \ ((S_{in}-S_{out})/S_{in})" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=500 ymin=1 ymax=500 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applying_correction_ecorr.txt' \
                ifmt1=ascii \
                leglabel1='interp.' \
                x1='x1' \
                y1='ecorr_from_interpolation' \
                \
                aux='x2' auxvisible=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                leglabel3='1:1' \
                \
                legpos=0.08,0.94 \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_ecorr_from_interpolation.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_from_interpolation.pdf\"!"



topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak} / rms\;noise" \
                ylabel="\Large 1/Scatter \ of \ ((S_{in}-S_{out})/S_{in})" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=500 ymin=1 ymax=500 \
                \
                layer2=mark \
                shape2=filled_circle \
                size2=1 \
                shading2=aux \
                in2='datatable_applying_correction_ecorr.txt' \
                ifmt2=ascii \
                leglabel2='function' \
                x2='x1' \
                y2='ecorr_from_function' \
                \
                aux='x2' auxvisible=true auxlabel="Maj_{source}/Maj_{beam}" auxmap=plasma \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                leglabel3='1:1' \
                \
                legpos=0.08,0.94 \
                seq="3,2" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_ecorr_from_function.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_from_function.pdf\"!"



# 
# combine datatable_applied_correction_ecorr.txt
# and datatable_applied_correction_fbias.txt
# 

#topcat -stilts tmatchn \
#                nin=2 \
#                in1='datatable_applied_correction_ecorr.txt' \
#                ifmt1=ascii \
#                values1="index" \
#                in2='datatable_applied_correction_fbias.txt' \
#                icmd2="keepcols \"S_out_uncorr S_out_corr\"" \
#                ifmt2=ascii \
#                values2="index" \
#                matcher=exact \
#                ofmt=ascii \
#                out='datatable_applied_correction_ecorr_and_fbias.txt'
#



# 
# Then plot histogram of S/N_{total}
# 

margin=(80 60 20 20) # left, bottom, right, top

if [[ -f "simu_data_input.txt" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S/N_{total}" \
                ylabel="\Large N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=1e5 \
                \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="-200" \
                in1='datatable_applied_correction_ecorr.txt' \
                ifmt1=ascii \
                leglabel1='uncorr' \
                x1="S_out_uncorr/e_S_out_uncorr" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="-200" \
                in2='datatable_applied_correction_ecorr.txt' \
                ifmt2=ascii \
                leglabel2='corr' \
                x2="S_out_corr/e_S_out_corr" \
                \
                layer6=histogram \
                thick6=1 \
                barform6=semi_filled \
                color6='gold' \
                transparency6=0 \
                binsize6="-200" \
                in6='simu_data_input.txt' \
                ifmt6=ascii \
                leglabel6='true \ S_{peak}/rms' \
                x6="S_peak/noise" \
                \
                legpos=0.08,0.94 \
                seq='1,2,6' \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
topcat -stilts tmatchn \
                nin=2 \
                in1='datatable_applied_correction_ecorr.txt' \
                ifmt1=ascii \
                values1="index" \
                in2='simu_data_input.txt' \
                ifmt2=ascii \
                values2="index" \
                matcher=exact \
                ocmd="keepcols \"S_out_uncorr S_out_corr e_S_out_uncorr e_S_out_corr S_in\"" \
                ofmt=ascii \
                out='datatable_applied_correction_ecorr_with_S_in.txt'
margin=(80 60 20 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large (S_{total,\,sim.}-S_{total,\,rec.}^{corr.})/\sigma_{S_{total,\,rec.}^{corr.}}" \
                ylabel="\Large N" \
                xlog=false xmin=-5 xmax=5 \
                ylog=true ymin=0.1 ymax=8 \
                \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="-100" \
                in1='datatable_applied_correction_ecorr_with_S_in.txt' \
                ifmt1=ascii \
                leglabel1='uncorrected' \
                x1="(S_in-S_out_uncorr)/e_S_out_uncorr" \
                normalise1="maximum" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="-100" \
                in2='datatable_applied_correction_ecorr_with_S_in.txt' \
                ifmt2=ascii \
                leglabel2='bias \ and \ error \ corrected' \
                x2="(S_in-S_out_corr)/e_S_out_corr" \
                normalise2="maximum" \
                \
                layer22=histogram \
                thick22=1 \
                barform22=semi_filled \
                color22=orange \
                transparency22=0 \
                binsize22="0.1" \
                in22="datatable_applied_correction_ecorr_with_S_in.txt" \
                ifmt22=ascii \
                leglabel22='only \ bias \ corrected' \
                x22="(S_in-S_out_corr)/(e_S_out_uncorr)" \
                normalise22="maximum" \
                \
                layer3=function \
                fexpr3='exp(-x*x/2)' \
                color3=black \
                antialias3=true \
                thick3=2 \
                leglabel3='Gaussian \ (\sigma=1)' \
                \
                legpos=0.08,0.94 \
                seq='1,2,22,3' \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_S_norm_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
else
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S/N_{total}" \
                ylabel="\Large N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=1e5 \
                \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1=blue \
                transparency1=0 \
                binsize1="-200" \
                in1='datatable_applied_correction_ecorr.txt' \
                ifmt1=ascii \
                leglabel1='uncorr' \
                x1="S_out_uncorr/e_S_out_uncorr" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="-200" \
                in2='datatable_applied_correction_ecorr.txt' \
                ifmt2=ascii \
                leglabel2='corr' \
                x2="S_out_corr/e_S_out_corr" \
                \
                legpos=0.08,0.94 \
                seq='1,2' \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
fi

echo "Output to \"Plot_corrected_ecorr_histogram.pdf\"!"



convert -density 150 "Plot_corrected_ecorr_from_interpolation.pdf" "Plot_corrected_ecorr_from_interpolation.png"

convert -density 150 "Plot_corrected_ecorr_from_function.pdf" "Plot_corrected_ecorr_from_function.png"

convert -density 150 "Plot_corrected_ecorr_histogram.pdf" "Plot_corrected_ecorr_histogram.png"







