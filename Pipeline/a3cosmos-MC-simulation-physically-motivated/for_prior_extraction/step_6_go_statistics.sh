#!/bin/bash
# 
# Identify those simulated sources which at actually at the position where original image pixel value is nan or 0.000000000
# 

#cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20170730_on_Phys_MC_Simulated_Images/

if [[ ! -f "Statistics/datatable_CrossMatched_only_matches.fits" ]]; then
    echo "Error! \"Statistics/datatable_CrossMatched_only_matches.fits\" was not found!"
    exit 1
fi

~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-statistics-analysis "Statistics/datatable_CrossMatched_only_matches.fits" "Statistics"

