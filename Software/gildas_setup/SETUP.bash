#!/bin/bash
#
export GAG_TOP_DIR=$(dirname $(perl -MCwd -e 'print Cwd::abs_path shift' ${BASH_SOURCE[0]}))
export GAG_SUB_DIR="gildas-exe-jan21a"

# allow user to input gildas version
if [[ $# -ge 1 ]]; then
    if [[ -d "$GAG_TOP_DIR/gildas-exe-$1" ]]; then
        echo "Setting GILDAS version $1 according to user input"
        export GAG_SUB_DIR="gildas-exe-$1"
    fi
fi

export GAG_ROOT_DIR=$(perl -MCwd -e 'print Cwd::abs_path shift' "$GAG_TOP_DIR/$GAG_SUB_DIR")
export GAG_EXEC_SYSTEM="x86_64-ubuntu17.10-gfortran" # $(ls -1 "$GAG_TOP_DIR/$GAG_SUB_DIR/" | grep gfortran)
if [[ -z "$GAG_EXEC_SYSTEM" ]]; then export GAG_EXEC_SYSTEM=$(ls -1 "$GAG_TOP_DIR/$GAG_SUB_DIR/" | grep ifort); fi
if [[ -z "$GAG_EXEC_SYSTEM" ]]; then echo "Error! Could not determine \$GAG_EXEC_SYSTEM from sub-directories: "$(ls "$GAG_TOP_DIR/$GAG_SUB_DIR/"); exit 255; fi
echo export GAG_ROOT_DIR=$GAG_ROOT_DIR
echo export GAG_EXEC_SYSTEM=$GAG_EXEC_SYSTEM
source "$GAG_TOP_DIR/bin/bin_setup.bash" -path "$GAG_TOP_DIR/$GAG_SUB_DIR/$GAG_EXEC_SYSTEM/bin" -check astro class mapping -clear '*gildas-exe-*' #-debug
source "$GAG_TOP_DIR/$GAG_SUB_DIR/etc/bash_profile" # > /dev/null

type astro class mapping

if [[ x"$GAG_ROOT_DIR" == x ]]; then
    echo "Error! Failed to source \"$GAG_TOP_DIR/$GAG_SUB_DIR/etc/bash_profile\"!"
    return
fi




# 
# Print version info if in interactive shell
if [[ $- =~ "i" ]]; then
    mapping -v
fi


