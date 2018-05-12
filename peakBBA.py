import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
from os.path import basename
import re

# Personal package import
from BlockData import BlockData
from bumpFindFit import bumpFindFit
from reportFn import genOptParamCSV, genPeakReportCSV, addFeatsToMaster

import time

def peakFitBBA(filepath, config):
    '''
    Wrapper for Bayesian Block Analysis of 1D Plots.  
    Takes file path
    Assumes 1D files live in (filepath.dirname)/Processed/
    '''
    print('\n')
    print('******************************************** Begin peak fitting...')
    ##############################################################
    ############ Parse filepath input ############################

    processedPath = os.path.join(os.path.dirname(filepath), 'Processed/')
    folder_path = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    fileRoot, ext = os.path.splitext(filename)
    
    savePath = processedPath + 'peak_details/'
    csvFilepath = os.path.join(processedPath, fileRoot + '_1D.csv')

    # Master CSV path
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) # name w/o ind
    index = re.match('.*?([0-9]+).[a-zA-Z]+$',filename).group(1)
    masterPath = os.path.join(folder_path, base_filename + 'master.csv')
    attDict = {'scanNo': index}

    if not config:
        peakShape = 'Voigt'
        numCurves = 2 
        fit_order = 2 
    else: 
        peakShape = config['peakShape']
        numCurves = config['peakNo']
        fit_order = config['fit_order']
        useBkgdImg = config['bkgdImg']
        print('config read')
    ##############End Input#######################################
    ##############################################################


    if not os.path.exists(savePath):
        os.makedirs(savePath)

    peakCnt = 0
    # File data into array
    print csvFilepath
    data = np.genfromtxt(csvFilepath, delimiter = ',')
    Qlist = data[:,0]
    IntAve = data[:,1] 
    dataArray = np.array([Qlist, IntAve])

    #### Data Structure object instantiation (data, fit_order, ncp_prior)
    dataIn = BlockData(dataArray, fit_order, 0.5, peakShape)
    #### has various functions
   
    if useBkgdImg: # if a background image has been supplied
        print(config['bkgdPath'])
        bkgdData = np.genfromtxt(config['bkgdPath'], delimiter=',')
        bkgdX = bkgdData[:,0]
        bkgdY = bkgdData[:,1]

        dataIn.bkgdSubImg(np.array([bkgdX, bkgdY]))
    # background subtracted with polynomial of order = fit_order, trims ends
    elif type(fit_order) is str:
        dataIn.bkgdSub()
    else: 
        dataIn.bkgdSubPoly(fit_order=fit_order) 
    #dataIn.trimSubData() # Trim off some values (taken from original script)
    
    # Plot bkgdSub Data
    plt.figure(figsize=(8,8))
    plt.plot(Qlist, IntAve, label='Raw data', marker='s', color='k')
    plt.plot(dataIn.subData[0], dataIn.bkgd, 
                '--', label='Background', color='g')
    plt.plot(dataIn.subData[0], dataIn.subData[1],
                label='Background subtracted', color='r')
    try:
        plt.plot(dataIn.downData[0,:], dataIn.downData[1,:], label='Downsampled',
                     color='b', marker='o', linestyle='None')
    except Exception as e:
        print(e)

    plt.legend()
    plt.savefig(savePath + basename(csvFilepath)[:-7] + '_plot.png')
    plt.close()

    # Guess at noise level
    hld = dataIn.subData
    sigmaGuess = np.std(hld[1][hld[1] <= np.median(hld[1])])

    dataIn.cellData = sigmaGuess * np.ones(len(dataIn.subData[0]))
    
    # incorporate block information into data struct
    dataIn.blockFinder()
    
    
    # Get optimized parameters from fitting each block and plot
    paramDict, litFWHM = bumpFindFit(dataIn, peakShape, numCurves, 
                            savePath, basename(csvFilepath)[:-7])
   
    # Print information to terminal, print data to csv
    print('---------Fitting Finished')
    print('Fit ({0}) curve(s) per peak'.format(paramDict['numCurves']))
    print('Using ({0}) peak shape'.format(paramDict['peakShape']))

    # Generate residual plot using stored optParams
    pctErr = dataIn.genResidPlot(savePath, csvFilepath)
    
    genOptParamCSV(savePath, csvFilepath, paramDict)

    genPeakReportCSV(savePath, filepath, litFWHM, pctErr)

    # Add features to master metadata
    # hard pull items for now
    attDict['scanNo'] = int(index)
    attDict['FSDP_loc'], attDict['FSDP_FWHM'], attDict['FSDP_Intens'] = findFitFSDP(paramDict, litFWHM) 
    attDict['maxPeak_loc'], attDict['maxPeak_FWHM'], attDict['maxPeak_Intens'] = findFitMaxPeak(paramDict, litFWHM)
    addFeatsToMaster(attDict, masterPath)

