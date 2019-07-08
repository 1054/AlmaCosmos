#!/usr/bin/fish
#
# Aim:
#    This code will add the directory of this toolkit into the PATH system variable. 
# 
# 
# BIN_SETUP_SCRIPT
if contains "Linux" (uname)
    set -x BIN_SETUP_SCRIPT1 (dirname (status --current-filename))/Software/bin_setup.bash
    set -x CRAB_TOOLKIT_DIR1 (dirname (status --current-filename))
    set -x BIN_SETUP_SCRIPT2 (dirname (status --current-filename))/Pipeline/bin_setup.bash
    set -x CRAB_TOOLKIT_DIR2 (dirname (status --current-filename))
end
if contains "Darwin" (uname)
    set -x BIN_SETUP_SCRIPT1 (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status --current-filename)))/Software/bin_setup.bash
    set -x CRAB_TOOLKIT_DIR1 (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status --current-filename)))
    set -x BIN_SETUP_SCRIPT2 (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status --current-filename)))/Pipeline/bin_setup.bash
    set -x CRAB_TOOLKIT_DIR2 (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status --current-filename)))
end
# 
# CHECK BIN_SETUP_SCRIPT
if [ x"$BIN_SETUP_SCRIPT1" = x"" ]
    exit 255
else
    #echo "$BIN_SETUP_SCRIPT1"
end
if [ x"$BIN_SETUP_SCRIPT2" = x"" ]
    exit 255
else
    #echo "$BIN_SETUP_SCRIPT2"
end
#
# SET PATH USING BIN_SETUP_SCRIPT
if not contains "$CRAB_TOOLKIT_DIR1" $PATH
    set -gx PATH (string split ":" (bash -c "source $BIN_SETUP_SCRIPT1 -print" | tail -n 1))
end
if not contains "$CRAB_TOOLKIT_DIR2" $PATH
    set -gx PATH (string split ":" (bash -c "source $BIN_SETUP_SCRIPT2 -print" | tail -n 1))
end


