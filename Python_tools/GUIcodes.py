#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Display GUI for parameter setting
# Classes :
#   - mainWindow
#   - WinChooseRep
#   - WinModifList
#   - WinChooseProcess
#   - WinCheckTempl


from Tkinter import *
import tkFileDialog
import glob
import os
import sys
import tkMessageBox
from GUItools import *

# ----------------------------------------------------------------------------------- #
class caseWindow(Tk):
    """ This first class creates a window to make user choose a case between "functional" and "diffusion".
    
        Choice is done by radio button widgets, only one can be selected.
        Default choice is "duffusion".
        If user clicks on "Cancel", execution interrupts.
        If user clicks on "OK", case choice is set in variable param["case"] and window is destroyed.
    """
    
    def __init__(self, master, param):
        """ Class constructor """ 
        Tk.__init__(self, master)
        scnWidth,scnHeight = self.maxsize() # get screen width and height
        tmpcnf = '%dx%d+%d+%d'%(240,100,(scnWidth-300)/2,(scnHeight-200)/2)
        self.geometry(tmpcnf)
        self.master = master
        self.param = param  
        self.initialize(master)
        #self.wm_attributes('-topmost',1)
        """
        self.frame=Frame(self, relief=RAISED, bd=1)
        self.frame.pack(fill=BOTH, expand=1)

        """
    def initialize(self, master):
        """ Creates window, with an instruction label, two radio buttons (unique choice) and buttons "Cancel" and "OK"."""
        """frame=Frame(self, relief=RAISED, bd=1)
        frame.pack(fill=BOTH, expand=1)
        Button(self,text=u"OK",command=self.clickOK).pack(side=BOTTOM, padx=5, pady=5)
        Button(self,text=u"Cancel", command=self.clickCancel).pack()
        
        """
        self.lift()  # display window in foreground
        label = Label(self, text="Choose case:")
        label.grid(column=0, row=0, sticky='w')
        self.case = StringVar()
        c1 = Radiobutton(self, text="diffusion MRI", variable=self.case, value="diffusion")
        c2 = Radiobutton(self, text="functional MRI", variable=self.case, value="functional")
        c1.select()
        c1.grid(column=0, row=1)
        c2.grid(column=1, row=1)
        
        Button(self, text=u"OK", command=self.clickOK).grid(column=1, row=2)
        Button(self, text=u"Cancel", command=self.clickCancel).grid(column=0, row=2)
        
    def clickCancel(self):
        """ Destroy window and stop script execution."""
        print"User Canceled, programme exit(0)"
        sys.exit(0)

    def clickOK(self):
        """ Set case value in param["case"] and destroy window."""
        self.param["case"] = self.case.get()
        self.destroy()        


