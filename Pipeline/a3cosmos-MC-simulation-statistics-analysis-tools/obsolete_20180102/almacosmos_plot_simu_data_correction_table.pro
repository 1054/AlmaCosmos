; IDL 


PRO plot_simu_data_correction_table
    
    x1 = Double(CrabTableReadColumn('datatable_correction.txt', 'cell_par1_median', Commente=';', SkipValidLines=1))
    x2 = Double(CrabTableReadColumn('datatable_correction.txt', 'cell_par2_median', Commente=';', SkipValidLines=1))
    y_obs = Double(CrabTableReadColumn('datatable_correction.txt', 'cell_rel_median', Commente=';', SkipValidLines=1))
    y_err = Double(CrabTableReadColumn('datatable_correction.txt', 'cell_rel_scatter_68', Commente=';', SkipValidLines=1))
    ;print, x1
    
    var_surface = surface(y_obs, (x1), x2, /xlog, xrange=([3,100]), yrange=[0.0,5.0], xtitle='peak flux / rms noise', ytitle='Maj source / Maj beam', xstyle=1, ystyle=1)
    
END