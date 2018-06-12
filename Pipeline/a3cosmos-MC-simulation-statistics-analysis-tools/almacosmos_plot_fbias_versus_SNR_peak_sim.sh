#!/bin/bash
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

if [[ ! -f "datatable_applied_correction_fbias_versus_SNR_peak_sim.txt" ]]; then
    topcat -stilts tmatchn nin=3 \
                            in1="datatable_applied_correction_fbias.txt" ifmt1=ascii \
                            in2="../simu_data_input_corrected.txt" ifmt2=ascii icmd2="keepcols \"S_in noise\"" \
                            in3="../simu_data_input.convolved_simulated_sizes.txt" ifmt3=ascii \
                            icmd3="addcol source_area_per_beam \"(Maj_in_convol*Min_in_convol)/(Maj_beam*Min_beam)\"" \
                            icmd3="keepcols \"source_area_per_beam\"" \
                            matcher=exact values1=index values2=index values3=index \
                            ocmd="addcol S_peak_sim \"S_in/source_area_per_beam\"" \
                            ocmd="addcol SNR_peak_sim \"S_peak_sim/noise\"" \
                            out="datatable_applied_correction_fbias_versus_SNR_peak_sim.txt" ofmt=ascii
fi

margin=(100 70 100 20) # left, bottom, right, top

topcat -stilts plot2plane \
                xpix=500 ypix=300 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak} / rms\;noise" \
                ylabel="\Large (S_{sim.}-S_{rec.})/S_{sim.}" \
                xlog=true \
                ylog=false \
                xmin=1 xmax=500 ymin=-1.25 ymax=1.25 \
                \
                layer1=mark \
                shape1=filled_circle \
                size1=1 \
                shading1=aux \
                in1='datatable_applied_correction_fbias_versus_SNR_peak_sim.txt' \
                ifmt1=ascii \
                icmd1="sort x2" \
                leglabel1="$Data_type" \
                x1='SNR_peak_sim' \
                y1='fbias' \
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
                out='Plot_corrected_fbias_versus_SNR_peak_sim.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_fbias_versus_SNR_peak_sim.pdf\"!"




convert -density 240 -geometry x800 "Plot_corrected_fbias_versus_SNR_peak_sim.pdf" "Plot_corrected_fbias_versus_SNR_peak_sim.png"