# ----------------------------------------------------------------------------------- #
class mainWindow(Tk):
    """ Main window for GUI.

    Possible actions:
        - choice between one (case 1) or several (case 2) datasets to process
        - datasets selection (folders containing initial data, in folder Original/)
        - process step selection, denpending on case
        
    Case is linked to data nature : functional MRI or diffusion MRI. This choice has been made in a
    caseWindow instance, and result is given in entry param["case"] (see method __init__).
    Process steps are loaded with method fctList of class allFunctions (see module functionsInfo.py).
    The resulting list depends on value of case.
    
    If case is "functional", process steps are:
        - data preprocessing, by matlab functions (SPM) to choose
        - quality check
        - time series extraction
        - graph computing
    If data preprocessing is chosen, user preprocessing steps are chosen in a new window, see class WinChooseProcess
    in this module. It is also possible to set SPM reference files (templates and atlases) with class WinCheckTempl.
    
    If case is "diffusion", process step are those given in module functionsInfo.py, whom attribute "case" is "diffusion".
        
        
********************************************************        
        
        - preprocessing by SPM selection
        - SPM atlases and templates selection
        - processing steps selection : quality check, times series, compute graphes (to be added)
        - existing files management.

    This class build dictionary param (attribute), which contains the parameters to process the data. See method clickOK for more information.
    The keys are:
        - examRep           list of paths to exam folders for each dataset;
        - process           list of functions names chosen for SPM processing;
        - allProcess        detailled list of functions names chosen for SPM processing;
        - allProcessInfo    list of dictionary of functions informations;
        - run               list of dictionary of boolean values, to know which function apply to which dataset;
        - pb                list of dictionary of boolean values, to know which function can't be applied to which dataset;
        - overwrite         string "y" or "n" to manage existing files (overwrite or not during data processing).

        Attributes:
            - Tkinter attributes
            - master
            - variables :
                - rootRep           root path to top folders arborescence in case of several datasets processing
                - pathoList         pathlogies folders list (complete paths) in case of several datasets processing
                - patientList       patient folders list (complete paths) in case of several datasets processing
                - examList          examination folder list (containing Anat/ and Functional/ folders with data files, complete paths)
                - processList       SPM functions list
                - allProcessDict    dictonary, gives information for each SPM functions, see method getProcessInfo()
                - allProcessList    SPM functions detailled list (keys of allProcessDict)
                - case1             "normal" (if case2 == "disable") or "disable" (if case2 == "normal")
                - case2             "normal" (if case1 == "disable") or "disable" (if case1 == "normal")
                - param             dictionary of process parameters (see main.py)
                - overwrite         "y" or "n", choice to overwrite existing files or not during data processing
            - widgets :
                - canvas            canvas on whole window, associated with local variables frame, vscrollbar, hscrollbar and method scrollWindow to allow horizontal and vertical scrolling if all widgets can't be displayed on main window.
                - case 1, if case1=="disable", these widgets are disabled:
                    - c1instr1      label, instruction exam folder selection
                    - c1instr2      label, help for exam folder selection
                    - c1dir	    listbox for selected dataset
                    - c1Research    button for folder research
                - case 2, if case2=="disable", these widgets are disabled:
                    - root folder:
                        - refinstr1 	label, gives instruction for root folder selection
                        - refinstr2 	label, gives help for root folder selection
                        - reflb 	listbox with root folder path
                        - c2Research1 	button for root folder research
                    - pathologies folders:
                        - pathoinstr1	label, gives instruction for pathologies folders selection
                        - pathoinstr2	label, gives help for pathologies folders selection
                        - pathoadd	button for pathologies folders selection, all folders in root folder are taken
                        - pathoch	button to choose pathologies folders from all folders contained in root folder
                        - pathomod	button to change pathologies folders list (order, size)
                        - pathoclr	button to clear pathologies, patients and exam folders lists
                        - patholb 	listbox with pathologies folders paths
                        - patholbNb	listbox with numbering of pathologies folders list, linked to patholb
                    - patients folders:
                        - patinstr1	label, gives instruction for patients folders selection
                        - patinstr2	label, gives help for patients folders selection
                        - patadd	button for patients folders selection, all folders in pathologies folders are taken
                        - patch		button to choose patients folders from all folders contained in pathologies folders
                        - patmod	button to change patients folders list (order, size)
                        - patclr 	button to clear patients and exam folders lists
                        - patlb 	listbox with patients folders paths
                        - patlbNb	listbox with numbering of patients folders list, linked to patlb
                    - examinations folders:
                        - exinstr1	label, gives instruction for exam folders selection
                        - exinstr2	label, gives help for exam folders selection
                        - exadd	 	button for exam folders selection, all folders in patients folders are taken
                        - exch		button to choose exam folders from all folders contained in patients folders
                        - exmod		button to change exam folders list (order, size)
                        - exclr 	button to clear exam folders list
                        - exlb 		listbox with exam folders paths
                        - exlbNb	listbox with numbering of exam folders list, linked to exlb
                - Process with SPM
                    - proclb	    listbox with function names list (attributes processList)
                    - proclbNb	    listbox with numbering of function names list"""
    
    def __init__(self, master, param):
        """ Class constructor """ 
        Tk.__init__(self, master)
        scnWidth,scnHeight = self.maxsize() # get screen width and height
        if sys.platform == "win32":
            width = 710
            height = 800
        else:
            width = 820
            height = 800
        if scnWidth<width:
            width = scnWidth-60
        if scnHeight<height:
            height = scnHeight-100
        tmpcnf = '%dx%d+%d+%d'%(width,height,(scnWidth-width)/2-20,(scnHeight-height)/2-40)
        self.geometry(tmpcnf)
        self.master = master
        self.rootRep = StringVar()
        self.rootRep.set("")
        self.pathoList = list()
        self.patientList = list()
        self.examList = list()
        self.process = list()
        self.processList = list()  # ["realign","dartel"]
        self.allProcessDict = dict()
        self.allProcessList = list()
        self.allCoordFile = dict()
        self.case1 = StringVar()
        self.case1.set('normal')
        self.case2 = StringVar()
        self.case2.set('disable')
        self.procState = StringVar()
        self.procState.set("disable")
        self.param = param        
        self.initialize(master)
                
    def initialize(self, master):
        """ Display main window.

        The window is divided in several parts:
            - case choice: one or several datasets to process
            - selection of dataset(s)
            - preprocess choice: list of SMP functions to apply, reference files choice, existing files management
            - quit ("OK" or "Cancel")."""

        # general
        self.lift()
        wi = 30  # listboxes width
        he = 5  # listboxes height
        self.DefClr = self.cget("bg")  # default background color
        self.title("~ Parameters setting for " + self.param["case"] + " MRI data ~")
                
        # scrollable window: canvas and frame
        vscrollbar = AutoScrollbar(self)
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = AutoScrollbar(self, orient=HORIZONTAL)
        hscrollbar.grid(row=1, column=0, sticky='ew')

        # create canvas: size is limited to screen dimensions
        hmax = self.winfo_screenheight()
        wmax = self.winfo_screenwidth()
        hwin = min(hmax, 850)
        wwin = min(wmax, 797)
        self.canvas = Canvas(self, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set, width=wwin, height=hwin)
        self.canvas.grid(row=0, column=0, sticky='nsew')        
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        # make the canvas expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # create frame        
        frame = Frame(self.canvas)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.pack(fill=BOTH, expand=1) 
        
        # ----- choose case -------------------------------------------------------------------------------
        label = Label(frame, text="Case:")
        label.grid(column=0, row=0, sticky='w')
        self.case = StringVar()
        c1 = Radiobutton(frame, text="one data set", variable=self.case, value="one", command=self.changeState)
        c2 = Radiobutton(frame, text="several data sets", variable=self.case, value="sev", command=self.changeState)
        c1.select()
        c1.grid(column=0, row=1)
        c2.grid(column=1, row=1)   
               
        # ----- case 1 : one dataset ----------------------------------------------------------------------
        fcase1 = Frame(frame, bd=1, relief='sunken')
        fcase1.grid(column=0, row=2, sticky='nsew')
        self.c1instr1 = Label(fcase1, text="Select the examination folder:", justify=LEFT, state=self.case1.get())
        self.c1instr1.grid(column=0, row=0, sticky='nw')
        if self.param["case"] == "functional":
            c1instr2Text = "Exam folder is a sub-folder of Original/.\nIt contains folders Anat/ and Functional/."
        else:
            c1instr2Text = "Exam folder is a sub-folder of Original/."
        self.c1instr2 = Label(fcase1, text=c1instr2Text, justify=LEFT, fg='#666666', state=self.case1.get())
        self.c1instr2.grid(column=0, row=1, columnspan=2, sticky='nw')
        # examination folder in listbox
        fbg = Frame(fcase1, background='#6699FF', bd=1)
        fbg.grid(column=0, row=2, sticky='sew')
        self.c1dir = Listbox(fbg, selectmode=SINGLE, bd=0, width=wi, bg="#BFCFFE", selectbackground="#BFCFFE", state=self.case1.get(), height=1)
        self.c1dir.grid(column=0, row=0)
        list2listbox(self.c1dir, self.examList)
        scrx = Scrollbar(fcase1, command=self.c1dir.xview, orient=HORIZONTAL)
        scrx.grid(column=0, row=3, sticky='new')
        self.c1dir.config(xscrollcommand=scrx.set)
        # button Research        
        self.c1Research = Button(fcase1, text=u"Research0", command=lambda case="one":self.AddRep(case), anchor='w', state=self.case1.get())
        self.c1Research.grid(column=1, row=2, sticky='sw')

        # ----- case 2 : several datasets ------------------------------------------------------------------
        fcase2 = Frame(frame, width=1000, height=50, bd=1, relief='sunken')
        fcase2.grid(column=1, row=2, sticky='nsew')

        # ----- Reference folder -----  
        # title
        self.refinstr1 = Label(fcase2, text="Select the root folder:", justify=LEFT, state=self.case2.get())
        self.refinstr1.grid(column=0, row=0, sticky='w')
        self.refinstr2 = Label(fcase2, text="Root folder contains all pathologies folders.", justify=LEFT, fg='#666666', state=self.case2.get())
        self.refinstr2.grid(column=0, row=1, columnspan=2, sticky='w')
        # reference folder
        lf = Frame(fcase2)
        lf.grid(column=0, row=2)
        fbg = Frame(lf, background='#6699FF', bd=1)
        fbg.grid(column=0, row=0)
        self.reflb = Listbox(fbg, selectmode=SINGLE, bd=0, width=wi, height=1, bg="#BFCFFE", selectbackground="#BFCFFE", state=self.case2.get())
        self.reflb.grid(column=0, row=0, sticky='w')
        self.updateListbox("root")
        scrx = Scrollbar(lf, command=self.reflb.xview, orient=HORIZONTAL)
        scrx.grid(column=0, row=1, sticky='new')
        self.reflb.config(xscrollcommand=scrx.set)
        # button Research        
        self.c2Research1 = Button(fcase2, text=u"Research", command=lambda case="root":self.AddRep(case), anchor='w', state=self.case2.get())
        self.c2Research1.grid(column=1, row=2)

        # ----- Pathologies folders -----
        # title
        self.pathoinstr1 = Label(fcase2, text="Select pathologies folders:", justify=LEFT, state=self.case2.get())
        self.pathoinstr1.grid(column=0, row=4, sticky='nw')
        self.pathoinstr2 = Label(fcase2, text="Pathology folder contains all patients folders.", justify=LEFT, fg='#666666', state=self.case2.get())
        self.pathoinstr2.grid(column=0, row=5, columnspan=2, sticky='w')
        # buttons
        case1 = "pathology"
        bf = Frame(fcase2)
        bf.grid(column=1, row=6, sticky='nsew')
        self.pathoadd = Button(bf, text=u"All folders", width=8, command=lambda x=case1:self.SelectAllRep(x), state=self.case2.get())
        self.pathoadd.grid(column=0, row=0)
        self.pathoch = Button(bf, text=u"Choose", width=8, command=lambda x=case1:self.AddRep(x), state=self.case2.get())
        self.pathoch.grid(column=0, row=1)
        self.pathomod = Button(bf, text=u"Modify", width=8, command=lambda x=case1:WinModifList(self, x), state=self.case2.get())
        self.pathomod.grid(column=1, row=0)
        self.pathoclr = Button(bf, text="Clear", width=8, command=lambda x=case1:self.ClearList(x), state=self.case2.get())
        self.pathoclr.grid(column=1, row=1)
        # folder(s) list
        lf = Frame(fcase2)
        lf.grid(column=0, row=6, sticky='nsew')
        fbg = Frame(lf, background='#6699FF', bd=1)
        fbg.grid(column=1, row=0, sticky='sew')
        self.patholb = Listbox(fbg, selectmode=SINGLE, bd=0, width=wi, height=he, bg="#BFCFFE", selectbackground="#BFCFFE", state=self.case2.get())
        self.patholb.grid(column=0, row=0, sticky='w')
        self.patholbNb = Listbox(lf, selectmode=SINGLE, bg=self.DefClr, selectbackground=self.DefClr, width=3, height=he, bd=0)
        self.patholbNb.grid(column=0, row=0, sticky='nse')
        self.updateListbox("pathology")
        scrx = Scrollbar(lf, command=self.patholb.xview, orient=HORIZONTAL)
        scrx.grid(column=1, row=1, sticky='new')
        self.patholb.config(xscrollcommand=scrx.set)
        scry = Scrollbar(lf)
        scry.grid(column=2, row=0, sticky='nsw')        
        linkedListboxes(self.patholb, self.patholbNb, scry)
        
        # ----- Patient folders -----
        # title
        self.patinstr1 = Label(fcase2, text="Select patients folders:", justify=LEFT, state=self.case2.get())
        self.patinstr1.grid(column=0, row=7, sticky='nw')
        self.patinstr2 = Label(fcase2, text="Patient folder contains all exam folders in sub-folder Original/.", justify=LEFT, fg='#666666', state=self.case2.get())
        self.patinstr2.grid(column=0, row=8, columnspan=2, sticky='w')
        # buttons
        case2 = "patient"
        bf = Frame(fcase2)
        bf.grid(column=1, row=9, sticky='w')
        self.patadd = Button(bf, text="All folders", width=8, command=lambda x=case2:self.SelectAllRep(x), state=self.case2.get())
        self.patadd.grid(column=0, row=0)
        self.patch = Button(bf, text=u"Choose", width=8, command=lambda x=case2:self.AddRep(x), state=self.case2.get())
        self.patch.grid(column=0, row=1)
        self.patmod = Button(bf, text=u"Modify", width=8, command=lambda x=case2:WinModifList(self, x), state=self.case2.get())
        self.patmod.grid(column=1, row=0)
        self.patclr = Button(bf, text="Clear", width=8, command=lambda x=case2:self.ClearList(x), state=self.case2.get())
        self.patclr.grid(column=1, row=1)
        # folder(s) list
        lf = Frame(fcase2)
        lf.grid(column=0, row=9, sticky='nsew')
        fbg = Frame(lf, background='#6699FF', bd=1)
        fbg.grid(column=1, row=0, sticky='sew')        
        self.patlb = Listbox(fbg, selectmode=SINGLE, bd=0, width=wi, height=he, bg="#BFCFFE", selectbackground="#BFCFFE", state=self.case2.get())
        self.patlb.grid(column=0, row=0, sticky='w')
        self.patlbNb = Listbox(lf, selectmode=SINGLE, bg=self.DefClr, selectbackground=self.DefClr, width=3, height=he, bd=0)
        self.patlbNb.grid(column=0, row=0, sticky='nse')
        self.updateListbox("patient")
        scrx = Scrollbar(lf, command=self.patlb.xview, orient=HORIZONTAL)
        scrx.grid(column=1, row=1, sticky='new')
        self.patlb.config(xscrollcommand=scrx.set)
        scry = Scrollbar(lf)
        scry.grid(column=2, row=0, sticky='nsw')        
        linkedListboxes(self.patlb, self.patlbNb, scry)

        # ----- Exam folders -----
        # title
        self.exinstr1 = Label(fcase2, text="Select examination folders:", justify=LEFT, state=self.case2.get())
        self.exinstr1.grid(column=0, row=10, sticky='nw')
        if self.param["case"] == "functional":
            exinstr2Text = "Exam folder is a sub-folder of Original/.\nIt contains folders Anat/ and Functional/."
        else:
            exinstr2Text = "Exam folder is a sub-folder of Original/."
        self.exinstr2 = Label(fcase2, text=exinstr2Text, justify=LEFT, fg='#666666', state=self.case2.get())
        self.exinstr2.grid(column=0, row=11, columnspan=2, sticky='w')
        # buttons
        case3 = "exam"
        bf = Frame(fcase2)
        bf.grid(column=1, row=12, sticky='w')
        self.exadd = Button(bf, text="All folders", width=8, command=lambda x=case3:self.SelectAllRep(x), state=self.case2.get())
        self.exadd.grid(column=0, row=0)
        self.exch = Button(bf, text=u"Choose", width=8, command=lambda x=case3:self.AddRep(x), state=self.case2.get())
        self.exch.grid(column=0, row=1)
        self.exmod = Button(bf, text=u"Modify", width=8, command=lambda x=case3:WinModifList(self, x), state=self.case2.get())
        self.exmod.grid(column=1, row=0)
        self.exclr = Button(bf, text="Clear", width=8, command=lambda x=case3:self.ClearList(x), state=self.case2.get())
        self.exclr.grid(column=1, row=1)
        # folder(s) list
        lf = Frame(fcase2)
        lf.grid(column=0, row=12, sticky='nsew')
        fbg = Frame(lf, background='#6699FF', bd=1)
        fbg.grid(column=1, row=0, sticky='sew')
        self.exlb = Listbox(fbg, selectmode=SINGLE, bd=0, width=wi, height=he, bg="#BFCFFE", selectbackground="#BFCFFE", state=self.case2.get())
        self.exlb.grid(column=0, row=0, sticky='w')
        self.exlbNb = Listbox(lf, selectmode=SINGLE, bg=self.DefClr, selectbackground=self.DefClr, width=3, height=he, bd=0)
        self.exlbNb.grid(column=0, row=0, sticky='nse')        
        self.updateListbox("exam")
        scrx = Scrollbar(lf, command=self.exlb.xview, orient=HORIZONTAL)
        scrx.grid(column=1, row=1, sticky='new')
        self.exlb.config(xscrollcommand=scrx.set)
        scry = Scrollbar(lf)
        scry.grid(column=2, row=0, sticky='nsw')        
        linkedListboxes(self.exlb, self.exlbNb, scry)        

        # ----- Data processes -----------------------------------------------------------------------------
        self.fproc = Frame(frame, bd=1, relief='sunken')
        self.fproc.grid(column=0, row=3, columnspan=2, sticky='nsew')
        self.processChoice()
        if self.param["case"] == "functional":
            self.coordChoice()
                
        # ----- Quit ---------------------------------------------------------------------------------------
        fquit = Frame(frame)
        fquit.grid(column=1, row=6, sticky='nsew')
        Button(fquit, text=u"OK", command=self.clickOK).grid(column=1, row=0)
        Button(fquit, text=u"Cancel", command=self.clickCancel).grid(column=0, row=0)
        
        
        # mouse wheel events and binding to vertical scrolling window (all frames and widgets)
        # event name depends on platform
        import platform
        ans = (platform.platform()).lower()
        if ans.find('linux') != -1:
            self.pltf = "lx"
            self.scrollUp = "<Button-4>"
            self.scrollDown = "<Button-5>"
        elif ans.find('windows') != -1:
            self.pltf = "win"
            self.scrollUp = "<MouseWheel>"
            self.scrollDown = "<MouseWheel>"
        else:
            self.pltf = "mac"
            self.scrollUp = "<MouseWheel>"
            self.scrollDown = "<MouseWheel>"
        self.bind_all(self.scrollUp, self.scrollWindow)
        self.bind_all(self.scrollDown, self.scrollWindow)
        
        # canvas and frame settings
        self.canvas.create_window(0, 0, anchor='nw', window=frame)        
        frame.update_idletasks()        
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
    def processChoice(self):
        
        Label(self.fproc, text="Data processing:").grid(column=0, row=0, sticky='nsw')
        ffct = Frame(self.fproc)
        ffct.grid(column=0, row=1, sticky='nsew')
        fdetails = Frame(self.fproc, bd=1, relief='sunken')
        fdetails.grid(column=1, row=1, sticky='nse')
        
        from functionsInfo import allFunctions
        fctInfo = allFunctions()
        self.fctList = fctInfo.fctList(self.param["case"]) 
        self.chosenFct = list()
        self.fctWidget = list()
        
        # button 1 : "all"
        self.chosenFct.insert(0, IntVar())
        self.fctWidget.insert(0, Checkbutton(ffct, text="all", variable=self.chosenFct[0], command=self.updateFctList))
        self.fctWidget[0].grid(column=2, row=1, sticky='nsw')
        
        # following buttons: functions names
        for i, f in enumerate(self.fctList):
            self.chosenFct.insert(i + 1, IntVar())
            self.fctWidget.insert(i + 1, Checkbutton(ffct, text=f, variable=self.chosenFct[i + 1], command=self.updateFctList))
            self.fctWidget[i + 1].grid(column=2, row=i + 2, sticky='nsw')
            
        # functional case: SPM functions selection
        if self.param["case"] == "functional":
            self.preprocTitle = Label(fdetails, text="data preprocessing by SPM8:", state=self.procState.get())
            self.preprocTitle.grid(column=0, row=0, columnspan=2, sticky='nsw')
            # label and button
            self.preprocModify = Button(fdetails, text=u"Modify list", command=self.chooseProcess, state=self.procState.get())
            self.preprocModify.grid(column=2, row=2)
            # preprocesses List
            flb = Frame(fdetails)
            flb.grid(column=1, row=2, rowspan=3, sticky='wns')
            fbg = Frame(flb, background='#6699FF', bd=1)
            fbg.grid(column=1, row=0, sticky='wns')
            fbg.columnconfigure(0, weight=1)
            fbg.rowconfigure(0, weight=1)
            self.proclb = Listbox(fbg, selectmode=SINGLE, bg="#BFCFFE", selectbackground="#BFCFFE", width=15, height=10, bd=0, state=self.procState.get())
            self.proclb.grid(column=0, row=0, sticky='wns')
            self.proclbNb = Listbox(flb, selectmode=SINGLE, bg=self.DefClr, selectbackground=self.DefClr, width=3, height=10, bd=0, state=self.procState.get())
            self.proclbNb.grid(column=0, row=0, sticky='nsw')
            self.updateListbox("process")        
            # template & atlas   
            self.preprocInstr = Label(fdetails, text="Set SPM reference file(s),\nlike template or atlas,\nfor each function:", justify='center', anchor="s", state=self.procState.get())
            self.preprocInstr.grid(column=2, row=3, sticky='w')
            self.preprocButton = Button(fdetails, text=u"click here", command=self.defineTempl, state=self.procState.get())
            self.preprocButton.grid(column=2, row=4)
            # for existing files
            fow = Frame(fdetails)
            fow.grid(column=0, row=5, columnspan=3, sticky='nsw')
            self.preprocOverW = Label(fow, text="Overwrite existing file(s)?", state=self.procState.get())
            self.preprocOverW.grid(column=0, row=0, sticky='nsw')
            self.overwrite = StringVar()
            self.preprocR1 = Radiobutton(fow, text="Yes", variable=self.overwrite, value="y", state=self.procState.get())
            self.preprocR2 = Radiobutton(fow, text="No" , variable=self.overwrite, value="n", state=self.procState.get())
            self.preprocR2.select()
            self.preprocR1.grid(column=1, row=0)
            self.preprocR2.grid(column=2, row=0)

    def coordChoice(self):
        fdetails2 = Frame(self.fproc, bd=1, relief='sunken')
        fdetails2.grid(column=3, row=1, sticky='nse')
        self.coordChoiceTitle = Label(fdetails2, text="Set Coordinates file(s) \n for each template \n(for Graph computing)", state=self.procState.get())
        self.coordChoiceTitle.grid(column=3, row=3, sticky='nsw')
        self.coordButton = Button(fdetails2, text=u"click here", command=self.defineCoord, state=self.procState.get())
        self.coordButton.grid(column=3, row=4)
    def updateFctList(self):
        
        self.process = list()
        if self.chosenFct[0].get() == 1:
            for i, f in enumerate(self.fctList):
                self.fctWidget[i + 1].select()

        for i, f in enumerate(self.fctList):
            if self.chosenFct[i + 1].get() == 1:
                self.process += [self.fctList[i]]
                
            # case "data preprocessing" for functional MRI: set state of corresponding widgets
            if self.fctList[i] == "data preprocessing":
                if self.chosenFct[i + 1].get() == 1:
                    self.procState.set("normal")
                else:
                    self.procState.set("disable")
                # update state
                self.preprocTitle.config(state=self.procState.get())
                self.preprocModify.config(state=self.procState.get())
                self.proclb.config(state=self.procState.get())
                self.proclbNb.config(state=self.procState.get())
                self.preprocInstr.config(state=self.procState.get())
                self.preprocButton.config(state=self.procState.get())
                self.preprocOverW.config(state=self.procState.get())
                self.preprocR1.config(state=self.procState.get())
                self.preprocR2.config(state=self.procState.get())  
            if self.fctList[i] == "graph computing":
                if self.chosenFct[i + 1].get() == 1:
                    self.procState.set("normal")
                else:
                    self.procState.set("disable")
                    
                self.coordChoiceTitle.config(state=self.procState.get())
                self.coordButton.config(state=self.procState.get())
    def scrollWindow(self, event):
        """ Vertical scrolling window with mouse wheel.
        /!\ to be tested for windows        """
        
        if self.pltf == "lx":
            if event.num == 4:
                ev = -1
            elif event.num == 5:
                ev = 1
        elif self.pltf == "win":
            ev = event.delta / 120
        else:
            ev = -1 * event.delta
        self.canvas.yview("scroll", ev, "units")
        return "break"
                
    def getProcessInfo(self):
        """ Get information for each SPM functions in self.processList list. Return information in dictionnary self.allProcessDict, whose keys are function name and whose values are the corresponding SPMfct class objects (see SPMfct in module matlabFct).
            If directories to SPM and other Matlab functions is not correctly defined in inintial self.param, user is asked to set new ones, and they are set in self.param["repTools"] and self.param["repSPM"]."""
        from matlabFct import functions, SPMfct
        for fct in self.processList:
            fctList = functions(fct)
            
            # check if SPM folder exist, and set it if not
            if "repSPM" in self.param:
                if self.param["repSPM"] == "":
                    self.param["repSPM"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Please select a directory for SPM:')
                else:
                    if not os.path.isdir(os.path.abspath(self.param["repSPM"]) + '/'):
                        print os.path.abspath(self.param["repSPM"]) + '/'
                        self.param["repSPM"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Wrong directory for SPM, please select another one:') 
            else:
                self.param["repSPM"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Please select a directory for SPM:')
            
            # check if MATLAB tools folder exist, and set it if not
            if "repTools" in self.param:
                if self.param["repTools"] == "":
                    self.param["repTools"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Please select a directory for MATLAB tools:')
                else:
                    if not os.path.isdir(self.param["repTools"]):
                        self.param["repTools"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Wrong directory for MATLAB tools, please select another one:') 
            else:
                self.param["repTools"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Please select a directory for MATLAB tools:')
            
            # loading SPM functions information            
            for i, f in enumerate(fctList):
                self.allProcessDict[f] = SPMfct(f, **self.param)
                self.allProcessDict[f].nb = i
                self.allProcessDict[f].parent = fct

    def defineTempl(self):
        """ Template and atlas choice for each SPM functions in self.allProcessList list. Call WinCheckTempl class object."""
        if (self.processList != []) and (self.processList != ()):
            WinCheckTempl(self)
    def defineCoord(self):
        """"""
        if len(self.processList) !=0 or len(self.examList) !=0:
            WinSetCoord(self)
        else:
            tkMessageBox.showwarning(title="Warning", message="No data folder!\nGive at least one directory to dataset.")
            
    def changeState(self):
        """ Changes widgets state (normal or disable) for the repertories selection, depending on the choice of case :
                - if attribute case is "one" (case 1), attributes case1 is set to 'normal', attributes case2 to 'disable' and root, pathologies, patients and exam folders lists are cleared;
                - if attribute case is "sev" (case 2), attributes case2 is set to 'normal', attributes case1 to 'disable' and exam folders list is cleared."""
        if self.case.get() == "sev":
            self.case1.set('disable')
            self.case2.set('normal')
            list2listbox(self.c1dir, [""])            
            self.ClearList("exam")
        elif self.case.get() == "one":
            self.case2.set('disable')
            self.case1.set('normal')
            list2listbox(self.reflb, [""])
            self.ClearList("pathology")
            self.examList.insert(0, StringVar())
            self.rootRep.set("")        
        self.c1instr1.config(state=self.case1.get())
        self.c1instr2.config(state=self.case1.get())
        self.c1dir.config(state=self.case1.get())
        self.c1Research.config(state=self.case1.get())
        self.refinstr1.config(state=self.case2.get())
        self.refinstr2.config(state=self.case2.get())
        self.reflb.config(state=self.case2.get())
        self.c2Research1.config(state=self.case2.get())
        self.pathoinstr1.config(state=self.case2.get())
        self.pathoinstr2.config(state=self.case2.get())
        self.pathoadd.config(state=self.case2.get())
        self.pathoch.config(state=self.case2.get())
        self.pathomod.config(state=self.case2.get())
        self.pathoclr.config(state=self.case2.get())
        self.patholb.config(state=self.case2.get())
        self.patholbNb.config(state=self.case2.get())
        self.patinstr1.config(state=self.case2.get())
        self.patinstr2.config(state=self.case2.get())
        self.patadd.config(state=self.case2.get())
        self.patch.config(state=self.case2.get())
        self.patmod.config(state=self.case2.get())
        self.patclr.config(state=self.case2.get())
        self.patlb.config(state=self.case2.get())
        self.patlbNb.config(state=self.case2.get())
        self.exinstr1.config(state=self.case2.get())
        self.exinstr2.config(state=self.case2.get())
        self.exadd.config(state=self.case2.get())
        self.exch.config(state=self.case2.get())
        self.exmod.config(state=self.case2.get())
        self.exclr.config(state=self.case2.get())
        self.exlb.config(state=self.case2.get())
        self.exlbNb.config(state=self.case2.get())

    def AddRep(self, case):
        """ Open new window for folders selection.

            If entry case is "one" or "root", the displayed window allows repertory navigation to select one folder.
            Otherwise the new window is a WinChooseRep object.
            In all cases, the listbox corresponding to the case is updated with new folders list."""        
        if self.case.get() == "one":
            t = tkFileDialog.askdirectory(parent=self.master, initialdir="~/Documents/NetBeansProjects/rootPatient/Patient/Patient1/Original/Exam0", title='Please select a directory')
            if t != "":
                del self.examList
                self.examList = list()
                self.examList.insert(0, t)
                list2listbox(self.c1dir, self.examList)
        elif case == "root":
            self.rootRep.set(tkFileDialog.askdirectory(parent=self.master, initialdir="~/Documents/", title='Please select a directory'))
            self.updateListbox("root")
        else:
            WinChooseRep(self, case)

    def updateListbox(self, case):
        """ Update folders or functions names lists and numbering in window, depending on entry "case"."""
        if case == "pathology":
            list2listbox(self.patholb, self.pathoList)
            numListbox2listbox(self.patholb, self.patholbNb)
        elif case == "patient":
            list2listbox(self.patlb, self.patientList)
            numListbox2listbox(self.patlb, self.patlbNb)
        elif case == "exam":
            list2listbox(self.exlb, self.examList)
            numListbox2listbox(self.exlb, self.exlbNb)
        elif case == "process":
            list2listbox(self.proclb, self.processList)
            numListbox2listbox(self.proclb, self.proclbNb)
        elif case == "root":
            list2listbox(self.reflb, [self.rootRep])

    def SelectAllRep(self, case):
        """ For a given case (entry "case"), select all folders contained in parent folder(s).

            If case == "pathology", parent folder (unique) is self.rootRep. Set new folders in self.patholist.
            If case == "patient", parent folders are in self.patholist. Set new folders in self.patientList.
            If case == "exam", parent folders are in self.patientList. Set new folders in self.examList.
            Corresponding listbox is updated."""
        if case == "pathology":
            del self.pathoList
            self.pathoList = list()
            content = glob.glob(self.rootRep.get() + "/*")
            for i in content:
                if os.path.isdir(i) is True:
                    self.pathoList.append(i.replace('\\','/'))
        elif case == "patient":
            del self.patientList
            self.patientList = list()
            for f in self.pathoList:
                content = glob.glob(f + "/*")
                for i in content:
                    if os.path.isdir(i) is True:
                        self.patientList.append(i.replace('\\','/'))
        elif case == "exam":
            del self.examList
            self.examList = list()
            for f in self.patientList:
                content = glob.glob(f + "/Original/*")
                for i in content:
                    if os.path.isdir(i) is True:
                        self.examList.append(i.replace('\\','/'))
        self.updateListbox(case)

    def ClearList(self, case):
        """ Clear lists and listboxes corresponding to entry "case".

            If case is "pathology", pathoList, patientList and examList are cleared.
            If case is "patient", patientList and examList are cleared.
            If case is "exam", only examList is cleared."""
        if case == "pathology":
            del self.pathoList
            self.pathoList = list()
            self.updateListbox(case)
            self.ClearList("patient")
            self.ClearList("exam")
        elif case == "patient":
            del self.patientList
            self.patientList = list()
            self.updateListbox(case)
            self.ClearList("exam")
        elif case == "exam":
            del self.examList
            self.examList = list()
            self.updateListbox(case)
            
    def chooseProcess(self):
        """ Call WinChooseProcess class object to choose dataset(s) processes by SPM."""
        WinChooseProcess(self)

    def clickCancel(self):
        """ Destroy window and stop process execution."""
        sys.exit("Cancel")

    def clickOK(self):
        """ Save folders and chosen functions lists, close window.

            If there is no exam folder, a warning window is displayed and main window is not destroyed.
            Folder(s) choice is checked by method checkFolderTree (module loadAndCheck). If there is error message, a warning window is displayed and main
            window is not destroyed. See checkFolderTree for details.
            Matlab function(s) choice is checked by method checkProcess (module loadAndCheck) to verify if chosen functions can be run on each dataset. If not, a
            warning window is displayed and main window is not destroyed. See checkProcess for details.
            Before closing window, new parameters in dictionary "param" are created:
                - param["examRep"]          list of exam folders for each dataset to be processed;
                - param["overwrite"]        string "y" or "n" to manage existing files (overwrite or not during data processing);
                - param["process"]          list of functions names chosen for SPM processing;
                - param["repR"]             directory to R scripts, if needed and if was not correctly defined in inintial self.param
                - param["allProcess"]       detailled list of functions names chosen for SPM processing;
                - param["allProcessInfo"]   list of dictionary of functions informations.
                                            Each element of list param["allProcessInfo"] is related to a path in param["examRep"].
                                            Keys of i-th dictionary param["allProcessInfo"][i] are functions names of list param["allProcess"].
                                            Content of this dictionary is a SPMfct object (see class SPMfct in module matlabFct), updated with information about the dataset (i-th path of param["examRep"]) and each function;
                - param["run"]              list of dictionary of boolean values, same structure as param["allProcessInfo"];
                                            Each element of list param["run"] is related to a path in param["examRep"].
                                            Keys of i-th dictionary param["run"][i] are functions names of list param["allProcess"].
                                            Value of param["run"][i][f] (dataset i and function f) is TRUE if function have to be applied to this dataset, or FALSE otherwise (see checkProcess);
                - param["pb"]               list of dictionary of boolean values, same structure as param["allProcessInfo"];
                                            Each element of list param["pb"] is related to a path in param["examRep"].
                                            Keys of i-th dictionary param["pb"][i] are functions names of list param["allProcess"].
                                            Value of param["pb"][i][f] (dataset i and function f) is TRUE if function can't to be applied to this dataset (if initial files are not aavailable), or FALSE otherwise (see checkProcess).
                                            While param["pb"][i][f] is TRUE, main window can't be closed, and user have to modify dataset choice and/or functions choice."""

        # directory to data sets
        self.param["examRep"] = []
        if len(self.examList) == 0:
            tkMessageBox.showwarning(title="Warning", message="No data folder!\nGive at least one directory to dataset.")
        elif self.examList[0] == "":
            tkMessageBox.showwarning(title="Warning", message="No data folder!\nGive at least one directory to dataset.")
        else:
            
            e = "ok"
            txt = ""

            # case 1: diffusion MRI
            # exam folders have to be in folder called Original
            if self.param["case"] == "diffusion":
                for p in self.examList:
                    if p.split("/")[-2] != "Original":
                        e = "error"
                        txt += p.split("/")[-1] + " not in folder Original/ as expected\n"
                if e == "error":
                    tkMessageBox.showwarning(title="Warning", message="Error in exam folder:\n" + txt)
                # save parameters and quit
                elif e == "ok":
                    for p in self.examList:
                        self.param["examRep"] += [p]
                    self.param["process"] = self.process
                    self.destroy()

            # case 2: functional MRI
            # exam folders have to be in folder called Original
            #                      contain folders called Anat and Functional
            else:                    
                from loadAndCheck import checkFolderTree
                msg, dataInfo = checkFolderTree(self.examList)
                for i, m in enumerate(msg):
                    if m[0:5] == "ERROR":
                        e = "error"
                        txt += " - Path " + self.examList[i] + "\n" + m + "\n"
                if e == "error":
                    tkMessageBox.showwarning(title="Warning", message="Errors in exam folder(s):\n" + txt)
                elif e == "ok":
                    # check preprocessing order and initial files
                    from loadAndCheck import checkProcess
                    run, pb, allPreprocessInfo = checkProcess(self.allProcessList, self.allProcessDict, self.examList, dataInfo, self.overwrite.get())
                    for i, f in enumerate(self.examList):
                        for p in self.allProcessList:
                            if pb[i][p]:
                                txt += "can't run function " + p + " with data in " + f + "\n"
                    if txt != "":
                        tkMessageBox.showwarning(title="Warning", message="Errors in functions choice:\n" + txt + "Check function order.")
                        del run, pb, allPreprocessInfo
                    
                    # save parameters and quit
                    else:
                        
                        # check if R functions folder exist, and set it if not
                        if ("time series extraction" in self.process) or ("graph computing" in self.process):
                            if "repR" in self.param:
                                if self.param["repR"] == "":
                                    self.param["repR"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Please select a directory for R scripts:')
                                else:
                                    if not os.path.isdir(self.param["repR"]):
                                        self.param["repR"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Wrong directory for R scripts, please select another one:')                                    
                            else:
                                self.param["repR"] = tkFileDialog.askdirectory(parent=self.master, initialdir="/", title='Please select a directory for R scripts:')
                        if "graph computing" in self.process and len(self.allCoordFile) == 0:
                            tkMessageBox.showwarning(title="Warning", message= "Please choose coordinates file(s) for graph computing")
                        else:
                            for p in self.examList:
                                self.param["examRep"] += [p]
                            self.param["overwrite"] = self.overwrite.get()
                            self.param["process"] = self.process
                            self.param["preprocess"] = self.processList
                            self.param["allPreprocess"] = self.allProcessList
                            self.param["allCoordFile"] = self.allCoordFile.copy()
                            self.param["allPreprocessInfo"] = allPreprocessInfo
                            self.param["run"] = run
                            self.param["pb"] = pb                   
                            self.destroy()
                       
            
# ----------------------------------------------------------------------------------- #
class WinChooseRep(Toplevel):
    """ Window for folder(s) selection, from parent folder. Main window is updated when "OK" is clicked.

        There are several cases:
        1. case == "pathology":
            - parent folders are in master.rootRep
            - folders chosen are added to master.pathoList
            - master.patholb and master.patholbNb in main window are updated
        2. case == "patient":
            - parent folders are in master.pathoList
            - folders chosen are added to master.patientList
            - master.patlb and master.patlbNb in main window are updated
        3. case == "exam":
            - parent folders are in repertory Original/ of all folder in master.patientList
            - folders chosen are added to master.examList
            - master.exlb, master.exlbNb are updated

        Principle:
        Parents folders are loaded in attribute "parent" (list) and displayed in listbox listbParent. When a folder is selected, the content (only repertories) appears in listbox listbContent (method extractContent). Then the user can select one or several folders in listbContent, they are added to dictionary selFolderDict where keys are parent folders names (method selectChild). When the user clicks on "OK" button, these folders are added to related master attributes.

        Attributes:
        - Tkinter and Toplevel attributes
        - case              "pathology", "patient" or "exam", same as entry "case"
        - parent            parent folders list (see above)
        - content           list, content of selected parent folders list
        - selection         dictionary: keys are parent folders selected and content are indexes of corresponding selected child folders
        - selFolderDict     dictionary: keys are parent folders selected and content are corresponding selected child folders
        - widgets (see initialize method):
            - listbParent   listbox
            - listbContent  listbox"""

    def __init__(self, master, case):
                
        Toplevel.__init__(self, master)
        self.master = master
        self.case = case
        self.parent = list()
        self.content = list()
        self.content.insert(0, "")
        self.selection = dict()
        self.selFolderDict = dict()
        if self.case == "pathology":
            self.parent.insert(0, self.master.rootRep.get())
        elif self.case == "patient":
            for i, f in enumerate(self.master.pathoList):
                self.parent.insert(i, f)
        elif self.case == "exam":
            # Show only rep exist
            for i, f in enumerate(self.master.patientList):
                if os.path.isdir(f + "/Original/") is True:
                    if sys.platform == "win32":
                        self.parent.insert(i, f.replace('\\','/') + "/Original")
                    else:
                        self.parent.insert(i, f + "/Original")

        self.initialize(master)

    def initialize(self, master):
        """ Display window.

            Widgets list (order of appearance in the script):
                - label             instructions for parent folders
                - fbg               frame for listbParent
                - listbParent       listbox, display listbParent (parent folders)
                - scrollbarx        horizontal scrollbar linked to listbParent
                - label             instructions for content
                - fbg               frame for listbContent
                - listbContent      listbox, display content (content of selected parent folder)
                - scrollbarx        horizontal scrollbar linked to listbContent
                - scrollbary        vertical scrollbar linked to listbContent
                - button "OK"       button to save selection list and close window
                - button "Cancel"   button to close window without saving.
            """
        
        self.title("Select folders")

        # parent folders : listbox
        Label(self, text="Parent folder(s): select to see content", justify='right', anchor="w").grid(column=0, row=0, sticky='w')
        fbg = Frame(self, background='#6699FF', bd=1)
        fbg.grid(column=0, row=1, sticky='w')
        self.listbParent = Listbox(fbg, selectmode=BROWSE, bd=0, height=len(self.parent), width=50, bg="#BFCFFE", selectbackground="#6699FF")
        self.listbParent.config(exportselection=0)
        list2listbox(self.listbParent, self.parent)
        self.listbParent.grid(column=0, row=0, sticky='w')
        scrollbarx = Scrollbar(self)
        scrollbarx.grid(column=0, row=2, sticky='new')       
        self.listbParent.config(xscrollcommand=scrollbarx.set)
        scrollbarx.config(command=self.listbParent.xview, orient=HORIZONTAL)
        self.listbParent.bind("<ButtonRelease-1>", self.extractContent)

        # possible folders : listbox
        Label(self, text="Select " + self.case + " folder(s):", justify='right', anchor="w").grid(column=0, row=3, sticky='w')
        fbg = Frame(self, background='#6699FF', bd=1)
        fbg.grid(column=0, row=4, sticky='w')
        self.listbContent = Listbox(fbg, selectmode=EXTENDED, bd=0, width=50, bg="#BFCFFE", selectbackground="#6699FF")
        self.listbContent.config(exportselection=0)
        self.extractContent()
        for f in self.content:
            self.listbContent.insert(END, f)
        self.listbContent.grid(column=0, row=0, sticky='w')
        scrollbarx = Scrollbar(self)
        scrollbarx.grid(column=0, row=5, sticky='new')
        scrollbary = Scrollbar(self)
        scrollbary.grid(column=1, row=4, sticky='nsw')
        self.listbContent.config(xscrollcommand=scrollbarx.set, yscrollcommand=scrollbary.set)
        scrollbarx.config(command=self.listbContent.xview, orient=HORIZONTAL)
        scrollbary.config(command=self.listbContent.yview)
        self.listbContent.bind("<ButtonRelease-1>", self.selectChild)

        # Cancel & OK
        Button(self, text="Cancel", command=self.destroy).grid(column=0, row=6, sticky='sw')
        Button(self, text="OK", command=self.clickOK).grid(column=1, row=6, sticky='sw')

    def extractContent(self, *x):
        """ For selected parent folder (highlighted), create list of all folders included and display it in listbContent.

    This method takes in account previous folder selections.
    Local variables:
        - itemParent    index of selected folder in listbParent
        - rep           selected folder name
        - ContentList   rep content complete list.
    When a parent folder rep is selected, this method extracts content of rep and checks if rep exists in selection. If there isn't rep in this list, the method creates a list in selection[rep] and selFolderDict[rep] and calls method selectChild. This method updates selected children folders lists. Then each folder of ContentList is set in content list. The listbox listbContent is updated to new list ContentList and if a selection has already been made (selection[rep] is not empty), chosen folders names are highlighted in listbContent.
    Entry x is related to event <ButtonRelease-1> (variable not used)."""

        itemParent = map(int, self.listbParent.curselection())
        if itemParent != []:
            rep = self.listbParent.get(itemParent[0])
            ContentList = glob.glob(rep + "/*")
            if (rep in self.selection) is False:
                self.selection[rep] = list()
                self.selFolderDict[rep] = list()
                self.selectChild()
            self.content = []
            for i, f in enumerate(ContentList):
                if os.path.isdir(f) is True:
                    self.content.insert(-1, f)                    
            if len(self.content) < 1:
                self.content.insert(0, "")
            self.listbContent.delete(first=0, last=END)
            for f in self.content:
                self.listbContent.insert(END, f)
            if self.selection[rep] != []:
                for i in self.selection[rep]:
                    self.listbContent.selection_set(first=i)
            else:
                self.listbContent.selection_clear(first=0, last=END)

    def selectChild(self, *x):
        """ Updates the list of children folders selected for current parent folder.

        If a parent folder rep is selected, method extractContent displays children folders in listbContent. selectChild extracts children folder current selection, and updates attributes selection and selFolderDict: selected children folders indexes in selection[rep] and selected children folders names in selFolderDict[rep].
        Local variables:
            - itemParent    index of selected folder in listbParent
            - itemChild     list of indexes of selected folders in listbContent
        Entry x is related to event <ButtonRelease-1> (variable not used)."""
        
        itemParent = map(int, self.listbParent.curselection())
        if itemParent != []:
            itemChild = map(int, self.listbContent.curselection())
            self.selection[self.parent[itemParent[0]]] = itemChild
            self.selFolderDict[self.parent[itemParent[0]]] = []
            for i, item in enumerate(itemChild):
                self.selFolderDict[self.parent[itemParent[0]]].insert(i, self.content[item])

    def clickOK(self):
        """ Save selections and quit."""
        if self.case == "pathology":
            del self.master.pathoList[0:]
            cpt = 0
            for key in self.selection:
                index = self.selection[key]
                for i in index:
                    self.master.pathoList.insert(cpt, self.content[i])
                    cpt += 1
        elif self.case == "patient":
            del self.master.patientList[0:]
            cpt = 0
            for key in self.selection:
                for name in self.selFolderDict[key]:
                    self.master.patientList.insert(cpt, name)
                    cpt += 1
        elif self.case == "exam":
            del self.master.examList[0:]
            cpt = 0
            for key in self.selection:
                for name in self.selFolderDict[key]:
                    self.master.examList.insert(cpt, name)
                    cpt += 1
        self.master.updateListbox(self.case)

        self.destroy()        

# ----------------------------------------------------------------------------------- #
class WinModifList(Toplevel):
    """ Window to modify a folders list by removing or moving elements.

        If confirmed, the new list is displayed on main window.
        Attributes:
            - case      "pathology", "patient" or "exam"
            - master    object mainWindow
            - ListMod   list displayed on window to be modified
            - listb     listbox showing elements of ListMod
            - listbNb   listbox showing numbering of ListMod elements
            - lbPack    two listboxes (listb and listbNb) linked with a vertical scrollbar
            - Tkinter attributes.           """
    
    def __init__(self, master, case):
        Toplevel.__init__(self, master)
        self.case = case
        self.master = master
        if case == "pathology":
            ListCpl = self.master.pathoList
        elif case == "patient":
            ListCpl = self.master.patientList
        elif case == "exam":
            ListCpl = self.master.examList            
        self.ListMod = list()
        for i, elt in enumerate(ListCpl):
            self.ListMod.insert(i, elt)
        self.initialize(master)  

    def initialize(self, master):
        """ Display window.

            Widgets list:
                - fbg               frame for listbox listb
                - listb             listbox with folders names
                - listbNb           listbox with numbering of folders names
                - scrollbarx        horizontal scrollbar, linked to listb
                - scrollbary        vertical scrollbar, linked to listb and listbNb
                - button "Remove"   button to remove selected element of listb
                - button "Up"       button to move up selected element of listb
                - button "Down"     button to move down selected element of listb
                - button "OK"       button to save new list and close window
                - button "Cancel"   button to close window without saving."""
        
        DefClr = self.cget("bg")
        self.title("Modify list")

        # folder list
        fbg = Frame(self, background='#6699FF', bd=1)
        fbg.grid(column=1, row=2, sticky='w')
        fbg.columnconfigure(0, weight=1)
        fbg.rowconfigure(0, weight=1)
        self.listb = Listbox(fbg, selectmode=BROWSE, bd=0, bg="#BFCFFE", selectbackground="#6699FF")
        list2listbox(self.listb, self.ListMod)
        self.listb.grid(column=1, row=0, sticky='w')        
        # numbering
        self.listbNb = Listbox(self, selectmode=BROWSE, bg=DefClr, selectbackground="#6699FF", width=3, bd=0)
        numListbox2listbox(self.listb, self.listbNb)
        self.listbNb.grid(column=0, row=2, sticky='w')
        # scrollbars
        scrollbarx = Scrollbar(self)
        scrollbary = Scrollbar(self)
        scrollbarx.grid(column=1, row=3, sticky='new')
        scrollbary.grid(column=2, row=2, sticky='nsw')        
        self.listb.config(xscrollcommand=scrollbarx.set)
        scrollbarx.config(command=self.listb.xview, orient=HORIZONTAL)
        self.lbPack = linkedListboxes(self.listb, self.listbNb, scrollbary)
        
        # move up or down, remove
        frem = Frame(self)
        frem.grid(column=3, row=2)
        Button(frem, text="Remove", command=self.removeElt).grid(column=0, row=2)
        Button(frem, text="Up", command=lambda x="up":self.moveElt(x), width=6).grid(column=0, row=0)
        Button(frem, text="Down", command=lambda x="down":self.moveElt(x), width=6).grid(column=0, row=1)

        # quit
        Button(self, text="OK", command=self.clickOK).grid(column=3, row=4, sticky='se')
        Button(self, text="Cancel", command=self.destroy).grid(column=1, row=4, sticky='sw')
        
    def removeElt(self):
        """ Remove selected element from ListMod and listb. listbNb is updated to new list.

            Local variables:
                - item      current selection index in listbox listb
                - index     new index for selection in listb"""
        item = map(int, self.listb.curselection())
        if item != []:
            self.listb.delete(item[0])
            del self.ListMod[item[0]]
            numListbox2listbox(self.listb, self.listbNb)            
            index = min(item[0], len(self.ListMod) - 1)
            self.lbPack.updateView(index)

    def moveElt(self, mvt):
        """ Move up or down selected element from ListMod and listb. listbNb is updated to new list."""
        item = map(int, self.listb.curselection())
        if item != []:
            if mvt == "up":
                index = max(item[0] - 1, 0)
            elif mvt == "down":
                index = min(item[0] + 1, len(self.ListMod) - 1)
            # changes list order
            elt = self.ListMod[item[0]]
            self.listb.delete(item[0])
            self.listb.insert(index, elt)
            # updates listboxes
            del self.ListMod[item[0]]
            self.ListMod.insert(index, elt)
            self.lbPack.updateView(index)
        
    def clickOK(self):
        """ Set ListMod content to master attributes, destroy object and updates main window (master).

            Depending on attributes "case", the list updated in master attributes is:
             - pathoList if "case" is "pathology";
             - patientList if "case" is "patient";
             - examList if "case" is "exam".
             Related master attributes are updated too by method updateListbox."""
        if self.case == "pathology":
            self.master.pathoList = self.ListMod
        elif self.case == "patient":
            self.master.patientList = self.ListMod
        elif self.case == "exam":
            self.master.examList = self.ListMod
        self.master.updateListbox(self.case)    
        self.destroy()

# ------------------------------------- #
class WinChooseProcess(Toplevel):
    """ New window to choose preprocessing functions for SPM8.

Functions names are those used in matlab file preprocess.m. They are loaded from module matlabFct.
This class displays two lists in a new window : possible functions and chosen functions.
The user choose SPM8 functions in the first list and add them in the second list. It can be modified with right located buttons.
Some functions include several others : "dartel" and "finergrid". When all are selected (button "select all"), "dartel" and "finergrid" are not included to avoid repetitions.

Attributes:
    - master        object class mainWindow
    - avFctList     list of available functions (see functions in module matlabFct)
    - selFctList    list of chosen functions
    - listbAv       listbox for available functions (displays avFctList)
    - listbSel      listbox for chosen functions (displays selFctList)
    - listbNb       listbox for numbering of listbSel elements
    - lbPack        two listboxes (listbSel and listbNb) linked with a vertical scrollbar
    - Tkinter attributes
    """
    
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.master = master
        from matlabFct import functions
        self.avFctList = functions("all")  # load functions names to available functions list
        self.selFctList = list()  # chosen function list
        for p in self.master.processList:
            self.selFctList.append(p)
            
        self.initialize(master)
        self.focus_set()
        self.grab_set()
    def initialize(self, master):
        """ Display window.

            It is divided in two parts : the list of existing functions (list 1), where the user can choose those he needs to apply, and the list of chosen functions (list 2). Function choice is done by selecting names in listbAv and clicking on "Add" or by double-clicking on a funtion name.          

            Widgets:
                - fl1                   frame for list 1
                - Label                 fl1 title
                - fbg                   frame for listbAv
                - listbAv               listbox for available functions (displays avFctList, list 1)
                - fb1                   frame for buttons to choose elements in listbAv
                - Button "Select all"   button to select all elemntary functions of avFctList (i.e. without functions including other, like "dartel" or "finergrid", see method allElt)
                - Button "Add"          button to add selected elements of avFctList to selFctList and listbSel (see method addElt)
                - fl2                   frame for list 2
                - Label                 fl2 title
                - fbg                   frame for listbSel
                - listbSel              listbox for chosen functions (displays selFctList, list 2)
                - listbNb               listbox for chosen functions numbering, linked to listbSel
                - scrollbary            vertical scrollbar, linked to listbSel and listbNb
                - fb2                   frame for buttons to modify listbSel
                - Button "Remove"       button to remove selected element in listbSel (see method removeElt)
                - Button "Clear"        button to clear listbSel (see method clearList)
                - Button "Up"           button to move up selected element in listbSel (see method moveElt)
                - Button "Down"         button to move down selected element in listbSel (see method moveElt)
                - Button "OK"           button to quit window and apply new chosen functions list in main window (see method clickOK)
                - Button "Cancel"       button to quit window without saving chosen functions list."""

        DefClr = self.cget("bg")
        self.grid()
        self.title("Data processing with SPM8")

        # ----- available processes -----
        fl1 = Frame(self, bd=1, relief='sunken')
        fl1.grid(column=0, row=0, sticky='nsew')
        # fl1.pack(fill=BOTH)
        Label(fl1, text="Choose functions:", justify='right', anchor="w").grid(column=0, row=0, columnspan=2, sticky='w')
        # functions list
        fbg = Frame(fl1, background='#6699FF', bd=1)
        fbg.grid(column=0, row=1, rowspan=2, sticky='w')
        self.listbAv = Listbox(fbg, selectmode=EXTENDED, bd=0, height=len(self.avFctList), bg="#BFCFFE", selectbackground="#6699FF")
        self.listbAv.config(exportselection=0)
        list2listbox(self.listbAv, self.avFctList)
        self.listbAv.grid(column=0, row=0, sticky='w')
        self.listbAv.bind("<Double-Button-1>", self.selectFct)
        # buttons : select all and add
        fb1 = Frame(fl1)
        fb1.grid(column=3, row=1, sticky='nsew')
        Button(fb1, text="Select all", command=self.allElt, width=10).grid(column=0, row=0)
        Button(fb1, text="Add", command=self.addElt, width=10).grid(column=0, row=1)
        
        # ----- chosen processes -----
        fl2 = Frame(self, bd=1, relief='sunken')
        fl2.grid(column=1, row=0, sticky='nsew')
        Label(fl2, text="Functions to be applied:", justify='right', anchor="w").grid(column=0, row=0, columnspan=3, sticky='w')     
        # functions list
        fbg = Frame(fl2, background='#6699FF', bd=1)
        fbg.grid(column=1, row=1, sticky='w')
        self.listbSel = Listbox(fbg, selectmode=BROWSE, bd=0, height=len(self.avFctList), bg="#BFCFFE", selectbackground="#6699FF")
        self.listbSel.config(exportselection=0)
        list2listbox(self.listbSel, self.selFctList)
        self.listbSel.grid(column=0, row=0, sticky='w')
        # numbering
        self.listbNb = Listbox(fl2, selectmode=BROWSE, bg=DefClr, selectbackground="#6699FF", width=3, bd=0, height=len(self.avFctList))
        numListbox2listbox(self.listbSel, self.listbNb)
        self.listbNb.grid(column=0, row=1, sticky='w')
        # scrollbar
        scrollbary = Scrollbar(fl2)
        scrollbary.grid(column=2, row=1, sticky='nsw')        
        self.lbPack = linkedListboxes(self.listbSel, self.listbNb, scrollbary)
        # buttons : move up, down, remove and clear
        fb2 = Frame(fl2)
        fb2.grid(column=3, row=1, sticky='nsew')
        Button(fb2, text="Remove", command=self.removeElt, width=6).grid(column=0, row=2)
        Button(fb2, text="Clear", command=self.clearList, width=6).grid(column=0, row=3)
        Button(fb2, text="Up", command=lambda x="up":self.moveElt(x), width=6).grid(column=0, row=0)
        Button(fb2, text="Down", command=lambda x="down":self.moveElt(x), width=6).grid(column=0, row=1)
        
        # Quit
        quitter = Button(self, text=u"OK", command=self.clickOK)
        quitter.grid(column=1, row=10)
        cancel = Button(self, text=u"Cancel", command=self.destroy)
        cancel.grid(column=0, row=10)       
        
    def selectFct(self, *x):
        """ Method called after double-click on an element of listbAv, which is then added at the end of selFctList. listbSel and listbNb are updated.
            Entry x is related to event <Double-Button-1> (variable not used).
            Mathode called by double click on ean element in listbAv."""
        
        item = map(int, self.listbAv.curselection())
        if item != []:
            for i in item:
                self.selFctList.append(self.avFctList[i])
            list2listbox(self.listbSel, self.selFctList)
            numListbox2listbox(self.listbSel, self.listbNb)

    def allElt(self):
        """ Select all elements of listbAv, except for 'dartel' and 'finergrid', to have a list of all possible functions without repetitions.
            Called by button "Select all"."""
        for i, f in enumerate(self.listbAv.get(0, END)):
            if (f != "dartel") and (f != "finergrid") and (f != "label"):
                self.listbAv.selection_set(i)
            else:
                self.listbAv.selection_clear(i)
                
    def addElt(self):
        """ Add selected elements of avFctList at the end of selFctList. listbSel and listbNb are updated.
            Called by button "Add"."""
        item = map(int, self.listbAv.curselection())
        if item != []:
            for i in item:
                if not self.avFctList[i] in self.selFctList: # to avoid that there are two same task
                    self.selFctList.append(self.avFctList[i])
            list2listbox(self.listbSel, self.selFctList)
            numListbox2listbox(self.listbSel, self.listbNb)

    def clearList(self):
        """ Clear selFctList, update listbSel and listbNb.
            Called by button "Clear"."""
        self.listbSel.delete(first=0, last=END)
        self.selFctList = []
        numListbox2listbox(self.listbSel, self.listbNb)

    def removeElt(self):
        """ Clear selected elements from listbSel. Linked widgets (in lbPack) are updated to adjust scrolling and numbering to new list in listbSel. The updateView method of object lbPack is called to set current selection to previous element on listbSel.
            Called by button "Remove"."""
        item = map(int, self.listbSel.curselection())
        if item != []:
            self.listbSel.delete(item[0])
            del self.selFctList[item[0]]
            index = max(item[0] - 1, 0)
            numListbox2listbox(self.listbSel, self.listbNb)
            self.lbPack.updateView(index)

    def moveElt(self, mvt):
        """ Move up or down selected element from selFctList and listbSel.
            Entry x is "up" or "dwon", it gives the movement direction.
            Linked widgets (in lbPack) are updated to adjust scrolling and numbering to new list in listbSel. The updateView method of object lbPack is called to maintain current selection to the same element on listbSel.
            Called by buttons "Up" and "Down"."""
        item = map(int, self.listbSel.curselection())
        if item != []:
            if mvt == "up":
                index = max(item[0] - 1, 0)
            elif mvt == "down":
                index = min(item[0] + 1, len(self.selFctList) - 1)
            # changes list order
            elt = self.selFctList[item[0]]
            self.listbSel.delete(item[0])
            self.listbSel.insert(index, elt)
            # updates listboxes
            del self.selFctList[item[0]]
            self.selFctList.insert(index, elt)
            numListbox2listbox(self.listbSel, self.listbNb)
            self.lbPack.updateView(index)
        
    def clickOK(self):
        """ Set new functions list to master attributes before closing current window.

            This method checks if any function is repeated in chosen functions list, in order to avoid confusion during data processing.
            With method functions (from module matlabFct), a list of detailled processes is returned for each function name of listbSel. Master attribute allProcessList is set to these new functions. Then method reduceList (from module preprocessCheck) is applied to the complete functions list.
            If an error message is returned in variable msg, a warning window appears to ask user to modify chosen functions list in order to avoid repetitions and method clickOK breaks off.
            If the new functions list is validated, it is set to master attribute processList and information about each function is loaded with master method getProcessInfo. Process list displayed in main window is updated too.
            Then current window is closed.
            Method called by button "OK".

            Warning : as method getProcessInfo is called at each new functions list validation, all changes done previously on SPM atlases or templates choice (use of WinCheckTempl class by clicking on button "click here" in main window) are lost."""

        self.master.allProcessList = list()
        from matlabFct import functions
        for fct in self.listbSel.get(0, END):
            self.master.allProcessList.extend(functions(fct))

        from loadAndCheck import reduceList
        msg = reduceList(self.master.allProcessList)        
        if msg == "rep":
            tkMessageBox.showwarning(title="Warning", message="Redondancy in functions list, modify it.\nFunctions \"dartel\" and \"finergrid\" include several other functions.")
        else:            
            self.master.processList = self.listbSel.get(0, END)
            self.master.getProcessInfo()
            self.master.updateListbox("process")
            self.destroy()

# ------------------------------------- #
class WinCheckTempl(Toplevel):
    """ Open new window to check or modify SPM reference files for each chosen function.

For each function (detailled list), a list of reference files (if needed by function) with path is displayed. They are default files, set in class SPMfct (from module matlabFct). Corresponding to those used in matlab script preprocess.m.
If user wants to change one of them, he clicks on "Change file" button at the right of file label, and can select one or more files in the new window. This new reference files list is saved in master attributes allProcessDict[function name].template["name"], that get information about each process to apply.
Master attribute param["repSPM"] is used as parent directory for new files research.

Attributes:
    - master        object class mainWindow;
    - templName     list of string: for function i, templName[i] gives files list in text format ('\n' between files names).
                    templName[i] is a variable string;
    - Tkinter attributes.

Warning : all changes done in reference files with this class are lost when user changes chosen function list (button "Modify list" in main window and "OK" in "Data processing with SPM8" window then)."""
    
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.master = master
        self.templName = []
        self.initialize(master)
        self.focus_set()
        self.grab_set()
    def initialize(self, master):
        """ Display window.

            The window is split into three columns:
            1. function name (labels)
            2. reference files list (label)
            3. "Change file" button
            There is one line per function, plus title and "Cancel" or "OK" buttons lines.
            For functions that don't need reference file, file list label and button are disabled.

            Widgets:
                - labels for columns titles
                - for each function :
                    - label for function name
                    - tlabel: label for files list (text format), shows templName[i] for function i, at line i+1
                    - change: button to change files list
                - button "OK" to save files lists and close window
                - button "Cancel" to ignore modifications in files lists and close window."""
        
        self.grid()
        self.title("SPM reference file(s)")

        # columns names
        Label(self, text="Function:", justify='center', anchor="s").grid(column=0, row=0)
        Label(self, text="Corresponding SPM reference file:", justify='center', anchor="s").grid(column=1, row=0)
        nb = len(self.master.allProcessList)
        
        for i, f in enumerate(self.master.allProcessList):
            irow = i + 1
            # function name            
            Label(self, text=f, justify='center', anchor="s").grid(column=0, row=irow)
            # state : active if template exists
            stateLab = StringVar()
            if self.master.allProcessDict[f].template["name"][0] == "":
                stateLab.set('disable')
                bgCol1 = "#CCCCCC"
                bgCol2 = "#999999"
            else:
                stateLab.set('normal')
                bgCol1 = "#BFCFFE"
                bgCol2 = "#6699FF"
            # templates names list
            tNameText = list2text(self.master.allProcessDict[f].template["name"])
            self.templName.insert(i, StringVar())
            self.templName[i].set(tNameText)
            fbg = Frame(self, background=bgCol2, bd=1)
            fbg.grid(column=1, row=irow, sticky='nw')
            tLabel = Label(fbg, textvariable=self.templName[i], justify='right', anchor="e", bg=bgCol1, width=40, state=stateLab.get())
            tLabel.grid(column=0, row=0, sticky='w')
            # change
            change = Button(self, text=u"Change file", command=lambda x=f, y=i:self.ChangeTemplate(x, y), anchor='w', state=stateLab.get()) 
            change.grid(column=2, row=irow)

        # Quit
        Button(self, text=u"OK", command=self.clickOK).grid(column=1, row=nb + 1)
        Button(self, text=u"Cancel", command=self.destroy).grid(column=0, row=nb + 1)

    def ChangeTemplate(self, f, i):
        """ Open a window for files selection, for function number i.
            Parent directory is master attribute master.param["repSPM"].
            Selected files (with paths) are set in templName[i] in text format with method list2text (from module GUItools).
            Method called by buttons "Change file"."""

        fileName = tkFileDialog.askopenfilenames(parent=self, initialdir=self.master.param["repSPM"], title='Please select file(s) for ' + f)      
        if (fileName != "") and (fileName != ()):
            print fileName
            if sys.platform == "win32":
                self.templName[i].set(fileName.replace(" ","\n")) # ¨¤ am¨¦liorer(quand il y a des espaces dans le nom de fichier)
            else:
                self.templName[i].set(list2text(fileName))

    def clickOK(self):
        """ Validation of reference files lists and window closing.

            For each function, master attribute master.allProcessDict, which gives function information, is updated with reference files list.
            For function i: master.allProcessDict[function i].template["name"] get files names from templName[i] (text split into list).
            Method called by button "OK"."""
            
        for i, f in enumerate(self.master.allProcessList):
            self.master.allProcessDict[f].template["name"] = self.templName[i].get().split("\n")
        self.destroy()
class WinSetCoord(Toplevel):
    
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.master = master
        self.coordFiles = dict()
        self.initialize(master)
        self.focus_set()
        self.grab_set()
    def initialize(self, master):
        """"""
        
        self.grid()
        self.title("Coordinates file(s)")

        # columns names
        Label(self, text="Function:", justify='center', anchor="s").grid(column=0, row=0)
        irow = 0
        if self.master.chosenFct[1].get() == 1:
            Label(self, text="Corresponding coordinates file(s):", justify='center', anchor="s").grid(column=1, row=0)
            for i, f in enumerate(self.master.allProcessList):
                if f == 'iwarp' or f == 'iwarp_finergrid':
                    for templBaseName in self.master.allProcessDict[f].template["name"]:
                        templBaseName = templBaseName.split("/")[-1].split(".")[0]
                        irow = irow + 1
                        # function name            
                        Label(self, text=templBaseName, justify='center', anchor="s").grid(column=0, row=irow)
                        # state : active if template exists
                        stateLab = StringVar()
                        stateLab.set('normal')
                        bgCol1 = "#BFCFFE"
                        bgCol2 = "#6699FF"
                        # templates names list
                        if self.master.allCoordFile.has_key(templBaseName):
                            tNameText = self.master.allCoordFile[templBaseName]
                        else:
                            tNameText = "cool"#list2text(self.master.allProcessDict[f].template["name"])
                        self.coordFiles.update({templBaseName:StringVar()})
                        self.coordFiles[templBaseName].set(tNameText)
                        fbg = Frame(self,background=bgCol2, bd=1)
                        fbg.grid(column=1, row=irow, sticky='nw')
                        tLabel = Label(fbg, textvariable=self.coordFiles[templBaseName], justify='right', anchor="e",bg=bgCol1, width=40, state=stateLab.get())
                        tLabel.grid(column=0, row=0, sticky='w')
                        # change
                        change = Button(self, text=u"Change file", command=lambda x=templBaseName, y=irow-1:self.ChangeCoordFile(x, y), anchor='w', state=stateLab.get()) 
                        change.grid(column=2, row=irow)
            if irow == 0:
                irow = irow+1
                Label(self, text="No template chosen for data preprocessing:", justify='center', anchor="s").grid(column=1, row=1)
        elif self.master.chosenFct[3].get() == 1:
            from os import path
            f = self.master.examList[0]
            if path.exists(f.replace("Original", "Processed")+"/Anat/Atlased/"):
                Label(self, text="For datas already atlased(realigned)", justify='center', anchor="s").grid(column=1, row=0)
                self.templBaseNames = glob.glob(f.replace("Original", "Processed") + "/Anat/Atlased/natw*.nii")
                for templBaseName in self.templBaseNames:
                    if sys.platform == "win32":
                        templBaseName = templBaseName.replace('\\','/')
                    templBaseName = templBaseName.split("/")[-1].split("_u_rc")[0].replace("natw","")
                    irow = irow + 1
                    # function name            
                    Label(self, text=templBaseName, justify='center', anchor="s").grid(column=0, row=irow)

                    stateLab = StringVar()
                    stateLab.set('normal')
                    bgCol1 = "#BFCFFE"
                    bgCol2 = "#6699FF"
                    # templates names list
                    if self.master.allCoordFile.has_key(templBaseName):
                        tNameText = self.master.allCoordFile[templBaseName]
                    else:
                        tNameText = "cool"#list2text(self.master.allProcessDict[f].template["name"])
                    self.coordFiles.update({templBaseName:StringVar()})
                    self.coordFiles[templBaseName].set(tNameText)
                    fbg = Frame(self,background=bgCol2, bd=1)
                    fbg.grid(column=1, row=irow, sticky='nw')
                    tLabel = Label(fbg, textvariable=self.coordFiles[templBaseName], justify='right', anchor="e",bg=bgCol1, width=40, state=stateLab.get())
                    tLabel.grid(column=0, row=0, sticky='w')
                    # change
                    change = Button(self, text=u"Change file", command=lambda x=templBaseName, y=irow-1:self.ChangeCoordFile(x, y), anchor='w', state=stateLab.get()) 
                    change.grid(column=2, row=irow)
            else:
                Label(self, text="No data atlased(realigned), please do data preprocessing first:", justify='center', anchor="s").grid(column=1, row=0)
        else:
            from os import path
            f = self.master.examList[0]
            if path.exists(f.replace("Original", "Processed")+"/Functional/corrected_data/"):
                Label(self, text="For file(s) time series extraction already exist", justify='center', anchor="s").grid(column=1, row=0)
                self.templBaseNames = glob.glob(f.replace("Original", "Processed") + "/Functional/corrected_data/*/func_ROI*_ts.txt")
                for templBaseName in self.templBaseNames:
                    if sys.platform == "win32":
                        templBaseName = templBaseName.replace('\\','/')
                    templBaseName = templBaseName.split("/")[-1].replace("func_ROI_","").replace("_ts.txt","")
                    irow = irow + 1
                    # function name            
                    Label(self, text=templBaseName, justify='center', anchor="s").grid(column=0, row=irow)
                    # state : active if template exists
                    stateLab = StringVar()
                    stateLab.set('normal')
                    bgCol1 = "#BFCFFE"
                    bgCol2 = "#6699FF"
                    # templates names list
                    if self.master.allCoordFile.has_key(templBaseName):
                        tNameText = self.master.allCoordFile[templBaseName]
                    else:
                        tNameText = "cool"#list2text(self.master.allProcessDict[f].template["name"])
                    self.coordFiles.update({templBaseName:StringVar()})
                    self.coordFiles[templBaseName].set(tNameText)
                    fbg = Frame(self,background=bgCol2, bd=1)
                    fbg.grid(column=1, row=irow, sticky='nw')
                    tLabel = Label(fbg, textvariable=self.coordFiles[templBaseName], justify='right', anchor="e",bg=bgCol1, width=40, state=stateLab.get())
                    tLabel.grid(column=0, row=0, sticky='w')
                    # change
                    change = Button(self, text=u"Change file", command=lambda x=templBaseName, y=irow-1:self.ChangeCoordFile(x, y), anchor='w', state=stateLab.get()) 
                    change.grid(column=2, row=irow)
            else:
                Label(self, text="No file(s) time series extraction exist, please check", justify='center', anchor="s").grid(column=1, row=0)


        # Quit
        Button(self, text=u"OK", command=self.clickOK).grid(column=1, row=irow + 1)
        Button(self, text=u"Cancel", command=self.destroy).grid(column=0, row=irow + 1)

    def ChangeCoordFile(self, f, i):
        """"""
        import os
        fileName = tkFileDialog.askopenfilename(parent=self, initialdir=self.master.param["repSPM"], title='Please select file for ' + f)      
        if (fileName != "") and (fileName != ()):
            print fileName
            if sys.platform == "win32":
                fileName = fileName.replace(" ","\n") # ¨¤ am¨¦liorer(quand il y a des espaces dans le nom de fichier)
            else:
                fileName = list2text(fileName)
            self.coordFiles[f].set(fileName)


    def clickOK(self):
        """"""
        import os
        ok = True
        for f in self.coordFiles:
            if os.path.isfile(self.coordFiles[f].get()):
                self.master.allCoordFile[f] = self.coordFiles[f].get()
            else:
                ok = False
                tkMessageBox.showwarning(title="Warning", message= self.coordFiles[f].get()+ " is not a file")

        print self.master.allCoordFile
        if ok is True:
            self.destroy()
