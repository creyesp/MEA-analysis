"""Script to get information about synchronization.

A simple script to read a mcd file from MEA record and get the
sincronization times for each displayed frame on projector. This script
create 4 txt file with different information about the synchronization.

Parameters
----------

mcdFile : str
    path to .mcd file
expName : str
    Name of experiment
mcdChannel : int
    number of channel where is the analog signal
    in .mcd file
realFps: float
    real fps used for projector. Look at the log file
    and check this number. Ex. 59.7694
outputFolder : str
    directory path to save files


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


Examples
--------

python syncAnalyzer_script.py \
 --mcdFile ../data/raw_data/2016-04-11/2016-04-11_analog.mcd \
 --expName '2016-04-11' \
 --mcdChannel 0 \
 --outputFolder ../data/sync/2016-04-11/ \
 --realFps 59.7596
"""
import argparse
from pathlib import Path

from mealib.preprocessing import Sync
from mealib.utils import checkDirectory


parser = argparse.ArgumentParser(
    prog='syncAnalyaer_script.py',
    description='''A simple script to read a mcd from MEA record and
            get the sincronization times for each displayed frame on
            projector. This script create 4 txt file with different
            information about the synchronization.''',
    epilog="""example:
            python syncAnalyzer_script.py
            --mcdFile ../data/raw_data/2016-04-11/2016-04-11_analog.mcd
            --expName '2016-04-11'
            --mcdChannel 0
            --outputFolder ../data/sync/
            --realFps 59.7596
           """,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--mcdFile', help='MCD file path with the analog signal ',
                    type=str, required=True)
parser.add_argument('--expName', help='Name of the output file',
                    type=str, required=True)
parser.add_argument('--mcdChannel', help='Number of the analog channel in MCD\
                    file to recovery synchronization signal', type=int,
                    default=0)
parser.add_argument('--realFps', help='Real fps used by projector. Check in\
                    the log file of experiment', type=float, required=True)
parser.add_argument('--outputFolder', help='Output folder',
                    type=str, default='')

args = parser.parse_args()

if args.outputFolder[-1] == '/':
    output_folder = args.outputFolder+args.expName+'/'
else:
    output_folder = args.outputFolder+'/'+args.expName+'/'
checkDirectory(output_folder)

sync_data = Sync(args.expName, args.realFps)
sync_data.read_mcd(args.mcdFile)
sync_data.showEntities()

sync_data.analyzer(args.mcdChannel)

sync_data.create_events()
sync_data.add_repeated()

sync_data.save_analyzed(output_folder)
sync_data.save_events(output_folder)
sync_data.close_file()
