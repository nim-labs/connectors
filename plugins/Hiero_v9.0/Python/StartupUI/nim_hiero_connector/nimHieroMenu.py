#******************************************************************************
#
# Filename: Hiero/nim_hiero_connector/nimHieroMenu.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2014-2020 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

from hiero.core import *
import hiero.ui
from PySide.QtGui import *

import sys

import nim_core.nim_prefs as nimPrefs
import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile

# Grab Hiero's MenuBar 
M = hiero.ui.menuBar() 
# Add a Menu to the MenuBar 
nimMainMenu = M.addMenu('NIM') 

# Create a new QAction
nimOpenAction = QAction('Open',nimMainMenu)
nimImportAction = QAction('Import',nimMainMenu) 
nimSaveAsAction = QAction('Save As',nimMainMenu) 
nimExportSelectedAction = QAction('Export Selected',nimMainMenu) 
nimVersionUpAction = QAction('Version Up',nimMainMenu) 
nimPublishAction = QAction('Publish',nimMainMenu) 
nimReloadScriptsAction = QAction('Reload Scripts',nimMainMenu) 

def nimOpen(): nimUI.mk("FILE")
def nimImport(): nimUI.mk("LOAD", _import=True)
def nimSaveAs(): nimUI.mk("SAVE")
def nimExportSelected(): nimUI.mk("SAVE", _export=True)
def nimVersionUp(): nimAPI.versionUp()
def nimPublish(): nimUI.mk("PUB")
def nimReloadScripts(): nimFile.scripts_reload()

# Set the QAction to trigger the launchNuke method 
nimOpenAction.triggered.connect(nimOpen)
nimImportAction.triggered.connect(nimImport) 
nimSaveAsAction.triggered.connect(nimSaveAs) 
nimExportSelectedAction.triggered.connect(nimExportSelected)
nimVersionUpAction.triggered.connect(nimVersionUp) 
nimPublishAction.triggered.connect(nimPublish) 
nimReloadScriptsAction.triggered.connect(nimReloadScripts) 

# Add the Action to your Nuke Menu
nimMainMenu.insertAction(None, nimOpenAction)
nimMainMenu.insertAction(None, nimImportAction)
nimMainMenu.insertAction(None, nimSaveAsAction)
nimMainMenu.insertAction(None, nimExportSelectedAction)
nimMainMenu.insertAction(None, nimVersionUpAction)
nimMainMenu.insertAction(None, nimPublishAction)
nimMainMenu.insertAction(None, nimReloadScriptsAction)