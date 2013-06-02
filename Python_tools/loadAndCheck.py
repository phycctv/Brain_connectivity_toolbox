#! /usr/bin/env python
# -*- coding: utf-8 -*-

# functions for parameters loading and checking
# Functions to check preprocessing coherence and feasability

import os
import sys
import glob
from os import path

# ----------------------------------------------------------------------------------- #
def loadParameter(param):
    """ Extraction of datasets and process information.

        Entry param is a  dictionary of parameters, which may already contains (see config.py):
            - mode          "graph" or "script", choice to use GUI or to load parameter file
            - option        choice to interact or not with user
                            "inter" to interact with user in console
                            "indep" otherwise
            - repSPM        mandatory if mode is "script" and "repSPM" is not given in parameter file, and "data preprocessing" is in process list
                            directory to SPM8 functions
            - repR          mandatory if mode is "graph"
                                      if mode is "script" and "repR" is not given in parameter file, and "time series extraction" or "graph computing" are in process list
                            directory to R scripts and functions
            - repTools      mandatory if mode is "graph"
                                      if mode is "script" and "repTools" is not given in parameter file, and "data preprocessing" is in process list
                            directory to matlab functions for data preprocessing (pp_loadVolumes, matlabbatch, etc...)
            - paramFile     mandatory if mode is "script"
                            parameter file name
                            
        Depending on mode, method mainWindow (module GUIcodes) or method setParamDict (module readParameterFile) is called.        
        
        If case is "functional" and if "data preprocessing" has been chosen, some checkings are done for each data set and each function.
            
        This method returns dictionary param completed with following elements (see mainWindow in GUIcodes.py or setParamDict in readParameterFile.py):
            - in all cases:
                - case
                - mode
                - option
                - examRep
                - process
            - depending on user's choices:
                - preprocess
                - allPreprocess
                - allPreprocessInfo
                - overwrite
                - pb
                - run
                - repSPM
                - repTools
                - repR
            """
    try:
        if param["mode"] == "graph":       
            # use GUI to get parameters
            from GUIcodes import caseWindow, mainWindow
            
            # case choice
            app = caseWindow(None, param)
            app.title("~ Case ~")
            app.focus_force()
            app.mainloop()
            if "case" not in param :
                print "Window closed by user, programme exit(0)"
                exit(0)
    
            # other parameters
            app = mainWindow(None, param)
            app.focus_force()
            app.mainloop()
    
        elif param["mode"] == "script":
            # load parameters from text file
            from readParameterFile import setParamDict
            param = setParamDict(param)
    
        # if case is "functional" and data preprocessing has been chosen
        msg = ""
        if param["case"] == "functional":
            # warning if some preprocessing functions can't be run
            for i, f in enumerate(param["examRep"]):
                for p in param["allPreprocess"]:
                    if param["pb"][i][p]:
                        msg += "\t- function \"" + p + "\" can't be run for data in " + f + "\n"
            if msg != "":
                # ask user's instruction if option == "inter"
                if param["option"] == "inter":
                    print "WARNING :\n" + msg + "Do you want to proceed (y to pursue, n to interrupt execution)?"
                    ans = ""
                    while ans != "y":
                        ans = raw_input()
                        ans = ans.lower()
                        if ans == "n":
                            sys.exit("Modify data choice or SPM functions order/choice in parameter file.")
                elif param["option"] == "indep":
                    print "WARNING :\n" + msg
    
        return param
        # exception if user clicks on the close button.
    except KeyError:
        return param
# # ---------------------------------------- ##
def setMode(param):
    """ set the "mode" of param "graph" or "script", choice to use GUI or to load parameter file
        Return param."""
    mode = raw_input("Please choice to use GUI or to load parameter file\n 1.Input \"script\" or \"s\" to use console mode.\n 2.Press Enter to use a graphical interface \n ->")
    if mode == "script" or mode == "s":
        param["mode"] = "script"
        print"Mode script:\n"
    else:
        param["mode"] = "graph"
        print"Mode graphic:\n"
        
        
    return param

# # ---------------------------------------- ##
def checkDir(rep):
    """ Check if entry rep (string) is a path, and add if necessary symbol "/" at the end.
        If rep is empty, set path "/".
        Return rep."""
    
     # last symbol /
    if len(rep) == 0:
        rep = rep + "/"
    else:
        if rep[-1] != "/":
            rep = rep + "/"

    # existence
    if not os.path.isdir(rep):
        sys.exit("ERROR: no such directory " + rep)

    return rep

