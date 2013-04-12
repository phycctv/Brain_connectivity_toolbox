%-----------------------------------------------------------------------
% Job configuration created by cfg_util (rev $Rev: 3599 $)
%-----------------------------------------------------------------------
matlabbatch{1}.spm.spatial.coreg.estwrite.ref = '<UNDEFINED>';
matlabbatch{1}.spm.spatial.coreg.estwrite.source = '<UNDEFINED>';
matlabbatch{1}.spm.spatial.coreg.estwrite.other = '<UNDEFINED>';
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.cost_fun = 'nmi';
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.sep = [4 2];
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.fwhm = [7 7];
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.interp = 4;
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.wrap = [0 0 0];
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.mask = 0;
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.prefix = 'nat';


% création de natc1*.nii dans Segmented/    (espace fonctionnel)
% à partir de :
%       - mean*.nii                         (espace fonctionnel)
%       - *.nii                             (espace anatomique)
%       - c1*.nii                           (espace anatomique)


% Même fonction que dartel_coregister.m, avec param.interp = 4 au lieu de
% 0, et template c1*.nii au lieu de wROI_MNI_V4_u_rc1*.nii.