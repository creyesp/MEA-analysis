# Install
## Prerequisits
For windows download and install Visual c++ https://visualstudio.microsoft.com/downloads/

## Create environments and install packages
Its necesary create 2 enviroment with conda because the module to read mcs files
only work on python2.7, for other things use python3. In the future all modules
going to work on python3.

```batch
$ conda install nb_conda nb_conda_kernels ipywidgets widgetsnbextension
$ conda create -n spklib3 python=3.6
$ python -m ipykernel install --user --name=spklib3
$ conda activate spklib3
$ conda install seaborn scipy scikit-learn pandas numpy matplotlib bokeh h5py statsmodels
$ pip install spikelib PeakUtils lmfit

$ conda create -n spklib2 python=2.7
$ python -m ipykernel install --user --name=spklib2
$ conda activate spklib2
$ conda install seabornscipy scikit-learn pandas numpy matplotlib bokeh h5py statsmodels
$ pip install numpy PeakUtils neuroshare lmfit spikelib
```

## Download external library to load mcd files
To read mcd file spikelib package use neuroshare package and its necesary
download the correct .dll or .so file. For moro details about neuroshare see https://pythonhosted.org/neuroshare/

Download neuroshare lib from https://www.multichannelsystems.com/software/neuroshare-library

For Linux:
```batch
$ tar xvzf nsMCDLibrary_Linux64_3.7b.tar.gz
$ cp nsMCDLibrary/* ~/.neuroshare/
```

For Windows:
```batch
unzip nsMCDLibrary_3.7b.zip
copy nsMCDLibrary_3.7b\Matlab\Matlab-Import-Filter\Matlab_Interface\nsMCDLibrary64.dll path_Anaconda3\envs\spklib2\DLLs\nsMCDLibrary.dll
```

## Activate nb extensions
- Table of Contents
- Variable inspector
- Notify
- Highlight selected word
- Codefolding in Editor
- table_beautiflier
- highligther
- Codefolding
