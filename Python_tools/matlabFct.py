##! /usr/bin/env python
## -*- coding: utf-8 -*-

"""This module contains methods to manage matlab instructions used in original scripts run_experiment.m, preprocess.m and pp_loadVolumes.m for data preprocessing by SPM functions.
Those scripts are divided into several parts, named 'segment', 'normalize', 'warp', 'iwarp', 'coregister', 'coregister_interp', 'iwarp,finergrid', 'coregister,finergrid', 'label', 'dartel', 'finergrid'
for steps that can be done by python interface, and 'QC', 'CLASSICSEGMENT', 'NEWSEGMENT' for those not run by python interface.
Matlab script parts are called "functions" in following documentation."""

import sys

## ---------------------------------------- ##
def functions(name):
    """ Check if "name" exists in list fctList, and give for this matlab function all possible sub-functions.

        If entry name is not found in reference list, an error message is displayed and script running interrupts.
        If it is a matlab function name, related elementary functions names are returned in a list.
        Expected values for entry name and related functions list are:
            - 'realign'                 -> ['realign']
            - 'dartel'                  -> ['segment','normalize','warp','iwarp','coregister','coregister_interp']
            - 'segment'                 -> ['segment']
            - 'normalize'               -> ['normalize']
            - 'warp'                    -> ['warp']
            - 'iwarp'                   -> ['iwarp']
            - 'coregister'              -> ['coregister']
            - 'coregister_interp'       -> ['coregister_interp']
            - 'label'                   -> ['label']
            - 'finergrid'               -> ['iwarp_finergrid','coregister_finergrid']
            - 'iwarp_finergrid'         -> ['iwarp_finergrid']
            - 'coregister_finergrid'    -> ['coregister_finergrid']
            - 'all'                     -> ['realign','dartel','segment','normalize','warp','iwarp','coregister','coregister_interp','finergrid','iwarpfinergrid','coregisterfinergrid','label']
                                           returns all possible values for entry name."""

    fctList = ["realign","segment","normalize","warp","iwarp","coregister","coregister_interp","label"]
   
    if name == "all":
        cplList = fctList
        cplList.insert(1,"dartel")
        cplList.insert(8,"finergrid")
        cplList.insert(9,"iwarp_finergrid")
        cplList.insert(10,"coregister_finergrid")
    else:
        if name == "dartel":
            index = [1,2,3,4,5,6]
        elif name == "finergrid":
            index = [4,5]
        elif name == "iwarp_finergrid":
            index = [4]
        elif name == "coregister_finergrid":
            index = [5]
        else:
            try:
                index = [fctList.index(name)]
            except ValueError:
                if len(name) == 0:
                    sys.exit("ERROR: function name empty")
                else:
                    sys.exit("ERROR: function \""+name+"\" not identified")

        cplList = list()
        for i,elt in enumerate(index):
            cplList.insert(i,fctList[elt])
            if name[-9:] == "finergrid":
                cplList[i]+="_finergrid"

    return cplList

