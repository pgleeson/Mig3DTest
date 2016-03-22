import copy
import neuroml

def splitSegmentAlongFraction(cell,parentName,parentGroup,fractionAlong,childName):

    child = [seg for seg in cell.morphology.segments if seg.name == childName][0]
    parent = [seg for seg in cell.morphology.segments if seg.name == parentName][0]

    newSegID = max([int(seg.id) for seg in cell.morphology.segments]) + 1

    parentA = copy.deepcopy(parent)

    parentB = copy.deepcopy(parent)
    parentB.id = newSegID
    parentB.parent.segments = parentA.id
    parentB.name = parentName + "_B"

    breakPoint = copy.deepcopy(parent.distal)

    breakPoint.x = parent.proximal.x + (parent.distal.x-parent.proximal.x) * fractionAlong
    breakPoint.y = parent.proximal.y + (parent.distal.y-parent.proximal.y) * fractionAlong
    breakPoint.z = parent.proximal.z + (parent.distal.z-parent.proximal.z) * fractionAlong

    parentA.distal = copy.deepcopy(breakPoint)
    parentB.proximal = copy.deepcopy(breakPoint)
    parentB.proximal.original_tagname_ = "proximal"

    i = 0
    for seg in cell.morphology.segments:
        if seg == parent:
            cell.morphology.segments[i] = parentA
            break
        i = i + 1

    cell.morphology.segments.append(parentB)

    [g for g in cell.morphology.segment_groups if g.id == parentGroup][0]\
        .members\
        .append(neuroml.Member(segments=newSegID))

    child.parent.segments = parent.id