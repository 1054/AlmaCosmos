#!/usr/bin/env python
# 

from __future__ import print_function
import os, sys, re, time, json, math, pkg_resources
pkg_resources.require('astroquery')
pkg_resources.require('keyrings.alt')
import astroquery
import requests
from astroquery.alma.core import Alma
import astropy.io.ascii as asciitable
from operator import itemgetter, attrgetter
from copy import copy
import socket

requests.packages.urllib3.disable_warnings()



# 
# read input argument, which should be http url
# 
tar_file_urls = []
i = 1
while i < len(sys.argv):
    tar_file_urls.append(sys.argv[i])
    i = i + 1

if len(tar_file_urls) == 0:
    print('Usage: ')
    print('    %s http://your_http_link.tar' % (os.path.basename(__file__)))
    sys.exit()




# 
# function
# 
def read_file_resource_at_offset(url, offset, max_count = 1, read_data = False):
    print('')
    print('requests.get', "bytes=%d-"%(offset))
    #headers = {"Range": "bytes=0-500", "User-Agent": "Custom/0.0.1", "Accept": "*/*"}
    headers = {"Range": "bytes=%d-"%(offset), "User-Agent": "Custom/0.0.1", "Accept": "*/*"} # "Connection": "close"
    r = requests.get(url, headers=headers, stream=True, verify=False, allow_redirects=True)
    #r.raise_for_status()
    if r.status_code != 200 and r.status_code != 206:
        return None
    TAR_BLOCKSIZE = 512
    TAR_blocks = []
    TAR_block = {}
    tar_file_resources = []
    tar_file_resource = {}
    is_new_block = True
    bytes_to_read = 0
    data = b""
    count = 0
    count_file_resource = 0
    for chunk in r.iter_content(TAR_BLOCKSIZE):
        bk=0
        if is_new_block:
            TAR_block['name']      = chunk[bk:bk+100]; bk=bk+100 
            TAR_block['mode']      = chunk[bk:bk+8  ]; bk=bk+8   
            TAR_block['uid']       = chunk[bk:bk+8  ]; bk=bk+8   
            TAR_block['gid']       = chunk[bk:bk+8  ]; bk=bk+8   
            TAR_block['size']      = chunk[bk:bk+12 ]; bk=bk+12  
            TAR_block['mtime']     = chunk[bk:bk+12 ]; bk=bk+12  
            TAR_block['chksum']    = chunk[bk:bk+8  ]; bk=bk+8   
            TAR_block['typeflag']  = chunk[bk:bk+1  ]; bk=bk+1   
            TAR_block['linkname']  = chunk[bk:bk+100]; bk=bk+100 
            TAR_block['magic']     = chunk[bk:bk+6  ]; bk=bk+6   
            TAR_block['version']   = chunk[bk:bk+2  ]; bk=bk+2   
            TAR_block['uname']     = chunk[bk:bk+32 ]; bk=bk+32  
            TAR_block['gname']     = chunk[bk:bk+32 ]; bk=bk+32  
            TAR_block['devmajor']  = chunk[bk:bk+8  ]; bk=bk+8   
            TAR_block['devminor']  = chunk[bk:bk+8  ]; bk=bk+8   
            TAR_block['prefix']    = chunk[bk:bk+155]; bk=bk+155 
            TAR_block['data']      = b''
            #print('')
            print('new block!')
            tar_file_resource['offset'] = offset
            tar_file_resource['headsize'] = TAR_BLOCKSIZE
            tar_file_resource['headspace'] = TAR_BLOCKSIZE
            tar_file_resource['datasize'] = int(TAR_block['size'].rstrip(b'\x00').decode('ascii'), 8) # the size is recorded as bytes string instead of int number! It has an ending null byte. And it is octal (8-based)!
            tar_file_resource['dataspace'] = TAR_BLOCKSIZE * int(math.ceil(float(tar_file_resource['datasize']) / TAR_BLOCKSIZE))
            tar_file_resource['nextoffset'] = tar_file_resource['offset'] + tar_file_resource['headspace'] + tar_file_resource['dataspace']
            tar_file_resource['name'] = TAR_block['name'].rstrip(b'\x00').decode('utf-8')
            tar_file_resource['prefix'] = TAR_block['prefix'].rstrip(b'\x00').decode('utf-8')
            tar_file_resource['typeflag'] = TAR_block['typeflag'].decode('ascii') # type flag is a single byte char, no ending null. 
            tar_file_resource['longlink'] = ''
            print(tar_file_resource)
            tar_file_resources.append(copy(tar_file_resource))
            count_file_resource = count_file_resource + 1
            bytes_to_read = tar_file_resource['dataspace']
            is_new_block = False
        else:
            if tar_file_resource['typeflag'] == 'L' and tar_file_resource['longlink'] == '':
                tar_file_resource['longlink'] = chunk.rstrip(b'\x00').decode('utf-8')
                tar_file_resources[-1] = copy(tar_file_resource) # update the tar_file_resource in the tar_file_resources list
                print(tar_file_resource, '(updated)')
            TAR_block['data'] += chunk
            bytes_to_read -= TAR_BLOCKSIZE
        # 
        print('bytes_to_read = %d' % (bytes_to_read) )
        # 
        # finished reading this block
        if bytes_to_read == 0:
            TAR_blocks.append(copy(TAR_block))
            is_new_block = True
        # 
        count = count+1
        offset += TAR_BLOCKSIZE
        # 
        if tar_file_resource['typeflag'] == 'L' and tar_file_resource['longlink'] == '':
            continue
        # 
        #if count > 3:
        #    break
        if read_data:
            if count_file_resource >= max_count:
                break
        else:
            if count_file_resource >= max_count-1:
                break
    # 
    r.close()
    # 
    return tar_file_resources



