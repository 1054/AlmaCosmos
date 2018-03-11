#!/bin/bash
# 



# rsync -avz --stats --progress -e "ssh -A -t gate.rzg.mpg.de ssh" --include '*' \
#         "isaac1.bc.rzg.mpg.de:/u/$USER/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Recovered/2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3/w_876.764_z_1.000_lgMstar_11.50_SB/" \
#         "Recovered/2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3/w_876.764_z_1.000_lgMstar_11.50_SB/"



# rsync -avz -r --stats --progress -e "ssh -A -t gate.rzg.mpg.de ssh" --include '*' \
#         "isaac1.bc.rzg.mpg.de:/$HOME/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS/" \
#         "$HOME/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS/"



#mkdir -p "/disk1/$USER/Works/AlmaCosmos/Simulations/20171105/Simulated"
#
#rsync -avz -r --stats --progress -e "ssh -A -t gate.rzg.mpg.de ssh" \
#        --include '**/*' \
#        "isaac1.bc.rzg.mpg.de:/u/$USER/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Simulated/" \
#        "/disk1/$USER/Works/AlmaCosmos/Simulations/20171105/Simulated"
#
#mkdir -p "/disk1/$USER/Works/AlmaCosmos/Simulations/20171105/Recovered"
#
#rsync -avz -r --stats --progress -e "ssh -A -t gate.rzg.mpg.de ssh" \
#        --include '**/*' \
#        "isaac1.bc.rzg.mpg.de:/u/$USER/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/Recovered/" \
#        "/disk1/$USER/Works/AlmaCosmos/Simulations/20171105/Recovered"




mkdir -p "/disk1/$USER/Works/AlmaCosmos/Simulations/Cosmological_Galaxy_Modelling_for_COSMOS"

rsync -avz -r --stats --progress -e "ssh -A -t gate.rzg.mpg.de ssh" \
        --include '**/*' \
        "isaac1.bc.rzg.mpg.de:/u/$USER/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS/" \
        "/disk1/$USER/Works/AlmaCosmos/Simulations/Cosmological_Galaxy_Modelling_for_COSMOS/"






