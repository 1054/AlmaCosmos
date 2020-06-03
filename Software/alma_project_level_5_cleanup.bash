#!/bin/bash
# 

list_of_raw_dirs=($(find "Level_1_Raw" -maxdepth 1 -mindepth 1 -type d -name "*.*.*.*" ))
#list_of_split_dirs=($(find "Level_3_Split" -maxdepth 1 -mindepth 1 -type d -name "DataSet_*"))

echo "Please run this command by yourself:"
echo "rm -rf ${list_of_raw_dirs[@]}"
ecoo "rm -rf Level_3_Split/DataSet_*/split_*"
ecoo "rm -rf Level_4_Data_Images/*/DataSet_*/processing"

