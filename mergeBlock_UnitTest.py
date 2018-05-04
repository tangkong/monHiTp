import os
import glob
import numpy as np
from peakBBA import peakFitBBA
from extDimRedPack import ext_peak_num
from os.path import expanduser as expUsr

def testCWT():
    # Run cont wavelet transform
    filePath = expUsr('~/monHiTp/testMergeBlock/NiTiCuCo_SampleID1_t60_0048_1D.csv')

    data = np.genfromtxt(filePath, delimiter=',')
    Qlist = data[:,0]
    IntAve = data[:,1]

    newRow, numPeaks = ext_peak_num(Qlist, IntAve, 48)
    print(newRow, numPeaks)

testCWT()
