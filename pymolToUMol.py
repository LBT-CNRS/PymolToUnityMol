#! /usr/bin/env python2.7
# coding: utf-8

#-------------------------------------------------------------
# Apache 2.0 licence, see LICENCE file
# Authors: Amélys DEBIOL & Xavier MARTINEZ
# Date: 26/07/2019
#-------------------------------------------------------------

#Runs on Python 2.x because of the pymol library

import pickle
import pymol #This is needed for the pickle.load call
import sys
from math import *
from array import *


def pymolToUnityMol(filepath):
	pse=pickle.load(open(filepath, 'rb')) # binaire -> ascii
	name=pse['names'] # names est la clé qui contient la liste des molécules/sélection ainsi que leurs pptés
	matchingRepre={"sticks":"Balls&Sticks","spheres":"VdW","surface":"s","label":"","nb_spheres":"","cartoon":"c","ribbon":"c","lines":"l","mesh":"wireframe","dots":"s","nonbonded":"hbond","cell":"", "licorice":"Licorice","wire":"l"}
	nbSele=0 # n° des sélections par représentation
	listeAtom=[] #liste atomes des sélection par représentation
	cols = "" #liste des couleurs de chaque sélection par représentation
	sele=[] #liste des atomid des sélections du .pse
	stock=[] #permet d'afficher les sélections à la fin
	printNameMol(filepath) # fetch toutes les molécules 

	for molecule in name: # molecule peut être une molecule ou une selection
		if molecule!=name[0] and molecule!=[]: #name[0]==None []== sélection vide
			if  molecule[5]!= [] and type(molecule[5][0][0])==int: # molecule
				listeMolRepre=moleculeRepre(molecule[5][7]) #liste de toutes les représentations ; molecule[5][7] == liste de tous les atomes de la sélection
				for i in listeMolRepre :
					if i!= 0: #i==0 -> atome caché 
						atomidAndColors=atomidAndColor(molecule[5][7],i) # liste contenant atomid et couleur : [(atomid,color)]   
						for j in atomidAndColors :
							cols+="Color"+printColor(pymolColors[j[1]])+", " #j[1]==couleur
							listeAtom.append(j[0])	#j[0]==atomid
						listeAtom.sort()	
						strParRepre=optimisationSele(listeAtom, molecule[0]) # sélection optimisée, molecule[0] == nom de la molécule	
						nbSele+=1
						print("select('"+str(strParRepre[:-4])+"', '"+molecule[0]+"_"+str(nbSele)+"')") #afficher les sélections par représentation
						for k in representation(i):	# en cas de superposition de représentations ou Licorice ou Wire			
							if k!="":
								repre=matchingRepre[k]								
								if repre=="Licorice" or repre=="VdW" or repre=="Balls&Sticks":
									print("showSelection('"+molecule[0]+"_"+str(nbSele)+"', 'hb')")
									print("cols"+str(nbSele)+"=List[Color](["+cols[0:-2]+"])")
									print("colorSelection('"+molecule[0]+"_"+str(nbSele)+"', 'hb', cols"+str(nbSele)+")")
									print("setHyperBallMetaphore('"+molecule[0]+"_"+str(nbSele)+"', '"+repre+"')")
								elif repre=="wireframe":
									print("showSelection('"+molecule[0]+"_"+str(nbSele)+"', 's')")
									print("cols"+str(nbSele)+"=List[Color](["+cols[0:-2]+"])")
									print("colorSelection('"+molecule[0]+"_"+str(nbSele)+"', 's', cols"+str(nbSele)+")")
									print("setWireframeSurface('"+molecule[0]+"_"+str(nbSele)+"')")

								else:
									print("showSelection('"+molecule[0]+"_"+str(nbSele)+"', '"+repre+"')")
									print("cols"+str(nbSele)+"=List[Color](["+cols[0:-2]+"])")
									print("colorSelection('"+molecule[0]+"_"+str(nbSele)+"', '"+repre+"', cols"+str(nbSele)+")")
						listeAtom=[]
						strParRepre =""
						cols=""

			if  molecule[5]!= [] and type(molecule[5][0][0])==str: #sélection
				for l in range(len(molecule[5])):
					dicAtom=numberToAtomid(molecule[5][l][0]) #clé == number; value == atomid , toutes les correspondances de la molécules
					for m in molecule[5][l][1]:  
						sele.append(dicAtom[m])
					sele.sort()
					strSele+=optimisationSele(sele,molecule[5][l][0])

					sele=[]								
				strSele=strSele[:-4]+"','"+molecule[0]
				stock.append(strSele)
			strSele	=""
	for m in stock:
		print("select('"+m+"')")
	print("clearSelections()")

