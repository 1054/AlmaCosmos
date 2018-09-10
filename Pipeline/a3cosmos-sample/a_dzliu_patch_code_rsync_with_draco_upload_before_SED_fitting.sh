#!/bin/bash
# 


ssh -A -t gate.rzg.mpg.de ssh -t draco.mpcdf.mpg.de "mkdir -p /ptmp/dzliu/"

rsync -avz -r --stats --progress -e "ssh -A -t gate.rzg.mpg.de ssh" \
        --include '**/*' \
        "isaac1.bc.rzg.mpg.de:/u/$USER/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS/" \
        "/disk1/$USER/Works/AlmaCosmos/Simulations/Cosmological_Galaxy_Modelling_for_COSMOS/"


rsync -ravz --stats --progress -e ssh \
    --include "Selected_Sample_v20180720c.photometry_with_prior_redshifts.*" \
    --include "datatable_known_alias.txt" \
    --include "datatable_known_zspec.txt" \
    --include "Multi-wavelength_SEDs/" \
    --include "Multi-wavelength_SEDs/**" \
    --exclude "*" \
    "./" \
    "aida40110:~/Work/AlmaCosmos/Samples/20180720e/" --dry-run
    # 20180720c -- APER3 and new prior redshifts after solving spec-z multiplicity
    # 20180720d -- fixed bug of df=1e10 in 'michi2_filter_flux_2sigma_fit_infrared_upper_limits.py'
    # 20180720e -- fixed bug of setting "fit?" in 'magphys_highz_go_a3cosmos'





