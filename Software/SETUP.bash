#!/bin/bash
#

BIN_SETUP_FOLDER=$(dirname "${BASH_SOURCE[0]}")
BIN_SETUP_SCRIPT=$(dirname "${BASH_SOURCE[0]}")/bin_setup.bash

# Supermongo
if [[ -d "$HOME/Softwares/Supermongo" ]]; then
    source "$BIN_SETUP_SCRIPT" -var PATH -prepend -path "$HOME/Softwares/Supermongo"
fi

# Python lib
if [[ -d "$BIN_SETUP_FOLDER/lib_python_dzliu/crabtable" ]]; then
    source "$BIN_SETUP_SCRIPT" -var PYTHONPATH -path "$BIN_SETUP_FOLDER/lib_python_dzliu/crabtable"
fi

# PyBDSF
# if [[ $(uname) == "Darwin" ]]; then
#     if [[ -d "$BIN_SETUP_FOLDER/3rd_pybdsf/mac_python2.7/lib/python2.7/site-packages/bdsf-1.8.13-py2.7-macosx-10.12-x86_64.egg/bdsf" ]]; then
#         source "$BIN_SETUP_SCRIPT" -var PATH                -path "$BIN_SETUP_FOLDER/3rd_pybdsf/mac_python2.7/bin"
#         source "$BIN_SETUP_SCRIPT" -var PYTHONPATH          -path "$BIN_SETUP_FOLDER/3rd_pybdsf/mac_python2.7/lib/python2.7/site-packages"
#         source "$BIN_SETUP_SCRIPT" -var PYTHONPATH          -path "$BIN_SETUP_FOLDER/3rd_pybdsf/mac_python2.7/lib/python2.7/site-packages/bdsf-1.8.13-py2.7-macosx-10.12-x86_64.egg"
#         source "$BIN_SETUP_SCRIPT" -var DYLD_LIBRARY_PATH   -path "$BIN_SETUP_FOLDER/3rd_pybdsf/mac_python2.7/lib"
#     fi
# else
#     if [[ -d "$BIN_SETUP_FOLDER/3rd_pybdsf/linux_python2.7/lib/python2.7/site-packages/bdsf-1.8.13-py2.7-linux-10.12-x86_64.egg/bdsf" ]]; then
#         source "$BIN_SETUP_SCRIPT" -var PATH                -path "$BIN_SETUP_FOLDER/3rd_pybdsf/linux_python2.7/bin"
#         source "$BIN_SETUP_SCRIPT" -var PYTHONPATH          -path "$BIN_SETUP_FOLDER/3rd_pybdsf/linux_python2.7/lib/python2.7/site-packages"
#         source "$BIN_SETUP_SCRIPT" -var PYTHONPATH          -path "$BIN_SETUP_FOLDER/3rd_pybdsf/linux_python2.7/lib/python2.7/site-packages/bdsf-1.8.13-py2.7-linux-10.12-x86_64.egg"
#         source "$BIN_SETUP_SCRIPT" -var DYLD_LIBRARY_PATH   -path "$BIN_SETUP_FOLDER/3rd_pybdsf/linux_python2.7/lib"
#     fi
# fi

# Check commands
source "$BIN_SETUP_SCRIPT" -check gethead getpix sky2xy xy2sky galfit lumdist sm


