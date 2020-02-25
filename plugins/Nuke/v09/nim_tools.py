#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/nim_tools.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2014-2020 NIM Labs LLC
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
