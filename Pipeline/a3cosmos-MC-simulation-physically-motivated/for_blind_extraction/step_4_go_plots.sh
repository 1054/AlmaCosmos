#!/bin/bash
# 

cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20171114_on_Phys_MC_Simulated_Images/check_simulated_image_fitting_statistics/

crossmatched_cat="CrossMatched/datatable_CrossMatched_all_entries.fits" # the output of step_1_*.sh
output_dir="CrossMatched"
do_overwrite=1

function check_input_dir() {
    local i=1
    for (( i=1; i<=$#; i++ )); do
        if [[ ! -d "${!i}" ]] && [[ ! -L "${!i}" ]]; then
            echo "Error! \"${!i}\" was not found!"
            exit 1
        fi
    done
}
function check_input_file() {
    local i=1
    for (( i=1; i<=$#; i++ )); do
        if [[ ! -f "${!i}" ]] && [[ ! -L "${!i}" ]]; then
            echo "Error! \"${!i}\" was not found!"
            exit 1
        fi
    done
}

check_input_file "$crossmatched_cat"

if [[ ! -d "$output_dir" ]]; then
    mkdir -p "$output_dir"
fi



# 
# plot flux-flux comparison, with data points colored by cat_2 SNR ftotal
# 
margin=(100 70 100 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{total,\,sim.}" \
                ylabel="\Large S_{total,\,rec.}" \
                xlog=true \
                ylog=true \
                \
                auxvisible=true auxlabel="SNR \ total \ (rec.)" \
                auxfunc=log \
                \
                layer_1=Mark \
                leglabel_1="flux comparison" \
                in_1="$crossmatched_cat" \
                icmd_1="select \"(flag_matched)\"" \
                icmd_1="sort \"(S_out/e_S_out)\"" \
                x_1="S_in" \
                y_1="S_out" \
                aux="(S_out/e_S_out)" \
                shading_1=aux \
                size_1=2 \
                \
                layer_3=function \
                fexpr_3='(x)' \
                color_3=black \
                antialias_3=true \
                thick_3=1 \
                leglabel_3='1:1' \
                \
                seq='_3,_1' \
                legend=false \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out="$output_dir/Plot_S_in_vs_S_out.pdf"



# 
# plot histograms
# 
margin=(80 50 20 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large SNR_{peak}" \
                ylabel="\Large N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=3e4 \
                \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1="cccccc" \
                transparency1=0 \
                binsize1="+1.10" \
                in1="$crossmatched_cat" \
                ifmt1=fits \
                icmd1="select \"(flag_matched || flag_nonmatched_spurious)\"" \
                leglabel1='all \ detections' \
                x1="S_peak/noise" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=orange \
                transparency2=0 \
                binsize2="+1.10" \
                in2="$crossmatched_cat" \
                ifmt2=fits \
                icmd2="select \"(flag_matched)\"" \
                leglabel2='detected \ and \ matched' \
                x2="S_peak/noise" \
                \
                layer3=histogram \
                thick3=1 \
                barform3=semi_filled \
                color3=blue \
                transparency3=0 \
                binsize3="+1.10" \
                in3="$crossmatched_cat" \
                ifmt3=fits \
                icmd3="select \"(flag_matched && ( abs(S_in-S_out)<(0.3*S_in) && abs(S_in-S_out)<(0.3*S_out) && S_peak>3.0*noise ))\"" \
                leglabel3='detected \ and \ flux \ accuracy \ < 30\%' \
                x3="S_peak/noise" \
                \
                layer4=histogram \
                thick4=1 \
                barform4=semi_filled \
                color4=magenta \
                transparency4=0 \
                binsize4="+1.10" \
                in4="$crossmatched_cat" \
                ifmt4=fits \
                icmd4="select \"(flag_nonmatched_spurious)\"" \
                leglabel4='spurious: no \ counterpart' \
                x4="S_peak/noise" \
                \
                legpos=0.08,0.94 \
                seq='1,2,3,4' \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_SNR_histogram_for_spurious_fraction.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html



# 
# plot histograms
# 
margin=(80 50 20 20) # left, bottom, right, top
binsize="+1.20" # "+1.10"
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{peak}/\sigma_{rms}" \
                ylabel="\Large N" \
                xlog=true \
                ylog=true \
                ymin=0.6 ymax=2e6 \
                \
                layer1=histogram \
                thick1=1 \
                barform1=semi_filled \
                color1="cccccc" \
                transparency1=0 \
                binsize1="$binsize" \
                in1="$crossmatched_cat" \
                ifmt1=fits \
                icmd1="select \"(flag_nonmatched_missed || flag_matched)\"" \
                leglabel1='all \ simulated' \
                x1="(S_in/((Maj_in*Min_in)/(Maj_beam*Min_beam)))/noise" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=orange \
                transparency2=0 \
                binsize2="$binsize" \
                in2="$crossmatched_cat" \
                ifmt2=fits \
                icmd2="select \"(flag_nonmatched_missed)\"" \
                leglabel2='simulated \ but \ not \ recovered' \
                x2="(S_in/((Maj_in*Min_in)/(Maj_beam*Min_beam)))/noise" \
                \
                layer3=histogram \
                thick3=1 \
                barform3=semi_filled \
                color3=green \
                transparency3=0.3 \
                binsize3="$binsize" \
                in3="$crossmatched_cat" \
                ifmt3=fits \
                icmd3="select \"(flag_matched)\"" \
                leglabel3='simulated \ and \ recovered' \
                x3="(S_in/((Maj_in*Min_in)/(Maj_beam*Min_beam)))/noise" \
                \
                layer4=histogram \
                thick4=1 \
                barform4=semi_filled \
                color4=blue \
                transparency4=0.4 \
                binsize4="$binsize" \
                in4="$crossmatched_cat" \
                ifmt4=fits \
                icmd4="select \"(flag_matched && ( abs(S_in-S_out)<(0.3*S_in) && abs(S_in-S_out)<(0.3*S_out) && S_peak>3.0*noise ))\"" \
                leglabel4='simulated \ and \ recovered \ and \ flux \ accuracy < 30\%' \
                x4="(S_in/((Maj_in*Min_in)/(Maj_beam*Min_beam)))/noise" \
                \
                legpos=0.08,0.94 \
                seq='1,2,3,4' \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_SNR_histogram_for_completeness.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html



#open 'Plot_SNR_histogram_for_spurious_fraction.pdf' 'Plot_SNR_histogram_for_completeness.pdf'





