#!/usr/bin/env python
# 
# 20190503

import os, sys, re, copy, datetime
import warnings
warnings.simplefilter("ignore")
import numpy as np
import astropy
from astropy.table import Table

import matplotlib
import matplotlib.pyplot as plt

xarray = 
yarray = 
xtitle = 
ytitle = 
output_name = 

fig = plt.figure(figsize=(15.0, 4.0))
ax = fig.add_subplot(1,1,1)
ax.plot(xarray, xarray*0.0, linestyle='solid', linewidth=0.9, color='#555555')
ax.step(xarray, yarray)
ax.tick_params(axis='both', which='major', direction='in', labelsize=13)
ax.xaxis.set_ticks_position('both')
ax.yaxis.set_ticks_position('both')
ax.set_xlabel(xtitle, fontsize=15, labelpad=10)
ax.set_ylabel(ytitle, fontsize=15, labelpad=10)
fig.tight_layout()
fig.savefig(output_name+'.pdf', dpi=250, overwrite=True)

print('Output to "%s"!'%(output_name+'.pdf'))
    









