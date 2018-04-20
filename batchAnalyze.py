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

calibPath = os.path.expanduser('~/monHiTp/testHold/8Nov17_calib_1.calib')
#calibPath = tkFileDialog.askopenfilename(title='Select Calibration File')
if calibPath is '':
    print('No calibration path selected, aborting...')
    sys.exit()

#dataPath = os.path.expanduser('/data/b_mehta/bl1-5/Mar2018/TiAlCo/data/k9a/')
dataPath = os.path.expanduser('~/monHiTp/test180420/')
#dataPath = tkFileDialog.askdirectory(title='Select folder to process')
if dataPath is '':
    print('No data folder selected, aborting...')
    sys.exit()

configPath = os.path.expanduser('~/monHiTp/config')
#configPath = tkFileDialog.askopenfilename(title='Select Config File')
if configPath is '':
    print('No config file supplied, aborting...')
    sys.exit()

print('Calibration File: ' + calibPath)
print('Config File: ' + configPath)
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
    if any(isinstance(n,str) for n in QRange) or any(isinstance(m,str) for m in ChiRange):
        print('Pass found, ignoring Q,Chi limits')
        QRange, ChiRange = None, None
    peakShape = config['peakShape']
    peakNo = config['peakNo']
    fit_order = config['fit_order']
    hiLimit = config['highlightLimit']
else:
    #Qrange, peakShape, peakNo, fit_order, hiLimit = None, None, None, None, None
    print('no config file')

files = fileList[config['startImg']:config['endImg']]
fileGen = (x for x in files)

loopTime = []
stage1Time = []
stage2Time = []
for filePath in fileGen:
    start = time.time()
    
    print('{0}'.format(filePath))
    filename = os.path.basename(filePath)
    print(filename + ' detected, processing')
    ########## Begin data reduction scripts ###########################
    SAXSDimReduce(calibPath, filePath, QRange=QRange, ChiRange=ChiRange)
    stage1int = time.time()

    peakFitBBA(filePath)
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

    break

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
