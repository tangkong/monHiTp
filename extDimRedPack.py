# -*- coding: utf-8 -*-
"""
Created on Mon Jun 06 18:02:32 2016

@author: Apurva Mehta, fangren, roberttk
Adapted from fangren scripts
"""

import numpy as np
from scipy.signal import find_peaks_cwt, medfilt, savgol_filter
from scipy.optimize import curve_fit

def ext_max_ave_intens(IntAve, index):
    """
    extract the maximum intensity, average intensity, and a ratio of the two from data
    """
    Imax = np.max(IntAve)
    Iave = np.mean(IntAve)
    ratio = Imax/Iave
    newRow = [index, Imax, Iave, ratio]
    return newRow


def ext_peak_num(Qlist, IntAve, index, a1 = 1, a2 = 20):
    """
    extract the peak numbers from 1D spectra
    @Ron Pandolfi (LBL), fangren
    """

    peaks = find_peaks_cwt(IntAve, np.arange(a1, a2, 0.05))
    peaks = peaks[1:-1]
    h = 15  # number of points skipped in finite differences

    peaks_accepted = []
    window = h
    
    filter = np.nan_to_num(np.sqrt(np.abs(-(IntAve[2 * h:] - 2 * IntAve[h:-h] 
                            + IntAve[0:-2 * h]))))
    for peak in peaks:
        # if Qlist[peak] < 3:
            filterwindow = filter[max(peak - h - window, 0):min(peak - h + window, 
                                                                        len(filter))]
            spectrawindow = IntAve[max(peak - window, h):min(peak + window,
                                                                        len(filter))]

            try:
                if np.any(filterwindow > spectrawindow / 200):  
                    # np.percentile(filter,85) is also a good threshold
                    peaks_accepted.append(peak)
            except ValueError:
                continue
        # else:
        #     peaks_accepted.append(peak)

    newRow = [index, len(peaks_accepted)]
    return newRow, peaks_accepted

def ext_text_extent(Qlist_texture, texture, index):
    texture = np.array(texture)
    texture = texture **2
    SqrSum = np.nansum(texture)
    NormSqrSum = SqrSum/float(len(Qlist_texture))
    newRow = [index, NormSqrSum]
    return newRow

def func(x, *params):
    """
    create a Gaussian fitted curve according to params
    """
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp( -((x - ctr)/wid)**2)
    return y

def ext_SNR(index, IntAve):
    filter_window = 15
    IntAve_smoothed = savgol_filter(IntAve, filter_window, 2)
    noise = IntAve - IntAve_smoothed


    ## set initial parameters for Gaussian fit
    guess = [0, 5, 10]
    high = [0.5, 300, 1000]
    low = [-0.5, 0, 0.1]
    bins = np.arange(-100, 100, 0.5)

    # fit noise histogram
    n, bins = np.histogram(noise, bins= bins)
    popt, pcov = curve_fit(func, bins[:-1], n, p0=guess, bounds = (low, high))
    slope = 9.16805348809
    intercept = 60.7206954077

    SNR = slope * np.log(1/popt[2]) + intercept
    return [index, SNR]
