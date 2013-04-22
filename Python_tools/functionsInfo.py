#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Created by Flore Harlé    02/10/2012
# Latest update :           10/10/2012

from time import strftime

# # ---------------------------------------- ##
class allFunctions():

    def __init__(self):
        self.dataPreprocessing = dataPreprocessing()
        self.QualityCheck = QualityCheck()
        self.TSExtraction = TSExtraction()
        self.graphComputing = graphComputing()

################## example for diffusion case
        self.function1 = function1()
        self.function2 = function2()
####################

    def fctName(self, name):
        nameSpace = "error"
        for key in self.__dict__:
            if (name == self.__dict__[key].name1) or (name == self.__dict__[key].name2):
                nameSpace = self.__dict__[key].name1
        return nameSpace

    def fctList(self, case):
        processList = list()
        index = list()
        for key in self.__dict__:
            if (case == self.__dict__[key].case):
                if "nb" in self.__dict__[key].__dict__:
                    index.append(self.__dict__[key].nb)
                processList.append(self.__dict__[key].name1)
        if index != []:
            processList = [ processList[index[i]] for i in index]
        return processList


# # ---------------------------------------- ##
class dataPreprocessing():

    def __init__(self):
        self.name1 = "data preprocessing"
        self.name2 = "datapreprocessing"
        self.case = "functional"
        self.scriptDone = "no"
        self.nb = 0

    def writeScript(self, param):
        """ Check or create necessary folders, write matlab sript for expected SPM functions."""

        print "\n=========== MATLAB SCRIPT WRITING ==================================================="

        # add information in temporary text file
        from os import mkdir, path
        textFile = open(param["tempFileName"], "a")
        textFile.write("Overwrite existing files: " + param["overwrite"] + "\n")
        textFile.write("\nChosen SPM functions - reference file in SPM:")
        for p in param["allPreprocess"]:
            textFile.write("\n\t" + p + "\t-\t")
            for t in param["allPreprocessInfo"][0][p].template["name"]:
                textFile.write(t + " ")
        textFile.write("\n\nFunctions status:\n")

        # processes checking
        if len(param["preprocess"]) > 0:
            param["runPreprocess"] = list()
            param["matlabFiles"] = list()
            param["jobsRep"] = list()
            for i, dataset in enumerate(param["examRep"]):
                param["runPreprocess"].insert(i, list())
                param["matlabFiles"].insert(i, "")
                param["jobsRep"].insert(i, "")
                for p in param["allPreprocess"]:
                    if param["run"][i][p] is False:
                        textFile.write("\t- " + p + "\tnot run (data already processed)\n")
                    else:
                        if param["pb"][i][p] is True:
                            textFile.write("\t- " + p + "\tcan't be run (input files not found)\n")
                        else:
                            textFile.write("\t- " + p + "\trun\n")
                            param["runPreprocess"][i].append(p)
                        
                if len(param["runPreprocess"][i]) > 0:
                    
                    # creates new folders
                    if dataset[-1] != "/":
                        dataset = dataset + "/"
                    rep = dataset.split("/")
                    patientDir = ("/").join(rep[0:-3])
                    newDir = [patientDir + "/Final", patientDir + "/Processed", patientDir + "/Processed/" + rep[-2]]
                    newDir.append(patientDir + "/Processed/" + rep[-2] + "/Anat")
                    newDir.append(patientDir + "/Processed/" + rep[-2] + "/Functional")           
                    param["jobsRep"][i] = patientDir + "/Processed/" + rep[-2] + "/Jobs"
                    newDir.append(param["jobsRep"][i])
                    for f in newDir:
                        if path.exists(f) is False:
                            mkdir(f)
                          
                    # matlab script
                    self.matlabFile = patientDir + "/Processed/" + rep[-2] + "/Jobs/" + "preprocessing_" + param["dateTime"] + ".m"
                    from matlabFct import writeScriptMatlab
                    writeScriptMatlab(self.matlabFile, param, i)
                    textFile.write("\nPreprocessing for data in " + dataset + "\n\t-> matlab script: " + self.matlabFile + ".\n")
                else:
                    print "No preprocessing for data in", dataset, "\n\t-> no matlab script written."
                    textFile.write("No preprocessing for data in " + dataset + "\n\t-> no matlab script written.\n")
                    
        textFile.write("\n")
        textFile.close()
        self.scriptDone = "yes"

    def run(self, param):
         
        import subprocess
        
        if self.scriptDone == "no":
            self.writeScript(param)

        print "\n=========== PREPROCESSING ==========================================================="
        for i, dataset in enumerate(param["examRep"]):
            if "runPreprocess" in param:
                if len(param["runPreprocess"][i]) > 0:
                    print "\n-------------------- \ndataset:", dataset
                    # TasksDone.mat update (if exist)
                    tasksNames = "{"
                    for p in param["allPreprocess"]:
                        if p in param["runPreprocess"][i]:
                            # function p will be run
                            tasksNames += "'" + p + "',0;"
                        elif (param["run"][i][p] is False) and (param["pb"][i][p] is False):
                            # function p has already been done
                            tasksNames += "'" + p + "',1;"
                    tasksNames = (tasksNames[0:-1] + "}").replace("_finergrid", ",finergrid")
                    updateTasksDone = "updateTasksDone(" + tasksNames + ",\'" + param["jobsRep"][i] + "\')"
           
                    # matlab command
                    if "matlabPath" in param:
                        runmat = param["matlabPath"] + "matlab -nojvm -nosplash -r \""
                    else:
                        runmat = "matlab -nojvm -nosplash -r \""
                    path1 = "addpath(\'" + param["jobsRep"][i] + "\');"
                    path2 = "addpath(\'" + param["repTools"] + "\');"
                    fct1 = updateTasksDone + ";"
                    fct2 = self.matlabFile.split("/")[-1][0:-2] + ";"
                    quitmat = "quit\""
                    matlabCmd = runmat + path1 + path2 + fct1 + fct2 + quitmat

                    # running script
                    print "Matlab script running at " + strftime("%H:%M:%S")
                    cmd = subprocess.Popen(matlabCmd, shell=True)  # display matlab messages on shell
                    stdoutdata, stderrdata = cmd.communicate()
                    
                    #compatibility for windows
                    import sys
                    if sys.platform == "win32":
                        print("Please wait until the Matlab script is finished, then press any key to continue")
                        import os
                        os.system('pause') 
            else:
                print "\n-------------------- \ndataset:", dataset, "not processed"
        textFile = open(param["tempFileName"], "a")
        textFile.write("Preprocessing done - " + strftime("%H:%M:%S") + "\n")
        textFile.close()

