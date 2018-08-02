%% Exploratory Data Analysis for structured HDF5 files 
%
% This script show you How to access HDF5 data from Matlab.
%
% In this case we going to use a structured HDF5 file to access 
% to timestamps for an experiment. We going to explore Groups, 
% Attributes and Dataset in the file and also we going to look at 
% three examples to plot data.
%


%% Load information about hdf5 file
% h5info function get all information about file in a structure.
% Also We can see this information in the workspace in data_info

addpath('../src/')
filename = '../data/structured_data/structured_data_2018-01-25.hdf5';
data_info = h5info(filename);

%% Groups
% We can get information about the  groups using a local function printInfo().
% This function show names of groups, number of subgroups and number of
% attributes

printInfo(data_info.Groups)
%% Groups in '/response'
% data_info variable has two principal groups, '/response' and '/stimulus'. 
% now we can check the groups in '/response'. 

response_group = data_info.Groups(1);
printInfo(response_group.Groups)


%% Dataset
% A dataset is similar to an Array and you can use 'slicing', and or steps. 
% 
% For example we can get infromation about dataset in checkerboard
n_protocol = 1

protocol_group  = response_group.Groups(n_protocol);
dataset = protocol_group.Datasets;

disp(protocol_group.Name)
printInfo(protocol_group)

for k = 1:10
    unit = dataset(k);
    unit_name = unit.Name;
    unit_nspikes = unit.Dataspace.Size;
    disp(['Name: ',unit_name,'   #spikes: ',int2str(unit_nspikes)])
end


%% Attributes
% Attributes describe Groups and Dataset and we can get a description about 
% our data.  
%
% We can select one of groups in response_group and for example,
% look at the attributes of checkerboard.
n_protocol = 1

protocol_group  = response_group.Groups(n_protocol);
protocol_attrs = protocol_group.Attributes;
disp(protocol_group.Name)

for k= 1:length(protocol_attrs)
    disp([protocol_attrs(k).Name,' : ',int2str(protocol_attrs(k).Value)])
end


%% Load Data 
% h5read function read directly dataset in a file. This function need 
% two arguments, filename, and datasetname and optionally we can use slice 
% and stride.
%
% h5read(filename,datasetname,start,count,stride)


% To get the first 10 spike for temp_1 in checkerboard:
temp_dataset = h5read(filename,'/response/checkerboard/temp_1',1,10);
temp_dataset
% To get the first 5 spike for temp_1 in checkerboard:
temp_dataset = h5read(filename,'/response/checkerboard/temp_1',1,5,2);
temp_dataset

%% Example protocol with repetitions
% Plot raster for a single unit

n_protocol = 2;
n_unit = 125;

response_group = data_info.Groups(1);
protocol_group  = response_group.Groups(n_protocol);
protocol_attrs = protocol_group.Attributes;
protocol_duration = protocol_group.Attributes(4).Value;
sample = protocol_group.Attributes(3).Value;

unit = protocol_group.Groups(n_unit);
dataset_unit = unit.Datasets;

figure()
for ktrial=1:length( dataset_unit )
    name_trial = [ unit.Name , '/' , dataset_unit(ktrial).Name ];
    hdf_data = h5read( filename , name_trial ) / sample;
    
    plot( hdf_data , ktrial*ones(length(hdf_data),1) , '.')
    hold on
end
title(unit.Name)
xlim([-1,protocol_duration+1])
ylim([0,length( dataset_unit )+1])
xlabel('Time [s]')
ylabel('Trials')

%% Plot psth for a single unit
figure()
hdf_data = 0;
for ktrial=1:length( dataset_unit)
    name_trial = [ unit.Name , '/' , dataset_unit(ktrial).Name ];
    hdf_data = [ hdf_data ; h5read(filename,name_trial)/sample ];
end
edges = [0:0.02:protocol_duration];
h = histogram(hdf_data,edges);
xlim([-1,protocol_duration+1])
title(unit.Name)
xlabel('Time [s]')
ylabel('Trials')


%% Response and stimulus together
% Example Chirp protocol

n_protocol = 2;
n_unit = 221;

stim = h5read(filename,'/stimulus/chirp');
stim_amp = stim(:,1)/255.0;
stim_time = stim(:,2);

response_group = data_info.Groups(1);
protocol_group  = response_group.Groups(n_protocol);
protocol_attrs = protocol_group.Attributes;
protocol_dureation = protocol_group.Attributes(4).Value;
sample = protocol_group.Attributes(3).Value;

unit = protocol_group.Groups(n_unit);
dataset_unit = unit.Datasets;


hdf_data = 0;
for ktrial=1:length( dataset_unit)
    name_trial = [ unit.Name , '/' , dataset_unit(ktrial).Name ];
    hdf_data = [ hdf_data ; h5read(filename,name_trial)/sample ];
end

figure()
edges = [0:0.02:protocol_dureation];
h = histogram(hdf_data,edges);
hold on
plot(stim_time,stim_amp*max(h.BinCounts)/2)
title(unit.Name)
xlim([-1,protocol_duration+1])
xlabel('Time [s]')
ylabel('Firing rate')
legend('Response','Stimulus')
