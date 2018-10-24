"""Spike Triggered Average module.

Spike Triggered Average (STA) is a algorithm to compute receptive
field of a cell.
"""
from functools import partial
from multiprocessing import cpu_count
from multiprocessing import Pool
from multiprocessing import RawArray
from multiprocessing import freeze_support

import h5py
import numpy as np
import matplotlib.pyplot as plt


# def load_stim(stimMini):
#     if stimMini.lower().endswith('.mat'):
#         try:
#             import scipy.io as sio
#             ensemble = sio.loadmat(stimMini)
#             estimulos = ensemble['stim']
#         except NotImplementedError:
#             import h5py
#             with h5py.File(stimMini, 'r') as hf:
#                 estimulos = hf['stim'][...]
#         except ValueError as verror:
#             verror('There are problems with {} file'.format(stimMini))
#         xSize, ySize, nchannels, lenEstimulos = estimulos.shape
#         estim = np.zeros((xSize, ySize, lenEstimulos))
#         for ke in range(lenEstimulos):
#             rgb = estimulos[:, :, :, ke]
#             gray = np.dot(rgb[..., :3], [0.299, 0.587, 0.144])
#             estim[:, :, ke] = gray
#         estim = np.asarray(estim)
#     elif stimMini.lower().endswith('.hdf5'):
#         # import h5py
#         with h5py.File(stimMini, 'r') as hf:
#             estimulos = hf['checkerboard'][...]
#             lenEstimulos, xSize, ySize, nchannels = estimulos.shape
#             estim = np.zeros((lenEstimulos, ySize, xSize))
#             estim = hf['checkerboard'][..., 1]
#     elif stimMini.lower().endswith('.np'):
#         estim = np.load(stimMatrix)
#     else:
#         raise ValueError('It necesary load a stim File')
#     return estim

def load_stim_hdf5(fname, norm=True, channel='g'):
    rgb = {'r': 0, 'g': 1, 'b': 2}
    with h5py.File(fname, 'r') as hdf_file:
        len_stim, ysize, xsize, nchannels = hdf_file['checkerboard'].shape
        stim = np.zeros((len_stim, ysize, xsize), dtype=np.float64)
        hdf_file['checkerboard'].read_direct(stim, np.s_[..., rgb[channel]])
    stim_min, stim_max = stim.min(), stim.max()
    stim = ((stim - stim_min) / ((stim_max - stim_min) / 2) - 1)
    return stim

def load_stim_multi(fname, norm=True, channel='g'):
    rgb = {'r': 0, 'g': 1, 'b': 2}
    with h5py.File(fname, 'r') as hdf_file:
        len_stim, ysize, xsize, nchannels = hdf_file['checkerboard'].shape
        stim_shape = (len_stim, ysize, xsize)
        stim_raw = np.zeros(stim_shape, dtype=np.float64)
        hdf_file['checkerboard'].read_direct(stim_raw, np.s_[..., rgb[channel]])
    stim_min, stim_max = stim_raw.min(), stim_raw.max()
    stim_raw = ((stim_raw - stim_min) / ((stim_max - stim_min) / 2) - 1)

    stim = RawArray('d', len_stim*ysize*xsize)
    stim_np = np.frombuffer(stim, dtype=np.float64).reshape(stim_shape)
    np.copyto(stim_np, stim_raw)
    return stim, stim_shape

def load_spk_txt():
    pass

def load_spk_hdf5():
    pass

def get_times_for_sta(timestamps, start_sync, end_sync):
    timestamp_filter = timestamps > start_sync
    vector_spikes = timestamps[timestamp_filter]
    timestamp_filter = vector_spikes < end_sync
    vector_spikes = vector_spikes[timestamp_filter]
    return vector_spikes

