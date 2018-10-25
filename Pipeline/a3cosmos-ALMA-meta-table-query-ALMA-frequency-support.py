#!/usr/bin/env python
# 

import os, sys, re

if len(sys.argv) <= 1:
    print('Usage: ')
    print('  ./a3cosmos-ALMA-meta-table-query-ALMA-frequency-support.py input_meta_table_file')
    print('')
    sys.exit()

import numpy as np, time, json
import astropy
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery import alma
from astroquery.alma import Alma
from datetime import datetime, timedelta
from dateutil import parser



# 
# read user input
input_meta_table_file = sys.argv[1]
#output_meta_table_file = sys.argv[2]

debug = False # False #<TODO># 


# 
# backup existing files
if os.path.isfile('query_ALMA_archive_integration_time.txt'):
    os.system('cp query_ALMA_archive_integration_time.txt query_ALMA_archive_integration_time.txt.backup')
if os.path.isfile('query_ALMA_archive_observation_date.txt'):
    os.system('cp query_ALMA_archive_observation_date.txt query_ALMA_archive_observation_date.txt.backup')
if os.path.isfile('query_ALMA_archive_frequency_support.txt'):
    os.system('cp query_ALMA_archive_frequency_support.txt query_ALMA_archive_frequency_support.txt.backup')


# 
# read input_meta_table
input_meta_table = Table.read(input_meta_table_file)
print(input_meta_table.columns)


# 
# load previous query results
output_integration_time = []
if os.path.isfile('query_ALMA_archive_integration_time.txt'):
    with open('query_ALMA_archive_integration_time.txt', 'r') as fp:
        output_integration_time = json.load(fp)
    if type(output_integration_time) is not list:
        output_integration_time = [output_integration_time]

output_observation_date = []
if os.path.isfile('query_ALMA_archive_observation_date.txt'):
    with open('query_ALMA_archive_observation_date.txt', 'r') as fp:
        output_observation_date = json.load(fp)
    if type(output_observation_date) is not list:
        output_observation_date = [output_observation_date]

output_frequency_support = []
if os.path.isfile('query_ALMA_archive_frequency_support.txt'):
    with open('query_ALMA_archive_frequency_support.txt', 'r') as fp:
        output_frequency_support = json.load(fp)
    if type(output_frequency_support) is not list:
        output_frequency_support = [output_frequency_support]



