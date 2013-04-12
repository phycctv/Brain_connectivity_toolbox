%-----------------------------------------------------------------------
% Job configuration created by cfg_util (rev $Rev: 3599 $)
%-----------------------------------------------------------------------
matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields = '<UNDEFINED>';
matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields.tname = 'Flow fields';
matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields.tgt_spec.name = 'filter';
matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields.tgt_spec.value = 'nifti';
matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields.sname = 'Run DARTEL (existing Templates): Flow Fields';
%%%matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields.src_exbranch = substruct('.','val', '{}',{2}, '.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1});
%%%matlabbatch{1}.spm.tools.dartel.crt_warped.flowfields.src_output = substruct('.','files', '()',{':'});
matlabbatch{1}.spm.tools.dartel.crt_warped.images = {'<UNDEFINED>'};
matlabbatch{1}.spm.tools.dartel.crt_warped.jactransf = 0;
matlabbatch{1}.spm.tools.dartel.crt_warped.K = 6;
matlabbatch{1}.spm.tools.dartel.crt_warped.interp = 4;

% création de w*.nii    (espace MIN)
% à partir de :
%       - *.nii         (espace anatomique)
%       - u_rc1*.nii    (espace MNI)

