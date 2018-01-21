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

if len(sys.argv) <= 1:
    print('Usage: almacosmos_recognize_fits_table_column_names.py catalog.fits')
    print('       almacosmos_recognize_fits_table_column_names.py catalog.fits -extract flux flux_error')
    print('Notes: This code will recognize ID, RA, Dec, z, Flux, Flux_error columns in the input catalog.')
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
                                             '^(.*)[_](id|Id|ID)$', 
                                             '^(.*)[_](id|Id|ID)[_](.*)$', 
                                             '^(sim|rec)_(id)$', 
                                           ]
                                         )


def recognize_flux(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(.*)[_](flux|FLUX)$', 
                                             '^(.*)[_](flux|FLUX)[_]([a-zA-Z]*)$', 
                                             '^(f|S)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(f)$', 
                                           ]
                                         )


def recognize_flux_error(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(e|E)[_](flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(e|E)[_](.*)[_](flux|Flux|FLUX)[_]([a-zA-Z]*)$', 
                                             '^(e|E)[_](.*)[_](flux|Flux|FLUX)$', 
                                             '^(df|e_S)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(df)$', 
                                           ]
                                         )


def recognize_peak_flux(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(peak|Peak|PEAK)_(flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(.*)[_](peak|Peak|PEAK)_(flux|Flux|FLUX)$', 
                                             '^(.*)[_](peak|Peak|PEAK)_(flux|Flux|FLUX)[_]([a-zA-Z]*)$', 
                                             '^(fpeak|f_peak|Speak|S_peak)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(fpeak)$', 
                                           ]
                                         )


def recognize_peak_flux_error(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(e|E)_(peak|Peak|PEAK)_(flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(dfpeak|df_peak|e_Speak|e_S_peak)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(dfpeak)$', 
                                           ]
                                         )


def recognize_total_flux(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(total|Total|TOTAL)_(flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(.*)[_](total|Total|TOTAL)_(flux|Flux|FLUX)$', 
                                             '^(.*)[_](total|Total|TOTAL)_(flux|Flux|FLUX)[_]([a-zA-Z]*)$', 
                                             '^(ftotal|f_total|Stotal|S_total)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(f)$', 
                                           ]
                                         )


def recognize_total_flux_error(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(e|E)_(total|Total|TOTAL)_(flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(dftotal|df_total|e_Stotal|e_S_total)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(df)$', 
                                           ]
                                         )


def recognize_residual_flux(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(residual|Residual|Res|RES)_(flux|Flux|FLUX)($|[^a-zA-Z]+.*$)', 
                                             '^(.*)[_](residual|Residual|Res|RES)_(flux|Flux|FLUX)$', 
                                             '^(.*)[_](residual|Residual|Res|RES)_(flux|Flux|FLUX)[_]([a-zA-Z]*)$', 
                                             '^(fres|f_res|fresidual|f_residual)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(fres|f_res|fresidual|f_residual)$', 
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


def recognize_z(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(z|Z|ZPHOT|ZPDF|ZML|PHOTOZ|PHOTO-Z)($|[^a-zA-Z]+.*$)', 
                                           ]
                                         )


def recognize_Maj(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(Maj|maj|Major|major)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(Maj|maj)$', 
                                           ]
                                         )


def recognize_Min(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(Min|min|Minor|minor)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(Min|min)$', 
                                           ]
                                         )


def recognize_PA(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(PA|pa)($|[^a-zA-Z]+.*$)', 
                                             '^(sim|rec)_(PA|pa)$', 
                                           ]
                                         )


def recognize_RMS_noise(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(rms|noise|rms noise)($|[^a-zA-Z]+.*$)', 
                                             '^sim_rms$', 
                                           ]
                                         )


def recognize_image_file(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(image_file|image file|Image|image|sim_data_dir|sim_image_dir)$', 
                                           ]
                                         )


def recognize_simu_name(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(Simu|simu|Sim|sim|sim_image_name|sim_dir_str)$', 
                                           ]
                                         )


def recognize_beam_Maj(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(beam|Beam|BEAM)[_](maj|Maj|major|Major)', 
                                             '^(maj|Maj|major|Major)[_](beam|Beam|BEAM)$', 
                                             '^(sim|rec)_(beam|Beam|BEAM)_(Maj|maj)$', 
                                           ]
                                         )


