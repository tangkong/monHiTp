import os, sys
import numpy as np
import glob
import numpy
import Tkinter, tkFileDialog
from monDimReduce import SAXSDimReduce
from peakBBA import peakFitBBA
from save_wafer_heatMap import FWHMmap, contrastMap
from input_file_parsing import parse_config

import time

print('*************************************************************')
print('*********************************** Begin Batch Processing...')
print('*************************************************************')

# grab monitor folder
#root = Tkinter.Tk()
#root.withdraw()

#dataPath = os.path.expanduser('~/monHiTp/testTakeI/')
dataPath = os.path.expanduser('~/data/bl1-5/Nov2017/Takeuchi/NiTiCuCo_SampleID2/')
#dataPath = os.path.expanduser('~/data/bl1-5/May2018/AlTiCo/data/k11a/')
#dataPath = tkFileDialog.askdirectory(title='Select folder to process')
if dataPath is '':
    print('No data folder selected, aborting...')
    sys.exit()

configPath = os.path.expanduser('~/monHiTp/config')
#configPath = tkFileDialog.askopenfilename(title='Select Config File')
if configPath is '':
    print('No config file supplied, aborting...')
    sys.exit()

print('Config File: ' + configPath)
print('Folder to process: ' + dataPath)
print('')

##########################################Extension chooser?...

fileList = glob.glob(os.path.join(dataPath + 'Processed/', '*1D.csv'))
if len(fileList) == 0:
    sys.exit('No files found')

# Sort out config file
config = parse_config(configPath)
if config: 
    skipExisting = config['skipExisting']
    hiLimit = config['highlightLimit']
else:
    #Qrange, peakShape, peakNo, fit_order, hiLimit = None, None, None, None, None
    print('no config file')

files = fileList[config['startImg']:config['endImg']]
fileGen = (x for x in files)

loopTime = []
stage2Time = []
for filePath in fileGen:
    filename = os.path.basename(filePath)
    fileRoot, ext = os.path.splitext(filename)
    
    if skipExisting:
        procPath = dataPath+'Processed/peak_details/'+fileRoot+'_curveParams.csv'
        hasParamsFile = os.path.isfile(procPath)
        if hasParamsFile:
            print('Skipping file: {}'.format(procPath))
            continue 
    
    start = time.time()
    
    print('{0}'.format(filePath))
    print(filename + ' detected, processing')

    # fake a path in prev folder
    # Assume name of format xxxxx_[index]_1D.csv
    fakeName = filename[:-7]+'.tif'
    fakePath = dataPath + fakeName
    print(fakePath)
    ########## Begin data reduction scripts ###########################
    stage1int = time.time()

    peakFitBBA(fakePath, config)
    stage2int = time.time()
    ########## Visualization #########################################
    # Pulling info from master CSV
    FWHMmap(fakePath)
    contrastMap(fakePath, hiLimit)

    print(filename + ' completed')

    end = time.time()
    loopTime += [(end-start)]
    stage2Time += [(stage2int - stage1int)]


    #break

# Evaluate performance
avgTime = np.mean(loopTime)
maxTime = np.max(loopTime)
avg2 = np.mean(stage2Time)
max2 = np.max(stage2Time)
print('====================================================')
print('====================================================')
print('Files finished processing')
print('-----Avg {:.4f}s / file, max {:.4f}.s / file'.format(avgTime, maxTime))
print('-----Stage2: Avg {:.4f}s / file, max {:.4f}.s / file'.format(avg2, max2))
print('-----Total Time Elapsed {:4f}s'.format(np.sum(loopTime)))
print('====================================================')
print('====================================================')
