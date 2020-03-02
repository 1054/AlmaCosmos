#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re, pkg_resources
pkg_resources.require('astroquery')
pkg_resources.require('keyrings.alt')
import astroquery
import requests
from astroquery.alma.core import Alma
import astropy.io.ascii as asciitable
from astropy.table import unique, Table
from operator import itemgetter, attrgetter


# 
# read input argument, which should be Member_ous_id
# 
Member_ous_ids = []
Login_user_name = ''
Use_alma_site = 'nrao'
Output_folder = ''
Only_products = False
Overwrite_query = False
Overwrite_download = False
i = 1
while i < len(sys.argv): 
    #print(sys.argv[i])
    arg_str = sys.argv[i].lower().replace('--','-')
    if arg_str.startswith("uid"):
        Member_ous_ids.append(sys.argv[1])
    elif arg_str.startswith("user:"):
        Login_user_name = sys.argv[i].replace('user:','')
    elif arg_str.startswith("-eso"):
        Use_alma_site = 'eso'
    elif arg_str.startswith("-only-products"):
        Only_products = True
    elif arg_str.startswith("-overwrite-query"):
        Overwrite_query = True
    elif arg_str.startswith("-overwrite-download"):
        Overwrite_download = True
    elif arg_str == '-user':
        if i+1 < len(sys.argv):
            i = i+1
            Login_user_name = sys.argv[i]
    elif arg_str == '-out':
        if i+1 < len(sys.argv):
            i = i+1
            Output_folder = sys.argv[i]
            if not os.path.isdir(Output_folder):
                os.makedirs(Output_folder)
    i = i+1

if len(Member_ous_ids) == 0:
    print('Usage: alma_archive_download_data_by_Mem_ous_id.py "uid://A001/X148/X119" [--user dzliu --eso] [--out OUTPUT_FOLDER] [--only-products]')
    sys.exit()


# 
# Output_folder
# 
if Output_folder != '':
    print('os.chdir("%s")' % (Output_folder) )
    os.chdir(Output_folder)
    print('os.getcwd()', os.getcwd())


# 
# query by Member_ous_id
# 
# result = Alma.query_region(orionkl, radius=0.034*u.deg)
# Member_ous_id = result['Member ous id']
#Member_ous_id = 'uid://A001/X148/X119'
for Member_ous_id in Member_ous_ids:
    Member_ous_name = Member_ous_id.replace(':','_').replace('/','_').replace('+','_')
    Output_name = 'alma_archive_download_tar_files_by_Mem_ous_id_%s'%(Member_ous_name)
    
    # check previous runs
    if os.path.isfile('%s.sh'%(Output_name)) and not Overwrite_download: 
        if os.path.isfile('%s.sh.done'%(Output_name)): 
            print('Found exisiting "%s.sh" and "%s.sh.done"! Will not re-run it!'%(Output_name,Output_name))
        else:
            print('Found exisiting "%s.sh"! But it seems not finished yet! Will launch it now!'%(Output_name))
            os.system('echo "" >> %s.log'%(Output_name))
            os.system('date +\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\" >> %s.log'%(Output_name))
            os.system('echo "" >> %s.log'%(Output_name))
            os.system('chmod +x %s.sh'%(Output_name))
            print('./%s.sh >> %s.log'%(Output_name,Output_name))
            os.system('./%s.sh >> %s.log'%(Output_name,Output_name))
        continue
    
    # check previous alma archive queries
    if os.path.isfile('%s.txt'%(Output_name)) and not Overwrite_query: 
        print('Found exisiting "%s.txt"! No "-overwrite-query" is set. Using it!'%(Output_name))
        uid_url_table_nodups = Table.read('%s.txt'%(Output_name), format='ascii.fixed_width_two_line')
    else:
        # 
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
        # 
        # login
        if Login_user_name != '':
            print('Logging in as ALMA User "%s"'%(Login_user_name))
            Alma.login(Login_user_name, store_password=True)
        
        print('Staging data for Member ObservingUnitSet ID "%s"'%(Member_ous_id))
        uid_url_table = Alma.stage_data(Member_ous_id)
        # 
        #filelist = Alma.download_and_extract_files(uid_url_table['URL'], regex='.*README$')
        #print(filelist)
        # 
        # remove duplicate URLs
        uid_url_table_nodups = unique(uid_url_table, keys='URL', keep='first')
        # 
        # save to disk
        asciitable.write(uid_url_table_nodups, '%s.txt'%(Output_name), Writer=asciitable.FixedWidthTwoLine)
    
    # 
    
    print(uid_url_table_nodups)
    
    os.system('date +"%%Y-%%m-%%d %%H:%%M:%%S %%Z" > %s.log'%(Output_name))
    os.system('echo "%s %s" >> %s.log'%(sys.argv[0],sys.argv[1],Output_name))
    
    uid_url_table_nrow = len(uid_url_table_nodups)
    
    for i in range(uid_url_table_nrow):
        uid_url_address = uid_url_table_nodups[i]['URL']
        
        # if user has input Only_products, then we only download products which contain .fits
        if Only_products:
            if not (uid_url_address.find('.fits.') > 0 or uid_url_address.endswith('.fits')):
                continue
        
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
        os.system('echo "alma_archive_download_data_via_http_link.sh \"%s\"" >> %s.sh'%(uid_url_address,Output_name))
        #os.system('echo "wget --no-check-certificate --auth-no-challenge --server-response --user dzliu --password  -c \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        #os.system('echo "wget -c \"%s\"" >> %s.sh'%(uid_url_address,Output_name))
    
    os.system('echo "" >> %s.sh'%(Output_name))
    os.system('echo \"date +\\\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\\\" > %s.sh.done\" >> %s.sh'%(Output_name,Output_name))
    os.system('echo "" >> %s.sh'%(Output_name))
    os.system('chmod +x %s.sh'%(Output_name))
    
    print('Now prepared a shell script "%s.sh" to download the Tar files!'%(Output_name))
    print('Running "./%s.sh >> %s.log" in terminal!'%(Output_name,Output_name))
    
    os.system('./%s.sh >> %s.log'%(Output_name,Output_name))
    
    #cache_location = os.getcwd() + os.path.sep + 'cache'
    #if not os.path.isdir(cache_location):
    #    os.mkdir(cache_location)
    
    #myAlma = Alma()
    #myAlma.cache_location = os.getcwd() + os.path.sep + 'cache'
    #myAlma.download_files(uid_url_table['URL'], cache=True)


