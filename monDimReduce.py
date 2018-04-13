"""
function for reducing dimension of saxs images
input: file name / path, calibration path, 
output: in new (processed) folder, 1D plots, texture plots
"""

import os
import glob
from os.path import basename
import re
import time
import numpy as np
import random
import sys
# import modules
from input_file_parsing import parse_calib
from image_loader import load_image
from data_reduction_smooth import data_reduction
from save_Qchi import save_Qchi
from save_1Dplot import save_1Dplot
from save_1Dcsv import save_1Dcsv
from extract_max_ave_intensity import extract_max_ave_intensity
from extract_peak_number import extract_peak_num
from add_feature_to_master import add_feature_to_master
from save_texture_plot_csv import save_texture_plot_csv
from extract_texture_extent import extract_texture_extent
from nearest_neighbor_cosine_distances import nearst_neighbor_distance
from extract_signal_to_noise_ratio import extract_SNR
from reportFn import addFeatsToMaster

def SAXSDimReduce(calibPath, pathname, Qrange=None):
    '''
    Processing script, reducing images to 1D plots (Q-Chi, Texture, etc)
    '''
    print('\n')
    print('******************************************** Begin image reduction...')
    # PP: beam polarization, according to beamline setup. 
    # Contact beamline scientist for this number
    PP = 0.95   
    pixelSize = 79  # detector pixel size, measured in microns

    # pathname was imageFullName
    folder_path = os.path.dirname(pathname)
    filename = os.path.basename(pathname)
    # fileRoot was imageFilename
    fileRoot, ext = os.path.splitext(filename)
    index = re.match('.*?([0-9]+).[a-zA-Z]+$',filename).group(1)
    base_filename = re.match('(.*?)[0-9]+.[a-zA-Z]+$',filename).group(1) # name w/o ind
   
    # Master CSV path
    masterPath = os.path.join(folder_path,base_filename + 'master.csv')
     
    # generate a folder to put processed files
    save_path = os.path.join(folder_path, 'Processed')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # make master index (vestigial)
    master_index = str(int(random.random()*100000000))

    attDict = dict.fromkeys(['scanNo', 'SNR', 'textureSum', 'Imax',
                                'Iave', 'I_ratio', 'numPeaks'])
    #attribute1=[['scan#', 'Imax', 'Iave', 'Imax/Iave']]
    #attribute2=[['scan#', 'texture_sum']]
    #attribute3=[['scan#', 'peak_num']]
    #attribute4=[['scan#', 'neighbor_distance']]
    #attribute5=[['scan#', 'SNR']]

    ###### BEGIN READING CALIB FILE #################################################
    # initializing params, transform the calibration parameters from WxDiff to Fit2D
    d_in_pixel, Rotation_angle, tilt_angle, lamda, x0, y0 = parse_calib(calibPath)
    Rot = (np.pi * 2 - Rotation_angle) / (2 * np.pi) * 360  # detector rotation
    tilt = tilt_angle / (2 * np.pi) * 360  # detector tilt  # wavelength
    d = d_in_pixel * pixelSize * 0.001  # measured in milimeters

    print 'Processing image file: ' + pathname 

    ###### BEGIN PROCESSING IMAGE####################################################
    # import image and convert it into an array
    imArray = load_image(pathname)

    # data_reduction to generate Q-chi and 1D spectra, Q
    Q, chi, cake, Qlist, IntAve = data_reduction(imArray, d, Rot, tilt, 
                                                lamda, x0, y0, PP, pixelSize, Qrange=Qrange)
    # save Qchi as a plot *.png and *.mat
    save_Qchi(Q, chi, cake, fileRoot, save_path)
    # save 1D spectra as a *.csv
    save_1Dcsv(Qlist, IntAve, fileRoot, save_path)
    # extract composition information if the information is available
    # extract the number of peaks in 1D spectra as attribute3 by default
    newRow3, peaks = extract_peak_num(Qlist, IntAve, index)
    attDict['numPeaks'] = len(peaks)
    #attribute3.append(newRow3)
    #attributes = np.array(attribute3)

    # save 1D plot with detected peaks shown in the plot
    save_1Dplot(Qlist, IntAve, peaks, fileRoot, save_path)

    if True: 
        # extract maximum/average intensity from 1D spectra as attribute1
        newRow1 = extract_max_ave_intensity(IntAve, index)
        attDict['scanNo'], attDict['Imax'], attDict['Iave'], attDict['I_ratio'] = newRow1
        #attribute1.append(newRow1)
        #attributes = np.concatenate((attribute1, attributes), axis=1)

    if True:
        # save 1D texture spectra as a plot (*.png) and *.csv
        Qlist_texture, texture = save_texture_plot_csv(Q, chi, cake, fileRoot, save_path)
        # extract texture square sum from the 1D texture spectra as attribute2
        newRow2 = extract_texture_extent(Qlist_texture, texture, index)
        attDict['textureSum'] = newRow2[1]
        #attribute2.append(newRow2)
        #attributes = np.concatenate((attribute2, attributes), axis=1)

    if False:
        # extract neighbor distances as attribute4
        newRow4 = nearst_neighbor_distance(index, Qlist, IntAve, 
                    folder_path, save_path, base_filename,num_of_smpls_per_row)
        #attribute4.append(newRow4)
        #attributes = np.concatenate((attribute4, attributes), axis=1)

    if True:
        # extract signal-to-noise ratio
        newRow5 = extract_SNR(index, IntAve)
        attDict['SNR'] = newRow5[1]
        #attribute5.append(newRow5)
        #attributes = np.concatenate((attribute5, attributes), axis=1)
    
    # add features (floats) to master metadata
    attDict['scanNo'] = int(index)
    addFeatsToMaster(attDict, masterPath)
