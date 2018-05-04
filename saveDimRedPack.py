# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13

@author: fangren, roberttk
Adapted from fangren code
"""

import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
import os.path
import scipy.io

def save_Qchi(Q, chi, cake, imageFilename, save_path):
    scipy.io.savemat(os.path.join(save_path, os.path.splitext(imageFilename)[0]+'_Qchi.mat'), {'Q':Q, 'chi':chi, 'cake':cake})
    Q, chi = np.meshgrid(Q, chi)

    plt.figure(1)
    plt.title('Q-chi polarization corrected_log scale')
    plt.pcolormesh(Q, chi, np.log(cake), cmap = 'viridis')
    plt.xlabel('Q')
    plt.ylabel('chi')
    #plt.xlim((0.7, 6.8))
    #plt.ylim((-56, 56))
    plt.clim((0, np.log(np.nanmax(cake))))
    # the next two lines contributed by S. Suram (JCAP)
    inds = np.nonzero(cake)
    plt.clim(scipy.stats.scoreatpercentile(np.log(cake[inds]), 5),
             scipy.stats.scoreatpercentile(np.log(cake[inds]), 95))
    plt.colorbar()
    plt.savefig(os.path.join(save_path, os.path.splitext(imageFilename)[0]+'_gamma'))
    plt.close()

def save_1Dcsv(Qlist, IntAve, imageFilename, save_path):
    """
    Qlist and IntAve are data. They are two 1D arrays created by 1D integrate function. 
    The function takes the two arrays and write them into two columns in a csv file
    imageFilename has the fomart of "*_0100.tif", the 1D csv will have the format of "_0100_1D.csv"
    """
    data= np.concatenate(([Qlist], [IntAve]))
    np.savetxt(os.path.join(save_path, os.path.splitext(imageFilename)[0]+'_1D.csv'), data.T, delimiter=',')

def save_1Dplot(Qlist, IntAve, peaks, imageFilename, save_path, titleAdd='.'):
    # generate a column average image
    plt.figure(2)
    plt.title('Column average' + titleAdd)
    plt.plot(Qlist, IntAve)
    plt.xlabel('Q')
    plt.ylabel('Intensity')
    #plt.xlim((0.7, 6.4))

    plt.savefig(os.path.join(save_path, os.path.splitext(imageFilename)[0]+'_1D'))
    
    plt.close()

def save_texture_plot_csv(Q, chi, cake, imageFilename, save_path):
    Q, chi = np.meshgrid(Q, chi)
    plt.figure(3)
    plt.title('texture')
    
    keep = (cake != 0)
    chi = chi*np.pi/180
    
    cake *= keep.astype(np.int)
    #chi *= keep.astype(np.int)    
    IntSum = np.bincount((Q.ravel()*100).astype(int), cake.ravel().astype(int))
    count = np.bincount((Q.ravel()*100).astype(int), keep.ravel().astype(int))
    IntAve = list(np.array(IntSum)/np.array(count))
    
    textureSum = np.bincount((Q.ravel()*100).astype(int), (cake*np.cos(chi)).ravel())
    chiCount = np.bincount((Q.ravel()*100).astype(int), (keep*np.cos(chi)).ravel())
    
    texture = list(np.array(textureSum)/np.array(IntAve)/np.array(chiCount)-1)
    
    step = 0.01
    Qlen = int(np.max(Q)/step+1)
    Qlist_texture = [i*step for i in range(Qlen)]
    
    plt.plot(Qlist_texture, texture)
    plt.xlabel('Q')
    plt.ylabel('Texture')
    #plt.xlim((0.7, 6.4))
    plt.savefig(os.path.join(save_path, os.path.splitext(imageFilename)[0] + '_texture'))
    plt.close()
    
    data = np.concatenate(([Qlist_texture], [texture]))
    np.savetxt(os.path.join(save_path, os.path.splitext(imageFilename)[0]+'_texture.csv'), data.T, delimiter=',')

    return Qlist_texture, texture
