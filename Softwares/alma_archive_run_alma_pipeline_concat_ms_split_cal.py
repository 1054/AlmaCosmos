
# Please run this code with CASA
# 
# casa -c 
# 

import os, sys, glob

uid_dirs = []
for uid_dir in os.listdir('.'):
    if uid_dir.endswith(os.sep):
        uid_dir = uid_dir[0:len(uid_dir)-1]
    if uid_dir.startswith('uid___') and uid_dir.endswith('.ms.split.cal'):
        uid_dirs.append(uid_dir)

if len(uid_dirs) == 0:
    print('Error! No "uid___*.ms.split.cal" was found!')
    sys.exit()


concatvis = 'calibrated.ms'
try:
    concat(vis=uid_dirs,
           concatvis=concatvis, 
           freqtol='20MHz')
except:
    concat(vis=uid_dirs,
           concatvis=concatvis)


#sourcevis = 'calibrated_final.ms'
#split(vis=concatvis,
#      intent='*TARGET*',
#      outputvis=sourcevis,
#      datacolumn='data')
#
#os.system('rm -rf '+concatvis)
#os.system('rm -rf '+concatvis+'.flagversions')