def recognize_beam_Min(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(beam|Beam|BEAM)[_](min|Min|minor|Minor)', 
                                             '^(min|Min|minor|Minor)[_](beam|Beam|BEAM)$', 
                                             '^(sim|rec)_(beam|Beam|BEAM)_(Min|min)$', 
                                           ]
                                         )


def recognize_beam_PA(input_str_list):
    return match_str_list_to_pattern_list( input_str_list, 
                                           [ '^(beam|Beam|BEAM)[_](PA|pa)', 
                                             '^(PA|pa)[_](beam|Beam|BEAM)$', 
                                             '^(sim|rec)_(beam|Beam|BEAM)_(PA|pa)$', 
                                           ]
                                         )




cat_file = ''
out_list = []
out_dirname = ''
out_basename = 'datatable_extracted_column_'
out_suffix = '.txt'
cmd_mode = ''
do_extract = False
do_printall = False

# 
# Read user input.
# User can input option "-extract col1 col2 col3" to extract some columns,
# and specifiy -output-dir and -output-base 
# 
i=1
while i < len(sys.argv):
    if not sys.argv[i].startswith('-'):
        if cmd_mode == '':
            if cat_file == '':
                cat_file = sys.argv[i]
        elif cmd_mode == 'extract':
            out_list.append(sys.argv[i])
        elif cmd_mode == 'output-dirname':
            out_dirname = sys.argv[i] + os.sep
        elif cmd_mode == 'output-basename':
            out_basename = sys.argv[i]
        elif cmd_mode == 'output-suffix':
            out_suffix = sys.argv[i]
    else:
        if sys.argv[i].lower() == '-extract' or sys.argv[i].lower() == '--extract' or \
           sys.argv[i].lower() == '-extract-columns' or sys.argv[i].lower() == '--extract-columns':
            do_extract = True
            cmd_mode = 'extract'
        elif sys.argv[i].lower() == '-printall' or sys.argv[i].lower() == '--printall' or \
             sys.argv[i].lower() == '-print-all' or sys.argv[i].lower() == '--print-all':
            do_printall = True
            cmd_mode = ''
        elif sys.argv[i].lower() == '-out' or sys.argv[i].lower() == '--out' or \
             sys.argv[i].lower() == '-output-dir' or sys.argv[i].lower() == '--output-dir' or \
             sys.argv[i].lower() == '-output-dirname' or sys.argv[i].lower() == '--output-dirname':
            cmd_mode = 'output-dirname'
        elif sys.argv[i].lower() == '-output-base' or sys.argv[i].lower() == '--output-base' or \
             sys.argv[i].lower() == '-output-basename' or sys.argv[i].lower() == '--output-basename':
            cmd_mode = 'output-basename'
        elif sys.argv[i].lower() == '-output-suffix' or sys.argv[i].lower() == '--output-suffix':
            cmd_mode = 'output-suffix'
    i=i+1


cat_data = CrabTable(cat_file)
col_names = cat_data.getColumnNames()

if do_printall:
    print('List of all columns: ')
    for i in range(len(col_names)):
        print('\t%d\t%s'%(i+1,col_names[i]))
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
cols['Peak_Flux'] = recognize_peak_flux(col_names)
cols['Peak_Flux_error'] = recognize_peak_flux_error(col_names)
cols['Total_Flux'] = recognize_total_flux(col_names)
cols['Total_Flux_error'] = recognize_total_flux_error(col_names)
cols['Residual_Flux'] = recognize_residual_flux(col_names)
cols['Maj'] = recognize_Maj(col_names)
cols['Min'] = recognize_Min(col_names)
cols['PA'] = recognize_PA(col_names)
cols['RMS_noise'] = recognize_RMS_noise(col_names)
cols['image_file'] = recognize_image_file(col_names)
cols['simu_name'] = recognize_simu_name(col_names)
cols['beam_Maj'] = recognize_beam_Maj(col_names)
cols['beam_Min'] = recognize_beam_Min(col_names)
cols['beam_PA'] = recognize_beam_PA(col_names)
#print(cols)


# 
# print each column
# 
for col_type in cols:
    col_name = ''
    if type(cols[col_type]) is list:
        if len(cols[col_type]) > 0:
            if do_printall:
                col_name = '; '.join(cols[col_type])
            else:
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


# 
# extract some columns according to the user input
# 
if do_extract:
    # extract columns
    # now first prepare out_dirname
    if out_dirname != '':
        if not os.path.isdir(out_dirname):
            os.makedirs(out_dirname)
    # extract each column
    for out_name in out_list:
        for col_type in cols:
            if out_name.lower == col_type.lower():
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

    





