#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Management of parameter file.

import sys
from os import path

######### loadParam finir commentaires
######### setParamDict revoir repR

# ---------------------------------------- ##
def setParamDict(param):
    """ Load and check parameters from text file param["paramFile"]. The aim is to return the same parameters than with GUI mode (see class mainWindow in GUIcodes).

        File is read by method loadParam, that returns dictionary paramStr of parameter names and values in string format.
        Then values are tested, converted or used to get variables in appropriate format, depending on parameter name. For parameters not found, default values may be loaded.
        
        First parameter search is "case":
            - if case is "diffusion", process will be done for diffusion MRI data
            - if case is "functional", process will be done for functional MRI data            
            
        Entry param is a  dictionary of parameters, which may already contains (see config.py, and loadParameter in loadAndCheck.py):
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
        
        This method returns dictionary param completed, whose new keys and values are listed below.
                    
        Two parameters are mandatory, otherwise the execution interrupts:
            - case          "functional" or "diffusion", data type
            - examRep       list of directory to medical exam folders
            
        Other parameters can be:
            - process           list of functions names (see module functionsInfo.py)
                                default value : [] (empty list)
            
            - preprocess        for case "functional"
                                if "data preprocessing" is in process
                                list of preprocessing, see module matlabFct.py for names
                                
            - overwrite         for case "functional"
                                if "data preprocessing" is in process
                                values are "y" or "n" (not case sensitive)
                                default value : "n"
                                
            - allPreprocess     for case "functional"
                                if "data preprocessing" is in process
                                detailled matlab functions names list
                                extracted from param['preprocess'] list by method functions
                                
            - allPreprocessInfo for case "functional"
                                if "data preprocessing" is in process
                                list of dictionary of matlab functions informations
                                each element of list param["allPreprocessInfo"] is related to a dataset path in param["examRep"]
                                keys of i-th dictionary param["allPreprocessInfo"][i] are functions names of list param["allPreprocess"]
                                value of param["allPreprocessInfo"][i][f] is the SMPfct class instance (see in module matlabFct), related to dataset in param["examRep"][i] and function f
                                
            - run               for case "functional"
                                if "data preprocessing" is in process
                                list of dictionary of boolean values, same structure as param["allPreprocessInfo"]
                                each element of list param["run"] is related to a dataset path in param["examRep"]
                                keys of i-th dictionary param["run"][i] are functions names of list param["allPreprocess"]
                                param["run"][i][f] is a boolean value, related to dataset in param["examRep"][i] and function f
                                param["run"][i][f] = TRUE  if function f have to be applied to this data in param["examRep"][i] (data never processed or overwriting on existing files)
                                                     FALSE if function won't be applied (data already processed and param["overwrite"] = "n")
                                                     
            - pb                for case "functional"
                                if "data preprocessing" is in process
                                list of dictionary of boolean values, same structure as param["allPreprocessInfo"]
                                each element of list param["pb"] is related to a dataset path in param["examRep"]
                                keys of i-th dictionary param["pb"][i] are functions names of list param["allPreprocess"]
                                param["pb"][i][f] is a boolean value, related to dataset in param["examRep"][i] and function f
                                param["pb"][i][f] = TRUE  if function f can't be applied to this data in param["examRep"][i] (input files are not available, functions choice and order have to be mofified)
                                                    FALSE if function can be applied
        Keys allPreprocessInfo, run and pb are not created if param["preprocess"] is empty


        When data preprocessing have to be done, some tests are done:
            - existence of repertories repSPM, repR or repTools
            - files existence for atlases and templates needed for matlab functions
            - absence of repetitions in functions list, by method reduceList (module loadAndCheck)
            - appropriate folder organization and existence of data, by method checkFolderTree (module loadAndCheck)
            - consistency of functions choice for preprocessing, order and available files, for each dataset, by method checkProcess (module loadAndCheck).
        If one of these tests fails, programm execution is interrupted and user is asked to correct parameter file.
        
        """

    from loadAndCheck import checkDir, checkFolderTree, checkProcess

    # Read parameter file and extract values
    paramStr = loadParam(param["paramFile"])

    # check content of dictionary paramStr
    if not ("case" in paramStr):
        sys.exit("ERROR: no case! Choose between \'functional\' and \'diffusion\'.")
    elif (paramStr["case"] != "functional") and (paramStr["case"] != "diffusion"):
        sys.exit("ERROR in case value! Choose between \'functional\' and \'diffusion\'.")
    else:
        param["case"] = paramStr["case"]
        
    if not "examRep" in paramStr:
        sys.exit("ERROR: no data folder! Give at least one directory to dataset in parameter \'examRep\'.")

    # ----- loading values ---- #
    
    arg = dict()
    for pname in paramStr:

        # overwrite
        if pname == "overwrite":
            ans = (paramStr[pname]).lower()
            if ((ans == "y") or (ans == "n")) is False:
                print "WARNING: can\'t read value for parameter \"overwrite\", set \"n\"."
                param["overwrite"] = "n"
            else:
                param["overwrite"] = ans

        # functions names
        elif pname == "process":
            from functionsInfo import allFunctions
            fctInfo = allFunctions()
            param[pname] = list()
            for p in paramStr[pname].split(","):
                param[pname].append(fctInfo.fctName(p))
                if param[pname][-1] == "error":
                    sys.exit("ERROR: function \""+p+"\" not identified, correct \"process\" in parameter file.")
                elif param[pname][-1] not in fctInfo.fctList(paramStr["case"]):
                    sys.exit("ERROR: function \""+p+"\" not defined for case \""+paramStr["case"]+"\".")
        elif pname == "preprocess":
            param[pname] = paramStr[pname].split(",")
        
        elif pname[0:6] == "templ_":
            arg[pname] = paramStr[pname].split(",")
            
        # files or folders
        else:
            # paths lists
            fList = paramStr[pname].split(",")

	    # exam folder list (data list)
            if pname == "examRep":
                param[pname] = list()
                for f in fList:
                    param[pname].append(checkDir(f))
                if len(param[pname])==0:
                    sys.exit("ERROR: no data folder!\nGive at least one directory to dataset in parameter \'examRep\'.")                    
                        
            # SPM, matlab or R functions folders
            elif (pname == "repSPM") or (pname == "repTools") or (pname == "repR"):
                param[pname] = paramStr[pname]

    # ----- checking values and default setting ---- #

    # check directory to R functions folder, necessary for time series extraction and graph computing, if case is "functional"
    if "process"in param:
        if ("time series extraction" in param["process"]) or ("graph computing" in param["process"]):
            if "repR" in param:
                if param["repR"] == "":
                    sys.exit("ERROR: no directory to R functions folder in config.py or parameter file. Add parameter \'repR\'.")
                else:
                    param["repR"] = checkDir(param["repR"])
            else:
                sys.exit("ERROR: no directory to R functions folder in config.py or in parameter file. Add parameter \'repR\'.")

    # atlases and templates
    if ("templ_iwarp_dartel" in arg) and ("templ_iwarp" in arg):
        print "WARNING: two atlases defined for function \'iwarp\' in Dartel, \'templ_iwarp\' value loaded only."

    # preprocessing
    param["allPreprocess"] = list()
    generalProcessInfo = dict()
    if "preprocess" in param:
        if "data preprocessing" not in param["process"]:
            print "WARNING: process \"data preprocessing\" not found, no function in \"preprocess\" will be run."
        else:
            i=0
            from matlabFct import functions, SPMfct
            
            # check directory to SPM folder, necessary for preprocessing
            if "repSPM" in param:
                if param["repSPM"] == "":
                    sys.exit("ERROR: no directory to SPM folder in config.py or parameter file. Add parameter \'repSPM\'.")
                else:
                    param["repSPM"] = checkDir(param["repSPM"])
            else:
                sys.exit("ERROR: no directory to SPM folder in config.py or in parameter file. Add parameter \'repSPM\'.")
                
             # check directory to matlab tools folder, necessary for preprocessing
            if "repTools" in param:
                if param["repTools"] == "":
                    sys.exit("ERROR: no directory to MATLAB tools folder in config.py or parameter file. Add parameter \'repTools\'.")

                else:
                    param["repTools"] = checkDir(param["repTools"])
            else:
                sys.exit("ERROR: no directory to MATLAB tools folder in config.py or in parameter file. Add parameter \'repTools\'.")        

            arg["repSPM"] = param["repSPM"]
            for p in param["preprocess"]:
                for f in functions(p):
                    # function information
                    param["allPreprocess"].append(f)
                    generalProcessInfo[f]=SPMfct(f,**arg)
                    generalProcessInfo[f].nb = i
                    generalProcessInfo[f].parent = p
                    # reference files existence
                    for t in generalProcessInfo[f].template["name"]:
                        if (t != "") and (not path.isfile(t)):
                            sys.exit("ERROR "+t+": no such file, check "+generalProcessInfo[f].template["param"]+" in parameter file.")    
                    i+=1

        # redondancy in processes list
        from loadAndCheck import reduceList
        msg = reduceList(param["allPreprocess"])
        if msg == "rep":
            sys.exit("ERROR: redondancy in functions list, modify it in parameter process.\nNB: functions \"dartel\" and \"finergrid\" include several other functions.")
            
    else:
        param["preprocess"] = list()
    

    if not ("overwrite" in param):
        param["overwrite"] = "n"

    # Check data folders
    msg, dataInfo = checkFolderTree(param["examRep"])
    for i,m in enumerate(msg):
        if m[0:5] == "ERROR":
            sys.exit(m+"\n   -> check data or parameter file.")

    # Check functions consistency for data preprocessing
    param["run"], param["pb"], param["allPreprocessInfo"] = checkProcess(param["allPreprocess"],generalProcessInfo,param["examRep"],dataInfo,param["overwrite"])
        
    return param