def single_sta(stim, timestamps, bins_stim, pre_frame=30, post_frame=0):
    """Compute the Spike Triggered Average for a cell."""
    len_stim = stim.shape[0]
    nspikes_in_frame, _ = np.histogram(timestamps, bins=bins_stim)
    valid_frames = np.where(nspikes_in_frame > 0)[0]
    filter_valid_fame = (valid_frames >= pre_frame) & \
                        (valid_frames < len_stim - post_frame)
    valid_frames = valid_frames[filter_valid_fame]

    spike_in_frames = nspikes_in_frame[valid_frames]
    nframe_stim, ysize, xsize = stim.shape
    sta_array = np.zeros((pre_frame+post_frame, ysize, xsize))
    # Valid frames consider itself as reference
    for kframe, nspikes in zip(valid_frames, spike_in_frames):
        sta_array += nspikes*stim[kframe+1-pre_frame:kframe+1+post_frame, :, :]
    sta_array /= spike_in_frames.sum()
    return sta_array

def multi_sta(timestamps, bins_stim, pre_frame=30, post_frame=0):
    """Compute the Spike Triggered Average for a cell.

    Parameter
    ---------
    timestamps: tuple(name, spikes)
    bins_stim: array
    pre_frame: int
    post_frame: int

    Return
    ---------
    tuple(name, sta)
    """
    unit_name, spk_time = timestamps

    print(len(spk_time))
    stim_matrix = np.frombuffer(
        GLOBAL_STIM['stim']).reshape(GLOBAL_STIM['stim_shape'])
    len_stim = stim_matrix.shape[0]
    nspikes_in_frame, _ = np.histogram(spk_time, bins=bins_stim)
    valid_frames = np.where(nspikes_in_frame > 0)[0]
    filter_valid_fame = (valid_frames >= pre_frame) & \
                        (valid_frames < len_stim - post_frame)
    valid_frames = valid_frames[filter_valid_fame]

    spike_in_frames = nspikes_in_frame[valid_frames]
    nframe_stim, ysize, xsize = stim_matrix.shape
    sta_array = np.zeros((pre_frame+post_frame, ysize, xsize), dtype=np.float64)
    # Valid frames consider itself as reference
    for kframe, nspikes in zip(valid_frames, spike_in_frames):
        start_frame = kframe+1-pre_frame
        end_frame = kframe+1+post_frame
        sta_array += nspikes*stim_matrix[start_frame:end_frame, :, :]
    sta_array /= spike_in_frames.sum()
    return (unit_name, sta_array)

# A global dictionary storing the variables passed from the initializer.
GLOBAL_STIM = {}
def init_multi_sta(stim, stim_shape):
    GLOBAL_STIM['stim'] = stim
    GLOBAL_STIM['stim_shape'] = stim_shape

def run_multi_sta(stim_file, bins_stim, spiketimes, pre_frame=30, post_frame=0):
    """Run sta in multiprocessing.

    Parameter
    ---------
    stim_file: str
        file of the stim
    bins_stim: array
        times of start and end of stim
    spiketimes: dict
        spiketimes to compute sta
    """
    freeze_support()
    stim, stim_shape = load_stim_multi(stim_file)

    pool = Pool(processes=cpu_count(), initializer=init_multi_sta,
                initargs=(stim, stim_shape))
    wrap_sta = partial(multi_sta, bins_stim=bins_stim, pre_frame=30,
                       post_frame=0)
    result = pool.map(wrap_sta, spiketimes)
    return result

def plot_sta(sta_array, name=''):
    nframes = sta_array.shape[0]
    ncol = 6
    nrow = nframes/ncol+1 if nframes % ncol else nframes/ncol
    max_c = (np.abs(sta_array)).max()
    fig, ax = plt.subplots(nrow, ncol,
                           sharex=True, sharey=True, figsize=(6, nrow)
                           )
    axf = ax.flatten()
    for kidx, kframe in enumerate(sta_array):
        img = axf[kidx].pcolor(kframe, vmin=-max_c, vmax=max_c, cmap='RdBu_r')
        axf[kidx].set_title('frame {}'.format(nframes-kidx-1))
        axf[kidx].set_aspect(1)
    fig.colorbar(img, ax=ax, orientation='vertical', fraction=.01)
    fig.suptitle(name)
    return (fig, ax)