# # ---------------------------------------- ##
def reduceList(l):
    """ Reduce list l in order to have only unique elements. In case of repetition, first occurence is kept.
        The method returns a message:
            - "ok" if no repetitions
            - "rep" if repetitions."""

    checkedList = list(set(l))
    msg = "ok"
    try:
        assert len(checkedList) == len(l)
    except AssertionError:
        msg = "rep"
    return msg

# # ---------------------------------------- ##
def checkFolderTree(examRep):
    """ For each repertory given in list examRep, check if parent folder is called "Original" and if folder contains expected sub-folders and files.

        Call function checkData to load data files names too.
        Return lists, whose numbering correponds to examRep numbering:
            - msg       list of strings
                            "ok" if folder organization is as expected,
                            text beginning with "ERROR" otherwise
            - filesInfo list of dictionary, returned by checkData."""

    filesInfo = list()
    msg = list()
    
    for fold in examRep:
        if sys.platform == "win32":
            fold = fold.replace('\\','/')
        fList = fold[0:-1].split("/")
        err = "ok"
        if len(fList) < 3:
            err = "ERROR: folder " + fList[-1] + " not in folder Original/ as expected."        
        elif fList[-2] != "Original":
            err = "ERROR: folder " + fList[-1] + " not in folder Original/ as expected."

        m, filesInfo2 = checkData(fold)
        filesInfo.append(filesInfo2)
        
        if m != "ok":
            if err == "ok":
                err = m
            else:
                err = m + "\n" + err

        msg.append(err)        
    return msg, filesInfo

        

# # ---------------------------------------- ##
def checkData(dataPath):
    """ Check folders and files existence for initial data in repertory dataPath (string), and extract files base names, for functional MRI data.

        dataPath must contains following sub-folders:
            - Anat          contains only one nifti file (extension ".nii")
            - Functional    contains several nifti files (extension ".nii")

        This method returns  a string msg containing error message(s) or "ok", and dictionary filesInfo of files information, whose keys are:
            - anatBaseName      base name of file in dataPath/Anat/, without extension
            - anatExt           extension of file in dataPath/Anat/
            - functBaseName     common part of file names in dataPath/Functional/, without extension
                                only first and last names of file list are compared
            - functExt          extension of files in dataPath/Functional/

        If there is no folder Anat or Functional in dataPath, filesInfo is empty.
            
        -------------
        Example:
        file organization in dataPath:
            dataPath
                        -> Anat
                                        -> anatfile.nii
                        -> Functional
                                        -> functfile_001.nii
                                        -> functfile_001.nii
                                            .
                                            .
                                            .
                                        -> functfile_405.nii

        resulting dictionary:
            filesInfo["anatBaseName"] = "anatfile"
            filesInfo["anatExt"] = "nii"
            filesInfo["functBaseName"] = "functfile"
            filesInfo["functExt"] = "nii"                
            """
    
    filesInfo = dict()
    err = list()
    if dataPath[-1] == "/":
        dataPath = dataPath[0:-1]
    
    # Check sub-folders 
    if path.exists(dataPath + "/Anat/") is False:
        err.append("ERROR: no repertory Anat/ in " + dataPath)
    if path.exists(dataPath + "/Functional/") is False:
        err.append("ERROR: no repertory Functional/ in " + dataPath)

    # Check data files and their names
    if len(err) == 0:
        
        # structural data
        anatList = glob.glob(dataPath + "/Anat/*.nii")
        if len(anatList) != 1:
            err.append("ERROR: no single NIFTI file in " + dataPath + "/Anat")
        else:
            #compatibility for windows
            if sys.platform == "win32":
                anatParts = anatList[0].split("\\")
            else:
                anatParts = anatList[0].split("/")
            anatParts2 = anatParts[-1].split(".")
            filesInfo["anatBaseName"] = anatParts2[0]
            filesInfo["anatExt"] = anatParts2[1]
            
        # functional data
        functList = glob.glob(dataPath + "/Functional/*.nii")
        if len(functList) == 0:
            err.append("ERROR: no NIFTI file in " + dataPath + "/Functional")
        else:
            # base name : common part for all files
            # comparison between first and last names
            functBaseName = ""
            namePart1 = functList[0].split("/")
            namePart2 = functList[-1].split("/")
            namePart11 = namePart1[-1].split(".")
            namePart21 = namePart2[-1].split(".")
            name1 = namePart11[0][0:-4]
            name2 = namePart21[0][0:-4]
            i = 0
            while i < len(name1):
                if name2.startswith(name1[0:i]):
                    functBaseName += name1[i]
                    i += 1
                else:
                    break
            #compatibility for windows
            if sys.platform == "win32":
                functBaseName = functBaseName.split("\\")[-1]
            filesInfo["functBaseName"] = functBaseName
            functParts = functList[0].split("/")
            functParts2 = functParts[-1].split(".")
            filesInfo["functExt"] = functParts2[-1]

    # end
    if len(err) != 0:
        msg = "\n".join(err)
    else:
        msg = "ok"
    return msg, filesInfo

