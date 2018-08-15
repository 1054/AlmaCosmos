#!/bin/bash
# 

#__DOCUMENTATION__  
#__DOCUMENTATION__  Description: 
#__DOCUMENTATION__      Selecting subsample from two photometry. 
#__DOCUMENTATION__      Creating fits format table file, in which each row is a source, and the photometry flux and error for each band are stored in each column. :
#__DOCUMENTATION__      
#__DOCUMENTATION__  Input Files:
#__DOCUMENTATION__      "../../Catalogs/A3COSMOS/A-COSMOS_prior_2018-06-01a_Gaussian_with_meta_without_very_high_res_projects_corrected_within_Pbcor_0.1.fits"
#__DOCUMENTATION__      "../../Catalogs/A3COSMOS/cat_pybdsm_concatenated_290318_mJy_within_cosmos_without_very_high_res_projects_with_meta_corrected.fits"
#__DOCUMENTATION__      
#__DOCUMENTATION__  Output Files:
#__DOCUMENTATION__      Selected_Sample_v20180720c.photometry_with_prior_redshifts.fits
#__DOCUMENTATION__      Selected_Sample_v20180720c.photometry.fits
#__DOCUMENTATION__      out_*.*
#__DOCUMENTATION__      tmp_*.*
#__DOCUMENTATION__  

# 20180720
# The problem about catalog cross-matching is confusion
# we can only cross-match our main sample catalog to other lower spatial resolution catalogs, 
# but not higher spatial resolution catalogs, 
# because our main sample catalog is sparsely selected from our master catalog. 
# so the solution is that, 
# we first cross-match the reference catalog to our master catalog with sky radius 1.0arcsec, 
# then cross-match our main sample catalog to the cross-matched ref-master catalog by master ID. 
# But I think this is not needed for Laigle photometry data because they are doing aperture photometry. 
# This is needed for photo-z and spec-z catalog!

# 20180720
# Now also corrected for astrometry for RA Dec from Laigle2016 catalog:
#     ---
#     in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_FIR+mm_Jin2017/COSMOS_fluxes_194428_20170324_850update_with_SFRs_20170223.fits' \
#     ifmt2=fits \
#     icmd2="replacecol _ra -name \"RA\" -desc \"corrected for astrometry for Laigle2016 priors\" \"(_id<1e8) ? _ra - 0.09/3600.0/cos(_de/180.0*PI) : _ra\"" \
#     icmd2="replacecol _de -name \"Dec\" -desc \"corrected for astrometry for Laigle2016 priors\" \"(_id<1e8) ? _de - 0.015/3600.0 : _de\"" \
#     ---
#     in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
#     icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
#     icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
#     ---

# 20180720
# Now also filtered GALFIT-out-of-FoV outliers
#     cmd="select \"!(Image_cutout_prior==\\\"2013.1.00118.S_SB1_GB1_MB1_AzTECC81_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==383026)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00260.S_SB2_GB1_MB1__13854__sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==469137)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00540.S_SB1_GB1_MB1_UVISTA-304384_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==875426)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00137.S_SB5_GB1_MB1_z23_4_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==886206)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00055.S_SB2_GB1_MB1_COSMOS_48162_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==638455)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00260.S_SB1_GB1_MB1__44655__sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==675106)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00137.S_SB2_GB1_MB1_z35_43_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==850879)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2012.1.00076.S_SB2_GB1_MB1_ID112_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==480154)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2013.1.00884.S_SB1_GB1_MB1_CS_AGN5_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==640381)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00137.S_SB2_GB1_MB1_z35_53_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==335295)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2015.1.00260.S_SB4_GB1_MB1__25494__sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==231714)\"" \
#     cmd="select \"!(Image_cutout_prior==\\\"2013.1.00034.S_SB2_GB2_MB1_lowz_cell9_149780_sci.spw0_1_2_3.cont.I.image.cut_-20_480_270_770\\\" && ID_prior==571036)\"" \


set -e

# 
# topcat command line usage
# see -- http://www.star.bristol.ac.uk/~mbt/stilts/
# 
#topcat -stilts
#topcat -stilts tmatchn       # -- cross matching
#topcat -stilts tpipe         # -- row selection
#topcat -stilts calc help     # -- calc and print to stdout


#output_cat="Selected_Sample_v20180720a"

#rm out_5.fits out_6.fits out_7.fits out_8.fits out_9.fits out_10.fits out_11.fits
#output_cat="Selected_Sample_v20180720b" #<20180727># fixed bug: Salvato2017 spec-z multiplicity issue
output_cat="Selected_Sample_v20180720c" #<20180728># fixed bug: Salvato2017 spec-z multiplicity issue with better option, now we list all possible spec-z and photo-zs, previously we ignore all photo-z if any photo-z agrees with spec-z.


