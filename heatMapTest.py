import os
import pandas as pd
import re
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

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
