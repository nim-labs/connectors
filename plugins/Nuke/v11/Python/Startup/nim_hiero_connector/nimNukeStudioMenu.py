#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/Python/Startup/nim_hiero_connector/nimNukeStudioMenu.py
# Version:  v2.6.80.170724
#
# Copyright (c) 2017 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

from hiero.core import *
import hiero.ui

from PySide2.QtWidgets import *
from PySide2.QtCore import *

import nuke

import sys,traceback

import nim_core.nim_prefs as nimPrefs
import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile
import nim_core.nim_print as P
import nim_nukeStudioUI as nimNS_UI

# Grab Hiero's MenuBar 
M = hiero.ui.menuBar() 
# Add a Menu to the MenuBar 
nimMainMenu = M.addMenu('NIM') 

# NIM Project Menu --------------------------------------------------------------------
if nuke.env[ 'studio' ]:
	nimProjectMenu = nimMainMenu.addMenu('Project')
else:
	nimProjectMenu = nimMainMenu

# Create a new QAction
nimProjectOpenAction = QAction('Open',nimProjectMenu)
#nimProjectImportAction = QAction('Import',nimProjectMenu) 
nimProjectSaveAsAction = QAction('Save As',nimProjectMenu) 
#nimProjectExportSelectedAction = QAction('Export Selected',nimProjectMenu) 
nimProjectVersionUpAction = QAction('Version Up',nimProjectMenu) 
#nimProjectPublishAction = QAction('Publish',nimProjectMenu) 

 

def nimProjectOpen(): nimNS_UI.openDialog()
#ef nimProjectImport(): nimUI.mk("LOAD", _import=True)
def nimProjectSaveAs(): nimNS_UI.saveDialog()
#def nimProjectExportSelected(): nimUI.mk("SAVE", _export=True)
def nimProjectVersionUp(): nimNS_UI.versionDialog()
#def nimProjectPublish(): nimUI.mk("PUB")



# Set the QAction to trigger the launchNuke method 
nimProjectOpenAction.triggered.connect(nimProjectOpen)
#nimProjectImportAction.triggered.connect(nimProjectImport) 
nimProjectSaveAsAction.triggered.connect(nimProjectSaveAs) 
#nimProjectExportSelectedAction.triggered.connect(nimProjectExportSelected)
nimProjectVersionUpAction.triggered.connect(nimProjectVersionUp) 
#nimProjectPublishAction.triggered.connect(nimProjectPublish) 



# Add the Action to your Nuke Menu
nimProjectMenu.insertAction(None, nimProjectOpenAction)
#nimProjectMenu.insertAction(None, nimProjectImportAction)
nimProjectMenu.insertAction(None, nimProjectSaveAsAction)
#nimProjectMenu.insertAction(None, nimProjectExportSelectedAction)
nimProjectMenu.insertAction(None, nimProjectVersionUpAction)
#nimProjectMenu.insertAction(None, nimProjectPublishAction)



# END NIM Project Menu ----------------------------------------------------------------