input_cat_1="../../Catalogs/A3COSMOS/A-COSMOS_prior_2018-06-01a_Gaussian_with_meta_without_very_high_res_projects_corrected_within_Pbcor_0.1.fits"
input_cat_2="../../Catalogs/A3COSMOS/cat_pybdsm_concatenated_290318_mJy_within_cosmos_without_very_high_res_projects_with_meta_corrected.fits"
input_cat_1_fmt="fits"
input_cat_2_fmt="fits"
input_cat_1_label="Prior \ Gaussian \ fitting"
input_cat_2_label="Blind \ PyBDSM \ fitting"
input_cat_1_radec=("ra" "dec")
input_cat_2_radec=("ra" "dec")
input_cat_1_image="Image_file"
input_cat_2_image="Image_file"
input_cat_1_lambda="Obs_wavelength"
input_cat_2_lambda="Obs_wavelength"
input_cat_1_fpeak=""
input_cat_1_dfpeak=""
input_cat_2_fpeak=""
input_cat_2_dfpeak=""
input_cat_1_ftotal="Total_flux_pbcor"
input_cat_1_dftotal="E_Total_flux_sim_pbcor"
input_cat_2_ftotal="Total_flux_pbcor"
input_cat_2_dftotal="E_Total_flux_sim_pbcor"
#input_cat_1_selection="x1>=3.84" # When SNR >= 3.84, spurious <= 20.0%, differential spurious at this SNR is 65.0%
#input_cat_2_selection="x1>=4.88" # When SNR >= 4.88, spurious <= 19.9%, differential spurious at this SNR is 66.7%
input_cat_1_selection="x1>=4.35" # When SNR >= 4.35, spurious <= 12.7%, differential spurious at this SNR is 50.0%
input_cat_2_selection="x1>=5.40" # When SNR >= 5.40, spurious <= 8.0%, differential spurious at this SNR is 50.1%
input_cat_1_suffix="_prior"
input_cat_2_suffix="_pybdsm"
#
crossmatched_seplimit="1.0" # arcsec
# 
input_cat_1_snr_total="${input_cat_1_ftotal}${input_cat_1_suffix}/${input_cat_1_dftotal}${input_cat_1_suffix}"
input_cat_2_snr_total="${input_cat_2_ftotal}${input_cat_2_suffix}/${input_cat_2_dftotal}${input_cat_2_suffix}"


