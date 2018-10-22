import numpy as np
import h5py
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

def load_stim_hdf5(fname, norm=True):
    with h5py.File(fname, 'r') as hdf_file:
        len_stim, ysize, xsize, nchannels = hdf_file['checkerboard'].shape
        stim = np.zeros((len_stim, ysize, xsize), dtype=np.float64)
        hdf_file['checkerboard'].read_direct(stim, np.s_[..., 1])
    stim_min, stim_max = stim.min(), stim.max()
    stim = ((stim - stim_min) / ((stim_max - stim_min) / 2) - 1)
    return stim

def spk_from_hdf5(fname):
    with h5py.File(fname, 'r') as sp_file:
        sp_file['spiketimes']
    return

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



def get_times_for_sta(timestamps, start_sync, end_sync):
    timestamp_filter = timestamps > start_sync
    vector_spikes = timestamps[timestamp_filter]
    timestamp_filter = vector_spikes < end_sync
    vector_spikes = vector_spikes[timestamp_filter]
    return vector_spikes

def plot_sta(sta_array, name=''):
    nframes = sta_array.shape[0]
    ncol = 6
    nrow = nframes/ncol+1 if nframes%ncol else nframes/ncol
    max_c = (np.abs(sta_array)).max()
    fig, ax = plt.subplots(nrow, ncol,
                           sharex=True, sharey=True, figsize=(6, nrow)
                           )
    axf = ax.flatten()
    for kidx, kframe in enumerate(sta_array):
        axf[kidx].pcolor(kframe, vmin=-max_c, vmax=max_c, cmap='RdBu_r')
        axf[kidx].set_title('frame {}'.format(nframes-kidx-1))
        axf[kidx].set_aspect(1)
    fig.colorbar(img, ax=ax, orientation='vertical', fraction=.01)
    fig.set_title(name)
    # plt.tight_layout()

def main():
    stim_file = '/home/cesar/exp/MEA-analysis/data/stim/checkerboard/stim_mini_MR-0227_.hdf5'
    sorting_file = '/home/cesar/exp/MEA-analysis/data/sorting/2018-01-25/2018-01-25.result.hdf5'
    sync_file = '/home/cesar/exp/MEA-analysis/data/sync/MR-0227/event_list/028.txt'

    sync_times = np.loadtxt(sync_file).T
    start_frame = sync_times[0]
    end_frame = sync_times[1]
    start_sync = start_frame[0]
    end_sync = end_frame[-1]
    bins_stim = np.concatenate((start_frame, end_frame[-1:]))
    len_sync = len(sync_times)
    sr = 20000

    stim_matrix = load_stim_hdf5(stim_file)

    with h5py.File(sorting_file) as sorting:
        timestamp = sorting['/spiketimes/temp_71'][...]
        ts_checkerboard = get_times_for_sta(timestamp, start_sync, end_sync)

    sta_array = single_sta(stim_matrix, ts_checkerboard, bins_stim)
    print sta_array.shape

    plot_sta(sta_array)

if __name__ == '__main__':
    main()
