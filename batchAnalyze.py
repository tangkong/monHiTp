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

calibPath = os.path.expanduser('/home/b_mehta/data/bl1-5/Nov2017/Takeuchi/huilong/LaB6_cali_final_201703.calib')
#calibPath = os.path.expanduser('/home/b_mehta/data/bl1-5/May2018/LaB6/calib_13May18n.calib')
#calibPath = os.path.expanduser('~/monHiTp/testHold/8Nov17_calib_1.calib')
#calibPath = tkFileDialog.askopenfilename(title='Select Calibration File')
if calibPath is '':
    print('No calibration path selected, aborting...')
    sys.exit()
dataPath = os.path.expanduser('/home/b_mehta/data/bl1-5/Nov2017/Takeuchi/Huilone_NiTiCu/')
#dataPath = os.path.expanduser('/home/b_mehta/data/bl1-5/May2018/AlTiCo/data/k11a/')
#dataPath = os.path.expanduser('~/monHiTp/testHold/')
#dataPath = tkFileDialog.askdirectory(title='Select folder to process')
if dataPath is '':
    print('No data folder selected, aborting...')
    sys.exit()

configPath = os.path.expanduser('~/monHiTp/config')
#configPath = tkFileDialog.askopenfilename(title='Select Config File')
if configPath is '':
    print('No config file supplied, aborting...')
    sys.exit()

bkgdPath = os.path.expanduser('~/monHiTp/testBkgdImg/bg/a40_th2p0_t45_center_bg_0001.tif')
#configPath = tkFileDialog.askopenfilename(title='Select Config File')
if bkgdPath is '':
    print('No bkgd file supplied, aborting...')
    sys.exit()
    
print('Calibration File: ' + calibPath)
print('Config File: ' + configPath)
print('BkgdImg File: ' + configPath)
print('Folder to process: ' + dataPath)
print('')

##########################################Extension chooser?...

fileList = glob.glob(os.path.join(dataPath, '*.tif'))
if len(fileList) == 0:
    sys.exit('No files found')

# Sort out config file
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
    skipExisting = config['skipExisting']
else:
    #Qrange, peakShape, peakNo, fit_order, hiLimit = None, None, None, None, None
    print('no config file')

############ Background image processsing
if config['bkgdImg']:
    print('~~~~~~~~ Processing bkgd image')
    SAXSDimReduce(calibPath, bkgdPath, config)
    bkgdPathDir = os.path.dirname(bkgdPath)
    bkgdPathName = os.path.basename(bkgdPath)

    # config points to csv for further processing
    config['bkgdPath'] = bkgdPathDir + '/Processed/' + bkgdPathName[:-4] + '_1D.csv'
################################################

files = fileList[config['startImg']:config['endImg']]
fileGen = (x for x in files)

loopTime = []
stage1Time = []
stage2Time = []
for filePath in fileGen:
    filename = os.path.basename(filePath)

    if skipExisting:
        fileRoot, ext = os.path.splitext(filename)
        procPath = dataPath+'Processed/'+fileRoot+'_1D.csv'
        print(procPath)
        has1DcsvFile = os.path.isfile(procPath)
        if has1DcsvFile:
            print('Skipping file: {}'.format(procPath))
            continue 
    
    start = time.time()
    
    print('{0}'.format(filePath))
    print(filename + ' detected, processing')
    ########## Begin data reduction scripts ###########################
    SAXSDimReduce(calibPath, filePath, config) #QRange=QRange, ChiRange=ChiRange)
    stage1int = time.time()

    peakFitBBA(filePath, config)
    stage2int = time.time()
    ########## Visualization #########################################
    # Pulling info from master CSV
    FWHMmap(filePath)
    contrastMap(filePath, hiLimit)

    print(filename + ' completed')

    end = time.time()
    loopTime += [(end-start)]
    stage1Time += [(stage1int - start)]
    stage2Time += [(stage2int - stage1int)]



# Evaluate performance
avgTime = np.mean(loopTime)
maxTime = np.max(loopTime)
avg1 = np.mean(stage1Time)
avg2 = np.mean(stage2Time)
max1 = np.max(stage1Time)
max2 = np.max(stage2Time)
print('====================================================')
print('====================================================')
print('Files finished processing')
print('-----Avg {:.4f}s / file, max {:.4f}.s / file'.format(avgTime, maxTime))
print('-----Stage1: Avg {:.4f}s / file, max {:.4f}.s / file'.format(avg1, max1))
print('-----Stage2: Avg {:.4f}s / file, max {:.4f}.s / file'.format(avg2, max2))
print('-----Total Time Elapsed {:4f}s'.format(np.sum(loopTime)))
print('====================================================')
print('====================================================')
