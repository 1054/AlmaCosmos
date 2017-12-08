#!/usr/bin/env tcsh
# 

# -- https://serverfault.com/questions/139285/tcsh-path-of-sourced-file -- While this is possible in other shells, I don't see a way to do it in tcsh. 
echo \$_ = $_
echo \$0 = $0
if ( "$0" == "tcsh" ) then
    set TCSH_SCRIPT_PATH=`echo $_ | cut -d ' ' -f 2`
    set BIN_SETUP_SCRIPT=`dirname $TCSH_SCRIPT_PATH`/bin_setup.bash
else
    pwd
    set BIN_SETUP_SCRIPT="$HOME/Cloud/Github/AlmaCosmos/Softwares/bin_setup.bash" # `dirname $0`/bin_setup.bash
endif

#echo 
#echo "PATH = $PATH"
#echo 

setenv PATH `bash -c "source $BIN_SETUP_SCRIPT -print"`

if ( -d "$HOME/Softwares/Supermongo" ) then
    setenv PATH `bash -c "source $BIN_SETUP_SCRIPT -var PATH -path $HOME/Softwares/Supermongo -print"`
endif

if ( -d "lib_python_dzliu/crabtable" ) then
    setenv PYTHONPATH `bash -c "source $BIN_SETUP_SCRIPT -var PYTHONPATH -path lib_python_dzliu/crabtable -print"`
endif

type gethead
type getpix
type sky2xy
type xy2sky
type galfit
type lumdist
type sm

#echo 
#echo "PATH = $PATH"
#echo 


