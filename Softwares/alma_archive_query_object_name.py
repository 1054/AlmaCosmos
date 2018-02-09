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
if len(sys.argv) <= 1:
    print('Usage: alma_archive_query_object_name.py "CenA"')
    sys.exit()

Object_name = ''
ALMA_user_name = ''
i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '--user': 
        i = i+1
        if i < len(sys.argv):
            ALMA_user_name = sys.argv[i]
    else:
        Object_name = sys.argv[i]
    i = i+1
if Object_name == '':
    print('Error! No ALMA Member OUS ID has been given!')
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

from operator import itemgetter, attrgetter


# 
# login
# 
Query_public = True
if ALMA_user_name != '':
    Alma.login(ALMA_user_name, store_password=True)
    Query_public = False


# 
# query by Object_name
# 
#query_result = Alma.query_region(orionkl, radius=0.034*u.deg)
#query_result = Alma.query_object(Object_name)
query_result = Alma.query_object(Object_name, public=Query_public)

#print(query_result) #<bug><20170926> directly print it can get error like "UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position"
for colname in query_result.colnames:
    if colname == 'Proposal authors':
        query_result[colname]._sharedmask = False
        for rownumb in range(len(query_result[colname])):
            #print '-------------------------------'
            #print query_result[colname][rownumb]
            #print query_result[colname][rownumb].decode('utf-8')
            query_result[colname][rownumb] = query_result[colname][rownumb].decode('utf-8').encode('ascii','xmlcharrefreplace')

query_result_backup = query_result
#query_result = sorted(query_result_backup, key=itemgetter('Project code'))
query_result = query_result_backup.group_by('Project code') # http://docs.astropy.org/en/stable/table/operations.html#table-operations
print(type(query_result))
print(query_result)

Project_code = query_result['Project code']
Member_ous_id = query_result['Member ous id']
Meta_info = (query_result['Project code'], query_result['Member ous id'], query_result['Array'], query_result['PI name'], query_result['SB name'], query_result['Project title'])

#filelist = Alma.download_and_extract_files(uid_url_table['URL'], regex='.*README$')
#print(filelist)

if os.path.isfile('alma_archive_query_object_name_result.txt'):
    os.system('mv "alma_archive_query_object_name_result.txt"                 "alma_archive_query_object_name_result.txt.backup"')
if os.path.isfile('alma_archive_query_object_name_result_project_code.txt'):
    os.system('mv "alma_archive_query_object_name_result_project_code.txt"    "alma_archive_query_object_name_result_project_code.txt.backup"')
if os.path.isfile('alma_archive_query_object_name_result_member_ous_id.txt'):
    os.system('mv "alma_archive_query_object_name_result_member_ous_id.txt"   "alma_archive_query_object_name_result_member_ous_id.txt.backup"')
if os.path.isfile('alma_archive_query_object_name_result_meta_info.txt'):
    os.system('mv "alma_archive_query_object_name_result_meta_info.txt"       "alma_archive_query_object_name_result_meta_info.txt.backup"')

asciitable.write(query_result,  'alma_archive_query_object_name_result.txt',                  Writer=asciitable.FixedWidthTwoLine)
asciitable.write(Project_code,  'alma_archive_query_object_name_result_project_code.txt',     Writer=asciitable.FixedWidthTwoLine)
asciitable.write(Member_ous_id, 'alma_archive_query_object_name_result_member_ous_id.txt',    Writer=asciitable.FixedWidthTwoLine)
asciitable.write(Meta_info,     'alma_archive_query_object_name_result_meta_info.txt',        Writer=asciitable.FixedWidthTwoLine)


