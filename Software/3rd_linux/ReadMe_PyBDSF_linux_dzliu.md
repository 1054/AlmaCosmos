
### About PyBDSF ###

PyBDSF (or PyBDSM) is an astronomical image blob detection tool. See [http://www.astron.nl/citt/pybdsf](http://www.astron.nl/citt/pybdsf).



### How to compile PyBDSF (on Linux) ###

This is how we compile and install PyBDSF into our 'Crab.Toolkit.CAAP' directory. We use "--prefix" to specify the target directory. 

First, install necessary python package dependencies. 

```
pip2.7 install --ignore-installed --install-option "--prefix=$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/" pyfits pywcs backports.shutil_get_terminal_size
```

Here we assume that you alread have 'numpy', 'scipy' in your python path. 

Before next step, if you have IRAF, remove "/PATH/TO/IRAF/iraf.macx.x86_64/" otherwise the f77.sh in the IRAF directory will cause error. 

Then, clone the PyBDSF code from github, then compile and install. 

```
git clone https://github.com/lofar-astron/PyBDSF.git
cd PyBDSF
rm -rf build/
locate "boost/python.h"
export PYTHONPATH="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/lib/python2.7/site-packages:$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/lib64/python2.7/site-packages"
python2.7 setup.py build_ext --inplace --include-dirs="/usr/include" --library-dirs="/usr/lib/gcc:/usr/lib" install --prefix="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux"
```

Then, we still need to copy some library files manually

```
# Be careful about the version
grep "__version" bdsf/_version.py
__version__ = '1.8.13'

cp bdsf/*.so        "$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/lib64/python2.7/site-packages/bdsf-1.8.13-py2.7-linux-x86_64.egg/bdsf/"
cp bdsf/nat/*.so    "$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/lib64/python2.7/site-packages/bdsf-1.8.13-py2.7-linux-x86_64.egg/bdsf/nat/"
```



### How to use PyBDSF ###

```
export PYTHONPATH="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/lib/python2.7/site-packages:$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_linux/lib64/python2.7/site-packages"
python2.7
```

```python
import numpy
import scipy
import bdsf

```





### 2017-11-08 Modified the source code to allow setting 'ngmax' ### 

vim lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg/bdsf/opts.py
#--> changed "ini_gaussfit = Enum(" to "ini_gaussfit = String("

vim lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg/bdsf/gausfit.py
#--> added ini_gausfit 'ngmax *'









