#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------------------------- #
#                                             GUI tools                                                      #
# ---------------------------------------------------------------------------------------------------------- #

# General functions used for graphical interface.
#
# Methods
# - list2text
# - list2listbox
# - numList2text
#
# Class
# - linkedListboxes
# - AutoScrollbar

from Tkinter import *

# ------------------------------------- #
def list2text(l):
    """ Convert a list of strings or variable strings (l) into a text (t).
Return text t.
If the list is empty, the text is empty.

example :
l = ['line 1','line 2','last line']
-> t =
'line1\nline 2\nlast line'   """

    if len(l) == 0:
        t = ""
    else:
        t = ""
        for i in range(0,len(l)):
            if i == 0:
                if type(l[0]).__name__ == "instance":
                    t = l[0].get()
                else:
                    t = l[0]
            else:
                try :
                    t += "\n"+l[i]
                except TypeError:
                    t += "\n"+l[i].get()
    return t

# ------------------------------------- #
def list2listbox(lb,l):
    """ Insert content of list l (list of strings or variable strings) into listbox lb."""
    
    lb.delete(first=0,last=END)
    if len(l) > 0:
        for p in l:
            if type(l[0]).__name__ == "instance":
                lb.insert(END,p.get())
            else:
                lb.insert(END,p)

# ------------------------------------- #
def numList2text(l):
    """ Generate the numbering of list elements (list l) into text format (t).
        Return text t.
        If list l is empty, t = "".     """
    
    if len(l) == 0:
        t = ""
    else:
        for i in range(0,len(l)):
            if i == 0:
                t = "1."
            else:
                t += "\n"+str(i+1)+"."
    return t

# ------------------------------------- #
def numListbox2listbox(lb,numlb):
    """ Generates the numbering of listbox elements (in lb) to display in another
        listbox (numlb).
        If the listbox is empty, no number is displayed."""
    numlb.delete(first=0,last=END)
    if lb.size() == 0:
        numlb.insert(0,"")
    else:
        for i in range(0,lb.size()):
            numlb.insert(i,str(i+1)+".")

# ------------------------------------- #
class linkedListboxes(Tk):
    """ This class creates an object composed of two listboxes lb1 and lb2 and a vertical scrollbar scrolly, linked together for movements.

System information are loaded with platform module to use appropriate events names and values for scrolling with mouse:
    - <Button-4> and <Button-5> for linux platform
    - <MouseWheel> for others
Windows case has not be tested yet.

Attributes:
    - lb1       listbox lb1 (already defined)
    - lb2       listbox lb2 (already defined)
    - scrolly   vertical scrollbar (already defined, but not linked to any widgets or event)  """

    def __init__(self,lb1,lb2,scrolly):
        """ Set configuration for lb1, lb2 and scolly, and bind methods and events."""
        
        self.lb1 = lb1
        self.lb2 = lb2
        self.scrolly = scrolly

        # scrolling with scrollbar
        self.lb1.config(yscrollcommand=self.scrolly.set,exportselection=0)
        self.lb2.config(yscrollcommand=self.scrolly.set,exportselection=0)
        scrolly.config(command=self.scrollListboxes)

        # scrolling with mouse wheel
        # /!\ for linux : <Button-4> and <Button-5> instead of <MouseWheel>
        # /!\ to be tested for windows
        import platform
        ans = (platform.platform()).lower()
        if ans.find('linux') != -1:
            self.lb1.bind("<Button-4>",self.OnMouseWheelLx)
            self.lb2.bind("<Button-4>",self.OnMouseWheelLx)
            self.lb1.bind("<Button-5>",self.OnMouseWheelLx)
            self.lb2.bind("<Button-5>",self.OnMouseWheelLx)
        elif ans.find('windows') != -1:
            self.lb1.bind("<MouseWheel>",self.OnMouseWheelWin)
            self.lb2.bind("<MouseWheel>",self.OnMouseWheelWin)
        else:
            self.lb1.bind("<MouseWheel>",self.OnMouseWheelMac)
            self.lb2.bind("<MouseWheel>",self.OnMouseWheelMac)

        # linking selection on listboxes
        self.lb1.bind("<<ListboxSelect>>",self.setSelection1)
        self.lb2.bind("<<ListboxSelect>>",self.setSelection2)

    def scrollListboxes(self,*args):
        """ Apply same movement to both lb1 and lb2. This method is called by using scrollbar scrolly. Entries *args are related to scrollbar."""
        self.lb1.yview(*args)
        self.lb2.yview(*args)

    def OnMouseWheelMac(self,event):
        """ Apply vertical scrolling of -1*event.delta to both lb1 and lb2.
            This method is called in Mac platforms when mouse wheel is used.
            Entry event correponds to <MouseWheel>."""
        self.lb1.yview("scroll",-1*event.delta,"units")
        self.lb2.yview("scroll",-1*event.delta,"units")
        return "break"
    
    def OnMouseWheelWin(self,event):    ################## à vérifier
        """ Apply vertical scrolling of event.delta/120 to both lb1 and lb2.
            This method is called in Windows platforms when mouse wheel is used.
            Entry event correponds to <MouseWheel>."""
        self.lb1.yview("scroll",event.delta/120,"units")
        self.lb2.yview("scroll",event.delta/120,"units")
        return "break"
    
    def OnMouseWheelLx(self,event):
        """ Apply vertical scrolling of + or - 1 to both lb1 and lb2.
            This method is called in Linux platforms when mouse wheel is used.
            Entry event correponds to <Button-4> and <Button-5>. Attribute event.num is used to know the scrolling direction."""
        if event.num == 4:
            ev = -1
        elif event.num == 5:
            ev = 1
        self.lb1.yview("scroll",ev,"units")
        self.lb2.yview("scroll",ev,"units")
        return "break"

    def setSelection1(self,*args):
        """ Set same selection on lb2 than lb1.
            This method is called by event <<ListboxSelect>> on lb1.
            Entries arg are due to event <<ListboxSelect>>."""
        sel = self.lb1.curselection()
        if len(sel)>0:
            self.lb2.selection_clear(first=0,last=END)
            self.lb2.selection_set(first=sel[0])
            
    def setSelection2(self,*args):
        """ Set same selection on lb1 than lb2.
            This method is called by event <<ListboxSelect>> on lb2.
            Entries arg are due to event <<ListboxSelect>>."""
        sel = self.lb2.curselection()
        if len(sel)>0:
            self.lb1.selection_clear(first=0,last=END)
            self.lb1.selection_set(first=sel[0])

    def updateView(self,index):
        """ Set new selection on lb1 and lb2 and same vertical position.
            The selected element is given by entry index, which is a positive integer."""
        self.lb1.selection_clear(first=0,last=END)
        self.lb1.selection_set(first=index)
        self.lb1.see(index)
        self.lb2.selection_clear(first=0,last=END)
        self.lb2.selection_set(first=index)
        self.lb2.see(index)
        ypos = self.lb1.yview()
        self.lb2.yview_moveto(ypos[0])
        
# ------------------------------------- #
class AutoScrollbar(Scrollbar):
    """ A scrollbar (vertical or horizontal) that hides itself if it's not needed.
    Only works with the grid geometry manager. Scrolling only with scrollbar (not mouse wheel).
    
    Script found at: http://effbot.org/zone/tkinter-autoscrollbar.htm
    Author: Fredrik Lundh
    """
    
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
        
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
        
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"
        
