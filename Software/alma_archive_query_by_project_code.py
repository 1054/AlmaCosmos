#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re, time, json, pkg_resources
pkg_resources.require('astroquery')
pkg_resources.require('keyrings.alt')
import astroquery
import requests
from astroquery.alma.core import Alma
from astropy.table import Table, Column
from datetime import datetime
from operator import itemgetter, attrgetter


# 
# read input argument, which should be Member_ous_id
# 
if len(sys.argv) <= 1:
    print('Usage: ')
    print('    alma_archive_query_by_project_code.py "2013.1.00034.S" [--user yourusername]')
    print('Notes:')
    print('    The output will be a file named "alma_archive_query_by_project_code_2013.1.00034.S.txt"')
    print('    If the data is proprietary, please input --user XXX"')
    print('    If we want to overwrite existing output file, please input --overwrite"')
    sys.exit()

project_codes = []
ALMA_user_name = ''
overwrite = False
output_full_table = True
i = 1
while i < len(sys.argv):
    if sys.argv[i].lower() == '-user' or sys.argv[i].lower() == '--user': 
        i = i+1
        if i < len(sys.argv):
            ALMA_user_name = sys.argv[i]
    elif sys.argv[i].lower() == '-overwrite' or sys.argv[i].lower() == '--overwrite': 
        overwrite = True
    #elif sys.argv[i].lower() == '-full' or sys.argv[i].lower() == '--full': 
    #    output_full_table = True
    else:
        project_codes.append(sys.argv[i])
    i = i+1
if len(project_codes) == 0:
    print('Error! No project code given!')
    sys.exit()


# 
# deal with sys.path
# 
#print(sys.path)
#sys.path.insert(0,os.path.dirname(os.path.abspath(sys.argv[0]))+'/Python/2.7/site-packages')
#print(sys.path)
#sys.exit()



# 
# loop inputs
# 
for project_code in project_codes:
    
    output_name = 'alma_archive_query_by_project_code_%s' % (project_code)
    
    if (not os.path.isfile(output_name+'.txt')) or overwrite:
        
        # 
        # login
        # 
        Has_login = False
        Query_public = True
        if ALMA_user_name != '' and Has_login == False:
            Alma.login(ALMA_user_name, store_password=True)
            Query_public = False
            Has_login = True
        
        # 
        # query
        # 
        query_result = Alma.query(payload = {'project_code':project_code}, public = Query_public)
        query_datetime = datetime.today().strftime('%Y-%m-%d %H:%M:%S %Z')

        #print(query_result) #<bug><20170926> directly print it can get error like "UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position"
        for colname in query_result.colnames:
            if colname == 'Proposal authors':
                query_result[colname]._sharedmask = False
                for rownumb in range(len(query_result[colname])):
                    #print('-------------------------------')
                    #print(query_result[colname][rownumb])
                    #print(query_result[colname][rownumb].decode('utf-8'))
                    try:
                        query_result[colname][rownumb] = query_result[colname][rownumb].decode('utf-8').encode('ascii','xmlcharrefreplace')
                    except:
                        pass
        
        #query_result_backup = query_result
        #query_result = sorted(query_result_backup, key=itemgetter('Project code'))
        #query_result = query_result.group_by(['Project code', 'Member ous id']) # http://docs.astropy.org/en/stable/table/operations.html#table-operations
        #print(type(query_result))
        #print(query_result.colnames)
        #print(query_result)
        #print(query_result.groups.keys)
        if len(query_result) == 0:
            print('\nError! No result found for the input project_code %s!\n'% (project_code) )
            continue
            #sys.exit()
        
        # sort
        try:
            query_result.sort(['Observation date', 'Member ous id', 'Source name'])
        except:
            pass
        
        # output the full table
        if output_full_table:
            #pass
            # fix ValueError: Illegal format `object`.
            # see https://github.com/astropy/astropy/issues/7480
            output_table = query_result
            output_table.meta['Query datetime'] = query_datetime
            for col in output_table.itercols():
                if col.dtype.kind == 'O':
                    output_table[col.name] = Column(col.tolist(), col.name)
            #output_table = Table([Column(col.tolist(),col.name) if col.dtype.kind == 'O' else col for col in query_result.itercols()])
            output_table.write(output_name+'.fits', format='fits', overwrite=overwrite)
            print('Output to "%s"!' % (output_name+'.fits'))
        
        
        # output selected columns
        output_table = query_result[['Project code','Member ous id','Source name','Observation date','Integration','Band','Array','Mosaic']]
        output_table['Observation date'] = [t.replace(' ','T') for t in output_table['Observation date']]
        output_table['Mosaic'] = [re.sub(r'^$',r'False',t) for t in output_table['Mosaic']]
        for colname in output_table.colnames:
            output_table.rename_column(colname, colname.replace(' ','_'))
        output_table.meta = None
        output_table.write(output_name+'.txt', format='ascii.fixed_width', delimiter=' ', bookend=True, overwrite=overwrite)
        with open(output_name+'.txt', 'r+') as fp:
            fp.seek(0)
            fp.write('#')
        print('Output to "%s"!' % (output_name+'.txt'))
        
        #with open(output_name+'.meta.txt', 'w') as fp:
        #    json.dump(output_table.meta, fp, sort_keys=True, indent=4)
        #print('Output to "%s"!' % (output_name+'.meta.txt'))
        
        with open(output_name+'.readme.txt', 'w') as fp:
            fp.write('Queried on %s with the script "%s".'%(query_datetime, os.path.abspath(__file__)))
        print('Output to "%s"!' % (output_name+'.readme.txt'))
    
    else:
        
        print('Using existing file %s'%(output_name))
    
    table = Table.read(output_name+'.txt', format='ascii.commented_header')
    print(table)











