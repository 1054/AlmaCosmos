#!/usr/bin/env python
# 
# copied from "alma_archive_find_casa_version_in_qa_weblog.py", for html not in *.tgz.
# 

from __future__ import print_function
import os, sys
from glob import glob
import tarfile
from bs4 import BeautifulSoup


# Print Usage
if len(sys.argv) <= 1:
    print('Usage: %s %s'%(os.path.basename(__file__), '/path/to/qa/member*.html'), file=sys.stderr)
    sys.exit()


# Read User Input
weblog_html = sys.argv[1]


# Check weblog html
if not os.path.isfile(weblog_html):
    print('Error! Could not find "%s"!'%(weblog_html), file=sys.stderr)
    sys.exit()


# Prepare to get casa_version
casa_version = ''


with open fp.open(weblog_html, 'r') as weblog_index_html:
    #print(weblog_index_html, file=sys.stderr)
    weblog_index_html_content = weblog_index_html.read()

    soup = BeautifulSoup(weblog_index_html_content, 'html.parser')

    #for soup_th in [t.parent for t in soup.findAll(text='CASA Version') if t.parent.name=='th']
    for soup_th in soup.findAll('th', text='CASA Version'):
        #print(soup_th) # soup_th.name # soup_th.text
        for soup_td in soup_th.find_next_siblings():
            #print(soup_td.text)
            if len(soup_td.text) > 0:
                if soup_td.text.find('.') > 0:
                    if soup_td.text.find(' ') > 0:
                        casa_version = soup_td.text.split()[0]
                    else:
                        casa_version = soup_td.text
            if casa_version != '':
                break
        
        if casa_version != '':
            break

    if casa_version != '':
        break

print('CASA version %s'%(casa_version))


