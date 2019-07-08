#!/bin/bash
cd $(dirname "${BASH_SOURCE[0]}")
ds9 -lock frame image -mecube pybdsm_img_*.fits -frame 2 -regions load pybdsm_cat0.ds9.reg -regions showtext no -zoom to fit -saveimage eps pybdsm_cat0.ds9.eps
