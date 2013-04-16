#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" This module realizes checking on files created by data preprocessing of functional MRI: necessary files (for possible next steps) are search and some of them are diplayed for user."""

from Tkinter import *
import nibabel as nib
from numpy import isnan, ma, array, zeros
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import glob
import os

# # ---------------------------------------- ##
def checkFiles(param, i, option):
    """ Display slices of volumes created by previous steps (data preprocessing with SPM) and check if necessary files for next steps exist.

        Entries:
            - param     parameters dictionary, see main.py
            - i         data set numbering: data exploited are in param["examRep"][i]
            - option    "inter" ou "indep" (see main.py)

        This function return "yes" or "no", that indicates if next step (time series extraction) can be done.

        Local variables:
            - 

        Images (in functional space) displayed are:
            - grey matter (from file natc1*.nii in Processed/[exam name]/Anat/Segmented/)
            - mean time series (from file mean*.nii in Processed/[exam name]/Functional/Realigned/)
            - atlasing (from file natw[atlas name]_u_rc1*.nii in Processed/[exam name]/Anat/Atlased/).
        All three slices are surimposed in a new window (see class WinVolShow), for each atlasing file in list reg (local variable).
        
        This list is completed as follow:
             - if function "coregister" or "coregister,finergrid" has been chosen (function name is in list param["allProcess"]), atlas name is known and corresponding atlasing file is found and added to list reg
             - if no function "coregister" (in dartel or finergrid) has been chosen, list reg is composed by all files whose names are natw*[anatomical file base name].nii
             
        Images displaying is done even if some files are missing, except if reg is empty. Depending on user's choice for entry option, new window appears during a longer or shorter minimum time:
             - if option is "inter", window exist for at least 2 minutes
             - if option is "indep", window exist for at least 10 seconds.
        This parameter is set in local variable delay. See class WinVolShow for more information.

        This function creates repertory QC in Processed/[exam name]/ if not existing, where figures of window created by WinVolShow are saved.
        Figure name contains atlas name (part between 'natw' and 'u_rc1' in atlasing files) to distinguish possible atlased used during preprocessing step.

        It checks following files too:
            - grey matter segmentation in MNI space (file Processed/[exam name]/Anat/Segmented/rc1[anatomical file base name].nii)
            - realigned time series in functional space (files list Processed/[exam name]/Functional/Realigned/r[functional file base name]*.nii)
            - time series movement corrections (file Processed/[exam name]/Functional/Realigned/rp_[functional file base name]*.txt)
        If one of those files is missing, an error message is displayed and function returns "no" (variable nextStep), otherwise it returns "yes".
    """
        
    from loadAndCheck import checkData, checkDir
    [msg, files] = checkData(param["examRep"][i])
    index = param["examRep"][i].find("Original")
    patientDir = param["examRep"][i][0:index]
    examName = checkDir(param["examRep"][i])[index + 9:]
    anatDir = patientDir + "Processed/" + examName + "Anat/"
    functDir = patientDir + "Processed/" + examName + "Functional/"

    # loading files:
    #   grey matter
    MG = glob.glob(anatDir + "Segmented/natc1" + files["anatBaseName"] + "." + files["anatExt"])
    #   mean time series
    mTS = glob.glob(functDir + "Realigned/mean" + files["functBaseName"] + "*." + files["functExt"])
    #   atlasing into regions
    reg = list()
    if "coregister" in param["allPreprocess"]:
        reg += glob.glob(param["allPreprocessInfo"][i]["coregister"].endFile[1])
    if "coregister_finergrid" in param["allPreprocess"]:
        reg += glob.glob(param["allPreprocessInfo"][i]["coregister_finergrid"].endFile[1])
    if not ("coregister" in param["allPreprocess"]) and not ("coregister_finergrid" in param["allPreprocess"]):
        reg = glob.glob(anatDir + "Atlased/natw" + "*" + files["anatBaseName"] + "." + files["anatExt"])
    
    # display slices for each atlas used
    for f in reg:
        l0 = f.split("natw")
        l1 = l0[-1].split("u_rc1")
        volList = mTS + MG + [f]
        QCDir = patientDir + "Processed/" + examName + "QC/"  # folder QC to save images      
        if os.path.exists(QCDir) is False:
            os.mkdir(QCDir)
        
        # window maximum duration before closing
        if option == "inter":
            delay = 120
        else:
            delay = 10

        # window to show SPM processing results
        app = WinVolShow(None, i, QCDir, volList, l1[0], delay)
        app.mainloop()

    # check if necessary files exist to proceed processing
    nofiles = list()
    fct = list()
    nextStep = True
    
    MG_MNI = glob.glob(anatDir + "Segmented/rc1" + files["anatBaseName"] + "." + files["anatExt"])
    rFunct = glob.glob(functDir + "Realigned/r" + files["functBaseName"] + "*." + files["functExt"])
    rpFunct = glob.glob(functDir + "Realigned/rp_" + files["functBaseName"] + "*.txt")
    
    if (len(rFunct) == 0) or (len(rpFunct) == 0):
        nofiles.append("no realigned time series")
        fct.append("\'realign\'")
    if len(MG_MNI) == 0:
        nofiles.append("no segmentation in grey matter")
        fct.append("\'segment\'")
    if len(reg) == 0:
        nofiles.append("no atlasing in functional space")
        fct.append("\'coregister\'")
    if nofiles != list():
        nextStep = False
        print "WARNING:  ", ("\n           ").join(nofiles)
        print "To do next processing step, SPM function(s)", (", ").join(fct), "must be run."
        
    return nextStep


