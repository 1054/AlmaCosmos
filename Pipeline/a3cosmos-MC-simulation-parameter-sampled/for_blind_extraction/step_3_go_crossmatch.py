#!/usr/bin/env python
# 

import os, sys, re, platform, time
import numpy
import astropy
from astropy.io import fits
import astropy.io.ascii as asciitable
import multiprocessing


# pip install --user pidly pexpect # see -- http://www.bdnyc.org/2013/10/using-idl-within-python/
import pidly
if os.path.isfile('/Applications/exelis/idl/bin/idl'): 
    idl = pidly.IDL('/Applications/exelis/idl/bin/idl')
elif os.path.isfile('/usr/local2/bin/idl'): 
    idl = pidly.IDL('/usr/local2/bin/idl')
elif os.path.isfile('/usr/local/bin/idl'): 
    idl = pidly.IDL('/usr/local/bin/idl')
else:
    print('Error! Could not find IDL (Interative Data Language)!')
    sys.exit()


# 
# Warning message
# 
print('This code should be ran on aida42198 machine and under "/disk1/ALMA_COSMOS/A3COSMOS/simulations/" directory.')
print("It also needs IDL.")

if not os.path.isdir('models'):
    print('Error! "models" was not found under current directory!')
    sys.exit()

if not os.path.isdir('output_PyBDSM'):
    print('Error! "output_PyBDSM" was not found under current directory!')
    sys.exit()


# 
# Read source_list
# 
alma_image_list = []
with open('output_PyBDSM/list_for_pyBDSM.txt','r') as fp:
    input_list_lines = fp.readlines()
    for lp in input_list_lines:
        if not lp.startswith('#'):
            input_list_items = lp.strip().split()
            input_one_item = input_list_items[len(input_list_items)-1]
            if input_one_item!='2011.0.00064.S_SB1_GB1_MB1_AzTEC-3' and \
               input_one_item!='2011.0.00064.S_SB1_GB1_MB1_AzTEC-3' :
                alma_image_list.append(input_one_item)

print('Listing %d ALMA images'%(len(alma_image_list)))
print(alma_image_list)
#sys.exit()


# # 
# # Define an output queue for parallal
# # 
# output = multiprocessing.Queue()


