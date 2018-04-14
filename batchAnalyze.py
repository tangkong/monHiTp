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

dataPath = os.path.expanduser('/data/b_mehta/bl1-5/Mar2018/TiAlCo/data/k9/')
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

print('Calibration File: ' + calibPath)
print('Config File: ' + configPath)
print('Folder to process: ' + dataPath)
print('\n\n')

##########################################Extension chooser?...

fileList = glob.glob(os.path.join(dataPath, '*.tif'))
if len(fileList) == 0:
    sys.exit('No files found')

# Sort out config file
config = parse_config(configPath)
if config: 
    Qrange = (config['Qmin'],config['Qmax'])
    peakShape = config['peakShape']
    peakNo = config['peakNo']
    fit_order = config['fit_order']
    hiLimit = config['highlightLimit']
    
else:
    Qrange, peakShape, peakNo, fit_order, hiLimit = None, None, None, None, None

files = fileList[config['startImg']:config['endImg']]
fileGen = (x for x in files)

loopTime = []
for filePath in fileGen:
    start = time.time()
    
    print('{0}'.format(filePath))
    filename = os.path.basename(filePath)
    print(filename + ' detected, processing')
    ########## Begin data reduction scripts ###########################
    SAXSDimReduce(calibPath, filePath, Qrange=Qrange)
    peakFitBBA(filePath)

    ########## Visualization #########################################
    # Pulling info from master CSV
    FWHMmap(filePath)
    contrastMap(filePath, hiLimit)

    print(filename + ' completed')

    end = time.time()
    loopTime += [(end-start)]


# Evaluate performance
avgTime = np.mean(loopTime)
maxTime = np.max(loopTime)
print('====================================================')
print('====================================================')
print('Files finished processing')
print('-----Avg {:.4f}s / file, max {:.4f}.s / file'.format(avgTime, maxTime))
print('-----Total Time Elapsed {:4f}s'.format(np.sum(loopTime)))
print('====================================================')
print('====================================================')