## ---------------------------------------- ##
class SPMfct():
    """ Information about each matlab function for data preprocessing.

        For a function "name" (__init__ entry), build an instance with all information available for thise function, like name, input and output files names, etc.
        If precise information are not given (undefined entries **arg in methods __init__, updateTempl, updateFiles), default value are set.
        Attributes are:
            - name          string, function name, see variable fctlist in method functions
            - initFile      string list, input files names, see method updateFiles
            - endFile       string list, output files names, see method updateFiles
            - anatBaseName  string, anatomical file base name, used as reference (see method checkData in module loadAndCheck.py for variable definition)
                            when is not known, symbol "*" is used instead
            - functBaseName string, functional files base name, used as reference (see method checkData in module loadAndCheck.py for variable definition)
                            when is not known, symbol "*" is used instead
            - template      dictionary, information about possible atlas or template file necessary for matlab function execution (see method updateTempl)
            - job           string, matlab file name (batch) related to this function
            - rawDataRep    string, directory to folder of raw data
            - procDataRep   string, directory to folder of processed data
            - repSPM        string, directory to folder of SPM files (see main.py)
            - nb            interger, function numbering
            - parent        string, parent function name ('dartel' or 'finergrid')
        Default value are loaded in __init__ method.

        Warning : parameter dictionary param should contains information on
        one dataset only (i.e. lists param['examRep'] and param['procDataRep']
        are empty or contains one element, if exist). Otherwise only first
        element is used."""
    
    def __init__(self,name,**arg):
        """ Define all attributes and set their default value.
            Call methods updateJob, updateTempl, updateFiles to complete attributes values with available information

            Entry is a string, one of matlab function names in variable fctList in method functions.

            Arguments in dictionary **arg can be:
                - repSPM                    string, directory to folder of SPM files (see main.py)
                - self.template["param"]    see method updateTempl
                - examRep                   see method updateFiles
                - procDataRep               see method updateFiles
                - anatBaseName              see method updateFiles
                - functBaseName             see method updateFiles           
        """
        
        self.name = name            # function name (see fctList in method functions)
        self.initFile = list()      # list of initial files (complete names)
        self.endFile = list()       # list of final files (complete names)
        self.anatBaseName = "*"     # base name of anatomical file
        self.functBaseName = "*"    # base name of functional files
        self.template = dict()      # dictionary of information on template
        self.template["name"] = [""]# list of templates or atlas files
        self.template["param"] = "" # key word in parameter file to search template name related to this function (see loadParam in module readParameterFile), empty if not defined
        self.job = ""               # matlab file name (batch) related to this function (in [matlab functions folder]/jobs/)
        self.rawDataRep = ""        # directory to folder of raw data (in Original/[exam name]/)        
        self.procDataRep = ""       # directory to folder of processed data (in Processed/[exam name]/)
        self.repSPM = ""            # directory to SPM folder
        self.nb = 0                 # function numbering
        self.parent = ""            # parent function name if function name is a sub-function

        if "repSPM" in arg:
            self.repSPM = arg["repSPM"]
            if self.repSPM[-1] != "/":
                self.repSPM += "/"

        self.updateJob()
        self.updateTempl(**arg)
        self.updateFiles(**arg)
        
    def updateJob(self):
        """ Set matlab file names in attribute job.
            Check if function name (attribute name) is one of those expected, otherwise an error message is displayed and script running interrupts."""
        
        if self.name == "realign":
            self.job = "align_job.m"
        elif self.name == "segment":
            self.job = "dartel_segment_vFlore.m"
        elif self.name == "normalize":
            self.job = "dartel_normalise_vFlore.m"
        elif self.name == "warp":
            self.job = "dartel_warp.m"
        elif self.name == "iwarp":
            self.job = "dartel_iwarp.m"
        elif self.name == "coregister":
            self.job = "dartel_coregister.m"
        elif self.name == "coregister_interp":
            self.job = "dartel_coregister_interp.m"
        elif self.name == "iwarp_finergrid":
            self.job = "dartel_iwarp.m"
        elif self.name == "coregister_finergrid":
            self.job = "dartel_coregister.m"
        elif self.name == "label":
            self.job = ""
        else:
            sys.exit("function not identified")

    def updateTempl(self,**arg):
        """ Set information about possible SPM reference file(s) (atlas or template), necessary for function, in dictionary self.template.

            These functions are, with default files (in repSPM repertory):
                - segment               toolbox/Seg/TPM.nii
                - normalize             in toolbox/AtlasMNI: TemGraph1_1.5.img, TemGraph2_1.5.img, TemGraph3_1.5.img, TemGraph4_1.5.img, TemGraph5_1.5.img, TemGraph6_1.5.img
                - iwarp                 toolbox/AtlasMNI/ROI_MNI_V4.nii
                - coregister            toolbox/AtlasMNI/ROI_MNI_V4.nii
                - iwarp_finergrid       toolbox/Atlas/Template.nii
                - coregister_finergrid  toolbox/Atlas/Template.nii
                - label                 toolbox/IBASPM/atlas116.img

            self.template content for each key is:
                - param     key word in parameter file to search template name related to the function (see loadParam in module readParameterFile)
                - name      string list, complete template files names
                - vol       only for function segment, integer list, volume numbering for content of template file

            Arguments in dictionary **arg for each key can be:
                - repSPM                    string, directory to folder of SPM files (see main.py)
                - self.template["param"]    name (see previous list)"""
        
        if self.name == "segment":                  # segment
            self.template["param"] = "templ_segment"
            if self.template["param"] in arg:
                self.template["name"] = arg[self.template["param"]]
            else:
                self.template["name"] = [self.repSPM+"toolbox/Seg/TPM.nii"]
            self.template["vol"] = [[1,2,3,4,5,6]]
        elif self.name == "normalize":              # normalize
            self.template["param"] = "templ_normalize"
            if self.template["param"] in arg:
                self.template["name"] = arg[self.template["param"]]
            else:
                self.template["name"] = ["TemGraph1_1.5.img","TemGraph2_1.5.img","TemGraph3_1.5.img",
                                     "TemGraph4_1.5.img","TemGraph5_1.5.img","TemGraph6_1.5.img"]
                for i,f in enumerate(self.template["name"]):
                    self.template["name"][i] = "/".join([self.repSPM+"toolbox/AtlasMNI",f])
        elif self.name == "iwarp":                  # iwarp
            self.template["param"] = "templ_iwarp"
            if self.template["param"] in arg:
                self.template["name"] = arg[self.template["param"]]
            elif "templ_iwarp_dartel" in arg:
                self.template["name"] = arg["templ_iwarp_dartel"]
            else:
                self.template["name"] = [self.repSPM+"toolbox/AtlasMNI/ROI_MNI_V4.nii"]
        elif self.name == "coregister":             # coregister
            self.name = "iwarp"
            self.updateTempl(**arg)
            self.name = "coregister"
        elif self.name == "iwarp_finergrid":        # iwarp, finergrid
            self.template["param"] = "templ_iwarp_finergrid"
            if self.template["param"] in arg:
                self.template["name"] = arg[self.template["param"]]
            else:
                self.template["name"] = [self.repSPM+"toolbox/Atlas/Template.nii"]
        elif self.name == "coregister_finergrid":   # coregister finergrid*********************************************
            self.name = "iwarp_finergrid"
            self.updateTempl(**arg)
            self.name = "coregister_finergrid"
        elif self.name == "label":                  # label
            self.template["param"] = "templ_label"
            if self.template["param"] in arg:
                self.template["name"] = arg[self.template["param"]]
            else:
                self.template["name"] = [self.repSPM+"toolbox/IBASPM/atlas116.img"]

    def updateFiles(self,**arg):
        """ Set information about input and output files for function running with matlab.

            This method fill initFile and endFile lists with input and output files names related to function name.
            Names are complete (with path and extension). If additional information about repertory or base names are available in entry **arg, file names are as accurate as possible,
            otherwise default names are used, with symbol "*" for unknow parts.

            Depending on function name, default files names are:
                - realign               input:  Functional/*.nii
                                        output: in Functional/Realigned/, mean**.nii, r**.nii, rp_**.txt 
                - segment               input:  Anat/*.nii
                                        output: in Anat/Segmented/, c1*.nii, c2*.nii, c3*.nii, c4*.nii, c5*.nii, rc1*.nii, rc2*.nii, rc3*.nii, rc4.nii, rc5*.nii, *_seg8.mat, iy_*.nii, y_*.nii
                - normalize             input:  Anat/Segmented/rc1*.nii
                                        output: Anat/Segmented/u_rc1*.nii
                - warp                  input:  Anat/*.nii, Anat/Segmented/u_rc1*.nii
                                        output: Anat/w*.nii
                - iwarp                 input:  Anat/Segmented/u_rc1*.nii
                                        output: Anat/Atlased/wROI_MNI_V4_u_rc1*.nii
                - coregister            input:  Anat/*.nii, Anat/Atlased/wROI_MNI_V4_u_rc1*.nii", Functional/Realigned/mean**.nii
                                        output: Anat/nat*.nii, Anat/Atlased/natw*_u_rc1*.nii
                - coregister_interp     input:  Anat/Segmented/c1*.nii", Functional/Realigned/mean**.nii
                                        output: Anat/Segmented/natc1*.nii
                - iwarp_finergrid        input:  Anat/Segmented/u_rc1*.nii"
                                        output: Anat/Atlased/wTemplate_u_rc1*.nii
                - coregister_finergrid   input:  Anat/*.nii, Anat/Atlased/wTemplate_u_rc1*.nii, Functional/Realigned/mean**.nii
                                        output: Anat/nat*.nii, Anat/Atlased/natw*_u_rc1*.nii
                - label                 input:  in Anat/Segmented/, c1*.nii, c2*.nii, c3*.nii, c4*.nii, c5*.nii, iy_*.nii
                                        output: Anat/Atlased/c1*_Atlas.nii

            In some cases (functions iwarp, coregister, iwarp,finergrid, coregister,finergrid), template name is get by method templFileName."""
        
        # look for additional information in param
        if ("examRep" in arg):
            if len(arg["examRep"])>0:
                self.rawDataRep = arg["examRep"][0]
                if self.rawDataRep[-1] != "/":
                    self.rawDataRep = self.rawDataRep+"/"
        if ("procDataRep" in arg) is True:
            self.procDataRep = arg["procDataRep"][0]
            if self.procDataRep[-1] != "/":
                self.procDataRep = self.procDataRep+"/"
        if ("anatBaseName" in arg) is True:
            self.anatBaseName = arg["anatBaseName"]
        if ("functBaseName" in arg) is True:
            self.functBaseName = arg["functBaseName"]           

        # define lists of input and output files
        if self.name == "realign":
            self.initFile = [self.rawDataRep+"Functional/"+self.functBaseName+"*.nii"]
            self.endFile = ["mean"+self.functBaseName+"*.nii","r"+self.functBaseName+"*.nii","rp_"+self.functBaseName+"*.txt"]
            for i,f in enumerate(self.endFile):
                self.endFile[i] = "/".join([self.procDataRep+"Functional/Realigned",f])
                
        elif self.name == "segment":
            self.initFile = [self.rawDataRep+"Anat/"+self.anatBaseName+".nii"]
            self.endFile = ["c1"+self.anatBaseName+".nii","c2"+self.anatBaseName+".nii","c3"+self.anatBaseName+".nii","c4"+self.anatBaseName+".nii","c5"+self.anatBaseName+".nii","rc1"+self.anatBaseName+".nii","rc2"+self.anatBaseName+".nii",
                            "rc3"+self.anatBaseName+".nii","rc4"+self.anatBaseName+".nii","rc5"+self.anatBaseName+".nii",self.anatBaseName+"_seg8.mat","iy_"+self.anatBaseName+".nii","y_"+self.anatBaseName+".nii"]
            for i,f in enumerate(self.endFile):
                self.endFile[i] = "/".join([self.procDataRep+"Anat/Segmented",f])
                
        elif self.name == "normalize":
            self.initFile = [self.procDataRep+"Anat/Segmented/rc1"+self.anatBaseName+".nii"]
            self.endFile = [self.procDataRep+"Anat/Segmented/u_rc1"+self.anatBaseName+".nii"]
            
        elif self.name == "warp":
            self.initFile = [self.rawDataRep+"Anat/"+self.anatBaseName+".nii",self.procDataRep+"Anat/Segmented/u_rc1"+self.anatBaseName+".nii"]
            self.endFile = [self.procDataRep+"Anat/w"+self.anatBaseName+".nii"]
            
        elif self.name == "iwarp":
            self.initFile = [self.procDataRep+"Anat/Segmented/u_rc1"+self.anatBaseName+".nii"]
            self.endFile = [self.procDataRep+"Anat/Atlased/w"+self.templFileName()+"_u_rc1"+self.anatBaseName+".nii"]
            
        elif self.name == "coregister":
            self.initFile = [self.rawDataRep+"Anat/"+self.anatBaseName+".nii",
                             self.procDataRep+"Anat/Atlased/w"+self.templFileName()+"_u_rc1"+self.anatBaseName+".nii",
                             self.procDataRep+"Functional/Realigned/mean"+self.functBaseName+"*.nii"]
            fname = self.initFile[1].split("/")
            self.endFile = [self.procDataRep+"Anat/nat"+self.anatBaseName+".nii",
                            self.procDataRep+"Anat/Atlased/nat"+fname[-1]]

        elif self.name == "coregister_interp":
            self.initFile = [self.procDataRep+"Anat/Segmented/c1"+self.anatBaseName+".nii",self.procDataRep+"Functional/Realigned/mean"+self.functBaseName+"*.nii"]
            self.endFile = [self.procDataRep+"Anat/Segmented/natc1"+self.anatBaseName+".nii"]

        elif self.name == "iwarp_finergrid":
            self.initFile = [self.procDataRep+"Anat/Segmented/u_rc1"+self.anatBaseName+".nii"]
            self.endFile = [self.procDataRep+"Anat/Atlased/w"+self.templFileName()+"_u_rc1"+self.anatBaseName+".nii"]
            
        elif self.name == "coregister_finergrid":
            self.initFile = [self.rawDataRep+"Anat/"+self.anatBaseName+".nii",
                             self.procDataRep+"Anat/Atlased/w"+self.templFileName()+"_u_rc1"+self.anatBaseName+".nii",
                             self.procDataRep+"Functional/Realigned/mean"+self.functBaseName+"*.nii"]
            fname = self.initFile[1].split("/")
            self.endFile = [self.procDataRep+"Anat/nat"+self.anatBaseName+".nii",
                            self.procDataRep+"Anat/Atlased/nat"+fname[-1]]
            
        elif self.name == "label":
            self.initFile = ["c1"+self.anatBaseName+".nii","c2"+self.anatBaseName+".nii","c3"+self.anatBaseName+".nii","c4"+self.anatBaseName+".nii","c5"+self.anatBaseName+".nii","iy_"+self.anatBaseName+".nii"]
            self.endFile = [self.procDataRep+"Anat/Atlased/c1"+self.anatBaseName+"_Atlas.nii"]
            for i,f in enumerate(self.initFile):
                self.initFile[i] = "/".join([self.procDataRep+"Anat/Segmented",f])
                
    def templFileName(self):
        """ Return reference file name (template or atlas, see method updateTempl) without path or extension, from self.template["name"][0]. If result is empty, return symbol "*"."""
        
        fname = self.template["name"][0].split("/")
        n = fname[-1].split(".")
        if n[0] == "":
            n[0] = "*"
        return n[0]

    def duplicate(self):
        """ Return new instance of self, with same values."""

        copy = SPMfct(self.name)
        copy.initFile           = self.initFile
        copy.endFile            = self.endFile
        copy.antBaseName        = self.anatBaseName
        copy.functBaseName      = self.functBaseName
        copy.template           = self.template
        copy.template["name"]   = self.template["name"]
        copy.template["param"]  = self.template["param"]
        copy.job                = self.job
        copy.rawDataRep         = self.rawDataRep
        copy.procDataRep        = self.procDataRep
        copy.repSPM             = self.repSPM
        copy.nb                 = self.nb
        copy.parent             = self.parent
        if "vol" in self.template:
            copy.template["vol"] = self.template["vol"]

        return copy

