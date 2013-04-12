%-----------------------------------------------------------------------
% Job configuration created by cfg_util (rev $Rev: 3599 $)
%-----------------------------------------------------------------------
%%%% DARTEL (run dartel existing template)
matlabbatch{1}.spm.tools.dartel.warp1.images{1} = '<UNDEFINED>';
matlabbatch{1}.spm.tools.dartel.warp1.images{1}.tname = 'Images';
matlabbatch{1}.spm.tools.dartel.warp1.images{1}.tgt_spec.name = 'filter';
matlabbatch{1}.spm.tools.dartel.warp1.images{1}.tgt_spec.value = 'image';
matlabbatch{1}.spm.tools.dartel.warp1.images{1}.tgt_spec.name = 'strtype';
matlabbatch{1}.spm.tools.dartel.warp1.images{1}.tgt_spec.value = 'e';
matlabbatch{1}.spm.tools.dartel.warp1.images{1}.sname = 'New Segment: rc1 Images';
%%%matlabbatch{1}.spm.tools.dartel.warp1.images{1}.src_exbranch = substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1});
%%%matlabbatch{1}.spm.tools.dartel.warp1.images{1}.src_output = substruct('.','tiss', '()',{1}, '.','rc', '()',{':'});
matlabbatch{1}.spm.tools.dartel.warp1.settings.rform = 0;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(1).its = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(1).rparam = [4 2 1e-06];
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(1).K = 0;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(1).template = '<UNDEFINED>';%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'TemGraph1_1.5.img')};
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(2).its = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(2).rparam = [2 1 1e-06];
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(2).K = 0;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(2).template = '<UNDEFINED>';%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'TemGraph2_1.5.img')};
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(3).its = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(3).rparam = [1 0.5 1e-06];
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(3).K = 1;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(3).template = '<UNDEFINED>';%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'TemGraph3_1.5.img')};
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(4).its = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(4).rparam = [0.5 0.25 1e-06];
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(4).K = 2;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(4).template = '<UNDEFINED>';%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'TemGraph4_1.5.img')};
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(5).its = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(5).rparam = [0.25 0.125 1e-06];
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(5).K = 4;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(5).template = '<UNDEFINED>';%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'TemGraph5_1.5.img')};
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(6).its = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(6).rparam = [0.25 0.125 1e-06];
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(6).K = 6;
matlabbatch{1}.spm.tools.dartel.warp1.settings.param(6).template = '<UNDEFINED>';%{fullfile(spm('Dir'), 'toolbox', 'AtlasMNI', 'TemGraph6_1.5.img')};
matlabbatch{1}.spm.tools.dartel.warp1.settings.optim.lmreg = 0.01;
matlabbatch{1}.spm.tools.dartel.warp1.settings.optim.cyc = 3;
matlabbatch{1}.spm.tools.dartel.warp1.settings.optim.its = 3;
