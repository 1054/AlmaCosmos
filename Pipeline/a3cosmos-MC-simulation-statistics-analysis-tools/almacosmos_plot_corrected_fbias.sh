#!/bin/bash
# 
# 20190506: changed "xmax=100" --> "xmax=60"
# 

set -e


if [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"*"prior"* ]]; then
    Data_type="PHYS-GALFIT"
    SNR_peak="4.35"
    SNR_peak_cut="3.90"
    Theta_beam_cut="4.0"
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"*"blind"* ]] || [[ $(pwd) == *"Aravena"* ]]; then
    Data_type="PHYS-PYBDSF" # "PHYS-PYBDSM"
    SNR_peak="5.40"
    SNR_peak_cut="4.44" # cut the data point because PyBDSM thresh_pix = 4.0, also because the first bin we spline fbias is x1=4.44
    Theta_beam_cut="4.0"
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"*"GALFIT"* ]]; then
    Data_type="FULL-GALFIT"
    SNR_peak="4.35"
    SNR_peak_cut="3.0"
    Theta_beam_cut="999.0"
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"*"PyBDSM"* ]]; then
    Data_type="FULL-PYBDSF" # "FULL-PYBDSM"
    SNR_peak="5.40"
    SNR_peak_cut="4.0" # cut the data point because PyBDSM thresh_pix = 4.0
    Theta_beam_cut="999.0"
else
    echo "Error! Could not recognize the simulation and photometry methods!"
    exit 1
fi


margin=(100 70 100 20) # left, bottom, right, top

topcat -stilts plot2plane \
                xpix=500 ypix=300 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S/N_{peak}" \
                ylabel="\Large (S_{sim.}-S_{rec.})/S_{sim.}" \
                xlog=true \
                ylog=false \
                xmin=3 xmax=60 ymin=-1.25 ymax=1.25 \
                \
                layer1=mark \
                shape1=filled_circle \
                size1=1 \
                shading1=aux \
                in1='datatable_applied_correction_fbias.txt' \
                ifmt1=ascii \
                icmd1="sort x2" \
                icmd1="select \"(x1>= $SNR_peak_cut )\"" \
                icmd1="select \"(x2<= $Theta_beam_cut )\"" \
                leglabel1="\large $Data_type" \
                x1='x1' \
                y1='fbias' \
                \
                aux='x2' auxvisible=true auxmap=rainbow2 auxflip=true auxfunc=log auxmin=1.0 auxmax=4.0 auxlabel="\large \Theta_{beam}" \
                \
                layer3=function \
                fexpr3='0.0' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                layer2=function \
                axis2=Vertical \
                dash2="dash" \
                fexpr2="$SNR_peak" \
                color2=black \
                antialias2=true \
                thick2=1 \
                leglabel2="S/N_{peak}=$SNR_peak" \
                \
                legpos=0.98,0.98 \
                seq="1,2,3" \
                legseq="1,2" \
                legborder=false \
                legopaque=false \
                fontsize=18 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_fbias.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
                # 
                # 2018-05-31 removed the color bar because this figure will be shown with another figure sharing the color bar
                #aux='x2' auxvisible=true auxmap=rainbow2 auxflip=true auxfunc=log auxlabel="\Theta_{beam}" auxmin=1.0 auxmax=4.0 \

echo "Output to \"Plot_corrected_fbias.pdf\"!"



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
                in1='datatable_applied_correction_fbias.txt' \
                icmd1="sort x2" \
                ifmt1=ascii \
                x1='S_out_uncorr' \
                y1='S_out_corr' \
                leglabel1="$Data_type" \
                \
                aux='x2' auxvisible=true auxmap=rainbow2 auxflip=true auxfunc=log auxlabel="\large \Theta_{beam}" auxmin=1.0 auxmax=4.0 \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=true \
                legpos=0.04,0.98 \
                seq="1,3" \
                legseq="1" \
                legborder=false \
                legopaque=false \
                fontsize=18 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out='Plot_corrected_fbias_vs_uncorrected.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_fbias_vs_uncorrected.pdf\"!"
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
                legborder=false \
                legopaque=false \
                fontsize=18 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_fbias_histogram.pdf'
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
                fontsize=18 \
                legborder=false \
                legopaque=false \
                texttype=latex \
                omode=out \
                out='Plot_corrected_fbias_histogram.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
fi

echo "Output to \"Plot_corrected_fbias_histogram.pdf\"!"



convert -density 200 "Plot_corrected_fbias.pdf" "Plot_corrected_fbias.png"

convert -density 200 "Plot_corrected_fbias_vs_uncorrected.pdf" "Plot_corrected_fbias_vs_uncorrected.png"

convert -density 200 "Plot_corrected_fbias_histogram.pdf" "Plot_corrected_fbias_histogram.png"






