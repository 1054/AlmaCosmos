#!/bin/bash
# 

set -e 


if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry! This code only works on aida42198!"
    exit
fi


echo ""
echo "This code will merge all the sim-rec-cross-matched catalogs into a big catalog"
echo ""
echo "Sleeping for 5 seconds then start ..."
sleep 5
echo ""


source $(dirname $(dirname $(dirname $(dirname "${BASH_SOURCE[0]}"))))/Softwares/SETUP.bash


cd /disk1/ALMA_COSMOS/A3COSMOS/simulations/

if [[ ! -d statistics_PyBDSM ]]; then echo "Error! \"statistics_PyBDSM\" does not exist!"; exit 255; fi

cd statistics_PyBDSM

find . -name "output_*.txt"



