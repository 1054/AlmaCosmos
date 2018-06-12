#!/bin/bash
# 
# 2018-05-08: fbias2 is defined as cell_noi_mean = (S_in-S_out)/noise
# 
# 

if [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"*"prior"* ]]; then
    Data_type="PHYS-GALFIT"
    SNR_peak="3.77"
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"*"blind"* ]] || [[ $(pwd) == *"Aravena"* ]]; then
    Data_type="PHYS-PYBDSM"
    SNR_peak="5.35"
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"*"GALFIT"* ]]; then
    Data_type="FULL-GALFIT"
    SNR_peak="3.77"
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"*"PyBDSM"* ]]; then
    Data_type="FULL-PYBDSM"
    SNR_peak="5.35"
fi


margin=(100 70 100 20) # left, bottom, right, top

topcat -stilts plot2plane \
                xpix=500 ypix=300 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak} / rms\;noise" \
                ylabel="\Large (S_{sim.}-S_{rec.})/rms\;noise" \
                xlog=true \
                ylog=false \
                xmin=1 xmax=500 ymin=-2.25 ymax=2.25 \
                \
                layer1=mark \
                shape1=filled_circle \
                size1=1 \
                shading1=aux \
                in1='datatable_applied_correction_fbias2.txt' \
                ifmt1=ascii \
                icmd1="sort x2" \
                leglabel1="$Data_type" \
                x1='x1' \
                y1='fbias2' \
                \
                aux='x2' auxvisible=true auxmap=rainbow2 auxflip=true auxfunc=log auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" auxmin=1.0 auxmax=4.0 \
                \
                layer3=function \
                fexpr3='0.0' \
                color3=black \
                antialias3=true \
                thick3=1 \
                leglabel3='\footnotesize Y=0' \
                \
                layer2=function \
                axis2=Vertical \
                dash2="dash" \
                fexpr2="$SNR_peak" \
                color2=black \
                antialias2=true \
                thick2=1 \
                leglabel2="\footnotesize S/N_{peak}=$SNR_peak" \
                \
                legpos=0.04,0.98 \
                seq="1,2,3" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_fbias2.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_fbias2.pdf\"!"



topcat -stilts plot2plane \
                xpix=500 ypix=300 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{rec.,\;uncorr.}" \
                ylabel="\Large S_{rec.,\;corr.}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=filled_circle \
                size1=1 \
                shading1=aux \
                in1='datatable_applied_correction_fbias2.txt' \
                icmd1="sort x2" \
                ifmt1=ascii \
                x1='S_out_uncorr' \
                y1='S_out_corr' \
                leglabel1="$Data_type" \
                \
                aux='x2' auxvisible=true auxmap=rainbow2 auxflip=true auxfunc=log auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" auxmin=1.0 auxmax=4.0 \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                leglabel3='\footnotesize 1:1' \
                \
                legend=true \
                legpos=0.04,0.98 \
                seq="1,3" \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_fbias2_vs_uncorrected.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_fbias2_vs_uncorrected.pdf\"!"
#exit



margin=(100 70 20 20) # left, bottom, right, top

if [[ -f "simu_data_input.txt" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=300 \
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
                in1='datatable_applied_correction_fbias2.txt' \
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
                in2='datatable_applied_correction_fbias2.txt' \
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
                out='Plot_corrected_fbias2_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
else
topcat -stilts plot2plane \
                xpix=500 ypix=300 \
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
                in1='datatable_applied_correction_fbias2.txt' \
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
                in2='datatable_applied_correction_fbias2.txt' \
                ifmt2=ascii \
                leglabel2='corr' \
                x2="S_out_corr" \
                \
                legpos=0.08,0.94 \
                seq='1,2' \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_fbias2_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
fi

echo "Output to \"Plot_corrected_fbias2_histogram.pdf\"!"



convert -density 240 -geometry x800 -background white "Plot_corrected_fbias2.pdf" "Plot_corrected_fbias2.png"

convert -density 240 -geometry x800 -background white "Plot_corrected_fbias2_vs_uncorrected.pdf" "Plot_corrected_fbias2_vs_uncorrected.png"

convert -density 240 -geometry x800 -background white "Plot_corrected_fbias2_histogram.pdf" "Plot_corrected_fbias2_histogram.png"






