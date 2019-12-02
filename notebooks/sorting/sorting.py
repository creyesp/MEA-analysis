import h5py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def get_features(sorting, isi_bin=2):
    """
    Make array with general information about a sorting.
    
    Return m features for each unit, spikerate, isi peak.
    
    Paramters
    ---------
    sorting: h5py.Group
        root group of soprting hdf5 file.
    isi_bin: int
        bin size to get isi values
    
    Return
    ------
    Array with nxm, where n is the number of units and m is number
    of features.
    """
    features = np.zeros((len(sorting['/spiketimes']), 2))
    duration = sorting['/info/duration/'][...]
    bins = np.linspace(0, isi_bin*100, 101)
    isi = np.zeros((len(sorting['/spiketimes']), bins.shape[0]-1))
    list_key = []
    for kidx, key in enumerate(sorting['/spiketimes']):
        list_key.append(key)
        spk = sorting['/spiketimes'][key][...].flatten()
        features[kidx, 0] = spk.size/duration.astype(float)
        dff = np.diff(spk) if spk.any() else 0
        count, bins = np.histogram(dff, bins=bins)

        isi[kidx] = count
        features[kidx, 1] = np.argmax(count)*isi_bin
    isi_df = pd.DataFrame(data=isi, index=list_key, columns=bins[:-1].astype(int))
    return features, isi_df


def plot_raster(sorting, range_view=None, idx_units=None, protocols_points=None, sr=20000.0, **kwargs):
    """Create a raster figure of a range of units.
    
    Parameters
    ----------
    sorting: h5py.Group
        oot group of soprting hdf5 file.
    range_view: tuple, defaul None
        range of unit index to plot. example (100,200)
    idx_units: list(int)
        index of units to plot raster.
    protocols_points: list, default None
        set of point to draw when the protocols was showed.
    sr: flaot, defaul 20000.0
        sampling rate
        
    Return
    ------
    fig: figure
        matplotlib figure object
    ax: Axis
        matplotlib axis object

    """
    sr = float(sr)
    protocols_points = np.asarray(protocols_points)
    protocols_points = protocols_points if protocols_points.any() else []
    
    if not idx_units:
        keys = list(sorting['/spiketimes'])[range_view[0]:range_view[1]]
    else:
        keys = ['temp_{:d}'.format(key) for key in idx_units]
    

    fig, ax = plt.subplots(**kwargs)
    for kidx, key in enumerate(keys):
        spk = sorting['spiketimes'][key][...]/sr
        ax.plot(spk, np.full(spk.shape, kidx), marker='|',alpha=0.1)
    ax.set_title('raster')
    ax.set_xlabel('time')
    ax.set_ylabel('units')
    
    for ktime in protocols_points:
        ax.vlines(ktime/sr, 0, len(keys), color='k', lw=1, alpha=0.3)
        
    return fig, ax