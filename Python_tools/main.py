#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" This module does MRI data processing, with or without a graphical interface.

Two kind of data are processed: functional MRI and diffusion MRI. The aims are to build functional connectivity graph
or conectome respectively.

In both cases, main steps are:
    0. loading setting from config.py (user is asked to set mandatory variables there)
    1. loading processing parameters (path to data, processing choice...) and checking their coherence;
    2. preparing processing for each dataset (folders creation, scripts writing...);
    3. data processing: loop on each function chosen by user, and for each function, loop on each data set
        - for functional MRI, functions may be:
            - preprocessing by SPM functions (run a script with matlab);
            - quality check: resulting volumes displayed
            - times series extraction by R scripts
            - graph construction by R scripts
        - for diffusion MRI.
        
During execution, a temporary file is written (text format) with all informations about user's choices, processing, date and time. This file is regularily updated, and can be found in folder /tmp/ in current directory.

See config.py for instruction to choose variables values.

To add new function to processing list, create a corresponding class object in module functionsInfo.py and use it in part 3 (processing).
Don't forget to add this new possibility to GUI (see module GUIcodes.py) and parameter file loading (see readParameterFile.py). Update class allFunctions in module functionsInfo.py too.

Created by Flore Harlé    01/06/2012
Latest update :           10/10/2012
version 2.0

"""

from os import mkdir, path, getcwd
from time import strftime
import sys

startTime = strftime("%A %d %B %Y %H:%M")
startTime2 = strftime("%Y_%m_%d_%Hh%M")

print " \n      ******************************************"
print "      *            Data Processing             *"
print "      ******************************************\n"


# ---------------------- SETTINGS ----------------------------------------- #
# User have to open config.py and set necessary variables in method settings,
# then values are loaded.

from config import settings
param = settings()
try:
    if (sys.argv[1] == "script") or (sys.argv[1] == "s"):
        param["mode"] = "script"
    elif sys.argv[1] == "--mode" or sys.argv[1] == "-m":
        from loadAndCheck import setMode
        param = setMode(param)
    else:
        param["mode"] = "graph"
except IndexError:
        param["mode"] = "graph"


# ---------------------------- LOAD DATA ---------------------------------- #
# All information on processing is collected in a dictionary :
# param["parameter_name"] = parameter_value

print "1. Select and check data"

# loads parameters and check consistency
from loadAndCheck import loadParameter
param = loadParameter(param)

# if param is updated by user(once param is updated, it contains processes)
if "process" in param :
    # ---------------------------- TEMPORARY FILE ----------------------------- #
    # write process main parameters in temporary file

    print "\n2. Write information in temporary file"

    crtDir = getcwd()
    if path.exists(crtDir + "/tmp") is False:
        mkdir(crtDir + "/tmp")
    param["tempFileName"] = "tmp/" + startTime2 + "_processing_info.txt"
    textFile = open(param["tempFileName"], "w")
    textFile.write(startTime + "\n\n")
    if param["mode"] == "script":
        textFile.write("Parameters read in file " + param["paramFile"] + "\n")
    else:
        textFile.write("Parameters set with GUI.\n")
    if param["case"] == "functional":
        textFile.write("Functional fMRI data processed.\n")
        textFile.write("Overwrite existing files: " + param["overwrite"] + "\n")
    else:
        textFile.write("Diffusion fMRI data processed.\n")
    textFile.write("\nChosen functions:")
    # if "process" in param:  test if process in param
    for p in param["process"]:
        textFile.write("\n\t" + p)
    textFile.write("\n\nData folders:\n")
    for i, f in enumerate(param["examRep"]):
        textFile.write(str(i + 1) + ". " + f + "\n")
    textFile.write("\n")
    textFile.close()

    print "Information saved in temporary file", param["tempFileName"], "\n"
    param["dateTime"] = startTime2
 

    # -------------------------- PROCESSING ----------------------------------- #
    # loop on all function name in param["process"]
    # at each step there is a loop on data sets

    print "3. Data processing"

    for p in param["process"]:
#-------------------------------Functional-----------------------------------------#
        # ---------------------- PREPROCESSING -------------------------------- #
        if p == "data preprocessing":
            from functionsInfo import dataPreprocessing
            preproc = dataPreprocessing()
            preproc.writeScript(param)
            preproc.run(param)

        # ---------------------- QUALITY CHECK -------------------------------- #
        elif p == "quality check":
            from functionsInfo import QualityCheck
            QC = QualityCheck()
            QC.run(param)

        # ---------------------- TIME SERIES ---------------------------------- #
        elif p == "time series extraction":
            from functionsInfo import TSExtraction
            TS = TSExtraction(**param)
            TS.run()

        # ---------------------- GRAPH ---------------------------------------- #
        elif p == "graph computing":
            from functionsInfo import graphComputing
            GC = graphComputing(**param)
            GC.run()
#-------------------------------Diffusion-----------------------------------------#
        # ---------------------- preprocess ----------------------------------- #
        elif p == "Preprocess":
            from functionsInfo import preprocess 
            preprocDif = preprocess()
            preprocDif.run(param)
        elif p == "Register":
            from functionsInfo import register 
            reg = register()
            reg.run(param)
        elif p == "TBSS":
            from functionsInfo import tbss 
            TB = tbss()
            TB.run(param)
    ##### add new function in this part: create instance related to this function and run it
    ##### warning: functions are run in order of appearance in param["process"]  


    # -------------------------- END ------------------------------------------ #
    
    print "End -", strftime("%H:%M")

    textFile = open(param["tempFileName"], "a")
    textFile.write("\nEnd - " + strftime("%H:%M"))
    textFile.close()
    import os
    import sys
    if sys.platform == "win32":
        os.system('pause')
    exit(0)
    
else:
    print "Window closed by user, programme exit(0)"
    exit(0)
    
