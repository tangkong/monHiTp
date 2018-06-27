import numpy as np
from peakShapes import voigtFn, gaussFn


##################################################################################
###  Criteria for selection of FSDP, and other peaks    
###  Edit this file to adjust logic
##################################################################################

def findFitFSDP(inputDict, litDict, config):
    '''
    takes fit FWHM dictionary (paramDict) and returns tuple with FSDP loc and FWHM
    v0.2: include intensity
    v0.3: modify limits, criteria.  Error handling
    Assumes [xloc, yloc, intensity, {peak params}, FWHM]

    Output: (curveLocation, curveFWHM, curveFitIValue, curveYMax)
    '''
    locList = np.array([])
    FWHMList = np.array([])
    intList = np.array([])
    peakNum = np.array([])
    peakList = np.array([])
    for key, item in inputDict.items():
        if type(key) is not str:
            for paramList in item:
                #print(paramList)
                
                # Calc max based on curveShape
                if config['peakShape'] == 'voigt':
                    func = voigtFn
                elif config['peakShape'] == 'gauss':
                    func = gaussFn
                else: 
                    func = voigtFn
                #print('I: {}'.format(paramList[2]))
                xRange = np.linspace(paramList[0]-0.1, paramList[0]+0.1,1000)
                yMax = np.max(func(xRange, *paramList[:-1])) # Dropping FWHM
                #print('ymax: {}'.format(yMax))
                
                ##############################################################
                # Logic for selection of peaks:
                ### pick if xLoc is 2.3 < x < 4.0, and FWHM < 2.0, and 
                ### yMax > 10
                ##############################################################
                validPeak = (litDict[key][0] > 2.3 and 
                    paramList[0] < 4.0 and paramList[-1] < 2.0 and 
                    yMax > 10 )#and
                    #type(litDict[key][1])!=str)
                if validPeak:
                    peakNum = np.append(peakNum, key)
                    locList = np.append(locList, paramList[0])
                    FWHMList = np.append(FWHMList, paramList[-1])
                    intList = np.append(intList, paramList[2])
                    peakList = np.append(peakList, yMax)

    try:
        # grab item with lowest x0 
        minPeakLocIndex = np.where(locList == min(locList))
        peakIndices = np.where(peakNum == peakNum[minPeakLocIndex])
        
        # compare curves within (peak with lowest x0), select curve with highest yMax
        i = np.where(peakList == max(peakList[peakIndices]))

        #print('FSDP:{}'.format((locList[i], FWHMList[i], intList[i])))
        a, b, c, d = locList[i], FWHMList[i], intList[i], peakList[i]
    except Exception as e:
        print('>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<')
        print(e)
        print('using non-sensical values for extracted parameter')
        print('>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<')
        a, b, c, d = 10, 0, 50, 100

    return a, b, c, d

def findFitMaxPeak(inputDict, litDict, config):
    '''
    takes fit FWHM dictionary and returns tuple with FSDP loc and FWHM
    v0.2: include intensity
    v0.3: modify limits, criteria.  Error handling
    '''
    locList = np.array([])
    FWHMList = np.array([])
    intList = np.array([])
    peakNum = np.array([])
    peakList = np.array([])
    for key, item in inputDict.items():
        if type(key) is not str:
            for paramList in item:
                if litDict[key][0] > 2.3 and type(litDict[key][1])!=str:
                    peakNum = np.append(peakNum, key)
                    locList = np.append(locList, paramList[0])
                    FWHMList = np.append(FWHMList, paramList[5])
                    intList = np.append(intList, paramList[2])

                    # Calc max based on curveShape
                    if config['peakShape'] == 'voigt':
                        func = voigtFn
                    elif config['peakShape'] == 'gauss':
                        func = gaussFn
                    else: 
                        func = voigtFn
                    #print('I: {}'.format(paramList[2]))
                    xRange = np.linspace(paramList[0]-0.1, paramList[0]+0.1,1000)
                    yMax = np.max(func(xRange, *paramList[:-1])) # Dropping FWHM
                    peakList = np.append(peakList, yMax)
                    #print('ymax: {}'.format(yMax))
    try: 
        # grab curve with highest yMax 
        maxIntIndex = np.where(peakList == max(peakList))
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
