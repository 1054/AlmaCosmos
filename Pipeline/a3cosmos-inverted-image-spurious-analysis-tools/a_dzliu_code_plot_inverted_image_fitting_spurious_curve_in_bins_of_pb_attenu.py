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
color_list = ['#1e90ff', 'orange', '#222222']


# set output name
output_name = 'Plot_inverted_image_fitting_spurious_curve_in_bins_of_pb_attenu.pdf'


# make plot
fig = plt.figure(figsize=(5.5,3.0))
ax = fig.add_subplot(1,1,1)

# set and loop pb_attenu_range0 pb_attenu_range1
pb_attenu_str_list = ['0.20', '0.34', '0.58', '1.00']
for i in range(len(pb_attenu_str_list)-1):
    data_dir = 'output_spurious_analysis_bin_by_pb_attenu_%s_%s'%(pb_attenu_str_list[i], pb_attenu_str_list[i+1])
    # Read data
    differential_curve = asciitable.read(data_dir+os.sep+'datatable_spurious_fraction_differential.txt', names=['snr','spur','aa','bb'], fill_values=[('-99',numpy.nan)])
    cumulative_curve = asciitable.read(data_dir+os.sep+'datatable_spurious_fraction_cumulative.txt', names=['snr','spur','aa','bb'], fill_values=[('-99',numpy.nan)])
    # plot 
    ax.plot(differential_curve['snr'], differential_curve['spur'], color=color_list[i], marker='o', markersize=3, linestyle='none', label='pb_attenu=%s-%s'%(pb_attenu_str_list[i], pb_attenu_str_list[i+1]), zorder=9)
    ax.plot(differential_curve['snr'], differential_curve['spur'], color=color_list[i], marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
    # 
    ax.plot(cumulative_curve['snr'], cumulative_curve['spur'], markerfacecolor='none', markeredgecolor=color_list[i], marker='o', markersize=4, linestyle='none', label='_nolegend_') # label='Cumulative'
    ax.plot(cumulative_curve['snr'], cumulative_curve['spur'], color=color_list[i], marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
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
plt.legend(loc='upper right', fontsize=12, handletextpad=0.0, labelspacing=0.15, borderpad=0.2, borderaxespad=0.2)


# Show more label
print('pwd', os.getcwd())
if os.getcwd().find('blind')>=0 or os.getcwd().find('Blind_Extraction')>=0:
    ax.text(0.98, 0.65, 'Blind Extraction', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)
elif os.getcwd().find('GALFIT')>=0 or os.getcwd().find('Prior_Fitting')>=0:
    ax.text(0.98, 0.65, 'Prior Fitting', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Save figure
fig.subplots_adjust(bottom=0.18, left=0.15, right=0.84, top=0.95)
fig.savefig(output_name)
print('Saved to "%s"'%(output_name))
os.system('open "%s"'%(output_name))




