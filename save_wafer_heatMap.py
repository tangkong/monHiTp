import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import re

def FWHMmap(pathname):
    '''
    save heat map based on two csvs
    heat map depicts FWHM of FSDP
    1: ..._scan1.csv giving locations (in image folder)
    2: ...master.csv giving data (in processed folder)
    '''

    folder_path = os.path.dirname(pathname)
    filename = os.path.basename(pathname)
    # fileRoot was imageFilename
    fileRoot, ext = os.path.splitext(filename)
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) # name w/o ind

    # generate paths for dataframes
    locCSVpath = os.path.join(folder_path, base_filename + 'scan1.csv')
    masterPath = os.path.join(folder_path, base_filename + 'master.csv')
    savePath = os.path.join(folder_path, base_filename + 'FWHMheatMap.png')

    locDF = pd.read_csv(locCSVpath, skiprows=1)
    locDF.index += 1 # make index match scan number
    masterDF = pd.read_csv(masterPath)
    
    # grab first line and extract coordinates
    locFile = open(locCSVpath, 'r')
    line1 = locFile.readline()
    
    # grab bits between parentheses
    match = re.match('^.*?\((.*?)\)', line1).group(1)
    lmLst = [float(x) for x in match.split(',')]
    lmLst = [int(x) for x in lmLst]

    # initialize scatter plot 
    scatt = np.zeros( (int(lmLst[1]-lmLst[0]), 
                       int(lmLst[3]-lmLst[2]))   )
    
    # populate matrix
    for index, row in masterDF.iterrows():
        scanNo = int(row['scanNo'])
        xloc = locDF.iloc[scanNo-1, 2]
        yloc = locDF.iloc[scanNo-1, 1]

        scatt[xloc + lmLst[1], yloc + lmLst[3]] = row['FSDP_FWHM']

    plt.figure()
    plt.imshow(scatt, extent=(lmLst[0], lmLst[1], lmLst[2], lmLst[3]), cmap=cm.hot)
    plt.title('FWHM at FSDP')
    plt.colorbar()
    plt.savefig(savePath)
    plt.close()
