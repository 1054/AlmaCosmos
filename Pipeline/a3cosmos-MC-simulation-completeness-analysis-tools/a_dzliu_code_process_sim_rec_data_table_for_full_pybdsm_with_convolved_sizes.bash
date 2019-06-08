#!/bin/bash
# 

set -e # set exit on error


topcat -stilts tpipe in="concat_sim_rec_data_table.fits" \
                cmd='keepcols "sim_Maj sim_Min sim_PA sim_beam_maj sim_beam_min sim_beam_pa"' \
                out="concat_sim_rec_data_table.maj.min.PA.txt" ofmt=ascii


cp ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-statistics-analysis-tools/a_dzliu_code_calc_Gaussian_convolved_sizes_for_any_data_input.sm  .


echo "macro read a_dzliu_code_calc_Gaussian_convolved_sizes_for_any_data_input.sm a_dzliu_code_calc_Gaussian_convolved_sizes concat_sim_rec_data_table.maj.min.PA" | sm


topcat -stilts tmatchn nin=2 in1="concat_sim_rec_data_table.fits"\
               in2="concat_sim_rec_data_table.maj.min.PA.convolved_sizes.txt" ifmt2=ascii \
               matcher=exact values1='index' values2='index' join1=always iref=1 fixcols=dups suffix1='' \
               out="concat_sim_rec_data_table_with_convolved_sizes.fits"


echo "Output to \"concat_sim_rec_data_table_with_convolved_sizes.fits\"!"

