function dispTasks(tasksTodo, tasksDone)
    global CLASSICSEGMENT;
    global NEWSEGMENT;
    global DARTEL;
    
    disp('The following tasks have already been done:')
    if tasksDone.realign, disp('- Realignment');  end
    if isfield(tasksDone, 'QC') && tasksDone.QC, disp('- Quality Control'); end
    %if tasksDone.coregister, disp('-Coregistration'); end
    if tasksDone.segment == NEWSEGMENT, disp('- New Segmentation'); end
    if tasksDone.segment == CLASSICSEGMENT, disp('- Classic Segmentation'); end
    if tasksDone.segment == DARTEL, disp('- Dartel'); end
    if tasksDone.dartel.segment, disp('    - segmentation'); end
    if tasksDone.dartel.normalize, disp('    - normalization'); end
    if tasksDone.dartel.warp, disp('    - warping'); end
    if tasksDone.dartel.iwarp, disp('    - inverse warping'); end
    if tasksDone.dartel.coregister, disp('    - coregistration'); end
    if tasksDone.dartel.coregister_interp, disp('    - coregistration with interpolation'); end
    if tasksDone.finergrid.iwarp || tasksDone.finergrid.coregister,disp('- Finergrid'); end
    if tasksDone.finergrid.iwarp, disp('    - inverse warping'); end
    if tasksDone.finergrid.coregister, disp('    - coregistration'); end
    if tasksDone.label, disp('- Labeling'); end

    disp(' ')
    disp('The following tasks have to be done:')
    if tasksTodo.realign, disp('- Realignment');  end
    if isfield(tasksTodo, 'QC') && tasksTodo.QC, disp('- Quality Control'); end
    %if tasksTodo.coregister, disp('-Coregistration'); end
    if tasksTodo.segment == NEWSEGMENT, disp('- New Segmentation'); end
    if tasksTodo.segment == CLASSICSEGMENT, disp('- Classic Segmentation'); end
    if tasksTodo.segment == DARTEL, disp('- Dartel'); end
    if tasksTodo.dartel.segment, disp('    - segmentation'); end
    if tasksTodo.dartel.normalize, disp('    - normalization'); end
    if tasksTodo.dartel.warp, disp('    - warping'); end
    if tasksTodo.dartel.iwarp, disp('    - inverse warping'); end
    if tasksTodo.dartel.coregister, disp('    - coregistration'); end
    if tasksTodo.dartel.coregister_interp, disp('    - coregistration with interpolation'); end
    if tasksTodo.finergrid.iwarp || tasksTodo.finergrid.coregister,disp('- Finergrid'); end
    if tasksTodo.finergrid.iwarp, disp('    - inverse warping'); end
    if tasksTodo.finergrid.coregister, disp('    - coregistration'); end
    if tasksTodo.label, disp('- Labeling'); end
    
return

% disp(' ')
% disp('recapitulatif :')
% disp(['- Realignment'   ,sprintf('\t\t'),int2str(tasksTodo.realign),' - ',int2str(tasksDone.realign)])
% disp(['- QC'            ,sprintf('\t\t\t'),int2str(tasksTodo.QC),' - ',int2str(tasksDone.QC)])
% disp(['- Segment'       ,sprintf('\t\t'),int2str(tasksTodo.segment),' - ',int2str(tasksDone.segment)])
% disp('- Dartel :')
% disp(['    - segment'   ,sprintf('\t\t'),int2str(tasksTodo.dartel.segment),' - ',int2str(tasksDone.dartel.segment)])
% disp(['    - normalize' ,sprintf('\t\t'),int2str(tasksTodo.dartel.normalize),' - ',int2str(tasksDone.dartel.normalize)])
% disp(['    - warp'      ,sprintf('\t\t'),int2str(tasksTodo.dartel.warp),' - ',int2str(tasksDone.dartel.warp)])
% disp(['    - iwarp'     ,sprintf('\t\t'),int2str(tasksTodo.dartel.iwarp),' - ',int2str(tasksDone.dartel.iwarp)])
% disp(['    - coregister',sprintf('\t'),int2str(tasksTodo.dartel.coregister),' - ',int2str(tasksDone.dartel.coregister)])
% disp(['    - coregister_interp',sprintf('\t'),int2str(tasksTodo.dartel.coregister_interp),' - ',int2str(tasksDone.dartel.coregister_interp)])
% disp('- Finergrid :')
% disp(['    - iwarp'     ,sprintf('\t\t'),int2str(tasksTodo.finergrid.iwarp),' - ',int2str(tasksDone.finergrid.iwarp)])
% disp(['    - coregister',sprintf('\t'),int2str(tasksTodo.finergrid.coregister),' - ',int2str(tasksDone.finergrid.coregister)])
% disp(['- label'         ,sprintf('\t\t\t'),int2str(tasksTodo.label),' - ',int2str(tasksDone.label)])
% 
% return


