#!/usr/bin/env python
# 

import os, sys, numpy

import astropy
import astropy.io.ascii as asciitable

import scipy
from scipy import interpolate

from copy import copy

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter, LogLocator, FormatStrFormatter


# define my_axis_formatter
def format_axis_tick_values(x_array):
    str_array = []
    for x in x_array:
        if x >= 100 or x <= -100:
            str_item = '%1.0f'%(x)
        else:
            str_item = '%1.1f'%(x)
        str_array.append(str_item)
    return str_array


# set up color
cmap = matplotlib.cm.get_cmap('plasma_r') # 'jet' #. 'gist_heat_r' (same as Eric J.-A. paper)
normalize = matplotlib.colors.Normalize(vmin=0.0, vmax=1.0)


# Read data
#differential_curve_1_2 = asciitable.read('Completeness_sim_Sbeam_1.0_2.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
#differential_curve_2_3 = asciitable.read('Completeness_sim_Sbeam_2.0_3.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
#differential_curve_3_4 = asciitable.read('Completeness_sim_Sbeam_3.0_4.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
#differential_curve_4_5 = asciitable.read('Completeness_sim_Sbeam_4.0_5.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_1p0_1p5 = asciitable.read('Completeness_sim_Sbeam_1.0_1.5/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_1p5_2p0 = asciitable.read('Completeness_sim_Sbeam_1.5_2.0/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_2p0_2p5 = asciitable.read('Completeness_sim_Sbeam_2.0_2.5/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_2p5_3p0 = asciitable.read('Completeness_sim_Sbeam_2.5_3.0/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_3p0_3p5 = asciitable.read('Completeness_sim_Sbeam_3.0_3.5/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_3p5_4p0 = asciitable.read('Completeness_sim_Sbeam_3.5_4.0/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_4p0_4p5 = asciitable.read('Completeness_sim_Sbeam_4.0_4.5/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_4p5_5p0 = asciitable.read('Completeness_sim_Sbeam_4.5_5.0/datatable_MC_sim_completeness_differential.S_total_sim_to_rms_noise.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
#print(differential_curve_1_2)

#differential_cube = numpy.column_stack((
#    1.0-differential_curve_1_2['incomp'].data,
#    1.0-differential_curve_2_3['incomp'].data,
#    1.0-differential_curve_3_4['incomp'].data,
#    1.0-differential_curve_4_5['incomp'].data))
differential_cube = numpy.column_stack((
    (differential_curve_1p0_1p5['incomp']).data,
    (differential_curve_1p5_2p0['incomp']).data,
    (differential_curve_2p0_2p5['incomp']).data,
    (differential_curve_2p5_3p0['incomp']).data,
    (differential_curve_3p0_3p5['incomp']).data,
    (differential_curve_3p5_4p0['incomp']).data,
    (differential_curve_4p0_4p5['incomp']).data,
    (differential_curve_4p5_5p0['incomp']).data))
print((1.0-differential_curve_1p0_1p5['incomp']).data)
print(differential_cube.T)
print(differential_cube.shape)
print(len(differential_curve_1p0_1p5['snr'].data))
x_array = numpy.power(10, numpy.linspace(numpy.log10(1.0),numpy.log10(1000.0),16)) # differential_curve_1p0_1p5['snr'].data
y_array = numpy.linspace(1.0,5.0,9)
print(x_array)
print(y_array)


# transpose so that each column is a different SNRpeak and each row is a different Theta_beam
differential_cube = differential_cube.T



