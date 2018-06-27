import os, sys
import glob
from save_wafer_heatMap import FWHMmap, contrastMap
'''
Takes data path and generates heatmaps based on existing master files

Skips data analysis / image reduction

'''
############ INPUT PARAMETERS HERE ################
dataPath = os.path.expanduser('/data/b_mehta/bl1-5/Mar2018/TiAlCo/data/k9a/')

threshFWHM = 0.57
########### END INPUT PARAMETERS ##################

# find single file for feeding into pre-existing functions
fileList = glob.glob(os.path.join(dataPath, '*.tif'))
if len(fileList) == 0:
    sys.exit('No files found')

FWHMmap(fileList[0])                    # generates both normal FWHM and key maps
contrastMap(fileList[0], threshFWHM)    # generates contrast heatmap
