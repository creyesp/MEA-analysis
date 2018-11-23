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


def ste(time_stim, stim, spikes, nsamples_before=30, nsamples_after=0):
    """
    Get all windows of stimulis triggered by a spike.

    This function create a iterator to get a set of stimulus for a
    spike.

    Parameters
    ----------
    time_stim : ndarray
        The time array corresponding to the start of each frame in
        the stimulus.

    stimulus : ndarray
        A spatiotemporal or temporal stimulus array, where time is the
        first dimension.

    spikes : ndarray
        A list or ndarray of spike times.

    nsamples_before : int
        Number of samples to include in the STE before the spike.

    nsamples_after : int defaults: 0
        Number of samples to include in the STE after the spike.

    Returns
    -------
    ste : generator
        A generator that yields samples from the spike-triggered ensemble.

    Notes
    -----
    The spike-triggered ensemble (STE) is the set of all stimuli immediately
    surrounding a spike. If the full stimulus distribution is p(s), the STE
    is p(s | spike).

    """
    # assert stim.shape[0] == time_stim.size[0]+1, 'time _stim must has len(stim)+1'
    nbefore, nafter = nsamples_before, nsamples_after
    len_stim = stim.shape[0]
    # Number of spikes in each frame of the stimulus
    (nspks_in_frames, _) = np.histogram(spikes, bins=time_stim)

    valid_frames = np.where(nspks_in_frames > 0)[0]
    filter_valid_fame = (valid_frames >= nbefore) & \
                        (valid_frames < len_stim - nafter)
    valid_frames = valid_frames[filter_valid_fame]
    spike_in_frames = nspks_in_frames[valid_frames]

    # Valid frames consider itself as reference
    for kfr, nspks in zip(valid_frames, spike_in_frames):
        yield nspks*stim[kfr+1-nbefore:kfr+1+nafter, :, :].astype('float64')


def sta(time_stim, stim, spikes, nsamples_before=30, nsamples_after=0):
    """
    Compute a spike-triggered average.

    Parameters
    ----------
    time_stim : ndarray
        The time array corresponding to the start of each frame in
        the stimulus.

    stimulus : ndarray
        A spatiotemporal or temporal stimulus array, where time is the
        first dimension.

    spikes : ndarray
        A list or ndarray of spike times

    nsamples_before : int
        Number of samples to include in the STA before the spike

    nsamples_after : int
        Number of samples to include in the STA after the spike (default: 0)

    Returns
    -------
    sta : ndarray
        The spatiotemporal spike-triggered average.

    References
    ----------
    A simple white noise analysis of neuronal light responses.
    E J Chichilnisky
    """
    nframe_stim, ysize, xsize = stim.shape
    sta_array = np.zeros((nsamples_before+nsamples_after, ysize, xsize))

    ste_it = ste(time_stim, stim, spikes, nsamples_before, nsamples_after)
    for kwindow_stim in ste_it:
        sta_array += kwindow_stim
    if sta_array.any():
        sta_array /= float(spikes.size)
    return sta_array


def load_stim(fname, norm=True, channel='g', stype='hdf5'):
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
    if sta_array.any():
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
    if sta_array.any():
        sta_array /= spike_in_frames.sum()
    return (unit_name, sta_array)


# A global dictionary storing the variables passed from the initializer.
GLOBAL_STIM = {}
def init_multi_sta(stim, stim_shape):
    GLOBAL_STIM['stim'] = stim
    GLOBAL_STIM['stim_shape'] = stim_shape


def run_multi_sta(stim_file, bins_stim, spiketimes, pre_frame=30,
                  post_frame=0):
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

    wrap_sta = partial(multi_sta, bins_stim=bins_stim, pre_frame=pre_frame,
                       post_frame=post_frame)
    with Pool(processes=cpu_count(), initializer=init_multi_sta,
              initargs=(stim, stim_shape)) as pool:
        result = pool.map(wrap_sta, spiketimes)
    return result


def plot_sta(sta_array, name=''):
    nframes = sta_array.shape[0]
    ncol = 6
    nrow = nframes//ncol+1 if nframes % ncol else nframes//ncol
    max_c = (np.abs(sta_array)).max()
    fig, ax = plt.subplots(nrow, ncol,
                           sharex=True, sharey=True, figsize=(ncol*1.5, nrow*1.5)
                           )
    axf = ax.flatten()
    for kidx, kframe in enumerate(sta_array):
        img = axf[kidx].pcolor(kframe, vmin=-max_c, vmax=max_c, cmap='RdBu_r')
        axf[kidx].set_title('frame {}'.format(nframes-kidx-1), fontsize=6)
        axf[kidx].set_aspect(1)
    fig.colorbar(img, ax=ax, orientation='vertical', fraction=.01,
                 label='Range of stimulu [-1,1]')
    fig.suptitle(name)
    return (fig, ax)
