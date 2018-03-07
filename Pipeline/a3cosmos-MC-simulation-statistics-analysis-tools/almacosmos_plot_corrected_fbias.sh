#!/bin/bash
# 

margin=(100 70 100 20) # left, bottom, right, top

topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak} / rms\;noise" \
                ylabel="\Large Median \ of \ ((S_{in}-S_{out})/S_{in})" \
                xlog=true \
                ylog=false \
                xmin=1 xmax=500 ymin=-2 ymax=2 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_fbias.txt' \
                ifmt1=ascii \
                leglabel1='interp.' \
                x1='x1' \
                y1='fbias' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='0.0' \
                color3=black \
                antialias3=true \
                thick3=1 \
                leglabel3='Y=0' \
                \
                legpos=0.08,0.94 \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_fbias.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_fbias.pdf\"!"



topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{total,\;uncorr.}" \
                ylabel="\Large S_{total,\;corr.}" \
                xlog=true \
                ylog=true \
                \
                layer2=mark \
                shape2=filled_circle \
                size2=1 \
                shading2=aux \
                in2='datatable_applied_correction_fbias.txt' \
                icmd2="sort x2" \
                ifmt2=ascii \
                x2='S_out_uncorr' \
                y2='S_out_corr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                leglabel3='1:1' \
                \
                legend=false \
                seq="3,2" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_fbias_vs_uncorrected.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_fbias_vs_uncorrected.pdf\"!"



margin=(100 70 20 20) # left, bottom, right, top

if [[ -f "simu_data_input.txt" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{total}" \
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
                in1='datatable_applied_correction_fbias.txt' \
                ifmt1=ascii \
                leglabel1='uncorr' \
                x1="S_out_uncorr" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="-200" \
                in2='datatable_applied_correction_fbias.txt' \
                ifmt2=ascii \
                leglabel2='corr' \
                x2="S_out_corr" \
                \
                layer6=histogram \
                thick6=1 \
                barform6=semi_filled \
                color6='gold' \
                transparency6=0 \
                binsize6="-200" \
                in6='simu_data_input.txt' \
                ifmt6=ascii \
                leglabel6='true \ S_{in}' \
                x6="S_in" \
                \
                legpos=0.08,0.94 \
                seq='1,2,6' \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_fbias_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
else
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{total}" \
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
                in1='datatable_applied_correction_fbias.txt' \
                ifmt1=ascii \
                leglabel1='uncorr' \
                x1="S_out_uncorr" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=red \
                transparency2=0 \
                binsize2="-200" \
                in2='datatable_applied_correction_fbias.txt' \
                ifmt2=ascii \
                leglabel2='corr' \
                x2="S_out_corr" \
                \
                legpos=0.08,0.94 \
                seq='1,2' \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_fbias_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
fi

echo "Output to \"Plot_corrected_fbias_histogram.pdf\"!"



convert -density 240 -geometry x800 "Plot_corrected_fbias.pdf" "Plot_corrected_fbias.png"

convert -density 240 -geometry x800 "Plot_corrected_fbias_vs_uncorrected.pdf" "Plot_corrected_fbias_vs_uncorrected.png"

convert -density 240 -geometry x800 "Plot_corrected_fbias_histogram.pdf" "Plot_corrected_fbias_histogram.png"






