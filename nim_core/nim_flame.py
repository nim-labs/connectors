#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_flame.py
# Version:  v4.0.51.200714
#
# Copyright (c) 2014-2020 NIM Labs LLC
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
version='v4.0.51'
winTitle='NIM_'+version


def set_vars( nim=None ) :
	'''Set NIM Variables'''
	P.info( '\nFlame - Setting Globals variables...' )

    #  User :
    userInfo=nim.userInfo()
    
  	# h_root.setUserData("nim_user", str(userInfo['name']) ) 
    os.environ['nim_user'] = str(userInfo['name'])

    # h_root.setUserData("nim_userID", str(userInfo['ID']) ) 
    os.environ['nim_userID'] = str(userInfo['ID'])

    # h_root.setUserData("nim_class", str(nim.tab()) ) 
    os.environ['nim_class'] = str(nim.tab())

    #h_root.setUserData("nim_server", str(nim.server()) ) 
    os.environ['nim_server'] = str(nim.server())

    # h_root.setUserData("nim_serverID", str(nim.ID('server')) ) 
    os.environ['nim_serverID'] = str(nim.ID('server'))

    # h_root.setUserData("nim_jobName", str(nim.name('job')) ) 
    os.environ['nim_jobName'] = str(nim.name('job'))

    # h_root.setUserData("nim_jobID", str(nim.ID('job')) ) 
    os.environ['nim_jobID'] = str(nim.ID('job'))

    # h_root.setUserData("nim_showName", str(nim.name('show')) ) 
    os.environ['nim_showName'] = str(nim.name('show'))

    # h_root.setUserData("nim_showID", str(nim.ID('show')) ) 
    os.environ['nim_showID'] = str(nim.ID('show'))

    # h_root.setUserData("nim_shot", str(nim.name('shot')) ) 
    os.environ['nim_shot'] = str(nim.name('shot'))

    # h_root.setUserData("nim_shotID", str(nim.ID('shot')) ) 
    os.environ['nim_shotID'] = str(nim.ID('shot'))

    # h_root.setUserData("nim_asset", str(nim.name('asset')) ) 
    os.environ['nim_asset'] = str(nim.name('asset'))

    # h_root.setUserData("nim_assetID", str(nim.ID('asset')) ) 
    os.environ['nim_assetID'] = str(nim.ID('asset'))

    # h_root.setUserData("nim_fileID", str(nim.ID('ver')) )
    os.environ['nim_fileID'] = str(nim.ID('ver'))

    if nim.tab()=='SHOT' :
        # h_root.setUserData("nim_name", str(nim.name('shot')))
        os.environ['nim_name'] = str(nim.name('shot'))
    elif # h_root.setUserData("nim_name", str(nim.name('asset')))
        os.environ['nim_name'] = str(nim.name('asset'))

    # h_root.setUserData("nim_basename", str(nim.name('base')) ) 
    os.environ['nim_basename'] = str(nim.name('base'))

    #h_root.setUserData("nim_type", str(nim.name( elem='task')) ) 
    os.environ['nim_type'] = str(nim.name( elem='task'))

    #h_root.setUserData("nim_typeID", str(nim.ID( elem='task' )) ) 
    os.environ['nim_typeID'] = str(nim.ID( elem='task' ))

    #h_root.setUserData("nim_typeFolder", str(nim.taskFolder()) ) 
    os.environ['nim_typeFolder'] = str(nim.taskFolder())

    #h_root.setUserData("nim_tag", str(nim.name('tag')) ) 
    os.environ['nim_tag'] = str(nim.name('tag'))

    #h_root.setUserData("nim_fileType", str(nim.fileType()) ) 
    os.environ['nim_fileType'] = str(nim.fileType())


	return

