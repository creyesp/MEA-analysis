from configparser import ConfigParser, ExtendedInterpolation

import h5py
import numpy as np

from spikelib import models
from spikelib.spiketools import chunk_spikes
from spikelib.utils import check_groups


if __name__ == '__main__':
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read('../config.ini')

    suffixs = ['nd3-255',]

    for suffix in suffixs:
        print('Computing whitenoise: {}'.format(suffix))
        exp_name = config['EXP']['name']
        stim_file = config['FILES']['wn_stim']
        sorting_file = config['FILES']['sorting']
        stimtime_file = config['SYNC']['wn']
        output_file = config['FILES']['processed']


        # Parameters
        nsamples_before = config['CHECKERBOAR']['nsamples_before']
        nsamples_after = config['CHECKERBOAR']['nsamples_after']
        fps = config['CHECKERBOAR']['fps']
        step = (np.arange(-nsamples_before, nsamples_after)+1)/fps

        # Sync
        stimtimes = np.loadtxt(stimtime_file).T
        start_frames = stimtimes[0]
        end_frames = stimtimes[1]
        start_stim = start_frames[0]
        end_stim = end_frames[-1]

        # Spikes
        with h5py.File(sorting_file) as fspiketimes:
            spks = fspiketimes['spiketimes']
            spiketimes = []
            for key in spks:
                ts_checkerboard = chunk_spikes(spks[key][...], start_stim, end_stim)
                spiketimes.append((key, ts_checkerboard))

        result = models.run_multi_sta(stim_file, start_frames, spiketimes,
                                      nsamples_before=nsamples_before,
                                      nsamples_after=nsamples_after,
                                      normed_stim=True,
                                      channel_stim='g',
                                      )
        print('Results (pool):\n', len(result))


        if SAVE_FILE:
            with h5py.File(output_file, 'a') as fsta:
                group_name = '/sta/{}/raw/'.format(suffix)
                check_groups(fsta, [group_name])

                for (key, ksta) in result:
                    dataset = group_name+'/{}'.format(key)
                    if key in fsta[group_name]:
                        fsta[group_name+key][...] = ksta
                    else:
                        fsta[group_name].create_dataset(key, data=ksta, dtype=np.float,
                                                        compression="gzip")

                fsta[group_name].attrs['fps'] = fps
                fsta[group_name].attrs['nsamples_before'] = nsamples_before
                fsta[group_name].attrs['nsamples_after'] = nsamples_after
                fsta[group_name].attrs['nsamples'] = nsamples_before+nsamples_after
                time_sta = (np.arange(-nsamples_before, nsamples_after)+1)/fps
                fsta[group_name].attrs['time'] = time_sta
