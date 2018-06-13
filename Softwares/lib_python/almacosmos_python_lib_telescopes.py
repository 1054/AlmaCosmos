#!/usr/bin/env python
# 

##################################################################################
# 
# class recognize_Instrument(str) -- return rec_Instrument, rec_Telescope
# 
##################################################################################

import os, sys, re





# 
def recognize_Instrument(FitsFileName):
    rec_Telescope = ""
    rec_Instrument = ""
    if type(FitsFileName) is str:
        if re.match(r'.*[^a-zA-Z]*ACS[^a-zA-Z]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "HST"
            rec_Instrument = "ACS"
        elif re.match(r'.*[^a-zA-Z]*IRAC[^a-zA-Z0-9]*ch1[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "IRAC ch1"
        elif re.match(r'.*[^a-zA-Z]*IRAC[^a-zA-Z0-9]*ch2[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "IRAC ch2"
        elif re.match(r'.*[^a-zA-Z]*IRAC[^a-zA-Z0-9]*ch3[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "IRAC ch3"
        elif re.match(r'.*[^a-zA-Z]*IRAC[^a-zA-Z0-9]*ch4[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "IRAC ch4"
        elif re.match(r'.*[^a-zA-Z]*MIPS[^a-zA-Z0-9]*160[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "MIPS 160um"
        elif re.match(r'.*[^a-zA-Z]*MIPS[^a-zA-Z0-9]*70[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "MIPS 70um"
        elif re.match(r'.*[^a-zA-Z]*MIPS[^a-zA-Z0-9]*24[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "Spitzer"
            rec_Instrument = "MIPS 24um"
        # 
        elif re.match(r'.*[^a-zA-Z]*U(ltra)*VISTA[^a-zA-Z0-9]*J[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            #<TODO># and FitsFileName.find('ir_bb')>=0
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "J"
        elif re.match(r'.*[^a-zA-Z]*U(ltra)*VISTA[^a-zA-Z0-9]*H[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            #<TODO># and FitsFileName.find('ir_bb')>=0
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "H"
        elif re.match(r'.*[^a-zA-Z]*U(ltra)*VISTA[^a-zA-Z0-9]*K(s)*[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            #<TODO># and FitsFileName.find('ir_bb')>=0
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "Ks"
        # 
        elif FitsFileName.lower().find(('.J.original').lower())>=0:
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "J"
        elif FitsFileName.lower().find(('.H.original').lower())>=0:
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "H"
        elif FitsFileName.lower().find(('.Ks.original').lower())>=0:
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "Ks"
        elif FitsFileName.lower().find(('.Ks.matched').lower())>=0:
            rec_Telescope = "UltraVISTA"
            rec_Instrument = "Ks"
        # 
        elif FitsFileName.lower().find(('_image_250_SMAP_').lower())>=0:
            rec_Telescope = "Herschel"
            rec_Instrument = "SPIRE 250um"
        elif FitsFileName.lower().find(('_image_350_SMAP_').lower())>=0:
            rec_Telescope = "Herschel"
            rec_Instrument = "SPIRE 350um"
        elif FitsFileName.lower().find(('_image_500_SMAP_').lower())>=0:
            rec_Telescope = "Herschel"
            rec_Instrument = "SPIRE 500um"
        elif FitsFileName.lower().find(('_pep_COSMOS_red_Map').lower())>=0:
            rec_Telescope = "Herschel"
            rec_Instrument = "PACS 160um"
        elif FitsFileName.lower().find(('_pep_COSMOS_green_Map').lower())>=0:
            rec_Telescope = "Herschel"
            rec_Instrument = "PACS 100um"
        elif FitsFileName.lower().find(('_pep_COSMOS_blue_Map').lower())>=0:
            rec_Telescope = "Herschel"
            rec_Instrument = "PACS 70um"
        elif FitsFileName.lower().find(('_cosmos08_gw_18Aug10_v6_').lower())>=0:
            rec_Telescope = ""
            rec_Instrument = ""
        elif FitsFileName.lower().find(('_MAMBO_image_').lower())>=0:
            rec_Telescope = "IRAM 30m"
            rec_Instrument = "MAMBO 1.2mm"
        elif FitsFileName.lower().find(('_vla_20cm').lower())>=0:
            rec_Telescope = "VLA"
            rec_Instrument = "20cm"
        elif FitsFileName.lower().find(('_vla_90cm').lower())>=0:
            rec_Telescope = "VLA"
            rec_Instrument = "90cm"
        elif re.match(r'.*[^a-zA-Z]*VLA[^a-zA-Z0-9]*3GHz*[^a-zA-Z0-9]*.*', FitsFileName, re.IGNORECASE) is not None:
            rec_Telescope = "VLA"
            rec_Instrument = "3GHz"
    # 
    return rec_Instrument, rec_Telescope




























