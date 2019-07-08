#!/usr/bin/python
# -*- coding: utf-8 -*-
# 

################################
# 
# 
################################

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

import os, sys, io, re
from datetime import datetime










# 
class CrabLogger(object):
    # "Lumberjack class - duplicates sys.stdout to a log file and it's okay"
    # source: http://stackoverflow.com/q/616645
    # see -- http://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python/2216517#2216517
    # usage:
    #    Output_Logger = CrabLogger()
    #    Output_Logger.begin_log_file()
    #    print('works all day')
    #    Output_Logger.end_log_file()
    #    Output_Logger.close()
    # 
    def __init__(self):
        self.file = None
        self.filename = ''
        self.stdout = sys.stdout
        sys.stdout = self
    
    def __del__(self):
        self.close()
    
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
    
    def begin_log_file(self, filename="CrabLogger.log", mode="a", buff=None):
        if self.file != None:
            self.file.close()
            self.file = None
        if filename != '':
            self.filename = filename
            if buff is None:
                self.file = open(filename, mode)
            else:
                self.file = open(filename, mode, buff)
            self.file.write("# %s\n\n"%(str(datetime.now()))) # write current time # datetime.isoformat(datetime.today())
    
    def end_log_file(self):
        if self.file != None:
            self.file.write("\n# %s\n"%(str(datetime.now()))) # write current time # datetime.isoformat(datetime.today())
            self.file.close()
            self.file = None
    
    def write(self, message):
        self.stdout.write(message)
        if self.file != None:
            self.file.write(message)
    
    def flush(self):
        self.stdout.flush()
        if self.file != None:
            self.file.flush()
            os.fsync(self.file.fileno())
    
    def close(self):
        if self.stdout != None:
            sys.stdout = self.stdout
            self.stdout = None
        if self.file != None:
            self.file.close()
            self.file = None
















