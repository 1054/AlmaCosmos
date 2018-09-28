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


# set up color
cmap = matplotlib.cm.get_cmap('rainbow') # 'jet'
normalize = matplotlib.colors.Normalize(vmin=1.0, vmax=5.0)
color_curve_1_2 = matplotlib.colors.rgb2hex(cmap(normalize(1.5)))
color_curve_2_3 = matplotlib.colors.rgb2hex(cmap(normalize(2.5)))
color_curve_3_4 = matplotlib.colors.rgb2hex(cmap(normalize(3.4)))
color_curve_4_5 = matplotlib.colors.rgb2hex(cmap(normalize(4.5)))
color_curve_ref = '#aaaaaa'
#print(color_curve_1_2)
#print(color_curve_2_3)
#print(color_curve_3_4)
#print(color_curve_4_5)


# Read data
differential_curve_1_2 = asciitable.read('Completeness_sim_Sbeam_1.0_2.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_2_3 = asciitable.read('Completeness_sim_Sbeam_2.0_3.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_3_4 = asciitable.read('Completeness_sim_Sbeam_3.0_4.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_4_5 = asciitable.read('Completeness_sim_Sbeam_4.0_5.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])

cumulative_curve_1_2 = asciitable.read('Completeness_sim_Sbeam_1.0_2.0/datatable_MC_sim_completeness_cumulative.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
cumulative_curve_2_3 = asciitable.read('Completeness_sim_Sbeam_2.0_3.0/datatable_MC_sim_completeness_cumulative.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
cumulative_curve_3_4 = asciitable.read('Completeness_sim_Sbeam_3.0_4.0/datatable_MC_sim_completeness_cumulative.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
cumulative_curve_4_5 = asciitable.read('Completeness_sim_Sbeam_4.0_5.0/datatable_MC_sim_completeness_cumulative.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])

differential_curve_ref = asciitable.read('Completeness_ref/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
width_of_curve_ref = 2.0 # assuming a factor of 2 uncertainty

#print(differential_curve_1_2)


# make plot
fig = plt.figure(figsize=(5.5,3.0))
ax = fig.add_subplot(1,1,1)
#
ax.plot(differential_curve_1_2['snr'], 1.0-differential_curve_1_2['incomp'], color=color_curve_1_2, marker='o', markersize=3, linestyle='none', label='Differential', zorder=9)
ax.plot(differential_curve_2_3['snr'], 1.0-differential_curve_2_3['incomp'], color=color_curve_2_3, marker='o', markersize=3, linestyle='none', label='_nolegend_', zorder=9)
ax.plot(differential_curve_3_4['snr'], 1.0-differential_curve_3_4['incomp'], color=color_curve_3_4, marker='o', markersize=3, linestyle='none', label='_nolegend_', zorder=9)
ax.plot(differential_curve_4_5['snr'], 1.0-differential_curve_4_5['incomp'], color=color_curve_4_5, marker='o', markersize=3, linestyle='none', label='_nolegend_', zorder=9)
ax.plot(differential_curve_1_2['snr'], 1.0-differential_curve_1_2['incomp'], color=color_curve_1_2, marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
ax.plot(differential_curve_2_3['snr'], 1.0-differential_curve_2_3['incomp'], color=color_curve_2_3, marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
ax.plot(differential_curve_3_4['snr'], 1.0-differential_curve_3_4['incomp'], color=color_curve_3_4, marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
ax.plot(differential_curve_4_5['snr'], 1.0-differential_curve_4_5['incomp'], color=color_curve_4_5, marker='.', markersize=1, linestyle='-', lw=1, label='_nolegend_', zorder=8)
#
ax.plot(cumulative_curve_1_2['snr'], 1.0-cumulative_curve_1_2['incomp'], markerfacecolor='none', markeredgecolor=color_curve_1_2, marker='o', markersize=4, linestyle='none', label='Cumulative')
ax.plot(cumulative_curve_2_3['snr'], 1.0-cumulative_curve_2_3['incomp'], markerfacecolor='none', markeredgecolor=color_curve_2_3, marker='o', markersize=4, linestyle='none', label='_nolegend_')
ax.plot(cumulative_curve_3_4['snr'], 1.0-cumulative_curve_3_4['incomp'], markerfacecolor='none', markeredgecolor=color_curve_3_4, marker='o', markersize=4, linestyle='none', label='_nolegend_')
ax.plot(cumulative_curve_4_5['snr'], 1.0-cumulative_curve_4_5['incomp'], markerfacecolor='none', markeredgecolor=color_curve_4_5, marker='o', markersize=4, linestyle='none', label='_nolegend_')
ax.plot(cumulative_curve_1_2['snr'], 1.0-cumulative_curve_1_2['incomp'], color=color_curve_1_2, marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
ax.plot(cumulative_curve_2_3['snr'], 1.0-cumulative_curve_2_3['incomp'], color=color_curve_2_3, marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
ax.plot(cumulative_curve_3_4['snr'], 1.0-cumulative_curve_3_4['incomp'], color=color_curve_3_4, marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
ax.plot(cumulative_curve_4_5['snr'], 1.0-cumulative_curve_4_5['incomp'], color=color_curve_4_5, marker='.', markersize=1, linestyle='dotted', lw=1, label='_nolegend_')
# 
# then shading reference completeness curve from PHYS-PyBDSM
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
ax.tick_params(axis='x', direction='in')
ax.tick_params(axis='y', direction='in')
plt.legend(bbox_to_anchor=(0.72,0.02), loc='lower center', fontsize=14, handletextpad=0.08)


# Now adding the colorbar
cax = fig.add_axes([0.85, 0.25, 0.03, 0.65]) # l,b,w,h
cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)
ax.text(1.19, 0.5, '$\Theta_{beam,sim.,convol.}$', transform=ax.transAxes, rotation=90, va='center', ha='center', fontsize=15)


# Show more label
ax.text(0.95, 0.45, 'FULL$\,-\,$PYBDSM', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Save figure
fig.subplots_adjust(bottom=0.18, left=0.15, right=0.84, top=0.95)
fig.savefig('Plot_Completeness_curves_for_various_source_sizes.pdf')

os.system('open Plot_Completeness_curves_for_various_source_sizes.pdf')




