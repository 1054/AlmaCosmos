#!/usr/bin/env python
# 
# 
# Here we use Python to calculate MC sim statistics
# in each grid cell of a N-parameter space
# 
# 20180225 Supercedes 'almacosmos_calc_simu_stats.sm'
# 20180305 Try x2 = (Maj_out*Min_out)/(Maj_beam*Min_beam), instead of x2 = Maj_out/Maj_beam. 
# 
# 

try:
    import pkg_resources
except ImportError:
    raise SystemExit("Error! Failed to import pkg_resources!")

pkg_resources.require("numpy")
pkg_resources.require("astropy")
pkg_resources.require("scipy")
pkg_resources.require("matplotlib")

import os, sys, copy, json
from copy import copy
import astropy.io.ascii as asciitable

if len(sys.argv) < 2:
    print('Usage: almacosmos_calc_simu_stats.py Input_MC_simulated_and_recovered_catalog.fits')
    sys.exit()




# 
# Import crabtable etc
# 
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabtable')
from CrabTable import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabplot')
from CrabPlot import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0])))+os.sep+'Softwares'+os.sep+'lib_python_dzliu'+os.sep+'crabgaussian')
from CrabGaussian import *



# 
# Function
# 
def calc_asymmetric_scatters(input_array, clip_sigma = 5.0, log_file = ''):
    # 3-sigma clipping
    arr = numpy.array(copy(input_array))
    arr_sigma = numpy.std(arr, ddof=1) # unbiased stddev, see https://stackoverflow.com/questions/27600207/why-does-numpy-std-give-a-different-result-to-matlab-std
    arr_mean = numpy.mean(arr)
    arr_median = numpy.median(arr)
    arr_clip = (arr < arr_median-clip_sigma*arr_sigma) | (arr > arr_median+clip_sigma*arr_sigma)
    arr_clip_args = numpy.argwhere(arr_clip)
    arr_clip_count = len(arr_clip_args)
    if(len(arr_clip_args)>0):
        arr = numpy.delete(arr, arr_clip_args)
    arr_sigma = numpy.nanstd(arr, ddof=1) # unbiased stddev, see https://stackoverflow.com/questions/27600207/why-does-numpy-std-give-a-different-result-to-matlab-std
    arr_mean = numpy.nanmean(arr)
    arr_median = numpy.nanmedian(arr)
    arr_max = numpy.nanmax(arr)
    arr_min = numpy.nanmin(arr)
    #arr_middle = arr_mean # mean is not good, too biased to outlier values
    arr_middle = arr_median
    # 
    # now we got arr_middle and sigma
    # we compute the size of array starting from arr_middle to lower and upper
    arr_clip_L68 = (arr<=arr_middle)
    arr_clip_H68 = (arr>=arr_middle)
    arr_size_L68 = len(numpy.argwhere(arr_clip_L68))
    arr_size_H68 = len(numpy.argwhere(arr_clip_H68))
    # 
    # prepare log file
    if log_file != '':
        log_file_stream = open(log_file, 'w')
        if(len(arr_clip_args)>0):
            print('Debug: calc_asymmetric_scatters: clipped %d data out of range %s %s'%( \
                    arr_clip_count, arr_mean-clip_sigma*arr_sigma, arr_mean+clip_sigma*arr_sigma \
                ), file = log_file_stream \
            )
    # 
    # now we count lower side
    arr_scatter_L68 = numpy.nan
    if arr_size_L68 > 5 and arr_min < arr_middle:
        arr_step_L68 = numpy.min( [ (arr_middle - arr_min) / 50.0, arr_sigma / 10.0 ] )
        arr_loop_L68 = arr_middle
        while arr_loop_L68 >= arr_min:
            if log_file != '':
                print('Debug: calc_asymmetric_scatters: L68: looping %s toward %s, count %s vs %s'%(
                        arr_loop_L68, arr_min, len(numpy.argwhere((arr>=arr_loop_L68) & (arr<=arr_middle))), arr_size_L68*0.682689492137086
                    ), file = log_file_stream
                )
            if len(numpy.argwhere((arr>=arr_loop_L68) & (arr<=arr_middle))) > arr_size_L68*0.682689492137086:
                arr_scatter_L68 = arr_middle-arr_loop_L68
                break
            arr_loop_L68 = arr_loop_L68 - arr_step_L68
    # 
    # now we count upper side
    arr_scatter_H68 = numpy.nan
    if arr_size_H68 > 5 and arr_max > arr_middle:
        arr_step_H68 = numpy.min( [ (arr_max - arr_middle) / 50.0, arr_sigma / 10.0 ] )
        arr_loop_H68 = arr_middle
        while arr_loop_L68 <= arr_max:
            if log_file != '':
                print('Debug: calc_asymmetric_scatters: H68: looping %s toward %s, count %s vs %s'%(
                        arr_loop_H68, arr_max, len(numpy.argwhere((arr<=arr_loop_H68) & (arr>=arr_middle))), arr_size_H68*0.682689492137086
                    ), file = log_file_stream
                )
            if len(numpy.argwhere((arr<=arr_loop_H68) & (arr>=arr_middle))) > arr_size_H68*0.682689492137086:
                arr_scatter_H68 = arr_loop_H68-arr_middle
                break
            arr_loop_H68 = arr_loop_H68 + arr_step_H68
    # 
    # close log file
    if log_file != '':
        log_file_stream.close()
    # 
    # return
    return arr_mean, arr_median, arr_sigma, arr_scatter_L68, arr_scatter_H68





































