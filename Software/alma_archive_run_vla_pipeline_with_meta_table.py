#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re, time, json 
# pkg_resources
#pkg_resources.require('astroquery')
#pkg_resources.require('keyrings.alt')
import astroquery
import requests
from astroquery.alma.core import Alma
import astropy.io.ascii as asciitable
from astropy.table import Table, Column
from datetime import datetime
from operator import itemgetter, attrgetter
import glob
import numpy as np

# try to overcome glob.glob recursive search issue
if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 5):
    #import formic
    import glob2


# 
# read input argument, which should be Member_ous_id
# 
if len(sys.argv) <= 1:
    print('Usage: alma_archive_run_vla_pipeline_with_meta_table.py "meta_table_file.txt"')
    sys.exit()

meta_table_file = ''
some_option = ''
output_full_table = True
EVLA_pipeline_path = '' # default
verbose = 0
i = 1
while i < len(sys.argv):
    tmp_arg = re.sub(r'^-+', r'', sys.argv[i].lower())
    if tmp_arg == 'some-option': 
        i = i+1
        if i < len(sys.argv):
            some_option = sys.argv[i]
    if tmp_arg == 'vla-pipeline-path': 
        i = i+1
        if i < len(sys.argv):
            EVLA_pipeline_path = sys.argv[i]
    elif tmp_arg == 'verbose': 
        verbose = verbose + 1
    else:
        meta_table_file = sys.argv[i]
    i = i+1
if meta_table_file == '':
    print('Error! No meta table file given!')
    sys.exit()


# 
# deal with sys.path
# 
#print(sys.path)
#sys.path.insert(0,os.path.dirname(os.path.abspath(sys.argv[0]))+'/Python/2.7/site-packages')
#print(sys.path)
#sys.exit()



# 
# check ~/Softwares/CASA/Portable/EVLA_pipeline1.4.0_for_CASA_5.0.0
# 
if EVLA_pipeline_path == '':
    if os.path.isdir(os.expanduer('~')+'/Softwares/CASA/Portable/EVLA_pipeline1.4.0_for_CASA_5.0.0'):
        EVLA_pipeline_path = os.expanduer('~')+'/Softwares/CASA/Portable/EVLA_pipeline1.4.0_for_CASA_5.0.0'
    else:
        print('Error! EVLA_pipeline_path not given! Please input -vla-pipeline-path!')
        sys.exit()



# 
# read meta table file
# 
meta_table = None
if meta_table_file.endswith('.fits'):
    meta_table = Table.read(meta_table_file)
else:
    try:
        meta_table = Table.read(meta_table_file, format='ascii.commented_header')
    except:
        try:
            meta_table = Table.read(meta_table_file, format='ascii')
        except:
            pass
if meta_table is None:
    print('Error! Failed to read the meta table file! Is it a fits catalog or ascii catalog?')
    sys.exit()

#print(meta_table)
#print(meta_table.colnames)

Project_code = None
if 'Project_code' in meta_table.colnames:
    Project_code = meta_table['Project_code']

Member_ous_id = None
if 'Member_ous_id' in meta_table.colnames:
    Member_ous_id = meta_table['Member_ous_id']

Source_name = None
if 'Source_name' in meta_table.colnames:
    Source_name = meta_table['Source_name']

Array = None
if 'Array' in meta_table.colnames:
    Array = meta_table['Array']

if Project_code is None or \
   Member_ous_id is None or \
   Source_name is None or \
   Array is None: 
    print('Error! The input meta data table should contain at least the following four columns: "Project_code" "Member_ous_id" "Source_name" "Array"!')
    sys.exit()



def my_function_to_make_symbolic_link(src, dst, verbose = 0):
    if os.path.islink(dst):
        #print(os.readlink(dst))
        #print(os.path.exists(dst))
        if not os.path.exists(dst):
            os.remove(dst)
        elif os.readlink(dst) != src:
            print('Rewriting the link "%s" which was linked to "%s".'%(dst, os.readlink(dst)))
            os.remove(dst)
    if not os.path.islink(dst):
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        if verbose >= 1 :
            print('Linking "%s" to "%s".'%(dst, src))
        os.symlink(src, dst)
        #print('ln -fsT "%s" "%s"'%(src, dst))
        #os.system('ln -fsT "%s" "%s"'%(src, dst))
    else:
        print('Found existing link "%s" to "%s".'%(dst, src))



# 
# check Level_2_Calib dir
# 
if not os.path.isdir('Level_2_Calib'):
    print('Error! Level_2_Calib does not exist! Please run \"alma_archive_make_data_dirs_with_meta_table.py\" first!')
    sys.exit()


# 
# cd Level_2_Calib and run EVLA_pipeline_path+os.sep+'EVLA_pipeline.py'
# 
output_table = meta_table.copy()
output_table['Downloaded'] = [False]*len(output_table)
output_table['Unpacked'] = [False]*len(output_table)
output_table['Calibrated'] = [False]*len(output_table)
output_table['Imaged'] = [False]*len(output_table)

for i in range(len(output_table)):
    t_Project_code = Project_code[i]
    t_Dataset_name = re.sub(r'[^a-zA-Z0-9._]', r'_', Member_ous_id[i])
    t_Source_name = re.sub(r'[^a-zA-Z0-9._+-]', r'_', Source_name[i])
    t_Source_name = re.sub(r'^_*(.*?)_*$', r'\1', t_Source_name)
    t_Array = Array[i]
    # reformat Source_name
    if re.match(r'[0-9]$', t_Source_name):
        t_Galaxy_name = t_Source_name
    else:
        t_Galaxy_name = t_Source_name
    # 
    # prepare Dataset dirname
    t_Dataset_ID_digits = np.ceil(np.log10(1.0*len(output_table))+1.0)
    if t_Dataset_ID_digits < 2: t_Dataset_ID_digits = 2
    t_Dataset_dirname = ('DataSet_%%0%dd'%(t_Dataset_ID_digits))%(i+1)
    # -- if there are multiple dirs for each t_Dataset_name
    t_found_dirs = glob.glob('Level_2_Calib/'+t_Dataset_dirname+'_*')
    if len(t_found_dirs) > 1:
        for t_found_dir in t_found_dirs:
            t_Dataset_dirname = ('DataSet_%%0%dd_%d'%(t_Dataset_ID_digits, t_found_dirs.index(t_found_dir)+1))%(i+1)
            # -- check dir
            if os.path.isdir('Level_2_Calib/'+t_Dataset_dirname+'/calibrated'):
                # 
                # check Dataset raw dir
                if len(os.listdir('Level_2_Calib/'+t_Dataset_dirname+'/calibrated')) > 0:
                    output_table['Unpacked'][i] = True
                    # 
                    # check Dataset calibrated dir
                    if os.path.isdir('Level_2_Calib/'+t_Dataset_dirname+'/calibrated'):
                        t_found_ms = glob.glob('Level_2_Calib/'+t_Dataset_dirname+'/calibrated/*.ms')
                        if len(t_found_ms) > 0:
                            output_table['Calibrated'][i] = True
                        else:
                            print('Ready to run calibration pipeline under "%s"'%('Level_2_Calib/'+t_Dataset_dirname+'/calibrated'))
                            current_dir = os.getcwd()
                            target_dir = 'Level_2_Calib/'+t_Dataset_dirname+'/calibrated'
                            #<TODO><20190113># 
                
    
        
    
print(output_table)







