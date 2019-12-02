from configparser import ConfigParser, ExtendedInterpolation
from multiprocessing import cpu_count
from multiprocessing import Pool

import h5py
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from spikelib.visualizations import plot_sta
from spikelib.utils import check_directory


def plotsta_multi(sta_data):
    """Plot sta in differents threats."""
    key = sta_data[0]
    sta_array = sta_data[1]
    spatial_char = sta_data[2]
    outputfolder = sta_data[3]
    

    intensities = ['nd2-255', 'nd3-255', 'nd4-255', 'nd5-255']
    frame_to_show = (21, 28)
    nrow = len(intensities)
    ncol = frame_to_show[1]-frame_to_show[0]
    figsize = (15,10)

    fig, (ax) = plt.subplots(nrow,ncol, figsize=figsize, sharex=True, sharey=True)
    for krow, intensity in zip(ax, intensities):            
        angle, a, b, x0, y0, snr, frame = spatial_char[intensity]
        frame_maxsta = sta_array[intensity][frame.astype('int')].max()
        max_amp = np.abs(sta_array[intensity]).max()
        for kidx_frame, kcol in zip(range(*frame_to_show), krow):
            frame_show = sta_array[intensity][kidx_frame]
            sta_imshow = kcol.imshow(frame_show, vmin=-max_amp, vmax=max_amp, cmap='RdBu_r', origin='upper') # upper lower
            kcol.hlines(y0, 0, 31, alpha=0.2, color='k')
            kcol.vlines(x0, 0, 31, alpha=0.2, color='k')
            kcol.set(title='{} f({})'.format(intensity, kidx_frame))
            pellipse = patches.Ellipse((x0,y0),a*2,b*2,angle=angle,facecolor='none',alpha=0.5, edgecolor='k', lw=2)
            kcol.add_patch(pellipse)
    for kax in ax.flatten():
        kax.set(xlim=(0,31), ylim=(0,31))
    plt.savefig('../fig/sta/check/'+key+'.png')
    plt.close()


def run_plot(input_file):
    outputfolder = u'../fig/sta/check/'
    check_directory(outputfolder)

    data = []
    with h5py.File(input_file, 'r') as stas:
        intensities = ['nd2-255', 'nd3-255', 'nd4-255', 'nd5-255']
        sta_group = '/sta/{}/raw/{}' 
        spatial_char_group = '/sta/{}/spatial/char/{}'
        
        for kkey in stas['/sta/nd5-255/raw/']:
        # for kkey in ['temp_{}'.format(kidx) for kidx in range(10)]:
            for intensity in intensities:
                sta_array_4i = {intensity: stas[sta_group.format(intensity, kkey)][...] for intensity in intensities}
                spatial_char_4i = {intensity: stas[spatial_char_group.format(intensity, kkey)][...] for intensity in intensities}
            data.append((kkey,
                         sta_array_4i,
                         spatial_char_4i,
                         outputfolder,
                        ))

    pool = Pool(processes=cpu_count())
    pool.map(plotsta_multi, data)


if __name__ == '__main__':


    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read('../config.ini')
    
    exp_name = config['EXP']['name']
    input_file = config['FILES']['processed']
    output_folder = config['REPORT']['sta']

    run_plot(input_file)
