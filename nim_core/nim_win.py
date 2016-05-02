#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_win.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  NIM Imports :
import nim_api as Api
import nim_file as F
import nim_prefs as Prefs
import nim_print as P
#  Import Python GUI packages :
try : from PySide import QtCore, QtGui
except :
    try : from PyQt4 import QtCore, QtGui
    except : pass


def popup( title='', msg='', type='ok', defaultInput='', pyside=False, _list=[], selNum=0, winPrnt=None ) :
    'Attempts to build a simple dialog window in either native application calls, or PySide'
    app=F.get_app()
    userInput=''
    
    #  Create PySide window :
    if pyside :
        try :
            from PySide import QtCore, QtGui
            if type=='comboBox' :
                userInput, ok=QtGui.QInputDialog.getItem( winPrnt, title, msg, _list, 0, False )
                if not ok :
                    userInput=None
        except :
            P.error( 'Sorry, problem loading PySide/PyQt4' )
    
    #  Maya Window :
    elif app=='Maya' :
        import maya.cmds as mc
        if type=='ok' :
            userInput=mc.confirmDialog( title=title, message=msg, button=['OK'], \
                defaultButton='OK' )
        elif type=='okCancel' :
            userInput=mc.confirmDialog( title=title, message=msg, button=['OK', 'Cancel'], \
                defaultButton='OK', cancelButton='Cancel', dismissString='Cancel' )
        elif type=='input' :
            userInput=mc.promptDialog( title=title, message=msg, text=defaultInput, \
                button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel' )
            if userInput=='OK' :
                userInput=str(mc.promptDialog( query=True, text=True ))
            else :
                userInput=''
    
    #  Nuke Window :
    elif app=='Nuke' :
        import nuke
        if type=='ok' :
            userInput=nuke.message( msg )
        elif type=='okCancel' :
            userInput=nuke.ask( msg )
            if userInput :
                userInput='OK'
            else :
                userInput='Cancel'
        elif type=='input' :
            userInput=nuke.getInput( msg, defaultInput )
    
    #  Hiero Window :
    elif app=='Hiero' :
        import hiero.ui
        from hiero.core import log
        from PySide import QtCore, QtGui
        if type=='ok' :
            dialog=QtGui.QMessageBox.information( hiero.ui.mainWindow(), title, msg, \
                QtGui.QMessageBox.Ok)
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
        elif type=='okCancel' :
            dialog=QtGui.QMessageBox.question( hiero.ui.mainWindow(), title, msg, \
                QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok )
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
            elif dialog==QtGui.QMessageBox.Cancel :
                userInput='Cancel'
        elif type=='input' :
            dialog=QtGui.QInputDialog.getText( QtGui.QInputDialog(), title, msg, \
                QtGui.QLineEdit.Normal )
            if dialog[1] :
                userInput=dialog[0]
            else :
                userInput=None
    
    #  C4D Window :
    elif app=='C4D' :
        import c4d
        from c4d import gui
        if type=='ok' :
            userInput=gui.MessageDialog( msg )
        elif type=='okCancel' :
            userInput=gui.QuestionDialog( text=msg )
            if userInput : userInput='OK'
        elif type=='input' :
            userInput=gui.InputDialog( msg )
    
    #  3dsMax :
    elif app=='3dsMax' :
        import MaxPlus
        from PySide import QtCore, QtGui
        #maxWin=MaxPlus.Win32_GetMAXHWnd()

        if type=='ok' :
            dialog=QtGui.QMessageBox.information( None, title, msg, \
                QtGui.QMessageBox.Ok)
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
        elif type=='okCancel' :
            dialog=QtGui.QMessageBox.question( None, title, msg, \
                QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok )
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
            elif dialog==QtGui.QMessageBox.Cancel :
                userInput='Cancel'
        elif type=='input' :
            dialog=QtGui.QInputDialog.getText( QtGui.QInputDialog(), title, msg, \
                QtGui.QLineEdit.Normal )
            if dialog[1] :
                userInput=dialog[0]
            else :
                userInput=None

    #  Houdini :
    elif app=='Houdini' :
        import hou
        from PySide import QtCore, QtGui

        if type=='ok' :
            dialog=QtGui.QMessageBox.information( None, title, msg, \
                QtGui.QMessageBox.Ok)
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
        elif type=='okCancel' :
            dialog=QtGui.QMessageBox.question( None, title, msg, \
                QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok )
            if dialog==QtGui.QMessageBox.Ok :
                userInput='OK'
            elif dialog==QtGui.QMessageBox.Cancel :
                userInput='Cancel'
        elif type=='input' :
            dialog=QtGui.QInputDialog.getText( QtGui.QInputDialog(), title, msg, \
                QtGui.QLineEdit.Normal )
            if dialog[1] :
                userInput=dialog[0]
            else :
                userInput=None

    #P.info('Returning PopUP INFO: %s' % userInput)
    return userInput


def userInfo( url='' ) :
    'Retrieves the User ID to use for the window'
    
    user, userID, userList='', '', []
    users=Api.get( sqlCmd={'q': 'getUsers'}, debug=False, nimURL=url )
    for u in users : userList.append( u['username'] )
    
    #  Create window to get user name from :
    user=popup( title='Select NIM User', msg='Pick a username to use', type='comboBox', \
        pyside=True, _list=userList )
    
    #  Get user ID :
    if url :
        userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False, nimURL=url )
    else :
        userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False )
    if type(userID)==type(list()) and len(userID)==1 :
        userID=userID[0]['ID']
    P.info( 'User set to "%s" (ID #%s)' % (user, userID) )
    
    #  Update Preferences :
    Prefs.update( attr='NIM_User', value=user )
    
    return (user, userID)


#  END

