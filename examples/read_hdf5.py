"""Example to read a hdf5 file with h5py.

Hdf5 has a heralchical structure similar to a file system on
linux or mac, where folders are groups and files are datasets.

/                     root group (root folder)
|--spiketimes/        a group (a folder)
   |--temp_0          a dataset (a file)
|--/amplitudes/
   |--temp_0
   |--temp_1
|--duration

Hdf5 groups can be manage similar to a dict on python, 'asi' you
can get a spiketimes group
  - hdf_object['/spiketimes/']
  - hdf_object['/spiketimes']
  - hdf_object['spiketimes']
To get a dataset you can concatenate full path o a relative path:
  - hdf_object['/spiketimes/temp_0']
  - hdf_object['/spiketimes']['temp_0']
Datasets have similar attributes to a np.narray, as shape, size,
dtype, and also you can do slicing to retrive a subset of value
like dataset[start:step:end]. to retrive the complete dataset to
a np.narray you should use ellipsis dataset[...]
"""
import h5py


file_path = 'data/example.result.hdf5'

# Context manager
with h5py.File(file_path) as sorting_file:
    # Print all groups and dataset on root group
    print([key for key in sorting_file])

    # Print all groups and dataset on spiketmes groups
    spk_group = '/spiketimes/'
    print([key for key in sorting_file[spk_group]])

    # Retrive first 10 spiketimes
    first_10 = sorting_file[spk_group+'temp_0'][:10]
    print(first_10)

    # Retrive all spiketimes
    all_spkts = sorting_file[spk_group+'temp_0'][...]
    print(all_spkts)
