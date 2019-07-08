#!/usr/bin/env tcsh
#
# Aim:
#    This code will add the directory of this toolkit into the PATH system variable. 
# 


setenv BIN_SETUP_SCRIPT1 `dirname $0`/Software/bin_setup.bash
setenv BIN_SETUP_SCRIPT2 `dirname $0`/Pipeline/bin_setup.bash

setenv PATH `bash -c "source $BIN_SETUP_SCRIPT1 -print" | tail -n 1`
setenv PATH `bash -c "source $BIN_SETUP_SCRIPT2 -print" | tail -n 1`


