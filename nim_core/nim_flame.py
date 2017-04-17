#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_maya.py
# Version:  v2.6.0.170226
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import os, sys, traceback
import nim as Nim
import nim_file as F
import nim_print as P

#  Import Python GUI packages :
try : 
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore
except ImportError :
    try : 
        from PySide import QtCore, QtGui
    except ImportError :
        try : 
            from PyQt4 import QtCore, QtGui
        except ImportError : 
            print "NIM: Failed to load UI Modules - Flame"

#  Variables :
version='v2.6.0'
winTitle='NIM_'+version