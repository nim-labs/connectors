#!/bin/env python
#******************************************************************************
#
# Filename:    projectHook.py
# Version:     v5.0.11.210722
# Compatible:  Python 3.x
#
# Copyright (c) 2014-2021 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

debug=True

import os

# Hook called when the user loads a project in the application.
# project_name : Name of the loaded project -- String.
def project_changed(project_name):
    print("project_changed - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    os.environ['NIM_FLAME_PROJECT'] = str(project_name)
    if debug :
        print(project_name)
    print("project_changed - end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    pass


# Hook called when the user loads a project in the application.
# info [Dictionary] [Modifiable]
#    Information about project
#
#    Keys:
#
#    flameProjectName: [String]
#       Name of the flame project.
#
#    shotgunProjectName: [String] [Modifiable]
#       Name of the shotgun projet it is linked with.
#       Will be empty if there is no link yet.
#
def project_changed_dict(info):
    pass


# Hook called when application is fully initialized
# project_name: the project that was loaded -- String
def app_initialized(project_name):
    pass


# Hook called after a project has been saved
#
# project_name: the project that was saved -- String
# save_time    : time to save the project (in seconds) -- Float
# is_auto_save : true if save was automatically initiated,
#                false if user initiated -- Bool
def project_saved(project_name, save_time, is_auto_save):
    pass

