PRO calc_Gaussian_convolved_sizes_Test_2_PA_diff_90
    
    print, 'Checking !PATH'
    print, !PATH
    print, ''
    
    print, 'resolve_all'
    resolve_all
    print, ''
    
    ; ------------------- ;
    ; Create Source Image ;
    ; ------------------- ;
    
    ; Create Gaussian with PSF_Gaussian (but setting PA is not working)
    ;Gaussian_1 = PSF_Gaussian(FWHM=[10.0,7.0],NPIXEL=[301,301],XY_CORREL=0.9)
    ;Image_1 = IMAGE(Gaussian_1)
    FWHM_1 = [30,22]
    PA_1 = -90.0 ; +X axis direction
    Gaussian_1 = CrabImageGaussian2D(FWHM=FWHM_1, NPIXEL=301, XArray=X, YArray=Y, PA=PA_1)
    print, 'MAX(Gaussian) =', MAX(Gaussian_1)
    print, 'TOTAL(Gaussian) =', TOTAL(Gaussian_1)
    print, 'MAX(Gaussian)*(!PI/(4*alog(2))*aFWHM*bFWHM) =', MAX(Gaussian_1)*(!PI/(4*alog(2))*FWHM_1[0]*FWHM_1[1]) ; Yes, matched!
    print, ''
    
    
    
    ; ---------------- ;
    ; Create PSF Image ;
    ; ---------------- ;
    
    FWHM_PSF = [30,5]
    PA_PSF = 0.0 ; +Y axis direction
    Gaussian_PSF = CrabImageGaussian2D(FWHM=FWHM_PSF, NPIXEL=301, PA=PA_PSF)
    
    
    
    ; --------------- ;
    ; Convolve Images ;
    ; --------------- ;
    
    Gaussian_Convol = convolve(Gaussian_1, Gaussian_PSF) / (2*!PI*SQRT(FWHM_1[0]*FWHM_1[1]+FWHM_PSF[0]*FWHM_PSF[1]))
    Gaussian_Convol_Reormalization = 1.0 / TOTAL(Gaussian_Convol,/DOUBLE) * TOTAL(Gaussian_1,/DOUBLE)
    Gaussian_Convol = Gaussian_Convol * Gaussian_Convol_Reormalization 
    print, 'MAX(Gaussian_Convol) =', MAX(Gaussian_Convol)
    print, 'TOTAL(Gaussian_Convol) =', TOTAL(Gaussian_Convol)
    print, 'MAX(Gaussian_Convol)*(!PI/(4*alog(2))*aFWHM*bFWHM) =', MAX(Gaussian_Convol)*(!PI/(4*alog(2))*FWHM_1[0]*FWHM_1[1]) ; Yes, matched!
    print, 'MAX(Gaussian_Convol)*(!PI/(4*alog(2))*(aFWHM*bFWHM+aPSF*bPSF)) =', MAX(Gaussian_Convol)*(!PI/(4*alog(2))*(FWHM_1[0]*FWHM_1[1]+FWHM_PSF[0]*FWHM_PSF[1])) ; Yes, matched!
    print, 'MAX(Gaussian_Convol)*(!PI/(4*alog(2))*SQRT(aFWHM^2+aPSF^2)*SQRT(bFWHM^2+bPSF^2)) =', MAX(Gaussian_Convol)*(!PI/(4*alog(2))*SQRT(FWHM_1[0]^2+FWHM_PSF[0]^2)*SQRT(FWHM_1[1]^2+FWHM_PSF[1]^2)) ; Yes, matched!
    print, ''
    
    ; check total/peak
    print, 'total/peak =', TOTAL(Gaussian_Convol) / MAX(Gaussian_Convol)
    print, 'A_source =', !PI/(4*alog(2))*SQRT(FWHM_1[0]^2+FWHM_PSF[0]^2)*SQRT(FWHM_1[1]^2+FWHM_PSF[1]^2)
    print, ''
    
    
    
    ; --------------- ;
    ; Save the images
    ; --------------- ;
    MKHDR, Gaussian_Convol_Header, Gaussian_Convol
    sxaddpar, Gaussian_Convol_Header, 'BMAJ', FWHM_PSF[0]
    sxaddpar, Gaussian_Convol_Header, 'BMIN', FWHM_PSF[1]
    sxaddpar, Gaussian_Convol_Header, 'BPA', PA_PSF
    sxaddpar, Gaussian_Convol_Header, 'BUNIT', 'Jy/beam'
    MWRFITS, Gaussian_Convol, 'Gaussian_Convol.fits', Gaussian_Convol_Header, /Create
    
    
    
    ; --------------- ;
    ; Show the images
    ; --------------- ;
    Image_1 = IMAGE(Gaussian_1, LAYOUT=[3,1,1])
    Image_1 = IMAGE(Gaussian_PSF, /CURRENT, LAYOUT=[3,1,2])
    Image_1 = IMAGE(Gaussian_Convol, /CURRENT, LAYOUT=[3,1,3])
    
    
    
    ; --------------- ;
    ; Gaussian 2D FIT ;
    ; --------------- ;
    ; referenece: https://www.harrisgeospatial.com/docs/gauss2dfit.html
    Fit_Image = GAUSS2DFIT(Gaussian_Convol, Fit_Param, /TILT)
    ; swap if Maj_convol < Min_convol
    if Fit_Param[2] LT Fit_Param[3] THEN BEGIN
        Temp_Param = Fit_Param[3]
        Fit_Param[3] = Fit_Param[2]
        Fit_Param[2] = Temp_Param
        Fit_Param[6] = Fit_Param[6]-90.0/180.0*!PI
        IF Fit_Param[6] LT -90.0 THEN BEGIN
            Fit_Param[6] = Fit_Param[6]+180.0/180.0*!PI ; note that the direction of Param[6] of GAUSS2DFIT is clockwise!
        ENDIF
    ENDIF
    print, ''
    print, 'Input intrinsic Maj FWHM =', FWHM_1[0]
    print, 'Input intrinsic Min FWHM =', FWHM_1[1]
    print, 'Input intrinsic PA =', (PA_1)
    print, 'Input PSF Maj FWHM =', FWHM_PSF[0]
    print, 'Input PSF Min FWHM =', FWHM_PSF[1]
    print, 'Input PSF PA =', (PA_PSF)
    print, 'Fitted convolved Maj FWHM =', Fit_Param[2] * 2.0*SQRT(2.0*alog(2.0))
    print, 'Fitted convolved Min FWHM =', Fit_Param[3] * 2.0*SQRT(2.0*alog(2.0))
    print, 'Fitted convolved PA =', (90.0-(Fit_Param[6])/!PI*180.0) ; Param[6] is the Rotation of T radians from the X axis, in the clockwise direction.
    print, ''
    print, 'Fitted intri+PSF Maj^2+Min^2 = ', (FWHM_1[0])^2 + (FWHM_1[1])^2 + (FWHM_PSF[0])^2 + (FWHM_PSF[1])^2
    print, 'Fitted convolved Maj^2+Min^2 = ', (Fit_Param[2] * 2.0*SQRT(2.0*alog(2.0)))^2 + (Fit_Param[3] * 2.0*SQRT(2.0*alog(2.0)))^2
    print, ''
    
    ; Create an array with our fitted results
    B = Fit_Param
    xprime = (X - B[4])*cos(B[6]) - (Y - B[5])*sin(B[6])
    yprime = (X - B[4])*sin(B[6]) + (Y - B[5])*cos(B[6])
    Ufit = (xprime/B[2])^2 + (yprime/B[3])^2
    Zfit = EXP(-Ufit/2)

    ; Contour plot of the fit.
    Contour_1 = CONTOUR(Zfit, /OVERPLOT, C_THICK=[0.5], C_VALUE=[0.5], C_LABEL_SHOW=0, COLOR='red')
    
    
    ; 
    ; 
    ; 
    
    
    
    
    ; Create gaussian Z with random noise:
    ;Z = Zideal + RANDOMN(seed, nx, ny)
    ;B = []  ; clear out the variable

    
    
    
END