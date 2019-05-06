import numpy as np
import matplotlib.pyplot as plt
import h5py
from multiprocessing import Pool
from multiprocessing import cpu_count

from spikelib.visualizations import plot_sta
from spikelib.utils import check_directory


def plotsta_multi(sta_data):
    """Plot sta in differents threats."""
    key = sta_data[0]
    sta_array = sta_data[1]
    outputfolder = sta_data[2]
    # sta_array = sta_data
    fig, ax = plot_sta(sta_array, key)
    fig.savefig('{}{}.png'.format(outputfolder, key))
    plt.close()

def run_plot(input_file, ksuffix):
    outputfolder = u'../fig/sta/{}__/'.format(ksuffix)
    check_directory(outputfolder)

    data = []
    with h5py.File(input_file, 'r') as stas:
        sta_group = '/sta/'+ksuffix+'/raw/'
        for kkey in stas[sta_group]:
        # for kkey in ['temp_{}'.format(kidx) for kidx in range(10)]:
            data.append((kkey,
                         stas[sta_group+kkey][...],
                         outputfolder,
                        ))

    pool = Pool(processes=cpu_count())
    pool.map(plotsta_multi, data)

if __name__ == '__main__':

    exp_name = 'MR-0092t2'
    input_file = '../data/{}_analysis_of_protocols_150um.hdf5'.format(exp_name)

    for ksuffix in ['nd2-255', 'nd3-255', 'nd4-255', 'nd5-255']:
        run_plot(input_file, ksuffix)