# ---------------------------------------- ##
def loadParam(name):
    """ Read parameter file (text format) and look for key words to find parameters value.
        Entry name is the complete name fo the file.

        Only two parameters are mandatory to do the processing:
            - case      "functional" or "diffusion"
            - examRep   list of directory to medical exam folders, containing data to process. Elements are separated by the symbol ",".
            
        Other parameters can be added:
            - process       list of process steps to apply to data, names are separated by ",". See module functionsInfo.py for their names (attibute name1 or name2 of each class).
            - preprocess    list of treatments to apply in preprocessing step, only if case is "functional" and "data preprocessing" is in process list
                            Functions names are given in method functions (module matlabFct). They are separated by ",".
                            Default value : empty (no data preprocessing);
            - information about templates/atlases chosen for preprocessing (with SPM8). If not given, some files are
              set by default in class SPMfct (module matlabFct). Names have to be complete (with path) and are separetd by symbol ",".
              Key words:
                - templ_segment             for function "segment"
                - templ_normalize           for function "normalize"
                - templ_iwarp               for functions "iwarp" and "coregister" (in Dartel)
                - templ_iwarp_dartel        for functions "iwarp" and "coregister" (in Dartel)
                - templ_iwarp_finergrid     for functions "iwarp" and "coregister" (in finergrid)
                - templ_label               for function "label"
            - acces to repertory of matlab functions, if not given in config.py:
                - repSPM    for SPM8 (if "data preprocessing" in process)
                - repTools  other Matlab functions (if "data preprocessing" in process)
                - repR      R functions for time series extraction or graph computing
            - instruction to decide if the existing files must be overwritten during data preprocessing:
              overwrite = y to overwrite, n otherwise (default setting).

        This method reads only lines begining by a keyword (parameter name), followed by
        symbol "=". Spaces have no incidence. In a line, text after "#" is skipped.
        Don't use "" for text.
        Warning: don't finish lists with "," or last element will be empty, converted in root directory "/" if expected value is a repertory."""


    # parameter file
    if not path.exists(name):
        sys.exit("ERROR for parameter file: no such file \'"+name+"\'.\n -> Correct it in config.py.")
    paramFile = open(name,"r")
    text = paramFile.read()

    # read text line by line
    lines = text.split("\n")
    paramList = list()
    for elt in lines:
        # remove empty lines, lines begining with # and lines without symbol =
        if (elt!="") and (elt.find("#",0,1)!=0) and (elt.isspace() is False) and (elt.find("=",0)!=-1):
            paramList.append(elt)

    # if empty file, error
    if len(paramList) < 1:
        sys.exit("No paramaters found in "+name+".\nDefine at least directory to exam folder(s) for data to be processed in examRep.")

    # extract parameters value
    paramDict = findKeyWords(paramList)

    # message: parameter list
    print "Parameters found in "+name+":"
    for key in paramDict:
        print "\t-",key
    print "Default values will be taken for other parameters."

    return paramDict

