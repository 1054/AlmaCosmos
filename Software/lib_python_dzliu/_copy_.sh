#!/bin/bash

cd $(dirname ${BASH_SOURCE[0]})

mkdir crabcurvefit
mkdir crabgaussian
mkdir crabimage
mkdir crablogger
mkdir crabplot
mkdir crabtable

cp ~/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabcurvefit/CrabCurveFit.py       crabcurvefit/CrabCurveFit.py
cp ~/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabgaussian/CrabGaussian.py       crabgaussian/CrabGaussian.py
cp ~/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabimage/CrabImage.py             crabimage/CrabImage.py
cp ~/Cloud/Github/Crab.Toolkit.Python/lib/crab/crablogger/CrabLogger.py           crablogger/CrabLogger.py
cp ~/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabplot/CrabPlot.py               crabplot/CrabPlot.py
cp ~/Cloud/Github/Crab.Toolkit.Python/lib/crab/crabtable/CrabTable.py             crabtable/CrabTable.py



mkdir crabcasa
cp ~/Cloud/Github/Crab.Toolkit.CASA/lib/python/dzliu_clean.py                     crabcasa/dzliu_clean.py