# NIM Comp Menu -----------------------------------------------------------------------
if nuke.env[ 'studio' ]:
	nimCompMenu = nimMainMenu.addMenu('Comp')

	# Create a new QAction
	nimCompOpenAction = QAction('Open',nimCompMenu)
	nimCompImportAction = QAction('Import',nimCompMenu) 
	nimCompSaveAsAction = QAction('Save As',nimCompMenu) 
	nimCompExportSelectedAction = QAction('Export Selected',nimCompMenu) 
	nimCompVersionUpAction = QAction('Version Up',nimCompMenu) 
	nimCompPublishAction = QAction('Publish',nimCompMenu)

	def nimCompOpen(): nimUI.mk("FILE")
	def nimCompImport(): nimUI.mk("LOAD", _import=True)
	def nimCompSaveAs(): nimUI.mk("SAVE")
	def nimCompExportSelected(): nimUI.mk("SAVE", _export=True)
	def nimCompVersionUp(): nimAPI.versionUp()
	def nimCompPublish(): nimUI.mk("PUB")

	# Set the QAction to trigger the launchNuke method 
	nimCompOpenAction.triggered.connect(nimCompOpen)
	nimCompImportAction.triggered.connect(nimCompImport) 
	nimCompSaveAsAction.triggered.connect(nimCompSaveAs) 
	nimCompExportSelectedAction.triggered.connect(nimCompExportSelected)
	nimCompVersionUpAction.triggered.connect(nimCompVersionUp) 
	nimCompPublishAction.triggered.connect(nimCompPublish) 

	# Add the Action to your Nuke Menu
	nimCompMenu.insertAction(None, nimCompOpenAction)
	nimCompMenu.insertAction(None, nimCompImportAction)
	nimCompMenu.insertAction(None, nimCompSaveAsAction)
	nimCompMenu.insertAction(None, nimCompExportSelectedAction)
	nimCompMenu.insertAction(None, nimCompVersionUpAction)
	nimCompMenu.insertAction(None, nimCompPublishAction)

	nimCompMenu.addSeparator()

	nimCompWriteMenu = nimCompMenu.addMenu('NIM Write')
	nimCreateWriteJPGAction = QAction('JPG', nimCompWriteMenu)
	nimCreateWritePNGAction = QAction('PNG', nimCompWriteMenu)
	nimCreateWriteEXRAction = QAction('EXR', nimCompWriteMenu)
	nimCreateWriteDPXAction = QAction('DPX', nimCompWriteMenu)
	nimCreateWriteTIFAction = QAction('TIF', nimCompWriteMenu)
	nimCreateWriteMOVAction = QAction('MOV', nimCompWriteMenu)

	#nimCompChangeUserAction = QAction('Change user',nimCompMenu) 
	#nimCompReloadScriptsAction = QAction('Reload Scripts',nimCompMenu) 

	def nimCreateWriteJPG(): nuke.createNode( 'WriteNIM_JPG' )
	def nimCreateWritePNG(): nuke.createNode( 'WriteNIM_PNG' )
	def nimCreateWriteEXR(): nuke.createNode( 'WriteNIM_EXR' )
	def nimCreateWriteDPX(): nuke.createNode( 'WriteNIM_DPX' )
	def nimCreateWriteTIF(): nuke.createNode( 'WriteNIM_TIF' )
	def nimCreateWriteMOV(): nuke.createNode( 'WriteNIM_MOV' )

	#def nimCompChangeUser(): nimUI.GUI().update_user()
	#def nimReloadCompScripts(): nimFile.scripts_reload()

	# Set the QAction to trigger the launchNuke method 
	nimCreateWriteJPGAction.triggered.connect(nimCreateWriteJPG) 
	nimCreateWritePNGAction.triggered.connect(nimCreateWritePNG) 
	nimCreateWriteEXRAction.triggered.connect(nimCreateWriteEXR) 
	nimCreateWriteDPXAction.triggered.connect(nimCreateWriteDPX) 
	nimCreateWriteTIFAction.triggered.connect(nimCreateWriteTIF) 
	nimCreateWriteMOVAction.triggered.connect(nimCreateWriteMOV) 

	#nimCompChangeUserAction.triggered.connect(nimCompChangeUser)
	#nimCompReloadScriptsAction.triggered.connect(nimReloadCompScripts) 

	# Add the Action to your Nuke Menu
	nimCompWriteMenu.insertAction(None, nimCreateWriteJPGAction)
	nimCompWriteMenu.insertAction(None, nimCreateWritePNGAction)
	nimCompWriteMenu.insertAction(None, nimCreateWriteEXRAction)
	nimCompWriteMenu.insertAction(None, nimCreateWriteDPXAction)
	nimCompWriteMenu.insertAction(None, nimCreateWriteTIFAction)
	nimCompWriteMenu.insertAction(None, nimCreateWriteMOVAction)

	#nimCompMenu.addSeparator()

	#nimCompMenu.insertAction(None, nimCompChangeUserAction)
	#nimCompMenu.insertAction(None, nimCompReloadScriptsAction)

# END NIM Comp Menu --------------------------------------------------------------------


# NIM Settings Menu --------------------------------------------------------------------
if nuke.env[ 'studio' ]:
	nimSettingsMenu = nimMainMenu.addMenu('NIM Settings')
else:
	nimSettingsMenu = nimMainMenu
	nimMainMenu.addSeparator()

nimProjectChangeUserAction = QAction('Change User',nimSettingsMenu)
nimProjectReloadScriptsAction = QAction('Reload Scripts',nimSettingsMenu)


def nimProjectChangeUser():
	try:
		nimUI.GUI().update_user()
	except Exception, e :
		print 'Sorry, there was a problem choosing NIM user...'
		print '    %s' % traceback.print_exc()
	return

def nimProjectReloadScripts():
	try:
		P.info('Reloading Scripts')
		import nim_core.nim_prefs as nimPrefs
		import nim_core.UI as nimUI
		import nim_core.nim_api as nimAPI
		import nim_core.nim_file as nimFile
		import nimHieroConnector as nimHC
		#import nimHieroExport as nimHExport
		import nim_nukeStudioUI as nimNS_UI
		import nimProcessorUI
		import nimShotProcessor
		reload(nimPrefs)
		reload(nimUI)
		reload(nimAPI)
		reload(nimFile)
		reload(nimHC)
		#reload(nimHExport)
		reload(nimNS_UI)
		reload(nimProcessorUI)
		reload(nimShotProcessor)
		
		if nuke.env[ 'studio' ]:
			nimFile.scripts_reload()

		P.info('Scripts Reloaded')
	except Exception, e :
		print 'Sorry, there was a problem reloading the NIM scripts...'
		print '    %s' % traceback.print_exc()
	return


nimProjectChangeUserAction.triggered.connect(nimProjectChangeUser) 
nimProjectReloadScriptsAction.triggered.connect(nimProjectReloadScripts)


nimSettingsMenu.insertAction(None, nimProjectChangeUserAction)
nimSettingsMenu.insertAction(None, nimProjectReloadScriptsAction)