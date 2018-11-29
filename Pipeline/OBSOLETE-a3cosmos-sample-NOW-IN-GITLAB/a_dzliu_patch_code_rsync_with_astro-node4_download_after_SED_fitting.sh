#!/bin/bash
# 


rsync -ravz --stats --progress -e ssh \
    --include "Multi-wavelength_SED_Plots/" \
    --include "Multi-wavelength_SED_Plots/SED_fitting_magphys_priorz_with_upper_limits/" \
    --include "Multi-wavelength_SED_Plots/SED_fitting_magphys_priorz_with_upper_limits/**" \
    --include "Multi-wavelength_SED_Results/" \
    --include "Multi-wavelength_SED_Results/SED_fitting_magphys_priorz_with_upper_limits/" \
    --include "Multi-wavelength_SED_Results/SED_fitting_magphys_priorz_with_upper_limits/**" \
    --exclude "*" \
    "astro-node4:~/Work/AlmaCosmos/Samples/20180720d/" \
    "./" --delete # --dry-run
    # 20180720c -- APER3 and new prior redshifts after solving spec-z multiplicity
    # 20180720d -- fixed bug of df=1e10 in 'michi2_filter_flux_2sigma_fit_infrared_upper_limits.py'
    
    #--include "Multi-wavelength_SEDs/" \
    #--include "Multi-wavelength_SEDs/ID_*/" \
    #--include "Multi-wavelength_SEDs/ID_*/SED_fitting_magphys_priorz_with_upper_limits/" \
    #--include "Multi-wavelength_SEDs/ID_*/SED_fitting_magphys_priorz_with_upper_limits/**" \





