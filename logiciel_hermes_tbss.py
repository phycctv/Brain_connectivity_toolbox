# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 10:03:07 2013

@author: Renard Felix
"""



import sys
import getopt
import os

from subprocess import call
import glob
import shutil
import nibabel as nib
import numpy as np


#############test function

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

#############

try:
    opts, args = getopt.getopt(sys.argv[1:], "ht:p:d:D:1234", ["help","temoin=","patient=","dir=","Dir=","tbss_1","tbss_2","tbss_3","tbss_4"])
except getopt.GetoptError as err:
    # Affiche l'aide et quitte le programme
    print(err) # Va afficher l'erreur en anglais
    print('Please see the help.') # Fonction à écrire rappelant la syntaxe de la commande
    sys.exit(2)
 
output = None
verbose = False
for o, a in opts:
    if o in ("-h", "--help"):
        # On affiche l'aide
        print('Help of the DTI prepocessing:')
        print('* means that no parameter is needed \n')
        print('     -h , --help: print the help')
        print('     -t , --temoin *: Directory for the first group')        
        print('     -p,  --patient *: Directory for the second group' )
        print('     -d,  --dir *: Directory for the TBSS group (copy the necessary data in this directory)' )        
        print('     -D,  --Dir *: Directory for the TBSS group (no data copy)' )
        print('     -1,  --tbss_1:  First step of TBSS' )
        print('     -2,  --tbss_2:  Second step of TBSS' )
        print('     -3,  --tbss_3:  Third step of TBSS' )
        print('     -4,  --tbss_4:  Fourth step of TBSS' )
        sys.exit()


    elif o in ("-t", "--temoin"):
        #Lecture des fichiers
        cur_dir = a
        if os.path.isdir(cur_dir)==False:
            print("Error")
            print cur_dir + " is not a directory."
            sys.exit(-1)


        print "\n Directory of the raw data for the first group:"+ cur_dir +" \n"
        file_name = cur_dir+"/*/*/*_dti_fa_MNI.nii.gz"
        name_t = glob.glob(file_name)
        if len(name_t)==0:
            print("Error")
            print("No FA files in MNI space are found in " + cur_dir+"/*/*/*_dti_fa_MNI.nii.gz")
            print("Please check the directory tree.")
            sys.exit(-1)

        print name_t

    
    elif o in ("-p","--patient"):
        ##Lecture des fichiers patients
        cur_dir = a
        if os.path.isdir(cur_dir)==False:
            print("Error")
            print cur_dir + " is not a directory."
            sys.exit(-1)

        print "\n Directory of the raw data for the second group:"+ cur_dir +" \n"
        file_name = cur_dir+"/*/*/*_dti_fa_MNI.nii.gz"
        name_p = glob.glob(file_name)
        if len(name_p)==0:
            print("Error")
            print("No FA files in MNI space are found in " + cur_dir+"/*/*/*_dti_fa_MNI.nii.gz")
            print("Please check the directory tree.")
            sys.exit(-1)

        print name_p
 
    elif o in ("-d","--dir"):
        ##Directory of the TBSS study
        print "Directory of the TBSS study \n"

        cur_dir = a
        if os.path.isdir(cur_dir)==False:
            print("Error")
            print cur_dir + " is not a directory."
            sys.exit(-1)
        
        try:
            os.mkdir(cur_dir +"/TBSS_FA_study/")
        except:
            print cur_dir +"/TBSS_FA_study/ already exists." 
            print "Warning! Data will be overwrite...\n"
        
        try:
            print "Copy first group from "+ name_t
        except:
            print "The first group is not set."
            print "Please refer to the help (-h) and fill the -t option"
            sys.exit(-1)
            
        for i in range(len(name_t)):
            tmp_name = "t_"+ name_t[i].split("/")[-1]
            shutil.copy(name_t[i],cur_dir +"/TBSS_FA_study/"+tmp_name)


        try:
            print "Copy second group from "+ name_p
        except:
            print "The first group is not set."
            print "Please refer to the help (-h) and fill the -p option"
            sys.exit(-1)
        
        for i in range(len(name_p)):
            tmp_name = "p_"+ name_p[i].split("/")[-1]
            shutil.copy(name_p[i],cur_dir +"/TBSS_FA_study/"+tmp_name)

    elif o in ("-D","--Dir"):
        ##Directory of the TBSS study
        print "Directory of the TBSS study \n"

        cur_dir = a
        if os.path.isdir(cur_dir)==False:
            print("Error")
            print cur_dir + " is not a directory."
            sys.exit(-1)


    elif o in ("-1","--tbss_1"):
        
        try:
            print "TBSS_1"
            print "TBSS directory=" +cur_dir+"/TBSS_FA_study/"
        except:
            print "The TBSS directory is not set."
            print "Please set the -d parameter (see the help)."
            sys.exit(-1)
            
        path = os.getcwd()
        os.chdir(cur_dir+"/TBSS_FA_study/")
        cmd = sorted(glob.glob(cur_dir+"/TBSS_FA_study/*"))
        cmd1 = []
        for i in range(len(cmd)):
            cmd1.append(cmd[i].split('/')[-1])
        cmd1.insert(0, "tbss_1_preproc")
        print cmd1
        call(cmd1)
        os.chdir(path)
        
    elif o in ("-2","--tbss_2"):
        
        try:
            print "TBSS_2"
            print "TBSS directory=" +cur_dir+"/TBSS_FA_study/"
        except:
            print "The TBSS directory is not set."
            print "Please set the -d parameter (see the help)."
            sys.exit(-1)
            
        path = os.getcwd()
        os.chdir(cur_dir+"/TBSS_FA_study/")
        cmd = "tbss_2_reg -T"
        call(cmd.split(" "))
        os.chdir(path)
        
    elif o in ("-3","--tbss_3"):

        try:
            print "TBSS_3"
            print "TBSS directory=" +cur_dir+"/TBSS_FA_study/"
        except:
            print "The TBSS directory is not set."
            print "Please set the -d parameter (see the help)."
            sys.exit(-1)

        path = os.getcwd()
        os.chdir(cur_dir+"/TBSS_FA_study/")
        cmd = "tbss_3_postreg -S"
        call(cmd.split(" "))
        os.chdir(path)
        
        
    elif o in ("-4","--tbss_4"):
        
        try:
            print "TBSS_4"
            print "TBSS directory=" +cur_dir+"/TBSS_FA_study/"
        except:
            print "The TBSS directory is not set."
            print "Please set the -d parameter (see the help)."
            sys.exit(-1)

        path = os.getcwd()
        os.chdir(cur_dir+"/TBSS_FA_study/")
        cmd = "tbss_4_prestats 0.2"
        call(cmd.split(" "))
        os.chdir(path)