## ---------------------------------------- ##
def findKeyWords(paramList):
    """ Comparison between strings of list paramList (entry) and elements of reference list KWlist.
        Spaces are suppressed. This method reads first letters before symbol "=", and compare it with words in KWlist.
        When a keyword is found, the method extracts the parameter value (in string), after the "=".
        The method returns dictionary paramDict:
            paramDict[parameter name] = corresponding values in paramList.
        In case of mutiple instances of a parameter name in paramList, it gets only the last value."""

    # keywords list -> complete this list to add new parameter names
    KWlist = ["case","examRep","process","preprocess","overwrite","templ_segment","templ_normalize",
             "templ_iwarp","templ_iwarp_dartel","templ_iwarp_finergrid","templ_label",
             "repSPM","repTools","repR"]

    paramDict = {}  # for parameters
    checkDict = {}  # parameters counter
    for elt in KWlist:
        checkDict[elt] = 0

    # keywords research for each line read in parameter file (see method loadParam)
    for eltParam in paramList:
        # suppress spaces
        eltParam = "".join(eltParam.split(" "))

        for eltKey in KWlist:
            if eltParam.find(eltKey,0)==0:
                # parameter name before symbol "="
                i = eltParam.find("=",len(eltKey),len(eltKey)+1)

                # words matching
                if i==len(eltKey):

                    # statement
                    checkDict[eltKey] += 1
                    if checkDict[eltKey] > 1:
                        print " WARNING!",eltKey,": parameter defined at least twice, last value selected."

                    # parameter value : between "=" and "#" or end of line
                    value = eltParam[i+1:len(eltParam)]
                    valueList = value.split("#")
                    value = valueList[0]
                    paramDict[eltKey] = value
                    
    return paramDict