# 
# Prepare simulated and recovered dir
# The simulated_dir should contain those simulation files from Philipp
# And the recovered_dir should contain those recovered files with PyBDSM
# 
#for alma_image_name in alma_image_list:
def read_MC_sim_recovery(alma_image_name, output=None):
    #simulated_dir = 'input_fits_files/2015.1.01495.S_SB1_GB1_MB1_COSMOS-16199'
    #recovered_dir = 'caap_blind_extraction_photometry_pybdsf'
    simulated_dir = 'models' + os.sep + alma_image_name
    recovered_dir = 'output_PyBDSM' + os.sep + alma_image_name
    if os.path.isfile('statistics_PyBDSM/done_output_sim_data_table_%s'%(alma_image_name)):
        print('# %s (already done, skip!)'%(alma_image_name))
        #output.put('# %s (already done, skip!)'%(alma_image_name))
        return
    else:
        print('# %s'%(alma_image_name))
        #output.put('# %s'%(alma_image_name))
    
    recovered_list_of_catalog = recovered_dir + os.sep + 'output_list_of_catalog.txt'
    if not os.path.isdir(simulated_dir):
        print('Error! The simulated directory "%s" was not found!'%(simulated_dir))
        #output.put('Error! The simulated directory "%s" was not found!'%(simulated_dir))
        return
    if not os.path.isdir(recovered_dir):
        print('Error! The recovered directory "%s" was not found!'%(recovered_dir))
        #output.put('Error! The recovered directory "%s" was not found!'%(recovered_dir))
        return
    if not os.path.isfile(recovered_list_of_catalog):
        print('Error! The recovered list of catalog "%s" was not found!'%(recovered_list_of_catalog))
        #output.put('Error! The recovered list of catalog "%s" was not found!'%(recovered_list_of_catalog))
        return
    
    # Prepare output data table
    has_print_header = False
    has_print_lines = 0
    output_data_table = 'statistics_PyBDSM/output_sim_data_table_%s.txt'%(alma_image_name)
    if not os.path.isdir(os.path.dirname(output_data_table)):
        os.makedirs(os.path.dirname(output_data_table))
    ofs = open(output_data_table, 'w')
    
    # Ready to read galfit output fits file
    with open(recovered_list_of_catalog) as fp:
        input_list_files = fp.readlines()
        #<DEBUG># input_list_files = input_list_files[214:216]
        for lp in input_list_files:
            input_fits_file = lp.strip()
            input_fits_name = os.path.basename(os.path.dirname(input_fits_file))
            input_fits_base = input_fits_name.replace('.fits.gz','').replace('.fits','')
            sim_param_file = simulated_dir + os.sep + input_fits_base.replace('_model','_info.save')
            rec_catalog_file = recovered_dir + os.sep + input_fits_base + os.sep + 'pybdsm_cat.fits'
            # 
            # read simulated parameter file
            if not os.path.isfile(sim_param_file):
                print('Error! The simulation parameter file "%s" was not found!'%(sim_param_file))
                #output.put('Error! The simulation parameter file "%s" was not found!'%(sim_param_file))
                return
            idl('restore, "%s", verbose = false'%(sim_param_file))
            sim_x = idl.CENX
            sim_y = idl.CENY
            sim_pixsc = idl.PIXSCL * 3600.0 # arcsec
            #sim_Maj = idl.SOURCE_SIZE * idl.BEAMSIZE_PIX * sim_pixsc # arcsec #<20171229><BUG># SOURCE_SIZE = sim_Size * BEAMSIZE_PIX
            sim_Maj = idl.SOURCE_SIZE * sim_pixsc # arcsec #<20171229><BUG># SOURCE_SIZE = sim_Size * BEAMSIZE_PIX
            sim_Min = sim_Maj * idl.AR # arcsec
            sim_PA = idl.PA # degree
            sim_fpeak = idl.PEAK_FLUX # Jy/beam
            sim_f = idl.TOTAL_FLUX # Jy
            sim_beam_maj = idl.BEAMSIZE_PIX * sim_pixsc # arcsec
            sim_beam_min = idl.BEAMSIZE_MINOR_PIX * sim_pixsc # arcsec
            sim_beam_pa = idl.BEAMPA # degree
            sim_str_split = re.findall('Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*', input_fits_base)
            sim_image_name = input_fits_base
            sim_image_dir = os.path.basename(simulated_dir)
            if sim_str_split:
                if len(sim_str_split[0]) >= 3:
                    sim_Size = float(sim_str_split[0][0])
                    sim_SNR_peak = float(sim_str_split[0][1])
                    sim_id = long(sim_str_split[0][2])
                    sim_rms = sim_fpeak / sim_SNR_peak
                else:
                    print('Error! Failed to run \"re.findall(\'Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*\', input_fits_base)\"!')
                    #output.put('Error! Failed to run \"re.findall(\'Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*\', input_fits_base)\"!')
                    return
            else:
                print('Error! Failed to run \"re.findall(\'Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*\', input_fits_base)\"!')
                #output.put('Error! Failed to run \"re.findall(\'Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*\', input_fits_base)\"!')
                return
            # 
            # prepare recovered variables
            rec_x = -99
            rec_y = -99
            rec_f = -99
            rec_df = -99
            rec_fpeak = -99
            rec_dfpeak = -99
            rec_Maj = -99
            rec_Min = -99
            rec_PA = -99
            rec_Maj_convol = -99
            rec_Min_convol = -99
            rec_PA_convol = -99
            rec_S_Code = -99
            # 
            # prepare spurious variables
            spurious_x = []
            spurious_y = []
            spurious_f = []
            spurious_df = []
            spurious_fpeak = []
            spurious_dfpeak = []
            spurious_Maj = []
            spurious_Min = []
            spurious_PA = []
            spurious_Maj_convol = []
            spurious_Min_convol = []
            spurious_PA_convol = []
            spurious_S_Code = []
            spurious_index = []
            # 
            # read recovered catalog file
            if os.path.isfile(rec_catalog_file):
                #print(rec_catalog_file)
                recovered_catalog_fits = fits.open(rec_catalog_file)
                #print(recovered_catalog_fits[0].header)
                recovered_catalog_header = recovered_catalog_fits[1].columns
                recovered_catalog_table = recovered_catalog_fits[1].data
                #print(recovered_catalog_header)
                #print(recovered_catalog_table)
                rec_x = recovered_catalog_table['Xposn']
                rec_y = recovered_catalog_table['Yposn']
                rec_dx = recovered_catalog_table['E_Xposn']
                rec_dy = recovered_catalog_table['E_Yposn']
                rec_f = recovered_catalog_table['Total_flux'] # Jy
                rec_df = recovered_catalog_table['E_Total_flux'] # Jy
                rec_fpeak = recovered_catalog_table['Peak_flux'] # Jy/beam
                rec_dfpeak = recovered_catalog_table['E_Peak_flux'] # Jy/beam
                rec_Maj = recovered_catalog_table['DC_Maj'] * 3600.0 # arcsec
                rec_dMaj = recovered_catalog_table['E_DC_Maj'] * 3600.0 # arcsec
                rec_Min = recovered_catalog_table['DC_Min'] * 3600.0 # arcsec
                rec_dMin = recovered_catalog_table['E_DC_Min'] * 3600.0 # arcsec
                rec_PA = recovered_catalog_table['DC_PA']
                rec_dPA = recovered_catalog_table['E_DC_PA']
                rec_Maj_convol = recovered_catalog_table['Maj'] * 3600.0 # arcsec
                rec_dMaj_convol = recovered_catalog_table['E_Maj'] * 3600.0 # arcsec
                rec_Min_convol = recovered_catalog_table['Min'] * 3600.0 # arcsec
                rec_dMin_convol = recovered_catalog_table['E_Min'] * 3600.0 # arcsec
                rec_PA_convol = recovered_catalog_table['PA']
                rec_dPA_convol = recovered_catalog_table['E_PA']
                rec_S_Code = recovered_catalog_table['S_Code']
                rec_xydis = numpy.sqrt((rec_x - sim_x)**2 + (rec_y - sim_y)**2)
                lim_arcsec = 1.5 # arcsec #<TODO># 
                lim_xydis = numpy.sqrt(rec_dx**2+rec_dy**2+(lim_arcsec/sim_pixsc)**2)
                #<DEBUG># for iii in range(len(lim_xydis)):
                #<DEBUG>#     print('rec_xy = %g %g, sim_x = %g %g'%(rec_x[iii], rec_y[iii], sim_x, sim_y))
                #<DEBUG>#     print('rec_xydis = %g, lim_xydis = %g'%(rec_xydis[iii], lim_xydis[iii]))
                # 
                # choose the brightest one within lim_xydis
                #rec_index = numpy.argwhere(rec_xydis<lim_xydis) # select the brightest recovered source that are within 2.0 arcsec radius of the simulated source as the right counterparat!
                # 
                # choose the cloest one (20171206: as Philipp suggested)
                rec_index = [numpy.argmin(rec_xydis)]
                if rec_xydis[rec_index[0]] > lim_xydis[rec_index[0]]:
                    rec_index = []
                # 
                # spurious
                if len(rec_index) > 1:
                    spurious_index = range(len(rec_xydis))
                    spurious_index.remove(rec_index[0])
                # 
                # close
                recovered_catalog_fits.close()
                #print(sim_pixsc)
                #print(rec_index)
                # 
                # spurious
                if len(spurious_index) > 0:
                    spurious_x = rec_x[spurious_index]
                    spurious_y = rec_y[spurious_index]
                    spurious_f = rec_f[spurious_index]
                    spurious_df = rec_df[spurious_index]
                    spurious_fpeak = rec_fpeak[spurious_index]
                    spurious_dfpeak = rec_dfpeak[spurious_index]
                    spurious_Maj = rec_Maj[spurious_index]
                    spurious_Min = rec_Min[spurious_index]
                    spurious_PA = rec_PA[spurious_index]
                    spurious_Maj_convol = rec_Maj_convol[spurious_index]
                    spurious_Min_convol = rec_Min_convol[spurious_index]
                    spurious_PA_convol = rec_PA_convol[spurious_index]
                    spurious_S_Code = rec_S_Code[spurious_index]
                # 
                # matched
                if len(rec_index) <= 0:
                    # no reasonably recovered source
                    #print('Warning! No recovered source was found within %.2f arcsec or %.3f pixel of the simulated source!'%(lim_arcsec, lim_xydis))
                    rec_x = -99
                    rec_y = -99
                    rec_f = -99
                    rec_df = -99
                    rec_fpeak = -99
                    rec_dfpeak = -99
                    rec_Maj = -99
                    rec_Min = -99
                    rec_PA = -99
                    rec_Maj_convol = -99
                    rec_Min_convol = -99
                    rec_PA_convol = -99
                    rec_S_Code = -99
                else:
                    rec_x = rec_x[rec_index[0]]
                    rec_y = rec_y[rec_index[0]]
                    rec_f = rec_f[rec_index[0]]
                    rec_df = rec_df[rec_index[0]]
                    rec_fpeak = rec_fpeak[rec_index[0]]
                    rec_dfpeak = rec_dfpeak[rec_index[0]]
                    rec_Maj = rec_Maj[rec_index[0]]
                    rec_Min = rec_Min[rec_index[0]]
                    rec_PA = rec_PA[rec_index[0]]
                    rec_Maj_convol = rec_Maj_convol[rec_index[0]]
                    rec_Min_convol = rec_Min_convol[rec_index[0]]
                    rec_PA_convol = rec_PA_convol[rec_index[0]]
                    rec_S_Code = rec_S_Code[rec_index[0]]
                    #spurious_index.remove(rec_index[0])
                #break
            # 
            # print header
            if not has_print_header:
                print('# %10s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s'%('sim_id', 'sim_Size', 'sim_SNR_peak', 'sim_rms', 'sim_pixsc', 'sim_f', 'sim_fpeak', 'sim_Maj', 'sim_Min', 'rec_f', 'rec_df', 'rec_fpeak', 'rec_dfpeak'))
                ofs.write('# %10s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %33s %50s %13s %13s %13s %13s %13s %13s %13s %13s %13s %16s %16s %16s %13s\n'%('sim_id', 'sim_Size', 'sim_SNR_peak', 'sim_rms', 'sim_pixsc', 'sim_beam_maj', 'sim_beam_min', 'sim_beam_pa', 'sim_x', 'sim_y', 'sim_f', 'sim_fpeak', 'sim_Maj', 'sim_Min', 'sim_PA', 'sim_image_name', 'sim_image_dir', 'rec_x', 'rec_y', 'rec_f', 'rec_df', 'rec_fpeak', 'rec_dfpeak', 'rec_Maj', 'rec_Min', 'rec_PA', 'rec_Maj_convol', 'rec_Min_convol', 'rec_PA_convol', 'rec_S_Code'))
                has_print_header = True
            # 
            # print matched source
            print('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g'%(sim_id, sim_Size, sim_SNR_peak, sim_rms, sim_pixsc, sim_f, sim_fpeak, sim_Maj, sim_Min, rec_f, rec_df, rec_fpeak, rec_dfpeak))
            ofs.write('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %33s %50s %13g %13g %13g %13g %13g %13g %13g %13g %13g %16g %16g %16g %13s\n'%(sim_id, sim_Size, sim_SNR_peak, sim_rms, sim_pixsc, sim_beam_maj, sim_beam_min, sim_beam_pa, sim_x, sim_y, sim_f, sim_fpeak, sim_Maj, sim_Min, sim_PA, sim_image_name, sim_image_dir, rec_x, rec_y, rec_f, rec_df, rec_fpeak, rec_dfpeak, rec_Maj, rec_Min, rec_PA, rec_Maj_convol, rec_Min_convol, rec_PA_convol, rec_S_Code))
            has_print_lines = has_print_lines + 1
            # 
            # print spurious sources
            if len(spurious_index) > 0:
                for spurious_i in range(spurious_index):
                    print('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g'%(-99, -99, -99, sim_rms, sim_pixsc, -99, -99, -99, -99, spurious_f[spurious_i], spurious_df[spurious_i], spurious_fpeak[spurious_i], spurious_dfpeak[spurious_i]))
                    ofs.write('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %33s %50s %13g %13g %13g %13g %13g %13g %13g %13g %13g %16g %16g %16g %13s\n'%(-99, -99, -99, sim_rms, sim_pixsc, sim_beam_maj, sim_beam_min, sim_beam_pa, -99, -99, -99, -99, -99, -99, -99, sim_image_name, sim_image_dir, spurious_x[spurious_i], spurious_y[spurious_i], spurious_f[spurious_i], spurious_df[spurious_i], spurious_fpeak[spurious_i], spurious_dfpeak[spurious_i], spurious_Maj[spurious_i], spurious_Min[spurious_i], spurious_PA[spurious_i], spurious_Maj_convol[spurious_i], spurious_Min_convol[spurious_i], spurious_PA_convol[spurious_i], spurious_S_Code[spurious_i]))
                    has_print_lines = has_print_lines + 1  
            # 
            # 
            #if has_print_lines > 100:
            #    break
        
    # 
    # 
    # Till now, we have got the sim_data_file, which contains a list of input and output fluxes.
    # 
    # 
    ofs.close()
    os.system('date +"%%Y-%%m-%%d %%H:%%M:%%S %%Z" > %s'%('statistics_PyBDSM/done_output_sim_data_table_%s'%(alma_image_name)))



