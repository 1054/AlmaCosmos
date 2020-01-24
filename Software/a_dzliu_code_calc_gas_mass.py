#!/usr/bin/env python
# 
from __future__ import print_function
import os, sys, re
import numpy as np
from astropy import units as u
from astropy import constants
from astropy.table import Table
import scipy
import scipy.interpolate
from astropy.modeling import models, fitting
from astropy.modeling.blackbody import blackbody_lambda, blackbody_nu
from astropy.cosmology import FlatLambdaCDM
cosmo = FlatLambdaCDM(H0=70, Om0=0.27, Tcmb0=2.725)
import a3cosmos_gas_evolution as a3g


# -- https://dust-emissivity.readthedocs.io/en/latest/_modules/dust_emissivity/blackbody.html
# Declare global constants with numeric values to allow for relatively
# high-performance (low-overhead) use of astropy units
_h = constants.h.cgs.value
_c = constants.c.cgs.value
_k_B = constants.k_B.cgs.value
_m_p = constants.m_p.cgs.value

# Globally define the unit of the blackbody function in CGS
_bbunit_nu_cgs = u.erg/u.s/u.cm**2/u.Hz/u.sr
_bbunit_lam_cgs = u.erg/u.s/u.cm**2/u.cm/u.sr


def _blackbody_hz(nu, temperature):
    """
    Compute the Planck function given nu in Hz and temperature in K with output
    in cgs
    """
    I = (2*_h*nu**3 / _c**2 * (exp(_h*nu/(_k_B*temperature)) - 1)**-1)

    return I


def _modified_blackbody_hz(nu, temperature, beta, column=1e21, muh2=2.8, kappanu=None,
                           kappa0=4.0, nu0=505e9, dusttogas=100.):
    """
    Numpy-only computation of the modified blackbody function.  Intended for
    use during fitting and in other cases of high-performance needs
    """
    if kappanu is None:
        kappanu = kappa0 / dusttogas * (nu/nu0)**beta
    
    # numpy apparently can't multiply floats and longs
    tau = muh2 * _m_p * kappanu * column

    modification = (1.0 - np.exp(-1.0 * tau))

    I = _blackbody_hz(nu, temperature)*modification

    return I









# 
# main
# 
if __name__ == '__main__':
    
    # best-fit SED copied from '/Users/dzliu/Work/DeepFields/Works_cooperated/2019_Emanuele_Daddi_RO1001/20191024_SED_fitting/run_SED_fitting_michi2_20191024_no_radio_but_has_radio_SED/results_fit_5/best-fit_SED_RO1001.txt'
    #SED_table = Table.read('best-fit_SED_RO1001.txt', format='ascii')
    #SED_flux_at_obs_frame = scipy.interpolate.interp1d(SED_table.columns[0].data, SED_table.columns[1].data)
    
    
    z = 6.85
    M_star = 10**9.2
    SFR = 20
    
    #obs_wavelength_um = 1250.0 # um
    #obs_flux_mJy = 5.94 # mJy
    
    
    #SED_Planck_wavelengths = np.logspace(0, 6, num=1000) * (1.0+z)
    #SED_Planck_temperature = 25.0 # K
    #SED_Planck_beta = 1.8
    #SED_Planck_flux = _modified_blackbody_hz(2.99792458e5/SED_Planck_wavelengths*1e9, SED_Planck_temperature, SED_Planck_beta)
    #SED_flux_at_obs_frame = scipy.interpolate.interp1d(SED_Planck_wavelengths, SED_Planck_flux)
    
    # 
    # Gas mass from dust RJ-tail continuum
    # 
    #SED_flux_at_obs_wavelength = SED_flux_at_obs_frame(obs_wavelength_um) # mJy
    #SED_flux_at_rest_850um = SED_flux_at_obs_frame(850.0*(1.0+z))
    obs_wavelength_um = 850*(1.0+6.85)
    obs_flux_mJy = 2.0e-3 # mJy
    SED_flux_at_obs_wavelength = 2.0e-3 # mJy
    SED_flux_at_rest_850um = 2.0e-3 # mJy
    M_mol_gas, method = a3g.calc_gas_mass_from_dust_continuum(obs_wavelength_um, obs_flux_mJy, SED_flux_at_obs_wavelength, SED_flux_at_rest_850um, z)
    print('M_mol_gas_Hughes2017 = %.3e (a3g, method %s)'%(M_mol_gas, method))
    
    
    
    # 
    # Gas mass from gas-to-dust ratio method
    # M_dust_table copied from '/Users/dzliu/Work/DeepFields/Works_cooperated/2019_Emanuele_Daddi_RO1001/20191024_SED_fitting/run_SED_fitting_michi2_20191024_no_radio_but_has_radio_SED/results_fit_5/best-fit_param_Mdust_total.txt'
    # 
    #M_dust_table = Table.read('best-fit_param_Mdust_total.txt', format='ipac')
    #M_dust = 10**(M_dust_table['param_best'][-1])
    #
    #M_mol_gas, method = a3g.calc_gas_mass_from_dust_mass(M_dust, M_star = M_star, SFR = SFR, z = z)
    #print('M_mol_gas_GDR_1 = %.3e (a3g, method %s)'%(M_mol_gas, method))
    #
    #M_mol_gas, method = a3g.calc_gas_mass_from_dust_mass(M_dust, M_star = M_star, SFR = SFR, method = 'Magdis2012')
    #print('M_mol_gas_GDR_2 = %.3e (a3g, method %s)'%(M_mol_gas, method))
    #
    #M_mol_gas, method = a3g.calc_gas_mass_from_dust_mass(M_dust, GDR = 100)
    #print('M_mol_gas_GDR_3 = %.3e (a3g, method %s)'%(M_mol_gas, method))
    






