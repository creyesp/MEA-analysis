from configparser import ConfigParser, ExtendedInterpolation

import h5py
import numpy as np
import pandas as pd

from spikelib import models
from spikelib.spiketools import chunk_spikes
from spikelib.utils import check_groups

if __name__ == '__main__':
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read('../config.ini')

    exp_name = config['EXP']['name']
    stim_file = config['FILES']['wn_stim']
    sorting_file = config['FILES']['sorting']
    events_file = config['SYNC']['events']
    frametime_file = config['SYNC']['frametime']
    output_file = config['FILES']['processed']

    # Parameters
    nsamples_before = int(config['CHECKERBOAR']['nsamples_before'])
    nsamples_after = int(config['CHECKERBOAR']['nsamples_after'])
    fps = float(config['CHECKERBOAR']['fps'])
    protocol_name = config['CHECKERBOAR']['protocol_name']
    step = (np.arange(-nsamples_before, nsamples_after) + 1) / fps

    frametimes = np.loadtxt(frametime_file).T
    df = pd.read_csv(events_file)
    checkerboard_times = df[df['protocol_name'] == protocol_name]

    for event in checkerboard_times.itertuples():
        # Sync
        start_stim = event.start_event
        end_stim = event.end_event
        name = '{}-{}'.format(event.nd, int(event.intensity))

        print('Computing whitenoise: {}'.format(name))
        start_frames = frametimes[0, np.logical_and(frametimes[0] >= start_stim, frametimes[0] < end_stim)]

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

        with h5py.File(output_file, 'a') as fsta:
            group_name = '/sta/{}/raw/'.format(name)
            check_groups(fsta, [group_name])

            for (key, ksta) in result:
                dataset = group_name + '/{}'.format(key)
                if key in fsta[group_name]:
                    fsta[group_name + key][...] = ksta
                else:
                    fsta[group_name].create_dataset(key, data=ksta, dtype=np.float,
                                                    compression="gzip")

            fsta[group_name].attrs['fps'] = fps
            fsta[group_name].attrs['nsamples_before'] = nsamples_before
            fsta[group_name].attrs['nsamples_after'] = nsamples_after
            fsta[group_name].attrs['nsamples'] = nsamples_before + nsamples_after
            time_sta = (np.arange(-nsamples_before, nsamples_after) + 1) / fps
            fsta[group_name].attrs['time'] = time_sta