## ---------------------------------------- ##
def writeScriptMatlab(fileName,param,index):
    """ Writes matlab script for data preprocessing by SPM functions.

        Entries:
            - fileName  matlab script name (complete)
            - param     dictionary of parameters, must contains:
                param["examRep"]            string list, paths to data sets
                param["runPreprocess"]      list, element index gives list of matlab functions to apply
                param["repSPM"]             string, directory to folder of SPM files (see main.py)
                param["repTools"]           string, directory to folder of matlab files (see main.py)
                param["allPreprocess"]      string list, all matlab functions chosen by user to process all data sets
                param["allPreprocessInfo"]  dictionary of SPMfct instances, whose keys are elements of param["allPreprocess"]
            - index     index of dataset to be processed, and of elements in several lists of param ("examRep", "matlaFiles", "runProcess"
        If param["matlabFiles"] or param["examRep"] is empty an error message is displayed and script execution stops.

        Output: matlab script, name is param["matlabFiles"][i]

        Main local variables:
            - filename          matlab script complete name, param["matlabFiles"][index]
            - filenameList      list of folders in filename
            - textFile          matlab script file (param["matlabFiles"][index]), where text is written
            - processList       matlab functions list, param["runPreprocess"][index]
            - dataDir           directory to data set, param["examRep"][index]
            - exam              exam folder name
            - patientDir        directory to patient folder
            - alignFolder       directory to Realigned folder ([patientDir]/Processed/[exam name]/Functional/Realigned)
            - jobsPath          directory to Job folder, for temporary files ([patientDir]/Processed/[exam name]/Job)
            - functPathP        directory to Functional folder, for processed functional file ([patientDir]/Processed/[exam name]/Functional)
            - functPathO        directory to Functional folder, for original functional files (dataDir/Functional)
            - structPathP       directory to Anat folder, for processed anatomical file ([patientDir]/Processed/[exam name]/Anat)
            - structPathO       directory to Anat folder, for original anatomical files (dataDir/Anat)
            - anatBaseName      base name for anatomical file, param["allPreprocessInfo"][index][processList[0]].anatBaseName
            - functBaseName     base name for functional files, param["allPreprocessInfo"][index][processList[0]].functBaseName
            - structFilename    anatomical file name, anatBaseName + extension
            - structFile        complete anatomical file name, structPathO+structFilename
            - writeStep         list of preprocessing steps to write in matlab script (see method functions and textCodeMatlab in codeMatlab.m)

        The matlab script is divided into several parts, and is built to the same design as preprocess.m.
        In this version, all parts are written in matlab file, even those that won't be run. The aim is to create a script that can be run directly with matlab, and user may want to use this script later for other preprocessing, including functions that python interface doesn't support (like classic segment or quality check). That is why all parts are written.
        To simplify this matlab script and write only essential parts, just modify content of writeStep with functions names from variable processList. Then unused parts (instructions in textCodeMatlab in codeMatlab.py and for functions that won't be run) are not written in matlab script.

        In this method, matlab script parts are given in blocks, as follow:
        # ----- part name---------------------------------------
        textFile.write(matlab instructions)
        # ------------------------------------------------------

        Note: if user wants to run matlab script for parts that are not functions managed by python interface, he had to check the code.
            
            """

    # variables setting
    processList = param["runPreprocess"][index]
    dataDir = param["examRep"][index]
    if dataDir[-1] != "/":
        dataDir += "/"
    patientDir = ("/").join(dataDir.split("/")[0:-3])
    exam = dataDir.split("/")[-2]
    alignFolder = patientDir+"/Processed/"+exam+"/Functional/realign/"
    jobsPath    = patientDir+"/Processed/"+exam+"/Job/"
    functPathP  = patientDir+"/Processed/"+exam+"/Functional/"
    functPathO  = patientDir+"/Original/" +exam+"/Functional/"
    structPathP = patientDir+"/Processed/"+exam+"/Anat/"
    structPathO = patientDir+"/Original/" +exam+"/Anat/"  
    anatBaseName = param["allPreprocessInfo"][index][processList[0]].anatBaseName
    functBaseName = param["allPreprocessInfo"][index][processList[0]].functBaseName
    structFilename = anatBaseName+".nii"
    structFile = structPathO+structFilename
    writeStep = ["realign","QC","classicSegment","newSegment","dartel","finergrid","label"]
    
    # display data path and functions to apply on screen
    print "\nData in", dataDir
    print "Processes:",(", ").join(processList)

    # start matlab script writing
    textFile = open(fileName,"w")
    fileNameList = fileName.split("/")

    # ----- file header ------------------------------------    
    textFile.write("% "+fileNameList[-1]+"\n")
    import time
    textFile.write("% "+time.strftime("%A %d %B %Y %H:%M:%S")+"\n\n")   
    textFile.write("disp('** STARTING PROCESSING');\nTstart = clock;\n")
    # ------------------------------------------------------

    # ----- matlab variables -------------------------------
    textFile.write("addpath('"+param["repSPM"]+"');\n")
    textFile.write("addpath('"+param["repTools"]+"');\n")
    varargin = ("\',\'").join(processList).replace("_finergrid",",finergrid")
    textFile.write("varargin = {'procChain',{"+"\'"+varargin+"\'"+"}};\n")        # functions to apply (processList)    
    textFile.write("structPathOrigin = '"+structPathO+"';\n")
    textFile.write("structPath = '"+structPathP+"';\n")
    textFile.write("functPathOrigin = '"+functPathO+"';\n")
    textFile.write("functPath = '"+functPathP+"';\n")
    textFile.write("functBaseName = '"+functBaseName+"';\n")
    textFile.write("anatBaseName = '"+anatBaseName+"';\n")
    textFile.write("structFilename = '"+structFilename+"';\n")
    textFile.write("structFile = '"+structFile+"';\n")
    textFile.write("jobsParentPath = '"+param["repTools"]+"';\n")
    # ------------------------------------------------------
    

    # ----- check and set necessary paths ------------------
    txt = """%% check and set necessary paths
if exist('spm.m','file')~=2
    error('SPM seems not to be on your matlab path.')
else
    spmLoc=spm('Dir');
    myPath=path();

    spmConfigLoc=[spmLoc filesep 'config'];

    if exist(spmConfigLoc,'dir')~=7
        error(['SPM installation seems to be missing a config dir at ' spmConfigLoc ', quitting.']);
    else
        addpath(spmConfigLoc);
    end
end"""
    textFile.write("\n"+txt+"\n")
    # ------------------------------------------------------
    

    # ----- initialize and load data -----------------------
    txt = """%% initialize and load data
spm('defaults', 'fMRI');
pp_loadVolumes_vFlore;"""
    textFile.write("\n"+txt+"\n")
    # ------------------------------------------------------


    # ----- instructions for each step of writeStep --------
    from codeMatlab import textCodeMatlab
    for mainP in writeStep:
        instr = textCodeMatlab(mainP)
        if len(instr)>0:
            textFile.write("\n"+instr+"\n")
        else:
            eltList = list()
            field = [""]
            if mainP == "realign" or mainP == "label":
                eltList = [mainP]
            elif mainP == "dartel":
                eltList = ["segment","normalize","warp","iwarp","coregister","coregister_interp"]
                field = [".segment",".normalize",".warp",".iwarp",".coregister",".coregister_interp"]
            elif mainP == "finergrid":
                eltList = ["iwarp_finergrid","coregister_finergrid"]
                field = [".iwarp",".coregister"]

            for i,elt in enumerate(eltList):
                if elt in param["allPreprocess"]:
                    Fct = param["allPreprocessInfo"][index][elt]
                else:
                    Fct = SPMfct(elt,**param)

                # for matlab : "iwarp,finergrid" and "coregister,finergrid" instead of "iwarp_finergrid" and "coregister_finergrid"
                elt = elt.replace("_finergrid",",finergrid")

                txt = """%% """+mainP+" "+field[i][1:]+"""
if  tasksTodo."""+mainP+field[i]+"""
    %---------------- """+elt+""" -------------------------
    disp(' ----------')
    disp('"""+elt+"""')"""
                textFile.write("\n"+txt)
                if elt != "label":

                    rep = """"""
                    inputs = """"""
                    move = """"""

                    # realign
                    if elt == "realign":
                        rep = """    if ~exist(alignFolder,'dir');mkdir(alignFolder);end;"""
                        inputs = """    inputs = {functFiles'};"""
                        move = """    movefile(fullfile(functPathOrigin,['r*',functBaseName,'*']),alignFolder);
    movefile(fullfile(functPathOrigin,['mean*',functBaseName,'*']),alignFolder);"""

                    # segment
                    elif elt == "segment":
                        rep = """    if ~exist(segFolder,'dir');mkdir(segFolder);end;"""
                        nbm = len(Fct.template["vol"][0])
                        inputs = """    inputs = cell("""+str(nbm+1)+""",1);
    inputs{1} = {structFile};
    for i="""+str(Fct.template["vol"][0])+"""
        inputs{i+1} = {['"""+Fct.template["name"][0]+""",' int2str(i)]};
    end"""
                        
    
                        move = """    movefile(fullfile(structPathOrigin,['*y_',structFilename]), segFolder);
    movefile(fullfile(structPathOrigin,['*c*',structFilename]), segFolder);
    movefile(fullfile(structPathOrigin,[anatBaseName,'_seg8.mat']), segFolder);"""

                    # normalize              
                    elif elt == "normalize":
                        nbm = len(Fct.template["name"])
                        inputs = """    inputs = cell("""+str(nbm+1)+""",1);
    inputs{1} = {fullfile(segFolder,['rc1' structFilename])};    
    """+'\n\t'.join(["inputs{%d} = {'%s'};" % (ind+2,f) for ind,f in enumerate(Fct.template["name"])])

                    # warp
                    elif elt == "warp":
                        rep = """    if ~exist(atlasFolder,'dir');mkdir(atlasFolder);end;"""
                        inputs = """    inputs = cell(2, 1);
    inputs{1} = {fullfile(segFolder,['u_rc1' structFilename])};
    inputs{2} = {fullfile(structPathOrigin,structFilename)};    """
                        move = """    movefile(fullfile(segFolder,['w',structFilename]), structPath);"""

                    # iwarp
                    elif elt[0:5] == "iwarp":
                        rep = """    if ~exist(atlasFolder,'dir');mkdir(atlasFolder);end;"""
                        inputs = """    inputs = cell(2, 1);
    inputs{1} = {fullfile(segFolder,['u_rc1' structFilename])};
    inputs{2} = {'"""+Fct.template["name"][0]+"'};"
                        move = """    movefile(fullfile(segFolder,['w*',structFilename]), atlasFolder);"""

                    # coregister
                    elif elt == "coregister" or elt == "coregister,finergrid":
                        filenamePart = Fct.initFile[1].split("/")
                        filename = filenamePart[-1].split("*")
                        inputs = """    inputs = cell(3, 1);
    inputs{1} = {fullfile(alignFolder, spm_select('List',alignFolder,['^mean.*\.']))};
    inputs{2} = {structFile};
    f = spm_select('List',atlasFolder,'^"""+filename[0]+""".*');
    inputs{3} = {fullfile(atlasFolder,[f,',1'])};"""
                        move = """    movefile(fullfile(structPathOrigin,['nat',structFilename]),structPath);"""

                    # coregister_interp
                    elif elt == "coregister_interp":
                        job = "dartel_coregister_interp.m"
                        inputs = """    inputs = cell(3, 1);
    inputs{1} = {fullfile(alignFolder, spm_select('List',alignFolder,['^mean.*\.']))};
    inputs{2} = {structFile};
    inputs{3} = {fullfile(segFolder, ['c1' structFilename ',1'])};"""
                        move = """    movefile(fullfile(structPathOrigin,['nat',structFilename]),structPath);"""

                    # write text in matlab script for each previous step
                    txt = rep+"\n"
                    txt += "    jobs = {fullfile(jobsParentPath,'jobs','"+Fct.job+"')};\n"
                    txt += inputs+"\n"
                    txt += "    spm_jobman('serial', jobs, '', inputs{:});\n"
                    txt += move+"\n"
                    txt += "    copyfile(jobs{:}, jobFolder);"
                    textFile.write("\n"+txt+"\n")                   

                # new auto labelling         
                elif elt == "label":
                    txt = """    list = spm_select('List',segFolder,['^c.*\.' volExt '$']);
    segmentFiles = cell(size(list,1),1);
    for i = 1:size(list,1)
        segmentFiles{i}= fullfile(segFolder, list(i,:));
    end
    atlasFile = '"""+Fct.template["name"][0]+"""';
    deform = fullfile(segFolder, ['iy_' structFilename]);
    new_Auto_Labelling(segmentFiles, atlasFile, deform, atlasFolder, []);"""
                    textFile.write("\n"+txt+"\n")

                if mainP+field[i] == "dartel.segment":
                    seg = "\n\ttasksDone.segment = DARTEL;"
                else:
                    seg = ""
                txt = """   %---------------- update tasksTodo -------------------------
    tasksDone."""+mainP+field[i]+""" = 1;"""+seg+"""
    save(fullfile(jobFolder, 'tasksDone.mat'), 'tasksDone');"""
                textFile.write("\n"+txt+"\nend\n")
    # ------------------------------------------------------

                
    # ----- end --------------------------------------------
    txt = """%% end
Ttotal=etime(clock, Tstart);
disp(['** DONE PROCESSING. Total time: ' num2str(Ttotal/60,'%3.1f') ' min.']);"""
    textFile.write("\n"+txt+"\n\n\n\n\n")    
    # ------------------------------------------------------

    textFile.close()
