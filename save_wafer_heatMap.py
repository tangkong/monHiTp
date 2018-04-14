import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import re

def FWHMmap(pathname):
    '''
    save heat map based on two csvs
    heat map depicts FWHM of FSDP
    
    Input: pathname, path to image file being processed.
            Finds following files in folder with image file
    1: ..._scan1.csv giving locations (in image folder)
    2: ...master.csv giving data (in processed folder)
    '''

    folder_path = os.path.dirname(pathname)
    filename = os.path.basename(pathname)
    # fileRoot was imageFilename
    fileRoot, ext = os.path.splitext(filename)
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) # name w/o ind

    # generate paths for dataframes
    #locCSVpath = os.path.join(folder_path, base_filename + 'scan1.csv')

    # if multiple scan files, stich them together 
    files = glob.glob(os.path.join(folder_path, base_filename+'*scan*.csv'))
    files.sort(natcasecmp)
    dfMast = pd.read_csv(files.pop(0), skiprows=1)

    for f in files:
        dfTemp = pd.read_csv(f, skiprows=1)
        dfMast = pd.concat([dfMast, dfTemp], ignore_index=True)
    locDF = dfMast
        
    # finish generating paths
    masterPath = os.path.join(folder_path, base_filename + 'master.csv')
    savePath = os.path.join(folder_path, base_filename + 'FWHMheatMap.png')

    
    #locDF = pd.read_csv(locCSVpath, skiprows=1)
    locDF.index += 1 # make index match scan number
    masterDF = pd.read_csv(masterPath)
    
    # grab location lists
    plateX = locDF.iloc[:,2].values
    plateY = locDF.iloc[:,1].values

    FSDP_FWHM = masterDF['FSDP_FWHM'].values
    
    try: 
        plt.figure()
        plt.scatter(plateY[:len(FSDP_FWHM)], plateX[:len(FSDP_FWHM)], c=FSDP_FWHM, 
                      s=120, marker='s', 
                      linewidths=0.5,edgecolors='k', cmap=cm.viridis)
        plt.title('FWHM at FSDP')
        plt.xlim((-36,36))
        plt.ylim((-36,36))
        plt.clim((0.2,0.6))
        plt.colorbar()
        plt.savefig(savePath)
        plt.close()

    except Exception as e: 
        print('>>>>>>>>>>>>>>>>>>>>>>>>>ERROR ERROR ERROR ERROR ERROR')
        print(str(e))
        print('>>>>>>>>>>>>>>>>>>>>>>>>>failed to create heatmap')


def contrastMap(pathname, limit=0.45):
    '''
    save contrast map based on two csvs
    threshold based on limit input, FWHM<limit -> 0, FWHM>= -> 1 
    
    Input: pathname, path to image file being processed.
            Finds following files in folder with image file
    1: ..._scan1.csv giving locations (in image folder)
    2: ...master.csv giving data (in processed folder)
    '''
    # fill default parameter
    if limit is None:
        limit = 0.45

    folder_path = os.path.dirname(pathname)
    filename = os.path.basename(pathname)
    # fileRoot was imageFilename
    fileRoot, ext = os.path.splitext(filename)
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) # name w/o ind

    # generate paths for dataframes
    #locCSVpath = os.path.join(folder_path, base_filename + 'scan1.csv')
    
    # if multiple scan files, stich them together 
    files = glob.glob(os.path.join(folder_path, base_filename+'*scan*.csv'))
    files.sort(natcasecmp)
    
    dfMast = pd.read_csv(files.pop(0), skiprows=1)
    for f in files:
        dfTemp = pd.read_csv(f, skiprows=1)
        dfMast = pd.concat([dfMast, dfTemp], ignore_index=True)
    locDF = dfMast
    

    masterPath = os.path.join(folder_path, base_filename + 'master.csv')
    savePath = os.path.join(folder_path, base_filename + 'FWHMcontrastMap.png')

    #locDF = pd.read_csv(locCSVpath, skiprows=1)
    locDF.index += 1 # make index match scan number
    masterDF = pd.read_csv(masterPath)
    
    # grab location lists
    plateX = locDF.iloc[:,2].values
    plateY = locDF.iloc[:,1].values

    FSDP_FWHM = masterDF['FSDP_FWHM'].values
    FWHM = np.array(FSDP_FWHM)

    mask = FWHM >= limit
    contDat = mask.astype(int)
    try: 
        plt.figure()
        plt.scatter(plateY[:len(contDat)], plateX[:len(contDat)], c=contDat, 
                      s=120, marker='s', 
                      linewidths=0.5,edgecolors='k', cmap=cm.viridis)
        plt.title('FWHM at FSDP,highlight if FWHM >= {}'.format(limit))
        plt.xlim((-36,36))
        plt.ylim((-36,36))
        plt.clim((0.2,0.6))
        plt.colorbar()
        plt.savefig(savePath)
        plt.close()

    except Exception as e: 
        print('>>>>>>>>>>>>>>>>>>>>>>>>>ERROR ERROR ERROR ERROR ERROR')
        print(str(e))
        print('>>>>>>>>>>>>>>>>>>>>>>>>>failed to create heatmap')


def try_int(s):
    "Convert to integer if possible."
    try: return int(s)
    except: return s

def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    return map(try_int, re.findall(r'(\d+|\D+)', s))

def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))

def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())