# 
# Read user inputs
# 
Input_MC_cat_file = ''
Output_dir = ''
Simulation_Phys = False # whether this is a physically motivated simulation with real luminosity function source distribution
iarg = 1 # skip sys.argv[0] which is the program itself
while iarg < len(sys.argv):
    if sys.argv[iarg].lower().startswith('-'):
        if sys.argv[iarg].lower() == '-out':
            if iarg+1 < len(sys.argv):
                iarg = iarg+1
                Output_dir = sys.argv[iarg]
        elif sys.argv[iarg].lower() == '-phys':
            Simulation_Phys = True
    else:
        if Input_MC_cat_file == '':
            Input_MC_cat_file = sys.argv[iarg]
    iarg = iarg + 1


# 
# Read MC sim input catalog with S_in, S_out, e_S_out, S_peak
# 
MC_cat = CrabTable(Input_MC_cat_file)


# 
# Check columns
# 
Col_check_OK = True
for Col_name in ['ID', 'Maj_in', 'Min_in', 'PA_in', 'S_in', 'S_out', 'e_S_out', 'S_peak', 'S_res', 'noise', 'Maj_out', 'Min_out', 'PA_out', 'Maj_beam', 'Min_beam', 'PA_beam']: 
    if Col_name in MC_cat.TableHeaders:
        globals()[Col_name] = MC_cat.TableData[Col_name]
        print('Found column "%s"!'%(Col_name))
    else:
        print('Error! Column "%s" was not found in the input catalog "%s"!'%(Col_name, Input_MC_cat_file))
        Col_check_OK = False
if not Col_check_OK:
    sys.exit()



# 
# print how many sources under analysis
print('')
print('Analyzing %d sources'%(len(S_in)))
print('')
# 
# compute median rms noise
noise_median = numpy.median(noise)
print('noise_median = %0.6e mJy'%(noise_median))
print('')
# 
# convolve beam
print('Computing source sizes convolved with beam')
Maj_in_convol, Min_in_convol, PA_in_convol = convolve_2D_Gaussian_Maj_Min_PA(Maj_in, Min_in, PA_in, Maj_beam, Min_beam, PA_beam)
Maj_out_convol, Min_out_convol, PA_out_convol = convolve_2D_Gaussian_Maj_Min_PA(Maj_out, Min_out, PA_out, Maj_beam, Min_beam, PA_beam)
print('minmax(Maj_beam) = %s, %s'%(numpy.min(Maj_beam),numpy.max(Maj_beam)))
print('minmax(Min_beam) = %s, %s'%(numpy.min(Min_beam),numpy.max(Min_beam)))
print('minmax(Maj_in) = %s, %s'%(numpy.min(Maj_in),numpy.max(Maj_in)))
print('minmax(Maj_out) = %s, %s'%(numpy.min(Maj_out),numpy.max(Maj_out)))
print('minmax(Maj_in_convol) = %s, %s'%(numpy.min(Maj_in_convol),numpy.max(Maj_in_convol)))
print('minmax(Maj_out_convol) = %s, %s'%(numpy.min(Maj_out_convol),numpy.max(Maj_out_convol)))
print('minmax(Min_in) = %s, %s'%(numpy.min(Min_in),numpy.max(Min_in)))
print('minmax(Min_out) = %s, %s'%(numpy.min(Min_out),numpy.max(Min_out)))
print('minmax(Min_in_convol) = %s, %s'%(numpy.min(Min_in_convol),numpy.max(Min_in_convol)))
print('minmax(Min_out_convol) = %s, %s'%(numpy.min(Min_out_convol),numpy.max(Min_out_convol)))
print('')
# 
# Prepare parameter grid cell
npar = 2
par1 = S_peak/noise
par1_str = 'S_{peak}/\\sigma_{rms noise}'
par1_grid = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0, 10., 20., 50., 100, 500, 1000.0]
if Simulation_Phys:
    par1_grid = [2.5, 5.0, 10., 100, 1000.0]