def findFitFSDP(inputDict, litDict):
    '''
    takes fit FWHM dictionary (paramDict) and returns tuple with FSDP loc and FWHM
    v0.2: include intensity
    v0.3: modify limits, criteria.  Error handling
    Assumes [xloc, yloc, intensity, {peak params}, FWHM]
    '''
    locList = np.array([])
    FWHMList = np.array([])
    intList = np.array([])
    peakNum = np.array([])
    for key, item in inputDict.items():
        if type(key) is not str:
            for paramList in item:
                # param list: [x-loc
                # pick if loc is 2.3 < x < 4.0, and FWHM < 2.0, and litFWHM exists
                validPeak = (litDict[key][0] > 2.3 and 
                    paramList[0] < 4.0 and paramList[-1] < 2.0)#and
                    #type(litDict[key][1])!=str)
                if validPeak:
                    peakNum = np.append(peakNum, key)
                    locList = np.append(locList, paramList[0])
                    FWHMList = np.append(FWHMList, paramList[-1])
                    intList = np.append(intList, paramList[2])

    try:
        # grab item with lowest x0 
        minPeakLocIndex = np.where(locList == min(locList))
        peakIndices = np.where(peakNum == peakNum[minPeakLocIndex])
        
        # compare curves within peak with lowest x0
        i = np.where(intList == max(intList[peakIndices]))

        #print('FSDP:{}'.format((locList[i], FWHMList[i], intList[i])))
        a, b, c = locList[i], FWHMList[i], intList[i]
    except Exception as e:
        print('>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<')
        print(e)
        print('using non-sensical values for extracted parameter')
        print('>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<')
        a, b, c = 10, 0, 50

    return a, b, c

def findFitMaxPeak(inputDict, litDict):
    '''
    takes fit FWHM dictionary and returns tuple with FSDP loc and FWHM
    v0.2: include intensity
    v0.3: modify limits, criteria.  Error handling
    '''
    locList = np.array([])
    FWHMList = np.array([])
    intList = np.array([])
    peakNum = np.array([])
    for key, item in inputDict.items():
        if type(key) is not str:
            for paramList in item:
                if litDict[key][0] > 2.3 and type(litDict[key][1])!=str:
                    peakNum = np.append(peakNum, key)
                    locList = np.append(locList, paramList[0])
                    FWHMList = np.append(FWHMList, paramList[5])
                    intList = np.append(intList, paramList[2])

    try: 
        # grab curve with lowest x0 
        maxIntIndex = np.where(intList == max(intList))
        # find peak with found x0
        peakIndices = np.where(peakNum == peakNum[maxIntIndex])
        
        # compare curves within peak with lowest x0
        i = np.where(intList == max(intList[peakIndices]))

        a, b, c = locList[i], FWHMList[i], intList[i]
    except Exception as e:
        print('>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<')
        print(e)
        print('using non-sensical values for extracted parameter')
        print('>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<')
        a, b, c = 10, 0, 50

    return a, b, c

def findFSDP(litFWHM):
    '''
    takes literal FWHM dictionary and returns tuple with FSDP loc and FWHM
    v0.2: include intensity
    '''
    locList = []
    FWHMList = []
    intList = []
    for key, item in litFWHM.items():
        if item[0] > 1.8 and item[1] != 'N/A':
            locList.append(item[0])
            FWHMList.append(item[1])
            intList.append(item[2])

    # grab item with lowest loc
    i = locList.index(min(locList))
    return locList[i], FWHMList[i], intList[i]

def findMaxPeak(litFWHM):
    '''
    takes literal FWHM dictionary and returns tuple with FSDP loc and FWHM
    v0.2: include intensity
    '''
    locList = []
    FWHMList = []
    intList = []
    for key, item in litFWHM.items():
        if item[0] > 1.8 and item[1] != 'N/A':
            locList.append(item[0])
            FWHMList.append(item[1])
            intList.append(item[2])
            print(item)
    # grab item with lowest loc
    i = intList.index(max(intList))
    return locList[i], FWHMList[i], intList[i]
