#!/bin/bash
# 




# Setup input datatable_sim_rec

if [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"* ]] && [[ $(pwd) == *"PyBDSM"* ]]; then

     datatable_sim_rec="datatable_CrossMatched/datatable_CrossMatched_all_entries_filtered_in_PB.fits.gz"
     
     echo "Error! We do not analyze completeness in bins of source size for PHYS-PYBDSM!"
     exit 255
     
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"* ]] && [[ $(pwd) == *"GALFIT"* ]]; then

     datatable_sim_rec="datatable_CrossMatched/datatable_CrossMatched_all_entries_filtered_in_PB.fits.gz"
     
     echo "Error! We do not analyze completeness in bins of source size for PHYS-GALFIT!"
     exit 255
     
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"* ]] && [[ $(pwd) == *"PyBDSM"* ]]; then
     
     datatable_sim_rec="datatable_CrossMatched/concat_sim_rec_data_table_with_convolved_sizes_with_flag_matched.fits.gz"

elif [[ $(pwd) == *"Monte_Carlo_Simulation_Parameter_Sampled"* ]] && [[ $(pwd) == *"GALFIT"* ]]; then
     
     datatable_sim_rec="datatable_CrossMatched/datatable_CrossMatched_filtered_with_flag_matched.fits.gz"
     
fi

if [[ -z "$datatable_sim_rec" ]]; then
     echo "Error! Could not determine which simulation it is from the current working directory \"$(pwd)\"!"
     exit 255
fi

if [[ ! -f "$datatable_sim_rec" ]]; then
     echo "Error! \"$datatable_sim_rec\" was not found!"
     exit 255
fi




# Check "Completeness_ref"

if [[ ! -f "Completeness_ref.tar.gz" ]] && [[ ! -d "Completeness_ref" ]]; then
     echo "Error! \"Completeness_ref\" or \"Completeness_ref.tar.gz\" was not found! Please calculate the completeness of PHYS-PYBDSM then copy the result \"Completeness\" directory as \"Completeness_ref\" here!"
     exit 255
fi




# Prepare output directory

output_dirname="Completeness_in_bins_of_source_sizes"
current_datetime=$(date +"%Y%m%d.%Hh%Mm%Ss")

if [[ -d "$output_dirname" ]]; then
     backup_dirname="$output_dirname"."$current_datetime"
     echo "Found existing \"$output_dirname\"! Backing it up as \"$backup_dirname\"!"
     mv "$output_dirname" "$backup_dirname"
fi

mkdir "$output_dirname"




#  Copy input "datatable_sim_rec" and "Completeness_ref"

if [[ "$datatable_sim_rec" == *".txt" ]]; then
     topcat -stilts tpipe in="$datatable_sim_rec" ifmt=ascii out="$output_dirname/datatable_sim_rec.fits"
else
     topcat -stilts tpipe in="$datatable_sim_rec" out="$output_dirname/datatable_sim_rec.fits"
fi

if [[ -f "Completeness_ref.tar.gz" ]]; then
     tar -xzf "Completeness_ref.tar.gz" -C "$output_dirname/"
elif [[ -d "Completeness_ref" ]]; then
     cp -r "Completeness_ref*" "$output_dirname/"
fi




# CD output directory

cd "$output_dirname"





# Then we compute the completeness curves with our pipeline code

s1=(1.0 2.0 3.0 4.0) # we need these broader bins for curves
s2=(2.0 3.0 4.0 5.0) # we need these broader bins for curves
s1+=(1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5) # and also these narrower bins for blocks
s2+=(1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0) # and also these narrower bins for blocks
for (( i=0; i<${#s1[@]}; i++ )); do
     
     topcat -stilts tpipe in="datatable_sim_rec.fits" \
                         cmd="select \"(Maj_convol*Min_convol)/(Maj_beam*Min_beam)>=${s1[i]} && (Maj_convol*Min_convol)/(Maj_beam*Min_beam)<=${s2[i]}\"" \
                         out="datatable_selected_sim_Sbeam_${s1[i]}_${s2[i]}.fits"
     
     ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis \
                         "datatable_selected_sim_Sbeam_${s1[i]}_${s2[i]}.fits"
     
     mv "Completeness" "Completeness_sim_Sbeam_${s1[i]}_${s2[i]}"

done









# Then make plot

cp ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis-tools/a_dzliu_code_plot_completeness_curves_for_various_source_sizes.py \
.

./a_dzliu_code_plot_completeness_curves_for_various_source_sizes.py





# Then make plot (2D image-like plot)

cp ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis-tools/a_dzliu_code_plot_completeness_blocks_for_various_source_sizes.py \
.

./a_dzliu_code_plot_completeness_blocks_for_various_source_sizes.py

cp ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis-tools/a_dzliu_code_plot_completeness_blocks_for_various_source_sizes_versus_S_total_sim_to_rms_noise.py \
.

./a_dzliu_code_plot_completeness_blocks_for_various_source_sizes_versus_S_total_sim_to_rms_noise.py








# Finally, clean-up

#find . -name ".*" -print0 | xargs -0 -I X rm X

tar -czf data_files_packed_for_${output_dirname}.tar.gz \
          Completeness_sim_Sbeam_* \
          Completeness_ref* \
          a_dzliu_code_plot_completeness_curves_for_various_source_sizes.py \
          a_dzliu_code_plot_completeness_blocks_for_various_source_sizes.py \
          a_dzliu_code_plot_completeness_blocks_for_various_source_sizes_versus_S_total_sim_to_rms_noise.py \
          Plot_Completeness_curves_for_various_source_sizes.pdf \
          Plot_Completeness_blocks_for_various_source_sizes.pdf \
          Plot_Completeness_blocks_for_various_source_sizes.S_total_sim_to_rms_noise.pdf

tar -tvvf data_files_packed_for_${output_dirname}.tar.gz 2>/dev/null \
        > data_files_packed_for_${output_dirname}.tar.log

echo "Produced by the code:" > data_files_packed_for_${output_dirname}.readme.txt
echo "    \"${BASH_SOURCE[0]}\"" >> data_files_packed_for_${output_dirname}.readme.txt
echo "" >> data_files_packed_for_${output_dirname}.readme.txt
echo "Under working directory: " >> data_files_packed_for_${output_dirname}.readme.txt
echo "    \"$(pwd)\"" >> data_files_packed_for_${output_dirname}.readme.txt
echo "" >> data_files_packed_for_${output_dirname}.readme.txt
echo "Current datetime: " >> data_files_packed_for_${output_dirname}.readme.txt
echo "    $current_datetime" >> data_files_packed_for_${output_dirname}.readme.txt
echo "" >> data_files_packed_for_${output_dirname}.readme.txt

if [[ $(cat data_files_packed_for_${output_dirname}.tar.log | tail -n 1 | grep "Archive Format: POSIX ustar format,  Compression: gzip" | wc -l) ]]; then
     rm -r \
          Completeness_sim_Sbeam_* \
          Completeness_ref* \
          a_dzliu_code_plot_completeness_curves_for_various_source_sizes.py \
          a_dzliu_code_plot_completeness_blocks_for_various_source_sizes.py \
          a_dzliu_code_plot_completeness_blocks_for_various_source_sizes_versus_S_total_sim_to_rms_noise.py
else
     echo "Error! Failed to pack data files via \"tar\"!"
     exit 255
fi












