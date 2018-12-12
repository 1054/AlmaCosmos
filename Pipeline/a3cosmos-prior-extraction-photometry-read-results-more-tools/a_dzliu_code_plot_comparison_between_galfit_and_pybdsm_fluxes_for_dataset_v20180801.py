#!/usr/bin/env python
# 

from __future__ import print_function
import pkg_resources
pkg_resources.require('astropy')
import os, sys, re, json, time, astropy
import numpy as np
import matplotlib
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table, Column, hstack
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib import ticker as ticker
from matplotlib.patches import Rectangle
from copy import copy

sys.path.append(os.path.expanduser('~')+os.sep+'Cloud'+os.sep+'Github'+os.sep+'AlmaCosmos'+os.sep+'Softwares')
from almacosmos_fit_Gaussian_1D import Func_Gaussian_1D, fit_Gaussian_1D

if sys.version_info.major <= 2:
    pass
else:
    long = int



output_name = 'Plot_comparison_between_galfit_and_pybdsm_fluxes'





def read_data():
    tb = Table.read('datatable_CrossMatched_pybdsm_to_prior_best.fits')
    #'/Volumes/GoogleDrive/Team Drives/A3COSMOS/Photometry/ALMA_full_archive/Prior_Fitting_by_Daizhong/20180106/compare_prior_vs_pybdsm_20180925/datatable_CrossMatched_pybdsm_to_prior_best.fits'
    # 
    tb['Image_pybdsm'] = [t.strip() for t in tb['Image_pybdsm']]
    tb['Image_prior'] = [t.strip() for t in tb['Image_prior']]
    mask = (tb['Peak_flux_prior']*1e3>2.5*tb['rms_prior'])
    tb = tb[mask]
    # 
    output_data = {}
    output_data['x'] = tb['Total_flux_pybdsm']*1e3 # mJy
    output_data['y'] = tb['Total_flux_prior']*1e3 # mJy
    output_data['xerr'] = tb['E_Total_flux_pybdsm']*1e3 # mJy
    output_data['yerr'] = tb['E_Total_flux_prior']*1e3 # mJy
    output_data['xpeak'] = tb['Peak_flux_pybdsm']*1e3 # mJy
    output_data['ypeak'] = tb['Peak_flux_prior']*1e3 # mJy
    output_data['xpeakerr'] = tb['Isl_rms_pybdsm']*1e3 # mJy
    output_data['ypeakerr'] = tb['rms_prior'] # mJy
    output_data['labels'] = tb['ID_prior']
    output_data['coords'] = tb['Image_pybdsm']
    output_data['images'] = tb['Image_pybdsm']
    # 
    if True:
        tbout = Table()
        for t in output_data:
            if not t in ['tb1','tb2']:
                tbout[t] = output_data[t]
        tbout.write(output_name+'.data.fits', overwrite=True)
    # 
    return output_data









