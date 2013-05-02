#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------------------- #
import sys
def settings():
    
    """ Settings for main.py execution.

    Variables are returned in a dictionary param, whose keys variables names and content are values.

    Some variables are mandatory and set for user's system (path to softwares or repertories), some are necessary only if others are set to specific values. Otherwise their content is ignored.
    This method applies a few checking on variables choice, and may display error message on screen and interrupt execution when necessary.    
    
    Variables list (all are strings):
        - mode         "graph" to use graphical interface
                       "script" to not display graphical interface and read parameters in a text file
                        mandatory
                        
        - option        "inter" to interact with user when necessary
                        "indep" to execute all program without asking for user instruction (except for parameter choice if mode == "graph")
                        mandatory

        - matlabPath    directory to MATLAB application
                        mandatory to run matlab functions, for example for functional MRI data preprocessing, if PATH not set in .bashrc or .bash_profile file
                        set it once for user's computer

        - repSPM        directory to SPM8 folder
                        mandatory for SPM functions use, if mode == "graph", or if mode == "script" and repSPM is not given in parameters file
                        if repSPM is given several times, value is loaded from in parameters file
                        
        - repTools      directory to MATLAB scripts folder for data preprocessing
                        mandatory if mode == "graph", or if mode == "script" and repTools is not in parameters file
                        if repTools is given several times, value is loaded from in parameters file
                        
        - repR          directory to R scripts folder
                        mandatory if mode == "graph", or if mode == "script" and repR is not in parameters file
                        if repR is given several times, value is loaded from in parameters file

        - paramFile     path and name to parameters file
                        mandatory if mode == "script"
    """
    import os
    param = dict()  
    param["mode"] = "graph"
    param["option"] = "indep"
    sourcePath = os.path.split(os.path.realpath(__file__))[0]
    if sys.platform == "win32":
        sourcePath = sourcePath.replace('\\','/')
    print "Source workspace : " + sourcePath
    try:
        configFile = open("Config.txt", "r")
        ############################# ? completer ###############################################
        lines = configFile.readlines()
        find = False
        for line in lines:
            if "matlabPath:" in line:
                matPath = line.split(":")[1]
                if os.path.isfile(matPath[0:-1]+"matlab"):
                    param["matlabPath"]=matPath
                    find = True
                else:
                    print matPath+"matlab is not a file"
        configFile.close()
        if find is not True:
            print("Can't find Matlab path in file Config.txt")
            print "Searching MATLAB "
            param["matlabPath"]=searchMatlab()
        
    except Exception,name:
        print name , " searching MATLAB "
        param["matlabPath"]=searchMatlab()
            
    param["repSPM"] = os.path.realpath(sourcePath +"/../../spm8/").replace('\\','/')
    param["repTools"] = os.path.realpath(sourcePath +"/../Matlab_tools/preproc_SPM8/").replace('\\','/')
    param["repR"] = os.path.realpath(sourcePath +"/../R_tools/").replace('\\','/')
    param["paramFile"] = os.path.realpath(sourcePath +"/paramfile.txt").replace('\\','/')

    
    # check values for mandatory variables
    if "mode" in param:
        if (param["mode"] != "graph") and (param["mode"] != "script"):
            sys.exit("ERROR: \"" + param["mode"] + "\" wrong value for variable mode in config.py\n -> should be \"graph\" or \"script\"")
    else:
        sys.exit("ERROR: define value for variable mode in config.py, \"graph\" or \"script\"")
    if "option" in param:
        if (param["option"] != "inter") and (param["option"] != "indep"):
            sys.exit("ERROR: \"" + param["option"] + "\" wrong value for variable option in config.py\n -> should be \"inter\" or \"indep\"")
    else:
        sys.exit("ERROR: define value for variable option in config.py, \"inter\" or \"indep\"")
        
    # if mode is "script", check if variable paramFile is given
    if (param["mode"] == "script") and ("paramFile" not in param):
        sys.exit("ERROR: to read parameters in a file, define file path and name in variable paramFile, in config.py")
    

    return param
# ---------------------------------------------------- #

def searchMatlab():
    if not sys.platform == "win32" :
        import subprocess
        p = subprocess.Popen("which matlab", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            None
            #print line #to display the result
        retval = p.wait()
        if " no " not in line:
            matlabPath0 = line.strip().split("/")
            matlabPath=""
            for p in matlabPath0[0:-1]:
                matlabPath= matlabPath+p+"/"
        else:
            p = subprocess.Popen(["/bin/bash","-i","-c","alias matlab"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                #None
                print line #to display the result
            p.communicate()
            if " not " not in line:
                matlabPath0 = line.strip().split("'")
                matlabPath=matlabPath0[1][0:-6]
            else:
                print "can't find matlab(please select the directory of MATLAB)"
                ############################# ? completer ###############################################
        configFile = open("Config.txt", "w")
        configFile.write("matlabPath:"+matlabPath+"\n")
        configFile.close()
        print("---Matlab found--- \n OK")
    return matlabPath
# ---------------------------------------------------- #
def reinitializeSettings(param):
    """ Set default values for parameters settings defined in function settings."""
  
    param["mode"] = "graph"
    param["option"] = "indep"
    param["matlabPath"] = ""
    param["repSPM"] = ""
    param["repTools"] = ""
    param["repR"] = ""
    param["paramFile"] = ""

    
