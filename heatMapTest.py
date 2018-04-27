import os
import glob
import pandas as pd
import re
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from save_wafer_heatMap import FWHMmap, contrastMap
def test1():
    locCSVpath = '/home/b_mehta/monHiTp/testHold/J1_100517_1_24x24_t30r_scan1.csv'
    masterPath = '/home/b_mehta/monHiTp/testHold/test2.csv'

    locDF = pd.read_csv(locCSVpath, skiprows=1)
    locDF.index += 1 # make index match scan number
    masterDF = pd.read_csv(masterPath)

    # grab first line and extract coordinates
    locFile = open(locCSVpath, 'r')
    line1 = locFile.readline()
    match = re.match('^.*?\((.*?)\)', line1).group(1) # grab bits between parentheses
    lmLst = [float(x) for x in match.split(',')]
    lmLst = [int(x) for x in lmLst]
    print(type(lmLst[2]))

    # initialize scatter plot 
    scatt = np.zeros( (int(lmLst[1]-lmLst[0]), 
                       int(lmLst[3]-lmLst[2]))   )

    print(scatt.shape)

    # populate matrix
    for index, row in masterDF.iterrows():
        scanNo = int(row['scanNo'])
        xloc = locDF.iloc[scanNo-1, 2]
        yloc = locDF.iloc[scanNo-1, 1]

        print(xloc)
        print(yloc)

        scatt[xloc + lmLst[1], yloc + lmLst[3]] = row['FSDP_FWHM']

    plt.figure()
    plt.imshow(scatt, extent=(lmLst[0], lmLst[1], lmLst[2], lmLst[3]), cmap=cm.hot)
    plt.title('FWHM at FSDP')
    plt.colorbar()
    plt.savefig('test.png')

def test2():

    masterPath = '/home/b_mehta/monHiTp/testHoldOld/k9a_040318_1_24x24_t45_0001.tif'
    FWHMmap(masterPath)
    print('test2 complete')

def test3():
    masterPath = '/home/b_mehta/monHiTp/testHoldOld/k9a_040318_1_24x24_t45_0001.tif'
    contrastMap(masterPath)
    print('test3 complete')

def test4():
    pathname = '/home/b_mehta/data/bl1-5/Mar2018/NREL/FeNbB/data/b0/b0_02290_1_24x24_t45_0180.tif'
    folder_path = os.path.dirname(pathname)
    filename = os.path.basename(pathname)
    # fileRoot was imageFilename
    fileRoot, ext = os.path.splitext(filename)
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) # name w/o ind

    # generate paths for dataframes
    locCSVpath = os.path.join(folder_path, base_filename + 'scan1.csv')
    
    files = glob.glob(os.path.join(folder_path, '*scan*.csv'))
    filesRev = files[::-1]
    filesRev.sort(natcasecmp)
    
    dfMast = pd.read_csv(filesRev.pop(0), skiprows=1)
    for f in filesRev:
        dfTemp = pd.read_csv(f, skiprows=1)
        dfMast = pd.concat([dfMast, dfTemp], ignore_index=True)
        
    print(dfMast.iloc[40:50,1], dfMast.iloc[40:50,2])

def try_int(s):
    "Convert to integer if possible."
    try: return int(s)
    except: return s

def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))

def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))

def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())

def test5():
    pathname = '/home/b_mehta/data/bl1-5/Mar2018/CoTaZr/data/k3b/k3_012918_1_24x24_t45b_0469.tif'
    FWHMmap(pathname)
    print('test5 complete')
    
test5()
