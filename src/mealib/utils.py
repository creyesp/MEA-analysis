import os
import sys


def cleanDirectory(inputfolder):
    """Delete all files and drectories in input directory.

    If the directory doesn't exist then this directory is create.

    Parameters
    ----------
    inputfolder: str
        path of directory

    Example
    ----------
        checkDirectory('../myinputfolder')
    """
    if not os.path.exists(inputfolder):
        try:
            os.makedirs(inputfolder)
        except:
            print('Unable to create folder ' + inputfolder)
            sys.exit()
    else:
        if os.listdir(inputfolder) != []:
            for files in os.listdir(inputfolder):
                os.remove(inputfolder+files)

def checkDirectory(inputfolder):
    """Check if exist the directory, else make a new folder.

    If the directory doesn't exist then this directory is create.

    Parameters
    ----------
    inputfolder: srt
        path of directory

    Example
    ----------
        checkDirectory('../myFolder')
    """
    if not os.path.exists(inputfolder):
        try:
            os.makedirs(inputfolder)
        except:
            print('Unable to create folder ' + inputfolder)
            sys.exit()
