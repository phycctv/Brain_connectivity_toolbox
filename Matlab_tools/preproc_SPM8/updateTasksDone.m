function updateTasksDone(tasks,jobFolder)

% Load or create file tasksDone.mat in jobFolder, containing information 
% about tasks of preprocess (see pp_loadVolumes_vFlore.m) that have been 
% done. Some fields of scructure tasksone are modified.
% Inputs :
%   - tasks : cell array
%       column 1 : names of the tasks that have to be modified (string). 
%                  If tasksNames = 'reset', all fields are set to
%                  0, even if column 2 = 1.
%       column 2 : value to set to the field (field name in column 1)
%                  0 tasks not done
%                  1 tasks done.
%   - jobFolder : directory to the folder of tasksdone.mat.
% Outputs : the new or modified structure tasksDone is saved in 
% jobFolder/tasksdone.mat.


if exist(fullfile(jobFolder, 'tasksDone.mat'),'file')
   load(fullfile(jobFolder, 'tasksDone.mat'))
else
    tasksDone = struct('realign',0,...
    'QC',0,...
    'coregister',0,...
    'dartel',struct('segment',0,'normalize',0,'warp',0,'iwarp',0,'coregister',0,'coregister_interp',0),...
    'finergrid',struct('iwarp',0,'coregister',0),...
    'label',0,...
    'segment',0);
end

for i = 1:size(tasks,1)
    switch tasks{i,1}
        case 'realign',             tasksDone.realign           = tasks{i,2};
        case 'QC',                  tasksDone.QC                = tasks{i,2};
%         case 'coregister',          tasksDone.coregister        = tasks{i,2};
        case 'classicSegment',      tasksDone.segment           = tasks{i,2};
        case 'newSegment',          tasksDone.segment           = tasks{i,2}*2;
        case 'dartel',              tasksDone.segment           = tasks{i,2}*3;
            tasksDone.dartel.segment    = tasks{i,2}; tasksDone.dartel.normalize  = tasks{i,2}; 
            tasksDone.dartel.warp       = tasks{i,2}; tasksDone.dartel.iwarp      = tasks{i,2};
            tasksDone.dartel.coregister = tasks{i,2}; tasksDone.dartel.coregister_interp = tasks{i,2};
        case 'segment',             tasksDone.dartel.segment    = tasks{i,2};   tasksDone.segment = tasks{i,2}*3;
        case 'normalize',           tasksDone.dartel.normalize  = tasks{i,2};
        case 'warp',                tasksDone.dartel.warp       = tasks{i,2};      
        case 'iwarp',               tasksDone.dartel.iwarp      = tasks{i,2};
        case 'coregister',          tasksDone.dartel.coregister = tasks{i,2};
        case 'coregister_interp',   tasksDone.dartel.coregister_interp = tasks{i,2};
        case 'finergrid',           tasksDone.finergrid.iwarp   = tasks{i,2};   tasksDone.finergrid.coregister = tasks{i,2};
        case 'iwarp,finergrid',     tasksDone.finergrid.iwarp   = tasks{i,2};
        case 'coregister,finergrid',tasksDone.finergrid.coregister = tasks{i,2};
        case 'label',               tasksDone.label             = tasks{i,2};
        case 'reset'
            tasksDone = struct('realign',0,...
    'QC',0,...
    'coregister',0,...
    'dartel',struct('segment',0,'normalize',0,'warp',0,'iwarp',0,'coregister',0,'coregister_interp',0),...
    'finergrid',struct('iwarp',0,'coregister',0),...
    'label',0,...
    'segment',0);
    end
end

save(fullfile(jobFolder, 'tasksDone.mat'), 'tasksDone');