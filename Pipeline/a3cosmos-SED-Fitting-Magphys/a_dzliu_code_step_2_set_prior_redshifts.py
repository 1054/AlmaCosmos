#!/usr/bin/env python
# 

#__DOCUMENTATION__  
#__DOCUMENTATION__  Description: 
#__DOCUMENTATION__      Set prior redshifts for the SED fitting.
#__DOCUMENTATION__      This is done by going through all available redshifts in the literature and solving their consistency.
#__DOCUMENTATION__  
#__DOCUMENTATION__  Usage Example: 
#__DOCUMENTATION__      
#__DOCUMENTATION__      
#__DOCUMENTATION__  Input Files::
#__DOCUMENTATION__      $input_cat_1
#__DOCUMENTATION__      $input_cat_2
#__DOCUMENTATION__      
#__DOCUMENTATION__  Output Files:
#__DOCUMENTATION__      $output_cat.photometry_with_prior_redshifts.fits
#__DOCUMENTATION__      out_*.*
#__DOCUMENTATION__  


# import python packages
import os, sys, json, time
import numpy as np

import astropy
import astropy.io.ascii as asciitable
from astropy.table import Table, Column

from copy import copy
from pprint import pprint

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter, LogLocator, MultipleLocator

np.warnings.filterwarnings('ignore')





# prepare variables
pcat = ''
zcats = []
znames = []
ztypes = []
out = ''

# read user input
arg_index = 1
arg_type = ''
arg_str = ''
while arg_index < len(sys.argv):
    arg_str = sys.argv[arg_index].lower().replace('--','-')
    # 
    if arg_str.startswith('-pcat'):
        if arg_index+1 < len(sys.argv):
            arg_index = arg_index + 1
            arg_type = 'pcat'
            continue
        else:
            print('Error! Please input a value for argument %s'%(arg_str))
            sys.exit()
    # 
    if arg_str.startswith('-zcat'):
        if arg_index+1 < len(sys.argv):
            arg_index = arg_index + 1
            arg_type = 'zcat'
            continue
        else:
            print('Error! Please input a value for argument %s'%(arg_str))
            sys.exit()
    # 
    if arg_str.startswith('-zname'):
        if arg_index+1 < len(sys.argv):
            arg_index = arg_index + 1
            arg_type = 'zname'
            continue
        else:
            print('Error! Please input a value for argument %s'%(arg_str))
            sys.exit()
    # 
    if arg_str.startswith('-ztype'):
        if arg_index+1 < len(sys.argv):
            arg_index = arg_index + 1
            arg_type = 'ztype'
            continue
        else:
            print('Error! Please input a value for argument %s'%(arg_str))
            sys.exit()
    # 
    if arg_str.startswith('-out'):
        if arg_index+1 < len(sys.argv):
            arg_index = arg_index + 1
            arg_type = 'out'
            continue
        else:
            print('Error! Please input a value for argument %s'%(arg_str))
            sys.exit()
    # 
    # 
    if arg_type == 'pcat':
        pcat = sys.argv[arg_index]
    elif arg_type == 'zcat':
        zcats.append(sys.argv[arg_index])
    elif arg_type == 'zname':
        znames.append(sys.argv[arg_index])
    elif arg_type == 'ztype':
        ztypes.append(sys.argv[arg_index])
    elif arg_type == 'out':
        out = sys.argv[arg_index]
    # 
    arg_index = arg_index + 1

# check user input and print usage
if pcat == '' or len(zcats) == 0 or out == '':
    print('Usage: ')
    print('    %s -pcat XXX.fits -zcat XXX_specz_cat_1.fits XXX_photoz_cat_1.fits XXX_photoz_cat_2.fits -out OUTPUT.fits\n'%(os.path.basename(__file__)))
    print('Notes: ')
    print('    -zcat catalog file names should contain either specz or photoz.')
    print('    -zcat catalogs should contain <ID_Master> column as the unique identifier for cross-matching with -pcat.')
    print('    -zcat spec-z catalogs should also contain <Q_z_spec> column.')
    print('    -out catalog will have the same row as in -pcat catalog.')
    print('    -pcat catalog should contain <ID_Master> as well.')
    sys.exit()






