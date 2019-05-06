
import h5py
import numpy as np

sr=20000
thr = 0.0005*sr

src_file = '../data/sorting/MR-0092t2.result-1_bkp.hdf5'
dst_file = '../data/sorting/MR-0092t2.result-1_bkp_modified.hdf5'

with h5py.File(src_file, 'r') as f_src, h5py.File(dst_file, 'w') as f_dst :
    f_dst.create_group('/spiketimes/')
    f_dst.create_group('/amplitudes/')
    f_dst.create_group('/info/')
    for key in f_src['spiketimes/']:
        spk = f_src['spiketimes/'+key][...]
        amp = f_src['amplitudes/'+key][...]
        duplicates = np.where(np.diff(spk[:,0]) < thr)[0]
        min_amp = np.where(
            amp[duplicates,0] < amp[duplicates+1,0],
            duplicates,
            duplicates+1,
        )
        if min_amp.any():
            filter_valid = ~np.isin(np.arange(0, spk.shape[0], dtype=int), min_amp)
        else:
            filter_valid = np.full(spk.shape[0], True, )
        f_dst['/spiketimes/'].create_dataset(name=key, data=spk[filter_valid]) 
        f_dst['/amplitudes/'].create_dataset(name=key, data=amp[filter_valid]) 
    f_dst['/info/'].create_dataset(name='duration', data=f_src['info/duration'])
