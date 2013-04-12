%-----------------------------------------------------------------------
% Job configuration created by cfg_util (rev $Rev: 3599 $)
%-----------------------------------------------------------------------
%%%% NEWSGMENT
matlabbatch{1}.spm.tools.preproc8.channel.vols = '<UNDEFINED>'; %%% subject T1
matlabbatch{1}.spm.tools.preproc8.channel.biasreg = 0.0001;
matlabbatch{1}.spm.tools.preproc8.channel.biasfwhm = 60;
matlabbatch{1}.spm.tools.preproc8.channel.write = [0 0];

matlabbatch{1}.spm.tools.preproc8.tissue(1).tpm = '<UNDEFINED>'; %{fullfile(spm('Dir'), 'toolbox', 'Seg', 'TPM.nii,1')};
matlabbatch{1}.spm.tools.preproc8.tissue(1).ngaus = 2;
matlabbatch{1}.spm.tools.preproc8.tissue(1).native = [1 1];
matlabbatch{1}.spm.tools.preproc8.tissue(1).warped = [0 0];

matlabbatch{1}.spm.tools.preproc8.tissue(2).tpm = '<UNDEFINED>'; %{fullfile(spm('Dir'), 'toolbox', 'Seg', 'TPM.nii,2')};
matlabbatch{1}.spm.tools.preproc8.tissue(2).ngaus = 2;
matlabbatch{1}.spm.tools.preproc8.tissue(2).native = [1 1];
matlabbatch{1}.spm.tools.preproc8.tissue(2).warped = [0 0];

matlabbatch{1}.spm.tools.preproc8.tissue(3).tpm = '<UNDEFINED>'; %{fullfile(spm('Dir'), 'toolbox', 'Seg', 'TPM.nii,3')};
matlabbatch{1}.spm.tools.preproc8.tissue(3).ngaus = 2;
matlabbatch{1}.spm.tools.preproc8.tissue(3).native = [1 1];
matlabbatch{1}.spm.tools.preproc8.tissue(3).warped = [0 0];

matlabbatch{1}.spm.tools.preproc8.tissue(4).tpm = '<UNDEFINED>'; %{fullfile(spm('Dir'), 'toolbox', 'Seg', 'TPM.nii,4')};
matlabbatch{1}.spm.tools.preproc8.tissue(4).ngaus = 3;
matlabbatch{1}.spm.tools.preproc8.tissue(4).native = [1 1];
matlabbatch{1}.spm.tools.preproc8.tissue(4).warped = [0 0];

matlabbatch{1}.spm.tools.preproc8.tissue(5).tpm = '<UNDEFINED>'; %{fullfile(spm('Dir'), 'toolbox', 'Seg', 'TPM.nii,5')};
matlabbatch{1}.spm.tools.preproc8.tissue(5).ngaus = 4;
matlabbatch{1}.spm.tools.preproc8.tissue(5).native = [1 1];
matlabbatch{1}.spm.tools.preproc8.tissue(5).warped = [0 0];

matlabbatch{1}.spm.tools.preproc8.tissue(6).tpm = '<UNDEFINED>'; %{fullfile(spm('Dir'), 'toolbox', 'Seg', 'TPM.nii,6')};
matlabbatch{1}.spm.tools.preproc8.tissue(6).ngaus = 2;
matlabbatch{1}.spm.tools.preproc8.tissue(6).native = [0 0];
matlabbatch{1}.spm.tools.preproc8.tissue(6).warped = [0 0];

matlabbatch{1}.spm.tools.preproc8.warp.reg = 4;
matlabbatch{1}.spm.tools.preproc8.warp.affreg = 'mni';
matlabbatch{1}.spm.tools.preproc8.warp.samp = 3;
matlabbatch{1}.spm.tools.preproc8.warp.write = [1 1];