# 
# main
# 
if __name__ == '__main__':
    
    if os.path.isfile(output_name+'.npy'):
        print('Found existing "%s"! Re-use it!' % (output_name+'.npy'))
        time.sleep(1.0)
        data = np.load(output_name+'.npy')
        data = data[()] # see https://stackoverflow.com/questions/30811918/saving-dictionary-of-numpy-arrays
    else:
        data = read_data()
        np.save(output_name+'.npy',data)
        print('Writting to "%s"! ' % (output_name+'.npy'))
    
    
    # 
    xarray = data['x']
    yarray = data['y']
    labels = data['labels']
    colors = (data['xpeak']/data['xpeakerr'])
    xlabel = r'$S_{\mathrm{PyBDSM}}$'
    ylabel = r'$S_{\mathrm{GALFIT}}$'
    print('len(labels) = %d' % (len(labels)))
    # 
    
    
    
    
    # consider detected data points, get histogram
    detected = np.logical_and( (data['xpeak'] / data['xpeakerr'] >= 3.0), (data['ypeak'] / data['ypeakerr'] >= 3.0) )
    var = np.log10(data['y'][detected]/data['x'][detected])
    hists, binedges = np.histogram(var, range=(-2.00, +2.00), bins=101)
    bincents = (binedges[0:-1]+binedges[1:])/2.0
    hists = np.array(hists) * 1.0
    #hists[np.argwhere(hists==np.max(hists)).flatten()] = np.nan
    
    # fit a gaussian to the histogram
    if False:
        if not os.path.isfile(output_name+'.fit'):
            fit_curve, fit_params = fit_Gaussian_1D(bincents, hists)
            print('fit_params', fit_params)
            with open(output_name+'.fit', 'w') as ofp:
                json.dump(fit_params, ofp, indent=4)
            print('Writting to "%s"' %(output_name+'.fit' ) )
        else:
            print('Loading from "%s"' %(output_name+'.fit' ) )
            with open(output_name+'.fit', 'r') as ifp:
                fit_params = json.load(ifp)
            fit_curve = Func_Gaussian_1D(bincents, fit_params['A'], fit_params['mu'], fit_params['sigma'] )
    else:
        fit_curve = []
        fit_params = {}
        fit_params['mu'] = np.median(var)
        fit_params['sigma'] = np.std(var)
        print(fit_params)
    
    # define the outlier_threshold
    #outlier_level = 3.0
    outlier_level = 5.0
    outlier_threshold = np.power(10.0, outlier_level*fit_params['sigma'])
    print('%d-sigma outlier threshold ='%(outlier_level), outlier_threshold )
    
    # print outliers
    for i in range(len(data['x'])):
        #print(detected[i], (data['y'][i]/data['x'][i]), data['labels'][i] )
        if detected[i]:
            #print((data['y'][i]/data['x'][i]), data['labels'][i] )
            if np.abs(np.log10(data['y'][i]/data['x'][i])) >= np.log10(outlier_threshold):
                print('Outlier: ID %d, S_GALFIT = %0.8f, S_PyBDSM = %0.8f, Image = "%s"' %(data['labels'][i], data['y'][i], data['x'][i], data['images'][i] ) )
    
    
    
    
    
    
    
    # 
    # make plot
    # 
    fig = plt.figure(figsize=(5.2,5.0))
    
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.4)
    
    # scatter plot
    ax1 = plt.subplot(gs[0])
    ax1_layer1_cm = plt.cm.get_cmap('jet')
    mask = np.argsort(colors)
    ax1_layer1 = ax1.scatter(data['x'][mask], data['y'][mask], s=8, c=colors[mask], norm=matplotlib.colors.LogNorm(vmin=2, vmax=60), cmap=ax1_layer1_cm, zorder=6)
    
    cbaxes = fig.add_axes([0.7, 0.55, 0.22, 0.03]) # x, y, width, height
    cbar = fig.colorbar(mappable=ax1_layer1, cax=cbaxes, orientation='horizontal', norm=matplotlib.colors.LogNorm(vmin=2, vmax=60), ticks=[3,10,50]) # ticks=[0.,1], 
    cbar.set_label(label=r'$\mathrm{S/N}_{\mathrm{peak},\,\mathrm{PyBDSM}}$', size=14)
    cbar.ax.set_xticklabels(['3','10','50'])
    cbar.ax.tick_params(labelsize=12)
    
    ax1_layer2a, ax1_layer2b, ax1_layer2c = ax1.errorbar(data['x'][mask], data['y'][mask], xerr=data['xerr'][mask], yerr=data['yerr'][mask], capsize=2, alpha=0.2, linestyle='none', linewidth=0.5, capthick=0.5, zorder=4)
    ax1_layer2c[0].set_color(cbar.to_rgba(colors[mask]))
    #ax1_layer2 = ax1.errorbar(xarray[~detected], 3.0*yerror[~detected], yerr=yerror[~detected], uplims=True, c=cbar.to_rgba(3.0), capsize=2, linestyle='none', linewidth=0.5, alpha=0.2, zorder=4) # uplims=upperlimits, lolims=lowerlimits, xuplims=True
    
    ax1.set_xlabel(xlabel, fontsize=16)
    ax1.set_ylabel(ylabel, fontsize=16)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim([2e-2,8e2])
    ax1.set_ylim([2e-2,8e2])
    ax1_layer3 = ax1.plot([1e-3,1e3], [1e-3,1e3], linestyle='--', color='k', linewidth=0.8, zorder=3)
    #ax1_legend1 = ax1.legend(loc='upper left')
    outlier_ID_2 = [831167, 605445, 334409]
    outlier_ID_2b = [735948]
    outlier_legend_x = 0.74 # label position
    outlier_legend_y = 0.62 # label position
    outlier_legend_dy = 0.06 # label line height
    outlier_count = len(outlier_ID_2) + len(outlier_ID_2b) + 1 # - 1 accounts for the header line.
    if outlier_count > 1:
        ax1.add_artist(Rectangle((outlier_legend_x-0.015, outlier_legend_y-outlier_legend_dy*outlier_count), 1.-outlier_legend_x, outlier_legend_dy*outlier_count+0.01, transform=ax1.transAxes, fc='w', fill=True, edgecolor='darkgray', alpha=0.5, lw=0.5, ls='solid')) # draw a rectangle around the label text
    for j in range(len(outlier_ID_2)):
        for i in range(len(labels)):
            if '%s'%(labels[i]) == '%s'%(outlier_ID_2[j]) and np.abs(np.log10(xarray[i]/yarray[i])) >= np.log10(outlier_threshold):
                ax1.annotate('%d'%(j+1), xy=(xarray[i], yarray[i]), xytext=(1, 1), textcoords='offset points', fontsize='11', zorder=6)
                if j==0:
                    ax1.annotate(r'%d-$\sigma$ outliers:'%(outlier_level), xy=(outlier_legend_x,outlier_legend_y), xycoords="axes fraction", fontsize='11', va='top')
                    outlier_legend_y -= outlier_legend_dy
                ax1.annotate('%d: %s'%(j+1, data['labels'][i]), xy=(outlier_legend_x,outlier_legend_y), xycoords="axes fraction", fontsize='11', va='top')
                outlier_legend_y -= outlier_legend_dy
                break
    #outlier_ID_2b = [842140]
    for j in range(len(outlier_ID_2b)):
        for i in range(len(labels)):
            if '%s'%(labels[i]) == '%s'%(outlier_ID_2b[j]) and np.abs(np.log10(xarray[i]/yarray[i])) >= np.log10(outlier_threshold):
                ax1.annotate('%s'%(chr(j+97)), xy=(xarray[i], yarray[i]), xytext=(1, 1), textcoords='offset points', fontsize='11', zorder=6) # use a,b,c to count the number.
                ax1.annotate('%s: %s'%(chr(j+97), data['labels'][i]), xy=(outlier_legend_x,outlier_legend_y), xycoords="axes fraction", fontsize='11', va='top')
                outlier_legend_y -= outlier_legend_dy
                break
        #if '%s'%(labels[i]) == '767332':
        #    ax1.annotate('%s (%s)'%(data['ID_2'][i], data['ID_1'][i]), xy=(xarray[i], yarray[i]), xytext=(0, 5), textcoords='offset points', fontsize='10', zorder=6, ha='center')
        #elif '%s'%(labels[i]) == '951838':
        #    ax1.annotate('%s (%s)'%(data['ID_2'][i], data['ID_1'][i]), xy=(xarray[i], yarray[i]), xytext=(0, 5), textcoords='offset points', fontsize='10', zorder=6, ha='center')
        #elif '%s'%(labels[i]) == '813955':
        #    ax1.annotate('%s (%s)'%(data['ID_2'][i], data['ID_1'][i]), xy=(xarray[i], yarray[i]), xytext=(-6, 5), textcoords='offset points', fontsize='10', zorder=6, ha='left')
    ax1_layer4 = ax1.plot([1e-3,1e3], np.array([1e-3,1e3])*outlier_threshold, linestyle='dotted', color='k', linewidth=0.8, zorder=3)
    ax1_layer4 = ax1.plot([1e-3,1e3], np.array([1e-3,1e3])/outlier_threshold, linestyle='dotted', color='k', linewidth=0.8, zorder=3)
    ax1.tick_params(labelsize=12)
    ax1.tick_params(direction='in', axis='both', which='both')
    ax1.tick_params(top=True, right=True, which='both') # top='on', right='on' -- deprecated -- use True/False instead
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(x),0)))).format(x) if np.abs(np.log10(x))<=3 else '$10^{%d}$'%(np.log10(x)) ) ) # https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y) if np.abs(np.log10(y))<=3 else '$10^{%d}$'%(np.log10(y)) ) ) # https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
    
    
    
    
    # histogram
    ax2 = plt.subplot(gs[1])
    ax2.set_yscale('log')
    ax2_layer1 = ax2.hist(var, bins=binedges, align='mid' )
    ax2.set_xlabel(r'$\log \ (\mathrm{S}_{\mathrm{PyBDSM}}\,/\,\mathrm{S}_{\mathrm{GALFIT}})$', fontsize=16)
    ax2.set_ylabel('N', fontsize=16)
    ax2.set_xlim([-0.5, +2])
    ax2.set_ylim([0.5, 500])
    ax2.set_yticks([1, 10, 100])
    if len(fit_curve)>0:
        ax2_layer3 = ax2.plot(bincents, fit_curve, linestyle='--', color='k', linewidth=1.6)
    ax2_layer4 = ax2.plot(np.array([0.0,0.0])-np.log10(outlier_threshold), ax2.get_ylim(), linestyle='dotted', color='k', linewidth=1.6)
    ax2_layer4 = ax2.plot(np.array([0.0,0.0])+np.log10(outlier_threshold), ax2.get_ylim(), linestyle='dotted', color='k', linewidth=1.6)
    ax2.text(np.log10(outlier_threshold)+0.01*(ax2.get_xlim()[1]-ax2.get_xlim()[0]), np.power(10.0, np.log10(ax2.get_ylim()[1])-0.05*(np.log10(ax2.get_ylim()[1])-np.log10(ax2.get_ylim()[0])) ), 
                r'$%d\sigma \ \mathrm{threshold}: $'%(outlier_level), 
                va='top', ha='left', fontsize=13)
    ax2.text(np.log10(outlier_threshold)+0.01*(ax2.get_xlim()[1]-ax2.get_xlim()[0]), np.power(10.0, np.log10(ax2.get_ylim()[1])-0.30*(np.log10(ax2.get_ylim()[1])-np.log10(ax2.get_ylim()[0])) ), 
                r'$\ \ \mathrm{S}_{\mathrm{PyBDSM}}\,/\,\mathrm{S}_{\mathrm{GALFIT}} > %0.2f$'%(outlier_threshold), 
                va='top', ha='left', fontsize=13)
    ax2.text(np.log10(outlier_threshold)+0.01*(ax2.get_xlim()[1]-ax2.get_xlim()[0]), np.power(10.0, np.log10(ax2.get_ylim()[1])-0.55*(np.log10(ax2.get_ylim()[1])-np.log10(ax2.get_ylim()[0])) ), 
                r'$\ \ \mathrm{or} \ \mathrm{S}_{\mathrm{GALFIT}}\,/\,\mathrm{S}_{\mathrm{PyBDSM}} > %0.2f$'%(outlier_threshold), 
                va='top', ha='left', fontsize=13)
    ax2.tick_params(labelsize=12)
    ax2.tick_params(direction='in', axis='both', which='both')
    ax2.tick_params(top=True, right=True, which='both')
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y))) # https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
    
    
    
    
    # savefig
    fig.subplots_adjust(left=0.20, right=0.95, bottom=0.10, top=0.95)
    fig.savefig(output_name+'.pdf')
    print('Output to "%s"' % (output_name+'.pdf'))
    os.system('open "%s"' % (output_name+'.pdf'))
    #plt.show(block=True)
    
    
    
    if True:
        for i in range(len(labels)):
            if True:
                ax1.annotate(labels[i], xy=(xarray[i], yarray[i]), xytext=(0, 0), textcoords='offset points', fontsize='2', zorder=6)
        fig.savefig(output_name+'_with_labels.pdf')
        print('Output to "%s"' % (output_name+'_with_labels.pdf'))
        os.system('open "%s"' % (output_name+'_with_labels.pdf'))



