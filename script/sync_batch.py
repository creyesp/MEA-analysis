"""Script to generate a set of sync files for a list of experiments

exps variable is a dictionary with the name of experiment as key and the
mcd channel as a value which contain the analog signal.
"""
from spikelib.utils import check_directory
from spikelib.preprocessing import Sync

if __name__ == '__main__':

    exps = {
        'MR-0000': 0, }
    real_fps = 59.75816

    base_path = 'exp/MEA-analysis/data/'
    for exp, channel in exps.items():
        source_folder = '{}raw/{}/{}_analog.mcd'.format(base_path, exp, exp)
        output_folder = '{}sync/{}/'.format(base_path, exp)
        output_folder_event = '{}sync/{}/event_list/'.format(base_path, exp)
        check_directory(output_folder)
        check_directory(output_folder_event)

        print('\n' + exp)
        sync_data = Sync(exp, real_fps)
        sync_data.read_mcd(source_folder)
        sync_data.show_entities()
        sync_data.analyzer(channel)

        sync_data.create_events()
        sync_data.add_repeated()

        sync_data.save_analyzed(output_folder)
        sync_data.save_events(output_folder)
        sync_data.create_separated_sync(output_folder_event)
        sync_data.close_file()
