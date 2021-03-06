% Helper script for preprocess.m - in charge of loading data
%% initialize
pp_defineConstants;
[volExt,chain,QCcoef, highpass]=process_options(varargin,'volExt','nii',...
   'procChain',{'realign','QC','coregister','newSegment','label',...
   'segment','normalize','warp','iwarp','new_auto_labelling'},...
   'QCcoef', 1.5, 'highpass', 0);

%% set folders
segFolder = fullfile(structPath,'Segmented');
normFolder = fullfile(structPath,'Normalized');
atlasFolder = fullfile(structPath,'Atlased');
alignFolder = fullfile(functPath,'Realigned');  % majuscule
QCFolder = fullfile(functPath,'QC');


% Jobs au lieu de jobs
minLength = min(size(structPath,2),size(functPath,2));
if exist(structPath,'dir') && ~exist(functPath,'dir'), jobFolder = fullfile(structPath,'Jobs');
elseif ~exist(structPath,'dir') && exist(functPath,'dir'), jobFolder = fullfile(functPath,'Jobs');
elseif exist(structPath,'dir') && exist(functPath,'dir')
    if strcmp(structPath, functPath), jobFolder = fullfile(functPath,'Jobs');
    else jobFolder = fullfile(fileparts(structPath(1:find(structPath(1:minLength) ~= functPath(1:minLength), 1 ))),'Jobs');
    end
else error('Functional and structural pathes do not exist.');
end
if ~exist(jobFolder,'dir'), mkdir(jobFolder); end;

%% save chain to the struct tasksTodo and check arguments
tasksTodo = struct('realign',0,...
    'QC',0,...
    'coregister',0,...
    'dartel',struct('segment',0,'normalize',0,'warp',0,'iwarp',0,'coregister',0,'coregister_interp',0),...
    'finergrid',struct('iwarp',0,'coregister',0),...
    'label',0,...
    'segment',0);

% liste des noms-clefs possibles:
% realign
% QC
% classicSegment
% newSegment
% dartel            => segment + normalize + warp + iwarp + coregister
% finergrid         => iwarp + coregister
% label
% segment
% normalize
% warp
% iwarp
% coregister
% coregister_interp
% iwarp,finergrid
% coregister,finregrid

for procElem = chain
    
    switch procElem{1}
        case 'realign'
            tasksTodo.realign = 1;
        case 'QC'
            tasksTodo.QC = 1;
        %case 'coregister'      % conflit avec new_segment, coregister
        %    tasksTodo.coregister = 1;
        case 'classicSegment'
            if tasksTodo.segment == 0
                tasksTodo.segment = CLASSICSEGMENT;
            else
                error('There must not be more than one segmentation method.');
            end
        case 'newSegment'
            if tasksTodo.segment == 0
                tasksTodo.segment = NEWSEGMENT;
            else
                error('There must not be more than one segmentation method.')
            end
        case 'dartel'
            if tasksTodo.segment == 0
                tasksTodo.segment = DARTEL;
                tasksTodo.dartel.segment = 1;
                tasksTodo.dartel.normalize = 1;
                tasksTodo.dartel.warp = 1;
                tasksTodo.dartel.iwarp = 1;
                tasksTodo.dartel.coregister = 1;
                tasksTodo.dartel.coregister_interp = 1;
            else
                error('There must not be more than one segmentation method.')
            end
        case 'finergrid'
            tasksTodo.finergrid.iwarp = 1;
            tasksTodo.finergrid.coregister = 1;
        case 'label'
            tasksTodo.label = 1;
        case 'segment'
            tasksTodo.segment = DARTEL;
            tasksTodo.dartel.segment = 1;
        case 'normalize'
            tasksTodo.segment = DARTEL;
            tasksTodo.dartel.normalize = 1;
        case 'warp'
            tasksTodo.segment = DARTEL;
            tasksTodo.dartel.warp = 1;
        case 'iwarp'
            tasksTodo.segment = DARTEL;
            tasksTodo.dartel.iwarp = 1;
        case 'coregister'
            tasksTodo.segment = DARTEL;
            tasksTodo.dartel.coregister = 1;
        case 'coregister_interp'
            tasksTodo.segment = DARTEL;
            tasksTodo.dartel.coregister_interp = 1;
        case 'iwarp,finergrid'
            tasksTodo.finergrid.iwarp = 1;
        case 'coregister,finergrid'
            tasksTodo.finergrid.coregister = 1;
            
        otherwise
            %error(['processing command "' procElem{1} '" does not exist']);
            disp(['processing command "' procElem{1} '" does not exist']);
    end
