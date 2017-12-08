#!/bin/bash
# 

if [[ "$USER" != "dzliu" ]]; then
    exit
fi


cd $(dirname "${BASH_SOURCE[0]}")

# Here I download necessary files

wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/astrodepth_abs_path                                     -O astrodepth_abs_path
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/astrodepth_command_line_arguments                       -O astrodepth_command_line_arguments
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/astrodepth_prior_extraction_photometry                  -O astrodepth_prior_extraction_photometry
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/astrodepth_prior_extraction_photometry_go_galfit.sm     -O astrodepth_prior_extraction_photometry_go_galfit.sm
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/astrodepth_prior_extraction_photometry_go_getpix.sm     -O astrodepth_prior_extraction_photometry_go_getpix.sm

wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/pixscale -O pixscale

wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/sky2xy  -O sky2xy
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/xy2sky  -O xy2sky
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/gethead -O gethead
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/sethead -O sethead
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/getpix  -O getpix

wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit -O galfit

wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/lumdist                   -O lumdist
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabFitsHeader            -O CrabFitsHeader
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabFitsImageCopy         -O CrabFitsImageCopy
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabFitsImageCrop         -O CrabFitsImageCrop
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabFitsImageArithmetic   -O CrabFitsImageArithmetic
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabPhotAperPhot          -O CrabPhotAperPhot
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabPhotImageStatistics   -O CrabPhotImageStatistics
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabTableReadInfo         -O CrabTableReadInfo
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/CrabTableReadColumn       -O CrabTableReadColumn

mkdir wcstools_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_mac/sky2xy  -O wcstools_mac/sky2xy
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_mac/xy2sky  -O wcstools_mac/xy2sky
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_mac/gethead -O wcstools_mac/gethead
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_mac/sethead -O wcstools_mac/sethead
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_mac/getpix  -O wcstools_mac/getpix

mkdir wcstools_linux_Glibc_2.14
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_linux_Glibc_2.14/sky2xy  -O wcstools_linux_Glibc_2.14/sky2xy
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_linux_Glibc_2.14/xy2sky  -O wcstools_linux_Glibc_2.14/xy2sky
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_linux_Glibc_2.14/gethead -O wcstools_linux_Glibc_2.14/gethead
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_linux_Glibc_2.14/sethead -O wcstools_linux_Glibc_2.14/sethead
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/wcstools_linux_Glibc_2.14/getpix  -O wcstools_linux_Glibc_2.14/getpix

mkdir galfit_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_mac/galfit    -O galfit_mac/galfit
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_mac/galfit30  -O galfit_mac/galfit30
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_mac/galfit255 -O galfit_mac/galfit255

mkdir galfit_linux_Glibc_2.12
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_linux_Glibc_2.12/galfit3redhat    -O galfit_linux_Glibc_2.12/galfit3redhat
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_linux_Glibc_2.12/galfit3redhat30  -O galfit_linux_Glibc_2.12/galfit3redhat30
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_linux_Glibc_2.12/galfit3redhat255 -O galfit_linux_Glibc_2.12/galfit3redhat255
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_linux_Glibc_2.12/libtinfo.so.5    -O galfit_linux_Glibc_2.12/libtinfo.so.5
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/galfit_linux_Glibc_2.12/libtinfo.so.5.9  -O galfit_linux_Glibc_2.12/libtinfo.so.5.9

mkdir ds9_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/lumdist_mac                   -O ds9_mac/lumdist_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabFitsHeader_mac            -O ds9_mac/CrabFitsHeader_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabFitsImageCopy_mac         -O ds9_mac/CrabFitsImageCopy_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabFitsImageCrop_mac         -O ds9_mac/CrabFitsImageCrop_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabFitsImageArithmetic_mac   -O ds9_mac/CrabFitsImageArithmetic_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabPhotAperPhot_mac          -O ds9_mac/CrabPhotAperPhot_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabPhotImageStatistics_mac   -O ds9_mac/CrabPhotImageStatistics_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabTableReadInfo_mac         -O ds9_mac/CrabTableReadInfo_mac
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_mac/CrabTableReadColumn_mac       -O ds9_mac/CrabTableReadColumn_mac

mkdir ds9_linux_Glibc_2.14
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/lumdist_linux_x86_64                   -O ds9_linux_Glibc_2.14/lumdist_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabFitsHeader_linux_x86_64            -O ds9_linux_Glibc_2.14/CrabFitsHeader_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabFitsImageCopy_linux_x86_64         -O ds9_linux_Glibc_2.14/CrabFitsImageCopy_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabFitsImageCrop_linux_x86_64         -O ds9_linux_Glibc_2.14/CrabFitsImageCrop_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabFitsImageArithmetic_linux_x86_64   -O ds9_linux_Glibc_2.14/CrabFitsImageArithmetic_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabPhotAperPhot_linux_x86_64          -O ds9_linux_Glibc_2.14/CrabPhotAperPhot_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabPhotImageStatistics_linux_x86_64   -O ds9_linux_Glibc_2.14/CrabPhotImageStatistics_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabTableReadInfo_linux_x86_64         -O ds9_linux_Glibc_2.14/CrabTableReadInfo_linux_x86_64
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/ds9_linux_Glibc_2.14/CrabTableReadColumn_linux_x86_64       -O ds9_linux_Glibc_2.14/CrabTableReadColumn_linux_x86_64

mkdir lib_python_dzliu
mkdir lib_python_dzliu/crabtable
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/lib_python_dzliu/crabtable/CrabTable.py   -O lib_python_dzliu/crabtable/CrabTable.py

wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/read_alma_fits_image_beam_area  -O read_alma_fits_image_beam_area
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/read_galfit_output_fits_result  -O read_galfit_output_fits_result
wget -q https://raw.githubusercontent.com/1054/DeepFields.SuperDeblending/master/Softwares/read_getpix_output_txt_result   -O read_getpix_output_txt_result

#wget -q 
#unzip 


chmod -R a+x *




