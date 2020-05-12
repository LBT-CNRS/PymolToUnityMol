#!/usr/bin/env python2.7
# coding: utf-8

#-------------------------------------------------------------
# Apache 2.0 licence, see LICENCE file
# Authors: Amélys DEBIOL & Xavier MARTINEZ & Hubert SANTUZ
# Date: 26/07/2019
#-------------------------------------------------------------

#Runs on Python 2.x because of the pymol library

from __future__ import print_function

import sys
import os
import argparse
import pickle

import pymol #This is needed for the pickle.load call

import pymolColors

def isfile(path):
    """Check if path is an existing file.
    If not, raise an error. Else, return the path."""
    if not os.path.isfile(path):
        if os.path.isdir(path):
            msg = "{0} is a directory".format(path)
        else:
            msg = "{0} does not exist.".format(path)
        raise argparse.ArgumentTypeError(msg)
    return path


def pymolToUnityMol(psefile, pycolors, umolfile):
    with open(psefile, 'rb') as f:
        pse = pickle.load(f)
    name = pse['names'] # 'names' contains the list of molecules/selections
    matchingRepre = {"sticks":"Balls&Sticks", "spheres":"VdW", "surface":"s", "label":"",
                     "nb_spheres":"", "cartoon":"c", "ribbon":"c", "lines":"l",
                     "mesh":"wireframe", "dots":"s", "nonbonded":"hbond", "cell":"",
                     "licorice":"Licorice", "wire":"l"}
    nbSele = 0 # selection number per representation
    listeAtom = [] # selection atoms per representation
    cols = "" # selection colors per representation
    sele = [] # selections atomid of pse file
    stock = [] #to print selection at the end

    f_out = open(umolfile, "w")

    printNameMol(pse, f_out) # fetch all molecules

    for molecule in name: # molecule can be a molecule or a selection
        if molecule != name[0] and molecule != []:
            if  molecule[5] != [] and type(molecule[5][0][0]) == int: # molecule
                listeMolRepre = moleculeRepre(molecule[5][7]) # molecule[5][7] == all atoms in selection
                for i in listeMolRepre:
                    if i != 0: #i==0 -> atom hidden
                        atomidAndColors = atomidAndColor(molecule[5][7], i) # list with atomid and color [(atomid, color)]
                        for j in atomidAndColors:
                            cols += "Color" + printColor(pycolors[j[1]]) + ", " # j[1]==couleur
                            listeAtom.append(j[0]) #j[0]==atomid
                        listeAtom.sort()
                        strParRepre = optimisationSele(listeAtom, molecule[0]) # molecule[0] == molecule name
                        nbSele += 1
                        print("select('" + str(strParRepre[:-4]) + "', '" + molecule[0] + "_" + str(nbSele) + "')", file=f_out)
                        for k in representation(i): # in case of superposition of representation or Licorice or Wire
                            if k != "":
                                repre = matchingRepre[k]
                                if repre == "Licorice" or repre == "VdW" or repre == "Balls&Sticks":
                                    print("showSelection('" + molecule[0] + "_"+ str(nbSele) + "', 'hb')", file=f_out)
                                    print("cols" + str(nbSele) + "=List[Color]([" + cols[0:-2] + "])", file=f_out)
                                    print("colorSelection('" + molecule[0] + "_"+str(nbSele) + "', 'hb', cols" + str(nbSele) + ")", file=f_out)
                                    print("setHyperBallMetaphore('" + molecule[0] + "_" + str(nbSele) + "', '" + repre+"')", file=f_out)
                                elif repre == "wireframe":
                                    print("showSelection('" + molecule[0] + "_"+str(nbSele) + "', 's')", file=f_out)
                                    print("cols" + str(nbSele) + "=List[Color]([" + cols[0:-2] + "])", file=f_out)
                                    print("colorSelection('" + molecule[0] + "_" + str(nbSele) + "', 's', cols" + str(nbSele) + ")", file=f_out)
                                    print("setWireframeSurface('" + molecule[0] + "_" + str(nbSele) + "')", file=f_out)

                                else:
                                    print("showSelection('" + molecule[0] + "_" + str(nbSele) + "', '" + repre + "')", file=f_out)
                                    print("cols" + str(nbSele) + "=List[Color]([" + cols[0:-2] + "])", file=f_out)
                                    print("colorSelection('" + molecule[0] + "_" + str(nbSele) + "', '" + repre + "', cols" + str(nbSele) + ")", file=f_out)
                        listeAtom = []
                        strParRepre = ""
                        cols = ""

            if  molecule[5] != [] and type(molecule[5][0][0]) == str: #selection
                for l in range(len(molecule[5])):
                    dicAtom = numberToAtomid(pse, molecule[5][l][0]) #key == number; value == atomid
                    for m in molecule[5][l][1]:
                        sele.append(dicAtom[m])
                    sele.sort()
                    strSele += optimisationSele(sele, molecule[5][l][0])

                    sele = []
                strSele = strSele[:-4] + "','" + molecule[0]
                stock.append(strSele)
            strSele = ""
    for m in stock:
        print("select('"+m+"')", file=f_out)
    print("clearSelections()", file=f_out)

    f_out.close()


