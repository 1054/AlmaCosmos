#!/bin/bash
# 




# Setup input datatable_sim_rec

if [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"* ]] && [[ $(pwd) == *"PyBDSM"* ]]; then

     datatable_sim_rec="datatable_CrossMatched/datatable_CrossMatched_all_entries_filtered_in_PB.fits.gz"
     
elif [[ $(pwd) == *"Monte_Carlo_Simulation_Physically_Motivated"* ]] && [[ $(pwd) == *"GALFIT"* ]]; then

     datatable_sim_rec="datatable_CrossMatched/datatable_CrossMatched_all_entries_filtered_in_PB.fits.gz"
     
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

#if [[ ! -d "Completeness_ref" ]]; then
#     echo "Error! \"Completeness_ref\" was not found! Please calculate the completeness of PHYS-PYBDSM then copy the result \"Completeness\" directory as \"Completeness_ref\" here!"
#     exit 255
#fi




# Prepare output directory

output_dirname="Completeness"
current_datetime=$(date +"%Y%m%d.%Hh%Mm%Ss")

if [[ -d "$output_dirname" ]]; then
     backup_dirname="$output_dirname"."$current_datetime"
     echo "Found existing \"$output_dirname\"! Backing it up as \"$backup_dirname\"!"
     mv "$output_dirname" "$backup_dirname"
fi

mkdir "$output_dirname"




#  Copy input datatable_sim_rec

if [[ "$datatable_sim_rec" == *".txt" ]]; then
     topcat -stilts tpipe in="$datatable_sim_rec" ifmt=ascii out="$output_dirname/datatable_sim_rec.fits"
else
     topcat -stilts tpipe in="$datatable_sim_rec" out="$output_dirname/datatable_sim_rec.fits"
fi

#cp -r "Completeness_ref*" "$output_dirname/"




# CD output directory

cd "$output_dirname"




# Then we compute the completeness curve with our pipeline code, the default output is a folder named "Completeness"

~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis \
                    datatable_sim_rec.fits













# Then make plot

cp ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis-tools/a_dzliu_code_plot_completeness_curve.py \
.

./a_dzliu_code_plot_completeness_curve.py












# Finally, clean-up

#find . -name ".*" -print0 | xargs -0 -I X rm X

tar -czf data_files_packed_for_${output_dirname}.tar.gz \
          Completeness \
          a_dzliu_code_plot_completeness_curve.py \
          Plot_Completeness_curve.pdf

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
          Completeness \
          a_dzliu_code_plot_completeness_curve.py
else
     echo "Error! Failed to pack data files via \"tar\"!"
     exit 255
fi