#<20180305>#par2 = Maj_out_convol/Maj_beam
par2 = numpy.sqrt((Maj_out_convol*Min_out_convol)/(Maj_beam*Min_beam))
par2_str = 'FWHM_{source}/FWHM_{beam}'
par2_grid = [1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00, +numpy.inf]
par2_max = 4.0
# 
# Prepare output directory name
if Output_dir != '':
    outdir = Output_dir
else:
    outdir = 'sim_diagram_output_no_galfit_flux_error'
if not os.path.isdir(outdir):
    os.makedirs(outdir)
if not os.path.isdir(outdir+os.sep+'dump'):
    os.makedirs(outdir+os.sep+'dump')
# 
# store uncorr0
S_out_uncorr0 = S_out
e_S_out_uncorr0 = e_S_out
# 
# prepare grid_cell_struct
grid_cell_struct = {}
grid_cell_struct['id'] = 0
grid_cell_struct['size'] = 0
grid_cell_struct['S_in-S_out'] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
grid_cell_struct['(S_in-S_out)/noise'] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
grid_cell_struct['(S_in-S_out)/S_in'] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
grid_cell_struct['(S_in-S_out)/e_S_out'] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
grid_cell_struct['e_S_out'] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
grid_cell_struct['noise'] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
for ipar in range(npar):
    grid_cell_struct['par%d'%(ipar+1)] = {'mean':numpy.nan, 'median':numpy.nan, 'scatter':numpy.nan, 'scatter_L68':numpy.nan, 'scatter_H68':numpy.nan}
## 
## prepare grid_cell_table
#grid_cell_table = []
# 
# compute cell_total_number
cell_total_number = 1
for ipar in range(npar):
    ipar_name = 'par%d_grid'%(ipar+1)
    if ipar_name in globals():
        ipar_grid = globals()[ipar_name]
        cell_total_number = cell_total_number * (len(ipar_grid)-1)
        ipar_message = 'param %d grid: '%(ipar+1) + '%s'%(ipar_grid)
        print(ipar_message)
    else:
        print('Error! Data array %s was not set! Please check your code and set proper parameters!'%(ipar_name))
        sys.exit()
print('cell_total_number = %d'%(cell_total_number))
print('')
## 
## generate cell_loop_table, which is a list of indices: (0,0,), (1,0,), (2,0,), ..., (9,0,), (0,1,), (1,1,), ...
#par1_mesh, par2_mesh = numpy.meshgrid(numpy.arange(len(par1_grid)), numpy.arange(len(par2_grid)))
# 
# prepare output arrays
all_cell_id = []
all_cell_size = []
all_cell_abs_mean = []
all_cell_abs_median = []
all_cell_abs_scatter = []
all_cell_abs_scatter_L68 = []
all_cell_abs_scatter_H68 = []
all_cell_noi_mean = []
all_cell_noi_median = []
all_cell_noi_scatter = []
all_cell_noi_scatter_L68 = []
all_cell_noi_scatter_H68 = []
all_cell_rel_mean = []
all_cell_rel_median = []
all_cell_rel_scatter = []
all_cell_rel_scatter_L68 = []
all_cell_rel_scatter_H68 = []
all_cell_norm_mean = []
all_cell_norm_median = []
all_cell_norm_scatter = []
all_cell_norm_scatter_L68 = []
all_cell_norm_scatter_H68 = []
all_cell_e_S_out_mean = []
all_cell_e_S_out_median = []
all_cell_rms_noise_mean = []
all_cell_rms_noise_median = []
all_cell_par1_mean = []
all_cell_par1_median = []
all_cell_par2_mean = []
all_cell_par2_median = []
# 
# loop grid cells
cell_loop_index = 0
for ipar in range(npar):
    globals()['par%d_loop'%(ipar+1)] = 0
