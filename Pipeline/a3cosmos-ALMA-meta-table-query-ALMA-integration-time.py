#!/usr/bin/env python
# 

import os, sys, re

if len(sys.argv) <= 2:
    print('Usage: ')
    print('  %s \\'%(os.path.basename(__file__)))
    print('  %s \\'%('input_meta_table_file'))
    print('  %s'%('output_meta_table_file'))
    sys.exit()

import astropy.io.ascii as asciitable
import astropy.io.fits as fits

input_meta_table_file = sys.argv[1]
output_meta_table_file = sys.argv[2]

input_meta_table_struct = fits.open(input_meta_table_file)
input_meta_table = input_meta_table_struct[1].data
#print(input_meta_table.columns)

from astroquery import alma
from astroquery.alma import Alma
from datetime import datetime, timedelta
from dateutil import parser
import numpy, time, json

output_integration_time = []
if os.path.isfile('output_integration_time.txt'):
    with open('output_integration_time.txt', 'r') as fp:
        output_integration_time = json.load(fp)
    if type(output_integration_time) is not list:
        output_integration_time = [output_integration_time]

output_observation_date = []
if os.path.isfile('output_observation_date.txt'):
    with open('output_observation_date.txt', 'r') as fp:
        output_observation_date = json.load(fp)
    if type(output_observation_date) is not list:
        output_observation_date = [output_observation_date]

alma = Alma() # 
i = len(output_integration_time)
i = 2
#output_integration_time = []
#output_observation_date = []
#set_no_check_found_row = True
set_no_check_found_row = False
while i < len(input_meta_table):
    project_code = input_meta_table['project'][i]
    start_date = input_meta_table['OBS_DATE'][i] # see -- https://media.readthedocs.org/pdf/test-astroquery/latest/test-astroquery.pdf
    source_ra = input_meta_table['obs_ra'][i]
    source_dec = input_meta_table['obs_dec'][i]
    source_name_alma = input_meta_table['source'][i]
    frequency_range = r'%0.5f .. %0.5f'%(2.99792458e5 / input_meta_table['wavelength'][i] - 7.5 - 3.5, 2.99792458e5 / input_meta_table['wavelength'][i] + 7.5 + 3.5)
    #start_date = re.sub(r'([0-9]+-[0-9]+-[0-9]+)T([0-9]+:[0-9]+:[0-9]+)\.[0-9]+', r'\1 \2', start_date)
    start_date = parser.parse(start_date)
    start_date_plus_one_day = start_date + timedelta(days=1)
    #start_date_reformatted = '<'+start_date.strftime(r'%d-%m-%Y')
    start_date_reformatted = start_date.strftime(r'%d-%m-%Y') + ' .. ' + start_date_plus_one_day.strftime(r'%d-%m-%Y') # re.sub(r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+:[0-9]+:[0-9]+)\.[0-9]+', r'\3-\2-\1', start_date) # see alma aq page
    #payload = {'project_code':project_code, 'start_date':start_date_reformatted, 'source_name_alma':source_name_alma} # 'frequency':frequency_range
    payload = {'project_code':project_code, 'start_date':start_date_reformatted, 'ra_dec':'%.7f %.7f, %f'%(source_ra, source_dec, 3.0/3600.0)} # 3 arcsec
    print(start_date)
    print('payload = %s'%(payload))
    query_result = alma.query(payload = payload, public = True, science = True)
    if query_result:
        #print(query_result.colnames)
        print(query_result)
        found_row = -1
        for k in range(len(query_result)):
            queried_observation_date_var = parser.parse(query_result['Observation date'][k].decode("utf-8"))
            print(queried_observation_date_var.strftime(r'%Y-%m-%d %H:%M:%S') + ' vs ' + start_date.strftime(r'%Y-%m-%d %H:%M:%S'))
            print(query_result['Integration'][k])
            if queried_observation_date_var.strftime(r'%Y-%m-%d %H') == start_date.strftime(r'%Y-%m-%d %H'):
                found_row = k
            elif set_no_check_found_row:
                found_row = k
        if found_row >= 0:
            queried_integration_time = query_result['Integration'][found_row]
            queried_observation_date = query_result['Observation date'][found_row].decode("utf-8")
        else:
            queried_integration_time = -99
            queried_observation_date = 'NULL'
    else:
        queried_integration_time = -99
        queried_observation_date = 'NULL'
    
    print('queried_integration_time = %s'%(queried_integration_time))
    print('queried_observation_date = %s'%(queried_observation_date))
    
    if i < len(output_integration_time):
        output_integration_time[i] = queried_integration_time
    else:
        output_integration_time.append(queried_integration_time)
    
    if i < len(output_observation_date):
        output_observation_date[i] = queried_observation_date
    else:
        output_observation_date.append(queried_observation_date)
    
    i=i+1
    
    time.sleep(0.5)
    break
    
    ##print(query_result.colnames)
    #query_result.sort(['Array','QA2 Status','Observation date'])
    #query_result.reverse()
    ##print(query_result[['Source name','Array','Observation date','QA2 Status']])
    #asciitable.write(query_result[['Source name','Array','Observation date','QA2 Status']], 'datatable_query_%s_%s.txt'%(project_code, datetime.now().strftime(r'%Y%m%d_%Hh%Mm%Ss') ), Writer=asciitable.FixedWidthTwoLine)
if os.path.isfile('output_integration_time.txt'):
    os.system('cp output_integration_time.txt output_integration_time.txt.backup')
if os.path.isfile('output_observation_date.txt'):
    os.system('cp output_observation_date.txt output_observation_date.txt.backup')
with open('output_integration_time.txt', 'w') as fp:
    json.dump(output_integration_time, fp, indent=4)
with open('output_observation_date.txt', 'w') as fp:
    json.dump(output_observation_date, fp, indent=4)



