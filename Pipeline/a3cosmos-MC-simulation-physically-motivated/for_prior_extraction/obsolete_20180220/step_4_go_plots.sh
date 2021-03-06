#!/bin/bash
# 

cd "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20170730_on_Phys_MC_Simulated_Images/"

crossmatched_cat="Statistics/datatable_CrossMatched_only_matches.fits" # the output of step_1_*.sh
output_dir="Statistics"

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


# Run topcat


# 
# plot scatter flux-flux comparison, with data points colored by cat_2 SNR ftotal
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
                auxvisible=true auxlabel="S/N \ total \ (rec.)" \
                auxfunc=log \
                \
                layer_1=Mark \
                leglabel_1="flux comparison" \
                in_1="$crossmatched_cat" \
                icmd_1="select (S_out/e_S_out>0.1)" \
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
                out="$output_dir/Plot_scatter_S_in_vs_S_out.pdf"

# 
# plot (S_in-S_out)/e_S_out histogram
# 
margin=(100 70 20 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large (S_{sim.}-S_{rec.})/\sigma_{S_{rec.}}" \
                ylabel="\Large N" \
                xlog=false \
                ylog=true \
                xmin=-5 xmax=5 \
                \
                layer_1=histogram \
                thick_1=1 \
                barform_1=semi_filled \
                color_1=blue \
                transparency_1=0 \
                in_1="$crossmatched_cat" \
                x_1="(S_in-S_out)/(e_S_out)" \
                \
                layer_3=function \
                fexpr_3='(2e4*exp(-x*x/2.0))' \
                color_3=black \
                antialias_3=true \
                thick_3=1 \
                leglabel_3='Gaussian' \
                \
                seq='_3,_1' \
                legend=false \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out="$output_dir/Plot_histogram_S_in_S_out_e_S_out.pdf"

# 
# plot scatter (S_in-S_out)/S_in vs S_in/noise
# 
margin=(100 70 100 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{total,\,sim.}/{\footnotesize rms\,noise}" \
                ylabel="\Large (S_{total,\,sim.}-S_{total,\,rec.})/S_{total,\,sim.}" \
                xlog=true \
                ylog=false ymin=-5 ymax=5 \
                \
                auxvisible=true auxlabel="S/N \ total \ (rec.)" \
                auxfunc=log \
                \
                layer_1=Mark \
                leglabel_1="flux comparison" \
                in_1="$crossmatched_cat" \
                icmd_1="select (S_out/e_S_out>0.1)" \
                x_1="S_in/noise" \
                y_1="(S_in-S_out)/S_in" \
                aux="(S_out/e_S_out)" \
                shading_1=aux \
                size_1=2 \
                \
                layer_3=function \
                fexpr_3='(0.0)' \
                color_3=black \
                antialias_3=true \
                thick_3=1 \
                leglabel_3='Y=0' \
                \
                seq='_3,_1' \
                legend=false \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out="$output_dir/Plot_scatter_rel_S_diff_vs_S_in.pdf"

# 
# plot scatter (S_in-S_out)/S_out vs S_out/noise
# 
margin=(100 70 100 20) # left, bottom, right, top
topcat -stilts plot2plane \
                xpix=500 ypix=400 \
                insets="${margin[3]},${margin[0]},${margin[1]},${margin[2]}" \
                xlabel="\Large S_{total,\,rec.}/{\footnotesize rms\,noise}" \
                ylabel="\Large (S_{total,\,sim.}-S_{total,\,rec.})/S_{total,\,rec.}" \
                xlog=true \
                ylog=false ymin=-5 ymax=5 \
                \
                auxvisible=true auxlabel="S/N \ total \ (rec.)" \
                auxfunc=log \
                \
                layer_1=Mark \
                leglabel_1="flux comparison" \
                in_1="$crossmatched_cat" \
                icmd_1="select (S_out/e_S_out>0.1)" \
                x_1="S_out/noise" \
                y_1="(S_in-S_out)/S_out" \
                aux="(S_out/e_S_out)" \
                shading_1=aux \
                size_1=2 \
                \
                layer_3=function \
                fexpr_3='(0.0)' \
                color_3=black \
                antialias_3=true \
                thick_3=1 \
                leglabel_3='Y=0' \
                \
                seq='_3,_1' \
                legend=false \
                fontsize=16 \
                texttype=latex \
                omode=out \
                out="$output_dir/Plot_scatter_rel_S_diff_vs_S_out.pdf"






