#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_win.py
# Version:  v2.5.0.160930
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import os
#  NIM Imports :
import nim_api as Api
import nim_file as F
import nim_prefs as Prefs
import nim_print as P
#  Import Python GUI packages :
try : 
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore
except ImportError :
    try : from PySide import QtCore, QtGui
    except ImportError :
        try : from PyQt4 import QtCore, QtGui
        except ImportError : 
            print "Failed to load UI Modules: Win"



def popup( title='', msg='', type='ok', defaultInput='', pyside=False, _list=[], selNum=0, winPrnt=None ) :
    'Attempts to build a simple dialog window in either native application calls, or PySide'
    app=F.get_app()
    userInput=''
    
    #  Create PySide window :
    if pyside :
        try :
            try : 
                from PySide2 import QtWidgets as QtGui
                from PySide2 import QtCore
            except :
                from PySide import QtCore, QtGui
            if type=='comboBox' :
                userInput, ok=QtGui.QInputDialog.getItem( winPrnt, title, msg, _list, 0, False )
                if not ok :
                    userInput=None
        except :
            P.error( 'Sorry, problem loading PySide/PyQt4' )
            
    elif app == 'Cinesync':
        try:
            from PySide import QtCore, QtGui
            if type == 'input' or type == 'okCancel':
                userInput, ok = QtGui.QInputDialog.getText(winPrnt, title, msg, QtGui.QLineEdit.Normal, defaultInput)
                if not ok:
                    userInput = None

        except Exception as err:
            P.error('Error with dialog: %s' % str(err))
    
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


def userInfo( url='', apiUser='' ) :
    'Retrieves the User ID to use for the window'
    
    user, userID, userList='', '', []
    
    print("apiUser: %s" % apiUser)

    user=popup( title='Enter NIM Login', msg='Please enter your NIM username:', type='input', defaultInput=apiUser )

    if user is None :
        return False
    else :
        print("newUser: %s" % user)
        #  Get user ID :
        if url :
            userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False, nimURL=url )
        else :
            userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False )
        if type(userID)==type(list()) and len(userID)==1 :
            try :
                print userID
                userID=userID[0]['ID']
                P.info( 'User set to "%s" (ID #%s)' % (user, userID) )
                #  Update Preferences :
                Prefs.update( attr='NIM_User', value=user )
                popup( title='NIM User Set', msg='The NIM user has been set to %s.' % user)
                return (user, userID)
            except :
                return False
        else :
            P.error( 'Failed to find NIM user.' )
            response = popup( title='User Not Found', msg='The username entered is not a valid NIM user.\n\n Would you like to enter a new username?', type='okCancel')
            if(response=='OK'):
                userInfo( url=url )
            else :
                return False


def setApiKey( url='' ) :
    'Sets the NIM user API Key'
    print('setApiKey::')
    nim_apiKey = ''
    
    connect_info = Api.get_connect_info()
    api_url = connect_info['nim_apiURL']
    api_user = connect_info['nim_apiUser']

    api_key=popup( title='Enter NIM API Key', msg='Failed to validate user.\n\n \
                    NIM Security is set to require the use of API Keys.\n \
                    Please obtain a valid NIM API KEY from your NIM Administrator.\n\n \
                    Enter the NIM API Key for your user:', type='input', defaultInput='' )

    if api_key is None :
        return False
    else :
        #  Get user ID :
        if api_url :
            testAPI = Api.testAPI(nimURL=api_url, nim_apiUser=api_user, nim_apiKey=api_key)
            print testAPI
            print type(testAPI)
            if type(testAPI)==type(list()) :
                if testAPI[0]['error'] != '':
                    P.error( testAPI[0]['error'] )
                    response = popup( title='NIM API Invalid', msg='The NIM API Key entered is invalid.\n\nRe-enter API Key?', type='okCancel')
                    if(response=='OK'):
                        setApiKey( url=url )
                    else :
                        return False
                else :
                    #  Update NIM Key File :
                    print "Key Valid: %s" % testAPI[0]['key']
                    try :
                        keyFile = os.path.normpath( os.path.join( Prefs.get_home(), 'nim.key' ) )
                        print keyFile
                        with open(keyFile, 'r+') as f:
                            f.seek(0)
                            f.write(api_key)
                            f.truncate()
                        popup( title='NIM API Key Set', msg='The NIM API Key has been set.\n\nPlease retry your last command.')
                        return True
                    except :
                        P.error('Failed writing NIM Key file.')
                        P.error( '    %s' % traceback.print_exc() )
                        popup(title='Error', msg='Failed writing NIM Key File.')
                        return False
            else :
                P.error( 'Failed to validate NIM API.' )
                response = popup( title='NIM API Invalid', msg='The NIM API Key entered is invalid.\n\nRe-enter API Key?', type='okCancel')
                if(response=='OK'):
                    setApiKey( url=url )
                else :
                    return False
        else :
            return None
    


#  END

