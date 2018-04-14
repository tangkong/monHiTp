import os
import glob
import numpy as np

def test1():
    # Try SAXSDimReduce independent of other files
    from monDimReduce import SAXSDimReduce
    from peakBBA import peakFitBBA
    import re

    monFolder = '/home/b_mehta/monHiTp/testMon'
    calibPath = '/home/b_mehta/monHiTp/testHold/8Nov17_calib_1.calib'
    filepath = '/home/b_mehta/monHiTp/testHold/J1_100517_1_24x24_t30r_0001.tif'

    print re.match('.*?([0-9]+).[a-zA-Z]+$',filepath).group(1)
    print re.match('.*?([0-9]+).[a-zA-Z]+$','testfile_32901001001_1x2xp_0101.tiffff').group(1)

    print re.match('^(.*?)[0-9]+.[a-zA-Z]+$',filepath).group(1)
    SAXSDimReduce(calibPath, filepath)
    peakFitBBA(filepath)


    # Use Pandas to manage csvs
    #import pandas as pd

    #testCSVpath = '/home/b_mehta/monHiTp/sampleCSVOutput.csv'

    #df = pd.read_csv(testCSVpath, index_col=0) #read csv, set scanNo as index
    #df.at[2, 'SNR'] = 33 # for writing values

def paramDictTest():
    paramDict = {}
    paramDict['numCurves'] = 2
    paramDict['peakShape'] = 'Voigt'
    paramDict[0] = [np.array([1.006,  -8.684,   5.6744e+01, 2.452e-09,   2.92e-01,   5.8444e-01]), np.array([1.047,  -5.597,   0.14412204,  23.8590638 , 19.65617282,  79.90229259] ) ]

    paramDict[2] = [np.array([  4.62156707e+00,  -4.22578698e+00,   7.46225225e+01,
         4.46319005e-01,   2.90532243e-15,   1.05100094e+00]), np.array([  5.60046949,  -9.14712851,  54.23428537,   0.09461727,
         0.44501695,   0.9479291 ])]
    paramDict[1] = [np.array([  2.82158773e+00,  -9.14726593e+00,   1.72169714e+02,
         1.35354339e-01,   1.32614083e-01,   4.82997645e-01]), np.array([  2.63117781e+00,  -9.14726593e+00,   3.72541574e+01,
         4.61985083e-01,   1.33943421e-20,   1.08789173e+00])]

    locList = np.array([])
    FWHMList = np.array([])
    intList = np.array([])
    peakNum = np.array([])
    for key, item in paramDict.items():
        if type(key) is not str:
            for paramList in item:
                if paramList[0] > 2.0:
                    print(peakNum, key) 
                    peakNum = np.append(peakNum, key)
                    locList = np.append(locList, paramList[0])
                    FWHMList = np.append(FWHMList, paramList[5])
                    intList = np.append(intList, paramList[2]) 
    print(peakNum)
    print(locList) 

    # grab item with lowest x0 
    minPeakLocIndex = np.where(locList == min(locList))
    peakIndices = np.where(peakNum == peakNum[minPeakLocIndex])
    
    # compare curves within peak with lowest x0
    i = np.where(intList == max(intList[peakIndices]))
     
    print(peakIndices)
    
    print(locList[i], FWHMList[i], intList[i])
                
