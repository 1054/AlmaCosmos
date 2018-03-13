#!/bin/bash
# 

rm Read_Results_all_final_fit_2.result.all.txt

find "." -name "fit_2.result.all.txt" -print0 | \
while IFS='' read -r -d $'\0' line; do 
Image=$(basename $(dirname $(dirname $(dirname "$line"))))
Simu=$(basename $(dirname $(dirname "$line")))
Dir=$(dirname "$line")
hdr_prepend=$(printf "# %50s   %60s \n" "Image" "Simu")
str_prepend=$(printf "  %50s   %60s \n" "$Image" "$Simu")
echo "$str_prepend"
if [[ ! -f Read_Results_all_final_fit_2.result.all.txt ]]; then
cat "$Dir/fit_2.result.all.txt"         | head -n 1 | sed -e "s/^# /$hdr_prepend   /g" > Read_Results_all_final_fit_2.result.all.txt
cat "$Dir/fit_2.result.flux_origin.txt" | head -n 1 | sed -e "s/^# /$hdr_prepend   /g" > Read_Results_all_final_fit_2.result.flux_origin.txt
cat "$Dir/fit_2.result.source_err.txt"  | head -n 1 | sed -e "s/^# /$hdr_prepend   /g" > Read_Results_all_final_fit_2.result.source_err.txt
cat "$Dir/fit_2.result.source_area.txt" | head -n 1 | sed -e "s/^# /$hdr_prepend   /g" > Read_Results_all_final_fit_2.result.source_area.txt
fi
cat "$Dir/fit_2.result.all.txt"         | grep -v "^#" | sed -e "s/^/$str_prepend   /g" >> Read_Results_all_final_fit_2.result.all.txt
cat "$Dir/fit_2.result.flux_origin.txt" | grep -v "^#" | sed -e "s/^/$str_prepend   /g" >> Read_Results_all_final_fit_2.result.flux_origin.txt
cat "$Dir/fit_2.result.source_err.txt"  | grep -v "^#" | sed -e "s/^/$str_prepend   /g" >> Read_Results_all_final_fit_2.result.source_err.txt
cat "$Dir/fit_2.result.source_area.txt" | grep -v "^#" | sed -e "s/^/$str_prepend   /g" >> Read_Results_all_final_fit_2.result.source_area.txt
done



#source ~/Softwares/Topcat/bin_setup.bash

#~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-prior-extraction-photometry-read-results-more-tools/combine-prior-fitting-results-and-output-prior-fitting-catalog -date 2018-03-12a -gaussian



