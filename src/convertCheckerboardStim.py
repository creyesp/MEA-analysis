import sys

from mealib.utils import checkDirectory
from mealib.preprocessing import correct_checkerboard

exp_name = 'MR-0227'
checkerboar_file = '028.txt'
mat_version = 'v7.3'

stim_file = '../data/stim/checkerboard/stim_mini_' + exp_name + '.mat'
sync_file = '../data/sync/' + exp_name + '/event_list/' + checkerboar_file
repeated_file = '../data/sync/' + exp_name + '/repeated_frames_' + \
                exp_name + '.txt'
outputfolder = '../data/stim/checkerboard/'
checkDirectory(outputfolder)
outputfile = outputfolder+'stim_mini_' + exp_name + '_.hdf5'

correct_checkerboard(sync_file, repeated_file, outputfile, stim_file)