end

if exist(fullfile(jobFolder, 'tasksDone.mat'),'file')
   load(fullfile(jobFolder, 'tasksDone.mat'))
   disp(['dartel, warp done ',int2str(tasksDone.dartel.warp)])
else
  tasksDone = struct('realign',0,...
    'QC',0,...
    'coregister',0,...
    'dartel',struct('segment',0,'normalize',0,'warp',0,'iwarp',0,'coregister',0,'coregister_interp',0),...
    'finergrid',struct('iwarp',0,'coregister',0),...
    'label',0,...
    'segment',0);
end

if tasksDone.realign,                   tasksTodo.realign = 0; end
if isfield(tasksDone, 'QC') && tasksDone.QC, tasksTodo.QC = 0; end
%if tasksDone.coregister, tasksTodo.coregister = 0; end
if (tasksTodo.segment && tasksDone.segment)
   if tasksDone.segment == tasksTodo.segment
       %tasksTodo.segment = 0;
   else
       error('A different segmentation method has already been applied.')
   end
end
if tasksDone.dartel.segment,            tasksTodo.dartel.segment=0; end
if tasksDone.dartel.normalize,          tasksTodo.dartel.normalize=0; end
if tasksDone.dartel.warp,               tasksTodo.dartel.warp=0; end
if tasksDone.dartel.iwarp,              tasksTodo.dartel.iwarp=0; end
if tasksDone.dartel.coregister,         tasksTodo.dartel.coregister=0; end
if tasksDone.dartel.coregister_interp,  tasksTodo.dartel.coregister_interp=0; end
if tasksDone.finergrid.iwarp,           tasksTodo.finergrid.iwarp=0; end
if ~tasksTodo.dartel.segment && ~tasksTodo.dartel.normalize && ~tasksTodo.dartel.warp &&...
        ~tasksTodo.dartel.iwarp && ~tasksTodo.dartel.coregister && ~tasksTodo.dartel.coregister_interp
    tasksTodo.segment = 0;
end
if tasksDone.finergrid.coregister,      tasksTodo.finergrid.coregister=0; end
if tasksDone.label,                     tasksTodo.label = 0; end

%% arguments sanity check
if (length(volExt)~=3)
    error('Volume filename extension must be 3 characters long');
end
if (tasksTodo.label && ~tasksTodo.segment && ~tasksDone.segment)
   error('Before labelling volume must be segmented. Add "newSegment", "classicSegment", "dartel" or "segment" to your processing chain.');
end
if (tasksTodo.coregister && ~tasksTodo.realign && ~tasksDone.realign)
   error('Before coregistering functional volumes must be realigned. Add "realign" to your processing chain.');
end
if (tasksTodo.QC && ~tasksTodo.realign && ~tasksDone.realign)
   error('Before quality control functional volumes must be realigned. Add "realign" to your processing chain.');
end
%if (tasksTodo.warp && ~tasksTodo.realign && ~tasksDone.realign && ~(tasksDone.segment==DARTEL))
%   error('For doing warp, dartel should have been run first. Add "dartel" to your processing chain.');
%end
if (tasksTodo.dartel.normalize && ~tasksTodo.dartel.segment && ~tasksDone.dartel.segment)
    error('Before normalization in dartel, volume must be segmented. Add "dartel" or "segment" to your processing chain.')
end
if (tasksTodo.dartel.warp && ~tasksTodo.dartel.normalize && ~tasksDone.dartel.normalize)
    error('Before warping in dartel, volume must be normalized. Add "dartel" or "normalize" to your processing chain.')
end
if (tasksTodo.dartel.iwarp && ~tasksTodo.dartel.normalize && ~tasksDone.dartel.normalize)
    error('Before inverse warping in dartel, volume must be normalized. Add "dartel" or "normalize" to your processing chain.')
end
if (tasksTodo.dartel.coregister && (~tasksTodo.dartel.iwarp && ~tasksDone.dartel.iwarp) || (~tasksTodo.realign && ~tasksDone.realign))
    error('Before coregistering in dartel, structural volume must be normalized and functional volumes must be realigned. Add "realign","dartel" or "realign","iwarp" to your processing chain.')