# 
# query Alma archive for each row of the input_meta_table
alma = Alma() # 
i = len(output_frequency_support) # continue from this index
set_no_consistency_check = False #<TODO># 
while i < len(input_meta_table):
    print('')
    print('Processing row %d/%d of the meta table ... '%(i+1, len(input_meta_table)))
    print('')
    project_code = input_meta_table['project'][i]
    start_date = input_meta_table['OBSDATE'][i] # see -- https://media.readthedocs.org/pdf/test-astroquery/latest/test-astroquery.pdf
    source_ra = input_meta_table['OBSRA'][i]
    source_dec = input_meta_table['OBSDEC'][i]
    source_name_alma = input_meta_table['source'][i]
    source_name_alma = re.sub(r'^[_]*(.*?)[_]*$', r'\1', source_name_alma)
    frequency_range = r'%0.5f .. %0.5f'%(2.99792458e5 / input_meta_table['wavelength'][i] - 7.5 - 3.5, 2.99792458e5 / input_meta_table['wavelength'][i] + 7.5 + 3.5)
    #start_date = re.sub(r'([0-9]+-[0-9]+-[0-9]+)T([0-9]+:[0-9]+:[0-9]+)\.[0-9]+', r'\1 \2', start_date)
    start_date = parser.parse(start_date)
    start_date_plus_one_day = start_date + timedelta(days=1)
    #start_date_reformatted = '<'+start_date.strftime(r'%d-%m-%Y')
    start_date_reformatted = start_date.strftime(r'%d-%m-%Y') + ' .. ' + start_date_plus_one_day.strftime(r'%d-%m-%Y') # re.sub(r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+:[0-9]+:[0-9]+)\.[0-9]+', r'\3-\2-\1', start_date) # see alma aq page
    # 
    # try to query (try multiple times)
    query_results = None
    # 
    if query_results is None or len(query_results) == 0:
        payload = {'project_code':project_code, 'start_date':start_date_reformatted, 'ra_dec':'%.7f %.7f, %f'%(source_ra, source_dec, 3.0/3600.0)} # 3 arcsec
        print('payload = %s'%(payload))
        query_results = alma.query(payload = payload, public = True, science = True)
        time.sleep(0.5)
        if debug:
            print('query_results is None?', query_results is None)
            print('len(query_results) == 0?', len(query_results) == 0)
    # 
    if query_results is None or len(query_results) == 0:
        payload = {'project_code':project_code, 'source_name_alma':source_name_alma, 'ra_dec':'%.7f %.7f, %f'%(source_ra, source_dec, 3.0/3600.0)} # 3 arcsec
        print('payload = %s'%(payload))
        query_results = alma.query(payload = payload, public = True, science = True)
        time.sleep(0.5)
        if debug:
            print('query_results is None?', query_results is None)
            print('len(query_results) == 0?', len(query_results) == 0)
    # 
    if query_results is None or len(query_results) == 0:
        payload = {'project_code':project_code, 'ra_dec':'%.7f %.7f, %f'%(source_ra, source_dec, 3.0/3600.0)} # 3 arcsec
        print('payload = %s'%(payload))
        query_results = alma.query(payload = payload, public = True, science = True)
        time.sleep(0.5)
        if debug:
            print('query_results is None?', query_results is None)
            print('len(query_results) == 0?', len(query_results) == 0)
    # 
    if query_results is None or len(query_results) == 0:
        payload = {'project_code':project_code, } # no RA Dec constraint
        print('payload = %s'%(payload))
        query_results = alma.query(payload = payload, public = True, science = True)
        time.sleep(0.5)
        if debug:
            print('query_results is None?', query_results is None)
            print('len(query_results) == 0?', len(query_results) == 0)
    # 
    if query_results:
        if debug:
            print(query_results.colnames)
            print(query_results)
        # 
        # sum the whole integration time for each Mem_ous_id
        queried_mem_ous_id_list = list(set(query_results['Member ous id'])) # make an unique list
        queried_mem_ous_id_integration = {}
        for queried_mem_ous_id in queried_mem_ous_id_list:
            queried_mem_ous_id_clean = queried_mem_ous_id.replace('/','_').replace(':','_')
            if 'COUNT' in query_results.colnames:
                queried_mem_ous_id_integration[queried_mem_ous_id_clean] = sum(query_results['Integration'][(query_results['Member ous id']==queried_mem_ous_id)] * query_results['COUNT'][(query_results['Member ous id']==queried_mem_ous_id)] )
            else:
                queried_mem_ous_id_integration[queried_mem_ous_id_clean] = sum(query_results['Integration'][(query_results['Member ous id']==queried_mem_ous_id)] )
        # 
        # process source name format and observation date time difference
        query_results['Source name cleaned'] = [t.replace(' ','_') for t in query_results['Source name']]
        query_results['Member ous id cleaned'] = [t.replace('/','_').replace(':','_') for t in query_results['Member ous id']]
        query_results['Observation date obj'] = [parser.parse(t.decode("utf-8")) for t in query_results['Observation date']]
        query_results['Observation date diff'] = [abs((t-start_date)).seconds for t in query_results['Observation date obj']]
        query_results['RA Dec diff'] = [SkyCoord(t_RA*u.deg,t_Dec*u.deg).separation(SkyCoord(source_ra*u.deg,source_dec*u.deg)).to(u.arcsec).value for t_RA,t_Dec in zip(query_results['RA'],query_results['Dec']) ]
        query_results.sort('Observation date diff')
        # 
        # find row by source name
        found_row = -1
        # 
        # 
        if found_row < 0:
            check_rows = range(len(query_results))
            if source_name_alma in query_results['Source name cleaned']:
                check_rows = np.argwhere(query_results['Source name cleaned'] == source_name_alma).flatten()
            for k in range(len(check_rows)):
                print('Checking row %d: Source name "%s" vs "%s", Observation date "%s" vs "%s", diff. time %s vs integr. time %s for Mem_ous_id "%s", diff. ra dec sep. %s' % (
                                    k+1, 
                                    query_results['Source name cleaned'][k], 
                                    source_name_alma, 
                                    query_results['Observation date obj'][k].strftime('%Y-%m-%d %H:%M:%S'), 
                                    start_date.strftime('%Y-%m-%d %H:%M:%S'), 
                                    query_results['Observation date diff'][k], 
                                    queried_mem_ous_id_integration[query_results['Member ous id cleaned'][k]], 
                                    query_results['Member ous id cleaned'][k], 
                                    query_results['RA Dec diff'][k]
                    ) )
                if (found_row < 0) and (query_results['Observation date diff'][k] <= queried_mem_ous_id_integration[query_results['Member ous id cleaned'][k]]):
                    found_row = check_rows[k]
                # 
                # <TODO> special cases:
                if (found_row < 0) and project_code == '2011.0.00097.S' and source_name_alma == 'COSMOS9_field2' and query_results['Source name cleaned'][k] == 'COSMOSmedz_83':
                    found_row = check_rows[k]
        # 
        if found_row >= 0:
            queried_integration_time = query_results['Integration'][found_row]
            queried_observation_date = query_results['Observation date'][found_row].decode("utf-8")
            queried_frequency_support = query_results['Frequency support'][found_row]
        else:
            queried_integration_time = -99
            queried_observation_date = 'NULL'
            queried_frequency_support = 'NULL'
    else:
        queried_integration_time = -99
        queried_observation_date = 'NULL'
        queried_frequency_support = 'NULL'
    
    print('queried_integration_time = %s'%(queried_integration_time))
    print('queried_observation_date = %s'%(queried_observation_date))
    print('queried_frequency_support = %s'%(queried_frequency_support))
    
    if queried_frequency_support == 'NULL':
        print('Error! Failed to get frequency_support!')
        sys.exit()
    
    if i < len(output_integration_time):
        output_integration_time[i] = queried_integration_time
    else:
        output_integration_time.append(queried_integration_time)
    
    if i < len(output_frequency_support):
        output_frequency_support[i] = queried_frequency_support
    else:
        output_frequency_support.append(queried_frequency_support)
    
    if i < len(output_observation_date):
        output_observation_date[i] = queried_observation_date
    else:
        output_observation_date.append(queried_observation_date)
    
    print('')
    
    i=i+1
    
    time.sleep(0.5)
    if debug:
        print('In debug mode we do not write to files.')
        sys.exit()

    ##print(query_result.colnames)
    #query_result.sort(['Array','QA2 Status','Observation date'])
    #query_result.reverse()
    ##print(query_result[['Source name','Array','Observation date','QA2 Status']])
    #asciitable.write(query_result[['Source name','Array','Observation date','QA2 Status']], 'datatable_query_%s_%s.txt'%(project_code, datetime.now().strftime(r'%Y%m%d_%Hh%Mm%Ss') ), Writer=asciitable.FixedWidthTwoLine)
    
    # 
    # output after each query
    with open('query_ALMA_archive_integration_time.txt', 'w') as fp:
        json.dump(output_integration_time, fp, indent=4)
    with open('query_ALMA_archive_observation_date.txt', 'w') as fp:
        json.dump(output_observation_date, fp, indent=4)
    with open('query_ALMA_archive_frequency_support.txt', 'w') as fp:
        json.dump(output_frequency_support, fp, indent=4)





