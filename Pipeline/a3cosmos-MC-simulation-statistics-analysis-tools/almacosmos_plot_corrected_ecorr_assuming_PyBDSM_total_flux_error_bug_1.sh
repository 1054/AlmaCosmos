#!/bin/bash
# 

margin=(100 70 100 20) # left, bottom, right, top

topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak} / rms \; noise" \
                ylabel="\Large Scatter \ of \ ((S_{in}-S_{out}) / rms \; noise)" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=1000 ymin=1 ymax=1000 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applying_correction_ecorr.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='x1' \
                y1='ecorr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr.pdf" "Plot_corrected_ecorr.png"


if [[ ! -f 'datatable_applied_correction_ecorr_with_S_peak.txt' ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1='datatable_applied_correction_ecorr.txt' ifmt1=ascii \
                in2='../simu_data_input.txt' ifmt2=ascii icmd2="keepcols \"S_peak noise Maj_out Min_out Maj_beam Min_beam image_file_STR simu_name_STR\"" \
                values1='index' values2='index' \
                suffix1="" \
                matcher=exact multimode=pairs iref=1 \
                out='datatable_applied_correction_ecorr_with_S_peak.txt'
fi


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{out} / \sigma_{S_{out,\,uncorr.}}" \
                ylabel="\Large S_{out} / \sigma_{S_{out,\,corr.}}" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=1000 ymin=1 ymax=1000 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_S_peak.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='S_out/(e_S_out_uncorr*(S_out/S_peak))' \
                y1='S_out/e_S_out_corr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_SNR.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_SNR.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_SNR.pdf" "Plot_corrected_ecorr_SNR.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large \sigma_{S_{out,\,uncorr.}}" \
                ylabel="\Large \sigma_{S_{out,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_S_peak.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='(e_S_out_uncorr*(S_out/S_peak))' \
                y1='e_S_out_corr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_vs_uncorrected_ecorr.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_vs_uncorrected_ecorr.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_vs_uncorrected_ecorr.pdf" "Plot_corrected_ecorr_vs_uncorrected_ecorr.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large \sigma_{S_{out,\,uncorr.}}" \
                ylabel="\Large \sigma_{S_{out,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_S_peak.txt' \
                ifmt1=ascii \
                icmd1='sort (Min_out/Maj_beam)' \
                x1='e_S_out_uncorr*(S_out/S_peak)' \
                y1='e_S_out_corr' \
                \
                aux='(Min_out/Maj_beam)' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Min_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Min_out.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Min_out.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Min_out.pdf" "Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Min_out.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large \sigma_{S_{out,\,uncorr.}}" \
                ylabel="\Large \sigma_{S_{out,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_S_peak.txt' \
                ifmt1=ascii \
                icmd1='sort (S_peak/noise)' \
                x1='e_S_out_uncorr*(S_out/S_peak)' \
                y1='e_S_out_corr' \
                \
                aux='(S_peak/noise)' auxvisible=true auxmap=rdbu auxflip=true auxfunc=log auxlabel="S_{peak}/{noise}" \
                \
                layer3=function \
                fexpr3='(x)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_S_peak.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_S_peak.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_S_peak.pdf" "Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_S_peak.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{out} / \sigma_{S_{out,\,uncorr.}}" \
                ylabel="\Large (S/N_{out,\,corr.}) / (S/N_{out,\,uncorr.})" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=1000 ymin=0.1 ymax=50 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_S_peak.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='S_out/(e_S_out_uncorr*(S_out/S_peak))' \
                y1='(S_out/e_S_out_corr)/(S_out/(e_S_out_uncorr*(S_out/S_peak)))' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
                \
                layer3=function \
                fexpr3='(1)' \
                color3=black \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="3,1" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_SNR_ratio.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html

echo "Output to \"Plot_corrected_ecorr_SNR_ratio.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_SNR_ratio.pdf" "Plot_corrected_ecorr_SNR_ratio.png"












