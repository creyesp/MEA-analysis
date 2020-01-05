# Install
## Prerequisits
Python 3.5+ or [Anaconda3](https://www.anaconda.com/distribution/)    

For windows download and install Visual c++ https://visualstudio.microsoft.com/downloads/

## Create environments and install packages
A good practice is creates a virtual environment with conda (or virtualenv) because create a isolated python environment.

```batch
$ conda install nb_conda nb_conda_kernels ipywidgets widgetsnbextension
$ conda env create -f conda_environment.yml
$ conda activate spklib # if you have problems with it, try windows: activate spklib linux: source activate spklib
```
or use virtualenv
```buildoutcfg
$ virtualenv --python=python3.7 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install -r requirements_git.txt
```

## Download external library to load mcd files
To read mcd files spikelib package use neuroshare package to do it. So you need download the correct .dll (windows) or .so (linux) file. For more details about neuroshare see https://pythonhosted.org/neuroshare/

Download neuroshare lib from https://www.multichannelsystems.com/software/neuroshare-library

For Linux:
```batch
$ tar xvzf nsMCDLibrary_Linux64_3.7b.tar.gz
$ cp nsMCDLibrary/* ~/.neuroshare/
```

For Windows:
```
1) UNCOMPRESS nsMCDLibrary_3.7b.zip file 
2) COPY nsMCDLibrary_3.7b\Matlab\Matlab-Import-Filter\Matlab_Interface\nsMCDLibrary64.dll
3) PASTE TO your_path\Anaconda3\envs\spklib\DLLs\nsMCDLibrary64.dll
4) RENAME nsMCDLibrary64.dll TO nsMCDLibrary.dll 
```

## Activate nb extensions (optional)
- Table of Contents
- Variable inspector
- Notify
- Highlight selected word
- Codefolding in Editor
- table_beautiflier
- highligther
- Codefolding
