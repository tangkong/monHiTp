# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13

@author: fangren

"""

import pyFAI
from PIL import Image
import numpy as np
from scipy import signal
import time

def data_reduction(imArray, d, Rot, tilt, lamda, x0, y0, PP, pixelsize, 
                    QRange=None, ChiRange=None):
    """
    The input is the raw file's name and calibration parameters
    return Q-chi (2D array) and a spectrum (1D array)
    """    
    s1 = int(imArray.shape[0])
    s2 = int(imArray.shape[1])
    imArray = signal.medfilt(imArray, kernel_size = 5)
    
    detector_mask = np.ones((s1,s2))*(imArray <= 0)
    p = pyFAI.AzimuthalIntegrator(wavelength=lamda)
    
    # refer to http://pythonhosted.org/pyFAI/api/pyFAI.html for pyFAI parameters
    p.setFit2D(d,x0,y0,tilt,Rot,pixelsize,pixelsize) 
   
    # modify ranges to fit with detector geometry
    if (QRange is not None) and (ChiRange is not None): 
        azRange = tuple([x-Rot for x in ChiRange])
        radRange = tuple([y/10E8 for y in QRange])
        print(azRange, radRange)
    else: 
        azRange, radRange = None, None

    # the output unit for Q is angstrom-1
    cake,Q,chi = p.integrate2d(imArray,1000, 1000, 
                            azimuth_range=azRange, radial_range=radRange,
                            mask = detector_mask, polarization_factor = PP)

    
    # pyFAI output unit for Fit2D gemoetry incorrect. Multiply by 10e8 for correction
    Q = Q * 10e8  
    chi = chi+90
    
    Qlist, IntAve = p.integrate1d(imArray, 1000, 
                            azimuth_range=azRange, radial_range=radRange,
                            mask = detector_mask, polarization_factor = PP)

    # the output unit for Q is angstrom-1
    Qlist = Qlist * 10e8

    return Q, chi, cake, Qlist, IntAve

