c***********************************************************************
c
c  calculate errors for flux densities in VLA continuum data
c  and deconvolve measured source sizes
c
c  compile with: f77 -o get_errors get_errors.f
c
c changes:
c 040701 - es: changed xmu?**2 --> xmu? - was wrong before!!
c
c***********************************************************************


	PROGRAM      get_errors


	real*4	    	xin(8,1000),xra(3,1000),xdec(3,1000)
        real            xsmaj,xsmin,xspa,xbmaj,xbmin,xbpa,xbmaj2,xbmin2
        real            ximaj,ximin,xipa,ximaj2,ximin2,xlipa,xlbpa
        real            sinc,cosc,rhoc,sigic2,det,rhoa
        data            const /28.647888/
        integer*4       ns,nl
	character*30 	fname(5)
        character*26    fcord(1000)
	character*10 	fvla(5)

c   get file name for source list

	print *,'Enter input file name: '
	read*,fname(1)
 	print *,fname(1)
	print *,'Enter output file name '
	read*,fname(2)
 	print *,fname(2)

           
        open(21,file=fname(1),form='formatted',status='unknown')       
        open(22,file=fname(2),form='formatted',status='unknown')       

c read in formated file 

        nl=0
        do i=1,1000
          read(21,31,end=1000)fcord(i),xin(1,i),xin(2,i),xin(3,i),xx,
     &         xin(4,i),xin(5,i),xin(6,i),xin(7,i),xin(8,i)
c          write(SCR,31)fcord(i),xin(1,i),xin(2,i),xin(3,i),xx,
c     &         xin(4,i),xin(5,i),xin(6,i),xin(7,i),xin(8,i)
           nl=nl+1
        enddo        
 31	format(a26,f7.3,f8.2,f10.3,f7.3,f10.3,f6.1,f6.1,f6.1,f7.3)

 1000	continue

c calculate errors following Hopkins et al. (2003) after Condon (1997)
c get errors xmu ~ 2/rho^2
c xmup: uncertainty in peak fit
c xmum: uncertainty in major axis fit
c xmun: uncertainty in minor axis fit
c and deconvolve beam using routine from AIPS SAD

c set clean beam values

        xbmaj=1.9
        xbmin=1.6
        xbpa=-23.0
        xcon=0.01**1

	do i=1,nl
           xmup=0.0 ![dzliu]! Gaussian term error
           xmum=0.0 ![dzliu]! major axis FWHM error
           xmun=0.0 ![dzliu]! minor axis FWHM error
           xper=0.0 ![dzliu]! peak flux error
           xier=0.0 ![dzliu]! total flux error
c get the errors for the flux density (see Hopkins et al. 2003)
c [dzliu]
c [dzliu] xin(5,i) should be the fitted apparent major axis FWHM (convolved!)
c [dzliu] xin(6,i) should be the fitted apparent minor axis FWHM (convolved!)
c [dzliu] xin(3,i) should be the fitted Gaussian normalizaiton A 'Condon_A'
c [dzliu] xin(8,i) should be the image rms noise 'Condon_mu'
c [dzliu] xmup is 'Condon_rho'**2
c [dzliu] xmup = Condon_rho = calc_Condon1997_rho(1.5,1.5)
c [dzliu] xmup = Condon_rho = sqrt((Condon_s_area)/(4*Condon_h_area) * Condon_h_maj**($1) * Condon_h_min**($2)) * Condon_A / Condon_mu
c [dzliu] xin(5,i) is 'convol_maj', xin(6,i) is 'convol_min'. xin(3,i) is 'Condon_A', xin(8,i) is 'Condon_mu'.
c [dzliu]
           xmup=xin(5,i)*xin(6,i)/(4*xbmaj*xbmin)*
     &          (xin(3,i)/xin(8,i))**2*
     &          (1+(xbmaj/xin(5,i))**2)**1.5*
     &          (1+(xbmin/xin(6,i))**2)**1.5
           xmum=xin(5,i)*xin(6,i)/(4*xbmaj*xbmin)*
     &          (xin(3,i)/xin(8,i))**2*
     &          (1+(xbmaj/xin(5,i))**2)**2.5*
     &          (1+(xbmin/xin(6,i))**2)**0.5
           xmun=xin(5,i)*xin(6,i)/(4*xbmaj*xbmin)*
     &          (xin(3,i)/xin(8,i))**2*
     &          (1+(xbmaj/xin(5,i))**2)**0.5*
     &          (1+(xbmin/xin(6,i))**2)**2.5
