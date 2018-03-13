#!/bin/bash
# 

source ~/Softwares/Topcat/bin_setup.bash
source ~/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash
source ~/Cloud/Github/AlmaCosmos/Pipeline/SETUP.bash

mkdir datatable_CrossMatched
cd datatable_CrossMatched

topcat -stilts tpipe \
        in="../Read_Results_all_final_fit_2.result.all.txt" ifmt=ascii \
        omode=count
        # columns: 34   rows: 99396

topcat -stilts tpipe \
        in="../Read_Results_all_final_fit_2.result.source_err.txt" ifmt=ascii \
        omode=count
        # columns: 15   rows: 99396

topcat -stilts tpipe \
        in="../Read_Results_all_final_fit_2.result.flux_origin.txt" ifmt=ascii \
        omode=count
        # columns: 5   rows: 99396

topcat -stilts tmatchn nin=3 \
        in1="../Read_Results_all_final_fit_2.result.all.txt" ifmt1=ascii \
        in2="../Read_Results_all_final_fit_2.result.source_err.txt" ifmt2=ascii \
        in3="../Read_Results_all_final_fit_2.result.flux_origin.txt" ifmt3=ascii \
        matcher=exact values1=index values2=index values3=index \
        suffix1="" suffix2="_2" suffix3="_3" \
        out="../Read_Results_all_final_fit_2.fits"

topcat -stilts tmatchn nin=2 \
        in1="../Read_Results_all_final_fit_2.result.all.txt" ifmt=ascii \
        in2="../Read_Results_all_final_fit_2.result.all.txt" ifmt=ascii \

