#!/bin/bash
# 

mkdir -p "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/"

rsync -avz -r --stats --progress -e "ssh" \
        --include '**/*' \
        "aida42198:/disk1/$USER/AlmaCosmos/S03_Photometry/ALMA_full_archive_Source_Extraction_by_Daizhong_Liu/ALMA_Calibrated_Images_by_Magnelli/" \
        "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/"



mkdir -p "/disk1/$USER/Works/AlmaCosmos/Photometry/ALMA_Calibrated_Images_by_Magnelli/"

rsync -avz -r --stats --progress -e "ssh" \
        --include '**/*' \
        "aida42198:/disk1/$USER/AlmaCosmos/S03_Photometry/ALMA_full_archive_Source_Extraction_by_Daizhong_Liu/Source_Extraction_by_Daizhong_Liu/" \
        "/disk1/$USER/Works/AlmaCosmos/Photometry/Source_Extraction_by_Daizhong_Liu/"


