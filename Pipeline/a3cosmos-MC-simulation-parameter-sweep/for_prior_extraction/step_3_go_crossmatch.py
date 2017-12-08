#!/usr/bin/env python
# 

import os, sys, re, platform, glob
import numpy
import astropy
from astropy.io import fits
import astropy.io.ascii as asciitable

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
print("This code should be ran on aida42198 machine and under \"/disk1/ALMA_COSMOS/A3COSMOS/simulations/\" directory.")
print("It also needs IDL, Supermongo and astroGalfit.sm macros, and \"github.com/1054/AlmaCosmos\" tools. Please ask liudz1054@gmail.com if you don't have them. ")

if not os.path.isdir('models'):
    print('Error! "models" was not found under current directory!')
    sys.exit()

if not os.path.isdir('output_GALFIT'):
    print('Error! "output_GALFIT" was not found under current directory!')
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

print(alma_image_list)
#sys.exit()


# 
# Prepare simulated and recovered dir
# The simulated_dir should contain those simulation files from Philipp
# And the recovered_dir should contain those recovered files with PyBDSM
# 
for alma_image_name in alma_image_list:
    #simulated_dir = 'input_fits_files/2015.1.01495.S_SB1_GB1_MB1_COSMOS-16199'
    #recovered_dir = 'caap_blind_extraction_photometry_pybdsf'
    simulated_dir = 'models' + os.sep + alma_image_name
    recovered_dir = 'output_GALFIT' + os.sep + alma_image_name
    if os.path.isfile('statistics_GALFIT/done_output_sim_data_table_%s'%(alma_image_name)):
        print('# %s (already done, skip!)'%(alma_image_name))
        continue
    else:
        print('# %s'%(alma_image_name))
    
    # DEBUG
    if alma_image_name != '2015.1.01495.S_SB1_GB1_MB1_COSMOS-16199':
        continue
    
    # Get simulated list
    simulated_list = []
    with open('models' + os.sep + alma_image_name + '_imlist.txt', 'r') as fp:
        input_list_lines = fp.readlines()
        for lp in input_list_lines:
            if not lp.startswith('#'):
                simulated_list.append(os.path.basename(lp.strip()).replace('.fits.gz',''))
    
    # Search for galfit output fits files
    recovered_galfit_fits_file_pattern = recovered_dir + os.sep + '*_freecen.fits'
    recovered_galfit_fits_files = glob.glob(recovered_dir + os.sep + '*_freecen.fits')
    
    if not os.path.isdir(simulated_dir):
        print('Error! The simulated directory "%s" was not found!'%(simulated_dir))
        sys.exit()
    if not os.path.isdir(recovered_dir):
        print('Error! The recovered directory "%s" was not found!'%(recovered_dir))
        sys.exit()
    if len(recovered_galfit_fits_files) == 0:
        print('Error! The recovered list of galfit fits files "%s" was not found!'%(recovered_galfit_fits_file_pattern))
        sys.exit()
    
    # Prepare output data table
    has_print_header = False
    has_print_lines = 0
    output_data_table = 'statistics_GALFIT/output_sim_data_table_%s.txt'%(alma_image_name)
    if not os.path.isdir(os.path.dirname(output_data_table)):
        os.makedirs(os.path.dirname(output_data_table))
    ofs = open(output_data_table, 'w')
    
    # Ready to read galfit output fits file
    for simulated_name in simulated_list:
        if True:
            sim_image_file = simulated_dir + os.sep + simulated_name + '.fits.gz'
            sim_param_file = simulated_dir + os.sep + simulated_name.replace('_model','_info.save')
            rec_galfit_file = recovered_dir + os.sep + simulated_name.replace('_model','_freecen.fits')
            # 
            # read simulated parameter file
            if not os.path.isfile(sim_param_file):
                #continue #<DEBUG>#
                print('Error! The simulation parameter file "%s" was not found!'%(sim_param_file))
                sys.exit()
            idl('restore, "%s", verbose = false'%(sim_param_file))
            sim_x = idl.CENX
            sim_y = idl.CENY
            sim_pixsc = idl.PIXSCL * 3600.0 # arcsec
            sim_Maj = idl.SOURCE_SIZE * idl.BEAMSIZE_PIX * sim_pixsc # arcsec
            sim_Min = sim_Maj * idl.AR # arcsec
            sim_PA = idl.PA # degree
            sim_fpeak = idl.PEAK_FLUX # Jy/beam
            sim_f = idl.TOTAL_FLUX # Jy
            sim_beam_maj = idl.BEAMSIZE_PIX * sim_pixsc # arcsec
            sim_beam_min = idl.BEAMSIZE_MINOR_PIX * sim_pixsc # arcsec
            sim_beam_pa = idl.BEAMPA # degree
            sim_str_split = re.findall('Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*', simulated_name)
            sim_image_name = simulated_name
            sim_image_dir = os.path.basename(simulated_dir)
            if sim_str_split:
                if len(sim_str_split[0]) >= 3:
                    sim_Size = float(sim_str_split[0][0])
                    sim_SNR_peak = float(sim_str_split[0][1])
                    sim_id = int(sim_str_split[0][2])
                    sim_rms = sim_fpeak / sim_SNR_peak
                else:
                    print('Error! Failed to run \"re.findall(\'Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*\', simulated_name)\"!')
                    sys.exit()
            else:
                print('Error! Failed to run \"re.findall(\'Size([0-9.]+)_SN([0-9.]+)_number([0-9]+)_.*\', simulated_name)\"!')
                sys.exit()
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
            spurious_S_Code = []
            spurious_index = []
            # 
            # read recovered catalog file
            if os.path.isfile(rec_galfit_file):
                # 
                # read galfit fits file with Supermongo and astroGalfit.sm macro
                temp_dir = 'temp_dzliu_read_galfit_output'
                if not os.path.isdir(temp_dir):
                    os.makedirs(temp_dir)
                if os.path.isfile(temp_dir+os.sep+'out.txt'):
                    os.system('rm -rf %s/*'%(temp_dir))
                os.system('gunzip -c "%s" > %s/image_sci.fits'%(sim_image_file, temp_dir))
                os.system('cp "%s" %s/temp.fits'%(rec_galfit_file, temp_dir))
                #os.system('gethead "%s/image_sci.fits" "BUNIT" > "%s/image_sci_fluxunit.txt"'%(temp_dir, temp_dir))
                #os.system('gethead "%s/image_sci.fits" "BMAJ" "BMIN" "BPA" > "%s/image_sci_beam.txt"'%(temp_dir, temp_dir))
                #os.system('pixscale "%s/image_sci.fits" > "%s/image_sci_pixscale.txt"'%(temp_dir, temp_dir))
                os.system('echo "%s" > "%s/image_sci_fluxunit.txt"'%('Jy/beam', temp_dir))
                os.system('echo "%0.15e" "%0.15e" "%0.15f" > "%s/image_sci_beam.txt"'%(sim_beam_maj/3600.0, sim_beam_min/3600.0, sim_beam_pa, temp_dir))
                os.system('echo "%0.15f" > "%s/image_sci_pixscale.txt"'%(sim_pixsc, temp_dir))
                os.system('echo "#!/bin/bash" > %s/temp.bash'%(temp_dir))
                os.system('echo "source $HOME/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash" >> %s/temp.bash'%(temp_dir))
                os.system('echo "echo \\\"macro read temp.sm go\\\" | sm" >> %s/temp.bash'%(temp_dir))
                os.system('echo "go" > %s/temp.sm'%(temp_dir))
                os.system('echo "    load astroGalfit.sm" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    readGalfitResult temp.fits" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                os.system('echo "    data image_sci_fluxunit.txt read fluxunit 1.s" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    data image_sci_beam.txt read {beam_maj 1.f beam_min 2.f}" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    data image_sci_pixscale.txt read pixscale 1.f" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set beam_maj = beam_maj * 3600.0 # arcsec" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set beam_min = beam_min * 3600.0 # arcsec" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set beamarea = pi/(4*ln(2))*beam_maj*beam_min # arcsec-square" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set fluxconv = ResultMags*0.0 + 1.0 / (beamarea/(pixscale*pixscale)) # assuming Jy/beam" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set Total_flux = 10**(ResultMags/(-2.5)) * fluxconv" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set Total_flux = 10**(ResultMags/(-2.5))" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set E_Total_flux = ResultMagsErr>0 ? ResultMagsErr*Total_flux/1.08 : ResultMagsErr" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set maj = ResultRads * 2 * pixscale # arcsec, converted Sersic effective radius -> FWHM" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set min = maj * ResultElli # arcsec" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set convol_maj = sqrt(beam_maj**2 + maj**2) # arcsec" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set convol_min = sqrt(beam_min**2 + min**2) # arcsec" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set convol_area_in_beam = (convol_maj*convol_min) / (beam_maj*beam_min)" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set Peak_flux = Total_flux * fluxconv / convol_area_in_beam #<BUG><CORRECTED><20171123># dzliu, Yoshinobu, Philipp" >> %s/temp.sm'%(temp_dir)) # from '/Users/dzliu/Cloud/Github/DeepFields.SuperDeblending/Softwares/astrodepth_prior_extraction_photometry_go_galfit.sm'
                os.system('echo "    set E_Peak_flux = Total_flux*0.0 + %s # just rms" >> %s/temp.sm'%(sim_rms, temp_dir)) # from '/Users/dzliu/Cloud/Github/DeepFields.SuperDeblending/Softwares/astrodepth_prior_extraction_photometry_go_galfit.sm'
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set Maj = maj / 3600.0 # degree" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set E_Maj = (ResultRadsErr>0) ? ResultRadsErr/ResultRads * maj : ResultRadsErr" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set Min = min / 3600.0 # degree" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set E_Min = (ResultElliErr>0) ? ResultElliErr/ResultElli * min : ResultElliErr" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set PA = ResultRoti" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set E_PA = (ResultRotiErr>0) ? ResultRotiErr/ResultRoti * min : ResultRotiErr" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                os.system('echo "    load wfile.sm" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set wfile_vectors = {ResultType ResultPosX ResultPosXErr ResultPosY ResultPosYErr Total_flux E_Total_flux Peak_flux E_Peak_flux Maj E_Maj Min E_Min PA E_PA fluxconv}" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set wfile_vectors = wfile_vectors concat {ResultMags ResultMagsErr ResultRads ResultRadsErr ResultSers ResultSersErr ResultElli ResultElliErr ResultRoti ResultRotiErr}" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    set wfile_fmt_ResultType = \'%%13s\'" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    wfile out.txt" >> %s/temp.sm'%(temp_dir))
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                os.system('echo "    " >> %s/temp.sm'%(temp_dir))
                print('# Running %s/temp.bash'%(temp_dir))
                os.system('chmod +x %s/temp.bash; cd %s; ./temp.bash > temp.log'%(temp_dir, temp_dir))
                print('# Finished %s/temp.bash'%(temp_dir))
                # 
                if not os.path.isfile(temp_dir+os.sep+'out.txt'):
                    print('Error! Failed to read the galfit output fits file "%s" with Supermongo and astroGalfit.sm macros!'%(rec_galfit_file))
                    print('Please check temporary directory "%s"/'%(temp_dir))
                    sys.exit()
                # 
                recovered_catalog_table = asciitable.read(temp_dir+os.sep+'out.txt')
                # 
                rec_x = recovered_catalog_table['ResultPosX']
                rec_y = recovered_catalog_table['ResultPosX']
                rec_dx = recovered_catalog_table['ResultPosXErr']
                rec_dy = recovered_catalog_table['ResultPosYErr']
                rec_f = recovered_catalog_table['Total_flux'] # Jy
                rec_df = recovered_catalog_table['E_Total_flux'] # Jy
                rec_fpeak = recovered_catalog_table['Peak_flux'] # Jy/beam
                rec_dfpeak = recovered_catalog_table['E_Peak_flux'] # Jy/beam
                rec_Maj = recovered_catalog_table['Maj'] * 3600.0 # arcsec
                rec_dMaj = recovered_catalog_table['E_Maj'] * 3600.0 # arcsec
                rec_Min = recovered_catalog_table['Min'] * 3600.0 # arcsec
                rec_dMin = recovered_catalog_table['E_Min'] * 3600.0 # arcsec
                rec_PA = recovered_catalog_table['PA']
                rec_dPA = recovered_catalog_table['E_PA']
                rec_S_Code = recovered_catalog_table['fluxconv']
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
                if rec_xydis[rec_index[0]] > lim_xydis:
                    rec_index = []
                # 
                # spurious
                if len(rec_index) > 1:
                    spurious_index = range(len(rec_xydis))
                    spurious_index.remove(rec_index[0])
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
                    rec_S_Code = rec_S_Code[rec_index[0]]
                    #spurious_index.remove(rec_index[0])
                #break
            # 
            # print header
            if not has_print_header:
                #print('%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s'%('sim_id', 'sim_Size', 'sim_SNR_peak', 'sim_rms', 'sim_pixsc', 'sim_f', 'sim_fpeak', 'sim_Maj', 'sim_Min', 'sim_beam_maj', 'sim_beam_min', 'sim_beam_pa'))
                print('# %10s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s'%('sim_id', 'sim_Size', 'sim_SNR_peak', 'sim_rms', 'sim_pixsc', 'sim_f', 'sim_fpeak', 'sim_Maj', 'sim_Min', 'rec_f', 'rec_df', 'rec_fpeak', 'rec_dfpeak'))
                ofs.write('# %10s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s %33s %50s %13s %13s %13s %13s %13s %13s %13s %13s %13s %13s\n'%('sim_id', 'sim_Size', 'sim_SNR_peak', 'sim_rms', 'sim_pixsc', 'sim_beam_maj', 'sim_beam_min', 'sim_beam_pa', 'sim_x', 'sim_y', 'sim_f', 'sim_fpeak', 'sim_Maj', 'sim_Min', 'sim_PA', 'sim_image_name', 'sim_image_dir', 'rec_x', 'rec_y', 'rec_f', 'rec_df', 'rec_fpeak', 'rec_dfpeak', 'rec_Maj', 'rec_Min', 'rec_PA', 'rec_S_Code'))
                has_print_header = True
            # 
            # print matched source
            #print('%15d %15g %15g %15g %15g %15g %15g %15g %15g %15g %15g %15g'%(sim_id, sim_Size, sim_SNR_peak, sim_rms, sim_pixsc, sim_f, sim_fpeak, sim_Maj, sim_Min, sim_beam_maj, sim_beam_min, sim_beam_pa))
            print('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g'%(sim_id, sim_Size, sim_SNR_peak, sim_rms, sim_pixsc, sim_f, sim_fpeak, sim_Maj, sim_Min, rec_f, rec_df, rec_fpeak, rec_dfpeak))
            ofs.write('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %33s %50s %13g %13g %13g %13g %13g %13g %13g %13g %13g %13s\n'%(sim_id, sim_Size, sim_SNR_peak, sim_rms, sim_pixsc, sim_beam_maj, sim_beam_min, sim_beam_pa, sim_x, sim_y, sim_f, sim_fpeak, sim_Maj, sim_Min, sim_PA, sim_image_name, sim_image_dir, rec_x, rec_y, rec_f, rec_df, rec_fpeak, rec_dfpeak, rec_Maj, rec_Min, rec_PA, rec_S_Code))
            has_print_lines = has_print_lines + 1
            # 
            # print spurious sources
            if len(spurious_index) > 0:
                for spurious_i in range(spurious_index):
                    print('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g'%(-99, -99, -99, sim_rms, sim_pixsc, -99, -99, -99, -99, spurious_f[spurious_i], spurious_df[spurious_i], spurious_fpeak[spurious_i], spurious_dfpeak[spurious_i]))
                    ofs.write('%12d %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %13g %33s %50s %13g %13g %13g %13g %13g %13g %13g %13g %13g %13s\n'%(-99, -99, -99, sim_rms, sim_pixsc, sim_beam_maj, sim_beam_min, sim_beam_pa, -99, -99, -99, -99, -99, -99, -99, sim_image_name, sim_image_dir, spurious_x[spurious_i], spurious_y[spurious_i], spurious_f[spurious_i], spurious_df[spurious_i], spurious_fpeak[spurious_i], spurious_dfpeak[spurious_i], spurious_Maj[spurious_i], spurious_Min[spurious_i], spurious_PA[spurious_i], spurious_S_Code[spurious_i]))
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
    os.system('date +"%Y-%m-%d %H:%M:%S %Z" > %s'%('statistics_GALFIT/done_output_sim_data_table_%s'%(alma_image_name)))





