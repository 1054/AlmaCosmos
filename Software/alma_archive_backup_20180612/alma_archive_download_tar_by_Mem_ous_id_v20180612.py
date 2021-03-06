#!/usr/bin/env python2.7
# 

# pip2.7 install --user astroquery
# pip2.7 install --user --install-option="--prefix=/home/dzliu/.local/lib/python2.7/site-packages" --ignore-installed requests
# pip2.7 install --user --install-option="--prefix=/home/dzliu/.local/lib/python2.7/site-packages" --ignore-installed pkg_resources
# pip2.7 install --user keyrings.alt
# 
# pip2.7 install --target="/mnt/fhgfs/PHANGS/ALMA/Common_Scripts/Python/2.7/site-packages" --ignore-installed requests numpy astropy astroquery

import os, sys, re

# 
# read input argument, which should be Member_ous_id
# 
Member_ous_ids = []
Login_user_name = ''
Use_alma_site = 'nrao'
if len(sys.argv) > 1:
    i = 0
    for i in range(1,len(sys.argv)):
        if sys.argv[i].find("uid")==0:
            Member_ous_ids.append(sys.argv[1])
        elif sys.argv[i].find("user:")==0:
            Login_user_name = sys.argv[i].replace('user:','')
        elif sys.argv[i].lower().find("-eso")==0 or sys.argv[i].lower().find("--eso")==0:
            Use_alma_site = 'eso'
else:
    print('Usage: alma_archive_download_tar_by_Mem_ous_id.py "uid://A001/X148/X119" "user:dzliu"')
    sys.exit()


# 
# deal with sys.path
# 
#print(sys.path)
#sys.path.insert(0,os.path.dirname(os.path.abspath(sys.argv[0]))+'/Python/2.7/site-packages')
#print(sys.path)
#sys.exit()

import astroquery
import requests

from astroquery.alma.core import Alma

import astropy.io.ascii as asciitable


# 
# query by Member_ous_id
# 
# result = Alma.query_region(orionkl, radius=0.034*u.deg)
# Member_ous_id = result['Member ous id']

#Member_ous_id = 'uid://A001/X148/X119'
for Member_ous_id in Member_ous_ids:
    Member_ous_name = Member_ous_id.replace(':','_').replace('/','_').replace('+','_')
    Output_name = 'alma_archive_download_tar_for_%s'%(Member_ous_name)
    
    # check previous runs
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
    
    print('Staging data for Member OUS ID "%s"'%(Member_ous_id))
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
        os.system('echo "alma_archive_download_tar_file_via_http_link.sh \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        #os.system('echo "wget --no-check-certificate --auth-no-challenge --server-response --user dzliu --password  -c \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        #os.system('echo "wget -c \"%s\"" >> %s.sh'%(uid_url_table[i]['URL'],Output_name))
        if i == len(uid_url_table)-1:
            os.system('echo "" >> %s.sh'%(Output_name))
            os.system('echo \"date +\\\"%%Y-%%m-%%d %%H:%%M:%%S %%Z\\\" > %s.sh.done\" >> %s.sh'%(Output_name,Output_name))
            os.system('echo "" >> %s.sh'%(Output_name))
            os.system('chmod +x %s.sh'%(Output_name))
    print('Now prepared a shell script "%s.sh" to download the Tar files!'%(Output_name))
    print('Running "%s.sh >> %s.log" in terminal!'%(Output_name,Output_name))
    
    os.system('%s.sh >> %s.log'%(Output_name,Output_name))
    
    #cache_location = os.getcwd() + os.path.sep + 'cache'
    #if not os.path.isdir(cache_location):
    #    os.mkdir(cache_location)
    
    #myAlma = Alma()
    #myAlma.cache_location = os.getcwd() + os.path.sep + 'cache'
    #myAlma.download_files(uid_url_table['URL'], cache=True)


