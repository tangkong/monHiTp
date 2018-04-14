import csv
import os
from os.path import basename
import numpy as np
import pandas as pd

def genOptParamCSV(savePath, file, optParams):
    '''
    Generate report CSV for given optParam dict and save path
    '''

    with open(savePath + basename(file)[:-7] + '_curveParams.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        if optParams['peakShape'] =='Voigt':
            #print('Array format: [x0, y0, I, alpha, gamma, FWHM]')
            writer.writerow([ 'peak', 'curve', 'x0', 'y0', 
                                'I', 'alpha', 'gamma', 'FWHM'])
        elif optParams['peakShape'] == 'Gaussian':
            #print('Array format: [x0, y0, I, sigma, FWHM]')
            writer.writerow(['peak', 'curve', 'x0', 'y0', 'I', 'sigma', 'FWHM'])
        for key, item in optParams.items():
            if key != 'numCurves' and key != 'peakShape':
                for i in range(len(item)):
                    #print('Param array for peak {0}, curve {1}: {2}'.format(key, i+1, 
                                            #np.array2string(item[i], precision=4)))

                    writer.writerow([key, i] + list(item[i]))
    
    print('OptParam report generated')

def genPeakReportCSV(savePath, file, litFWHM, pctErr):
    '''
    Generate report CSV for lit FWHM
    '''
    with open(savePath + basename(file)[:-4] + '_peakParams.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['peakNumber', 'peakLocation', 'FWHM', 'intensity','% Error'])

        for key, item in litFWHM.items():
            writer.writerow([key] + list(item) + [pctErr[key]])
    
    print('Peak report generated')

def addFeatsToMaster(featureDict, masterPath):
    '''
    Adds dictionary items to master csv
        each dict should represent a single scan. 
    If master CSV does not exist, create it.
    If master csv exists, append items
    Add columns as necessary
    '''

    if os.path.isfile(masterPath):
        attFrame = pd.read_csv(masterPath, index_col=0)
        newdf = pd.DataFrame(featureDict, index=['i',])
        newdf = newdf.set_index('scanNo')
        if featureDict['scanNo'] in attFrame.index: 
            # If adding info to existing scan, join on index (default)
            print('Join on {}'.format(featureDict['scanNo']))

            if 'FSDP_FWHM' not in attFrame.columns:
                # only join unique columns (new info)
                cols_to_use = newdf.columns.difference(attFrame.columns)
                #print(cols_to_use)
                attFrame = attFrame.join(newdf[cols_to_use]) 
            else:
                # in case where we are filling values:
                #print(attFrame)
                #print(newdf)
                attFrame.fillna(newdf, axis=0, inplace=True)
        else: 
            # if scan not yet recorded, append
            print('Found: {0} not in index'.format(featureDict['scanNo']))
            attFrame = attFrame.append(newdf)
            
        print('Feat added to Master for scan {}'.format(featureDict['scanNo']))
        
    else: # if file does not exist
        attFrame = pd.DataFrame(featureDict, index=['i',])
        attFrame = attFrame.set_index('scanNo')

        print('Master CSV generated')

    # write master csv
    attFrame.to_csv(masterPath)
    
        



