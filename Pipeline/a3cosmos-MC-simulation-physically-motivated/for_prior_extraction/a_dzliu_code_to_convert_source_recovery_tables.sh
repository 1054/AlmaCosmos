#!/bin/bash
# 

set -e

if [[ $(type topcat | wc -l) -eq 0 ]]; then
    echo "Error! Topcat was not found!"
    exit
fi

if [[ ! -d "Output_catalogs" ]]; then
    echo "Error! \"Output_catalogs\" was not found under current directory!"
    exit
fi

OutputDir="Output_catalogs"

cd "$OutputDir"


# 
# Count rows, make sure they are the same
# 
topcat -stilts tpipe in='Output_Prior_Galfit_Gaussian_Condon_errors.txt' ifmt=ascii \
                    cmd='keepcols "cat_id"' \
                    out='Output_Prior_Galfit_Gaussian_Condon_errors.id.txt' ofmt=ascii

topcat -stilts tpipe in='Output_Prior_Galfit_Gaussian_main_result.txt' ifmt=ascii \
                    cmd='keepcols "id_fit_2_str"' \
                    out='Output_Prior_Galfit_Gaussian_main_result.id.txt' ofmt=ascii

cat 'Output_Prior_Galfit_Gaussian_Condon_errors.id.txt' | wc -l # 495971
cat 'Output_Prior_Galfit_Gaussian_main_result.id.txt' | wc -l # 495930


# 
# Now we combine resulting catalogs.
# Here we also cross-match Getpix catalog, so as to filter out some sources which are simulated on NaN pixels
# 
topcat -stilts tmatchn \
            nin=3 \
            in1='Output_Prior_Galfit_Gaussian_main_result.txt' \
            ifmt1=ascii \
            icmd1="replacecol Image -name \"Image_1\" \"Image\"" \
            icmd1="replacecol Simu -name \"Simu_1\" \"Simu\"" \
            values1="id_fit_2_str Image_1 Simu_1" \
            \
            in2='Output_Prior_Galfit_Gaussian_Condon_errors.txt' \
            ifmt2=ascii \
            icmd2="replacecol Image -name \"Image_2\" \"Image\"" \
            icmd2="replacecol Simu -name \"Simu_2\" \"Simu\"" \
            values2="cat_id Image_2 Simu_2" \
            \
            in3='Output_Prior_Getpix_000.txt' \
            ifmt3=ascii \
            icmd3="keepcols \"pix_000 cat_id Simu Image\"" \
            icmd3="replacecol cat_id -name \"getpix_id\" \"cat_id\"" \
            icmd3="replacecol Image -name \"getpix_Image\" \"Image\"" \
            icmd3="replacecol Simu -name \"getpix_Simu\" \"Simu\"" \
            values3="getpix_id getpix_Image getpix_Simu" \
            \
            matcher="exact+exact+exact" \
            ofmt=fits \
            ocmd="select \"(flag_buffer==0)\"" \
            ocmd="select \"(pix_000 != 0)\"" \
            ocmd="addcol ID \"id_fit_2_str\"" \
            ocmd="addcol RA \"ra_fit_2\"" \
            ocmd="addcol Dec \"dec_fit_2\"" \
            ocmd="addcol Total_flux -units \"mJy\" \"source_total * 1e3\"" \
            ocmd="addcol E_Total_flux -units \"mJy\" \"source_total_err * 1e3\"" \
            ocmd="addcol Galfit_flux -units \"mJy\" \"f_fit_2\"" \
            ocmd="addcol E_Galfit_flux -units \"mJy\" \"df_fit_2\"" \
            ocmd="addcol Peak_flux -units \"mJy\" \"source_peak * 1e3\"" \
            ocmd="addcol E_Peak_flux -units \"mJy\" \"source_peak_err * 1e3\"" \
            ocmd="addcol Residual_flux -units \"mJy\" \"fres_fit_2\"" \
            ocmd="addcol Total_RMS -units \"mJy/beam\" \"rms_fit_2\"" \
            ocmd="addcol Maj_deconv -units \"arcsec\" \"maj_fit_2\"" \
            ocmd="addcol E_Maj_deconv -units \"arcsec\" \"maj_err_fit_2\"" \
            ocmd="addcol Min_deconv -units \"arcsec\" \"min_fit_2\"" \
            ocmd="addcol E_Min_deconv -units \"arcsec\" \"min_err_fit_2\"" \
            ocmd="addcol PA_deconv \"PA_fit_2\"" \
            ocmd="addcol E_PA_deconv \"PA_err_fit_2\"" \
            ocmd="addcol Pixel_noise -units \"mJy/beam\" \"pix_noise * 1e3\"" \
            ocmd="addcol Pixel_scale \"pix_scale\"" \
            ocmd="addcol Beam_area -units \"square-arcsec\" \"beam_area\"" \
            ocmd="addcol Obs_frequency -units \"GHz\" \"obs_freq\"" \
            ocmd="addcol Obs_wavelength -units \"um\" \"obs_lambda\"" \
            ocmd="addcol Pb_corr_pb_image \"pbcorr\"" \
            ocmd="addcol Pb_corr_equation \"pb_corr\"" \
            ocmd="addcol Galfit_chi_square \"chisq\"" \
            ocmd="addcol Galfit_reduced_chi_square \"rchisq\"" \
            ocmd="addcol Galfit_N_aperture_pixel \"n_aperpix\"" \
            ocmd="addcol Galfit_N_free_parameter \"n_freepar\"" \
            ocmd="addcol Flag_size_lower_boundary \"(abs(maj_fit_2-1.0*pix_scale)<0.02)\"" \
            ocmd="addcol Flag_size_upper_boundary \"(abs(maj_fit_2-3.0)<0.02)\"" \
            ocmd="addcol Flag_size_initial_guess \"(abs(maj_fit_2-0.25)<0.02)\"" \
            ocmd="addcol Flag_zero_galfit_flux_error \"(df_fit_2==0)\"" \
            ocmd="addcol Flag_zero_galfit_size_error \"(maj_fit_2>0 && maj_err_fit_2==0)\"" \
            ocmd="addcol Image_file_name \"Rect_1\"" \
            ocmd="addcol Image \"Image_1\"" \
            ocmd="addcol Simu \"Simu_1\"" \
            ocmd="delcols \"\$1 \$2 \$3 \$4 \$5 \$6 \$7 \$8 \$9 \$10\"" \
            ocmd="delcols \"\$1 \$2 \$3 \$4 \$5 \$6 \$7 \$8 \$9 \$10\"" \
            ocmd="delcols \"\$1 \$2 \$3 \$4 \$5 \$6 \$7 \$8 \$9 \$10\"" \
            ocmd="delcols \"\$1 \$2 \$3 \$4 \$5 \$6 \$7 \$8 \$9 \$10\"" \
            ocmd="delcols \"\$1 \$2 \$3 \$4 \$5 \$6 \$7 \$8 \$9\"" \
            out="Output_Prior_Galfit_Gaussian_Catalog.fits"
            # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn-usage.html
            # 
            # converts all units to Jy, Jy/beam.
            # 
            # note: Total_RMS = pixnoise * fluxconv
            # 


