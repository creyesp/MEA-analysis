import numpy as np

from spikelib import spiketools as spkt
from spikelib.utils import check_groups


def get_flash_response(spks, panalysis, protocol_name, nd, intensity, extra,
                       event_list, psth_bin, bandwidth_fit,
                       fit_resolution, sr=20000.0, offset_time = 0.0):
    """Compute from spiketime psht and estimated FR.
    
    Parameters
    ----------
    spks: h5py.Group
    panalysis: h5py.Group
    nd: str
    intensity: int
    extra: str
    event_list: str
    prefix: str
    intensity: str
    psth_bin: flaot
    bandwidth_fit: float
    fit_resolution: float
    sr: float, defaul 20000.0
    offset_time: float, default 0.0

    """
    fields_df = ['start_event', 'end_event', 'start_next_event']
    filter_flash = ((event_list['protocol_name'] == protocol_name)
                    & (event_list['nd'] == nd)
                    & (event_list['intensity'] == intensity)
                    & (event_list['extra_desciption'].isin([extra]))
                    )
    if not filter_flash.any():
        return

    bound_time = np.array(event_list[filter_flash][fields_df])/sr
    # Stimulius time
    (on_dur, off_dur) = np.median(np.diff(bound_time,axis=1), axis=0) # Seconds
    start_on = offset_time
    end_on = offset_time + on_dur
    start_off = offset_time + on_dur
    end_off = offset_time + off_dur + on_dur
    total_dur = off_dur + on_dur
    (start_trials, end_trials) = bound_time[:,[0,2]].T
    ntrails = len(start_trials)
    bins_fit = np.linspace(start_on, end_off,
                            int(np.ceil(total_dur/fit_resolution))
                           )
    bins_psth = np.linspace(start_on, end_off,
                            int(np.ceil(total_dur/psth_bin))
                           )
    # Name of group in HDF5 file
    fields = dict(protocol=protocol_name, nd=nd, intensity=int(intensity),
                 extra=extra)

    base_group = '/{protocol}/{nd}/{intensity:03d}_{extra}/'.format(**fields)
    intensityg = base_group
    est_respg = '{}est_psth/'.format(base_group)
    psth_respg = '{}psth/'.format(base_group)

    check_groups(panalysis, [est_respg, psth_respg])
    for key in spks['/spiketimes/']:
        spikes = spks['/spiketimes/'+key][...]/sr
        trials_flash = spkt.get_trials(spikes, start_trials, end_trials,
                                        offset=offset_time)
        spks_flash = spkt.flatten_trials(trials_flash)

        # Response
        (psth, _) = np.histogram(spks_flash, bins=bins_psth)
        psth = psth/float(ntrails)
        est_resp = spkt.est_pdf(trials_flash, bins_fit, bandwidth=bandwidth_fit,
                                 norm_factor=psth.max())

        if key in panalysis[est_respg]:
            panalysis[est_respg+key][...] = est_resp
        else:
            panalysis[est_respg].create_dataset(key, data=est_resp, dtype=np.float, compression='gzip')

        if key in panalysis[psth_respg]:
            panalysis[psth_respg+key][...] = psth
        else:
            panalysis[psth_respg].create_dataset(key, data=psth, dtype=np.float, compression='gzip')

    panalysis[intensityg].attrs['bounds'] = (start_on, end_on, start_off, end_off)
    panalysis[psth_respg].attrs['bins'] = bins_psth
    panalysis[est_respg].attrs['time'] = bins_fit
    panalysis[est_respg].attrs['bounds'] = (start_on, end_on, start_off, end_off)
    panalysis[est_respg].attrs['bounds_name'] = u'start_on,end_on,start_off,end_off'
    
    
def get_flash_features(panalysis, protocol_name, nd, intensity, extra,
                       kwargs_fit, kind='estimated'):
    """Compute a set of feature from estimated psth
    
    Parametes
    ---------
    panalysis: h5py.Group
    prefix: str
    intensity: int
    kind: str
        Source to get flash features
    """
    # Name of group in HDF5 file
    fields = dict(protocol=protocol_name, nd=nd, intensity=int(intensity),
                 extra=extra)
    base_group = '/{protocol}/{nd}/{intensity:03d}_{extra}/'.format(**fields)

    intensityg = base_group
    est_respg = '{}est_psth/'.format(base_group)
    psth_respg = '{}psth/'.format(base_group)
    type_respg = '{}type/'.format(base_group)
    char_respg = '{}char/'.format(base_group)

    check_groups(panalysis, [est_respg, psth_respg, type_respg, char_respg])

    for key in panalysis[est_respg]:
        # TODO: add a if clause to select source from estimated or psth
        est_resp = panalysis[est_respg + key]
        est_time = panalysis[est_respg].attrs['time']
        bounds = panalysis[est_respg].attrs['bounds']
        type_fit, char_fit = spkt.get_features_flash(est_resp, est_time, bounds, **kwargs_fit)

        if key in panalysis[char_respg]:
            panalysis[char_respg+key][...] = char_fit
        else:
            panalysis[char_respg].create_dataset(key, data=char_fit, dtype=np.float, compression='gzip')

        if key in panalysis[type_respg]:
            panalysis[type_respg+key][...] = type_fit
        else:
            panalysis[type_respg].create_dataset(key, data=type_fit, dtype=np.int)        

        col_name = (u'latency_on,latency_off,bias_idx,decay_on,decay_off,'
                    u'resp_index_on,resp_index_off,sust_index_on,sust_index_off,'
                    u'frmax_on,frmax_off')
        panalysis[char_respg].attrs['col_name'] = col_name
        panalysis[type_respg].attrs['type_name'] = u'null:0,on:1,off:2,onoff:3'
        panalysis[char_respg].attrs['kwargs'] = str(kwargs_fit)  