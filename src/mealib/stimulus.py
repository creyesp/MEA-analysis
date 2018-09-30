"""Tools to manipulate stumulus."""

import numpy as np
import h5py


def correct_checkerboard(sync_file, repeated_file, outputFile, stim_file):
    """Create a new stimulus with all repeated frames.

    Take a checkerboar stimulus and add all repeated frame found in a
    experiment and create a new stim file.

    Parameters
    ----------
    sync_file : str
        path to syncronozacion file with start and end time for
        checkerboar.
    repeated_file :
        path to file with all repeated times of experiment.
    outputFile :
        path to save new file.
    stim_file :
        path to original stim file (.mat).


    Note
    ----------
    scipy.io.loadmat read matfile in mantain the matlab axis order
    to access array, ej. shape (y,x,channel,frame) = (35,35,3,72000)
    and python should be (frame,y,x,channel) = (72000,35,35,3), for
    this reason the output file keep python format.
    https://eli.thegreenplace.net/2015/memory-layout-of-multi-dimensional-arrays/
    http://scikit-image.org/docs/dev/user_guide/numpy_images.html
    """

    # Load data
    try:
        from scipy.io import loadmat
        stim = loadmat(stim_file)
        stim = stim['stim']
        # Scikit-image convention
        (row, col, ch, pln) = (0, 1, 2, 3)
        stim = np.transpose(stim, (pln, row, col, ch))
    except NotImplementedError:
        with h5py.File(stim_file, 'r') as stim_raw:
            (pln, ch, col, row) = (0, 1, 2, 3)
            stim = np.empty(stim_raw['stim'].shape, dtype=np.uint8)
            stim_raw['stim'].read_direct(stim, np.s_[...])
            stim = np.transpose(stim, (pln, row, col, ch))
    except ValueError as verror:
        verror('There are problems with {} file'.format(stim_file))

    print 'Shape for checkerboar file: {}'.format(stim.shape)
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
