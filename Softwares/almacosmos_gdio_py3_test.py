#!/usr/bin/env python
# 

# pip install --user --upgrade google-api-python-client

# code are mainly from 
# -- https://developers.google.com/drive/v3/web/quickstart/python

# before runing this code, make sure you have created credential via the following link: 
# https://console.developers.google.com/start/api?id=drive

import os, sys, io, re

from almacosmos_gdio_py3 import CAAP_Google_Drive_Operator





foo = CAAP_Google_Drive_Operator()
#foo.print_files_in_drive()
foo.print_all_team_drives()
#foo.get_folder_by_name('Samples')
#foo.search_files('Samples')
folders = foo.search_folders('Samples', verbose=True)
folders = foo.search_files('OptiLIB_bc03_highz.params', verbose=True)