# 
# main
# 
for tar_file_url in tar_file_urls:
    print(tar_file_url)
    
    tar_file_name = re.sub(r'^https?://(.*)/([^/]+)\.tar$', r'\2', tar_file_url)
    
    tar_file_resources = []
    if os.path.isfile(tar_file_name+'.json'):
        with open(tar_file_name+'.json', 'r') as fp:
            tar_file_resources = json.load(fp)
    
    # use requests.get() to get the file
    # 
    #r = requests.head(tar_file_url, allow_redirects=True)
    ##print(headers)
    ##print(r)
    ##print(r.headers)
    #print('Content-Length:', r.headers['Content-Length'])
    ##print(r.history)
    # 
    # we can test the http headers of partial file downloading with
    # `wget -c -v -d https://almascience.nrao.edu/dataPortal/requests/anonymous/1645420715214/ALMA/2011.0.00742.S_2013-02-08_001_of_001.tar/2011.0.00742.S_2013-02-08_001_of_001.tar`
    #headers = {"Range": "bytes=0-500", "User-Agent": "Custom/0.0.1", "Accept": "*/*"}
    #headers = {"Range": "bytes=%d-"%(offset), "User-Agent": "Custom/0.0.1", "Accept": "*/*"}
    #r = requests.get(tar_file_url, headers=headers, stream=True, verify=False, allow_redirects=True)
    #r.raise_for_status() # now moved inside read_file_resource_at_offset()
    # 
    # 
    if len(tar_file_resources) == 0:
        offset = 0
    else:
        offset = tar_file_resources[-1]['nextoffset']
    
    
    count_file_resource = 0
    max_count = 99999999 # 25 #<TODO># 
    while count_file_resource < max_count:
        tar_file_resources2 = read_file_resource_at_offset(tar_file_url, offset)
        if tar_file_resources2 is None:
            break
        tar_file_resources.extend(tar_file_resources2)
        offset = tar_file_resources[-1]['nextoffset']
        count_file_resource += 1
        time.sleep(1.283)
    
    with open(tar_file_name+'.json', 'w') as fp:
        json.dump(tar_file_resources, fp, indent=4)
    
    sys.exit()
    
    # use socket to download the file 
    #connect_host = re.sub(r'^https?://([^/]+?)/(.+)', r'\1', tar_file_url)
    #connect_path = re.sub(r'^https?://([^/]+?)/(.+)', r'\2', tar_file_url)
    #connect_file = re.sub(r'^https?://(.*)/([^/]+)$', r'\2', tar_file_url)
    #connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect_sock.connect((connect_host, 80))
    #connect_smsg = (\
    #    bytes("GET /%s HTTP/1.1\r\n"%(connect_path), 'utf-8')+\
    #    bytes("Host: %s\r\n"%(connect_host), 'utf-8')+\
    #    bytes("Range: bytes=%d-%d\r\n"%(0,500), 'utf-8')+\
    #    #bytes("Content-Length: %d\r\n"%(500), 'utf-8')+\
    #    bytes("Content-Type: \r\n", 'utf-8')+\
    #    bytes("Content-Disposition: attachment;filename=%s\r\n"%(connect_file), 'utf-8')+\
    #    #bytes("Vary: Accept-Charset,Accept-Encoding,Accept-Language,Accept\r\n", 'utf-8')+\
    #    #bytes("Accept: */*\r\n", 'utf-8')+\
    #    #bytes("User-Agent: Custom/0.0.1\r\n", 'utf-8')+\
    #    #bytes("Connection: close\r\n", 'utf-8')+\
    #    bytes("\r\n", 'utf-8')
    #)
    #print('')
    #print(connect_smsg.decode('utf-8'))
    #connect_sock.send(connect_smsg)
    #print(connect_sock)
    #print('')
    #print("Range: bytes=%d-%d\r\n"%(1,500))
    #MAX_LIMIT = 1024
    #MAX_COUNT = 3 # max count when size is not increased
    #curr_size = 0
    #prev_size = 0
    #curr_count = 0
    #data = ""
    #while curr_size < MAX_LIMIT:
    #    time.sleep(1.5)
    #    print('len(data) = %d' % (len(data)))
    #    data += connect_sock.recv(MAX_LIMIT - curr_size).decode()
    #    curr_size = len(data)
    #    curr_count = curr_count + 1
    #    if curr_count >= MAX_COUNT and prev_size == curr_size:
    #        break
    #    prev_size = curr_size
    #connect_sock.close()
    #
    #print(data)

    # tar file format 
    # -- https://www.gnu.org/software/tar/manual/html_node/Standard.html
    # struct posix_header
    # {                              /* byte offset */
    #   char name[100];               /*   0 */
    #   char mode[8];                 /* 100 */
    #   char uid[8];                  /* 108 */
    #   char gid[8];                  /* 116 */
    #   char size[12];                /* 124 */
    #   char mtime[12];               /* 136 */
    #   char chksum[8];               /* 148 */
    #   char typeflag;                /* 156 */
    #   char linkname[100];           /* 157 */
    #   char magic[6];                /* 257 */
    #   char version[2];              /* 263 */
    #   char uname[32];               /* 265 */
    #   char gname[32];               /* 297 */
    #   char devmajor[8];             /* 329 */
    #   char devminor[8];             /* 337 */
    #   char prefix[155];             /* 345 */
    #                                 /* 500 */
    # };



