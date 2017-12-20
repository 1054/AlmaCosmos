#!/usr/bin/env python
# 
# 
# This code will read a fits table and get the column names
# and recognize some of the columns according to the user input
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")

import os, sys

if len(sys.argv) <= 2:
    print('Usage: almacosmos_recognize_fits_table_column_names.py catalog.fits "flux"')
    sys.exit()

dir_crabtable = os.path.dirname(sys.argv[0]) + os.sep + 'lib_python_dzliu' + os.sep + 'crabtable'
if os.path.isdir(dir_crabtable):
    sys.path.append(dir_crabtable)
else:
    print('Error! "%s" was not found! Please completely download from "https://github.com/1054/AlmaCosmos.git"!'%(dir_crabtable))
    sys.exit()


from CrabTable import *

from copy import copy

import re

import astropy.io.ascii as asciitable



def match_str_list_to_pattern_list(input_str_list, input_pattern_list, ignore_case=False):
    matched_str_list = []
    copied_str_list = copy(input_str_list)
    for input_pattern in input_pattern_list:
        if ignore_case:
            matcher = re.compile(input_pattern, re.IGNORECASE)
        else:
            matcher = re.compile(input_pattern)
        # 
        index_str = 0
        while index_str < len(copied_str_list):
            input_str = copied_str_list[index_str]
            if matcher.match(input_str):
                matched_str_list.append(input_str)
                copied_str_list.remove(input_str)
            else:
                index_str = index_str + 1
    # 
    return matched_str_list


def recognize_id(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '(id|Id|ID)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )


def recognize_flux(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(flux|Flux|FLUX|f|S)($|[^a-zA-Z]+.*$)', 
                                             '^(.*)[_](flux|FLUX)$', 
                                           ]
                                         )


def recognize_flux_error(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(e_flux|E_Flux|E_FLUX|df|e_S)($|[^a-zA-Z]+.*$)', 
                                             '^(e|E)[_](.*)[_](flux|FLUX)$', 
                                           ]
                                         )


def recognize_ra(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(ra|RA)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )


def recognize_dec(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(dec|Dec|DEC)($|[^a-zA-Z]+.*$)', 
                                             '^(de|De|DE)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )
    # 
    return output_col_list


def recognize_z(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(z|Z|ZPHOT|ZPDF|ZML|PHOTOZ|PHOTO-Z)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )


def recognize_Maj(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(Maj|maj|Major|major)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )


def recognize_Min(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(Min|min|Minor|minor)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )




cat_file = ''
out_list = []
out_dirname = ''
out_basename = 'datatable_extracted_column_'
out_suffix = '.txt'
do_extract = False

for i in range(len(sys.argv)):
    if i>=1:
        if not sys.argv[i].startswith('-'):
            if cat_file == '':
                cat_file = sys.argv[i]
            else:
                out_list.append(sys.argv[i])
        else:
          if sys.argv[i].lower() == '-extract' or sys.argv[i].lower() == '--extract':
              do_extract = True
          elif sys.argv[i].lower() == '-out' or sys.argv[i].lower() == '--out':
              out_dirname = sys.argv[i] + os.sep
          elif sys.argv[i].lower() == '-output-dirname' or sys.argv[i].lower() == '--output-dirname':
              out_dirname = sys.argv[i] + os.sep
          elif sys.argv[i].lower() == '-output-basename' or sys.argv[i].lower() == '--output-basename':
              out_basename = sys.argv[i]
          elif sys.argv[i].lower() == '-output-suffix' or sys.argv[i].lower() == '--output-suffix':
              out_suffix = sys.argv[i]


cat_data = CrabTable(cat_file)
col_names = cat_data.getColumnNames()
#col_names.append('ID_test')
#col_names.append('ID100_test')
#col_names.append('ID200_test')
#col_names.append('Id300_test')
#col_names.append('f_test')
#col_names.append('S_test')
#col_names.append('f100_test')
#col_names.append('S100_test')
#print(col_names)
cols = {}
cols['ID'] = recognize_id(col_names)
cols['RA'] = recognize_ra(col_names)
cols['Dec'] = recognize_dec(col_names)
cols['z'] = recognize_z(col_names)
cols['Flux'] = recognize_flux(col_names)
cols['Flux_error'] = recognize_flux_error(col_names)
cols['Maj'] = recognize_Maj(col_names)
cols['Min'] = recognize_Min(col_names)
#print(cols)

if do_extract:
    # extract columns
    # now first prepare out_dirname
    if out_dirname != '':
        if not os.path.isdir(out_dirname):
            os.makedirs(out_dirname)
    # extract each column
    for col_type in cols:
        col_name = ''
        if type(cols[col_type]) is list:
            if len(cols[col_type]) > 0:
                col_name = cols[col_type][0]
            else:
                col_name = ''
        else:
            col_name = str(cols[col_type])
        # 
        if col_name != '':
            out_colname = col_type # re.sub(r'\W', '_', col_name)
            out_coldata = cat_data.getColumn(col_name)
            out_filename = out_dirname + out_basename + out_colname + out_suffix
            print('Output %d rows for column "%s" to "%s"'%(len(out_coldata), col_name, out_filename))
            asciitable.write(out_coldata, out_filename, asciitable.FixedWidthTwoLine)
            print('Output to "%s"!'%(out_filename))
else:
    # print each column
    for col_type in cols:
        col_name = ''
        if type(cols[col_type]) is list:
            if len(cols[col_type]) > 0:
                col_name = cols[col_type][0]
            else:
                col_name = ''
        else:
            col_name = str(cols[col_type])
        # 
        if col_name != '':
            print('%s: %s'%(col_type, col_name))
        else:
            print('%s: %s'%(col_type, '__NULL__'))
    





