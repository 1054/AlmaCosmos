#!/bin/bash
# 

# 
# About PyBDSF
# 
# PyBDSF (or PyBDSM) is an astronomical image blob detection tool. 
# See [http://www.astron.nl/citt/pybdsf](http://www.astron.nl/citt/pybdsf).



# How to compile PyBDSF

#py_version=$(/usr/bin/env python --version | sed -e 's/Python //g' | cut -b 1-3)
py_version="2.7" # PyBDSF only works with Python 2.7 for now, 
echo "py_version=$py_version"
if [[ $(uname) == "Darwin" ]]; then
    os_system="mac"
else
    os_system="linux"
fi

py_prefix=$(cd $(dirname "${BASH_SOURCE[0]}"); pwd)"/${os_system}_python${py_version}"
echo "py_prefix=${py_prefix}"

if [[ ! -d "${py_prefix}/lib" ]]; then
    mkdir -p "${py_prefix}/lib"
fi

if [[ $(type pip-$py_version 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "Error! pip-$py_version was not found!"
    exit
fi

#
# Then install necessary python packages
# 
if [[ ! -d "${py_prefix}/lib/python$py_version/site-packages/pyfits" ]]; then
echo "pip-$py_version install --ignore-installed --prefix=\"${py_prefix}\" numpy scipy pyfits pywcs backports.shutil_get_terminal_size"
pip-$py_version install --ignore-installed --prefix="${py_prefix}" numpy scipy pyfits pywcs backports.shutil_get_terminal_size
fi

# 
# Here we assume that you alread have 'numpy', 'scipy' in your python path. 
# 

# 
# Before next step, if you have IRAF, remove "/PATH/TO/IRAF/iraf.macx.x86_64/" otherwise the f77.sh in the IRAF directory will cause error. 
# 

# 
# Then, clone the PyBDSF code from github, then compile and install. 
# 
if [[ ! -d "PyBDSF" ]]; then
    echo "git clone https://github.com/lofar-astron/PyBDSF.git"
    git clone https://github.com/lofar-astron/PyBDSF.git
fi
if [[ 1 == 1 ]]; then
    cd "PyBDSF"
    rm -rf build/
    rm PyBDSF/bdsf/_cbdsm.so
    export PATH=".:/opt/local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    export PYTHONPATH="${py_prefix}/lib/python$py_version/site-packages"
    #export LD_LIBRARY_PATH="../${os_system}_python${py_version}/lib"
    if [[ $(uname) == "Darwin" ]]; then
        # 
        # Install boost library version 1.59 using Brew under MacOS
        # 
        #if [[ ! -d "/usr/local/opt/boost@1.59/include" ]]; then
        #    #/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        #    brew install boost@1.59 --with-python # CAN NOT USE VERSION HIGHER THAN 1.65 (https://github.com/rdkit/rdkit/issues/1581)
        #    brew install boost-python@1.59
        #    brew list boost
        #    brew list boost-python
        #fi
        #
        # Then copy boost library
        # 
        if [[ ! -f "${py_prefix}/lib/libboost_regex.dylib" ]]; then
            echo "cp /usr/local/opt/boost@1.59/lib/*.dylib ${py_prefix}/lib/"
            cp /usr/local/opt/boost@1.59/lib/*.dylib ${py_prefix}/lib/
        fi
        if [[ ! -f "${py_prefix}/lib/libboost_python-mt.dylib" ]]; then
            echo "cp /usr/local/opt/boost-python@1.59/lib/*.dylib ${py_prefix}/lib/"
            cp /usr/local/opt/boost-python@1.59/lib/*.dylib ${py_prefix}/lib/
        fi
        # 
        if [[ ! -f "${py_prefix}/lib/libboost_python-mt.dylib" ]]; then
            echo "cp /opt/local/lib/libgcc/{libgcc_s.1.dylib,libgfortran.3.dylib,libquadmath.0.dylib} ${py_prefix}/lib/"
            cp /opt/local/lib/libgcc/{libgcc_s.1.dylib,libgfortran.3.dylib,libquadmath.0.dylib} ${py_prefix}/lib/
        fi
        chmod +w "${py_prefix}/lib/libboost_python-mt.dylib"
        install_name_tool -id "@loader_path/../../../../libboost_python-mt.dylib" "${py_prefix}/lib/libboost_python-mt.dylib"
        otool -L "${py_prefix}/lib/libboost_python-mt.dylib"
        # 
        if [[ ! -f "${py_prefix}/lib/libgfortran.a" ]]; then
            echo "cp /opt/local/lib/gcc48/libgfortran.a ${py_prefix}/lib/"
            cp /opt/local/lib/gcc48/libgfortran.a ${py_prefix}/lib/
        fi
        # 
        if [[ ! -d "include" ]]; then
            mkdir "include"
            echo "cp -r /usr/local/opt/boost@1.59/include/boost include/"
            cp -r /usr/local/opt/boost@1.59/include/boost include/
        fi
        # 
        # Then compile
        # 
        echo "python$py_version setup.py build_ext"
        python$py_version setup.py build_ext --inplace --include-dirs="include" --library-dirs="../${os_system}_python${py_version}/lib" --rpath "../${os_system}_python${py_version}/lib" install --prefix="${py_prefix}"
        #python$py_version setup.py build_ext --inplace --include-dirs="include:/opt/local/include" --library-dirs="/usr/local/opt/boost-python@1.59/lib:/usr/local/opt/boost@1.59/lib:/opt/local/lib/gcc48:/opt/local/lib" install --prefix="${py_prefix}"
        # 
        # Then fix rpath and rebuild "bdsf/_cbdsm.so"
        # 
        /usr/bin/clang++ -bundle -undefined dynamic_lookup -Wl,-headerpad_max_install_names build/temp.macosx-10.12-x86_64-2.7/src/c++/Fitter_dn2g.o build/temp.macosx-10.12-x86_64-2.7/src/c++/Fitter_dnsg.o build/temp.macosx-10.12-x86_64-2.7/src/c++/Fitter_lmder.o build/temp.macosx-10.12-x86_64-2.7/src/c++/MGFunction1.o build/temp.macosx-10.12-x86_64-2.7/src/c++/MGFunction2.o build/temp.macosx-10.12-x86_64-2.7/src/c++/cbdsm_main.o build/temp.macosx-10.12-x86_64-2.7/src/c++/stat.o build/temp.macosx-10.12-x86_64-2.7/src/c++/num_util/num_util.o -Lsrc/minpack -Lsrc/port3 -L../${os_system}_python${py_version}/lib -lminpack -lport3 -lgfortran -lboost_python-mt -o "bdsf/_cbdsm.so"
        # 
        # Check 
        # 
        otool -L "bdsf/_cbdsm.so"
    else
        python$py_version setup.py build_ext --inplace --include-dirs="/usr/include" --library-dirs="/usr/lib/gcc:/usr/lib" install --prefix="${py_prefix}"
    fi
    cd "../"
fi

# 
# Then, we still need to copy some library files manually
# 
py_outdir=$(ls -1d "${py_prefix}/lib/python$py_version/site-packages/bdsf-"*".egg" | head -n 1)
echo cp -i PyBDSF/bdsf/*.so                      "${py_outdir}/bdsf/"
echo cp -i PyBDSF/bdsf/nat/*.so                  "${py_outdir}/bdsf/nat/"
cp -i PyBDSF/bdsf/*.so                           "${py_outdir}/bdsf/"
cp -i PyBDSF/bdsf/nat/*.so                       "${py_outdir}/bdsf/nat/"
#cp -i /usr/local/opt/boost-python@1.59/lib/*     "${py_prefix}/lib/"
#cp -i /opt/local/lib/libgcc/libgfortran.3.dylib  "${py_prefix}/lib/"
#cp -i /opt/local/lib/libgcc/libgcc_s.1.dylib     "${py_prefix}/lib/"
#cp -i /opt/local/lib/libgcc/libquadmath.0.dylib  "${py_prefix}/lib/"



#   ### How to use PyBDSF ###
#   
#   ```
#   export PYTHONPATH="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_mac/lib/python2.7/site-packages"
#   python2.7
#   ```
#   
#   ```python
#   import numpy
#   import scipy
#   import bdsf
#   
#   ```
#   
#   
#   
#   
#   
#   ### 2017-11-08 Modified the source code to allow setting 'ngmax' ### 
#   
#   vim lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg/bdsf/opts.py
#   #--> changed "ini_gaussfit = Enum(" to "ini_gaussfit = String("
#   
#   vim lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg/bdsf/gausfit.py
#   #--> added ini_gausfit 'ngmax *'









