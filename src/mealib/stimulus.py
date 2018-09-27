"""Tools to manipulate stumulus."""

import numpy as np
import h5py


def correct_checkerboard(sync_file, repeated_file, outputFile, stim_file,
                         mat_v73):
    """Create a new stimulus with all repeated frames.

    Take a checkerboar stimulus and add all repeated frame found in a
    experiment and create a new file.

    Parameters
    ----------


    Note
    ----------
    When a file is saved in vertion 7.3 by Matlab, it create a .mat
    file with a HDF5 format.

    Matlab use automaticly v7.3 when file has more than 100.000.000
    values, for example checkerboar
    31 [blocks]*31 [blocks] *72000 [img] use v7.0
    31 [blocks]*31 [blocks] *108000 [img]  use v7.3
    35 [blocks]*35 [blocks] *72000 [img]  use v7.3

    Todo
    ----------
    Check what is the correct order of dimentions in mat file and
    python. scipy.io.loadmat read matfile in inverse order to access
    array, ej. shape(*.mat) = (35,35,3,72000) and python should be
    (72000,3,35,35).
    """

    # Load data
    try:
        from scipy.io import loadmat
        stim = loadmat(stim_file)
        stim = stim['stim']
        stim = np.transpose(stim, np.arange(stim.ndim)[::-1])
        print 'Shape for checkerboar file: {}'.format(stim.shape)
    except NotImplementedError:
        with h5py.File(stim_file, 'r') as stim_raw:
            stim_raw_shape = np.array(stim_raw['stim'].shape)
            fix_dim = np.arange(stim_raw['stim'].ndim)
            fix_dim[-2:] = fix_dim[-2:][::-1]
            stim = np.empty(tuple(stim_raw_shape[fix_dim]), dtype=np.uint8)
            stim_raw['stim'].read_direct(stim, np.s_[...])
            stim = np.transpose(stim, fix_dim)
            print 'Shape for checkerboar file: {}'.format(stim.shape)
    except ValueError as verror:
        verror('There are problems with {} file'.format(stimMini))

    sync_frame = np.loadtxt(sync_file)
    repetared_frame = np.loadtxt(repeated_file)

    repeated = np.where(np.isin(sync_frame[:, 0], repetared_frame))[0]
    n_repeated = len(repeated)

    # Find repeated position an number of repetitions
    if n_repeated > 1:
        rep_pointer = 0
        counter = {repeated[rep_pointer]: 1}
        for krep in range(1, len(repeated)):
            if (repeated[krep] - repeated[krep-1]) > 1:
                counter[repeated[krep]] = 1
                rep_pointer = krep
            else:
                counter[repeated[rep_pointer]] += 1

    elif n_repeated == 1:
        counter = {repeated[0]: 1}
    else:
        counter = {}

    # Correct of repeated to get the original stim repeated
    sort_keys = [k for k in counter.keys()]
    sort_keys.sort()
    print 'Repeated frame {}'.format(sort_keys)

    if len(counter) > 1:
        corrected_repeated = {sort_keys[0]: counter[sort_keys[0]]}
        corrected_sum = counter[sort_keys[0]]
        for krep in range(1, len(sort_keys)):
            kkey = sort_keys[krep]
            corrected_repeated[kkey-corrected_sum] = counter[kkey]
            corrected_sum += counter[kkey]
    elif len(counter) == 1:
        corrected_repeated = counter
        corrected_sum = counter[sort_keys[0]]
    else:
        corrected_repeated = counter
        corrected_sum = 0

    stim_shape = stim.shape
    stim_shape = list(stim_shape)
    new_stim_shape = list(stim_shape)
    new_stim_shape[0] += corrected_sum

    new_stim = np.empty(tuple(new_stim_shape), dtype=np.uint8)

    range_stim = [k for k in corrected_repeated]
    range_stim.sort()
    range_stim = np.array([[0] + range_stim, range_stim + [stim_shape[0]]])
    range_stim = range_stim.transpose()

    if 0 not in corrected_repeated:
        corrected_repeated[0] = 0

    delay = 0
    for kstart, kend in range_stim:
        delay_rep = corrected_repeated[kstart]
        new_start, new_end = (kstart+delay, kstart+delay+delay_rep)
        new_stim[new_start:new_end, ...] = stim[kstart:kstart+1, ...]
        delay += delay_rep
        new_stim[kstart+delay:kend+delay, ...] = stim[kstart:kend, ...]
    del stim, sync_frame, repetared_frame

    with h5py.File(outputFile, 'w') as f:
        f.create_dataset('checkerboard', data=new_stim, dtype=np.uint8,
                         chunks=tuple([1]+new_stim_shape[1:]),
                         compression='gzip', shuffle=False)
