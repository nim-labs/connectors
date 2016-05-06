#!/usr/bin/env python
#******************************************************************************
#
# Filename: Nuke/menu.py
# Version:  2.0.0.160502
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

#################################################################################################
# NIM MENU

import nim_tools
nuke.addOnScriptSave(nim_tools.updateNimWriteNodes)

#  Make prefs:
import nim_core.nim_prefs as Prefs
Prefs.mk_default( notify_success=True )

try:
	isNuke = False
	if nuke.env['NukeVersionMajor'] > 6:
		if not nuke.env[ 'studio' ] and not nuke.env['hiero']:
			isNuke = True
	else:
		if not nuke.env[ 'studio' ]:
			isNuke = True
			
	if isNuke:
		m=nuke.menu('Nuke')
		nimRootMenu=m.addMenu("NIM")

		#  NIM Menu Structure:
		nimRootMenu.addCommand( 'Open', 'import nim_core.UI as UI; UI.mk("FILE")' )
		nimRootMenu.addCommand( 'Import', 'import nim_core.UI as UI; UI.mk("LOAD", _import=True)' )
		nimRootMenu.addSeparator()
		nimRootMenu.addCommand( 'Save As', 'import nim_core.UI as UI; UI.mk("SAVE")' )
		nimRootMenu.addCommand( 'Export Selected', 'import nim_core.UI as UI; UI.mk("SAVE", _export=True)' )
		nimRootMenu.addSeparator()
		nimRootMenu.addCommand( 'Version Up', 'import nim_core.nim_api as Api; Api.versionUp()' )
		nimRootMenu.addCommand( 'Publish', 'import nim_core.UI as UI; UI.mk("PUB")' )
		nimRootMenu.addSeparator()
		#

		# NIM Write Gizmos:
		nimWriteMenu=nimRootMenu.addMenu("NIM Write")
		nimWriteMenu.addCommand('JPG', lambda: nuke.createNode( 'WriteNIM_JPG' ) )
		nimWriteMenu.addCommand('PNG', lambda: nuke.createNode( 'WriteNIM_PNG' ) )
		nimWriteMenu.addCommand('EXR', lambda: nuke.createNode( 'WriteNIM_EXR' ) )
		nimWriteMenu.addCommand('DPX', lambda: nuke.createNode( 'WriteNIM_DPX' ) )
		nimWriteMenu.addCommand('TIF', lambda: nuke.createNode( 'WriteNIM_TIF' ) )
		nimWriteMenu.addCommand('MOV', lambda: nuke.createNode( 'WriteNIM_MOV' ) )

		nimRootMenu.addSeparator()
		nimSettingsMenu=nimRootMenu.addMenu("Settings")
		nimSettingsMenu.addCommand( 'Change User', 'import nim_core.UI as UI; UI.GUI().update_user()' )
		nimSettingsMenu.addCommand( 'Reload Scripts', 'import nim_core.nim_file as F; F.scripts_reload()' )
except:
	pass


# END
#################################################################################################