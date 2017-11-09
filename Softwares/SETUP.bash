#!/bin/bash
#
# CURRENT DIR
#export ALMACOSMOS=$(dirname $(perl -MCwd -e 'print Cwd::abs_path shift' "${BASH_SOURCE[0]}"))
export ALMACOSMOS=$(bash -c "cd \$(dirname \"${BASH_SOURCE[0]}\"); pwd -P;")
if [[ x"$ALMACOSMOS" = x"" ]]; then
    echo "Failed to source ${BASH_SOURCE[0]}!"; exit 1
fi
#
# PATH
if [[ $PATH != *"$ALMACOSMOS"* ]]; then
    export PATH="$ALMACOSMOS:$PATH"
fi
if [[ $PATH != *"$ALMACOSMOS/3rd/bin"* ]]; then
    export PATH="$ALMACOSMOS/3rd/bin:$PATH"
fi
if [[ x"$PYTHONPATH" != x*"$ALMACOSMOS/3rd/lib/python2.7/site-packages"* ]]; then
    if [[ -z "$PYTHONPATH" ]]; then
        export PYTHONPATH="$ALMACOSMOS/3rd/lib/python2.7/site-packages:$ALMACOSMOS/3rd/lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg"
    else
        export PYTHONPATH="$ALMACOSMOS/3rd/lib/python2.7/site-packages:$ALMACOSMOS/3rd/lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg:$PYTHONPATH"
    fi
fi
#
# LIST
ALMACOSMOSCMD=("almacosmos-sky-coverage" "almacosmos-fits-image-to-coverage-polyogn" "almacosmos-analyze-fits-image-pixel-histogram" "almacosmos-generate-PSF-Gaussian-2D" "almacosmos-highz-galaxy-crossmatcher" "almacosmos-highz-galaxy-crossmatcher-read-results")
# 
# CHECK
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
if [[ $- =~ "i" ]]; then 
  for TEMPTOOLKITCMD in ${ALMACOSMOSCMD[@]}; do
    type $TEMPTOOLKITCMD
  done
fi


