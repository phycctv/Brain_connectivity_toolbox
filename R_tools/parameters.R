rm(list=ls())


############### parameters TO CHECK #################

## Use the new template given by Nicolas

n.regions<-116

distance<-"norm"
method<-'modwt'
 wf <- "la8"
 boundary <- "periodic"
n.levels<-4

p<-0.05
proc.length<-400
n.ind<-0
use.atanh<-FALSE
num.levels<-3
  var.ind<-0
test.method<-"gaussian"

num.nb.edges<-seq(100,4000,100)
length.nb.edges<-length(num.nb.edges)

################ Name of patients

##name.patients<-c(0,3,6:18)
##num.patient<-length(name.patients)

#name.patients<-c(0,3,7:11,13,14,15,16,17,18:20,22,24)
#name.patients<-c(0,3,7:11,13,15,16,18:20,22,24)

#num.patient<-length(name.patients)

name.red.classic <- c("PreCG", "SFGdor", "ORBsup", "MFG", "ORBmid",
"IFGoperc", "IFGtriang",
"ORBinf", "ROL", "SMA",
"OLF", "SFGmed", "ORBsupmed", "REC", "INS", "ACG", "DCG", "PCG", "HIP",
"PHG", "AMYG", "CAL", "CUN", "LING", "SOG", "MOG",
"IOG", "FFG", "PoCG", "SPG", "IPL", "SMG", "ANG",
"PCUN", "PCL", "CAU", "PUT",
"PAL", "THA","HES", "STG", "TPOsup", "MTG", "TPOmid", "ITG")


noms_classic <- c("PreCG.L", "PreCG.R", "SFGdor.L", "SFGdor.R", "ORBsup.L",
"ORBsup.R", "MFG.L", "MFG.R", "ORBmid.L", "ORBmid.R",
"IFGoperc.L", "IFGoperc.R", "IFGtriang.L", "IFGtriang.R",
"ORBinf.L", "ORBinf.R", "ROL.L", "ROL.R", "SMA.L", "SMA.R",
"OLF.L", "OLF.R", "SFGmed.L", "SFGmed.R", "ORBsupmed.L",
"ORBsupmed.R", "REC.L", "REC.R", "INS.L", "INS.R", "ACG.L",
"ACG.R", "DCG.L", "DCG.R", "PCG.L", "PCG.R", "HIP.L", "HIP.R",
"PHG.L", "PHG.R", "AMYG.L", "AMYG.R", "CAL.L", "CAL.R", "CUN.L",
"CUN.R", "LING.L", "LING.R", "SOG.L", "SOG.R", "MOG.L", "MOG.R",
"IOG.L", "IOG.R", "FFG.L", "FFG.R", "PoCG.L", "PoCG.R", "SPG.L",
"SPG.R", "IPL.L", "IPL.R", "SMG.L", "SMG.R", "ANG.L", "ANG.R",
"PCUN.L", "PCUN.R", "PCL.L", "PCL.R", "CAU.L", "CAU.R", "PUT.L", "PUT.R",
"PAL.L", "PAL.R", "THA.L", "THA.R", "HES.L", "HES.R", "STG.L",
"STG.R", "TPOsup.L", "TPOsup.R", "MTG.L", "MTG.R", "TPOmid.L",
"TPOmid.R", "ITG.L", "ITG.R")