# 
# Parallize Python not working because of the calling of IDL
# 
# 
# # 
# # Parallize
# # 
# processes = []
# for i in range(len(alma_image_list)):
#     processes.append( \
#         multiprocessing.Process(target=read_MC_sim_recovery, args=(alma_image_list[i], output))
#     )
# 
# 
# # 
# # Run processes
# # 
# lim_processes = 2
# for p in processes:
#     p.start()
#     print(p)
#     time.sleep(3.0)
#     print(len(multiprocessing.active_children()))
#     while len(multiprocessing.active_children())>lim_processes:
#         time.sleep(30.0)
# 
# 
# # 
# # Exit the completed processes
# # 
# for p in processes:
#     p.join()
# 
# 
# # 
# # Get process results from the output queue
# # 
# results = [output.get() for p in processes]
# 
# #print(results)
# print('All done!')





# 
# Run the function
# 
processes = [] # 'processes' contains the number of alma image, e.g., 0, 1, 2, 3, ..., len(alma_image_list)-1. Can read from input, but input number starts from 1 to len(alma_image_list). 
if len(sys.argv)>1:
    i=1
    while i<len(sys.argv):
        if(int(sys.argv[i])<=len(alma_image_list)):
            processes.append(int(sys.argv[i])-1)
        i=i+1
else:
    processes = range(len(alma_image_list))
    print('Running processes %d to %d'%(1,max(processes)))

if len(processes) > 0:
    for i in range(len(processes)):
        read_MC_sim_recovery(alma_image_list[processes[i]])








