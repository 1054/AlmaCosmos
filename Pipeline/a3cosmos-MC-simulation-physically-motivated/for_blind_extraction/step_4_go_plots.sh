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
                icmd_1="addcol Xf -after \"flux\" \"(flux)\"" \
                icmd_1="addcol f -after \"Total_flux_fit\" \"(Total_flux_fit*1e3)\"" \
                icmd_1="addcol df -after \"f\" \"(E_Total_flux_fit*1e3)\"" \
                icmd_1="sort \"(f/df)\"" \
                x_1="Xf" \
                y_1="f" \
                aux="(f/df)" \
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
                out="$output_dir/Plot_ftotal_scatter.pdf"










# 
# compute S/N_peak of all detections
if [[ ! -f "$output_dir/datatable_AllDetections.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_matched || flag_nonmatched_spurious)\"" \
                cmd="addcol SNR_peak \"(Peak_flux_fit/Isl_rms_fit)\"" \
                cmd="keepcols \"SNR_peak\"" \
                ofmt=ascii \
                out="$output_dir/datatable_AllDetections.SNR_peak.txt"
fi

# 
# get the SNR_peak of the detected sources that do not have simulated source counterpart -- spurious (no counterpart)
if [[ ! -f "$output_dir/datatable_AllDetections.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_nonmatched_spurious)\"" \
                cmd="addcol SNR_peak \"(Peak_flux_fit/Isl_rms_fit)\"" \
                cmd="keepcols \"SNR_peak\"" \
                ofmt=ascii \
                out="$output_dir/datatable_NotSimulated.spurious.SNR_peak.txt"
fi

# 
# get the SNR_peak of the detected sources that do have simulated source counterpart (but could be both good or flux-boosted)
if [[ ! -f "$output_dir/datatable_Matched.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_matched)\"" \
                cmd="addcol SNR_peak \"(Peak_flux_fit/Isl_rms_fit)\"" \
                cmd="keepcols \"SNR_peak\"" \
                ofmt=ascii \
                out="$output_dir/datatable_Matched.SNR_peak.txt"
fi

# 
# get the SNR_peak of the detected sources that do have simulated source counterpart and have good flux measurements
if [[ ! -f "$output_dir/datatable_Matched.good.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_matched)\"" \
                cmd="addcol Xf -after flux \"(flux)\"" \
                cmd="addcol f -after Total_flux_fit \"(Total_flux_fit*1e3)\"" \
                cmd="select \"(fpeak>=3.0*rms && abs(Xf-f)<0.3*Xf && abs(Xf-f)<0.3*f)\"" \
                cmd="addcol SNR_peak \"(Peak_flux_fit/Isl_rms_fit)\"" \
                cmd="keepcols \"SNR_peak\"" \
                ofmt=ascii \
                out="$output_dir/datatable_Matched.good.SNR_peak.txt"
fi

# 
# get the SNR_peak of the detected sources that do have simulated source counterpart but do not have good flux measurements -- spurious (flux boosted)
if [[ ! -f "$output_dir/datatable_Matched.spurious.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_matched)\"" \
                cmd="addcol Xf -after flux \"(flux)\"" \
                cmd="addcol f -after Total_flux_fit \"(Total_flux_fit*1e3)\"" \
                cmd="select \"!(fpeak>=3.0*rms && abs(Xf-f)<0.3*Xf && abs(Xf-f)<0.3*f)\"" \
                cmd="addcol SNR_peak \"(Peak_flux_fit/Isl_rms_fit)\"" \
                cmd="keepcols \"SNR_peak\"" \
                ofmt=ascii \
                out="$output_dir/datatable_Matched.spurious.SNR_peak.txt"
fi

# 
# get the SNR_peak of all spurious sources, including non-detected sources and detected sources which have wrong boosted fluxes
if [[ ! -f "$output_dir/datatable_AllSpurious.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
    cat "$output_dir/datatable_NotSimulated.spurious.SNR_peak.txt" > "$output_dir/datatable_AllSpurious.SNR_peak.txt"
    cat "$output_dir/datatable_Matched.spurious.SNR_peak.txt" | grep -v '^#' >> "$output_dir/datatable_AllSpurious.SNR_peak.txt"
fi


# 
# plot histograms
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
                in1="$output_dir/datatable_AllDetections.SNR_peak.txt" \
                ifmt1=ascii \
                leglabel1='all \ detections' \
                x1="SNR_peak" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=blue \
                transparency2=0 \
                binsize2="+1.10" \
                in2="$output_dir/datatable_Matched.good.SNR_peak.txt" \
                ifmt2=ascii \
                leglabel2='detected \ and \ flux \ accuracy \ < 30\%' \
                x2="SNR_peak" \
                \
                layer3=histogram \
                thick3=1 \
                barform3=semi_filled \
                color3=red \
                transparency3=0 \
                binsize3="+1.10" \
                in3="$output_dir/datatable_AllSpurious.SNR_peak.txt" \
                ifmt3=ascii \
                leglabel3='spurious: flux \ boosted + no \ counterpart' \
                x3="SNR_peak" \
                \
                layer4=histogram \
                thick4=1 \
                barform4=semi_filled \
                color4=yellow \
                transparency4=0 \
                binsize4="+1.10" \
                in4="$output_dir/datatable_NotSimulated.spurious.SNR_peak.txt" \
                ifmt4=ascii \
                leglabel4='spurious: no \ counterpart' \
                x4="SNR_peak" \
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
                # omode=swing












# 
# simulated sources that are not blindly extracted
if [[ ! -f "$output_dir/datatable_NotRecovered.missed.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
topcat -stilts tpipe \
                in="$crossmatched_cat" \
                ifmt=fits \
                cmd="select \"(flag_nonmatched_missed)\"" \
                cmd="addcol SNR_peak \"fpeak/rms\"" \
                cmd="keepcols \"SNR_peak\"" \
                ofmt=ascii \
                out="$output_dir/datatable_NotRecovered.missed.SNR_peak.txt"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
fi

# 
# get the SNR_peak of all simulated sources, including non-detected but simulated sources and all detected sources which have cross-matched to a simulated source. 
if [[ ! -f "$output_dir/datatable_AllSimulated.SNR_peak.txt" ]] || [[ $do_overwrite -eq 1 ]]; then
    cat "$output_dir/datatable_NotRecovered.missed.SNR_peak.txt" > "$output_dir/datatable_AllSimulated.SNR_peak.txt"
    cat "$output_dir/datatable_Matched.SNR_peak.txt" | grep -v '^#' >> "$output_dir/datatable_AllSimulated.SNR_peak.txt"
fi


# 
# plot histograms
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
                in1="$output_dir/datatable_AllSimulated.SNR_peak.txt" \
                ifmt1=ascii \
                leglabel1='all \ simulated' \
                x1="SNR_peak" \
                \
                layer3=histogram \
                thick3=1 \
                barform3=semi_filled \
                color3=orange \
                transparency3=0 \
                binsize3="$binsize" \
                in3="$output_dir/datatable_NotRecovered.missed.SNR_peak.txt" \
                ifmt3=ascii \
                leglabel3='simulated \ but \ not \ recovered' \
                x3="SNR_peak" \
                \
                layer2=histogram \
                thick2=1 \
                barform2=semi_filled \
                color2=green \
                transparency2=0.3 \
                binsize2="$binsize" \
                in2="$output_dir/datatable_Matched.SNR_peak.txt" \
                ifmt2=ascii \
                leglabel2='simulated \ and \ recovered' \
                x2="SNR_peak" \
                \
                layer4=histogram \
                thick4=1 \
                barform4=semi_filled \
                color4=blue \
                transparency4=0.4 \
                binsize4="$binsize" \
                in4="$output_dir/datatable_Matched.good.SNR_peak.txt" \
                ifmt4=ascii \
                leglabel4='simulated \ and \ recovered \ and \ flux \ accuracy < 30\%' \
                x4="SNR_peak" \
                \
                legpos=0.08,0.94 \
                seq='1,3,2,4' \
                fontsize=16 \
                texttype=latex \
                aspect=1.0 \
                omode=out \
                out="$output_dir/Plot_SNR_histogram_for_completeness.pdf"
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-usage.html
                # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/plot2plane-examples.html
                # omode=swing




open 'Plot_SNR_histogram_for_spurious_fraction.pdf' 'Plot_SNR_histogram_for_completeness.pdf'