# # ---------------------------------------- ##
class QualityCheck():
    
    def __init__(self):
        self.name1 = "quality check"
        self.name2 = "qualitycheck"
        self.case = "functional"
        self.nextStep = list()
        self.nb = 1
        
    def run(self, param):
        print "\n=========== QUALITY CHECK ==========================================================="
        for i, dataset in enumerate(param["examRep"]):
            print "dataset:", dataset, "\n"
            from checkResults import checkFiles
            self.nextStep.insert(i, checkFiles(param, i, param["option"]))
        param["nextStep"] = self.nextStep

        textFile = open(param["tempFileName"], "a")
        textFile.write("Quality check done - " + strftime("%H:%M:%S") + "\n")
        textFile.write("\tnext step for data sets:\n")
        for i, dataset in enumerate(param["examRep"]):
            if self.nextStep[i]:
                textFile.write("\t" + dataset + "\n")
        textFile.close()

# # ---------------------------------------- ##
class TSExtraction():
    
    def __init__(self, **param):
        self.name1 = "time series extraction"
        self.name2 = "timeseriesextraction"
        self.case = "functional"
        self.nb = 2
        self.templBaseName = "ROI_MNI_V4"
        
        if "tempFileName" in param:
            self.tmpfile = param["tempFileName"]

        if "repR" in param:
            self.repR = param["repR"]
        self.dataset = list()
        self.resultRep = list()
        self.rep = list()
        self.todo = list()
        if "examRep" in param:
            for i, dataset in enumerate(param["examRep"]):
                if dataset[-1] != "/":
                    dataset += "/"
                self.dataset.insert(i, dataset)
                self.resultRep.insert(i, dataset.replace("Original", "Processed"))
                self.rep.insert(i, self.resultRep[-1] + "Functional/")
                self.todo.insert(i, True)               

        if "nextStep" in param:
            self.todo = param["nextStep"]

    def setFolders(self, i):
        from os import mkdir, path
        if path.exists(self.rep[i] + "corrected_data/") is False:
            mkdir(self.rep[i] + "corrected_data/")
        if path.exists(self.rep[i] + "grey_matter_data/") is False:
            mkdir(self.rep[i] + "grey_matter_data/")
        if path.exists(self.rep[i] + "index/") is False:
            mkdir(self.rep[i] + "index/")
        if path.exists(self.rep[i] + "data/") is False:
            mkdir(self.rep[i] + "data/")

    def run(self):
        import rpy2.robjects as robjects
        import glob

        print "\n=========== TIME SERIES ============================================================="       
        for i, dataset in enumerate(self.dataset):            

            if self.todo[i]:
                print "\n-------------------- \ndataset:", dataset, ": time series extraction"
                self.setFolders(i)
                r = robjects.r
                r.source(self.repR + "/const_time_series_template_patients_oro_nifti_functional_Vflore.R")
                r.extractTS(self.repR, dataset, self.resultRep[i], self.templBaseName)
            else:
                print "\n-------------------- \ndataset:", dataset, ": time series extraction not done"

        textFile = open(self.tmpfile, "a")
        textFile.write("Time series extraction done - " + strftime("%H:%M:%S") + "\n")
        textFile.close()

