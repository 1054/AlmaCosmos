#!/usr/bin/env python
#
import os, sys
sys.path.append('/Users/dzliu/Cloud/Github/AlmaCosmos/Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
os.chdir('/Users/dzliu/Cloud/Github/AlmaCosmos/Tests/Test_Prior_Source_Fitting/Prior_source_fitting_test')
from CrabTable import CrabTable
Cat = CrabTable('/Users/dzliu/Work/AlmaCosmos/Catalogs/COSMOS_Master_Catalog_20170426/master_catalog_single_entry_with_Flag_Outlier_with_ZPDF_with_MASS_v20171107a.fits')
if Cat:
    Cat_ID = Cat.getColumn(1)
    Cat_RA = Cat.getColumn(2)
    Cat_DEC = Cat.getColumn(3)
    if len(Cat_ID)>0 and len(Cat_RA)>0 and len(Cat_DEC)>0:
        Cat_ID = Cat_ID.astype(str)
        Cat_RA = Cat_RA.astype(float)
        Cat_DEC = Cat_DEC.astype(float)
        Cat_MASK = [0 for x in Cat_DEC]
        with open('astrodepth_prior_extraction_photometry/astrodepth_catalog_0_ra_dec.txt', 'w') as fp:
            #fp.write('# %16s %18s\n'%('RA', 'Dec'))
            print('Writing %d rows to "%s"'%(
                   len(Cat_ID), 'astrodepth_prior_extraction_photometry/astrodepth_catalog_0_ra_dec.txt'))
            for i in range(len(Cat_ID)):
                fp.write('%18.7f %18.7f\n'%(Cat_RA[i], Cat_DEC[i]))
            fp.close()

        with open('astrodepth_prior_extraction_photometry/astrodepth_catalog_0_id_mask.txt', 'w') as fp:
            #fp.write('# %28s %18s\n'%('ID', 'Mask'))
            print('Writing %d rows to "%s"'%(
                   len(Cat_ID), 'astrodepth_prior_extraction_photometry/astrodepth_catalog_0_id_mask.txt'))
            for i in range(len(Cat_ID)):
                fp.write('%30s %18d\n'%(Cat_ID[i], Cat_MASK[i]))
            fp.close()