def printNameMol(pse, f_out):
    """
    save all molecules in the file
    """
    name = pse['names']
    for mol in name:
        if mol != name[0] and mol != []:
            if  mol[5] != []and type(mol[5][0][0]) == int:
                print("fetch('" + mol[0] + "', showDefaultRep=False)", file=f_out)


def moleculeRepre(mol):
    """
    Return the list of all representations of one molecule
    """
    listeRepre = []
    for atom in mol:
        if atom[20] not in listeRepre:
            listeRepre.append(atom[20])
    return listeRepre


def atomidAndColor(mol, repre):
    """
    Return a dict which contains the atomid with their associated color
    for each representation.
    """
    dicRepre = {}
    for atom in mol:
        if atom[20] == repre:
            dicRepre[atom[22]] = atom[21]
    return sorted(dicRepre.items(), key=lambda t: t[0])


def printColor(c):
    return '(%0.2f, %0.2f, %0.2f)'%(c[0], c[1], c[2])


def optimisationSele(listeAtom, molecule):
    """
    Return a optimized list to do selections
    """
    strParRepre = ""
    listeSele = []
    if len(listeAtom) == 1:
        return "atomid " + str(listeAtom[0]) + " and " + molecule + " or "
    for a in range(len(listeAtom)-1):
        if listeAtom[a] + 1 == listeAtom[a+1]:
            listeSele.append(listeAtom[a])

            if a == len(listeAtom)-2:  # end of selection
                listeSele.append(listeAtom[a+1])
                strParRepre += "atomid " + str(listeSele[0]) + ":"+str(listeSele[-1]) + " and " + molecule + " or "
                listeSele = []

        if listeAtom[a] + 1 != listeAtom[a+1]: #s'il ne se suivent pas
            listeSele.append(listeAtom[a])
            if a == len(listeAtom) - 2:
                listeSele.append(listeAtom[a+1])
            if len(listeSele) != 1:
                strParRepre += "atomid " + str(listeSele[0]) + ":" + str(listeSele[-1]) + " and " + molecule+" or "
                listeSele = []

            elif len(listeSele) == 1:
                strParRepre += "atomid " + str(listeSele[0]) + " and " + molecule + " or "
                listeSele = []
    return strParRepre


def representation(repreNumber):
    """
    Return the list of representation per atom
    """
    liste = []
    bitsdictionary = {0:'sticks', 1:'spheres', 2:'surface', 3:'label', 4:'nb_spheres', 5:'cartoon',
                      6:'ribbon', 7:'lines', 8:'mesh', 9:'dots', 10:'unknown', 11:'nonbonded',
                      12:'cell', 20:'valence'}
    a = bits(repreNumber)
    compteur = 0
    for i in a[::-1]:
        if int(i) == 1:
            liste.append(bitsdictionary[compteur])
        compteur += 1
    for z in range(0, len(liste) - 1):
        if liste[z] == 'lines' and liste[z+1] == 'nonbonded':
            liste[z] = "wire"
            liste[z+1] = ""
        if liste[z] == 'sticks' and liste[z+1] == 'nb_spheres':
            liste[z] = "licorice"
            liste[z+1] = ""
    return liste


def bits(repreNumber):
    """
    Return the atom representation in binary
    """
    return "{0:b}".format(int(repreNumber))


def numberToAtomid(pse, mol):
    name = pse['names']
    dic_atom = {}
    for molecule in name:
        if molecule != name[0] and molecule != []:
            if  molecule[5] != [] and type(molecule[5][0][0]) == int:
                if molecule[0] == mol:
                    for a in molecule[5][7]:
                        dic_atom[a[36]] = a[22] #a[36] == n° in .pse; a[22] == atomid
    return dic_atom


def define_options(argv):
    """Define the script options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", action="store", type=isfile, dest="filin",
                        required=True, help=("The Pymol session file"))
    parser.add_argument("-o", action="store", type=str, dest="filout",
                        default="UMolSession.py",
                        help="The output Umol session file.")
    args = parser.parse_args(argv)
    return args


if __name__ == "__main__":
    #Command line parsing
    args = define_options(sys.argv[1:])

    pycolors = pymolColors.dicColor()
    pymolToUnityMol(args.filin, pycolors, args.filout)
