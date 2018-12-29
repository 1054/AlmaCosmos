#!/usr/bin/env python
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
differential_curve = asciitable.read('Completeness/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
cumulative_curve = asciitable.read('Completeness/datatable_MC_sim_completeness_cumulative.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])

differential_curve_ref = asciitable.read('Completeness/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
width_of_curve_ref = 2.0 # assuming a factor of 2 uncertainty


# make plot
fig = plt.figure(figsize=(5.5,3.0))
ax = fig.add_subplot(1,1,1)
# 
ax.plot(differential_curve['snr'], 1.0-differential_curve['incomp'], color=color_curve, marker='o', markersize=3, linestyle='none', label='Differential', zorder=9)
ax.plot(differential_curve['snr'], 1.0-differential_curve['incomp'], color=color_curve, marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
# 
ax.plot(cumulative_curve['snr'], 1.0-cumulative_curve['incomp'], markerfacecolor='none', markeredgecolor=color_curve, marker='o', markersize=4, linestyle='none', label='Cumulative')
ax.plot(cumulative_curve['snr'], 1.0-cumulative_curve['incomp'], color=color_curve, marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
# 
# then shading the completeness curve
#ax.fill_between(differential_curve_ref['snr'], (1.0-differential_curve_ref['incomp']/width_of_curve_ref), (1.0-differential_curve_ref['incomp']*width_of_curve_ref), edgecolor=color_curve_ref, facecolor='none', hatch='////', lw=0, label='_nolegend_', zorder=1)
ax.fill_between(differential_curve_ref['snr'], (1.0-differential_curve_ref['incomp']/width_of_curve_ref), (1.0-differential_curve_ref['incomp']*width_of_curve_ref), edgecolor=color_curve_ref, facecolor='none', alpha=0.2, hatch='\\\\\\\\\\', lw=0, label='_nolegend_', zorder=1)
ax.fill_between(differential_curve_ref['snr'], (1.0-differential_curve_ref['incomp']/width_of_curve_ref), (1.0-differential_curve_ref['incomp']*width_of_curve_ref), color=color_curve_ref, alpha=0.2, lw=0, label='_nolegend_', zorder=1)
# 
ax.set_xlabel(r'$S_{\mathrm{peak,sim.}}\,/\,\mathrm{rms\,noise}$', fontsize=15)
ax.set_ylabel('Completeness', fontsize=15)
ax.set_xscale('log')
ax.set_xlim([1,500])
ax.set_ylim([0,1.1])
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_major_formatter(my_yaxis_formatter)
ax.yaxis.labelpad = 3
ax.grid(True)
ax.yaxis.grid(color='gray', linestyle='dotted')
ax.xaxis.grid(color='gray', linestyle='dotted')
ax.tick_params(axis='x', which='both', direction='in')
ax.tick_params(axis='y', which='both', direction='in')
plt.legend(bbox_to_anchor=(0.72,0.02), loc='lower center', fontsize=14, handletextpad=0.08)


# Show more label
print(os.getcwd())
if os.getcwd().find('blind')>=0 and os.getcwd().find('Physically_Motivated')>=0:
    ax.text(0.95, 0.45, 'PHYS$\,-\,$PYBDSF', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)
elif os.getcwd().find('blind')>=0 and os.getcwd().find('Parameter_Sampled')>=0:
    ax.text(0.95, 0.45, 'FULL$\,-\,$PYBDSF', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)
elif os.getcwd().find('GALFIT')>=0 and os.getcwd().find('Parameter_Sampled')>=0:
    ax.text(0.95, 0.45, 'FULL$\,-\,$GALFIT', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Save figure
fig.subplots_adjust(bottom=0.18, left=0.15, right=0.84, top=0.95)
fig.savefig('Plot_Completeness_curve.pdf')

os.system('open Plot_Completeness_curve.pdf')