# interpolate
nx = differential_cube.shape[1]
ny = differential_cube.shape[0]
xx, yy = numpy.meshgrid(numpy.arange(nx), numpy.arange(ny))
pts = numpy.array([[i,j] for i in range(nx) for j in range(ny)])
vals = differential_cube.flatten()
mask1 = ~numpy.isnan(vals) # valid values to interpolate with
pts1 = pts[mask1]
vals1 = vals[mask1]
print('pts.shape', pts.shape)
print('vals.shape', vals.shape)
#mask2 = numpy.logical_and(numpy.isnan(vals), numpy.logical_and(xx.flatten()>=7, yy.flatten()>=2)) # invalid values to interpolate for
#pts2 = pts[mask2]
#vals2 = vals[mask2]
mask2 = numpy.logical_or(numpy.logical_or(numpy.logical_or(\
            numpy.logical_and(xx.flatten()==9, yy.flatten()==2), 
            numpy.logical_and(xx.flatten()==10, yy.flatten()==5)), 
            numpy.logical_and(xx.flatten()==10, yy.flatten()==6)), 
            numpy.logical_and(xx.flatten()==12, yy.flatten()==6)) # invalid values to interpolate for
pts2 = pts[mask2]
differential_cube_original = copy(differential_cube)
differential_cube_interpolated = differential_cube.flatten()
differential_cube_interpolated[mask2] = interpolate.griddata(pts1, vals1, pts2, method='nearest')
differential_cube = differential_cube_interpolated.reshape(differential_cube.shape)
print('differential_cube.shape', differential_cube.shape)
# 
#nx = differential_cube.shape[1]
#ny = differential_cube.shape[0]
#x = numpy.arange(nx)
#y = numpy.arange(ny)
#xx, yy = numpy.meshgrid(x, y)
#zz = differential_cube
#print('xx.shape', xx.shape)
#print('yy.shape', yy.shape)
#print('zz.shape', zz.shape)
#mask = (~numpy.isnan(zz))
#xxx = xx[mask]
#yyy = yy[mask]
#zzz = zz[mask]
#print('xxx.shape', xxx.shape)
#print('yyy.shape', yyy.shape)
#print('zzz.shape', zzz.shape)
#fff = interpolate.interp2d(xxx, yyy, zzz, kind='linear')
#differential_cube_interpolated = fff(x, y)
#print('differential_cube_interpolated.shape', differential_cube_interpolated.shape)
#differential_cube_original = differential_cube
#differential_cube = differential_cube_interpolated.reshape(differential_cube.shape)
#print('differential_cube.shape', differential_cube.shape)



# make plot
fig = plt.figure(figsize=(5.5,3.0))
ax = fig.add_subplot(1,1,1)
ax.imshow(differential_cube, cmap=cmap, norm=normalize, aspect=1.0, origin='lower') # , extent=[-0.5, len(x_array)-0.5, 1.0, 5.0]
plt.xticks(numpy.arange(-0.5,len(x_array)-0.5,1), rotation=45)
plt.yticks(numpy.arange(-0.5,len(y_array)-0.5,1))
ax.set_xticklabels(format_axis_tick_values(x_array))
ax.set_yticklabels(format_axis_tick_values(y_array))
ax.set_xlabel(r'$S_{\mathrm{total,sim.}}\,/\,\mathrm{rms\,noise}$', fontsize=15)
ax.set_ylabel(r'$\Theta_{\mathrm{beam,sim.,convol.}}$', fontsize=15)
ax.yaxis.labelpad = 10
ax.tick_params(axis='x', direction='in')
ax.tick_params(axis='y', direction='in')



# Show more label
ax.text(1.00, 1.04, r'FULL$\,-\,$PYBDSF', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Now adding the colorbar
cax = fig.add_axes([0.85, 0.27, 0.03, 0.65]) # l,b,w,h
cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, ticks=[1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
cbar.ax.set_yticklabels(['0%','20%','40%','60%','80%','100%'])
cbar.ax.set_ylim(1.0,0.0)
cbar.ax.tick_params(axis='y', direction='in')
cbar.ax.text(4.3, 0.48, 'Completeness', transform=cbar.ax.transAxes, rotation=90, va='center', ha='center', fontsize=14)


# Save figure
fig.subplots_adjust(bottom=0.20, left=0.15, right=0.84, top=0.97)
fig.savefig('Plot_Completeness_blocks_for_various_source_sizes.S_total_sim_to_rms_noise.pdf')

os.system('open Plot_Completeness_blocks_for_various_source_sizes.S_total_sim_to_rms_noise.pdf')




