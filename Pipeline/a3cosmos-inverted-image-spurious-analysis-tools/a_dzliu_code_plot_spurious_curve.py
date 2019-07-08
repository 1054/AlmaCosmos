#!/usr/bin/env python
# 
# 20190506: focusing on SNRpeak 3-10, plotting range 1-20
# 

import os, sys, numpy

import astropy
import astropy.io.ascii as asciitable

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter, LogLocator


# define my_axis_formatter
def my_yaxis_formatter_function(x, pos):
    'The two args are the value and tick position'
    return '%1.0f%%'%(x*100.0)

my_yaxis_formatter = FuncFormatter(my_yaxis_formatter_function)


# set color
color_curve = '#222222'
color_curve_ref = '#aaaaaa'


# Read data
differential_curve = asciitable.read('Spurious/datatable_spurious_fraction_differential.txt', names=['snr','spur','aa','bb'], fill_values=[('-99',numpy.nan)])
cumulative_curve = asciitable.read('Spurious/datatable_spurious_fraction_cumulative.txt', names=['snr','spur','aa','bb'], fill_values=[('-99',numpy.nan)])


# make plot
fig = plt.figure(figsize=(5.5,3.0))
ax = fig.add_subplot(1,1,1)
# 
ax.plot(differential_curve['snr'], differential_curve['spur'], color=color_curve, marker='o', markersize=3, linestyle='none', label='Differential', zorder=9)
ax.plot(differential_curve['snr'], differential_curve['spur'], color=color_curve, marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
# 
ax.plot(cumulative_curve['snr'], cumulative_curve['spur'], markerfacecolor='none', markeredgecolor=color_curve, marker='o', markersize=4, linestyle='none', label='Cumulative')
ax.plot(cumulative_curve['snr'], cumulative_curve['spur'], color=color_curve, marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
# 
ax.set_xlabel(r'$\mathrm{S/N_{peak}} \equiv S_{\mathrm{peak,rec.}}\,/\,\mathrm{rms\,noise}$', fontsize=15)
ax.set_ylabel('Spurious', fontsize=15)
ax.set_xscale('log')
#ax.set_xlim([1,200]) #<20190506>#
ax.set_xlim([2.0,30]) #<20190506>#
ax.set_ylim([-0.02,1.02])
ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1.0,2.0,3.0,4.0,5.0,6.0,7.0)))
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_major_formatter(my_yaxis_formatter)
ax.yaxis.labelpad = 3
ax.grid(True)
ax.yaxis.grid(color='gray', linestyle='dotted')
ax.xaxis.grid(color='gray', linestyle='dotted')
ax.tick_params(axis='x', which='both', direction='in')
ax.tick_params(axis='y', which='both', direction='in')
plt.legend(bbox_to_anchor=(0.72,0.98), loc='upper center', fontsize=13.5, handletextpad=0.08)


# Show more label
print(os.getcwd())
if os.getcwd().find('blind')>=0 or os.getcwd().find('Blind_Extraction')>=0:
    ax.text(0.90, 0.58, 'Blind Extraction', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)
elif os.getcwd().find('GALFIT')>=0 or os.getcwd().find('Prior_Fitting')>=0:
    ax.text(0.90, 0.58, 'Prior Fitting', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Save figure
fig.subplots_adjust(bottom=0.18, left=0.15, right=0.84, top=0.95)
fig.savefig('Plot_Spurious_curve.pdf')

os.system('open Plot_Spurious_curve.pdf')