# # ---------------------------------------- ##
class graphComputing():
    def __init__(self, **param):
        self.name1 = "graph computing"
        self.name2 = "graphcomputing"
        self.case = "functional"
        self.nb = 3
        self.nbReg = 90
        
        if "tempFileName" in param:
            self.tmpfile = param["tempFileName"]
        
        if "repR" in param:
            self.repR = param["repR"]
        self.dataset = list()
        self.resultRep = list()
        self.todo = list()
        if "examRep" in param:
            for i, dataset in enumerate(param["examRep"]):
                if dataset[-1] != "/":
                    dataset += "/"
                self.dataset.insert(i, dataset)
                self.resultRep.insert(i, dataset.replace("Original", "Processed"))
                self.todo.insert(i, True)

        if "nextStep" in param:
            self.todo = param["nextStep"]

    def run(self):
        
        import glob
        
        print "\n=========== GRAPH COMPUTING  ========================================================"
        for i, dataset in enumerate(self.dataset):
            if self.todo[i]:                
                print "\n-------------------- \ndataset:", dataset
                nbTimePoint = len(glob.glob(dataset + "/Functional/*.nii"))
                self.ComputeMeasure(i)
                self.DoGraphs(i)
                self.CalculateMoves(i)
            else:
                print "\n-------------------- \ndataset:", dataset, ": graph computing not done"

        textFile = open(self.tmpfile, "a")
        textFile.write("Graph computing done - " + strftime("%H:%M:%S") + "\n")
        textFile.close()

    def ComputeMeasure(self, i):
            import rpy2.robjects as robjects
            r = robjects.r
            print("***** Start compute measures")
            r.source(self.repR + "/computeGraphs.R")

            #compatibility for windows
            import sys
            if sys.platform == "win32":
                import os

                os.mkdir( self.resultRep[i] + "/Graph_Measures/")
            r.compute_MST(self.repR, self.resultRep[i], self.nbReg)
            
    def DoGraphs(self, i):
            import rpy2.robjects as robjects
            r = robjects.r
            print("***** Start do graphs") 
            r.source(self.repR + "/computeGraphs.R")
            r.read_results(self.repR, self.resultRep[i], self.nbReg)

    def CalculateMoves(self, i):
            import rpy2.robjects as robjects
            r = robjects.r
            print("***** Start calculate moves") 
            r.source(self.repR + "/computeGraphs.R")
            r.plot_mvt(self.repR, self.resultRep[i])





################## examples for diffusion caes
            

# # ---------------------------------------- ##
class function1():
    def __init__(self):
        self.name1 = "fonction 1"
        self.name2 = "fonction1"
        self.case = "diffusion"
        

    def run(self, param):
        print self.name1, 'run'
        
# # ---------------------------------------- ##
class function2():
    def __init__(self):
        self.name1 = "fonction 2"
        self.name2 = "fonction2"
        self.case = "diffusion"