c 040701 - change xmu?**2 --> xmu? - was wrong before!! (see above)
           xper=xin(3,i)*(2/xmup+(xin(8,i)/xin(3,i))**2+xcon)**0.5
           xier=xin(4,i)*((xin(8,i)/xin(3,i))**2+xcon+2/xmup
     &          +xbmaj*xbmin/(xin(5,i)*xin(6,i))
     &          *(2/xmum+2/xmun))**0.5
c [dzliu]
c [dzliu] So I translated these as:
c [dzliu]     source_peak_err = peak * sqrt(2/Condon_rho**2 + (Condon_mu/Condon_A)**2 + xcon)
c [dzliu]     source_total_err = total * sqrt(2/Condon_rho**2 + (Condon_mu/Condon_A)**2 + xcon + Condon_h_area/Condon_s_area*(2/xmum+2/xmun))
c [dzliu]     source_total_err = total * sqrt(2/Condon_rho**2 + (Condon_mu/Condon_A)**2 + xcon + Condon_h_area/Condon_s_area*(maj_err/maj)**2 + Condon_h_area/Condon_s_area*(min_err/min)**2)
c [dzliu]
c [dzliu] where
c [dzliu]     peak = Condon_A
c [dzliu]     maj*min \propto Condon_s_area
c [dzliu]     bmaj*bmin \propto Condon_h_area
c [dzliu]     xmup = calc_Condon1997_rho(1.5,1.5)**2 # Condon1997 Eq(41)
c [dzliu]     xmum = calc_Condon1997_rho(2.5,0.5)**2 # Condon1997 Eq(41)
c [dzliu]     xmun = calc_Condon1997_rho(0.5,2.5)**2 # Condon1997 Eq(41)
c [dzliu]     maj_err / maj = sqrt(2 / xmum) # dzliu
c [dzliu]     min_err / min = sqrt(2 / xmun) # dzliu
c [dzliu]     peak_err / peak = sqrt(2 / xmup) # dzliu
c [dzliu]
c [dzliu] dzliu equations are slightly different form the above uncommented codes. The later ones are based on Eqs(1,2,3) of Hopkins, et al., 2003AJ....125..465H,
c [dzliu] so there is an additional item '(Condon_mu/Condon_A)**2' and another additional item 'xcon' in each error equation.
c [dzliu]
           print*,'----',i,'---',xmup,xmum,xmun,xper,xier
c
c
c
c
c
c
c deconvolve the source size following AIPS
           xlinpa=mod(xin(7,i)+900.0,180.0)
           xlbpa=mod(xbpa+900.0,180.0)
           xbmaj2=xbmaj*xbmaj
           xbmin2=xbmin*xbmin
           ximaj2=xin(5,i)*xin(5,i)
           ximin2=xin(6,i)*xin(6,i)
           sinc=(xlinpa-xlbpa)/const
           cosc=cos(sinc)
           sinc=sin(sinc)
           rhoc=(ximaj2-ximin2)*cosc-(xbmaj2-xbmin2)
           if (rhoc.eq.0.0) then
              sigic2=0.0
              rhoa=0.0
           else
              sigic2=atan((ximaj2-ximin2)*sinc/rhoc)
              rhoa=((xbmaj2-xbmin2)-(ximaj2-ximin2)*cosc)
     &             /(2.0*cos(sigic2))
           endif
           xspa=sigic2*const+xlbpa
           det=((ximaj2+ximin2)-(xbmaj2+xbmin2))/2.0
           xsmaj=det-rhoa
           xsmin=det+rhoa
           xsmaj=max(0.0,xsmaj)
           xsmin=max(0.0,xsmin)
           xsmaj=sqrt(abs(xsmaj))
           xsmin=sqrt(abs(xsmin))
           if (xsmaj.lt.xsmin) then
              sinc=xsmaj
              xsmaj=xsmin
              xsmin=sinc
              xspa=xspa+90.0
           endif
           xspa=mod(xspa+900.0,180.0)
           if (xsmaj.eq.0.0) then
              xspa=0.0
           else if (xsmin.eq.0.0) then
              if ((abs(xspa-xlinpa).gt.45.0) .and.
     &           (abs(xspa-xlinpa).lt.135.0)) then
                 xspa=mod(xspa+450.0,180.0)
              endif
           endif
           write(22,32)fcord(i),xin(1,i),xin(2,i),xin(3,i),xper,
     &           xin(4,i),xier,xin(8,i),xin(5,i),xin(6,i),xin(7,i),
     &           xsmaj,xsmin,xspa
	enddo


 32	format(a26,2x,f7.3,2x,f6.2,2x,f7.3,2x,f6.3,2x,f7.3,2x,f6.3,2x,
     &         f6.3,2x,f4.1,2x,f4.1,2x,f5.1,2x,f4.1,2x,f4.1,2x,f5.1)

        close(21)
        close(22)

	end
 