# # ---------------------------------------- ##
class WinVolShow(Tk):
    """ Window displaying superimposed volumes slices for grey matter, mean time series and atlasing files in functional space for quality check step.

        Volumes to be ckecked are loaded in files of self.volList list.
        See method initialize for window description.

        Attributes:
            - Tkinter, Tk attributes
            - master    entry master of method __init__            
            - QCRep     string, directory to filder QC where images are saved, entry QCRep or method __init__ (see method svgFigure)
            - volList   list of string, files to display, entry volList or method __init__            
            - figName   string, base name for images to save, entry figName or method __init__ (see method svgFigure)
            - viewNum   integer, number of image to save (see method svgFigure)
            - nb        integer, number of files in self.volList            
            - data      3D-matrix, volume data of first file in volList
            - ImXY      3D-matrix, containing slices in plan (y,z) of each file of volList (see method showSlices)
            - ImYZ      3D-matrix, containing slices in plan (x,z) of each file of volList (see method showSlices)
            - ImXZ      3D-matrix, containing slices in plan (x,y) of each file of volList (see method showSlices)
            - posx      integer variable, coordinate in x for slice in plan (y,z) (see methods initialize, setViews and showSlices)
            - poxy      integer variable, coordinate in y for slice in plan (x,z) (see methods initialize, setViews and showSlices)
            - posz      integer variable, coordinate in z for slice in plan (x,y) (see methods initialize, setViews and showSlices)
            - slicex    scale, set value for slices coordinate in x-axis (see methods initialize and setViews)
            - slicey    scale, set value for slices coordinate in y-axis (see methods initialize and setViews)
            - slicez    scale, set value for slices coordinate in z-axis (see methods initialize and setViews)
            - f         matplotlib figure, with surimposed slices of normalized volumes ni volList file list (see method imSumShow)
            - figw      integer, figure self.f width (in inches, see methods __init__ and imSumShow)
            - figh      integer, figure self.f height (in inches, see methods __init__ and imSumShow)
            - figDPI    integer, figure self.f reslotion (in dots per inch, see methods __init__ and imSumShow)            
            - hide      list of integer variables, 0 or 1 to show or hide slices for a given file i (see method imSumShow)
            - i         list of integer variables, between 0 and 1 (step 0.2) to set transparency of slices for a given file (see method imSumShow)
            - Clmn1     canvas for the first column of the window
            - delay     integer, minimum time (in seconds) before automatic window closing (see method poll)
            - msg       string variable, message displayed in clock label, which show remaining time before automatic window closing (see methods poll and pausePoll)
            - state     string, "run" or "pause", countdown state (see methods poll and pausePoll)
            - count     integer, number of second remaining in countdown (see methods poll and pausePoll)
            - ids       event, linked to countdown in method poll    """    

    def __init__(self, master, setNb, QCRep, volList, figName, delay):
        Tk.__init__(self, master)
        self.master = master

        # files
        self.QCRep = QCRep
        self.volList = volList
        self.figName = figName
        self.viewNum = 1
        self.nb = len(self.volList)

        # window
        self.title("~ Quality check for data set " + str(setNb) + " ~")       
        self.delay = delay        
        self.msg = StringVar()
        self.msg.set("Wait...")
        self.state = "run"        
        
        # images
        self.figw = 6  # images width (inches)
        self.figh = 6  # images height
        self.figDPI = 100  # images resolution: dots per inch
        self.posx = IntVar()
        self.posy = IntVar()
        self.posz = IntVar()
        self.posx.set("-1")
        self.hide = list()
        for i, v in enumerate(self.volList):
            self.hide.insert(i, IntVar())
            self.hide[i].set(0)
        self.i = [1, 1, 1]

        # build window
        self.initialize(master)
                
    def initialize(self, master):
        """ Display window for quality check step.

            Window description:
                - column 1: file names and images
                    - self.nb labels for self.nb files, displaying files names from self.volList
                    - figure created by method imSumShow with surimposed and processed data from files
                        - view in plan (x,z)
                        - view in plan (y,z)
                        - view in plan (x,y)
                      figure dimensions are set by self.figw, self.figh and self.figDPI (in method __init__)
                - column 2:
                    - images settings: two frames (transFrame and viewFrame)
                        - transparency (label "Transparency")
                            - self.nb labels (nameLabel), to give file nature
                            - self.nb scales (slicef), to set transparency, between 0 and 1, by step of 0.2, for file i
                              set value for self.i[i], and call method setTransparency
                              also restart countdown
                            - self.nb check buttons (hide), to display or not a file i
                              set value for self.hide[i], and call method imSumShow
                              also restart countdown
                        - view (label "View")
                            - current coordinates
                                - label "Current coordinates:"
                                - labels "x", "y" and "z"
                                - labels for current coordinates, under "x", "y", "z"
                                  display values of self.posx, self.posy and self.posz
                            - new coordinates
                                - label "New coordinates:"
                                - labels "x", "y" and "z" (vertically displayed)
                                - scales self.slicex, self.slicey and self.slicez, near labels "x", "y", or "z"
                                  set value for new coordinates
                                  self.slicex set self.posx.get(), from 0 to self.data.shape[0] (number of voxel in x dimension in files)
                                  self.slicey set self.posy.get(), from 0 to self.data.shape[1] (number of voxel in y dimension in files)
                                  self.slicez set self.posz.get(), from 0 to self.data.shape[2] (number of voxel in z dimension in files)
                            - button "Update view" to display new view, call method setViews
                              also restart countdown
                    - save image, exit window (frame quitFrame)
                        - countdown before closing window:
                            - label displaying message self.msg, linked to methods poll and pausePoll
                              when countdown reach "00:00", method quitOK is called
                            - button "Pause" to stop countdown ar start again, call method pausePoll
                        - save and exit buttons:
                            - button "save figure" to save current figure (second part of column 1) without closing window, call method svgFigure
                            - button "save & stop" to save current figure and exit process, call method quitInterrupt
                            - button "save & next" to save current figure and close window, call method quitOK
            """
       
        # window divided into two columns
        self.Clmn1 = Canvas(self, width=self.figw * self.figDPI)
        self.Clmn1.grid(row=0, column=0, sticky='nsew')
        Clmn2 = Canvas(self)
        Clmn2.grid(row=0, column=1, sticky='nsew')

        # ----- Column 1 -----------------------------
        # images displaying in bottom of column 1
        canvasInit = Canvas(self.Clmn1, width=self.figw * self.figDPI, height=self.figh * self.figDPI)
        canvasInit.grid(row=1, column=0, sticky='nsew')
        self.showSlices()
        
        # files names in top of column 1
        namesFrame = Frame(self.Clmn1, bd=1, relief='sunken')
        namesFrame.grid(row=0, column=0, sticky='nsew')
        for i, f in enumerate(self.volList):
            Label(namesFrame, text=str(i + 1) + ". " + f.split("/")[-1], justify=LEFT, anchor='w').grid(column=0, row=i, sticky='ew')

        # ----- Column 2 -----------------------------
        # set slices transparency
        transFrame = Frame(Clmn2, bd=1, relief='sunken')
        transFrame.grid(row=0, column=0, sticky='nsew')
        Label(transFrame, text="Transparency").grid(column=0, row=0, columnspan=3, sticky='ew')        
        for i, f in enumerate(self.volList):
            # files type (if exist in list self.volList)
            if f.split("/")[-1][0:4] == "mean":
                Label(transFrame, text="Mean time series:").grid(column=0, row=i + 1, sticky='new')
            elif f.split("/")[-1][0:5] == "natc1":
                Label(transFrame, text="Grey matter:").grid(column=0, row=i + 1, sticky='new')
            elif f.split("/")[-1][0:4] == "natw":
                Label(transFrame, text="Atlasing:").grid(column=0, row=i + 1, sticky='new')
            # transparency scale and "Hide" checkbutton
            slicef = Scale(transFrame, from_=0, to=1, resolution=0.2, orient=HORIZONTAL, command=lambda x, y=i:self.setTransparency(x, y))
            slicef.set(1)     
            slicef.grid(column=1, row=i + 1, sticky='ew')
            Checkbutton(transFrame, text="Hide", variable=self.hide[i], command=self.imSumShow).grid(column=2, row=i + 1)
            
        # set slices coordinates
        viewFrame = Frame(Clmn2, bd=1, relief='sunken')
        viewFrame.grid(row=1, column=0, sticky='nsew')
        Label(viewFrame, text="View").grid(column=0, row=0, columnspan=4, sticky='ew')
        #   current view: labels with coordinates
        framepos = Frame(viewFrame, bd=2)
        framepos.grid(column=0, row=1, sticky='nsew')
        Label(framepos, text="Current coordinates:").grid(column=0, row=0, columnspan=3, sticky='n')
        Label(framepos, text="x").grid(column=0, row=1, sticky='sew')
        Label(framepos, text="y").grid(column=1, row=1, sticky='sew')
        Label(framepos, text="z").grid(column=2, row=1, sticky='sew')
        Label(framepos, textvariable=str(self.posx), bd=2, relief='ridge').grid(column=0, row=2, sticky='new')
        Label(framepos, textvariable=str(self.posy), bd=2, relief='ridge').grid(column=1, row=2, sticky='new')
        Label(framepos, textvariable=str(self.posz), bd=2, relief='ridge').grid(column=2, row=2, sticky='new')   
        #   next view: scales for x, y and z directions
        coordFrame = Frame(viewFrame, bd=2)
        coordFrame.grid(column=1, row=1, rowspan=2, sticky='nsew')
        Label(coordFrame, text="New coordinates:").grid(column=0, row=0, columnspan=2, sticky='n')
        Label(coordFrame, text="x").grid(column=0, row=1, sticky='sew')
        Label(coordFrame, text="y").grid(column=0, row=2, sticky='sew')
        Label(coordFrame, text="z").grid(column=0, row=3, sticky='sew')
        self.slicex = Scale(coordFrame, from_=0, to=self.data.shape[0], orient=HORIZONTAL)
        self.slicey = Scale(coordFrame, from_=0, to=self.data.shape[1], orient=HORIZONTAL)
        self.slicez = Scale(coordFrame, from_=0, to=self.data.shape[2], orient=HORIZONTAL)
        self.slicex.set(self.posx.get())
        self.slicey.set(self.posy.get())
        self.slicez.set(self.posz.get())       
        self.slicex.grid(column=1, row=1, sticky='new')
        self.slicey.grid(column=1, row=2, sticky='new')        
        self.slicez.grid(column=1, row=3, sticky='new')
        #   set to new view: button "Update view"
        Button(viewFrame, text=u"Update view", command=self.setViews).grid(column=0, row=2)
        
        # clock and quit
        quitFrame = Frame(Clmn2, bd=1, relief='sunken')
        quitFrame.grid(row=2, column=0, sticky='new')        
        #   clock: time before window closing
        Label(quitFrame, textvariable=self.msg, anchor='s', justify=CENTER, foreground="#7c7b85").grid(column=0, row=0, columnspan=2, sticky='ew')
        Button(quitFrame, text=u"Pause", command=self.pausePoll).grid(column=2, row=0)
        #   buttons to save and/or close window, and/or interrupt process
        Button(quitFrame, text=u"save figure", command=self.svgFigure).grid(column=0, row=2)
        Button(quitFrame, text=u"save & stop", command=self.quitInterrupt).grid(column=1, row=2)
        Button(quitFrame, text=u"save & next", command=self.quitOK).grid(column=2, row=2)

        self.update()
            
    def poll(self, count):
        """ Countdown before window closing, starts at count (entry) seconds.

            If self.state == "run", countdown is running, and starts at new value.
            If self.state == "pause", button "pause" has been pressed, then countdown is not running, but value in count is set to self.count, for next countdown start.

            Number of seconds remaining is set in attribute self.count. At the end method quitOK is called.
            Clock message in window is updated by attribute self.msg with remaining time (format mm:ss, m for minutes, s for seconds).
            """
       
        if self.state == "run":
            if count > 0 :
                self.ids = self.after(1000, self.poll, count - 1)
                mins, secs = divmod(count, 60)
                self.msg.set("Time before closing window\n%02d:%02d        " % (mins, secs))
                self.count = count
            if count == 0:
                self.quitOK()
        self.count = count

    def pausePoll(self):
        """ Stop or play countdown of method poll.

            This method is called by button "Pause" in current window. At first countdown is running, and its state (given by attribute self.state) is "run".

            If self.state is "run", countdown is stopped (method after_cancel is called for event self.ids), and an indication is displayed near
            clock message in window (add " - pause" to text).
            If state is "pause", countdown starts again at value self.count (method self.poll is called), which may be different of current countdown value.

            Local variable remTime gives remaining time displayed on window (see self.msg), with format mm:ss."""
        
        if self.state == "run":
            self.state = "pause"            
            self.after_cancel(self.ids)
            remTime = self.msg.get()[-13:-8]
            self.msg.set("Time before closing window\n" + remTime + " - pause")
        elif self.state == "pause":
            self.state = "run"
            self.poll(self.count)

    def quitOK(self):
        """ Save current figure with method self.svgFigure, cancel countdown with method self.after_cancel (if event self.ids exist) and destroy window."""
        
        self.svgFigure()
        if hasattr(self, 'ids'):
            self.after_cancel(self.ids)
        self.destroy()

    def quitInterrupt(self):
        """ Save current figure with method self.svgFigure, destroy window and end all processes. A message is displayed on console."""
        
        self.svgFigure()
        self.destroy()
        sys.exit("Execution interrupted after preprocessing quality check.")

    def svgFigure(self):
        """ Save current figure (content of self.f) in repertory QCRep, with png format.

            File name is: "fig_" [name given in self.figName] [figure number given in self.viewNum].
            Value of self.viewNum is incremented after each neaw figure. See function checkFiles for figure names in  self.figName."""

        Name = self.QCRep + "fig_" + self.figName + str(self.viewNum) + ".png"
        self.f.savefig(Name, format="png")
        self.viewNum += 1

    def setTransparency(self, val, i):
        """ Update figure with new transparency values.

            Transparency is adjusted by scales in column 2 of the window, each scale is linked to a file.
            When transparency is changed on a scale, the corresponding parameter self.i[i] (entry i for scale i, file i) gets
            scale value (entry val). Then method imSumShow is called to show new figure."""
        
        self.i[i] = float(val)
        self.imSumShow()

    def imSumShow(self):
        """ Create figure from slices extracted from files, with transparency and showing settings, and show figure in window.

            The figure is a matplotlib object, composed by three views of surimposed slices of volumes in self.volList file list.
            Data from files have been processed by method showSlices to fill matrixes self.ImXY, self.ImYZ and self.ImXZ with slices to display.

            At first, data in self.ImXY, self.ImYZ and self.ImXZ are completed with transparency and hidden parameters self.i and
            self.hide for each file j (i.e. each coordinate j of matrixes third dimension). Results are set in matrixes ImhXY, ImhYZ and ImhXZ respectively.
            Those attributes are lists containing a value for each file j:
                - self.i[j] gives a coefficient between 0 and 1 for transparency (0 image invisible, 1 image fully visible).
                  It is related to scale (slicef) number j, in column 2 of the window.
                - self.hide[j] is 0 to show image, or 1 to hide it, whatever transparency value is.
                  It is related to button hide number j, in column 2 of the window.

            Then pixels values are added along third dimension (files number) for each slice, and resulting images are set in 2D-matrixes:
                - ImsXY is the resulting image of ImhXY
                - ImsYZ is the resulting image of ImhYZ
                - ImsXZ is the resulting image of ImhXZ

            Those images are displayed in figure self.f by matplotlib figure method add_subplot, with titles and axes names. Figure dimensions self.figw, self.figh and self.figDPI are set in method __init__. Then the figure is displayed on canvas, in the first column of the window.

            At last countdown (event self.ids) is started or restarted with initial delay (self.delay)."""

        # slices matrixes initialization
        ImhXY = zeros(self.ImXY.shape)
        ImhYZ = zeros(self.ImYZ.shape)
        ImhXZ = zeros(self.ImXZ.shape)

        # voxels values with transparency and possible hidden files for each file
        for j, v in enumerate(self.volList):
            ImhXY[:, :, j] = self.ImXY[:, :, j] * self.i[j] * (not self.hide[j].get())
            ImhYZ[:, :, j] = self.ImYZ[:, :, j] * self.i[j] * (not self.hide[j].get())
            ImhXZ[:, :, j] = self.ImXZ[:, :, j] * self.i[j] * (not self.hide[j].get())

        # slices (files) summation for each view
        ImsXY = ImhXY.sum(axis=2)
        ImsYZ = ImhYZ.sum(axis=2)
        ImsXZ = ImhXZ.sum(axis=2)

        # displaying 3 images on a figure: slices (xz), (yz), (xy)
        self.f = Figure(figsize=(self.figw, self.figh), dpi=self.figDPI)
        imAdded = self.f.add_subplot(2, 2, 1)
        imAdded.imshow(ImsXZ.transpose(), origin='lower')
        imAdded.set_title("XZ")
        imAdded.set_xlabel("x")
        imAdded.set_ylabel("z")
        imAdded = self.f.add_subplot(2, 2, 2)
        imAdded.imshow(ImsYZ.transpose(), origin='lower')
        imAdded.set_title("YZ")
        imAdded.set_xlabel("y")
        imAdded.set_ylabel("z")
        imAdded = self.f.add_subplot(2, 2, 3)
        imAdded.imshow(ImsXY.transpose(), origin='lower')
        imAdded.set_title("XY")
        imAdded.set_xlabel("x")
        imAdded.set_ylabel("y")

        # showing figure in window
        canvas = FigureCanvasTkAgg(self.f, master=self.Clmn1)
        canvas.show()
        canvas.get_tk_widget().grid(column=0, row=1, sticky='nsew')
        canvas._tkcanvas.grid(column=0, row=1, sticky='nsew')

        # start or restart countdown before closing window
        if hasattr(self, 'ids'):
            self.after_cancel(self.ids)
            self.poll(self.delay)
        else:
            self.poll(self.delay)

    def setViews(self):
        """ Update figure with new view, given by chosen coordinates in window.

            The view is adjusted by coordinates scales (self.slicex, self.slicey and self.slicez) in column 2 of the window, each scale is linked to a direction x, y or z.
            To apply new coordinates, user have to click on "Update view" button (see method initialize), then slices coordinates self.posz, self.posy and self.posz get their new values from self.slicex, self.slicey and self.slicez respectively, and method showSlices is called to create new figure."""
        
        self.posx.set(self.slicex.get())
        self.posy.set(self.slicey.get())
        self.posz.set(self.slicez.get())
        self.showSlices()

    def showSlices(self):
        """ Data loading from files, processing and displaying in window.

            Data are loaded by nibabel functions, and processed by numpy functions. All files in self.volList must contain same volume size.

            For each file (number i), full volume is loaded. Then indifined values (nan) are suppressed, and voxels are normalized by minimum and maximum values for visibility.
            Three views are extracted from volume:
                - slice in (x,y) plan -> set by self.posz
                - slice in (y,z) plan -> set by self.posx
                - slice in (x,z) plan -> set by self.posy
            Slices coordinates (self.posz, self.posy, self.posz) are initially set to the center of the volume (when self.posx value is -1). Later these coordinates may change (see setViews method).            
            The slices are set in 3D-matrixes self.ImXY, self.ImYZ and self.XZ, in (:,:,i).
            Then, method imSumShow is called to create and show figure.

            Note that each time this method is called (window initialization, change of view coordinates by method setViews) complete files are loaded again and previous figure is lost.

            Variables:
                - vol           content of a file, loaded by bibabel fonction load
                - self.volList  files names list, created by function checkFiles
                - self.data     voxels values of volume in first file
                - self.posx, self.posy, self.posz
                                slices coordinates for plans (y,z), (x,z) and (x,y) respectively
                - self.ImXY, self.ImYZ, self.ImXZ
                                3D-matrixes, containing slices of each file, one matrix per slice plan
                                dimensions 1 and 2: size of slices in plans (y,z), (x,z) and (x,y) respectively
                                dimension 3: file number
                - data          voxels values of volume vol
                - mindata       for volume vol, gives lower voxel value
                - maxdata       for volume vol, gives higher voxel value
                - dataNorm      volume vol normalized by mindata and maxdata
                """ 
        
        # images dimensions
        vol = nib.load(self.volList[0])
        self.data = vol.get_data()

        # first reference ccordinates
        if self.posx.get() == -1:
            self.posx.set(self.data.shape[0] / 2)
            self.posy.set(self.data.shape[1] / 2)
            self.posz.set(self.data.shape[2] / 2)

        # matrixes initialization
        self.ImXY = zeros((self.data.shape[0], self.data.shape[1], self.nb))
        self.ImYZ = zeros((self.data.shape[1], self.data.shape[2], self.nb))
        self.ImXZ = zeros((self.data.shape[0], self.data.shape[2], self.nb))  

        # normalized slices
        for i, v in enumerate(self.volList):

            # volume loading
            vol = nib.load(v)
            data = vol.get_data()

            # nan are suppressed
            data = ma.where(~isnan(data), data, array(zeros(data.shape)))

            # volume normalization
            mindata = data.min()
            dataNorm = data - mindata
            maxdata = dataNorm.max()
            dataNorm = dataNorm / maxdata
            mindata = dataNorm.min()
            maxdata = dataNorm.max()

            # slices extraction from volume
            self.ImXY[:, :, i] = dataNorm[:, :, self.posz.get()]
            self.ImYZ[:, :, i] = dataNorm[self.posx.get(), :, :]
            self.ImXZ[:, :, i] = dataNorm[:, self.posy.get(), :]

        # show images
        self.imSumShow()

