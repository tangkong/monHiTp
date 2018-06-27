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
from peakShapes import voigtFn, gaussFn
from selectPeakCriteria import findFitFSDP, findFitMaxPeak
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

    # Generate Master CSV path
    ### name w/o ind
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) 
    ### index
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

    ##############################################################
    #### Data Structure object instantiation (data, fit_order, ncp_prior)
    dataIn = BlockData(dataArray, fit_order, 0.5, peakShape)
    #### has various functions
    ##############################################################
  
    dataIn.trimData(trimLen=50)
     
    if useBkgdImg: # if a background image has been supplied
        print(config['bkgdPath'])
        bkgdData = np.genfromtxt(config['bkgdPath'], delimiter=',')
        bkgdX = bkgdData[:,0]
        bkgdY = bkgdData[:,1]

        dataIn.bkgdSubImg(np.array([bkgdX, bkgdY]))
    # background subtracted with polynomial of order = fit_order, trims ends
    elif type(fit_order) is str:
        dataIn.bkgdSub() # Trim using chebyshev 
    else: 
        dataIn.bkgdSubPoly(fit_order=fit_order) 
    
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
    paramDict, litFWHM = bumpFindFit(dataIn, peakShape, numCurves, config, 
                            savePath, basename(csvFilepath)[:-7])
   
    # Print information to terminal, print data to csv
    print('---------Fitting Finished')
    print('Fit ({0}) curve(s) per peak'.format(paramDict['numCurves']))
    print('Using ({0}) peak shape'.format(paramDict['peakShape']))

    # Generate residual plot using stored optParams
    pctErr = dataIn.genResidPlot(savePath, csvFilepath)
    
    genOptParamCSV(savePath, csvFilepath, paramDict)

    genPeakReportCSV(savePath, filepath, litFWHM, pctErr)

    ###############################################################################
    # Add features to master metadata
    # hard pull items for now
    attDict['scanNo'] = int(index)
    (attDict['FSDP_loc'], attDict['FSDP_FWHM'], attDict['FSDP_Intens'], 
        attDict['FSDP_yMax'])            = findFitFSDP(paramDict, litFWHM, config)
    (attDict['maxPeak_loc'], attDict['maxPeak_FWHM'], 
        attDict['maxPeak_Intens'])       = findFitMaxPeak(paramDict, litFWHM, config)

    addFeatsToMaster(attDict, masterPath)

