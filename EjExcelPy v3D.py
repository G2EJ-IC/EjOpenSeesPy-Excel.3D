#%% [code]
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 23:06:41 2021

@author: IC.EJGuerreroG
"""

#%% [code]

#Change plot backend to Qt. ONLY if you are using an Ipython console (e.g. Spyder)
#%matplotlib qt

#Change plot backend to 'Nbagg' if using in Jupyter notebook to get an interactive, inline plot.
#%matplotlib notebook

#import sys
#sys.path.append('C:/ProgramData/Anaconda3/Lib/site-packages/openseespywin')

#from openseespy.opensees import *

# ---import OpenSeesPy rendering module---
#import openseespy.postprocessing.Get_Rendering as opsplt
#import openseespyvis.Get_Rendering as opsplt
#import import vfo.vfo as vfo
import openseespyvis.Get_Rendering as opsplt
import openseespy.opensees as ops
#import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd


import math
#from math import asin, atan, sqrt
# from openseespy.postprocessing.Get_Rendering import *
#%% [code]

############################################
### Units and Constants  ###################
############################################

mt = 1;
kg = 1;
sec = 1;
#%% [code]
# Dependent units
mt2 = mt*mt
cm = mt/100
mm = mt/1000
#%% [code]
# Constants
g = 9.81*mt/(sec*sec);
pi = 4 * math.atan(1.0)

ops.wipe()

#Importar Libro de Excel
import os as os
print('\n\n' + os.getcwd())

rutaPWD= os.getcwd()
rutaPATH = '/'
nombreXLSX='EjemploPy v3D-001.xlsx'

excel_file = rutaPWD + rutaPATH + nombreXLSX

print('\n\n' + excel_file)
print('\n\nImportar Libro de Excel')

nodos = pd.read_excel(excel_file , sheet_name = 'pNodos').to_numpy()
print('\n\nnodos = ')
print(nodos)
#%% [code]
elementos = pd.read_excel(excel_file , sheet_name = 'pElementos').to_numpy()
print('\n\nelementos = ')
print(elementos)

print('\n\n1.0 Definicnion del modelo')
#   1.0 Definicnion del modelo
#model( 'Basic' , '-ndm' , ndm , '-ndf' , ndf = ndm * (ndm + 1) / 2 )
ops.model('Basic', '-ndm', 3, '-ndf', 6)

print('\n\n2.0 Coordenadas de los nodos')
#   2.0 Coordenadas de los nodos
#node( nodeTag , * crds , '-ndf' , ndf , '-mass' , * mass , '-disp' , * disp , '-vel' , * vel , '-accel' , * accel )

BeamCoordTransf = 'Linear'  # Linear, PDelta, Corotational
ColCoordTransf = 'PDelta'  # Linear, PDelta, Corotational

ColTransfTag=1
BeamTranfTag=2

massType = '-lMass'  # -lMass, -cMass
massX = 0.49
mass = 0.

#%% [code]
for i in range (len(nodos)):
    print('i = ', i)
    nodeTag = int(nodos[i,0])
    CoorX = float(nodos[i,1])
    CoorY = float(nodos[i,2])
    CoorZ = float(nodos[i,3])
    ops.node(nodeTag, CoorX, CoorY, CoorZ)
    ops.mass(nodeTag, massX, massX, 0.01, 1.0e-10, 1.0e-10, 1.0e-10)

#%% [code]      
ops.fixZ(0.0, 1, 1, 1, 1, 1, 1)
opsplt.plot_model('nodes')

#%% [code]     
print('\n\n4.0 Definición de los elementos')
#   4.0 Definición de los elementos
#ops.geomTransf( transfType , transfTag , * transfArgs )
#Columnas
ops.geomTransf(ColCoordTransf, ColTransfTag, 0, -1, 0)
#Vigas
ops.geomTransf(BeamCoordTransf, BeamTranfTag, 0, 0, 1)

#%% [code]
Area = (0.40*mt)*(0.40*mt)
E_mod = 4700*((28)**0.5)*1000
G_mod = 1000
Jxx = (1/12)*(0.40*mt)*((0.40*mt)**3)
Iy = (1/12)*(0.40*mt)*((0.40*mt)**3)
Iz = (1/12)*(0.40*mt)*((0.40*mt)**3)

for i in range (len(elementos)):
    print('i = ', i)
    eleTag = int(elementos[i,0])
    NudoI = int(elementos[i,1])
    NudoJ = int(elementos[i,2])
    if i <= 48:
        transfTag=ColTransfTag
    else:
        transfTag=BeamTranfTag
    # ops.element( 'elasticBeamColumn' , eleTag , * eleNodes , Area , E_mod , G_mod , Jxx , Iy , Iz , transfTag , <'- mass' , mass> , <'- cMass'> )
    eleNodes=[NudoI,NudoJ]
    ops.element('elasticBeamColumn', eleTag, * eleNodes, Area, E_mod, G_mod, Jxx, Iy, Iz, transfTag, '-mass', mass, massType)

opsplt.plot_model('nodes' , 'elements')
    
# calculate eigenvalues & print results
numEigen = 7
eigenValues = ops.eigen(numEigen)

###################################
#### Display the active model with node tags only
#opsplt.plot_model("nodes")

####  Display specific mode shape with scale factor of 300 using the active model
opsplt.plot_modeshape(5, 3)

###################################
# To save the analysis output for deformed shape, use createODB command before running the analysis
# The following command saves the model data, and output for gravity analysis and the first 3 modes 
# in a folder "3DFrame_ODB"

opsplt.createODB("3DFrame", "Gravity", Nmodes=3)

# Define Static Analysis
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(60, 1, 0, 0, 0, 0, 0)
ops.analysis('Static')

# Run Analysis
ops.analyze(10)

# IMPORTANT: Make sure to issue a wipe() command to close all the recorders. Not issuing a wipe() command
# ... can cause errors in the plot_deformedshape() command.

ops.wipe()

####################################
### Now plot mode shape 2 with scale factor of 300 and the deformed shape using the recorded output data

opsplt.plot_modeshape(2, 3, Model="3DFrame")
opsplt.plot_deformedshape(Model="3DFrame", LoadCase="Gravity")

#%% [code]