if [[ ! -f "$output_cat.photometry.fits" ]]; then
    # 
    # Cross match blind extraction and prior fitting catalog
    # 
    if [[ ! -f "out_1.fits" ]]; then
    topcat -stilts tmatchn \
                    nin=2 \
                    in1="$input_cat_1" \
                    ifmt1="fits" \
                    icmd1="sort -down \"${input_cat_1_ftotal}\"" \
                    icmd1="select \"${input_cat_1_selection}\"" \
                    values1="${input_cat_1_radec[0]} ${input_cat_1_radec[1]} $input_cat_1_image" \
                    suffix1="$input_cat_1_suffix" \
                    in2="$input_cat_2" \
                    ifmt2="fits" \
                    icmd2="sort -down \"${input_cat_2_ftotal}\"" \
                    icmd2="select \"${input_cat_2_selection}\"" \
                    values2="${input_cat_2_radec[0]} ${input_cat_2_radec[1]} $input_cat_2_image" \
                    suffix2="$input_cat_2_suffix" \
                    fixcols=all \
                    matcher="sky+exact" \
                    join1=always \
                    join2=always \
                    multimode=group \
                    params="${crossmatched_seplimit}" \
                    ocmd="addcol Flag_matched \"!NULL_${input_cat_1_ftotal}${input_cat_1_suffix} && !NULL_${input_cat_2_ftotal}${input_cat_2_suffix}\"" \
                    ocmd="addcol Flag_only${input_cat_1_suffix} \"!NULL_${input_cat_1_ftotal}${input_cat_1_suffix} && NULL_${input_cat_2_ftotal}${input_cat_2_suffix}\"" \
                    ocmd="addcol Flag_only${input_cat_2_suffix} \"NULL_${input_cat_1_ftotal}${input_cat_1_suffix} && !NULL_${input_cat_2_ftotal}${input_cat_2_suffix}\"" \
                    ocmd="addcol x1 -desc \"SNR_peak = Peak_flux/RMS_noise\" \"!NULL_x1${input_cat_1_suffix} ? x1${input_cat_1_suffix} : x1${input_cat_2_suffix}\"" \
                    ocmd="addcol x2 -desc \"Theta_beam = sqrt((Maj_convol*Min_convl)/(Maj_beam*Min_beam))\" \"!NULL_x2${input_cat_1_suffix} ? x2${input_cat_1_suffix} : x2${input_cat_2_suffix}\"" \
                    ocmd="addcol IMAGE_ALMA -units \"um\" \"!NULL_${input_cat_1_ftotal}${input_cat_1_suffix} ? ${input_cat_1_image}${input_cat_1_suffix} : ${input_cat_2_image}${input_cat_2_suffix}\"" \
                    ocmd="addcol WAVELENGTH_ALMA -units \"um\" \"!NULL_${input_cat_1_ftotal}${input_cat_1_suffix} ? ${input_cat_1_lambda}${input_cat_1_suffix} : ${input_cat_2_lambda}${input_cat_2_suffix}\"" \
                    ocmd="addcol FLUX_ALMA -units \"mJy\" \"!NULL_${input_cat_1_ftotal}${input_cat_1_suffix} ? ${input_cat_1_ftotal}${input_cat_1_suffix} : ${input_cat_2_ftotal}${input_cat_2_suffix}\"" \
                    ocmd="addcol FLUXERR_ALMA -units \"mJy\" \"!NULL_${input_cat_1_ftotal}${input_cat_1_suffix} ? ${input_cat_1_dftotal}${input_cat_1_suffix} : ${input_cat_2_dftotal}${input_cat_2_suffix}\"" \
                    ofmt="fits" \
                    out="out_1.fits"
                    # http://www.star.bristol.ac.uk/~mbt/stilts/sun256/tmatchn.html
    topcat -stilts tpipe \
                   in='out_1.fits' \
                   ifmt=fits \
                   omode=count \
                   | tee 'out_1.count.txt'
                   # count
                   # columns: 53   rows: 1452
                   # columns: 53   rows: 1158
    topcat -stilts tpipe \
                   in='out_1.fits' \
                   ifmt=fits \
                   omode=meta \
                   | tee 'out_1.meta.txt'
                   # meta
    if [[ -f 'out_2.fits' ]]; then rm 'out_2.fits'; fi
    if [[ -f 'out_3.fits' ]]; then rm 'out_3.fits'; fi
    if [[ -f 'out_4.fits' ]]; then rm 'out_4.fits'; fi
    fi
    
    
    # 
    # Now we cross-match our Master Catalog
    # 
    if [[ ! -f 'out_2.fits' ]]; then
    topcat -stilts tmatchn \
                    nin=2 \
                    in1='out_1.fits' \
                    ifmt1=fits \
                    values1="id${input_cat_1_suffix}" \
                    suffix1="" \
                    join1=always \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    ifmt2=fits \
                    values2="ID" \
                    suffix2="_Master" \
                    multimode=pairs \
                    matcher=exact \
                    fixcols=all \
                    ofmt=fits \
                    out='out_2.fits'
                    # 
    topcat -stilts tpipe \
                    in='out_2.fits' \
                    ifmt=fits \
                    omode=meta \
                   | tee 'out_2.meta.txt'
                   # meta
    if [[ -f 'out_3.fits' ]]; then rm 'out_3.fits'; fi
    if [[ -f 'out_4.fits' ]]; then rm 'out_4.fits'; fi
    fi
    
    
    # 
    # Now we cross-match the Laigle2016 Catalog only for photometry data
    # 
    if [[ ! -f 'out_3.fits' ]]; then
    topcat -stilts tmatchn \
                    nin=2 \
                    in1='out_2.fits' \
                    ifmt1=fits \
                    values1="ra${input_cat_1_suffix} dec${input_cat_1_suffix}" \
                    suffix1="" \
                    join1=always \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS2015_Laigle2016/COSMOS2015_Laigle+_v1.1.fits' \
                    ifmt2=fits \
                    icmd2='replacecol ALPHA_J2000 -name RA -desc "corrected for astrometry" "ALPHA_J2000 - 0.09/3600.0/cos(DELTA_J2000/180.0*PI)"' \
                    icmd2='replacecol DELTA_J2000 -name Dec -desc "corrected for astrometry" "DELTA_J2000 - 0.015/3600.0"' \
                    icmd2='replacecol NUMBER -name ID NUMBER' \
                    icmd2='delcols "*_IMAGE FLUX_RADIUS KRON_RADIUS NAME_* *XMM* *CHANDRA* *_20CM *_90CM *GALEX*"' \
                    icmd2='delcols "FLAG_XRAYBLEND OFFSET PHOTOZ TYPE ZPDF ZPDF_L68 ZPDF_H68 ZMINCHI2 CHI2_BEST ZP_2 CHI2_2 NBFILT ZQ CHIQ MODQ MODS CHIS MODEL AGE EXTINCTION MNUV MU MB MV MR MI MZ MY MJ MH MK MNUV_MR CLASS MASS_MED MASS_MED_MIN68 MASS_MED_MAX68 MASS_BEST SFR_MED SFR_MED_MIN68 SFR_MED_MAX68 SFR_BEST SSFR_MED SSFR_MED_MIN68 SSFR_MED_MAX68 SSFR_BEST L_NU L_R L_K"' \
                    icmd2='delcols "*_APER2 *_APER2_* *_MAG *_MAG_* *_MAGERR *_MAGERR_* *_FLAGS *_FLAGS_* *_IMAFLAGS *_IMAFLAGS_* *_NUSTAR *_NUSTAR_* ID_A24 ID2006 ID2008 ID2013"' \
                    icmd2='delcols "FLUX_814W FLUXERR_814W"' \
                    icmd2='delcols "FLUX_24 FLUXERR_24 MAG_24 MAGERR_24 FLUX_100 FLUXERR_100 FLUX_160 FLUXERR_160 FLUX_250 FLUXERR_250 FLUXERRTOT_250 FLUX_350 FLUXERR_350 FLUXERRTOT_350 FLUX_500 FLUXERR_500 FLUXERRTOT_500"' \
                    values2="RA Dec" \
                    suffix2="_Laigle2016" \
                    multimode=pairs \
                    matcher=sky \
                    params="${crossmatched_seplimit}" \
                    fixcols=all \
                    ofmt=fits \
                    out='out_3.fits'
                    #<TODO>#
                    #icmd2='delcols "FLUX_814W FLUXERR_814W"' \
                    #icmd2='replacecol FLUX_814W -name FLUX_814W -units "uJy" "FLUX_814W > -90 ? pow(10, FLUX_814W/(-2.5) ) * 3630.780548 * 1e6 : -99"' \
                    #icmd2='replacecol FLUXERR_814W -name FLUXERR_814W -units "uJy" "FLUX_814W > -90 ? FLUXERR_814W * FLUX_814W : -99"' \
                    # 
    topcat -stilts tpipe \
                    in='out_3.fits' \
                    ifmt=fits \
                    omode=meta \
                   | tee 'out_3.meta.txt'
                   # meta
    if [[ -f 'out_4.fits' ]]; then rm 'out_4.fits'; fi
    fi
    
    
    # 
    # Now we cross-match the Jin2018 Catalog only for photometry data
    # 
    if [[ ! -f 'out_4.fits' ]]; then
    topcat -stilts tmatchn \
                    nin=2 \
                    in1='out_3.fits'\
                    ifmt1=fits \
                    values1="ra${input_cat_1_suffix} dec${input_cat_1_suffix}" \
                    suffix1="" \
                    join1=always \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_FIR+mm_Jin2017/COSMOS_fluxes_194428_20170324_850update_with_SFRs_20170223.fits' \
                    ifmt2=fits \
                    icmd2="replacecol _ra -name \"RA\" -desc \"corrected for astrometry for Laigle2016 priors\" \"(_id<1e8) ? _ra - 0.09/3600.0/cos(_de/180.0*PI) : _ra\"" \
                    icmd2="replacecol _de -name \"Dec\" -desc \"corrected for astrometry for Laigle2016 priors\" \"(_id<1e8) ? _de - 0.015/3600.0 : _de\"" \
                    icmd2="replacecol _id -name \"ID\" \"_id\"" \
                    icmd2="addcol f_K -before f250 \"(KtotX!=-99) ? pow(10,(-0.4*(KtotX-23.9)-3.0)) : -99\"" \
                    icmd2="addcol df_K -before f250 \"(KtotX!=-99) ? f_K/10.0 : 1e10\"" \
                    icmd2="replacecol f24_jin -name \"f24\" -units \"mJy\" \"(f24_jin!=-99) ? f24_jin/1e3 : -99\"" \
                    icmd2="replacecol df24_jin -name \"df24\" -units \"mJy\" \"(f24!=-99) ? df24_jin/1e3 : 1e10\"" \
                    icmd2="replacecol _fch1 -name \"f_irac1\" -units \"mJy\" \"(_fch1!=-99) ? _fch1/1e3 : -99\"" \
                    icmd2="replacecol _dfch1 -name \"df_irac1\" -units \"mJy\" \"(f_irac1!=-99) ? _dfch1/1e3 : 1e10\"" \
                    icmd2="replacecol _fch2 -name \"f_irac2\" -units \"mJy\" \"(_fch2!=-99) ? _fch2/1e3 : -99\"" \
                    icmd2="replacecol _dfch2 -name \"df_irac2\" -units \"mJy\" \"(f_irac2!=-99) ? _dfch2/1e3 : 1e10\"" \
                    icmd2="replacecol _fch3 -name \"f_irac3\" -units \"mJy\" \"(_fch3!=-99) ? _fch3/1e3 : -99\"" \
                    icmd2="replacecol _dfch3 -name \"df_irac3\" -units \"mJy\" \"(f_irac3!=-99) ? _dfch3/1e3 : 1e10\"" \
                    icmd2="replacecol _fch4 -name \"f_irac4\" -units \"mJy\" \"(_fch4!=-99) ? _fch4/1e3 : -99\"" \
                    icmd2="replacecol _dfch4 -name \"df_irac4\" -units \"mJy\" \"(f_irac4!=-99) ? _dfch4/1e3 : 1e10\"" \
                    icmd2="replacecol f3ghz -name \"f_10cm_VLA\" -units \"mJy\" \"(f3ghz!=-99) ? f3ghz/1e3 : -99\"" \
                    icmd2="replacecol df3ghz -name \"df_10cm_VLA\" -units \"mJy\" \"(f_10cm_VLA!=-99) ? df3ghz/1e3 : 1e10\"" \
                    icmd2="replacecol f20cm -name \"f_20cm_VLA\" -units \"mJy\" \"(f20cm!=-99) ? f20cm/1e3 : -99\"" \
                    icmd2="replacecol df20cm -name \"df_20cm_VLA\" -units \"mJy\" \"(f_20cm_VLA!=-99) ? df20cm/1e3 : 1e10\"" \
                    icmd2="delcols \"KtotX f3ghz_* df3ghz_* SAVEDid\"" \
                    values2="RA Dec" \
                    suffix2="_Jin2018" \
                    multimode=pairs \
                    matcher=sky \
                    params="${crossmatched_seplimit}" \
                    fixcols=all \
                    ofmt=fits \
                    out='out_4.fits'
                    # 
    topcat -stilts tpipe \
                    in='out_4.fits' \
                    ifmt=fits \
                    omode=meta \
                   | tee 'out_4.meta.txt'
                   # meta
    fi
    
    if [[ ! -f "$output_cat.photometry.fits" ]]; then
    topcat -stilts tpipe \
                    in='out_4.fits' \
                    cmd="select \"!(Image_cutout_prior==\\\"2013.1.00118.S_SB1_GB1_MB1_AzTECC81_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==383026)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00260.S_SB2_GB1_MB1__13854__sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==469137)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00540.S_SB1_GB1_MB1_UVISTA-304384_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==875426)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00137.S_SB5_GB1_MB1_z23_4_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==886206)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00055.S_SB2_GB1_MB1_COSMOS_48162_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==638455)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00260.S_SB1_GB1_MB1__44655__sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==675106)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00137.S_SB2_GB1_MB1_z35_43_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==850879)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2012.1.00076.S_SB2_GB1_MB1_ID112_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==480154)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2013.1.00884.S_SB1_GB1_MB1_CS_AGN5_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==640381)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00137.S_SB2_GB1_MB1_z35_53_sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==335295)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2015.1.00260.S_SB4_GB1_MB1__25494__sci.spw0_1_2_3.cont.I.image\\\" && ID_prior==231714)\"" \
                    cmd="select \"!(Image_cutout_prior==\\\"2013.1.00034.S_SB2_GB2_MB1_lowz_cell9_149780_sci.spw0_1_2_3.cont.I.image.cut_-20_480_270_770\\\" && ID_prior==571036)\"" \
                    out="$output_cat.photometry.fits"
                    # 
    topcat -stilts tpipe \
                   in="$output_cat.photometry.fits" \
                   ifmt=fits \
                   omode=meta \
                   | tee "$output_cat.photometry.meta.txt"
                   # meta
    fi
    
