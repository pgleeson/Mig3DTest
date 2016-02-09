import os
import sys
from neuron import h
from pyneuroml import pynml

#import pydevd
#pydevd.settrace('10.211.55.3', port=4200, stdoutToServer=True, stderrToServer=True)

h.chdir('../NEURON')
sys.path.append('../NEURON')


def __main__():
    import customsim
    import modeldata

    MCs = 1
    GCsPerMC = 5

    networkTemplate = FileTemplate("../NeuroML2/Networks/NetworkTemplate.xml")
    includeTemplate = FileTemplate("../NeuroML2/Networks/IncludeTemplate.xml")
    populationTemplate = FileTemplate("../NeuroML2/Networks/PopulationTemplate.xml")
    projectionTemplate = FileTemplate("../NeuroML2/Networks/ProjectionTemplate.xml")

    customsim.setup(MCs, GCsPerMC)
    model = modeldata.getmodel()

    netFile = "../NeuroML2/Networks/Bulb_%iMC_%iGC.net.nml" % (len(model.mitral_gids), len(model.granule_gids))

    includes = ""
    populations = ""
    projections = ""

    mcNMLs = {}
    gcNMLs = {}

    # Make MC includes and populations
    for mcgid in model.mitral_gids:

        includes += includeTemplate.text\
            .replace("[CellType]", "Mitral")\
            .replace("[GID]", `mcgid`)

        populations += populationTemplate.text\
            .replace("[CellType]", "Mitral")\
            .replace("[GID]", `mcgid`)\
            .replace("[X]", `model.mitrals[mcgid].x`)\
            .replace("[Y]", `model.mitrals[mcgid].y`)\
            .replace("[Z]", `model.mitrals[mcgid].z`)

        # Retain mitral cell NML
        mcNML = pynml\
                .read_neuroml2_file("../NeuroML2/MitralCells/Exported/Mitral_0_%i.cell.nml" % mcgid)\
                .cells[0]
        
        mcNMLs.update({mcgid:mcNML})

    # Make GC includes and populations
    import granules
    from neuroml.nml.nml import NeuroMLDocument

    for gcgid in model.granule_gids:

        includes += includeTemplate.text\
            .replace("[CellType]", "Granule")\
            .replace("[GID]", `gcgid`)

        populations += populationTemplate.text\
            .replace("[CellType]", "Granule")\
            .replace("[GID]", `gcgid`)\
            .replace("[X]", `granules.gid2pos[gcgid][0]`)\
            .replace("[Y]", `granules.gid2pos[gcgid][1]`)\
            .replace("[Z]", `granules.gid2pos[gcgid][2]`)

        # Retain granule cell NML
        gcNML = pynml\
                .read_neuroml2_file("../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml" % gcgid)\

        gcNMLs.update({gcgid:gcNML})

    # Add a projection for each synapse
    synCount = len(model.mgrss.keys())
    curSyn = 0

    for sgid in model.mgrss.keys():

        print('Building synapse %i of %i' % (curSyn+1,synCount))

        synapse = model.mgrss[sgid]

        nsecden = model.mitrals[synapse.mgid].secden[synapse.isec].nseg
        secdenIndex = min(nsecden-1, int(synapse.xm * nsecden))
        postSegmentId = [seg.id\
                         for seg in mcNMLs[synapse.mgid].morphology.segments\
                         if seg.name == "Seg%i_secden_%i"%(secdenIndex,synapse.isec)\
                        ][0]

        gcNML = gcNMLs[synapse.ggid].cells[0]

        # Position the spine along the GC priden
        neck = [seg for seg in gcNML.morphology.segments if seg.name == 'Seg0_neck'][0]
        neck.parent.fraction_along = `synapse.xg`
        pynml.write_neuroml2_file(gcNMLs[synapse.ggid], "../NeuroML2/GranuleCells/Exported/Granule_0_%i.cell.nml" % synapse.ggid)

        # Add Dendro-dendritic synapses
        # GC -> MC part
        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`+'_G2M')\
            .replace("[PreCellType]", "Granule")\
            .replace("[PreGID]", `synapse.ggid`)\
            .replace("[PreSegment]", `4`)\
            .replace("[PreAlong]", `0.5`)\
            .replace("[PostCellType]", "Mitral")\
            .replace("[PostGID]", `synapse.mgid`)\
            .replace("[PostSegment]", `postSegmentId`)\
            .replace("[PostAlong]", "0.5")\
            .replace("[Synapse]", "FIsyn")\

        # MC -> GC part
        projections += projectionTemplate.text\
            .replace("[ProjectionID]", `sgid`+'_M2G')\
            .replace("[PreCellType]", "Mitral")\
            .replace("[PreGID]", `synapse.mgid`)\
            .replace("[PreSegment]", `postSegmentId`)\
            .replace("[PreAlong]", `0.5`)\
            .replace("[PostCellType]", "Granule")\
            .replace("[PostGID]", `synapse.ggid`)\
            .replace("[PostSegment]", `4`)\
            .replace("[PostAlong]", "0.5")\
            .replace("[Synapse]", "AmpaNmdaSyn")\

        curSyn += 1


    network = networkTemplate.text\
        .replace("[IncludesPlaceholder]", includes)\
        .replace("[PopulationsPlaceholder]", populations)\
        .replace("[ProjectionsPlaceholder]", projections)

    with open(netFile, "w") as file:
        file.write(network)

    print('Net file saved to: ' + netFile)

class FileTemplate():
    def __init__(self, path):
        self.path = path

        with open(self.path, "r") as file:
            self.text = file.read()


if __name__ == "__main__":
    __main__()
