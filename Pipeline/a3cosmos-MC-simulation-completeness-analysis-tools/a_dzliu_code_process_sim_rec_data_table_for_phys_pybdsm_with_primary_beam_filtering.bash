#!/bin/bash
# 

set -e # set exit on error


topcat -stilts tpipe in="datatable_CrossMatched_all_entries.fits" \
                    cmd="addcol dist_ra_cen_arcsec \"(ra_from_sim_cat-obs_ra_from_sim_cat)*3600.0*cos(obs_dec_from_sim_cat/180.0*PI)\"" \
                    cmd="addcol dist_dec_cen_arcsec \"(dec_from_sim_cat-obs_dec_from_sim_cat)*3600.0\"" \
                    cmd="addcol flag_is_in_PB \"sqrt(dist_ra_cen_arcsec*dist_ra_cen_arcsec+dist_dec_cen_arcsec*dist_dec_cen_arcsec)<primary_beam_from_sim_cat/2.0*0.9\"" \
                    cmd="select \"flag_is_in_PB\"" \
                    cmd="addcol source_area_in_beam \"(Maj_in*Min_in)/(Maj_beam*Min_beam)\"" \
                    cmd="addcol convol_area_in_beam \"sqrt(source_area_in_beam*source_area_in_beam+1)\"" \
                    cmd="addcol SNR_peak_from_sim_cat \"flux_from_sim_cat/convol_area_in_beam/rms_from_sim_cat\"" \
                    out="datatable_CrossMatched_all_entries_filtered_in_PB.fits"

echo "Output to \"datatable_CrossMatched_all_entries_filtered_in_PB.fits\"!"


# Then we can run the analysis
#/Users/dzliu/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-completeness-analysis \
#                    datatable_CrossMatched/datatable_CrossMatched_all_entries_filtered_in_PB.fits




