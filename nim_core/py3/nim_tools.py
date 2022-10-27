#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_tools.py
# Version:  v5.3.0.221027
#
# Copyright (c) 2014-2022 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************
import os

qt_import=True
try : 
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore
except :
    try :
        from PySide import QtCore, QtGui
    except :
        try : 
            from PyQt4 import QtCore, QtGui
        except :
            try :
                from PyQt5 import QtWidgets as QtGui
                from PyQt5 import QtCore
            except :
                # print "NIM: Failed to load UI Modules - Tools"
                qt_import=False

from . import nim_print
from . import nim_win

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

def ui2py( uiFile='', pyFile='') :
    'Converts qt-Creator, ".ui" files, into python, ".py", files'
    
    try :
        import pysideuic
        if os.path.isfile( uiFile ) :
            pysideuic.compileUi( fileRead, pyFile, indent=0 )
    except :
        pass
    
    return


def get_comment( app='', num_requests=3 ) :
    'Gets a comment from the user'
    msgs=['Please enter a comment:                                    ']
    comment=''
    
    for i in range(0,num_requests) :
        #  Prompt user for comment, in Maya :
        if app=='Maya' :
            import maya.cmds as mc
            commentWin=mc.promptDialog( title='NIM - Input Comment', message=msgs[i], \
                button=['Ok'], defaultButton='Ok', dismissString='Ok' )
            if commentWin=='Ok' :
                comment=mc.promptDialog( query=True, text=True )
        #  Prompt user for comment, in Nuke :
        elif app=='Nuke' :
            import nuke
            comment=nuke.getInput( 'Enter Note :' )
        elif app=='C4D' :
            comment=nim_win.popup( title='NIM - Input Comment', msg=msgs[i], type='input' )
        elif app=='Hiero' :
            comment=nim_win.popup( app='Hiero', title='NIM - Input Comment', msg=msgs[i], type='input' )
        elif app=='3dsMax' :
            comment=nim_win.popup( title='NIM - Input Comment', msg=msgs[i], type='input' )
        elif app=='Houdini' :
            comment=nim_win.popup( title='NIM - Input Comment', msg=msgs[i], type='input' )
        elif app=='Flame' :
            comment=nim_win.popup( title='NIM - Input Comment', msg=msgs[i], type='input' )
        else :
            nim_print.info( 'Couldn\'t determine the application to prompt for a user comment.  :\'(' )
        #  Stop, once a comment has been input :
        if comment : break
    
    if not comment :
        nim_print.info( 'Consider entering a comment next time.' )
    
    return comment


def get_home() :
    'Gets the NIM home directory'
    userHome=os.path.expanduser( '~' )
    if userHome.endswith( 'Documents' ) :
        userHome=userHome[:-9]
    return os.path.normpath( os.path.join( userHome,'.nim' ) )

def mk_home() :
    'Creates the nim folder in the user\'s home directory'
    
    #  Get NIM home folder :
    nimHome=get_home()
    
    #  Make NIM home directory :
    if not os.path.exists( nimHome ) :
        os.makedirs( nimHome )
    
    subDirs=['scripts', 'imgs', 'css', 'apps']
    #  Make NIM subdirectories :
    for subDir in subDirs :
        mk_dir=os.path.normpath( os.path.join( nimHome, subDir ) )
        if not os.path.exists( mk_dir ) :
            os.makedirs( mk_dir )
    
    appDirs=['Maya', 'Nuke', 'C4D', '3dsMax', 'Houdini', 'Flame']
    #  Make Application subdirectories :
    for appDir in appDirs :
        mk_dir=os.path.normpath( os.path.join( nimHome, 'apps', appDir ) )
        if not os.path.exists( mk_dir ) :
            os.makedirs( mk_dir )
    
    return nimHome


if qt_import :
    class PopUp( QtGui.QDialog ) :
        
        def __init__( self, parent=None, title='', msg='', get_text=False, usr_input='' ) :
            'Creates a PySide pop-up notification window'
            super( PopUp, self ).__init__( parent )
            self.get_text=get_text
            
            #  Widgets :
            self.text=QtGui.QLabel( msg )
            if self.get_text :
                self.usr_input=QtGui.QLineEdit()
                self.usr_input.setMinimumWidth( 375 )
                self.usr_input.setText( usr_input )
            self.btn=QtGui.QPushButton( 'OK' )
            self.btn.setDefault( True )
            
            #  Layout :
            self.layout=QtGui.QVBoxLayout( self )
            #  Add to Layout :
            self.layout.addWidget( self.text )
            if get_text :
                self.layout.addWidget( self.usr_input )
            self.layout.addWidget( self.btn )
            
            #  Connections :
            self.btn.clicked.connect( self.close )
            
            #  Window :
            self.setWindowTitle( title )
            
            return
        
        def get_input( self ) :
            if self.get_text :
                return self.usr_input.text()



#  End

