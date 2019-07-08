#!/usr/bin/python

# converts a gregorian date to julian date
# expects one or two arguments, first is date in dd.mm.yyyy,
# second optional is time in hh:mm:ss. If time is omitted,
# 12:00:00 is assumed

import math, sys, string

if len(sys.argv)==1:
    print "\n gd2jd.py converts a gregorian date to julian date."
    print "\n Usage: gd2jd.py dd.mm.yyyy [hh:mm:ss.ssss]\n"
    sys.exit()

date=string.split(sys.argv[1], ".")
dd=int(date[0])
mm=int(date[1])
yyyy=int(date[2])


if len(sys.argv)==3:
    time=string.split(sys.argv[2], ":")
    hh=float(time[0])
    min=float(time[1])
    sec=float(time[2])
else:
    hh=12.0
    min=0.0
    sec=0.0

UT=hh+min/60+sec/3600

print "UT="+`UT`

total_seconds=hh*3600+min*60+sec
fracday=total_seconds/86400

print "Fractional day: %f" % fracday
# print dd,mm,yyyy, hh,min,sec, UT

if (100*yyyy+mm-190002.5)>0:
    sig=1
else:
    sig=-1

JD = 367*yyyy - int(7*(yyyy+int((mm+9)/12))/4) + int(275*mm/9) + dd + 1721013.5 + UT/24 - 0.5*sig +0.5

months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

print "\n"+months[mm-1]+" %i, %i, %i:%i:%i UT = JD %f" % (dd, yyyy, hh, min, sec, JD),

# Now calculate the fractional year. Do we have a leap year?
daylist=[31,28,31,30,31,30,31,31,30,31,30,31]
daylist2=[31,29,31,30,31,30,31,31,30,31,30,31]
if (yyyy%4 != 0):
    days=daylist2
elif (yyyy%400 == 0):
    days=daylist2
elif (yyyy%100 == 0):
    days=daylist
else:
    days=daylist2

daysum=0
for y in range(mm-1):
    daysum=daysum+days[y]
daysum=daysum+dd-1+UT/24

if days[1]==29:
    fracyear=yyyy+daysum/366
else:
    fracyear=yyyy+daysum/365
print " = " + `fracyear`+"\n"