fi








if [[ ! -f "$output_cat.photometry_with_prior_redshifts.fits" ]]; then
    # 
    # Now we cross-match the Salvato2017 (COSMOS team only) Catalog for spec-z data
    # here we need the backward cross-matching
    # 
    if [[ ! -f 'tmp_Salvato2017_specz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_spec-z_Maria_Salvato_2017/OBSERVED_TARGETS_01SEP2017/OBSERVED_TARGETS_01SEP2017.fits' \
                    icmd1='replacecol RA_corr -name RA RA_corr' \
                    icmd1='replacecol Dec_corr -name Dec Dec_corr' \
                    icmd1='addcol Type_z "\"spec-z\""' \
                    icmd1='addcol z "z_spec"' \
                    icmd1='addcol Ref_z_spec "Contact+\", \"+Instr"' \
                    icmd1='replacecol Q_f -name Q_z_spec -desc "quality of spec-z, i.e., number of line features" "Q_f"' \
                    icmd1='keepcols "ID RA Dec z Type_z z_spec Ref_z_spec Q_z_spec"' \
                    icmd1='select "(z_spec>0 && z_spec<9 && Q_z_spec>=1)"' \
                    values1='RA Dec' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='RA Dec' \
                    suffix2='_Master' \
                    \
                    matcher=sky \
                    params=1.0 \
                    multimode=pairs \
                    iref=1 \
                    join1=match \
                    join2=match \
                    fixcols=all \
                    out='tmp_Salvato2017_specz_xmatch_backward.fits'
                    # 
    fi
    
    
    # 
    # Now we cross-match the Salvato2011 (Chandra X-ray AGN) Catalog for photo-z data
    # here we need the backward cross-matching
    # 
    if [[ ! -f 'tmp_Salvato2011_Chandra_photoz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Salvato2011/Catalog_Salvato2011_1sq_deg_Chandra_COSMOS_with_ID_RA_Dec.txt' \
                    ifmt1=ascii \
                    icmd1='replacecol z_phot -name z "z_phot"' \
                    icmd1='keepcols "ID RA Dec z"' \
                    icmd1='addcol Type_z "\"photo-z, optimized for AGN\""' \
                    values1='RA Dec' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='RA Dec' \
                    suffix2='_Master' \
                    \
                    matcher=sky \
                    params=1.0 \
                    multimode=pairs \
                    iref=1 \
                    join1=match \
                    join2=match \
                    fixcols=all \
                    out='tmp_Salvato2011_Chandra_photoz_xmatch_backward.fits'
    fi
    
    
    # 
    # Now we cross-match the Salvato2011 (Chandra X-ray AGN) Catalog for photo-z data
    # here we need the backward cross-matching
    # 
    if [[ ! -f 'tmp_Salvato2011_XMM_photoz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Salvato2011/Catalog_Salvato2011_2sq_deg_XMM_COSMOS_with_ID_RA_Dec.txt' \
                    ifmt1=ascii \
                    icmd1='replacecol z_phot -name z "z_phot"' \
                    icmd1='keepcols "ID RA Dec z"' \
                    icmd1='addcol Type_z "\"photo-z, optimized for AGN\""' \
                    values1='RA Dec' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='RA Dec' \
                    suffix2='_Master' \
                    \
                    matcher=sky \
                    params=1.0 \
                    multimode=pairs \
                    iref=1 \
                    join1=match \
                    join2=match \
                    fixcols=all \
                    out='tmp_Salvato2011_XMM_photoz_xmatch_backward.fits'
    fi
    
    
    # 
    # Now we cross-match the Laigle2016 Catalog but only for photo-z data
    # here we do not need the backward cross-matching because our master catalog ID equals Laigle2016 ID when they are counterparts
    # 
    if [[ ! -f 'tmp_Laigle2016_photoz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS2015_Laigle2016/COSMOS2015_Laigle+_v1.1.fits' \
                    ifmt1=fits \
                    icmd1='replacecol NUMBER -name ID NUMBER' \
                    icmd1='replacecol ZPDF -name z ZPDF' \
                    icmd1='replacecol ZPDF_L68 -name z_L68 ZPDF_L68' \
                    icmd1='replacecol ZPDF_H68 -name z_H68 ZPDF_H68' \
                    icmd1='replacecol MASS_MED -name lgMstar MASS_MED' \
                    icmd1='replacecol MASS_MED_MIN68 -name lgMstar_L68 MASS_MED_MIN68' \
                    icmd1='replacecol MASS_MED_MAX68 -name lgMstar_H68 MASS_MED_MAX68' \
                    icmd1='replacecol SFR_MED -name lgSFR SFR_MED' \
                    icmd1='replacecol SFR_MED_MIN68 -name lgSFR_L68 SFR_MED_MIN68' \
                    icmd1='replacecol SFR_MED_MAX68 -name lgSFR_H68 SFR_MED_MAX68' \
                    icmd1='replacecol ZMINCHI2 -name z_peak ZMINCHI2' \
                    icmd1='replacecol CHI2_BEST -name chisq_peak CHI2_2' \
                    icmd1='replacecol MASS_BEST -name lgMstar_peak MASS_BEST' \
                    icmd1='replacecol SFR_BEST -name lgSFR_peak SFR_BEST' \
                    icmd1='replacecol ZP_2 -name z_second_peak ZP_2' \
                    icmd1='replacecol CHI2_2 -name chisq_second_peak CHI2_2' \
                    icmd1='replacecol EXTINCTION -name A_V EXTINCTION' \
                    icmd1='addcol Type_z "\"photo-z, LePhare code, no AGN component\""' \
                    icmd1='addcol Flag_Xray_AGN -after TYPE "TYPE==2"' \
                    icmd1='keepcols "ID z z_L68 z_H68 z_peak chisq_peak z_second_peak chisq_second_peak Type_z Flag_Xray_AGN lgMstar lgMstar_L68 lgMstar_H68 lgMstar_peak lgSFR lgSFR_L68 lgSFR_H68 lgSFR_peak AGE EBV A_V"' \
                    values1='ID' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='ID' \
                    suffix2='_Master' \
                    \
                    matcher=exact \
                    multimode=pairs \
                    iref=1 \
                    join1=match \
                    join2=match \
                    fixcols=all \
                    out='tmp_Laigle2016_photoz_xmatch_backward.fits'
    fi
    
    
    # 
    # Now we cross-match the Davidzon2017 Catalog but only for photo-z data
    # here we do not need the backward cross-matching because our master catalog ID equals Laigle2016 ID and Davidzon2017 ID equals Laigle2016 ID when they are counterparts
    # 
    if [[ ! -f 'tmp_Davidzon2017_photoz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS2015_Davidzon2017/cosmos2015_D17_v2.0_zmin-zmax.fits' \
                    ifmt1=fits \
                    icmd1='replacecol ZML -name z ZML' \
                    icmd1='replacecol ZML_L68 -name z_L68 ZML_L68' \
                    icmd1='replacecol ZML_H68 -name z_H68 ZML_H68' \
                    icmd1='replacecol ZBEST -name z_peak ZBEST' \
                    icmd1='replacecol CHI2 -name chisq_peak CHI2' \
                    icmd1='replacecol logMASS_MED -name lgMstar logMASS_MED' \
                    icmd1='replacecol logMASS_L68 -name lgMstar_L68 logMASS_L68' \
                    icmd1='replacecol logMASS_H68 -name lgMstar_H68 logMASS_H68' \
                    icmd1='replacecol logSFR_MED -name lgSFR logSFR_MED' \
                    icmd1='replacecol logSFR_L68 -name lgSFR_L68 logSFR_L68' \
                    icmd1='replacecol logSFR_H68 -name lgSFR_H68 logSFR_H68' \
                    icmd1='replacecol AGE_MED -name AGE AGE_MED' \
                    icmd1='replacecol AGE_L68 -name AGE_L68 AGE_L68' \
                    icmd1='replacecol AGE_H68 -name AGE_H68 AGE_H68' \
                    icmd1='addcol Type_z "\"photo-z, LePhare code, optimized for z>2.5 sources, no AGN component\""' \
                    icmd1='keepcols "ID z z_L68 z_H68 z_peak chisq_peak Type_z lgMstar lgMstar_L68 lgMstar_H68 lgSFR lgSFR_L68 lgSFR_H68 AGE AGE_L68 AGE_H68 EBV"' \
                    values1='ID' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='ID' \
                    suffix2='_Master' \
                    \
                    matcher=exact \
                    multimode=pairs \
                    iref=1 \
                    join1=match \
                    join2=match \
                    fixcols=all \
                    out='tmp_Davidzon2017_photoz_xmatch_backward.fits'
    fi
    
    
    # 
    # Now we cross-match the Jin2018 Catalog for photo-z data
    # here we need the backward cross-matching
    # 
    if [[ ! -f 'tmp_Jin2018_photoz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_FIR+mm_Jin2017/v20180712/COSMOS_Super_Deblended_FIRmm_Catalog_20180712.fits' \
                    ifmt1=fits \
                    icmd1="replacecol RA -name \"RA\" -desc \"corrected for astrometry for Laigle2016 priors\" \"(ID<1e8) ? RA - 0.09/3600.0/cos(DEC/180.0*PI) : RA\"" \
                    icmd1="replacecol Dec -name \"Dec\" -desc \"corrected for astrometry for Laigle2016 priors\" \"(ID<1e8) ? DEC - 0.015/3600.0 : DEC\"" \
                    icmd1='replacecol z_IR -name z z_IR' \
                    icmd1='replacecol ez_IR -name E_z ez_IR' \
                    icmd1='replacecol zphot -name z_phot zphot' \
                    icmd1='replacecol zspec -name z_spec zspec' \
                    icmd1='replacecol zspec_ref -name Ref_z_spec zspec_ref' \
                    icmd1='replacecol SFR_IR -name SFR SFR_IR' \
                    icmd1='replacecol eSFR_IR -name E_SFR eSFR_IR' \
                    icmd1='addcol Type_z "E_z==0 ? \"spec-z from Ref_z_spec\" : \"photo-z optimized for AGN and FIR and mm\""' \
                    icmd1='keepcols "ID RA Dec z E_z Type_z z_phot z_spec Ref_z_spec Mstar SFR E_SFR"' \
                    values1='RA Dec' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='RA Dec' \
                    suffix2='_Master' \
                    \
                    matcher=sky \
                    params=1.0 \
                    multimode=pairs \
                    iref=1 \
                    join1=match \
                    join2=match \
                    fixcols=all \
                    out='tmp_Jin2018_photoz_xmatch_backward.fits'
    fi
    
    
    # 
    # Now we cross-match the Delvecchio2017 Catalog for photo-z data
    # here we need the backward cross-matching
    # 
    if [[ ! -f 'tmp_Delvecchio2017_photoz_xmatch_backward.fits' ]]; then
    topcat -stilts tmatchn nin=2 \
                    in1='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_VLA_Delvecchio2017/VLA_3GHz_counterpart_array_20170210_paper_delvecchio_et_al.fits' \
                    ifmt1=fits \
                    icmd1="replacecol RA_VLA3 -name \"RA\" RA_VLA3" \
                    icmd1="replacecol DEC_VLA3 -name \"Dec\" DEC_VLA3" \
                    icmd1="replacecol ID_VLA3 -name \"ID\" ID_VLA3" \
                    icmd1='replacecol Z_BEST -name z Z_BEST' \
                    icmd1='replacecol Z_TYPE -name Type_z "(Z_TYPE==\"spec\") ? \"spec-z\" : ((Z_TYPE==\"phot\") ? \"photo-z\" : Z_TYPE) "' \
                    icmd1='replacecol SFR_IR -name SFR SFR_IR' \
                    icmd1='addcol Flag_Xray_AGN "XRAY_AGN==1"' \
                    icmd1='addcol Flag_midIR_AGN "MIR_AGN==1"' \
                    icmd1='addcol Flag_SED_AGN "SED_AGN==1"' \
                    icmd1='addcol Flag_Radio_excess "Radio_excess==1"' \
                    icmd1='keepcols "ID RA Dec z Type_z SFR Flag_Xray_AGN Flag_midIR_AGN Flag_SED_AGN Flag_Radio_excess"' \
                    values1='RA Dec' \
                    suffix1='' \
                    \
                    in2='/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20180325a.fits' \
                    icmd2='replacecol RA -desc "corrected for astrometry: Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA" "Origin==1 ? RA-0.09/3600.0/cos(Dec/180.0*PI) : RA"' \
                    icmd2='replacecol Dec -desc "corrected for astrometry: Origin==1 ? Dec-0.015/3600.0 : RA" "Origin==1 ? Dec-0.015/3600.0 : Dec"' \
                    icmd2='keepcols "ID RA Dec Origin ID_Origin"' \
                    values2='RA Dec' \
                    suffix2='_Master' \
                    \
                    matcher=sky \
                    params=1.0 \
                    multimode=pairs iref=1 \
                    join1=always \
                    join2=match \
                    fixcols=all \
                    out='tmp_Delvecchio2017_photoz_xmatch_backward.fits'
    fi
    
    
    # 
    # OK, now we merge all prior redshift catalogs and solve the multiplicity!
    # 
    echo ""
    echo "Running \"./a_dzliu_patch_code_set_prior_redshifts_v2.py\"!"
    ./a_dzliu_patch_code_set_prior_redshifts_v2.py \
    -pcat "$output_cat.photometry.fits" \
    -zcat \
        'tmp_Salvato2017_specz_xmatch_backward.fits' \
        'tmp_Salvato2011_Chandra_photoz_xmatch_backward.fits' \
        'tmp_Salvato2011_XMM_photoz_xmatch_backward.fits' \
        'tmp_Laigle2016_photoz_xmatch_backward.fits' \
        'tmp_Davidzon2017_photoz_xmatch_backward.fits' \
        'tmp_Delvecchio2017_photoz_xmatch_backward.fits' \
        'tmp_Jin2018_photoz_xmatch_backward.fits' \
    -zname \
        'Salvato2017_specz' \
        'Salvato2011_Chandra_photoz' \
        'Salvato2011_XMM_photoz' \
        'Laigle2016_photoz' \
        'Davidzon2017_photoz' \
        'Delvecchio2017_photoz' \
        'Jin2018_photoz' \
    -out "$output_cat.photometry_with_prior_redshifts.fits"
    
    
    topcat -stilts tpipe \
                   in="$output_cat.photometry_with_prior_redshifts.fits" \
                   ifmt=fits \
                   omode=meta \
                   | tee "$output_cat.photometry_with_prior_redshifts.meta.txt"
                   # meta
    
fi






















