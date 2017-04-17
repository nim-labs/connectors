#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/nim_tools.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import os

#This part of the scripts checks the output path and if it doesn't exist it creates it for you
def CheckOutputPath():
    import nuke
    file = nuke.filename(nuke.thisNode())
    dir = os.path.dirname(file)
    osdir = nuke.callbacks.filenameFilter(dir)
    try:
        os.makedirs (osdir)
    except OSError:
        pass

def updateNimWriteNodes():
    import nuke
    writeNodes = nuke.allNodes('WriteNIM_JPG')
    writeNodes.extend(nuke.allNodes('WriteNIM_PNG'))
    writeNodes.extend(nuke.allNodes('WriteNIM_EXR'))
    writeNodes.extend(nuke.allNodes('WriteNIM_DPX'))
    writeNodes.extend(nuke.allNodes('WriteNIM_TIF'))
    writeNodes.extend(nuke.allNodes('WriteNIM_MOV'))
    
    # find autoFillWrite nodes
    for n in writeNodes:
        for k in n.knobs():
            print k
            if k == "nim_outputFileText":
                try:
                    n[k].setValue(n.knobs()['nimFilename'].value())
                except:
                    print("No NIM Write Nodes Found.")