# 
while cell_loop_index < cell_total_number:
    # 
    # select grid cell
    print('  selecting data points in param grid cell %d'%(cell_loop_index))
    for ipar in range(npar):
        parN = globals()['par%d'%(ipar+1)]
        parN_loop = globals()['par%d_loop'%(ipar+1)]
        parN_grid = globals()['par%d_grid'%(ipar+1)]
        if parN_loop >= len(parN_grid)-1:
            parN_loop = parN_loop - (len(parN_grid)-1)
            if 'par%d_loop'%(ipar+2) in globals():
                globals()['par%d_loop'%(ipar+2)] = globals()['par%d_loop'%(ipar+2)] + 1
            else:
                break
        # 
        # 
        parN_lower = parN_grid[parN_loop]
        parN_upper = parN_grid[parN_loop+1]
        # 
        if ipar == 0:
            select_by_param = (parN>=parN_lower) & (parN<=parN_upper)
        else:
            select_by_param = (select_by_param) & (parN>=parN_lower) & (parN<=parN_upper)
        print('  selecting param %d range %s %s'%(ipar+1, parN_lower, parN_upper))
        # 
        if ipar == 0:
            parN_loop = parN_loop + 1
        # 
        globals()['par%d_loop'%(ipar+1)] = parN_loop
    # 
    # select data points in the grid cell
    selected_args = numpy.argwhere(select_by_param).flatten()
    print('  selected %d data points in param grid cell %d'%(len(selected_args), cell_loop_index))
    print('')
    # 
    # compute statistics
    minimum_number_for_statistics = 25 # 5 before 2018-03-09, however, 5 can lead to overestimating the scatter.
    if len(selected_args) > minimum_number_for_statistics:
        grid_cell_struct['id'] = cell_loop_index
        grid_cell_struct['size'] = len(selected_args)
        grid_cell_struct['S_in-S_out']['mean'], \
        grid_cell_struct['S_in-S_out']['median'], \
        grid_cell_struct['S_in-S_out']['scatter'], \
        grid_cell_struct['S_in-S_out']['scatter_L68'], \
        grid_cell_struct['S_in-S_out']['scatter_H68'] = calc_asymmetric_scatters((S_in[selected_args]-S_out[selected_args]), log_file = outdir+os.sep+'dump'+os.sep+'log_calc_asymmetric_abs_scatter_cell_%d.txt'%(cell_loop_index))
        grid_cell_struct['(S_in-S_out)/noise']['mean'], \
        grid_cell_struct['(S_in-S_out)/noise']['median'], \
        grid_cell_struct['(S_in-S_out)/noise']['scatter'], \
        grid_cell_struct['(S_in-S_out)/noise']['scatter_L68'], \
        grid_cell_struct['(S_in-S_out)/noise']['scatter_H68'] = calc_asymmetric_scatters((S_in[selected_args]-S_out[selected_args])/noise[selected_args], log_file = outdir+os.sep+'dump'+os.sep+'log_calc_asymmetric_noi_scatter_cell_%d.txt'%(cell_loop_index))
        grid_cell_struct['(S_in-S_out)/S_in']['mean'], \
        grid_cell_struct['(S_in-S_out)/S_in']['median'], \
        grid_cell_struct['(S_in-S_out)/S_in']['scatter'], \
        grid_cell_struct['(S_in-S_out)/S_in']['scatter_L68'], \
        grid_cell_struct['(S_in-S_out)/S_in']['scatter_H68'] = calc_asymmetric_scatters((S_in[selected_args]-S_out[selected_args])/S_in[selected_args], clip_sigma=2.0, log_file = outdir+os.sep+'dump'+os.sep+'log_calc_asymmetric_rel_scatter_cell_%d.txt'%(cell_loop_index))
        grid_cell_struct['(S_in-S_out)/e_S_out']['mean'], \
        grid_cell_struct['(S_in-S_out)/e_S_out']['median'], \
        grid_cell_struct['(S_in-S_out)/e_S_out']['scatter'], \
        grid_cell_struct['(S_in-S_out)/e_S_out']['scatter_L68'], \
        grid_cell_struct['(S_in-S_out)/e_S_out']['scatter_H68'] = calc_asymmetric_scatters((S_in[selected_args]-S_out[selected_args])/e_S_out[selected_args], log_file = outdir+os.sep+'dump'+os.sep+'log_calc_asymmetric_norm_scatter_cell_%d.txt'%(cell_loop_index))
        grid_cell_struct['e_S_out']['mean'] = numpy.mean(e_S_out[selected_args])
        grid_cell_struct['e_S_out']['median'] = numpy.median(e_S_out[selected_args])
        grid_cell_struct['noise']['mean'] = numpy.mean(noise[selected_args])
        grid_cell_struct['noise']['median'] = numpy.median(noise[selected_args])
        for ipar in range(npar):
            parN = globals()['par%d'%(ipar+1)]
            grid_cell_struct['par%d'%(ipar+1)]['mean'] = numpy.mean(parN[selected_args])
            grid_cell_struct['par%d'%(ipar+1)]['median'] = numpy.median(parN[selected_args])
        # 
        # dump plot
        plot_engine = CrabPlot(figure_size=(5,5))
        plot_engine.set_figure_margin(left=0.2)
        plot_engine.plot_xy(S_peak[selected_args]/noise[selected_args], 
                            (S_in[selected_args]-S_out[selected_args]), 
                             symsize=0.3, xtitle='$S_{peak} / rms \ noise$', ytitle='$S_{in}-S_{out}$')
        plot_engine.plot_xy(grid_cell_struct['par1']['median'], 
                            grid_cell_struct['S_in-S_out']['median'], 
                            yerr=[ [ grid_cell_struct['S_in-S_out']['scatter_L68'] ], 
                                   [ grid_cell_struct['S_in-S_out']['scatter_H68'] ]
                                 ], 
                            capsize=3, 
                            symsize=2, symbol='open square', color='k', zorder=6, overplot=True)
        plot_engine.plot_line(0.0,0.0, 1000,0.0, overplot=True, color='k')
        plot_engine.savefig(outdir+os.sep+'dump'+os.sep+'dump_figure_abs_scatter_cell_%d.pdf'%(cell_loop_index))
        plot_engine.clear()
        # 
        # dump plot
        plot_engine = CrabPlot(figure_size=(5,5))
        plot_engine.set_figure_margin(left=0.2)
        plot_engine.plot_xy(S_peak[selected_args]/noise[selected_args], 
                            (S_in[selected_args]-S_out[selected_args])/(e_S_out[selected_args]), 
                             symsize=0.3, yrange=[-10,10], xtitle='$S_{peak} / rms \ noise$', ytitle='$(S_{in}-S_{out})/\sigma_{S_{out}}$')
        plot_engine.plot_xy(grid_cell_struct['par1']['median'], 
                            grid_cell_struct['(S_in-S_out)/e_S_out']['median'], 
                            yerr=[ [ grid_cell_struct['(S_in-S_out)/e_S_out']['scatter_L68'] ], 
                                   [ grid_cell_struct['(S_in-S_out)/e_S_out']['scatter_H68'] ]
                                 ], 
                            capsize=3, 
                            symsize=2, symbol='open square', color='k', zorder=6, overplot=True)
        plot_engine.plot_line(0.0,0.0, 1000,0.0, overplot=True, color='k')
        plot_engine.savefig(outdir+os.sep+'dump'+os.sep+'dump_figure_norm_scatter_cell_%d.pdf'%(cell_loop_index))
        plot_engine.clear()
        # 
        # dump plot
        plot_engine = CrabPlot(figure_size=(5,5))
        plot_engine.set_figure_margin(left=0.2)
        plot_engine.plot_xy(S_peak[selected_args]/noise[selected_args], 
                            (S_in[selected_args]-S_out[selected_args])/(S_in[selected_args]), 
                             symsize=0.3, yrange=[-10,1.5], xtitle='$S_{peak} / rms \ noise$', ytitle='$(S_{in}-S_{out})/S_{in}$')
        plot_engine.plot_xy(grid_cell_struct['par1']['median'], 
                            grid_cell_struct['(S_in-S_out)/S_in']['median'], 
                            yerr=[ [ grid_cell_struct['(S_in-S_out)/S_in']['scatter_L68'] ], 
                                   [ grid_cell_struct['(S_in-S_out)/S_in']['scatter_H68'] ]
                                 ], 
                            capsize=3, 
                            symsize=2, symbol='open square', color='k', zorder=6, overplot=True)
        plot_engine.plot_line(0.0,0.0, 1000,0.0, overplot=True, color='k')
        plot_engine.savefig(outdir+os.sep+'dump'+os.sep+'dump_figure_rel_scatter_cell_%d.pdf'%(cell_loop_index))
        plot_engine.clear()
        # 
        # dump plot
        plot_engine = CrabPlot(figure_size=(5,5))
        plot_engine.set_figure_margin(left=0.2)
        plot_engine.plot_xy(S_peak[selected_args]/noise[selected_args], 
                            (S_in[selected_args]-S_out[selected_args])/(noise[selected_args]), 
                             symsize=0.3, yrange=[-10,10], xtitle='$S_{peak} / rms \ noise$', ytitle='$(S_{in}-S_{out}) / rms \ noise$')
        plot_engine.plot_xy(grid_cell_struct['par1']['median'], 
                            grid_cell_struct['(S_in-S_out)/noise']['median'], 
                            yerr=[ [ grid_cell_struct['(S_in-S_out)/noise']['scatter_L68'] ], 
                                   [ grid_cell_struct['(S_in-S_out)/noise']['scatter_H68'] ]
                                 ], 
                            capsize=3, 
                            symsize=2, symbol='open square', color='k', zorder=6, overplot=True)
        plot_engine.plot_line(0.0,0.0, 1000,0.0, overplot=True, color='k')
        plot_engine.savefig(outdir+os.sep+'dump'+os.sep+'dump_figure_noi_scatter_cell_%d.pdf'%(cell_loop_index))
        plot_engine.clear()
        # 
        # dump text file
        j = json.dumps(grid_cell_struct, indent=4)
        f = open(outdir+os.sep+'dump'+os.sep+'dump_data_cell_%d.json'%(cell_loop_index), 'w')
        print(j,file=f)
        f.close()
        # 
        # append to output arrays
        all_cell_id.append(grid_cell_struct['id'])
        all_cell_size.append(grid_cell_struct['size'])
        all_cell_abs_mean.append(grid_cell_struct['S_in-S_out']['mean'])
        all_cell_abs_median.append(grid_cell_struct['S_in-S_out']['median'])
        all_cell_abs_scatter.append(grid_cell_struct['S_in-S_out']['scatter'])
        all_cell_abs_scatter_L68.append(grid_cell_struct['S_in-S_out']['scatter_L68'])
        all_cell_abs_scatter_H68.append(grid_cell_struct['S_in-S_out']['scatter_H68'])
        all_cell_noi_mean.append(grid_cell_struct['(S_in-S_out)/noise']['mean'])
        all_cell_noi_median.append(grid_cell_struct['(S_in-S_out)/noise']['median'])
        all_cell_noi_scatter.append(grid_cell_struct['(S_in-S_out)/noise']['scatter'])
        all_cell_noi_scatter_L68.append(grid_cell_struct['(S_in-S_out)/noise']['scatter_L68'])
        all_cell_noi_scatter_H68.append(grid_cell_struct['(S_in-S_out)/noise']['scatter_H68'])
        all_cell_rel_mean.append(grid_cell_struct['(S_in-S_out)/S_in']['mean'])
        all_cell_rel_median.append(grid_cell_struct['(S_in-S_out)/S_in']['median'])
        all_cell_rel_scatter.append(grid_cell_struct['(S_in-S_out)/S_in']['scatter'])
        all_cell_rel_scatter_L68.append(grid_cell_struct['(S_in-S_out)/S_in']['scatter_L68'])
        all_cell_rel_scatter_H68.append(grid_cell_struct['(S_in-S_out)/S_in']['scatter_H68'])
        all_cell_norm_mean.append(grid_cell_struct['(S_in-S_out)/e_S_out']['mean'])
        all_cell_norm_median.append(grid_cell_struct['(S_in-S_out)/e_S_out']['median'])
        all_cell_norm_scatter.append(grid_cell_struct['(S_in-S_out)/e_S_out']['scatter'])
        all_cell_norm_scatter_L68.append(grid_cell_struct['(S_in-S_out)/e_S_out']['scatter_L68'])
        all_cell_norm_scatter_H68.append(grid_cell_struct['(S_in-S_out)/e_S_out']['scatter_H68'])
        all_cell_e_S_out_mean.append(grid_cell_struct['e_S_out']['mean'])
        all_cell_e_S_out_median.append(grid_cell_struct['e_S_out']['median'])
        all_cell_rms_noise_mean.append(grid_cell_struct['noise']['mean'])
        all_cell_rms_noise_median.append(grid_cell_struct['noise']['median'])
        all_cell_par1_mean.append(grid_cell_struct['par1']['mean'])
        all_cell_par1_median.append(grid_cell_struct['par1']['median'])
        all_cell_par2_mean.append(grid_cell_struct['par2']['mean'])
        all_cell_par2_median.append(grid_cell_struct['par2']['median'])
        
        
    # 
    # 
    cell_loop_index = cell_loop_index + 1


