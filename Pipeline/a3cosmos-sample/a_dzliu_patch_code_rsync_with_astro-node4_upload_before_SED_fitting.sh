#!/bin/bash
# 


rsync -ravz --stats --progress -e ssh \
    --include "a_dzliu_code_step_4_run_sed_fitting_magphys_priorz_with_upper_limits_stage_1_before_examining_z.bash" \
    --include "a_dzliu_code_step_4_run_sed_fitting_magphys_priorz_with_upper_limits_stage_2_read_results.bash" \
    --include "datatable_known_alias.txt" \
    --include "datatable_known_zspec.txt" \
    --include "Multi-wavelength_SEDs/" \
    --include "Multi-wavelength_SEDs/**" \
    --exclude "*" \
    "./" \
    "astro-node4:~/Work/AlmaCosmos/Samples/20180720d/" --dry-run
    # 20180720c -- APER3 and new prior redshifts after solving spec-z multiplicity
    # 20180720d -- fixed bug of df=1e10 in 'michi2_filter_flux_2sigma_fit_infrared_upper_limits.py'