def printNameMol(filepath): #affiche toutes les molécules présentes dans le fichier
	pse=pickle.load(open(filepath, 'rb')) 
	name=pse['names'] 
	for mol in name: 
		if mol!=name[0] and mol!=[]: 
			if  mol[5]!= []and type(mol[5][0][0])==int: 
				print("fetch('"+mol[0]+"', showDefaultRep=False)") 

def moleculeRepre(mol): #renvoie la liste de toutes les représentations (chifrées) d'une molécule
	listeRepre=[]
	for atom in mol:
		if atom[20] not in listeRepre: #permet de ne pas avoir de doublons/liste à ralonge
			listeRepre.append(atom[20])
	return listeRepre

def atomidAndColor(mol,repre): #renvoie un dico contenant les atomid (clé) et leur couleur associée (valeur) pour chaque représentation
	dicRepre={}
	for atom in mol:
		if atom[20]==repre:
			dicRepre[atom[22]]=atom[21] #n° atome puis couleur
	return sorted(dicRepre.items(), key=lambda t: t[0])

def printColor(c):
	return '(%0.2f, %0.2f, %0.2f)'%(c[0],c[1],c[2])

def optimisationSele(listeAtom, molecule): #renvoie la liste optimiser pour faire les sélections
	strParRepre	=""
	listeSele=[]
	if len(listeAtom)==1:
		return "atomid "+str(listeAtom[0])+" and "+molecule+" or "
	for a in range(len(listeAtom)-1):
		if listeAtom[a]+1==listeAtom[a+1]: #si les atomid se suivent 
			listeSele.append(listeAtom[a]) #on les ajoute à la liste de sélection
								
			if a==len(listeAtom)-2:  # on arrive à la fin de la sélection
				listeSele.append(listeAtom[a+1]) 
				strParRepre+="atomid "+str(listeSele[0])+":"+str(listeSele[-1])+" and "+molecule+" or "
				listeSele=[]

		if listeAtom[a]+1!=listeAtom[a+1]: #s'il ne se suivent pas
			listeSele.append(listeAtom[a])
			if a==len(listeAtom)-2:
				listeSele.append(listeAtom[a+1])
			if len(listeSele)!=1:
		 		strParRepre+="atomid "+str(listeSele[0])+":"+str(listeSele[-1])+" and "+molecule+" or "
		 		listeSele=[]
									
			elif len(listeSele)==1:
				strParRepre+="atomid "+str(listeSele[0])+" and "+molecule+" or "
				listeSele=[]
	return strParRepre	

def representation(repreNumber): #renvoie la liste des représentation par atome (superposition etc)
	liste=[] 
	bitsdictionary={0:'sticks', 1:'spheres', 2:'surface', 3:'label', 4:'nb_spheres', 5:'cartoon', 6:'ribbon', 7:'lines', 8:'mesh', 9:'dots', 10:'unknown', 11:'nonbonded', 12:'cell', 20:'valence'}
	a=bits(repreNumber)
	compteur=0  
	for i in a[::-1]: #parcours la liste à l'envers car binaire
		if int(i)==1:				
			liste.append(bitsdictionary[compteur])
		compteur+=1
	for z in range(0,len(liste)-1):
		if liste[z]=='lines' and liste[z+1]=='nonbonded':
			liste[z]="wire"
			liste[z+1]=""
		if liste[z]=='sticks' and liste[z+1]=='nb_spheres':
			liste[z]="licorice"
			liste[z+1]=""
	return liste
	
def bits(repreNumber) : #renvoie la représentation de l'atome en binaire	
	return "{0:b}".format(int(repreNumber))

