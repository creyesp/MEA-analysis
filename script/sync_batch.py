from spikelib.utils import check_directory
from spikelib.preprocessing import Sync

if __name__ == '__main__':

    exp = {'MR-0092t2': 0}
    real_fps = 59.75816
    
    for kexp in exp:
        source_folder = 'exp/MEA-analysis/data/raw_data/'+kexp+'/'+kexp+'_analog.mcd'
        output_folder = 'exp/MEA-analysis/data/sync/'+kexp+'/'
        output_folder_event = 'exp/MEA-analysis/data/sync/'+kexp+'/event_list/'
        mcd_channel = exp[kexp]
        check_directory(output_folder)
        check_directory(output_folder_event)

        print('\n'+kexp)
        sync_data = Sync(kexp, real_fps)
        sync_data.read_mcd(source_folder)
        sync_data.show_entities()
        sync_data.analyzer(mcd_channel)

        sync_data.create_events()
        sync_data.add_repeated()

        sync_data.save_analyzed(output_folder)
        sync_data.save_events(output_folder)
        sync_data.create_separated_sync(output_folder_event)
        sync_data.close_file()
