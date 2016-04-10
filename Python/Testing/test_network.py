# This script shows the output of a network with MC and GC
# From this folder, run it with the following command:
# cd ../../neuron && nrniv -python ../Python/Testing/test_network.py; cd ../Python/Testing

import sys
import os

#os.chdir("../../NEURON")
from neuron import h
os.chdir("../NeuroML2")

h.chdir('../NEURON')
sys.path.append('../NEURON')

import custom_params
custom_params.filename = 'fig7'

custom_params.customMitralCount = 1
custom_params.customGranulesPerMitralCount = 1

import params
import runsim

from common import *
import params
import util
import parrun
import weightsave
import net_mitral_centric as nmc
makeSynConns = False

nmc.build_net_round_robin(getmodel(), 'c10.dic')

model = getmodel()

h.tstop = 300
h.dt = 1/64.0

#GIDs
mc = 0
gc = 110821
syn = 703836162

clampM = h.IClamp(model.mitrals[mc].soma(0.5))
clampM.delay = 50
clampM.dur = 200
clampM.amp = 0.8

clampG = h.IClamp(model.granules[gc].soma(0.5))
clampG.delay = 50
clampG.dur = 200
clampG.amp = 0.05

g=h.Graph()
h.graphList[0].append(g)
g.size(0,h.tstop,-80,50)
g.addvar('mitral soma',   'v(0.5)',  1,0, sec = model.mitrals[mc].soma)
g.addvar('mitral secden', 'v(0.829)',2,0, sec = model.mitrals[mc].secden[8])

g2=h.Graph()
h.graphList[0].append(g2)
g2.size(0,h.tstop,-80,50)
g2.addvar('gran soma',       'v(0.5)',2,0, sec = model.granules[gc].soma)
g2.addvar('gran spine head', 'v(0.5)',5,0, sec = model.mgrss[syn].spine.head)



h.nrnmainmenu()


gc = model.granules[gc]

from neuronHelper import *
details(gc.soma)

h.run()