# 
# Done
# 
echo "Output to \"Output_Prior_Galfit_Gaussian_Catalog.fits\"!"
# 
#topcat -stilts tpipe \
#            in="Output_Prior_Galfit_Gaussian_Catalog.fits" \
#            cmd="select (Total_flux/E_Total_flux>=3.0)" \
#            cmd="keepcols \"ID RA Dec Total_flux E_Total_flux Galfit_flux E_Galfit_flux Peak_flux E_Peak_flux Residual_flux RMS Maj_deconv E_Maj_deconv Min_deconv E_Min_deconv PA_deconv E_PA_deconv Pixel_noise Pixel_scale Beam_area Obs_frequency Obs_wavelength Pb_corr_pb_image Pb_corr_equation Galfit_chi_square Galfit_reduced_chi_square Galfit_N_aperture_pixel Galfit_N_free_parameter Flag_size_lower_boundary Flag_size_upper_boundary Flag_size_initial_guess Flag_zero_galfit_flux_error Flag_zero_galfit_size_error Image_file_name Image Simu\"" \
#            out="Output_Prior_Galfit_Gaussian_Catalog_SNR_GE_3.fits"
## 
#echo "Output to \"Output_Prior_Galfit_Gaussian_Catalog_SNR_GE_3.fits\"!"

if [[ -f "Output_Prior_Galfit_Gaussian_Catalog.fits" ]]; then
      rm "Output_Prior_Galfit_Gaussian_Condon_errors.id.txt"
      rm "Output_Prior_Galfit_Gaussian_main_result.id.txt"
      gzip "Output_Prior_Getpix_000.txt"
      gzip "Output_Prior_Galfit_Gaussian_Condon_errors.txt"
      gzip "Output_Prior_Galfit_Gaussian_main_result.txt"
      gzip "Output_Prior_Galfit_Gaussian_Catalog.fits"
fi






