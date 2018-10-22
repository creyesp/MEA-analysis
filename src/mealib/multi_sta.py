from functools import partial
from multiprocessing import Pool, RawArray, freeze_support
import numpy as np
import h5py

from sta import get_times_for_sta, load_stim_hdf5


def multi_sta(timestamps, bins_stim, pre_frame=30, post_frame=0):
    """Compute the Spike Triggered Average for a cell."""
    print len(timestamps)
    stim_matrix = np.frombuffer(var_dict['stim']).reshape(var_dict['stim_shape'])
    len_stim = stim_matrix.shape[0]
    nspikes_in_frame, _ = np.histogram(timestamps, bins=bins_stim)
    valid_frames = np.where(nspikes_in_frame > 0)[0]
    filter_valid_fame = (valid_frames >= pre_frame) & \
                        (valid_frames < len_stim - post_frame)
    valid_frames = valid_frames[filter_valid_fame]

    spike_in_frames = nspikes_in_frame[valid_frames]
    nframe_stim, ysize, xsize = stim_matrix.shape
    sta_array = np.zeros((pre_frame+post_frame, ysize, xsize))
    # Valid frames consider itself as reference
    for kframe, nspikes in zip(valid_frames, spike_in_frames):
        start_frame = kframe+1-pre_frame
        end_frame = kframe+1+post_frame
        sta_array += nspikes*stim_matrix[start_frame:end_frame, :, :]
    sta_array /= spike_in_frames.sum()
    return sta_array

# A global dictionary storing the variables passed from the initializer.
var_dict = {}

def init_worker(stim, stim_shape):
    var_dict['stim'] = stim
    var_dict['stim_shape'] = stim_shape

def main():
    stim_file = '/home/cesar/exp/MEA-analysis/data/stim/checkerboard/stim_mini_MR-0227_.hdf5'
    sorting_file = '/home/cesar/exp/MEA-analysis/data/sorting/2018-01-25/2018-01-25.result.hdf5'
    sync_file = '/home/cesar/exp/MEA-analysis/data/sync/MR-0227/event_list/028.txt'

    # Sync
    sync_times = np.loadtxt(sync_file).T
    start_frame = sync_times[0]
    end_frame = sync_times[1]
    start_sync = start_frame[0]
    end_sync = end_frame[-1]
    bins_stim = np.concatenate((start_frame, end_frame[-1:]))

    # Stim
    stim_matrix = load_stim_hdf5(stim_file)
    stim_shape = stim_matrix.shape
    stim = RawArray('d', np.prod(stim_shape))
    stim_np = np.frombuffer(stim, dtype=np.float64).reshape(stim_shape)
    np.copyto(stim_np, stim_matrix)

    # Spikes
    spiketimes = h5py.File(sorting_file)
    list_name = [kname for kname in spiketimes['spiketimes']]
    tss = []
    for key in list_name[:40]:
        timestamp = spiketimes['/spiketimes/'+key][...]
        ts_checkerboard = get_times_for_sta(timestamp, start_sync, end_sync)
        tss.append(ts_checkerboard)
    spiketimes.close()

    pool = Pool(processes=4, initializer=init_worker,
                initargs=(stim, stim_shape))
    sta_cell = partial(multi_sta, bins_stim=bins_stim, pre_frame=30,
                       post_frame=0)
    result = pool.map(sta_cell, tss)
    print('Results (pool):\n', len(result))



if __name__ == '__main__':
    freeze_support()
    main()
