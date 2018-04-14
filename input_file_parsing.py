# -*- coding: utf-8 -*-
"""
Created on Nov 10

@author: fangren, roberttk
v0.2: 180410

"""
import os
import pandas as pd
import numpy as np

def parse_calib(filename):
    file=open(filename,'r')
    data = []
    with file as inputfile:
        for line in inputfile:
            data.append(line.strip().split('\n'))
    bcenter_x = float(data[6][0][10:])
    bcenter_y = float(data[7][0][10:])
    detector_dist = float(data[8][0][12:])
    detect_tilt_alpha = float(data[9][0][18:])
    detect_tilt_delta = float(data[10][0][18:])
    wavelength = float(data[11][0][11:])
    return detector_dist, detect_tilt_alpha, detect_tilt_delta, wavelength, bcenter_x, bcenter_y

def parse_config(filepath):
    '''
    Parses config file
    Returns dictionary with values for use in processing scripts
    if invalid, pass None
    '''
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        configDict = df.to_dict(orient='records')[0]
        
        return configDict
    else:
        print('File not found')
        return None

