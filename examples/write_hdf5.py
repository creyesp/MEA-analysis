"""Example to write in a hdf5 file with h5py"""
import os

import h5py
import numpy as np


if __name__ == '__main__':

    file_path = 'data/example.results.hdf5'
    if os.path.exists(file_path):
        os.remove(file_path)

    with h5py.File(file_path, 'w') as f:
        # Create a groups
        group_names = ['spiketimes', 'amplitudes']
        _ = [f.create_group(key) for key in group_names]

        # Create sinthetic data
        spikes = np.random.randint(low=0, high=123456, size=(100,))
        amplitude = np.random.rand(100)

        # Create datasets in each group
        f['spiketimes/'].create_dataset(name='temp_0', data=spikes,)
        f['amplitudes/'].create_dataset(name='temp_0', data=amplitude,)

        # Create a dataset with a value on root groups
        f.create_dataset(name='duration', data=[123456])

        # Also you can create attributes to autodescribe groups or datasets
        f['amplitudes/'].attrs['info'] = 'spike amplitudes'
        f['duration'].attrs['info'] = 'total duration of record'
