import os
import glob

# Try SAXSDimReduce independent of other files
from monDimReduce import SAXSDimReduce
from peakBBA import peakFitBBA
import re

monFolder = '/home/b_mehta/monHiTp/testMon'
calibPath = '/home/b_mehta/monHiTp/testHold/8Nov17_calib_1.calib'
filepath = '/home/b_mehta/monHiTp/testHold/J1_100517_1_24x24_t30r_0001.tif'

print re.match('.*?([0-9]+).[a-zA-Z]+$',filepath).group(1)
print re.match('.*?([0-9]+).[a-zA-Z]+$','testfile_32901001001_1x2xp_0101.tiffff').group(1)

print re.match('^(.*?)[0-9]+.[a-zA-Z]+$',filepath).group(1)
SAXSDimReduce(calibPath, filepath)
peakFitBBA(filepath)


# Use Pandas to manage csvs
#import pandas as pd

#testCSVpath = '/home/b_mehta/monHiTp/sampleCSVOutput.csv'

#df = pd.read_csv(testCSVpath, index_col=0) #read csv, set scanNo as index
#df.at[2, 'SNR'] = 33 # for writing values

