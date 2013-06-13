# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:19:45 2013

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

#from save_fib_ROI_hermes import *

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
    opts, args = getopt.getopt(sys.argv[1:], "hd:t:rRv", ["help","dir=","template=","reglin","Regnonlin","grad","eddy","erosion","dti","trackvis="])
except getopt.GetoptError as err:
    # Affiche l'aide et quitte le programme
    print(err) # Va afficher l'erreur en anglais
    print('Please see the help.') # Fonction à écrire rappelant la syntaxe de la commande
    sys.exit(2)
 
output = None
verbose = False
for o, a in opts:
    if o == "-v":
        # On place l'option 'verbose' à True
        verbose = True


    elif o in ("-h", "--help"):
        # On affiche l'aide
        print('Help of the DTI prepocessing:')
        print('* means that no parameter is needed \n')
        print('     -h , --help: print the help')
        print('     -d , --dir *: Source directory (MUST be set)')        
        print('     -t,  --template *: Add a template for FA registration' )
        print('     -r , --reglin : Linear registration ')
        print('     -R , --Regnonlin : Non linear registration' )
        print('     -a , --applywarp *: Apply warp on the FA images ')        
        sys.exit()


    elif o in ("-d", "--dir"):
        #Lecture des fichiers
        cur_dir = a
        if os.path.isdir(cur_dir)==False:
            print("Error")
            print cur_dir + " is not a directory."
            sys.exit(-1)


        print "\n Directory of the raw data:"+ cur_dir +" \n"
        file_name = cur_dir+"/*/*/*REC"
        name = glob.glob(file_name)
        if len(name)==0:
            print("Error")
            print("No REC files are found in " + cur_dir+"/*/*/*REC")
            print("Please check the directory tree.")
            sys.exit(-1)

        #recupere les noms des dossiers
        dir_name = []
        dir_name.append("/")
        name_pat = []
        for i in range(len(name)):
            L = name[i].split("/")[1:-1]
            for j in range(len(L)):
                dir_name[i] = dir_name[i] + L[j] +"/"
            dir_name.append("/")
            name_pat.append(L[j])
        dir_name.pop()


    
    elif o in ("-t","--template"):
        ##definir un template
        if  os.path.isfile(a)==False:
            print("Error")
            print a + " is not a file."
            sys.exit(-1)
        else:
            FA_template = a
            
    elif o in ("-r","--reglin"):
        ##recalage lineaire
        print "Linear registration \n"

        try:
            name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        try:
            FA_template
        except NameError:
            print("Set the FA template by default")
            FA_template = "/home/renardfe/Logiciel/fsl/data/standard/FMRIB58_FA_1mm.nii.gz"
        
        for i in range(len(name)):
                print dir_name[i]
                im_in = dir_name[i]+name_pat[i]+"_dti_fa.nii"
                im_out = dir_name[i]+name_pat[i]+"_dti_fa_MNI.nii.gz"
                omat = dir_name[i]+name_pat[i]+"transfo_linear_fa.mat"
                cmd = "flirt -in "+im_in+" -ref "+FA_template+" -out "+im_out+" -omat "+omat+" -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear"
                call(cmd.split())


        #calcul de la transfo inverse lineaire (inversion de matrice)
        print "Inverse the linear transformation \n"
        for i in range(len(dir_name)):
            print dir_name[i]
            omat = dir_name[i]+name_pat[i]+"transfo_linear_fa.mat"
            omat_inv = dir_name[i]+name_pat[i]+"transfo_linear_fa.mat"
            cmd = "convert_xfm -omat "+omat+" -inverse "+omat_inv
            call(cmd.split())


    elif o in ("-R","--Regnonlin"):
        ##recalage non lineaire
        print "Non linear registration \n"

        try:
            name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        try:
            FA_template
        except NameError:
            print("Set the FA template by default")
            FA_template = "/home/renardfe/Logiciel/fsl/data/standard/FMRIB58_FA_1mm.nii.gz"
        

        for i in range(len(dir_name)):
            print dir_name[i]
            im_in = dir_name[i]+name_pat[i]+"_dti_fa_MNI.nii.gz"
            im_out = dir_name[i]+name_pat[i]+"_dti_fa_MNI_NL.nii.gz"
            im_cout = dir_name[i]+name_pat[i]+"_dti_fa_warp_coeff.nii.gz"
            im_fout = dir_name[i]+name_pat[i]+"_dti_fa_warp_field.nii.gz"	
            cmd = "fnirt --in="+im_in +" --ref="+FA_template + " --iout="+ im_out+" --cout="+im_cout+" --fout="+im_fout
            call(cmd.split())

        #calcul de la transfo inverse non lineaire
        print "Inverse the non linear registration field \n"
        for i in range(len(dir_name)):
            print dir_name[i]
            ref = dir_name[i]+name_pat[i]+"_dti_fa_MNI.nii.gz"
            im_fout = dir_name[i]+name_pat[i]+"_dti_fa_inv_warp_field.nii.gz"
            im_fin = dir_name[i]+name_pat[i]+"_dti_fa_warp_field.nii.gz"	
            cmd = "invwarp --warp="+im_fin +" --ref="+ref + " --out="+im_fout
            call(cmd.split())

    elif o in ("-a","--applywarp"):
        ##recalage non lineaire
        print "Apply warp on the data \n"

        try:
            name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        #application de la transfo inverse non lineaire puis lineaire
        for i in range(len(dir_name)):
            print dir_name[i]    
            im_ref_lin = dir_name[i]+name_pat[i]+"_dti_fa.nii"
            im_out = dir_name[i]+name_pat[i]+"_dti_label_MNI.nii.gz"
            im_ref = dir_name[i]+name_pat[i]+"_dti_fa_MNI.nii.gz"
            im_warp = dir_name[i]+name_pat[i]+"_dti_fa_warp_field.nii.gz"
            omat_inv = dir_name[i]+name_pat[i]+"transfo_linear_fa.mat"
            cmd = "applywarp --in="+label_template+" --out="+im_out+" --ref="+im_red+" --warp="+im_warp+" --interp=nn"
            call(cmd.split())
            cmd = "flirt -applyxfm -interp nearestneighbour -init "+omat_inv+" -out "+im_out+" -ref "+im_ref_lin+" -in "+im_out
            call(cmd.split())
     

