#!/usr/bin/env python
# 

import os, sys
import numpy as np

import astropy
from astropy.table import Table

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import ScalarFormatter, FuncFormatter, FormatStrFormatter, NullFormatter, LogLocator


# read data
# cd 
tb = Table.read('cat_pybdsm_concatenated_negative_290318_mJy_within_cosmos_without_very_high_res_projects.fits')
mask = (tb['Pbcor']>=0.2)
Pbcor = tb['Pbcor'][mask].data
SNRpeak = tb['Peak_flux'][mask].data / tb['rms_noise'][mask].data



# prepare function
def calc_primary_beam_attenuation(primary_beam_dist, sky_wavelength):
    # primary_beam_dist # arcsec
    primary_beam_disq = primary_beam_dist**2
    # sky_wavelength = 2.99792458e5/sky_frequency # um
    primary_beam_diam = 12.0 # ALMA 12m
    #primary_beam_tape = 10.0 # https://safe.nrao.edu/wiki/bin/view/ALMA/AlmaPrimaryBeamCorrection
    #primary_beam_bpar = 1.243 - 0.343 * primary_beam_tape + 0.12 * primary_beam_tape**2 # http://legacy.nrao.edu/alma/memos/html-memos/alma456/memo456.pdf -- Eq(18)
    primary_beam_bpar = 1.13
    primary_beam_fwhm = primary_beam_disq*0.0 + primary_beam_bpar * sky_wavelength / (primary_beam_diam*1e6) / np.pi * 180.0 * 3600.0 # arcsec
    primary_beam_sigm = primary_beam_disq*0.0 + primary_beam_fwhm/(2.0*np.sqrt(2.0*np.log(2)))
    primary_beam_attenuation = np.exp((-primary_beam_disq)/(2.0*((primary_beam_sigm)**2))) #<TODO><20170613># 
    return primary_beam_attenuation

# prepare function
def calc_primary_beam_dist(primary_beam_attenuation, sky_wavelength):
    # inversed process of calc_primary_beam_attenuation
    primary_beam_diam = 12.0 # ALMA 12m
    primary_beam_bpar = 1.13
    primary_beam_fwhm = primary_beam_attenuation*0.0 + primary_beam_bpar * sky_wavelength / (primary_beam_diam*1e6) / np.pi * 180.0 * 3600.0 # arcsec
    primary_beam_sigm = primary_beam_attenuation*0.0 + primary_beam_fwhm/(2.0*np.sqrt(2.0*np.log(2)))
    primary_beam_disq = - np.log(primary_beam_attenuation) * (2.0*((primary_beam_sigm)**2))
    primary_beam_dist = np.sqrt(primary_beam_disq)
    return primary_beam_dist/primary_beam_fwhm # return normalized value



# prepare figure
fig = plt.figure(figsize=(5.5,4.5))
figGridSpec = gridspec.GridSpec(ncols=1, nrows=4, figure=fig)

# make plot 1
ax = fig.add_subplot(figGridSpec[0:3, 0])

# plot data 1
ax.scatter(Pbcor, SNRpeak, s=1.2)

# tune axes
ax.set_xlim([0.19, 1.05])
ax.set_xscale('log')
ax.set_yscale('log')
#ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(0.1,5.0)))
#ax.xaxis.set_major_formatter(ScalarFormatter())
ax.set_xticks([0.2, 0.3, 0.4, 0.5, 0.7, 1.0])
ax.set_yticks([3, 4, 5, 6, 7, 8, 9, 10])
ax.xaxis.set_major_formatter(NullFormatter())
ax.xaxis.set_minor_formatter(NullFormatter())
ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
ax.yaxis.set_minor_formatter(FormatStrFormatter('%g'))
#ax.yaxis.labelpad = 3
#ax.grid(True, color='gray', linestyle='dotted')
ax.tick_params(axis='x', which='both', direction='in', labelsize=12)
ax.tick_params(axis='y', which='both', direction='in', labelsize=12)
ax.xaxis.set_ticks_position('both')
ax.yaxis.set_ticks_position('both')

# axes titles
ax.set_ylabel(r'$S/N_{\mathrm{peak}}$', labelpad=6, fontsize=14)




# make plot 2
ax = fig.add_subplot(figGridSpec[3:, 0])

# plot data 2
binhist, binedges = np.histogram(np.log(Pbcor), bins=np.linspace(np.log(0.2),np.log(1.0),num=15,endpoint=True))
binloc = np.exp(binedges[0:-1])
binwidth = np.exp(binedges[1:]) - binloc
ax.bar(binloc, binhist, width=binwidth*0.95, align='edge', edgecolor='C0', lw=1.5, color='#1f77b466')
#binvalue = binloc * 0.0
#for i in range(len(binloc)):
#    binvalue[i] = np.median(SNRpeak[np.logical_and(Pbcor>=binloc[i],Pbcor<binloc[i]+binwidth[i])])
#ax.bar(binloc, binvalue, width=binwidth*0.95, align='edge', edgecolor='C0', lw=1.5, color='#1f77b466')

# tune axes
ax.set_xlim([0.19, 1.05])
#ax.set_ylim([3.0, 5.0])
ax.set_xscale('log')
#ax.set_yscale('log')
ax.set_xticks([0.2, 0.3, 0.4, 0.5, 0.7, 1.0])
#ax.set_yticks([0, 50, 100, 150,])
ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
ax.xaxis.set_minor_formatter(NullFormatter())
#ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
#ax.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))
ax.tick_params(axis='x', which='both', direction='in', labelsize=12)
ax.tick_params(axis='y', which='both', direction='in', labelsize=12)
ax.xaxis.set_ticks_position('both')
ax.yaxis.set_ticks_position('both')

# axes titles
ax.set_xlabel('Primary beam attenuation', labelpad=8, fontsize=14)
#ax.set_ylabel(r'$\left<S/N_{\mathrm{peak}}\right>$', fontsize=14)
ax.set_ylabel(r'$N$', fontsize=14)



# adjust margins
fig.subplots_adjust(bottom=0.13, left=0.13, right=0.98, top=0.98, hspace=0.2)

## Show more label
#print(os.getcwd())
#if os.getcwd().find('blind')>=0 or os.getcwd().find('Blind_Extraction')>=0:
#    ax.text(0.90, 0.58, 'Blind Extraction', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)
#elif os.getcwd().find('GALFIT')>=0 or os.getcwd().find('Prior_Fitting')>=0:
#    ax.text(0.90, 0.58, 'Prior Fitting', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Save figure
fig.savefig('Plot_inverted_image_fitting_SNRpeak_versus_Pbcor.pdf')

os.system('open Plot_inverted_image_fitting_SNRpeak_versus_Pbcor.pdf')




