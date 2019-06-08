#!/usr/bin/env python
# 
# 20190506: adjusted plotting range
# 

import os, sys, numpy

import astropy
import astropy.io.ascii as asciitable

import scipy
from scipy import interpolate

import copy

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
            str_item = '%1.0f'%(x)
        str_array.append(str_item)
    return str_array

def format_axis_tick_values_2(x, pos):
    if 10**x >= 100 or 10**x <= -100:
        str_item = '%1.0f'%(10**x)
    else:
        str_item = '%1.1f'%(10**x)
    return str_item


# set up color
cmap = matplotlib.cm.get_cmap('plasma_r') # 'jet' #. 'gist_heat_r' (same as Eric J.-A. paper)
normalize = matplotlib.colors.Normalize(vmin=0.0, vmax=1.0)


# Read data
differential_curve_1 = asciitable.read('Completeness_alma_beam_0.2_0.6/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_2 = asciitable.read('Completeness_alma_beam_0.6_1.0/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])
differential_curve_3 = asciitable.read('Completeness_alma_beam_1.0_1.4/datatable_MC_sim_completeness_differential.txt', names=['snr','incomp','aa','bb'], fill_values=[('-99',numpy.nan)])

differential_cube = numpy.column_stack((
    (differential_curve_1['incomp']).data,
    (differential_curve_2['incomp']).data,
    (differential_curve_3['incomp']).data,
    ))
x_array = (differential_curve_1['snr'].data)
y_array = numpy.arange(0.2, 1.4, 0.6)
print('x_array', x_array)
print('y_array', y_array)


# transpose so that each column is a different SNRpeak and each row is a different Theta_beam
differential_cube = differential_cube.T



# interpolate
print('Interpolating NAN pixels')
nx = differential_cube.shape[1]
ny = differential_cube.shape[0]
xx, yy = numpy.meshgrid(numpy.arange(nx), numpy.arange(ny))
pts = numpy.stack((yy,xx), axis=2)
vals = differential_cube
mask1 = ~numpy.isnan(vals) # valid values to interpolate with
pts1 = pts[mask1]
vals1 = vals[mask1]
mask2 = numpy.zeros(differential_cube.shape, dtype=bool)
for j in range(ny):
    for i in range(nx):
        if numpy.isnan(differential_cube[j,i]):
            print('pixel (i,j) = (%d,%d) has NAN'%(i, j))
            if i >= 1 and i <= nx-2:
                if j >= 1 and j <= ny-2:
                    #print( numpy.count_nonzero(~numpy.isnan(differential_cube[j-1:j+2,i-1:i+2])) )
                    if numpy.count_nonzero(~numpy.isnan(differential_cube[j-1:j+2,i-1:i+2])) >= 4:
                        # having 4 non-nan nearby pixels
                        mask2[j,i] = True
                elif j == 0:
                    if numpy.count_nonzero(~numpy.isnan(differential_cube[j:j+2,i-1:i+2])) >= 4:
                        # having 4 non-nan nearby pixels
                        mask2[j,i] = True
                elif j == ny-1:
                    if numpy.count_nonzero(~numpy.isnan(differential_cube[j-1:j+1,i-1:i+2])) >= 4:
                        # having 4 non-nan nearby pixels
                        mask2[j,i] = True
pts2 = pts[mask2]
#print('pts1.shape', pts1.shape)
#print('pts2.shape', pts2.shape)
differential_cube_original = copy.deepcopy(differential_cube)
differential_cube_interpolated = copy.deepcopy(differential_cube)
differential_cube_interpolated[mask2] = interpolate.griddata(pts1, vals1, pts2, method='linear')
differential_cube = differential_cube_interpolated.reshape(differential_cube.shape)
print('differential_cube.shape', differential_cube.shape)



# set plot range
user_xlim = [2.5, 60.0]



# make plot
fig = plt.figure(figsize=(5.5,2.6))
ax = fig.add_subplot(1,1,1)
ax.imshow(differential_cube, cmap=cmap, norm=normalize, aspect=1.0, origin='lower')
ax.set_xlim([numpy.argmax(x_array>=user_xlim[0])-1.0, numpy.argmax(x_array>=user_xlim[1])+1.0])
grid_xticks = numpy.arange(-0.5,len(x_array)-0.5,1.0)
grid_yticks = numpy.arange(-0.5,len(y_array)-0.5,1.0)
user_xtickvalues = numpy.array([2.5, 3.0, 4.0, 5.0, 10.0, 20.0, 50.0, 100.0])
user_xticks = numpy.interp(user_xtickvalues, x_array, grid_xticks + 0.5) # spline from value array to xaxis grid number
plt.xticks(user_xticks) # rotation=45
plt.yticks(grid_yticks + 0.5)
ax.set_xticklabels(['%g'%t for t in user_xtickvalues])
ax.set_yticklabels(['%0.1f'%t for t in y_array])
ax.set_xlabel(r'$S_{\mathrm{peak,sim.}}\,/\,\mathrm{rms\,noise}$', fontsize=15, labelpad=9)
ax.set_ylabel(r'$\theta_{\mathrm{beam,ALMA.}}$', fontsize=15)
ax.yaxis.labelpad = 10
ax.tick_params(axis='both', direction='in', labelsize=12)
ax.xaxis.set_ticks_position('both')
ax.yaxis.set_ticks_position('both')


# Show more label
ax.text(1.00, 1.08, r'FULL$\,-\,$PYBDSF', transform=ax.transAxes, va='center', ha='right', fontsize=13.5)


# Now adding the colorbar
cax = fig.add_axes([0.85, 0.22, 0.03, 0.65]) # l,b,w,h
cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, ticks=[1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
cbar.ax.set_yticklabels(['0%','20%','40%','60%','80%','100%'])
cbar.ax.set_ylim(1.0,0.0)
cbar.ax.tick_params(axis='y', direction='in')
cbar.ax.text(4.20, 0.48, 'Completeness', transform=cbar.ax.transAxes, rotation=90, va='center', ha='center', fontsize=14)



# Save figure
fig.subplots_adjust(bottom=0.13, left=0.13, right=0.83, top=0.97)
fig.savefig('Plot_Completeness_blocks_for_various_alma_beams.pdf')

os.system('open Plot_Completeness_blocks_for_various_alma_beams.pdf')




