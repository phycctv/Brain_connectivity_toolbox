# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 09:55:38 2013

@author: Felix Renard
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
    opts, args = getopt.getopt(sys.argv[1:], "hd:lgemrct:v", ["help","dir=","load","grad","eddy","mask","erosion","dti","trackvis="])
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
        print('     -d , --dir : Source directory (MUST be set)')
        print('     -l , --load *: transform the dicom into nifti via dcm2nii ')
        print('     -g , --grad *: Apply correction to the gradient' )
        print('     -e , --eddy *: Apply Eddy current correction on DWIs ')        
        print('     -m , --mask *: Apply BET algorithm to estimate mask ')        
        print('     -r , --erosion *: Apply erosion on the current mask ')
        print('     -t,  --trackvis: Repertory of the trackvis and dtk' )
        print('     -c , --dti *: Estimate the coefficients FA, MD, eigen values and vectors with Trackvis')        
        sys.exit()


    elif o in ("-d", "--dir"):
        #Lecture des fichiers
        cur_dir = a
        print a
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


    elif o in ("-l","--load"):
        #Transformation des PAR REC avec dicom2nii
        print "Convert dicom to nifti \n"

        try:
            name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)


        for i in range(len(name)):
            cmd = "dcm2nii -o "+dir_name[i]+" "+ name[i]
            call(cmd.split())
        #Modifier le fichier en raw_diff
        for i in range(len(dir_name)):
            print dir_name[i]
            file_name = glob.glob(dir_name[i]+"*.nii.gz")    
            shutil.move(file_name[0],dir_name[i]+name_pat[i]+"_raw_diff.nii.gz")
            cmd = "fslmaths "+dir_name[i]+name_pat[i]+"_raw_diff.nii.gz -add 0 "+dir_name[i]+name_pat[i]+"_raw_diff.nii.gz"
            call(cmd.split())
            img = nib.load(dir_name[i]+name_pat[i]+"_raw_diff.nii.gz")
            aff = img.get_affine()
            hdr = img.get_header()
            img = img.get_data()
            img2 = np.zeros(img.shape)
            for j in range(70*61):
                q1 = np.divide(j,61)
                q2 = np.divide(j,70)
                r1 = np.mod(j,61)
                r2 = np.mod(j,70)
                img2[:,:,q1,r1] = img[:,:,r2,q2]
            img = nib.Nifti1Image(img2, aff,header=hdr)
            img.to_filename(dir_name[i]+name_pat[i]+"_raw_diff.nii.gz")


    elif o in ("-e","--eddy"):
        #eddy current correction
        print "Eddy current correction \n"

        try:
            dir_name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        for i in range(len(dir_name)):
            print dir_name[i]
            cmd = "eddy_correct "+dir_name[i]+name_pat[i]+ "_raw_diff.nii.gz " +dir_name[i]+name_pat[i]+ "_ec_data.nii.gz 1"
            call(cmd.split())
            
    elif o in ("-g","--grad"):
        cur_dir_tmp = os.curdir
        print('Gradient correction')
        dir_grad = sys.path[0]
        try:
            dir_name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        for i in range(len(dir_name)):
            print dir_name[i]
            os.chdir(dir_name[i])            
            #shutil.copy(dir_grad+'/gen_table.sh','.')           
            fichier = open("gen_table.sh", "w")
            fichier.write("matlab -nodesktop -r ' addpath "+dir_grad+" , genGradTable , quit()' ")
            fichier.close()
            cmd = './gen_table.sh'
            call(cmd.split(),shell=True)
        os.chdir(cur_dir_tmp)


    elif o in ("-m","--mask"):
        #estimation du masque
        print "Mask estimation \n"

        try:
            dir_name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        for i in range(len(dir_name)):
            print dir_name[i]
            cmd = "fslmaths "+dir_name[i]+name_pat[i]+ "_ec_data.nii.gz -Tmean "+dir_name[i]+name_pat[i]+ "_ec_data_mean.nii.gz"
            call(cmd.split())
            cmd = "bet "+dir_name[i]+name_pat[i]+ "_ec_data_mean.nii.gz "+ dir_name[i]+name_pat[i]+"_ec_data_mean_brain.nii.gz  -f 0.5 -g 0 -m"
            call(cmd.split())

    elif o in ("-r","-erosion"):
        print('Mask erosion')
        
        try:
            dir_name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)

        for i in range(len(dir_name)):
            print dir_name[i]
            cmd = "fslmaths "+dir_name[i]+name_pat[i]+"_ec_data_mean_brain_mask.nii.gz -ero "+dir_name[i]+name_pat[i]+"_mask_ero.nii.gz"
            call(cmd.split())
            cmd = "fslmaths "+dir_name[i]+name_pat[i]+"_mask_ero.nii.gz -ero "+dir_name[i]+name_pat[i]+"_mask_ero_2.nii.gz"
            call(cmd.split())
            cmd = "fslmaths "+dir_name[i]+name_pat[i]+"_ec_data -mas "+dir_name[i]+name_pat[i]+"_mask_ero "+dir_name[i]+name_pat[i]+"_mdata_diff"
            call(cmd.split())
            cmd = "fslmaths "+dir_name[i]+name_pat[i]+"_ec_data -mas "+dir_name[i]+name_pat[i]+"_mask_ero_2 "+dir_name[i]+name_pat[i]+"_mdata_diff_2"
            call(cmd.split())   

    elif o in ("-t","--trackvis"):
        print a
        if os.path.isdir(a)==False:
            print("Error")
            print a + " is not a directory."
            sys.exit(-1)
        trackvis = a +"/"


    elif o in ("-c","--dti"):
        #calcul des coeffs DTI
        try:
            dir_name
        except NameError:
            print("Error with directory")
            print("Directory is no set or empty.")
            print("Please specify the -d or --dir parameters.")
            sys.exit(-1)
        try:
            trackvis
        except NameError:
            if which("dti_recon")==None :
                print("dti_recon is not recognized.")
                print("Please add dti_recon to your PATH,")
                print("or fill the -t or -trackvis option")
                sys.exit(-1)
            for i in range(len(dir_name)):
                cmd = "dti_recon "+dir_name[i]+name_pat[i]+"_raw_diff.nii.gz "+dir_name[i]+name_pat[i]+"_dti -gm "+dir_name[i]+"grad_table.txt"
                call(cmd.split())
        for i in range(len(dir_name)):
                print i
                cmd = trackvis+"dti_recon "+dir_name[i]+name_pat[i]+"_raw_diff.nii.gz "+dir_name[i]+name_pat[i]+"_dti -gm "+dir_name[i]+"grad_table.txt"
                print cmd
                call(cmd.split())
    else:
        print("Unknown {} option".format(o))
        sys.exit(2)

