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

def logNimRender(writeNode=None):
    # Add to writeNIM node - afterRender: import nim_tools; nim_tools.logNimRender(nuke.thisNode())

    if writeNode is not None :
        print "Logging Render to NIM"
        import nuke
        import nim_core.nim_api as nimAPI
        
        shotID = nuke.root().knob('nim_shotID').getValue()
        #taskID = nuke.root().knob('nim_taskID').getValue()

        taskID = 15221
        elementTypeID = 1
        nimFolder = writeNode.knob('nimFolder').getValue()
        nimFileName = writeNode.knob('nimFilename').getValue()
        nimPath = writeNode.knob('nimPath').getValue()
        startFrame = writeNode.knob('first').getValue()
        endFrame = writeNode.knob('last').getValue()
        handles = 0
        isPublished = False
        
        '''
        result = nimAPI.add_render(taskID=taskID, renderName=nimFolder)
        if result['success'] == 'true':
            #nimAPI.upload_renderIcon(renderID=result['ID'],img='/path/to/icon.jpeg')

            nimAPI.add_element( parent='render', parentID=result['ID'], \
                                path=nimPath, name=nimFileName, \
                                startFrame=startFrame, endFrame=endFrame, \
                                handles=handles, isPublished=isPublished )
        else :
            print "Failed to add Render"
        '''
        
        nimAPI.add_element( parent='shot', parentID=shotID, \
                            path=nimPath, name=nimFileName, \
                            elementTypeID=elementTypeID, \
                            startFrame=startFrame, endFrame=endFrame, \
                            handles=handles, isPublished=isPublished )

    return