# read data tables
data_table_zcats = {}
for j in range(len(zcats)):
    # 
    # get zname from zcat file name
    if len(znames) <= j:
        znames.append(os.path.basename(zcats[j]).replace('.fits','').replace('tmp_','').replace('_xmatch_backward',''))
    # 
    # get ztype from zcat file name
    if len(ztypes) <= j:
        if znames[j].lower().find('specz')>=0 or znames[j].lower().find('spec-z')>=0:
            ztypes.append('spec')
            #print(znames[j], ztypes[j]) #debug
        else:
            ztypes.append('phot')
            #print(znames[j], ztypes[j]) #debug
    # 
    data_table = Table.read(zcats[j])
    # 
    # check columns
    if not ('ID_Master' in data_table.colnames):
        print('Error! The prior redshift catalog does not have the <ID_Master> column! It first needs a backward cross-matching to the Master Catalog! Please run the "a_dzliu_code_step_1_select_subsample.bash" code first!')
        sys.exit()
    if not ('z' in data_table.colnames):
        print('Error! The prior redshift catalog does not have the <z> column! It first needs a backward cross-matching to the Master Catalog! Please run the "a_dzliu_code_step_1_select_subsample.bash" code first!')
        sys.exit()
    # 
    # sort by -Q_z_spec if the column exists (and this means this zcat is a spec-z catalog)
    if ('Q_z_spec' in data_table.colnames):
        ztypes[j] = 'spec'
        #print(znames[j], ztypes[j], '*') #debug
        data_table['Inversed_Q_z_spec'] = -data_table['Q_z_spec']
        data_table.sort(['ID_Master', 'Inversed_Q_z_spec'])
        data_table.remove_column('Inversed_Q_z_spec')
    # 
    # append to data_table_zcats
    data_table_zcats[znames[j]] = data_table


# read main data table
data_table_pcat = Table.read(pcat)


# set output file name
output_name = out
data_table_out = data_table_pcat.copy()

data_table_out['N_z_spec'] = np.zeros(len(data_table_out), dtype=int)
data_table_out['z_spec'] = np.zeros(len(data_table_out), dtype=float)
data_table_out['z_spec'].description = 'The most reliable spectroscopic redshift, if available, listed at the beginning of the <z_prior> column.'
data_table_out['Ref_z_spec'] = np.zeros(len(data_table_out), dtype='<U255')

data_table_out['N_z_phot'] = np.zeros(len(data_table_out), dtype=int)
data_table_out['z_phot'] = np.zeros(len(data_table_out), dtype=float)
data_table_out['z_phot'].description = 'The first photometric redshift listed in the <z_prior> column, if available.'
data_table_out['Ref_z_phot'] = np.zeros(len(data_table_out), dtype='<U255')

data_table_out['N_z_prior'] = np.zeros(len(data_table_out), dtype=int)
data_table_out['z_prior'] = np.zeros(len(data_table_out), dtype='<U255')
data_table_out['z_prior'].description = 'All possible redshifts compiled from the literature, see the <Ref_z_prior> column.'
data_table_out['Ref_z_prior'] = np.zeros(len(data_table_out), dtype='<U255')



#sys.exit()
print('zcats = ', zcats) # debug
print('znames = ', znames) # debug
print('ztypes = ', ztypes) # debug




#if not os.path.isdir('check_inconsistent_spectroscopic_redshifts'):
#    os.makedirs('check_inconsistent_spectroscopic_redshifts')
#os.chdir('check_inconsistent_spectroscopic_redshifts')


# Set constant
const_catastrophic_error = 0.15 # see Laigle+2016 Sect. 4.3, second paragraph