# 
#fpout = open(outdir+os.sep+'datatable_param_grid_cell_statistics.txt', 'w')
#
#fpout.close()
outfile = outdir+os.sep+'datatable_param_grid_cell_statistics.txt'

asciitable.write( numpy.column_stack( 
                      ( all_cell_id, 
                        all_cell_size, 
                        all_cell_abs_mean, 
                        all_cell_abs_median, 
                        all_cell_abs_scatter, 
                        all_cell_abs_scatter_L68, 
                        all_cell_abs_scatter_H68, 
                        all_cell_noi_mean, 
                        all_cell_noi_median, 
                        all_cell_noi_scatter, 
                        all_cell_noi_scatter_L68, 
                        all_cell_noi_scatter_H68, 
                        all_cell_rel_mean, 
                        all_cell_rel_median, 
                        all_cell_rel_scatter, 
                        all_cell_rel_scatter_L68, 
                        all_cell_rel_scatter_H68, 
                        all_cell_norm_mean, 
                        all_cell_norm_median, 
                        all_cell_norm_scatter, 
                        all_cell_norm_scatter_L68, 
                        all_cell_norm_scatter_H68, 
                        all_cell_e_S_out_mean, 
                        all_cell_e_S_out_median, 
                        all_cell_rms_noise_mean, 
                        all_cell_rms_noise_median, 
                        all_cell_par1_mean, 
                        all_cell_par1_median,
                        all_cell_par2_mean, 
                        all_cell_par2_median )
                  ), 
                  outfile, 
                  Writer=asciitable.FixedWidthTwoLine,  
                  names = 
                      ( 'cell_id', 
                        'cell_size', 
                        'cell_abs_mean', 
                        'cell_abs_median', 
                        'cell_abs_scatter', 
                        'cell_abs_scatter_L68', 
                        'cell_abs_scatter_H68', 
                        'cell_noi_mean', 
                        'cell_noi_median', 
                        'cell_noi_scatter', 
                        'cell_noi_scatter_L68', 
                        'cell_noi_scatter_H68', 
                        'cell_rel_mean', 
                        'cell_rel_median', 
                        'cell_rel_scatter', 
                        'cell_rel_scatter_L68', 
                        'cell_rel_scatter_H68', 
                        'cell_norm_mean', 
                        'cell_norm_median', 
                        'cell_norm_scatter', 
                        'cell_norm_scatter_L68', 
                        'cell_norm_scatter_H68', 
                        'cell_e_S_out_mean', 
                        'cell_e_S_out_median', 
                        'cell_rms_noise_mean', 
                        'cell_rms_noise_median',
                        'cell_par1_mean', 
                        'cell_par1_median', 
                        'cell_par2_mean', 
                        'cell_par2_median' ), 
                  overwrite=True
                )


sys.exit()






























