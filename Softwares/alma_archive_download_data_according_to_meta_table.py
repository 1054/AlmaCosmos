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





# 
# read input argument, which should be Member_ous_id
# 
if len(sys.argv) <= 1:
    print('Usage: alma_archive_download_data_according_to_meta_table.py "meta_table_file.txt" [--user dzliu] [--eso] [--out project_code.cache]')
    sys.exit()

meta_table_file = ''
some_option = ''
Login_user_name = ''
Use_alma_site = 'nrao'
output_dir = ''
verbose = 0
i = 1
while i < len(sys.argv):
    tmp_arg = re.sub(r'^[-]+', r'-', sys.argv[i].lower())
    if tmp_arg == '-some-option': 
        i = i+1
        if i < len(sys.argv):
            some_option = sys.argv[i]
    elif tmp_arg == '-user': 
        i = i+1
        if i < len(sys.argv):
            Login_user_name = sys.argv[i]
    elif tmp_arg == '-out': 
        i = i+1
        if i < len(sys.argv):
            output_dir = sys.argv[i]
    elif tmp_arg == '-eso': 
        Use_alma_site = 'eso'
    elif tmp_arg == '-verbose': 
        verbose = verbose + 1
    else:
        meta_table_file = sys.argv[i]
    i = i+1
if meta_table_file == '':
    print('Error! No meta table file given!')
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

if not ('Project_code' in meta_table.colnames) or \
   not ('Member_ous_id' in meta_table.colnames) or \
   not ('Source_name' in meta_table.colnames) or \
   not ('Dataset_dirname' in meta_table.colnames) or \
   not ('Array' in meta_table.colnames):
    print('Error! The input meta data table should contain at least the following four columns: "Project_code" "Member_ous_id" "Source_name" "Array"!')
    sys.exit()






# 
# Loop each row
# 
for i in range(len(meta_table)):
    # 
    # prepare output dir
    # 
    if output_dir == '':
        output_dir_path = meta_table['Project_code'][i]+'.cache'
    else:
        output_dir_path = output_dir
    # 
    # change dir
    # 
    current_dir_path = os.getcwd()
    print('os.chdir("%s")' % (output_dir_path) )
    os.chdir(output_dir_path)
    print('os.getcwd()', os.getcwd())
    # 
    # query by Member_ous_id
    # 
    # result = Alma.query_region(orionkl, radius=0.034*u.deg)
    # Member_ous_id = result['Member ous id']
    #Member_ous_id = 'uid://A001/X148/X119'
    Member_ous_id = meta_table['Member_ous_id'][i]
    Member_ous_name = Member_ous_id.replace(':','_').replace('/','_').replace('+','_')
    Output_name = 'alma_archive_download_tar_files_by_Mem_ous_id_%s'%(Member_ous_name)
    # 
    # check previous runs
    # 
    if os.path.isfile('%s.sh'%(Output_name)): 
        if os.path.isfile('%s.sh.done'%(Output_name)): 
            print('Found exisiting "%s.sh" and "%s.sh.done"! Will not re-run it!'%(Output_name,Output_name))
        else:
            print('Found exisiting "%s.sh"! But it seems not finished yet! Will launch it now!'%(Output_name))
            os.system('echo "" >> %s.log'%(Output_name))
            os.system('date +\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\" >> %s.log'%(Output_name))
            os.system('echo "" >> %s.log'%(Output_name))
            print('%s.sh >> %s.log'%(Output_name,Output_name))
            os.system('%s.sh >> %s.log'%(Output_name,Output_name))
        # 
        # cd back and continue
        # 
        print('os.chdir("%s")' % (current_dir_path) )
        os.chdir(current_dir_path)
        print('os.getcwd()', os.getcwd())
        continue
    
    # archive url
    # 'http://almascience.org',
    # 'https://almascience.eso.org',
    # 'https://almascience.nrao.edu',
    # 'https://almascience.nao.ac.jp',
    # 'https://beta.cadc-ccda.hia-iha.nrc-cnrc.gc.ca'
    if Use_alma_site == 'eso':
        Alma.archive_url = u'https://almascience.eso.org'
    else:
        Alma.archive_url = u'https://almascience.nrao.edu'
    
    # login
    if Login_user_name != '':
        print('Logging in as ALMA User "%s"'%(Login_user_name))
        Alma.login(Login_user_name, store_password=True)
    
    print('Staging data for Member ObservingUnitSet ID "%s"'%(Member_ous_id))
    uid_url_table = Alma.stage_data(Member_ous_id)
    print(uid_url_table)
    
    #filelist = Alma.download_and_extract_files(uid_url_table['URL'], regex='.*README$')
    #print(filelist)
    
    asciitable.write(uid_url_table, '%s.txt'%(Output_name), Writer=asciitable.FixedWidthTwoLine)
    os.system('date +"%%Y-%%m-%%d %%H:%%M:%%S %%Z" > %s.log'%(Output_name))
    os.system('echo "%s %s" >> %s.log'%(sys.argv[0],sys.argv[1],Output_name))
    
    for i in range(len(uid_url_table)):
        if i == 0:
            os.system('echo "#!/bin/bash" > %s.sh'%(Output_name))
            os.system('echo "" >> %s.sh'%(Output_name))
            os.system('echo "set -e" >> %s.sh'%(Output_name))
            os.system('echo "" >> %s.sh'%(Output_name))
            os.system('echo "export PATH=\\\"\$PATH:%s\\\"" >> %s.sh'%(os.path.dirname(sys.argv[0]),Output_name))
            if Login_user_name != '':
                os.system('echo "export ALMA_USERNAME=\\\"%s\\\"" >> %s.sh'%(Login_user_name,Output_name))
            else:
                os.system('echo "export ALMA_USERNAME=\\\"\\\"" >> %s.sh'%(Output_name))
        os.system('echo "" >> %s.sh'%(Output_name))
        os.system('echo "alma_archive_download_data_via_http_link.sh \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        #os.system('echo "wget --no-check-certificate --auth-no-challenge --server-response --user dzliu --password  -c \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        #os.system('echo "wget -c \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        if i == len(uid_url_table)-1:
            os.system('echo "" >> %s.sh'%(Output_name))
            os.system('echo \"date +\\\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\\\" > %s.sh.done\" >> %s.sh'%(Output_name,Output_name))
            os.system('echo "" >> %s.sh'%(Output_name))
            os.system('chmod +x %s.sh'%(Output_name))
    print('Now prepared a shell script "%s.sh" to download the Tar files!'%(Output_name))
    print('Running "%s.sh >> %s.log" in terminal!'%(Output_name,Output_name))
    
    os.system('%s.sh >> %s.log'%(Output_name, Output_name))
    
    #cache_location = os.getcwd() + os.path.sep + 'cache'
    #if not os.path.isdir(cache_location):
    #    os.mkdir(cache_location)
    
    #myAlma = Alma()
    #myAlma.cache_location = os.getcwd() + os.path.sep + 'cache'
    #myAlma.download_files(uid_url_table['URL'], cache=True)
    
    
    # 
    # cd back
    # 
    print('os.chdir("%s")' % (current_dir_path) )
    os.chdir(current_dir_path)
    print('os.getcwd()', os.getcwd())
    


