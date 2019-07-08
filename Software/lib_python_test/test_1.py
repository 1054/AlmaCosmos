#!/usr/bin/env python
# 

import os, sys
sys.path.append('/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/lib_python')
sys.path.append('/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares/lib_python_dzliu')

from crabgaussian.CrabGaussian import *

from almacosmos_python_lib_highz import *


my_catalog = Highz_Catalogue('test_1_catalog.fits')
print(my_catalog)
print(my_catalog.id())
print(my_catalog.id_2())
#print(my_catalog.ra())
#print(my_catalog.ra_2())
#print(my_catalog.dec())
#print(my_catalog.dec_2())
#print(my_catalog.addCol('test', [100], InputDataType=float))
#print(my_catalog.calc_crowdedness(150.0, 02.0, input_fwhm=300.0))
print(my_catalog.about())
#print(my_catalog.save('test_1_catalog_saved.fits', overwrite=True))


my_galaxy = Highz_Galaxy()
