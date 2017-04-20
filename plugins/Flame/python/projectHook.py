#!/bin/env python
#******************************************************************************
#
# Filename: projectHook.py
#
# Copyright (c) 2014 Autodesk Inc.
# All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

# Hook called when the user loads a project in the application.
# projectName : Name of the loaded project -- String.
def projectChanged(projectName):
   pass


# Hook called when application is fully initialized
# projectName: the project that was loaded -- String
def appInitialized( projectName ):
   pass


# Hook called after a project has been saved
#
# projectName: the project that was saved -- String
# saveTime   : time to save the project (in seconds) -- Float
# isAutoSave : true if save was automatically initiated,
#              false if user initiated -- Bool
def projectSaved( projectName, saveTime, isAutoSave ):
   pass