#    verif la cmd apply inv lineaire avec 2 im_out
#    
#FA_template = "/soft/fsl/data/standard/FMRIB58_FA_1mm.nii.gz"
#label_template = acomplete
#label_CC = acomplete
#
#    
#
#
##faire stats faisceau archee_D
#ind = 16
#fibre = 'faisceau_archee_D'
#modalite = '_FA_'
#name_coord = 'Z'
#img_label = nib.load(label_template)
#data_label = img_label.get_data()
#ind_lab = np.where(data_label == ind)
#u_lab,ind_lab_unique = np.unique(ind_lab,return_inverse = True)
#tmp = tmp.shape[0]
#fib_stat = np.zeros(tmp,3)
#for i in range(len(dir_name)):
#    print dir_name[i]
#    csv_file = dir_name[i]+name_pat[i]+modalite+fibre+'.csv'
#    file_name = dir_name[i]+name_pat[i]+"_dti_fa_MNI_NL.nii.gz"
#    img = nib.load(file_name)
#    data = img.get_data()
#    for j in range(tmp):
#        L = []
#        for k in range(ind_lab[:,ind_lab_unique==j]):
#            L.append(data[IND[:,ind_lab_unique==j][0,k],IND[:,ind_lab_unique==j][1,k],IND[:,ind_lab_unique==j][2,k]])
#        fib_stat[j,0] = u_lab[j]
#        fib_stat[j,1] = mean(L) 
#        fib_stat[j,2] = var(L)
#    write_csv(fib_stat,csv_file,name_pat[i],fibre,name_coord)
#    