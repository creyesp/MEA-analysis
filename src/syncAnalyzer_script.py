r"""
A simple script to read a mcd from MEA record and get the
sincronization times for each displayed frame on projector. This script
create 4 txt file with different information about the synchronization.

Returns
-------

Save 4 file in output_folder

start_end_frames : narray
    narray with the start and end point of each frame showed.
repeted_frames : narray
    narray with start of repeated frame.
total_duration : int
    total number of points in the record
event_list : DataFrame
    list of events in start_end_frames
"""


import argparse

from mealib.preprocessing import Sync
from mealib.utils import checkDirectory


def get_sync(exp_name, real_fps, mcd_file, mcd_channel, output_folder):
    """Execute the normal rutine to get the syncronization"""
    sync_data = Sync(exp_name, real_fps)
    sync_data.read_mcd(mcd_file)
    sync_data.show_entities()

    sync_data.analyzer(mcd_channel)

    sync_data.create_events()
    sync_data.add_repeated()

    sync_data.save_analyzed(output_folder)
    sync_data.save_events(output_folder)
    sync_data.close_file()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    parser.add_argument(
        "mcdfile", type=str,
        help='MCD file path with the analog signal ',
        )
    parser.add_argument(
        "expname", type=str,
        help='Name of the output file',
        )
    parser.add_argument(
        'fps', type=float,
        help='Real fps used by projector. Check inthe log file of experiment',
        )
    parser.add_argument(
        '-c', dest='mcd_channel', type=int, default=0,
        help='Number of the analog channel in MCD file. Default 0',
        )
    parser.add_argument(
        '-o', dest='output_folder', type=str, default='',
        help='Directory path to save files. Default ./',
        )
    args = parser.parse_args()

    if args.output_folder[-1] == '/':
        output_folder = args.output_folder + args.expname+'/'
    else:
        output_folder = args.output_folder + '/' + args.expname+'/'

    checkDirectory(output_folder)

    get_sync(args.expname, args.fps, args.mcdfile, args.mcd_channel,
             output_folder)


if __name__ == "__main__":
    main()