end
if (tasksTodo.dartel.coregister_interp && (~tasksTodo.dartel.iwarp && ~tasksDone.dartel.iwarp) || (~tasksTodo.realign && ~tasksDone.realign))
    error('Before coregistering in dartel, structural volume must be normalized and functional volumes must be realigned. Add "realign","dartel" or "realign","iwarp" to your processing chain.')
end
if (tasksTodo.finergrid.iwarp && ~tasksTodo.dartel.normalize && ~tasksDone.dartel.normalize)
    error('Before inverse warping in finregrid, volume must be normalized and warped. Add "dartel" or "normalize" to your processing chain.')
end
if (tasksTodo.finergrid.coregister && (~tasksTodo.finergrid.iwarp && ~tasksDone.finergrid.iwarp) || (~tasksTodo.realign && ~tasksDone.realign))
    error('Before coregistering in finergrid, structural volume must be normalized and functional volumes must be realigned. Add "realign","finergrid" or "realign","iwarp,finergrid" to your processing chain.')
end   

%% check if files are compressed
% functPathOrigin au lieu de functPath
% structPathOrigin au lieu de structPath

%--------- structural files ---------------------------
niiDirs = dir(fullfile(structPathOrigin,['*.',volExt]));
gzDirs = dir(fullfile(structPathOrigin,'*.gz'));

if size(gzDirs,1) && ~size(niiDirs,1)
    gzStructFile = fullfile(structPathOrigin, gzDirs(1).name);
    gunzip(gzStructFile);
    
    vol = spm_vol(gzStructFile(1:end-3));
    vol.mat(:,4) = [130 -130 -60 1];
    
    spm_write_vol(vol, spm_read_vols(vol));
end

%--------- functional files ---------------------------
niiDirs = dir(fullfile(functPathOrigin,['*.',volExt]));
gzDirs = dir(fullfile(functPathOrigin,'*.gz'));

if size(gzDirs,1) && ~size(niiDirs,1)
    gzFunctFile = fullfile(functPathOrigin, gzDirs(1).name);
    gunzip(gzFunctFile);
end

%% check if 4d nii file
% � adapter aux nouveaux r�pertoires?
niiDirs = dir(fullfile(functPathOrigin,['*.',volExt]));

if size(niiDirs,1) == 1
    functFile = fullfile(functPathOrigin, niiDirs(1).name);
    vols = spm_vol(functFile);
    for i = 1:size(vols,1)
        vol = vols(i);
        [path name ext] = fileparts(vol.fname);
        numberStr = ['00' int2str(i)];
        numberStr = numberStr(size(numberStr,2)-2:end);
        
        vol.mat(:,4) = [110 -110 0 1];
        
        vol.fname = fullfile(path, ['f' name numberStr ext]);   % path � v�rifier
        vol.n = [1 1];
        spm_write_vol(vol, spm_read_vols(vols(i)));
    end
end

%% select structural files
if tasksTodo.coregister || tasksTodo.segment || tasksTodo.label %|| tasksTodo.warp 
    if ~exist(structPathOrigin,'dir'), error(['Structural path does not exist: ' path_s ]); end
    
    % s�lection de tous les fichiers du r�pertoire structPathOrigin, avec
    % l'extension volExt
    structFilename = spm_select('List',structPathOrigin,['.*\.' volExt '$']); %['^[ms2].*\.' volExt '$']);
	if size(structFilename,1)~=1, error('There should be exactly 1 structural volume, check code.'); end
    structFile = fullfile(structPathOrigin, structFilename);
end

%% select functional files
if tasksTodo.realign || tasksTodo.coregister || tasksTodo.QC
    if ~exist(functPathOrigin,'dir'), error(['Functional path does not exist: ' path_f ]); end
    
    % s�lection de tous les fichiers du r�pertoire functPathOrigin, avec
    % l'extension volExt
    functFilenames = spm_select('List',functPathOrigin,['.*\.' volExt '$']); %['^2.*\.' volExt '$']); %% first letter of functional images file name
    nFiles=size(functFilenames,1);
    if nFiles==0 && (tasksTodo.realign || tasksTodo.coregister)
        error('No functional files selected');
    else
        disp(['Selected ' num2str(nFiles) ' functional volume files for processing']);
    end
    % prepend full dir;
    functFiles=cell(nFiles,1);
    for f=1:nFiles
        functFiles{f}=fullfile(functPathOrigin,functFilenames(f,:));
    end
    

end

%%
dispTasks_vFlore(tasksTodo, tasksDone);
