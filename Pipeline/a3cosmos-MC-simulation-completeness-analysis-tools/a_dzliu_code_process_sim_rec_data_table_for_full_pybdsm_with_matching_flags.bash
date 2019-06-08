#!/bin/bash
# 

set -e # set exit on error


topcat -stilts tpipe in="concat_sim_rec_data_table_with_convolved_sizes.fits" \
                    cmd="addcol flag_matched \"rec_f>0\"" \
                    cmd="addcol flag_nonmatched_missed \"!flag_matched\"" \
                    cmd="addcol Maj_in \"sim_Maj\"" \
                    cmd="addcol Min_in \"sim_Min\"" \
                    cmd="addcol PA_in \"sim_PA\"" \
                    cmd="addcol Maj_beam \"sim_beam_Maj\"" \
                    cmd="addcol Min_beam \"sim_beam_Min\"" \
                    cmd="addcol PA_beam \"sim_beam_PA\"" \
                    cmd="addcol Maj_out \"rec_Maj\"" \
                    cmd="addcol Min_out \"rec_Min\"" \
                    cmd="addcol PA_out \"rec_PA\"" \
                    cmd="addcol S_in \"sim_f\"" \
                    cmd="addcol S_out \"rec_f\"" \
                    cmd="addcol S_peak \"rec_fpeak\"" \
                    cmd="addcol noise \"sim_rms\"" \
                    out="concat_sim_rec_data_table_with_convolved_sizes_with_flag_matched.fits"


echo "Output to \"concat_sim_rec_data_table_with_convolved_sizes_with_flag_matched.fits\"!"