def get_vars( nim=None ) :
	'''Get NIM Variables'''
	#  User :
	'''
    if mc.objExists( 'defaultRenderGlobals.nim_user' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_user' )
        P.debug( 'User = %s' % value )
        nim.set_user( userName=value )
    '''
    #  User :
    if os.environ.get('nim_user', '-1') != -1 :
        value=os.environ.get('nim_user', '-1')
        P.debug( 'User = %s' % value )
        nim.set_user( userName=value )

    '''
    #  User ID :
    if mc.objExists( 'defaultRenderGlobals.nim_userID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_userID' )
        P.debug( 'User ID = %s' % value )
        nim.set_userID( userID=value )
    '''
    #  User ID :
    if os.environ.get('nim_userID', '-1') != -1 :
        value=os.environ.get('nim_userID', '-1')
        P.debug( 'User = %s' % value )
        nim.set_userID( userName=value )



    #  Tab/Class :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_class' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_class' )
        P.debug( 'Tab = %s' % value )
        nim.set_tab( value )
    '''
    if os.environ.get('nim_class', '-1') != -1 :
        value=os.environ.get('nim_class', '-1')
        P.debug( 'Tab = %s' % value )
        nim.set_tab( value )


    #  Server :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_server' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_server' )
        P.debug( 'Server = %s' % value )
        nim.set_server( path=value )
    '''
    if os.environ.get('nim_server', '-1') != -1 :
        value=os.environ.get('nim_server', '-1')
        P.debug( 'Server = %s' % value )
        nim.set_server( path=value )



    #  Server ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_serverID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_serverID' )
        P.debug( 'Server ID = %s' % value )
        nim.set_ID( elem='server', ID=value )
    '''
    if os.environ.get('nim_serverID', '-1') != -1 :
        value=os.environ.get('nim_serverID', '-1')
        P.debug( 'Server ID = %s' % value )
        nim.set_ID( elem='server', ID=value )




    #  Job :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_jobName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobName' )
        P.debug( 'Job = %s' % value )
        nim.set_name( elem='job', name=value )
    '''
    if os.environ.get('nim_jobName', '-1') != -1 :
        value=os.environ.get('nim_jobName', '-1')
        P.debug( 'Job = %s' % value )
        nim.set_name( elem='job', name=value )



    #  Job ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_jobID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobID' )
        P.debug( 'Job ID = %s' % value )
        nim.set_ID( elem='job', ID=value )
    '''
    if os.environ.get('nim_jobID', '-1') != -1 :
        value=os.environ.get('nim_jobID', '-1')
        P.debug( 'Job ID = %s' % value )
        nim.set_ID( elem='job', ID=value )



    #  Show :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_showName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showName' )
        P.debug( 'Show = %s' % value )
        nim.set_name( elem='show', name=value )
    '''
    if os.environ.get('nim_showName', '-1') != -1 :
        value=os.environ.get('nim_showName', '-1')
        P.debug( 'Show = %s' % value )
        nim.set_name( elem='show', name=value )


    #  Show ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_showID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showID' )
        P.debug( 'Show ID = %s' % value )
        nim.set_ID( elem='show', ID=value )
    '''
    if os.environ.get('nim_showID', '-1') != -1 :
        value=os.environ.get('nim_showID', '-1')
        P.debug( 'Show ID = %s' % value )
        nim.set_ID( elem='show', ID=value )


    #  Shot :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_shot' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shot' )
        P.debug( 'Shot = %s' % value )
        nim.set_name( elem='shot', name=value )
    '''
    if os.environ.get('nim_shot', '-1') != -1 :
        value=os.environ.get('nim_shot', '-1')
        P.debug( 'Shot = %s' % value )
        nim.set_name( elem='shot', name=value )


    #  Shot ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_shotID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shotID' )
        P.debug( 'Shot ID = %s' % value )
        nim.set_ID( elem='shot', ID=value )
    '''
    if os.environ.get('nim_shotID', '-1') != -1 :
        value=os.environ.get('nim_shotID', '-1')
        P.debug( 'Shot ID = %s' % value )
        nim.set_ID( elem='shot', ID=value )

    #  Asset :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_asset' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_asset' )
        P.debug( 'Asset = %s' % value )
        nim.set_name( elem='asset', name=value )
    '''
    if os.environ.get('nim_asset', '-1') != -1 :
        value=os.environ.get('nim_asset', '-1')
        P.debug( 'Asset = %s' % value )
        nim.set_name( elem='asset', name=value )

    #  Asset ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_assetID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_assetID' )
        P.debug( 'Asset ID = %s' % value )
        nim.set_ID( elem='asset', ID=value )
    '''
    if os.environ.get('nim_assetID', '-1') != -1 :
        value=os.environ.get('nim_assetID', '-1')
        P.debug( 'Asset ID = %s' % value )
        nim.set_ID( elem='asset', ID=value )


    #  Shot/Asset Name :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_name' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_name' )
        #  Determine what the tab is set to :
        if nim.tab()=='SHOT' :
            P.debug( 'Shot Name = %s' % value )
            #  No corresponding NIM attribute :
            #nim.set_tab( value )
        elif nim.tab()=='ASSET' :
            P.debug( 'Asset Name = %s' % value )
            #  No corresponding NIM attribute :
            #nim.set_tab( value )
    '''

    if os.environ.get('nim_name', '-1') != -1 :
        value=os.environ.get('nim_name', '-1')
        #  Determine what the tab is set to :
        if nim.tab()=='SHOT' :
            P.debug( 'Shot Name = %s' % value )
            #  No corresponding NIM attribute :
            #nim.set_tab( value )
        elif nim.tab()=='ASSET' :
            P.debug( 'Asset Name = %s' % value )
            #  No corresponding NIM attribute :
            #nim.set_tab( value )




    #  Basename :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_basename' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_basename' )
        P.debug( 'Basename = %s' % value )
        nim.set_name( elem='base', name=value )
    '''
    if os.environ.get('nim_basename', '-1') != -1 :
        value=os.environ.get('nim_basename', '-1')
        P.debug( 'Basename = %s' % value )
        nim.set_name( elem='base', name=value )

    #  Task :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_type' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_type' )
        P.debug( 'Task = %s' % value )
        nim.set_name( elem='task', name=value )
    '''
    if os.environ.get('nim_type', '-1') != -1 :
        value=os.environ.get('nim_type', '-1')
        P.debug( 'Task = %s' % value )
        nim.set_name( elem='task', name=value )

    #  Task ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_typeID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeID' )
        P.debug( 'Task ID = %s' % value )
        nim.set_ID( elem='task', ID=value )
    '''
    if os.environ.get('nim_typeID', '-1') != -1 :
        value=os.environ.get('nim_typeID', '-1')
        P.debug( 'Task ID = %s' % value )
        nim.set_ID( elem='task', ID=value )

    #  Task Folder :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_typeFolder' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeFolder' )
        P.debug( 'Task Folder = %s' % value )
        nim.set_taskFolder( folder=value )
    '''
    if os.environ.get('nim_typeFolder', '-1') != -1 :
        value=os.environ.get('nim_typeFolder', '-1')
        P.debug( 'Task Folder = %s' % value )
        nim.set_taskFolder( folder=value )


    #  Tag :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_tag' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_tag' )
        P.debug( 'Tag = %s' % value )
        nim.set_name( elem='tag', name=value )
    '''
    if os.environ.get('nim_tag', '-1') != -1 :
        value=os.environ.get('nim_tag', '-1')
        P.debug( 'Tag = %s' % value )
        nim.set_name( elem='tag', name=value )


    #  File Type :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_fileType' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_fileType' )
        P.debug( 'File Type = %s' % value )
        nim.set_name( elem='file', name=value )
    '''
    if os.environ.get('nim_fileType', '-1') != -1 :
        value=os.environ.get('nim_fileType', '-1')
        P.debug( 'File Type = %s' % value )
        nim.set_name( elem='file', name=value )
    
    #  Print dictionary :
    #P.info('\nNIM Dictionary from get vars...')
    #nim.Print()
    
    return