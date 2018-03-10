#!/bin/bash
# 

margin=(100 70 100 20) # left, bottom, right, top

if [[ ! -f "Plot_corrected_ecorr.png" ]]; then
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large x1 = S_{peak} / rms \; noise" \
                ylabel="\Large Scatter \ of \ ((S_{in}-S_{out}) / rms \; noise)" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=1000 ymin=1 ymax=1000 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='x1' \
                y1='ecorr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" \
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
fi


if [[ ! -f 'datatable_applied_correction_ecorr_with_more_columns.txt' ]]; then
topcat -stilts tmatchn \
                nin=2 \
                in1='datatable_applied_correction_ecorr.txt' ifmt1=ascii \
                in2='../simu_data_input.txt' ifmt2=ascii icmd2="keepcols \"S_peak noise Maj_out Min_out Maj_beam Min_beam image_file_STR simu_name_STR\"" \
                values1='index' values2='index' \
                suffix1="" \
                matcher=exact multimode=pairs iref=1 \
                out='datatable_applied_correction_ecorr_with_more_columns.txt'
fi


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{out} / \sigma_{S_{total,\,C97}}" \
                ylabel="\Large S_{out} / \sigma_{S_{total,\,corr.}}" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=1000 ymin=1 ymax=1000 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='S_out/e_S_out_uncorr' \
                y1='S_out/e_S_out_corr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" \
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
                xlabel="\Large S_{out} / \sigma_{S_{total,\,C97}}" \
                ylabel="\Large (S/N_{out,\,corr.}) / (S/N_{out,\,uncorr.})" \
                xlog=true \
                ylog=true \
                xmin=1 xmax=1000 ymin=0.01 ymax=50 \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='S_out/e_S_out_uncorr' \
                y1='(S_out/e_S_out_corr)/(S_out/e_S_out_uncorr)' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" \
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


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large \sigma_{S_{total,\,C97}}" \
                ylabel="\Large \sigma_{S_{total,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='e_S_out_uncorr' \
                y1='e_S_out_corr' \
                \
                aux='x2' auxvisible=true auxmap=rdbu auxflip=true auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" \
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
                xlabel="\Large \sigma_{S_{total,\,C97}}" \
                ylabel="\Large \sigma_{S_{total,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort (Maj_out/Maj_beam)' \
                x1='e_S_out_uncorr' \
                y1='e_S_out_corr' \
                \
                aux='(Maj_out/Maj_beam)' auxvisible=true auxmap=rdbu auxflip=true auxlabel="Maj_{source}/Maj_{beam}" \
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
                out='Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Maj_out.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Maj_out.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Maj_out.pdf" "Plot_corrected_ecorr_vs_uncorrected_ecorr_colored_by_Maj_out.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large \sigma_{S_{total,\,C97}}" \
                ylabel="\Large \sigma_{S_{total,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort (Min_out/Maj_beam)' \
                x1='e_S_out_uncorr' \
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
                xlabel="\Large \sigma_{S_{total,\,C97}}" \
                ylabel="\Large \sigma_{S_{total,\,corr.}}" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort (S_peak/noise)' \
                x1='e_S_out_uncorr' \
                y1='e_S_out_corr' \
                \
                aux='(S_peak/noise)' auxvisible=true auxmap=rdbu auxflip=true auxfunc=log auxlabel="x1 = S_{peak}/{noise}" \
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
                xlabel="\Large x2 = sqrt(Area_{source}/Area_{beam})" \
                ylabel="\Large (\sigma_{S_{total,\,corr.}}) / (rms \ noise)" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x1' \
                x1='x2' \
                y1='(e_S_out_corr/noise)' \
                \
                aux='x1' auxvisible=true auxfunc=log auxmap=rdbu auxflip=true auxlabel="x1 = S_{peak}/(rms \ noise)" \
                \
                layer3=function \
                fexpr3='sqrt(8*pow(x,2)/(pow((1+(1/pow(x,2))),1.5)*pow((1+(1/pow(x,2))),1.5)) + 8/(pow((1+(1/pow(x,2))),2.5)*pow((1+(1/pow(x,2))),0.5)) + 8/(pow((1+(1/pow(x,2))),0.5)*pow((1+(1/pow(x,2))),2.5)) )' \
                color3=red \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="1,3" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_corrected_ecorr_vs_x2_colored_by_x1.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"Plot_corrected_ecorr_vs_x2_colored_by_x1.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_vs_x2_colored_by_x1.pdf" "Plot_corrected_ecorr_vs_x2_colored_by_x1.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large x2 = sqrt(Area_{source}/Area_{beam})" \
                ylabel="\Large (\sigma_{S_{total,\,C97}}) / (rms \ noise)" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x1' \
                x1='x2' \
                y1='(e_S_out_uncorr/noise)' \
                \
                aux='x1' auxvisible=true auxfunc=log auxmap=rdbu auxflip=true auxlabel="x1 = S_{peak}/(rms \ noise)" \
                \
                layer3=function \
                fexpr3='sqrt(8*pow(x,2)/(pow((1+(1/pow(x,2))),1.5)*pow((1+(1/pow(x,2))),1.5)) + 8/(pow((1+(1/pow(x,2))),2.5)*pow((1+(1/pow(x,2))),0.5)) + 8/(pow((1+(1/pow(x,2))),0.5)*pow((1+(1/pow(x,2))),2.5)) )' \
                color3=red \
                antialias3=true \
                thick3=1 \
                \
                legend=false \
                seq="1,3" \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out='Plot_uncorrected_ecorr_vs_x2_colored_by_x1.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"Plot_uncorrected_ecorr_vs_x2_colored_by_x1.pdf\"!"
convert -density 240 -geometry x800 "Plot_uncorrected_ecorr_vs_x2_colored_by_x1.pdf" "Plot_uncorrected_ecorr_vs_x2_colored_by_x1.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large x1 = S_{peak}/(rms \ noise)" \
                ylabel="\Large (\sigma_{S_{total,\,corr.}}) / (rms \ noise)" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='x1' \
                y1='(e_S_out_corr/noise)' \
                \
                aux='x2' auxvisible=true auxfunc=log auxmap=rdbu auxflip=true auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" \
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
                out='Plot_corrected_ecorr_vs_x1_colored_by_x2.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"Plot_corrected_ecorr_vs_x1_colored_by_x2.pdf\"!"
convert -density 240 -geometry x800 "Plot_corrected_ecorr_vs_x1_colored_by_x2.pdf" "Plot_corrected_ecorr_vs_x1_colored_by_x2.png"


topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large x1 = S_{peak}/(rms \ noise)" \
                ylabel="\Large (\sigma_{S_{total,\,C97}}) / (rms \ noise)" \
                xlog=true \
                ylog=true \
                \
                layer1=mark \
                shape1=open_circle \
                shading1=aux \
                in1='datatable_applied_correction_ecorr_with_more_columns.txt' \
                ifmt1=ascii \
                icmd1='sort x2' \
                x1='x1' \
                y1='(e_S_out_uncorr/noise)' \
                \
                aux='x2' auxvisible=true auxfunc=log auxmap=rdbu auxflip=true auxlabel="x2 = sqrt(Area_{source}/Area_{beam})" \
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
                out='Plot_uncorrected_ecorr_vs_x1_colored_by_x2.pdf'
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
echo "Output to \"Plot_uncorrected_ecorr_vs_x1_colored_by_x2.pdf\"!"
convert -density 240 -geometry x800 "Plot_uncorrected_ecorr_vs_x1_colored_by_x2.pdf" "Plot_uncorrected_ecorr_vs_x1_colored_by_x2.png"







exit


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

margin=(100 70 20 20) # left, bottom, right, top

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
                x1="S_out/e_S_out_uncorr" \
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
                x2="S_out/e_S_out_corr" \
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

convert -density 240 -geometry x800 "Plot_corrected_ecorr_histogram.pdf" "Plot_corrected_ecorr_histogram.png"







