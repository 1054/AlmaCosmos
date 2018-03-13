#!/bin/bash
# 

rm concat_simulation_catalogs.txt

find "." -name "Size*_SN*_number*_catalog.txt" -print0 | \
while IFS='' read -r -d $'\0' line; do 
Image=$(basename $(dirname $(dirname "$line")))
Simu=$(basename "$line" | sed -e 's/_catalog.txt$//g')
Dir=$(dirname "$line")
hdr_prepend=$(printf "# %50s   %60s \n" "Image" "Simu")
str_prepend=$(printf "  %50s   %60s \n" "$Image" "$Simu")
echo "$str_prepend"
if [[ ! -f concat_simulation_catalogs.txt ]]; then
cat "$line" | head -n 1 | sed -e "s/^# /$hdr_prepend   /g" > concat_simulation_catalogs.txt
fi
cat "$line" | grep -v "^#" | sed -e "s/^/$str_prepend   /g" >> concat_simulation_catalogs.txt
done



