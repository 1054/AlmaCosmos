#!/usr/bin/env fish
# 


set BIN_SETUP_SCRIPT (dirname (status --current-filename))/bin_setup.bash

#echo 
#echo "PATH = $PATH"
#echo 

set -x PATH (string split ":" (bash -c "source $BIN_SETUP_SCRIPT -print" | tail -n 1))

type a3cosmos-prior-extraction-photometry

#echo 
#echo "PATH = $PATH"
#echo 