# # ---------------------------------------- ##
def checkProcess(processList, processInfo, dataRep, dataInfo, overwrite):
    """ For each dataset in dataRep list, look for which function of processList list have to be applied, depending on overwrite value and existing files,
and if a function have to be run, check if it is possible, considering existing files and those that will be created by previous functions.

    Entries are:
        - processList       list of functions names, detailled
        - processInfo       dictionary of SPMfct class instance (see module matlabFct), whose keys are elemnts of processList
        - dataRep           list of paths to each dataset
        - dataInfo          dictionary generated by method checkData, containing base names for anatomical and functional files in each dataset
        - overwrite         "y" to overwrite existing files, "n" otherwise.

    NB : if overwrite is "n", only functions whose all output files exist won'y be run. If one of several files are missing, other function output files will be overwritten.

    For each dataset (number i), this method creates a list of available files avFile (empty at first), and inserts an element in lists run, pb and allProcessInfo.
    For each function f:
        0. Initialization: run[i][f] = TRUE, pb[i][f] = FALSE.
        1. SPMfct class instance is created, allProcessInfo[i][p], related to dataset and function tested, using files names information in dataInfo[i] and general process information in processInfo[f].
        2. If overwrite is "n", variable run[i][f] is set with value FALSE. Output files (given in allProcessInfo[i][p].endFile list) of f are searched in existing files.
        If at least one is missing, function f have to be run, and variable run[i][f] gets value TRUE.
        3. If run[i][f] is TRUE (overwrite is "y" or all output files were not found), function consistency is tested.
           Each input files (given in allProcessInfo[i][p].initFile list) is search in existing files. If it is not found, it is search in avFile list. If is
           it still missing, variable pb[i][f] gets value TRUE, because function f can't be run. If all input files are found (pb[i][f] is FALSE), output files are added to avFile, because they will be created before next functions execution.

    Finally, variables allProcessInfo, run and pb are returned.       """

    run = list()
    pb = list()
    allProcessInfo = list()

    # for each dataset
    for i, dataset in enumerate(dataRep):

        run.insert(i, dict())
        pb.insert(i, dict())
        avFile = list()
        allProcessInfo.insert(i, dict())

        # for each matlab function (process p)
        for p in processList:
            # data information
            arg = dict()
            arg["examRep"] = [dataset]
            if dataset[-1] == "/":
                rep = dataset[0:-1].split("/")
            else:
                rep = dataset.split("/")
            patientDir = ("/").join(rep[0:-2])
            arg["procDataRep"] = [patientDir + "/Processed/" + rep[-1]]
            arg["anatBaseName"] = dataInfo[i]["anatBaseName"]
            arg["functBaseName"] = dataInfo[i]["functBaseName"]
            
            # update files names for process p in instance of object SPMfct, copy of processInfo[p]
            allProcessInfo[i][p] = processInfo[p].duplicate()
            allProcessInfo[i][p].updateFiles(**arg)

            # in and out files checking
            pb[i][p] = False
            run[i][p] = True            

            # if user doesn't want to overwrite existing files:
            if overwrite == "n":
                # check if all out files already exist
                run[i][p] = False
                for f in allProcessInfo[i][p].endFile:
                    endFile = glob.glob(f)
                    if len(endFile) == 0:
                        # at least one file is missing => process p have to be run
                        run[i][p] = True

            # check if all initial files are available (exist or will be created)
            if run[i][p] == True:
                for f in allProcessInfo[i][p].initFile:
                    initFile = glob.glob(f)
                    endFile = list()
                    if len(initFile) == 0:
                        # nothing found for file(s) f
                        if f in avFile:
                            # f will be created by previous processes
                            endFile.extend(allProcessInfo[i][p].endFile)
                        else:
                            # impossible to run process p
                            pb[i][p] = True
                    else:
                        endFile.extend(allProcessInfo[i][p].endFile)
                if not pb[i][p]:
                    # process p can be run => add out files to available files list
                    avFile.extend(endFile)

    return run, pb, allProcessInfo

    
