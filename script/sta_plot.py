from configparser import ConfigParser, ExtendedInterpolation
from multiprocessing import Pool
from multiprocessing import cpu_count
import os

import h5py
import numpy as np
import matplotlib.pyplot as plt

from spikelib.visualizations import plot_sta
from spikelib.utils import check_directory

def plotsta_multi(sta_data):
    """Plot sta in differents threats."""
    key = sta_data[0]
    sta_array = sta_data[1]
    outputfolder = sta_data[2]
    fig, ax = plot_sta(sta_array, key)
    fig.savefig('{}{}.png'.format(outputfolder, key))
    plt.close()

def run_plot(input_file, output_folder, ksuffix):
    outputfolder = os.path.join(output_folder, ksuffix)
    #u'{}/fig/{}/'.format(output_folder, ksuffix)
    check_directory(outputfolder)

    data = []
    with h5py.File(input_file, 'r') as stas:
        sta_group = '/sta/'+ksuffix+'/raw/'
        for kkey in stas[sta_group]:
            data.append((kkey,
                         stas[sta_group+kkey][...],
                         outputfolder,
                        ))

    pool = Pool(processes=cpu_count())
    pool.map(plotsta_multi, data)

if __name__ == '__main__':

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read('../config.ini')
    
    exp_name = config['EXP']['name']
    processed_file = config['FILES']['processed']
    output_folder = config['REPORT']['sta']

    with h5py.File(processed_file,'r') as pfile:
        protocols = list(pfile['/sta'].keys())

    for ksuffix in protocols:
        run_plot(input_file, output_folder, ksuffix)
