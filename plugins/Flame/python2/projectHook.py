#!/bin/env python
#******************************************************************************
#
# Filename: projectHook.py
#
# *****************************************************************************

debug=True

import os

# Hook called when the user loads a project in the application.
# projectName : Name of the loaded project -- String.
def projectChanged(projectName):
   print "projectChanged - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
   os.environ['NIM_FLAME_PROJECT'] = str(projectName)
   if debug :
      print projectName
   print "projectChanged - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
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