# check multiple spec-z sources which have inconsistent spec-z-s
print('Looping %d sources ...'%(len(data_table_out)))
for i in range(len(data_table_out)):
    # 
    # prepare check_dict
    check_dict = {}
    check_dict['row_index'] = []
    check_dict['ID_Master'] = []
    check_dict['z'] = []
    check_dict['Ref_z'] = []
    check_dict['Type_z'] = []
    check_dict['Q_z_spec'] = []
    check_dict['Ref_z_spec'] = []
    # 
    # cross-match by ID_Master
    for j in range(len(znames)):
        data_table = data_table_zcats[znames[j]]
        flag_xmatch = np.logical_and( data_table['ID_Master'] == data_table_out['ID_Master'][i] , 
                        np.logical_and( ~data_table['z'].mask , 
                            np.logical_and( data_table['z'] > 0.0 , 
                                            data_table['z'] < 9.0 
                            ) 
                        )
                    )
        # 
        #print('Found %d matched rows in zcat "%s" for ID_Master %d'%(len(np.argwhere(flag_xmatch)), znames[j], data_table_out['ID_Master'][i])) # debug
        if len(np.argwhere(flag_xmatch)) > 0:
            row_indices = np.arange(len(data_table))
            check_dict['row_index'].extend(row_indices[flag_xmatch])
            check_dict['ID_Master'].extend(data_table['ID_Master'][flag_xmatch])
            check_dict['z'].extend(data_table['z'][flag_xmatch])
            check_dict['Ref_z'].extend(np.full(len(row_indices[flag_xmatch]), znames[j], dtype='<U255' ) )
            # 
            if ztypes[j] == 'spec':
                check_dict['Type_z'].extend(np.full(len(row_indices[flag_xmatch]), 'spec', dtype='<U31' ) )
            else:
                check_dict['Type_z'].extend(np.full(len(row_indices[flag_xmatch]), 'phot', dtype='<U31' ) )
            # 
            if 'Q_z_spec' in data_table.colnames:
                check_dict['Q_z_spec'].extend(data_table['Q_z_spec'][flag_xmatch])
            else:
                check_dict['Q_z_spec'].extend(np.full(len(row_indices[flag_xmatch]), -99, dtype=int ) )
            # 
            if 'Ref_z_spec' in data_table.colnames:
                check_dict['Ref_z_spec'].extend(data_table['Ref_z_spec'][flag_xmatch])
            else:
                check_dict['Ref_z_spec'].extend(np.zeros(len(row_indices[flag_xmatch]), dtype='<U255' ) )
        # 
    # 
    # now we have got multiple prior redshifts from zcats
    # then we solve their consistency
    solve_dict = {}
    solve_dict['z'] = []
    solve_dict['Ref_z'] = []
    solve_dict['Type_z'] = []
    solve_dict['Q_z_spec'] = []
    solve_dict['Ref_z_spec'] = []
    # 
    if len(check_dict['z']) > 0:
        for k in range(len(check_dict['z'])):
            if len(solve_dict['z']) > 0:
                check_z1 = check_dict['z'][k]
                check_z2 = np.array(solve_dict['z'])
                if np.min(np.abs(check_z2 - check_z1)) > const_catastrophic_error * (1.0 + check_z1):
                    solve_dict['z'].append(check_dict['z'][k])
                    solve_dict['Ref_z'].append(check_dict['Ref_z'][k])
                    solve_dict['Type_z'].append(check_dict['Type_z'][k])
                    solve_dict['Q_z_spec'].append(check_dict['Q_z_spec'][k])
                    solve_dict['Ref_z_spec'].append(check_dict['Ref_z_spec'][k])
            else:
                solve_dict['z'].append(check_dict['z'][k])
                solve_dict['Ref_z'].append(check_dict['Ref_z'][k])
                solve_dict['Type_z'].append(check_dict['Type_z'][k])
                solve_dict['Q_z_spec'].append(check_dict['Q_z_spec'][k])
                solve_dict['Ref_z_spec'].append(check_dict['Ref_z_spec'][k])
    # 
    # debug
    if len(solve_dict['z']) >= 3:
        print('')
        print('check_dict = ')
        pprint(check_dict)
        print('')
        print('solve_dict = # (removed similar values)')
        pprint(solve_dict)
        print('')
        #time.sleep(30)
    # 
    # save into output table
    if len(solve_dict['z']) > 0:
        data_table_out['N_z_prior'][i] = len(solve_dict['z'])
        data_table_out['z_prior'][i] = ''
        data_table_out['Ref_z_prior'][i] = ''
        for k in range(len(solve_dict['z'])):
            data_table_out['z_prior'][i] = data_table_out['z_prior'][i] + '%0.4f'%(solve_dict['z'][k]) # np.around(solve_dict['z'][k],4)
            data_table_out['Ref_z_prior'][i] = data_table_out['Ref_z_prior'][i] + solve_dict['Ref_z'][k].strip()
            if solve_dict['Type_z'][k]=='spec':
                data_table_out['Ref_z_prior'][i] = data_table_out['Ref_z_prior'][i] + '(Qz=%d)'%(solve_dict['Q_z_spec'][k])
            if k < len(solve_dict['z'])-1:
                data_table_out['z_prior'][i] = data_table_out['z_prior'][i] + ' '
                data_table_out['Ref_z_prior'][i] = data_table_out['Ref_z_prior'][i] + ' '
        
    # 
    # for z_spec and z_phot, we do not do z_prior multiplicity solution but just take the first z_spec and z_phot respectively.
    flag_z_spec = (np.array(check_dict['Type_z'])=='spec')
    where_z_spec = np.argwhere(flag_z_spec).flatten().tolist()
    #print(where_z_spec)
    if len(where_z_spec) > 0:
        data_table_out['N_z_spec'][i] = len(where_z_spec)
        data_table_out['z_spec'][i] = check_dict['z'][where_z_spec[0]]
        data_table_out['Ref_z_spec'][i] = check_dict['Ref_z'][where_z_spec[0]].strip()
        if check_dict['Ref_z_spec'][where_z_spec[0]] != '':
            data_table_out['Ref_z_spec'][i] = data_table_out['Ref_z_spec'][i] + '(%s)'%(check_dict['Ref_z_spec'][where_z_spec[0]].strip().replace(' ','_'))
    # 
    flag_z_phot = (np.array(check_dict['Type_z'])=='phot')
    where_z_phot = np.argwhere(flag_z_phot).flatten().tolist()
    #print(where_z_phot)
    if len(where_z_phot) > 0:
        data_table_out['N_z_phot'][i] = len(where_z_phot)
        data_table_out['z_phot'][i] = check_dict['z'][where_z_phot[0]]
        data_table_out['Ref_z_phot'][i] = check_dict['Ref_z'][where_z_phot[0]].strip()
    
    # 
    # print progress
    print('ID_Master %d (%0.2f%%)'%( data_table_out['ID_Master'][i], float(i+1) / len(data_table_out) * 100.0 )  )
        
        
        


data_table_out.write(output_name, overwrite=True)
print('')
print('Output to "%s"!'%(output_name))






