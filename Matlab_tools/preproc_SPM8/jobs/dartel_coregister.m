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
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.interp = 0;
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.wrap = [0 0 0];
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.mask = 0;
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.prefix = 'nat';

% depuis New Segmentation and DARTEL : 
    % création de natwROI_MNI_V4_u_rc1*.nii dans Atlased/   (espace fonctionnel)
    % création de nat*.nii dans Anat/                       (espace fonctionnel)
    % à partir de :
    %       - mean*.nii                                     (espace fonctionnel)
    %       - *.nii                                         (espace anatomique)
    %       - wROI_MNI_V4_u_rc1*.nii                        (espace MNI)

% depuis Finergrid :
    % création de natwTemplate_u_rc1*.nii dans Atlased/     (espace fonctionnel)
    % à partir de :
    %       - mean*.nii                                     (espace fonctionnel)
    %       - *.nii                                         (espace anatomique)
    %       - wTemplate_u_rc1*.nii                          (espace MNI)