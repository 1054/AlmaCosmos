
### About PyBDSF ###

PyBDSF (or PyBDSM) is an astronomical image blob detection tool. See [http://www.astron.nl/citt/pybdsf](http://www.astron.nl/citt/pybdsf).



### How to compile PyBDSF (on Mac) ###

This is how we compile and install PyBDSF into our 'Crab.Toolkit.CAAP' directory. We use "--prefix" to specify the target directory. 

First, install necessary python package dependencies. 

```
pip-2.7 install --ignore-installed --prefix="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd/" pyfits pywcs
pip-2.7 install --ignore-installed --prefix="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd/" backports.shutil_get_terminal_size
```

Here we assume that you alread have 'numpy', 'scipy' in your python path. 

Before next step, if you have IRAF, remove "/PATH/TO/IRAF/iraf.macx.x86_64/" otherwise the f77.sh in the IRAF directory will cause error. 

Then, clone the PyBDSF code from github, then compile and install. 

```
git clone https://github.com/lofar-astron/PyBDSF.git
cd PyBDSF
rm -rf build/
brew install boost --with-python
brew install boost-python
export PYTHONPATH="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd/lib/python2.7/site-packages"
python2.7 setup.py build_ext --inplace --include-dirs="/opt/local/include" --library-dirs="/opt/local/lib/gcc48:/opt/local/lib" install --prefix="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd"
```

Then, we still need to copy some library files manually

```
cp bdsf/*.so        "/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/3rd/lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg/bdsf/"
cp bdsf/nat/*.so    "/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/3rd/lib/python2.7/site-packages/bdsf-1.8.12-py2.7-macosx-10.12-x86_64.egg/bdsf/nat/"
```



### How to use PyBDSF ###

```
export PYTHONPATH="$HOME/Cloud/Github/AlmaCosmos/Softwares/3rd_mac/lib/python2.7/site-packages"
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









