#!/usr/bin/env python
# 

import os, sys, time, re, glob


# 
# check Python version, must > 3.5 so as to use glob with '**' pattern
#if sys.version_info < (3, 5):
#    print('Sorry! The Python version is lower than 3.5, but we need version >= 3.5!')
#    sys.exit()


# 
# check directories
check_ok = True
if not os.path.isdir('By_Project'):
    print('Error! \"By_Project\" was not found under current directory!')
    check_ok = False
if not check_ok:
    sys.exit()


# 
# make directories
if not os.path.isdir('By_PI'):
    os.makdirs('By_PI')


# 
# define function
def a_dzliu_python_subroutine_to_list_files_and_subfolders(input_path, search_pattern = '', verbose = True, maxdepth = None, current_depth = None):
    # 
    list_of_files = []
    list_of_subfolders = []
    # 
    if current_depth is None:
        current_depth = 1
    # 
    if maxdepth is not None:
        if current_depth > maxdepth:
            return list_of_files, list_of_subfolders
    # 
    for current_path, list_of_subfolders, list_of_files in os.walk(input_path):
        if verbose: print(current_path)
        continue
        # list files
        for filename in list_of_files:
            if search_pattern == '':
                list_of_files.append(current_path + os.sep + filename)
                #if verbose: print(current_path + os.sep + filename)
            elif re.match(search_pattern, filename):
                list_of_files.append(current_path + os.sep + filename)
                #if verbose: print(current_path + os.sep + filename)
        # check depth
        # list subfolders and recursively list files therein
        for subfoldername in list_of_subfolders:
            list_of_subfolders.append(current_path + os.sep + subfoldername)
            if verbose: print(current_path + os.sep + subfoldername)
            list2_of_files, list2_of_subfolders = a_dzliu_python_subroutine_to_list_files_and_subfolders(current_path + os.sep + subfoldername, search_pattern = search_pattern, current_depth = current_depth+1, maxdepth = maxdepth)
            if len(list2_of_files) > 0:
                list_of_files.extend(list2_of_files)
            if len(list2_of_subfolders) > 0:
                list_of_subfolders.extend(list2_of_subfolders)
    # 
    return list_of_files, list_of_subfolders


# 
# search for README files
#list_of_readme_files = glob.glob('By_Project', 'README')
#print(list_of_readme_files)
#a_dzliu_python_subroutine_to_list_files_and_subfolders('By_Project', search_pattern='README', maxdepth=3)
for list_of_dir_paths, list_of_dir_names, list_of_file_names in os.walk('By_Project'):
    if 'README' in list_of_file_names or True:
        print('list_of_dir_paths = ', list_of_dir_paths)
        print('list_of_dir_names = ', list_of_dir_names)
        print('list_of_file_names = ', list_of_file_names)


















