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
    print('Usage: alma_archive_make_data_dirs_with_meta_table.py "meta_table_file.txt"')
    sys.exit()

meta_table_file = ''
some_option = ''
output_full_table = True
verbose = 0
i = 1
while i < len(sys.argv):
    tmp_arg = re.sub(r'^-+', r'', sys.argv[i].lower())
    if tmp_arg == 'some-option': 
        i = i+1
        if i < len(sys.argv):
            some_option = sys.argv[i]
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

Dataset_dirname = None
if 'Dataset_dirname' in meta_table.colnames:
    Dataset_dirname = meta_table['Dataset_dirname']

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



output_table = meta_table.copy()
output_table['Dataset_dirname'] = np.array(['']*len(output_table), dtype="object")
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
    # check Level_1_Raw dir
    if os.path.isdir('Level_1_Raw'):
        # 
        # try to find downloaded tar files
        if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 5):
            #t_found_fileset = formic.FileSet(include='Level_1_Raw/**/*'+t_Dataset_name+'.tar')
            #t_found_files = []
            #for t_found_fileitem in t_found_fileset.qualified_files(absolute=False):
            #    t_found_files.append(t_found_fileitem)
            t_found_files = glob2.glob('Level_1_Raw/**/*'+t_Dataset_name+'.tar')
        else:
            t_found_files = glob.glob('Level_1_Raw/**/*'+t_Dataset_name+'.tar', recursive=True)
        if verbose >= 1 :
            print('Searching for '+'Level_1_Raw/**/*'+t_Dataset_name+'.tar')
            print(t_found_files)
        if len(t_found_files) > 1:
            print('Warning! Found multiple dataset dirs for "Level_1_Raw/**/*'+t_Dataset_name+'.tar"!')
        if len(t_found_files) > 0:
            output_table['Downloaded'][i] = True
        # 
        # try to find unpacked raw data dirs
        if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 5):
            #t_found_fileset = formic.FileSet(include='Level_1_Raw/**/*'+t_Dataset_name)
            #t_found_dirs = []
            #for t_found_fileitem in t_found_fileset.qualified_files(absolute=False):
            #    t_found_dirs.append(t_found_fileitem)
            t_found_dirs = glob2.glob('Level_1_Raw/**/*'+t_Dataset_name, recursive=True)
        else:
            t_found_dirs = glob.glob('Level_1_Raw/**/*'+t_Dataset_name, recursive=True)
        if verbose >= 1 :
            print('Searching for '+'Level_1_Raw/**/*'+t_Dataset_name)
            print(t_found_dirs)
        if len(t_found_dirs) > 1:
            print('Warning! Found multiple dataset dirs for "Level_1_Raw/**/*'+t_Dataset_name+'"!')
        if len(t_found_dirs) > 0:
            output_table['Downloaded'][i] = True
            output_table['Unpacked'] = True
            # 
            # check Level_2_Calib dir
            if not os.path.isdir('Level_2_Calib'):
                os.mkdir('Level_2_Calib')
            # 
            # loop Level_2_Calib dirs
            for t_found_dir in t_found_dirs:
                # 
                # prepare Dataset dirname
                # -- if there are multiple dirs for each t_Dataset_name
                t_Dataset_ID_digits = min(np.ceil(np.log10(len(output_table))), 2) # count digits and format the ID of each DataSet. 
                # 
                # set Dataset_dirname
                if t_Dataset_ID_digits < 2: t_Dataset_ID_digits = 2
                if len(t_found_dirs) > 1:
                    t_Dataset_dirname = ('DataSet_%%0%dd_%d'%(t_Dataset_ID_digits, t_found_dirs.index(t_found_dir)+1))%(i+1)
                else:
                    t_Dataset_dirname = ('DataSet_%%0%dd'%(t_Dataset_ID_digits))%(i+1)
                # 
                # set Dataset_dirname if it exists in the meta table
                if Dataset_dirname is not None:
                    if len(Dataset_dirname) > i:
                        if Dataset_dirname[i] != '':
                            t_Dataset_dirname = Dataset_dirname[i]
                output_table['Dataset_dirname'][i] = t_Dataset_dirname
                # 
                # -- if the project is VLA or ALMA
                if t_Project_code.startswith('VLA'):
                    t_Dataset_link = 'Level_2_Calib/'+t_Dataset_dirname+'/raw'
                    t_Dataset_link2 = 'Level_2_Calib/'+t_Dataset_dirname+'/calibrated/'+os.path.basename(t_found_dir)
                    # make link (including parenet dirs)
                    my_function_to_make_symbolic_link('../../'+t_found_dir, t_Dataset_link, verbose=verbose)
                    my_function_to_make_symbolic_link('../../../'+t_found_dir, t_Dataset_link2, verbose=verbose)
                    # 
                    # check calibration script
                    t_Dataset_calib_script = 'Level_2_Calib/'+t_Dataset_dirname+'/calibrated/'+'scriptForDatasetRecalibration.py'
                    if not os.path.isfile(t_Dataset_calib_script):
                        t_EVLA_calib_script = os.getenv('HOME')+os.sep+'Softwares/CASA/Portable/EVLA_pipeline1.4.0_for_CASA_5.0.0/EVLA_pipeline.py'
                        t_CASA_setup_script = os.getenv('HOME')+os.sep+'Softwares/CASA/SETUP.bash'
                        t_CASA_dir = os.getenv('HOME')+os.sep+'Softwares/CASA/Portable/casa-release-5.0.0-218.el6'
                        t_CASA_version = '5.0.0'
                        if os.path.isfile(t_EVLA_calib_script) and os.path.isdir(t_CASA_dir) and os.path.isfile(t_CASA_setup_script):
                            if verbose >= 1:
                                print('Writing calibration script "%s"'%(t_Dataset_calib_script))
                            with open(t_Dataset_calib_script, 'w') as fp:
                                fp.write('#!/usr/bin/env python\n')
                                fp.write('SDM_name = \'%s\'\n'%(os.path.basename(t_found_dir)))
                                fp.write('mymodel = \'y\'\n')
                                fp.write('myHanning = \'n\'\n')
                                fp.write('execfile(\'/home/dzliu/Softwares/CASA/Portable/EVLA_pipeline1.4.0_for_CASA_5.0.0/EVLA_pipeline.py\')\n')
                                fp.write('')
                            with open(re.sub(r'\.py$', r'.sh', t_Dataset_calib_script), 'w') as fp:
                                fp.write('\n')
                                fp.write('source \"%s\" %s\n'%(t_CASA_setup_script, t_CASA_version))
                                fp.write('cd \"%s/%s\"\n'%(os.getcwd(), os.path.dirname(t_Dataset_calib_script)))
                                fp.write('pwd\n')
                                fp.write('casa -c \"%s\"\n'%(os.path.basename(t_Dataset_calib_script)))
                                fp.write('')
                            os.system('chmod +x "%s"'%(re.sub(r'\.py$', r'.sh', t_Dataset_calib_script)))
                else:
                    t_Dataset_link = 'Level_2_Calib/'+t_Dataset_dirname
                    # make link (including parenet dirs)
                    my_function_to_make_symbolic_link('../../'+t_found_dir, t_Dataset_link, verbose=verbose)
                # 
                # check Dataset link
                #print(t_Dataset_link)
                # 
                # check Dataset raw dir
                if verbose >= 2:
                    print('Checking '+'Level_2_Calib/'+t_Dataset_dirname+'/raw')
                if len(os.listdir('Level_2_Calib/'+t_Dataset_dirname+'/raw')) == 0:
                    output_table['Unpacked'][i] = False
                # 
                # check Dataset calibrated dir
                if verbose >= 2:
                    print('Checking '+'Level_2_Calib/'+t_Dataset_dirname+'/calibrated/*.ms')
                if os.path.isdir('Level_2_Calib/'+t_Dataset_dirname+'/calibrated'):
                    t_found_ms = glob.glob('Level_2_Calib/'+t_Dataset_dirname+'/calibrated/*.ms')
                    if len(t_found_ms) > 0:
                        output_table['Calibrated'][i] = True
                ## 
                ## check calibrated dir
                #t_found_dirs3 = glob.glob(Project_code+'/science_goal.*/group.*/member.'+t_Dataset_name+'/'+'calibrated'+'/'+'*.ms')
                #if len(t_found_dirs3) > 0:
                #    output_table['Calibrated'][i] = True
                ## check imaged fits files
                #t_found_dirs3 = glob.glob('imaging/'+t_Galaxy_name.lower()+'/'+t_Galaxy_name+'_'+t_Array+'_*.fits')
                #if len(t_found_dirs3) > 0:
                #    output_table['Calibrated'][i] = True
    
        
        
print(output_table)







