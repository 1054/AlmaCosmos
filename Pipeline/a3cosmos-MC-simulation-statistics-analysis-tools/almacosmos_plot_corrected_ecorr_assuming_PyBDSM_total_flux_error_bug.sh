#!/bin/bash
# 

#if [[ ! -d "Plot_corrected_ecorr__with_PyBDSM_total_flux_error" ]]; then
#    mkdir "Plot_corrected_ecorr__with_PyBDSM_total_flux_error"
#    mv "datatable_applied_correction_ecorr_with_more_columns.txt" "Plot_corrected_ecorr__with_PyBDSM_total_flux_error/"
#    mv Plot_corrected_ecorr*.* Plot_uncorrected_ecorr*.* "Plot_corrected_ecorr__with_PyBDSM_total_flux_error/"
#fi


cp Plot_corrected_ecorr__via_spline_table/datatable_applied_correction_ecorr.txt .


topcat -stilts tmatchn \
                nin=2 \
                in1='datatable_applied_correction_ecorr.txt' ifmt1=ascii \
                in2='../simu_data_input.txt' ifmt2=ascii \
                icmd2="keepcols \"S_peak noise Maj_out Min_out Maj_beam Min_beam image_file_STR simu_name_STR\"" \
                values1='index' values2='index' \
                suffix1="" \
                matcher=exact multimode=pairs iref=1 \
                ocmd="replacecol e_S_out_uncorr \"e_S_out_uncorr * ((Maj_out*Min_out)/(Maj_beam*Min_beam)+1)\"" \
                out='datatable_applied_correction_ecorr_with_more_columns.txt'


$(dirname "${BASH_SOURCE[0]}")/almacosmos_plot_corrected_ecorr.sh


mkdir "Plot_corrected_ecorr__via_spline_table__assuming_PyBDSM_total_flux_error_bug"
mv "Plot_corrected_ecorr"*.* "Plot_corrected_ecorr__via_spline_table__assuming_PyBDSM_total_flux_error_bug/"
#mv "datatable_applied_correction_ecorr.txt" "Plot_corrected_ecorr__via_spline_table__assuming_PyBDSM_total_flux_error_bug/"
#mv "datatable_applying_correction_ecorr.txt" "Plot_corrected_ecorr__via_spline_table__assuming_PyBDSM_total_flux_error_bug/"
mv "datatable_applied_correction_ecorr_with_more_columns.txt" "Plot_corrected_ecorr__via_spline_table__assuming_PyBDSM_total_flux_error_bug/"











