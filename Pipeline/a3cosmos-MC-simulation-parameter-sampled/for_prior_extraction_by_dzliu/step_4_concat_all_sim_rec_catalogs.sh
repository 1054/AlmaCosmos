#!/bin/bash
# 

rm Read_Results_all_final_fit_2.result.all.txt

IFS=$'\n' read -d '' -r -a list_of_projects < "../output_GALFIT_dzliu/list_of_sim_projects.txt"

for (( i = 0; i < ${#list_of_projects[@]}; i++ )); do
    name_of_project=$(basename "${list_of_projects[i]}")
    if [[ x"$name_of_project" == x ]]; then continue; fi
    echo "Checking $name_of_project ..."
    ls "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.all.txt"
    ls "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.flux_origin.txt"
    ls "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_err.txt"
    ls "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_area.txt"
    ls "../output_GALFIT_dzliu/$name_of_project/concat_simulation_catalogs.txt"
    if [[ -f "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.all.txt" ]] && \
        [[ -f "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.flux_origin.txt" ]] && \
        [[ -f "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_err.txt" ]] && \
        [[ -f "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_area.txt" ]] && \
        [[ -f "../output_GALFIT_dzliu/$name_of_project/concat_simulation_catalogs.txt" ]]; then
        echo "Concatenating $name_of_project ..."
        if [[ ! -f Read_Results_all_final_fit_2.result.all.txt ]]; then
            cp "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.all.txt"         .
            cp "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.flux_origin.txt" .
            cp "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_err.txt"  .
            cp "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_area.txt" .
            cp "../output_GALFIT_dzliu/$name_of_project/concat_simulation_catalogs.txt"                      .
        else
            cat "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.all.txt"         | grep -v "^#" >> Read_Results_all_final_fit_2.result.all.txt
            cat "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.flux_origin.txt" | grep -v "^#" >> Read_Results_all_final_fit_2.result.flux_origin.txt
            cat "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_err.txt"  | grep -v "^#" >> Read_Results_all_final_fit_2.result.source_err.txt
            cat "../output_GALFIT_dzliu/$name_of_project/Read_Results_all_final_fit_2.result.source_area.txt" | grep -v "^#" >> Read_Results_all_final_fit_2.result.source_area.txt
            cat "../output_GALFIT_dzliu/$name_of_project/concat_simulation_catalogs.txt"                      | grep -v "^#" >> concat_simulation_catalogs.txt
        fi
    fi
done


cat Read_Results_all_final_fit_2.result.all.txt          | wc -l
cat Read_Results_all_final_fit_2.result.flux_origin.txt  | wc -l
cat Read_Results_all_final_fit_2.result.source_err.txt   | wc -l
cat Read_Results_all_final_fit_2.result.source_area.txt  | wc -l
cat concat_simulation_catalogs.txt                       | wc -l


source ~/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash
source ~/Cloud/Github/AlmaCosmos/Pipeline/SETUP.bash
source ~/Softwares/Topcat/bin_setup.bash

topcat -stilts tmatchn nin=4 \
        in1="Read_Results_all_final_fit_2.result.all.txt" ifmt1=ascii \
        in2="Read_Results_all_final_fit_2.result.source_err.txt" ifmt2=ascii \
        in3="Read_Results_all_final_fit_2.result.source_area.txt" ifmt3=ascii \
        in4="Read_Results_all_final_fit_2.result.flux_origin.txt" ifmt4=ascii \
        matcher=exact values1=index values2=index values3=index values4=index \
        suffix1="" suffix2="_2" suffix3="_3" suffix4="_4" \
        ocmd="select (flag_buffer==0)" \
        ocmd="addcol Total_flux -units \"Jy\" \"source_total\" " \
        ocmd="addcol E_Total_flux -units \"Jy\" \"source_total_err\" " \
        ocmd="addcol Peak_flux -units \"Jy/beam\" \"source_peak\" " \
        ocmd="addcol E_Peak_flux -units \"Jy/beam\" \"source_peak_err\" " \
        ocmd="addcol Maj_deconv -units \"arcsec\" \"Maj_fit_2\" " \
        ocmd="addcol Min_deconv -units \"arcsec\" \"Min_fit_2\" " \
        ocmd="addcol PA_deconv -units \"degree\" \"PA_fit_2\" " \
        ocmd="addcol RMS -units \"Jy/beam\" \"pix_noise\"" \
        ocmd="addcol ID \"id_fit_2_str\"" \
        ocmd="addcol RA -units \"degree\" \"ra_fit_2\"" \
        ocmd="addcol Dec -units \"degree\" \"dec_fit_2\"" \
        ocmd="replacecol pb_corr -name \"pb_corr_from_equation\" \"pb_corr\" " \
        ocmd="keepcols \"ID RA Dec Total_flux E_Total_flux Peak_flux E_Peak_flux Maj_deconv Min_deconv PA_deconv convol_area_in_beam beam_area RMS pix_scale flux_conv pb_corr_from_equation Image Simu\"" \
        out="concat_recovery_catalogs.fits"



mkdir "datatable_CrossMatched"

topcat -stilts tmatchn nin=2 \
        in1=concat_simulation_catalogs.txt ifmt1=ascii \
        in2=concat_recovery_catalogs.fits \
        matcher="sky+exact+exact" params=1.0 \
        values1="SIM_RA SIM_Dec Image Simu" values2="RA Dec Image Simu" \
        suffix1="_SIM" suffix2="" \
        multimode=pairs iref=1 \
        ocmd='select "(!NULL_SIM_TOTAL_FLUX && !NULL_Total_flux)"' \
        ocmd="replacecol SIM_TOTAL_FLUX -units \"Jy\" \"SIM_TOTAL_FLUX*flux_conv\"" \
        ocmd="addcol S_in -units \"Jy\" \"SIM_TOTAL_FLUX\"" \
        ocmd="addcol e_S_out -units \"Jy\" \"E_Total_flux\"" \
        ocmd="addcol S_out -units \"Jy\" \"Total_flux\"" \
        ocmd="addcol S_peak -units \"Jy/beam\" \"Peak_flux\"" \
        ocmd="addcol S_res -units \"Jy\" \"Total_flux*0.0\"" \
        ocmd="addcol noise -units \"Jy/beam\" \"SIM_RMS\"" \
        ocmd="addcol Maj_in -units \"arcec\" \"SIM_MAJ\"" \
        ocmd="addcol Min_in -units \"arcec\" \"SIM_MIN\"" \
        ocmd="addcol PA_in -units \"degree\" \"SIM_PA\"" \
        ocmd="addcol Maj_out -units \"arcec\" \"Maj_deconv\"" \
        ocmd="addcol Min_out -units \"arcec\" \"Min_deconv\"" \
        ocmd="addcol PA_out -units \"degree\" \"PA_deconv\"" \
        ocmd="addcol Maj_beam -units \"arcec\" \"SIM_BEAM_MAJ\"" \
        ocmd="addcol Min_beam -units \"arcec\" \"SIM_BEAM_MIN\"" \
        ocmd="addcol PA_beam -units \"degree\" \"SIM_BEAM_PA\"" \
        ocmd="addcol image_file_STR \"Image\"" \
        ocmd="addcol simu_name_STR \"Simu\"" \
        out="datatable_CrossMatched/datatable_CrossMatched.fits"



topcat -stilts tpipe \
        in="datatable_CrossMatched/datatable_CrossMatched.fits" \
        cmd="select \"(SIM_MAJ/SIM_BEAM_MAJ<3.99 && SIM_MAJ<=3.0)\"" \
        out="datatable_CrossMatched/datatable_CrossMatched_filtered.fits"




#a3cosmos-MC-simulation-statistics-analysis datatable_CrossMatched/datatable_CrossMatched_filtered.fits