def numberToAtomid(mol): #fonction utile pour les sélections
	pse=pickle.load(open(filepath, 'rb')) 
	name=pse['names'] 
	dicAtom={}
	for molecule in name:
		if molecule!=name[0] and molecule!=[]: 
			if  molecule[5]!= [] and type(molecule[5][0][0])==int: 
				if molecule[0]==mol:
					for a in molecule[5][7]:
						dicAtom[a[36]]=a[22] #a[36] == n° in .pse; a[22] == atomid
	return dicAtom

def dicColor(): # renvoie la liste de toutes les couleurs possibles générées par PyMol
	dic={}
	# #color->Name = reg_name(I->Idx, n_color, "white")
	n_color=0
	color=0
	liste=[]

	liste.append(1.0)
	liste.append(1.0)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# #color->Name = reg_name(I->Idx, n_color, "black")

	liste.append(0.0)
	liste.append(0.0)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# #color->Name = reg_name(I->Idx, n_color, "blue")

	liste.append(0.0)
	liste.append(0.0)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "green")

	liste.append(0.0)
	liste.append(1.0)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "red")

	liste.append(1.0)
	liste.append(0.0)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	
	

	# color->Name = reg_name(I->Idx, n_color, "cyan")
	liste.append(0.0)
	liste.append(1.0)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "yellow")
	liste.append(1.0)
	liste.append(1.0)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "dash")
	liste.append(1.0)
	liste.append(1.0)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "magenta")
	liste.append(1.0)
	liste.append(0.0)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "salmon")
	liste.append(1.0)
	liste.append(0.6)       #/* was 0.5 */
	liste.append(0.6)       #/* wat 0.5 */
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "lime")
	liste.append(0.5)
	liste.append(1.0)
	liste.append(0.5)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "slate")
	liste.append(0.5)
	liste.append(0.5)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "hotpink")
	liste.append(1.0)
	liste.append(0.0)
	liste.append(0.5)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "orange")
	liste.append(1.0)
	liste.append(0.5)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "chartreuse")        /* AKA puke green */
	liste.append(0.5)
	liste.append(1.0)
	liste.append(0.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "limegreen")
	liste.append(0.0)
	liste.append(1.0)
	liste.append(0.5)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "purpleblue")        /* legacy name */
	liste.append(0.5)
	liste.append(0.0)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "marine")
	liste.append(0.0)
	liste.append(0.5)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "olive")
	liste.append(0.77)
	liste.append(0.70)
	liste.append(0.00)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "purple")
	liste.append(0.75)
	liste.append(0.00)
	liste.append(0.75)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "teal")
	liste.append(0.00)
	liste.append(0.75)
	liste.append(0.75)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "ruby")
	liste.append(0.6)
	liste.append(0.2)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "forest")
	liste.append(0.2)
	liste.append(0.6)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "deepblue")  /* was "deep" */
	liste.append(0.25)
	liste.append(0.25)
	liste.append(0.65)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "grey")      /* english spelling */
	liste.append(0.5)
	liste.append(0.5)
	liste.append(0.5)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "gray")      /* american spelling */
	liste.append(0.5)
	liste.append(0.5)
	liste.append(0.5)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "carbon")
	liste.append(0.2)
	liste.append(1.0)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "nitrogen")
	liste.append(0.2)
	liste.append(0.2)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "oxygen")
	liste.append(1.0)
	liste.append(0.3)
	liste.append(0.3)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "hydrogen")
	liste.append(0.9)
	liste.append(0.9)
	liste.append(0.9)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "brightorange")
	liste.append(1.0)
	liste.append(0.7)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "sulur")
	liste.append(0.9)       #/* needs to be ar enough rom "yellow" */
	liste.append(0.775)     #/* to be resolved, while still slightly on */)
	liste.append(0.25)      #/* the yellow side o yelloworange */
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "tv_red")
	liste.append(1.0)
	liste.append(0.2)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "tv_green")
	liste.append(0.2)
	liste.append(1.0)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "tv_blue")
	liste.append(0.3)
	liste.append(0.3)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "tv_yellow")
	liste.append(1.0)
	liste.append(1.0)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "yelloworange")
	liste.append(1.0)
	liste.append(0.87)
	liste.append(0.37)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "tv_orange")
	liste.append(1.0)
	liste.append(0.55)
	liste.append(0.15)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	
	
	# color->Name = reg_name(I->Idx, n_color, "br0")
	liste.append(0.1)
	liste.append(0.1)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br1")
	liste.append(0.2)
	liste.append(0.1)
	liste.append(0.9)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br2")
	liste.append(0.3)
	liste.append(0.1)
	liste.append(0.8)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br3")
	liste.append(0.4)
	liste.append(0.1)
	liste.append(0.7)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br4")
	liste.append(0.5)
	liste.append(0.1)
	liste.append(0.6)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br5")
	liste.append(0.6)
	liste.append(0.1)
	liste.append(0.5)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br6")
	liste.append(0.7)
	liste.append(0.1)
	liste.append(0.4)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br7")
	liste.append(0.8)
	liste.append(0.1)
	liste.append(0.3)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br8")
	liste.append(0.9)
	liste.append(0.1)
	liste.append(0.2)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "br9")
	liste.append(1.0)
	liste.append(0.1)
	liste.append(0.1)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "pink")
	liste.append(1.0)
	liste.append(0.65)
	liste.append(0.85)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "irebrick")
	liste.append(0.698)
	liste.append(0.13)
	liste.append(0.13)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	
	
	# color->Name = reg_name(I->Idx, n_color, "chocolate")
	liste.append(0.555)
	liste.append(0.222)
	liste.append(0.111)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "brown")
	liste.append(0.65)
	liste.append(0.32)
	liste.append(0.17)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "wheat")
	liste.append(0.99)
	liste.append(0.82)
	liste.append(0.65)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	# color->Name = reg_name(I->Idx, n_color, "violet")
	liste.append(1.0)
	liste.append(0.5)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1

	# /* greybow */
	for a in range(0,100): #grey00 -> grey99
		liste.append(a/99.0)
		liste.append(a/99.0)
		liste.append(a/99.0)
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1
	# color->Name = reg_name(I->Idx, n_color, "lightmagenta")
	liste.append(1.0)
	liste.append(0.2)
	liste.append(0.8)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	


	spectrumS=[[1.0, 0.0, 1.0], [0.5, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.5, 1.0], [0.0, 1.0, 1.0], [0.0, 1.0, 0.5], [0.0, 1.0, 0.0], [0.5, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.5, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.5], [1.0, 0.0, 1.0]]

	spectrumR= [[1.0, 1.0, 0.0], [0.5, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.5], [0.0, 1.0, 1.0], [0.0, 0.5, 1.0], [0.0, 0.0, 1.0], [0.5, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 0.5], [1.0, 0.0, 0.0], [1.0, 0.5, 0.0], [1.0, 1.0, 0.0]]

	spectrumC= [[1.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 1.0]]

	adiv=83.333333333
	

	for a in range(0,1000): #s000->s999
		set1= int(a/adiv)
		f=1.0- (a-(set1*adiv))/adiv
		liste.append(f * spectrumS[set1][0] + (1.0-f) * spectrumS[set1 + 1][0])
		liste.append(f * spectrumS[set1][1] + (1.0-f) * spectrumS[set1 + 1][1])
		liste.append(f * spectrumS[set1][2] + (1.0-f) * spectrumS[set1 + 1][2])
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1
		
	for a in range(0,1000): #r000->r999
		set1= int(a/adiv)
		f=1.0- (a-(set1*adiv))/adiv
		liste.append(f * spectrumR[set1][0] + (1.0-f) * spectrumR[set1 + 1][0])
		liste.append(f * spectrumR[set1][1] + (1.0-f) * spectrumR[set1 + 1][1])
		liste.append(f * spectrumR[set1][2] + (1.0-f) * spectrumR[set1 + 1][2])
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1

	for a in range(0,1000): #c000->c999
		set1= int(a/adiv)
		f=1.0- (a-(set1*adiv))/adiv
		liste.append(f * spectrumC[set1][0] + (1.0-f) * spectrumC[set1 + 1][0])
		liste.append(f * spectrumC[set1][1] + (1.0-f) * spectrumC[set1 + 1][1])
		liste.append(f * spectrumC[set1][2] + (1.0-f) * spectrumC[set1 + 1][2])
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1


	wdiv= 41.666666667

	spectrumW= [[1.0, 1.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0],[1.0, 0.0, 0.0], [1.0, 1.0, 1.0],[0.0, 1.0, 0.0], [1.0, 1.0, 1.0],[1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0],[1.0, 1.0, 0.0], [1.0, 1.0, 1.0],[0.0, 1.0, 0.0], [1.0, 1.0, 1.0],[0.0, 0.0, 1.0], [1.0, 1.0, 1.0],[1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0],[1.0, 0.0, 0.0], [1.0, 1.0, 1.0],[0.0, 1.0, 1.0]]

	for a in range(0,1000): #w000->w999
		set1= int(a/wdiv)
		f=1.0- (a-(set1*wdiv))/wdiv
		liste.append(f * spectrumW[set1][0] + (1.0-f) * spectrumW[set1 + 1][0])
		liste.append(f * spectrumW[set1][1] + (1.0-f) * spectrumW[set1 + 1][1])
		liste.append(f * spectrumW[set1][2] + (1.0-f) * spectrumW[set1 + 1][2])
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1

	# color->Name = reg_name(I->Idx, n_color, "density")
	liste.append(0.1)
	liste.append(0.1)
	liste.append(0.6)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	
	for a in range(0,100): #gray00 -> gray99  american
		liste.append(a/99.0)
		liste.append(a/99.0)
		liste.append(a/99.0)
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1
	
	bdiv= 35.7143

	spectrumO= [[1.0, 0.0, 1.0], [0.8, 0.0, 1.0], [0.5, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.2, 1.0], [0.0, 0.5, 1.0], [0.0, 0.8, 1.0], [0.0, 1.0, 1.0], [0.0, 1.0, 0.8], [0.0, 1.0, 0.5], [0.0, 1.0, 0.2],
    [0.0, 1.0, 0.0], [0.2, 1.0, 0.0], [0.5, 1.0, 0.0], [0.8, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.9, 0.0], [1.0, 0.75, 0.0], [1.0, 0.6, 0.0],[1.0, 0.5, 0.0], [1.0, 0.4, 0.0], [1.0, 0.3, 0.0], [1.0, 0.2, 0.0],
    [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.5], [1.0, 0.0, 0.8], [1.0, 0.0, 1.0]]

	for a in range(0,1000): #o000->o999
		set1= int(a/bdiv)
		f=1.0- (a-(set1*bdiv))/bdiv
		liste.append(f * spectrumO[set1][0] + (1.0-f) * spectrumO[set1 + 1][0])
		liste.append(f * spectrumO[set1][1] + (1.0-f) * spectrumO[set1 + 1][1])
		liste.append(f * spectrumO[set1][2] + (1.0-f) * spectrumO[set1 + 1][2])
		liste.append(1.0)
		dic[n_color]=liste
		liste=[]
		n_color+=1
		color+=1

	#color->Name = reg_name(I->Idx, n_color, "paleyellow")
	liste.append(1.0)
	liste.append(1.0)
	liste.append(0.5)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "aquamarine")
	liste.append(0.5)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "deepsalmon")
	liste.append(1.0)
	liste.append(0.5)
	liste.append(0.5)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "palegreen")
	liste.append(0.65)
	liste.append(0.9)
	liste.append(0.65)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "deepolive")
	liste.append(0.6)
	liste.append(0.6)
	liste.append(0.1)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "deeppurple")
	liste.append(0.6)
	liste.append(0.1)
	liste.append(0.6)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "deepteal")
	liste.append(0.1)
	liste.append(0.6)
	liste.append(0.6)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lightblue")
	liste.append(0.75)
	liste.append(0.75)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lightorange")
	liste.append(1.0)
	liste.append(0.8)
	liste.append(0.5)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "palecyan")
	liste.append(0.8)
	liste.append(1.0)
	liste.append(1.0)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lightteal")
	liste.append(0.4)
	liste.append(0.7)
	liste.append(0.7)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "splitpea")
	liste.append(0.52)
	liste.append(0.75)
	liste.append(0.00)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "raspberry")
	liste.append(0.70)
	liste.append(0.30)
	liste.append(0.40)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "sand")
	liste.append(0.72)
	liste.append(0.55)
	liste.append(0.30)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "smudge")
	liste.append(0.55)
	liste.append(0.70)
	liste.append(0.40)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "violetpurple")
	liste.append(0.55)
	liste.append(0.25)
	liste.append(0.60)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "dirtyviolet")
	liste.append(0.70)
	liste.append(0.50)
	liste.append(0.50)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "deepsalmon")
	liste.append(1.00)
	liste.append(0.42)
	liste.append(0.42)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	
	
	#color->Name = reg_name(I->Idx, n_color, "lightpink")
	liste.append(1.00)
	liste.append(0.75)
	liste.append(0.87)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "greencyan")
	liste.append(0.25)
	liste.append(1.00)
	liste.append(0.75)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "limon")
	liste.append(0.75)
	liste.append(1.00)
	liste.append(0.25)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "skyblue")
	liste.append(0.20)
	liste.append(0.50)
	liste.append(0.80)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "bluewhite")
	liste.append(0.85)
	liste.append(0.85)
	liste.append(1.00)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "warmpink")
	liste.append(0.85)
	liste.append(0.20)
	liste.append(0.50)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "darksalmon")
	liste.append(0.73)
	liste.append(0.55)
	liste.append(0.52)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "helium")
	liste.append(0.850980392)
	liste.append(1.000000000)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lithium")
	liste.append(0.800000000)
	liste.append(0.501960784)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "beryllium")
	liste.append(0.760784314)
	liste.append(1.000000000)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "boron")
	liste.append(1.000000000)
	liste.append(0.709803922)
	liste.append(0.709803922)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "luorine")
	liste.append(0.701960784)
	liste.append(1.000000000)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "neon")
	liste.append(0.701960784)
	liste.append(0.890196078)
	liste.append(0.960784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "sodium")
	liste.append(0.670588235)
	liste.append(0.360784314)
	liste.append(0.949019608)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "magnesium")
	liste.append(0.541176471)
	liste.append(1.000000000)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "aluminum")
	liste.append(0.749019608)
	liste.append(0.650980392)
	liste.append(0.650980392)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "silicon")
	liste.append(0.941176471)
	liste.append(0.784313725)
	liste.append(0.627450980)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "phosphorus")
	liste.append(1.000000000)
	liste.append(0.501960784)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "chlorine")
	liste.append(0.121568627)
	liste.append(0.941176471)
	liste.append(0.121568627)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "argon")
	liste.append(0.501960784)
	liste.append(0.819607843)
	liste.append(0.890196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "potassium")
	liste.append(0.560784314)
	liste.append(0.250980392)
	liste.append(0.831372549)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "calcium")
	liste.append(0.239215686)
	liste.append(1.000000000)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "scandium")
	liste.append(0.901960784)
	liste.append(0.901960784)
	liste.append(0.901960784)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "titanium")
	liste.append(0.749019608)
	liste.append(0.760784314)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "vanadium")
	liste.append(0.650980392)
	liste.append(0.650980392)
	liste.append(0.670588235)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "chromium")
	liste.append(0.541176471)
	liste.append(0.600000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "manganese")
	liste.append(0.611764706)
	liste.append(0.478431373)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "iron")
	liste.append(0.878431373)
	liste.append(0.400000000)
	liste.append(0.200000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "cobalt")
	liste.append(0.941176471)
	liste.append(0.564705882)
	liste.append(0.627450980)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "nickel")
	liste.append(0.313725490)
	liste.append(0.815686275)
	liste.append(0.313725490)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "copper")
	liste.append(0.784313725)
	liste.append(0.501960784)
	liste.append(0.200000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "zinc")
	liste.append(0.490196078)
	liste.append(0.501960784)
	liste.append(0.690196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "gallium")
	liste.append(0.760784314)
	liste.append(0.560784314)
	liste.append(0.560784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "germanium")
	liste.append(0.400000000)
	liste.append(0.560784314)
	liste.append(0.560784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "arsenic")
	liste.append(0.741176471)
	liste.append(0.501960784)
	liste.append(0.890196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "selenium")
	liste.append(1.000000000)
	liste.append(0.631372549)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "bromine")
	liste.append(0.650980392)
	liste.append(0.160784314)
	liste.append(0.160784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "krypton")
	liste.append(0.360784314)
	liste.append(0.721568627)
	liste.append(0.819607843)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "rubidium")
	liste.append(0.439215686)
	liste.append(0.180392157)
	liste.append(0.690196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "strontium")
	liste.append(0.000000000)
	liste.append(1.000000000)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "yttrium")
	liste.append(0.580392157)
	liste.append(1.000000000)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "zirconium")
	liste.append(0.580392157)
	liste.append(0.878431373)
	liste.append(0.878431373)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "niobium")
	liste.append(0.450980392)
	liste.append(0.760784314)
	liste.append(0.788235294)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "molybdenum")
	liste.append(0.329411765)
	liste.append(0.709803922)
	liste.append(0.709803922)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "technetium")
	liste.append(0.231372549)
	liste.append(0.619607843)
	liste.append(0.619607843)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "ruthenium")
	liste.append(0.141176471)
	liste.append(0.560784314)
	liste.append(0.560784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "rhodium")
	liste.append(0.039215686)
	liste.append(0.490196078)
	liste.append(0.549019608)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "palladium")
	liste.append(0.000000000)
	liste.append(0.411764706)
	liste.append(0.521568627)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "silver")
	liste.append(0.752941176)
	liste.append(0.752941176)
	liste.append(0.752941176)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "cadmium")
	liste.append(1.000000000)
	liste.append(0.850980392)
	liste.append(0.560784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "indium")
	liste.append(0.650980392)
	liste.append(0.458823529)
	liste.append(0.450980392)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "tin")
	liste.append(0.400000000)
	liste.append(0.501960784)
	liste.append(0.501960784)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "antimony")
	liste.append(0.619607843)
	liste.append(0.388235294)
	liste.append(0.709803922)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "tellurium")
	liste.append(0.831372549)
	liste.append(0.478431373)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "iodine")
	liste.append(0.580392157)
	liste.append(0.000000000)
	liste.append(0.580392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "xenon")
	liste.append(0.258823529)
	liste.append(0.619607843)
	liste.append(0.690196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "cesium")
	liste.append(0.341176471)
	liste.append(0.090196078)
	liste.append(0.560784314)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "barium")
	liste.append(0.000000000)
	liste.append(0.788235294)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lanthanum")
	liste.append(0.439215686)
	liste.append(0.831372549)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "cerium")
	liste.append(1.000000000)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "praseodymium")
	liste.append(0.850980392)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "neodymium")
	liste.append(0.780392157)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "promethium")
	liste.append(0.639215686)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "samarium")
	liste.append(0.560784314)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "europium")
	liste.append(0.380392157)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "gadolinium")
	liste.append(0.270588235)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "terbium")
	liste.append(0.188235294)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "dysprosium")
	liste.append(0.121568627)
	liste.append(1.000000000)
	liste.append(0.780392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "holmium")
	liste.append(0.000000000)
	liste.append(1.000000000)
	liste.append(0.611764706)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "erbium")
	liste.append(0.000000000)
	liste.append(0.901960784)
	liste.append(0.458823529)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "thulium")
	liste.append(0.000000000)
	liste.append(0.831372549)
	liste.append(0.321568627)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "ytterbium")
	liste.append(0.000000000)
	liste.append(0.749019608)
	liste.append(0.219607843)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lutetium")
	liste.append(0.000000000)
	liste.append(0.670588235)
	liste.append(0.141176471)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "hanium")
	liste.append(0.301960784)
	liste.append(0.760784314)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "tantalum")
	liste.append(0.301960784)
	liste.append(0.650980392)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "tungsten")
	liste.append(0.129411765)
	liste.append(0.580392157)
	liste.append(0.839215686)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "rhenium")
	liste.append(0.149019608)
	liste.append(0.490196078)
	liste.append(0.670588235)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "osmium")
	liste.append(0.149019608)
	liste.append(0.400000000)
	liste.append(0.588235294)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "iridium")
	liste.append(0.090196078)
	liste.append(0.329411765)
	liste.append(0.529411765)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "platinum")
	liste.append(0.815686275)
	liste.append(0.815686275)
	liste.append(0.878431373)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "gold")
	liste.append(1.000000000)
	liste.append(0.819607843)
	liste.append(0.137254902)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "mercury")
	liste.append(0.721568627)
	liste.append(0.721568627)
	liste.append(0.815686275)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "thallium")
	liste.append(0.650980392)
	liste.append(0.329411765)
	liste.append(0.301960784)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lead")
	liste.append(0.341176471)
	liste.append(0.349019608)
	liste.append(0.380392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "bismuth")
	liste.append(0.619607843)
	liste.append(0.309803922)
	liste.append(0.709803922)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "polonium")
	liste.append(0.670588235)
	liste.append(0.360784314)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "astatine")
	liste.append(0.458823529)
	liste.append(0.309803922)
	liste.append(0.270588235)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "radon")
	liste.append(0.258823529)
	liste.append(0.509803922)
	liste.append(0.588235294)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "rancium")
	liste.append(0.258823529)
	liste.append(0.000000000)
	liste.append(0.400000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "radium")
	liste.append(0.000000000)
	liste.append(0.490196078)
	liste.append(0.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "actinium")
	liste.append(0.439215686)
	liste.append(0.670588235)
	liste.append(0.980392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "thorium")
	liste.append(0.000000000)
	liste.append(0.729411765)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "protactinium")
	liste.append(0.000000000)
	liste.append(0.631372549)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "uranium")
	liste.append(0.000000000)
	liste.append(0.560784314)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "neptunium")
	liste.append(0.000000000)
	liste.append(0.501960784)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "plutonium")
	liste.append(0.000000000)
	liste.append(0.419607843)
	liste.append(1.000000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "americium")
	liste.append(0.329411765)
	liste.append(0.360784314)
	liste.append(0.949019608)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "curium")
	liste.append(0.470588235)
	liste.append(0.360784314)
	liste.append(0.890196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "berkelium")
	liste.append(0.541176471)
	liste.append(0.309803922)
	liste.append(0.890196078)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "caliornium")
	liste.append(0.631372549)
	liste.append(0.211764706)
	liste.append(0.831372549)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "einsteinium")
	liste.append(0.701960784)
	liste.append(0.121568627)
	liste.append(0.831372549)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "ermium")
	liste.append(0.701960784)
	liste.append(0.121568627)
	liste.append(0.729411765)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "mendelevium")
	liste.append(0.701960784)
	liste.append(0.050980392)
	liste.append(0.650980392)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "nobelium")
	liste.append(0.741176471)
	liste.append(0.050980392)
	liste.append(0.529411765)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lawrencium")
	liste.append(0.780392157)
	liste.append(0.000000000)
	liste.append(0.400000000)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "rutherordium")
	liste.append(0.800000000)
	liste.append(0.000000000)
	liste.append(0.349019608)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "dubnium")
	liste.append(0.819607843)
	liste.append(0.000000000)
	liste.append(0.309803922)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "seaborgium")
	liste.append(0.850980392)
	liste.append(0.000000000)
	liste.append(0.270588235)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "bohrium")
	liste.append(0.878431373)
	liste.append(0.000000000)
	liste.append(0.219607843)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "hassium")
	liste.append(0.901960784)
	liste.append(0.000000000)
	liste.append(0.180392157)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "meitnerium")
	liste.append(0.921568627)
	liste.append(0.000000000)
	liste.append(0.149019608)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "deuterium")
	liste.append(0.9)
	liste.append(0.9)
	liste.append(0.9)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "lonepair")
	liste.append(0.5)
	liste.append(0.5)
	liste.append(0.5)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	#color->Name = reg_name(I->Idx, n_color, "pseudoatom")
	liste.append(0.9)
	liste.append(0.9)
	liste.append(0.9)
	dic[n_color]=liste
	liste=[]
	n_color+=1	
	color+=1	

	return dic

pymolColors=dicColor()

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python",sys.argv[0],"pymolsession.pse")
		exit(-1)

	filepath=sys.argv[1]
	pymolToUnityMol(filepath)
