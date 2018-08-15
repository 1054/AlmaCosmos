#!/bin/bash
# 
# Jin+2018 catalog contains some non-physical flux errors, they can not be used as upper limits!
# 


topcat -stilts tpipe \
               in='Selected_Sample_v20180720c.photometry_with_prior_redshifts.fits' \
               cmd='replacecol df_irac1_Jin2018 "(df_irac1_Jin2018>=1e6) ? 1e10 : df_irac1_Jin2018"' \
               cmd='replacecol df_irac2_Jin2018 "(df_irac2_Jin2018>=1e6) ? 1e10 : df_irac2_Jin2018"' \
               cmd='replacecol df_irac3_Jin2018 "(df_irac3_Jin2018>=1e6) ? 1e10 : df_irac3_Jin2018"' \
               cmd='replacecol df_irac4_Jin2018 "(df_irac4_Jin2018>=1e6) ? 1e10 : df_irac4_Jin2018"' \
               cmd='replacecol df_K_Jin2018 "(df_K_Jin2018>=1e6) || (f_K_Jin2018<1e-6) ? 1e10 : df_K_Jin2018"' \
               cmd='replacecol df24_Jin2018 "(df24_Jin2018>=1e6) || (f24_Jin2018<1e-6) ? 1e10 : df24_Jin2018"' \
               cmd='replacecol df_20cm_VLA_Jin2018 "(df_20cm_VLA_Jin2018>=1e3) || (f_20cm_VLA_Jin2018<1e-6) ? 1e10 : df_20cm_VLA_Jin2018"' \
               cmd='replacecol df100_Jin2018 "(f100_Jin2018<3.0*df100_Jin2018 && df100_Jin2018>=10) || (f100_Jin2018<1e-4) ? 1e10 : df100_Jin2018"' \
               cmd='replacecol df160_Jin2018 "(f160_Jin2018<3.0*df160_Jin2018 && df160_Jin2018>=15) || (f160_Jin2018<1e-4) ? 1e10 : df160_Jin2018"' \
               cmd='replacecol df250_Jin2018 "(f250_Jin2018<3.0*df250_Jin2018 && df250_Jin2018>=15) || (f250_Jin2018<1e-5) ? 1e10 : df250_Jin2018"' \
               cmd='replacecol df350_Jin2018 "(f350_Jin2018<3.0*df350_Jin2018 && df350_Jin2018>=20) || (f350_Jin2018<1e-5) ? 1e10 : df350_Jin2018"' \
               cmd='replacecol df500_Jin2018 "(f500_Jin2018<3.0*df500_Jin2018 && df500_Jin2018>=20) || (f500_Jin2018<1e-5) ? 1e10 : df500_Jin2018"' \
               cmd='replacecol df850_Jin2018 "(f850_Jin2018<3.0*df850_Jin2018 && df850_Jin2018>=10) || (f850_Jin2018<1e-5) ? 1e10 : df850_Jin2018"' \
               cmd='replacecol df1100_Jin2018 "(f1100_Jin2018<3.0*df1100_Jin2018 && df1100_Jin2018>=10) || (f1100_Jin2018<1e-5) ? 1e10 : df1100_Jin2018"' \
               cmd='replacecol df1200_Jin2018 "(f1200_Jin2018<3.0*df1200_Jin2018 && df1200_Jin2018>=10) || (f1200_Jin2018<1e-5) ? 1e10 : df1200_Jin2018"' \
               out='Selected_Sample_v20180720c.photometry_with_prior_redshifts.patched_20180414_18h53m.fits'







