import os
from os.path import expanduser as expUsr  
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

def test1():
    # Try SAXSDimReduce independent of other files
    from monDimReduce import SAXSDimReduce
    from peakBBA import peakFitBBA
    import re

    monFolder = '/home/b_mehta/monHiTp/test180420'
    calibPath = '/home/b_mehta/monHiTp/testHold/8Nov17_calib_1.calib'
    filepath = '/home/b_mehta/monHiTp/test180420/k3_012918_1_24x24_t45b_0357.tif'

    print re.match('.*?([0-9]+).[a-zA-Z]+$',filepath).group(1)
    print re.match('.*?([0-9]+).[a-zA-Z]+$','testfile_32901001001_1x2xp_0101.tiffff').group(1)

    print re.match('^(.*?)[0-9]+.[a-zA-Z]+$',filepath).group(1)
    SAXSDimReduce(calibPath, filepath)
    #peakFitBBA(filepath)


    # Use Pandas to manage csvs
    #import pandas as pd

    #testCSVpath = '/home/b_mehta/monHiTp/sampleCSVOutput.csv'

    #df = pd.read_csv(testCSVpath, index_col=0) #read csv, set scanNo as index
    #df.at[2, 'SNR'] = 33 # for writing values

def test2():
    
    # Try SAXSDimReduce independent of other files
    # Dim reduce on file with broken bound issues
    from monDimReduce import SAXSDimReduce
    from peakBBA import peakFitBBA
    import re

    calibPath = os.path.expanduser('~/monHiTp/test180504/cal_28mar18.calib')
    filepath = os.path.expanduser('~/monHiTp/test180504/k3_012918_1_24x24_t45b_0001.tif')
    filepath2 = os.path.expanduser('~/monHiTp/testHold/J1_100517_1_24x24_t30r_0001.tif')
    calibPath2 = os.path.expanduser('~/monHiTp/testHold/8Nov17_calib_1.calib')
    SAXSDimReduce(calibPath2, filepath2, QRange=(1.0,5.0), ChiRange=(-20,20))

    SAXSDimReduce(calibPath, filepath, QRange=(1.0,5.0), ChiRange=(-20,20))

def viewTif():
    from image_loader import load_image
    filepath = '/home/b_mehta/monHiTp/test180420/k3_012918_1_24x24_t45b_0357.tif'

    imArray = load_image(filepath)
    plt.figure()
    plt.imshow(imArray)
    plt.savefig('/home/b_mehta/monHiTp/test180420/test.png')

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

def getAllCalibPath():
    # map all sample images path to calib file path for error checking

    p = expUsr('~/allSampleTest/')
    outList = [ (p+'cal_28mar18.calib'), 
                (p+'cal_2.2deg_8April18.calib'),
                (p+'cal_1deg_8April18.calib'),
                (p+'cal_31mar18.calib'),
                (p+'cal_7April18.calib'),
                (p+'cal_5April18.calib')]

    return outList

def testInteg():
    from peakBBA import peakFitBBA
    from monDimReduce import SAXSDimReduce
    from input_file_parsing import parse_config
    calibList = getAllCalibPath()

    dataPath = expUsr('~/allSampleTest/')
    configPath = expUsr('~/monHiTp/config')
    fileList = glob.glob(os.path.join(dataPath, '*.tif'))

    fileGen = (x for x in fileList)
    config = parse_config(configPath)
    if config: 
        QRange = (config['Qmin'],config['Qmax'])
        ChiRange = (config['ChiMin'],config['ChiMax'])
        # require all bounds to exist, currently can't check default limits
        if (any(isinstance(n,str) for n in QRange) or 
                any(isinstance(m,str) for m in ChiRange)):
            print('Pass found, ignoring Q,Chi limits')
            QRange, ChiRange = None, None
        peakShape = config['peakShape']
        peakNo = config['peakNo']
        fit_order = config['fit_order']
        hiLimit = config['highlightLimit']
        

        config['bkgdPath'] = expUsr('~/monHiTp/')
    else:
        #Qrange, peakShape, peakNo, fit_order, hiLimit = None, None, None, None, None
        print('no config file')


    start = time.time()
    for f in fileGen:
        if any(x in f for x in ['k1', 'k2', 'k3', 'a1', 'k5']):
            c = calibList[0]
        elif any(x in f for x in ['k6', 'k7']):
            c = calibList[5]
        elif any(x in f for x in ['k8a']):
            c = calibList[1]
        elif any(x in f for x in ['k9a']):
            c = calibList[2]
        elif any(x in f for x in ['r5', 'r15']):
            c = calibList[4]
        else:
            c = calibList[3]

        print(f + '\n<===>\n' + c)
        
        SAXSDimReduce(c, f, config)
        peakFitBBA(f, config)
        
    end = time.time()

    print(end-start)
    print(len(fileList)) 


def adjGammaPlot():
    print('test')

################################# Function calls below #######################


testInteg()
