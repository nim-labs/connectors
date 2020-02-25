#****************************************************************************
#
# Filename: Houdini/nimMenu.py
# Version:  2.5.0.161013
#
# Copyright (c) 2014-2020 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
#
# ****************************************************************************
import hou
import os,sys

action = sys.argv[1]

nimScriptPath = hou.expandString('$NIM_CONNECTOR_ROOT')
sys.path.append(nimScriptPath)
print "NIM Script Path: %s" % nimScriptPath


import nim_core.UI as nimUI
import nim_core.nim_api as nimAPI
import nim_core.nim_file as nimFile
import nim_core.nim_win as nimWin

reload(nimUI)
reload(nimAPI)
reload(nimFile)
reload(nimWin)

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

def changeUserAction():
    try:
        nimWin.userInfo()
    except Exception, e :
        print 'Sorry, there was a problem choosing NIM user...'
        print '    %s' % traceback.print_exc()
    print 'NIM: changeUserAction'


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

if action == 'user':
    changeUserAction()

if action == 'reload':
	reloadScriptsAction()