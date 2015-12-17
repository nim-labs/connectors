#****************************************************************************
#
# Filename: Houdini/nimMenu.py
# Version:  v1.0.3.151215
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#
# ****************************************************************************
import hou
import os,sys

'''
nimHoudiniScriptPath = os.path.dirname(os.path.realpath(__file__))
nimHoudiniScriptPath = nimHoudiniScriptPath.replace('\\','/')
nimScriptPath = nimHoudiniScriptPath.rstrip('/plugins/Houdini/scripts')
print "NIM Script Path: %s" % nimScriptPath
'''

action = sys.argv[1]
nimScriptPath = sys.argv[2]
print "NIM Script Path: %s" % nimScriptPath

#sys.path.append('[NIM_CONNECTOR_ROOT]')
#sys.path.append(nimScriptPath)

sys.path.append('I:/VAULT/modules/nim_dev')

import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile

reload(nimUI)
reload(nimAPI)
reload(nimFile)

def openFileAction():
    nimUI.mk('FILE')
    print 'NIM: openFileAction'

def importFileAction():
    nimUI.mk('LOAD', _import=True )
    print 'NIM: importFileAction'

def refereceFileAction():
    nimUI.mk('LOAD', ref=True)
    print 'NIM: refereceFileAction'

def saveFileAction():
    nimUI.mk('SAVE')
    print 'NIM: saveFileAction'

def saveSelectedAction():
    nimUI.mk( mode='SAVE', _export=True )
    print 'NIM: saveSelectedAction'

def versionUpAction():
    nimAPI.versionUp()
    print 'NIM: versionUpAction'

def publishAction():
    nimUI.mk('PUB')
    print 'NIM: publishAction'

def reloadScriptsAction():
    nimFile.scripts_reload()
    print 'NIM: reloadScriptsAction'


if action == 'open':
	openFileAction()

if action == 'import':
	importFileAction()

if action == 'ref':
	refereceFileAction()

if action == 'saveas':
	saveFileAction()

if action == 'savesel':
	saveSelectedAction()

if action == 'ver':
	versionUpAction()

if action == 'pub':
	publishAction()

if action == 'reload':
	reloadScriptsAction()