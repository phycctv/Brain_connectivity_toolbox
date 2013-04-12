%-----------------------------------------------------------------------
% Job configuration created by cfg_util (rev $Rev: 3599 $)
%-----------------------------------------------------------------------
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields = '<UNDEFINED>';
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields.tname = 'Flow fields';
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields.tgt_spec{1}.name = 'filter';
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields.tgt_spec{1}.value = 'nifti';
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields.sname = 'Run DARTEL (existing Templates): Flow Fields';
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields.src_exbranch = substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1});
matlabbatch{1}.spm.tools.dartel.crt_iwarped.flowfields.src_output = substruct('.','files', '()',{':'});
matlabbatch{1}.spm.tools.dartel.crt_iwarped.images = {'<UNDEFINED>'}; %%%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'ROI_MNI_V4.nii')};
matlabbatch{1}.spm.tools.dartel.crt_iwarped.K = 6;
matlabbatch{1}.spm.tools.dartel.crt_iwarped.interp = 0;%% Nearest neighbours

% depuis New Segmentation and DARTEL : 
    % création de wROI_MNI_V4_u_rc1*.nii    (espace MNI)
    % à partir de :
    %       - u_rc1*.nii                    (espace MNI)
    %       - ROI_MNI_V4*.nii               (espace template 90 régions)
    
% depuis Finergrid :
    % création de wTemplate_u_rc1*.nii      (espace MNI)
    % à partir de :
    %       - u_rc1*.nii                    (espace MNI)
    %       - toolbox/Atlas/Template.nii    (espace template 470 régions)
   