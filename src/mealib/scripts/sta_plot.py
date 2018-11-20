import numpy as np
import matplotlib.pyplot as plt
import h5py
from multiprocessing import Pool

from mealib.analysis import sta
from mealib.utils import check_directory



def plotsta_multi(sta_data):
    key = sta_data[0]
    sta_array = sta_data[1]
    output_folder = [2]
    fig, ax = sta.plot_sta(sta_array, key)
    fig.savefig(output_folder+key+'.png')
    plt.close()


if __name__ == '__main__':

    intensity = '255'
    outputfolder = 'STA_MR-0181_'+intensity+'/'
    check_directory(outputfolder)

    data = []
    input_file = 'STAs_MR-0181_intensity'+intensity+'.hdf5'
    with h5py.File(input_file) as stas:
        for kkey in stas['/STA/'+intensity]:
            data.append((kkey, 
                         stas['/STA/'+intensity+'/'+kkey][...],
                         output_folder
                         ))

    with Pool(4) as p:
        p.map(plotsta_multi, data)
