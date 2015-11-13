#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_3dsmax.py
# Version:  v1.0.3.151112
#
# Copyright (c) 2015 NIM Labs LLC
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
#  3dsMax Imports :
import MaxPlus
#  Import Python GUI packages :
try : from PySide import QtCore, QtGui
except :
    try : from PyQt4 import QtCore, QtGui
    except : pass

#  Variables :
version='v1.0.3'
winTitle='NIM_'+version

def get_mainWin() :
    'Returns the name of the main 3dsMax window'
    import MaxPlus
    maxWin=MaxPlus.Win32_GetMAXHWnd()
    return maxWin

def set_vars( nim=None ) :
    'Add variables to Maya Render Globals'
    
    P.info( '\n3dsMax - Setting Render Globals variables...' )
    '''
    #  User :
    userInfo=nim.userInfo()
    if not mc.attributeQuery( 'nim_user', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_user', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_user', userInfo['name'], type='string' )
    #  User ID :
    if not mc.attributeQuery( 'nim_userID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_userID', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_userID', userInfo['ID'], type='string' )
    #  Tab/Class :
    if not mc.attributeQuery( 'nim_class', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_class', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_class', nim.tab(), type='string' )
    #  Server :
    if not mc.attributeQuery( 'nim_server', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_server', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_server', nim.server(), type='string' )
    #  Server ID :
    if not mc.attributeQuery( 'nim_serverID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_serverID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_serverID', str(nim.ID('server')), type='string' )
    #  Job :
    if not mc.attributeQuery( 'nim_jobName', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_jobName', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_jobName', nim.name('job'), type='string' )
    #  Job ID :
    if not mc.attributeQuery( 'nim_jobID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_jobID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_jobID', str(nim.ID('job')), type='string' )
    #  Show :
    if not mc.attributeQuery( 'nim_showName', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_showName', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_showName', nim.name('show'), type='string' )
    #  Show ID :
    if nim.tab()=='SHOT' :
        if not mc.attributeQuery( 'nim_showID', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_showID', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_showID', str(nim.ID('show')), type='string' )
    #  Shot :
    if not mc.attributeQuery( 'nim_shot', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_shot', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_shot', str(nim.name('shot')), type='string' )
    #  Shot ID :
    if not mc.attributeQuery( 'nim_shotID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_shotID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_shotID', str(nim.ID('shot')), type='string' )
    #  Asset :
    if nim.tab()=='ASSET' :
        if not mc.attributeQuery( 'nim_asset', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_asset', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_asset', str(nim.name('asset')), type='string' )
    #  Asset ID :
    if nim.tab()=='ASSET' :
        if not mc.attributeQuery( 'nim_assetID', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_assetID', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_assetID', str(nim.ID('asset')), type='string' )
    #  File ID :
    if not mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_fileID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_fileID', str(nim.ID('ver')), type='string' )
    #  Shot/Asset Name :
    if not mc.attributeQuery( 'nim_name', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_name', dt="string")
    if nim.tab()=='SHOT' :
        mc.setAttr( 'defaultRenderGlobals.nim_name', nim.name('shot'), type='string' )
    elif nim.tab()=='ASSET' :
        mc.setAttr( 'defaultRenderGlobals.nim_name', nim.name('asset'), type='string' )
    #  Basename :
    if not mc.attributeQuery( 'nim_basename', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_basename', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_basename', nim.name('base'), type='string' )
    #  Task :
    if not mc.attributeQuery( 'nim_type', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_type', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_type', nim.name( elem='task' ), type='string' )
    #  Task ID :
    if not mc.attributeQuery( 'nim_typeID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_typeID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_typeID', str(nim.ID( elem='task' )), type='string' )
    #  Task Folder :
    if not mc.attributeQuery( 'nim_typeFolder', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_typeFolder', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_typeFolder', str(nim.taskFolder()), type='string' )
    #  Tag :
    if not mc.attributeQuery( 'nim_tag', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_tag', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_tag', nim.name('tag'), type='string' )
    #  File Type :
    if not mc.attributeQuery( 'nim_fileType', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_fileType', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_fileType', nim.fileType(), type='string' )
    
    P.info('    Completed setting NIM attributes on the defaultRenderGlobals node.')
    #nim.Print()
    
    return
    '''

def get_vars( nim=None ) :
    'Gets NIM settings from the defaultRenderGlobals node in Maya.'
    P.info('3dsMax Getting information from NIM attributes on the defaultRenderGlobals node...')
    '''
    #  User :
    if mc.objExists( 'defaultRenderGlobals.nim_user' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_user' )
        P.debug( 'User = %s' % value )
        nim.set_user( userName=value )
    #  User ID :
    if mc.objExists( 'defaultRenderGlobals.nim_userID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_userID' )
        P.debug( 'User ID = %s' % value )
        nim.set_userID( userID=value )
    #  Tab/Class :
    if mc.objExists( 'defaultRenderGlobals.nim_class' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_class' )
        P.debug( 'Tab = %s' % value )
        nim.set_tab( value )
    #  Server :
    if mc.objExists( 'defaultRenderGlobals.nim_server' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_server' )
        P.debug( 'Server = %s' % value )
        nim.set_server( path=value )
    #  Server ID :
    if mc.objExists( 'defaultRenderGlobals.nim_serverID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_serverID' )
        P.debug( 'Server ID = %s' % value )
        nim.set_ID( elem='server', ID=value )
    #  Job :
    if mc.objExists( 'defaultRenderGlobals.nim_jobName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobName' )
        P.debug( 'Job = %s' % value )
        nim.set_name( elem='job', name=value )
    #  Job ID :
    if mc.objExists( 'defaultRenderGlobals.nim_jobID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobID' )
        P.debug( 'Job ID = %s' % value )
        nim.set_ID( elem='job', ID=value )
    #  Show :
    if mc.objExists( 'defaultRenderGlobals.nim_showName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showName' )
        P.debug( 'Show = %s' % value )
        nim.set_name( elem='show', name=value )
    #  Show ID :
    if mc.objExists( 'defaultRenderGlobals.nim_showID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showID' )
        P.debug( 'Show ID = %s' % value )
        nim.set_ID( elem='show', ID=value )
    #  Shot :
    if mc.objExists( 'defaultRenderGlobals.nim_shot' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shot' )
        P.debug( 'Shot = %s' % value )
        nim.set_name( elem='shot', name=value )
    #  Shot ID :
    if mc.objExists( 'defaultRenderGlobals.nim_shotID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shotID' )
        P.debug( 'Shot ID = %s' % value )
        nim.set_ID( elem='shot', ID=value )
    #  Asset :
    if mc.objExists( 'defaultRenderGlobals.nim_asset' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_asset' )
        P.debug( 'Asset = %s' % value )
        nim.set_name( elem='asset', name=value )
    #  Asset ID :
    if mc.objExists( 'defaultRenderGlobals.nim_assetID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_assetID' )
        P.debug( 'Asset ID = %s' % value )
        nim.set_ID( elem='asset', ID=value )
    #  File ID :
    '''
    '''
    if mc.attributeQuery( 'defaultRenderGlobals.nim_fileID' ) :
        value=mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals' )
        P.debug( 'Class = %s' % value )
        nim.set_tab( tab=value )
    '''
    '''
    #  Shot/Asset Name :
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
    #  Basename :
    if mc.objExists( 'defaultRenderGlobals.nim_basename' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_basename' )
        P.debug( 'Basename = %s' % value )
        nim.set_name( elem='base', name=value )
    #  Task :
    if mc.objExists( 'defaultRenderGlobals.nim_type' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_type' )
        P.debug( 'Task = %s' % value )
        nim.set_name( elem='task', name=value )
    #  Task ID :
    if mc.objExists( 'defaultRenderGlobals.nim_typeID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeID' )
        P.debug( 'Task ID = %s' % value )
        nim.set_ID( elem='task', ID=value )
    #  Task Folder :
    if mc.objExists( 'defaultRenderGlobals.nim_typeFolder' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeFolder' )
        P.debug( 'Task Folder = %s' % value )
        nim.set_taskFolder( folder=value )
    #  Tag :
    if mc.objExists( 'defaultRenderGlobals.nim_tag' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_tag' )
        P.debug( 'Tag = %s' % value )
        nim.set_name( elem='tag', name=value )
    #  File Type :
    if mc.objExists( 'defaultRenderGlobals.nim_fileType' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_fileType' )
        P.debug( 'File Type = %s' % value )
        nim.set_name( elem='file', name=value )
    
    #  Print dictionary :
    #P.info('\nNIM Dictionary from get vars...')
    #nim.Print()
    
    return
    '''

def mk_workspace( proj_folder='', renPath='' ) :
    'Creates the NIM Project Workspace'

    proj_folder = ''

    workspace='\n'
    workspace='[Directories]\n'
    workspace +='Animations=./sceneassets/animations\n'
    workspace +='Archives=./archives\n'
    workspace +='AutoBackup=./autoback\n'
    workspace +='BitmapProxies=./proxies\n'
    workspace +='Downloads=./downloads\n'
    workspace +='Export=./export\n'
    workspace +='Expressions=./express\n'
    workspace +='Images=./sceneassets/images\n'
    workspace +='Import=./import\n'
    workspace +='Materials=./materiallibraries\n'
    workspace +='MaxStart=./scenes\n'
    workspace +='Photometric=./sceneassets\photometric\n'
    workspace +='Previews=./previews\n'

    workspace +='ProjectFolder='+proj_folder+'\n'

    workspace +='RenderAssets=./sceneassets/renderassets\n'
    
    #  Add render images directory :
    if not renPath :
        workspace +='RenderOutput=./renderoutput\n'
    else :
        renPath=renPath.replace('\\', '/')
        workspace +='RenderOutput='+renPath+'\n'

    workspace +='RenderPresets=./renderpresets\n'
   
    workspace +='Scenes=./scenes\n'
    workspace +='Sounds=./sceneassets/sound\n'
    workspace +='VideoPost=./vpost\n'
    workspace +='[XReferenceDirs]\n'
    workspace +='Dir1=./scenes\n'

    #TODO: UPDATE WITH ACTIVE BITMAP DIRS
    workspace +='[BitmapDirs]\n'
    workspace +='Dir1=C:/Program Files/Autodesk/3ds Max 2016/Maps\n'
    workspace +='Dir2=C:/Program Files/Autodesk/3ds Max 2016/Maps/glare\n'
    workspace +='Dir3=C:/Program Files/Autodesk/3ds Max 2016/Maps/adskMtl\n'
    workspace +='Dir4=C:/Program Files/Autodesk/3ds Max 2016/Maps/Noise\n'
    workspace +='Dir5=C:/Program Files/Autodesk/3ds Max 2016/Maps/Substance\noises\n'
    workspace +='Dir6=C:/Program Files/Autodesk/3ds Max 2016/Maps/Substance\textures\n'
    workspace +='Dir7=C:/Program Files/Autodesk/3ds Max 2016/Maps/mental_mill\n'
    workspace +='Dir8=C:/Program Files/Autodesk/3ds Max 2016/Maps/fx\n'
    workspace +='Dir9=C:/Program Files/Autodesk/3ds Max 2016/Maps/Particle Flow Presets\n'
    workspace +='Dir10=./downloads\n'

    return workspace
    

def mk_proj( path='', renPath='' ) :
    'Creates a show project structure'
    import MaxPlus
    workspaceExists=False
    
    #  Variables :
    projDirs=['sceneassets/animations', 'archives', 'autoback', 'proxies', 'downloads',
        'export', 'express', 'sceneassets/images', 'import', 'materiallibraries', 'scenes',
        'sceneassets\photometric', 'previews', 'sceneassets/renderassets', 'renderoutput', 'renderpresets',
        'sceneassets/sound', 'vpost' ]
    
    projectName = os.path.basename(os.path.normpath(path))
    P.info('Project Folder: %s' % projectName)

    #  Create 3dsMax project directories :
    if os.path.isdir( path ) :
        for projDir in projDirs:
            _dir=os.path.normpath( os.path.join( path, projDir ) )
            if not os.path.isdir( _dir ) :
                try : os.mkdir( _dir )
                except Exception, e :
                    P.error( 'Failed creating the directory: %s' % _dir )
                    P.error( '    %s' % traceback.print_exc() )
                    return False
    
    #  Check for workspace file :
    projectConfigFileName = projectName+'.mxp'
    workspaceFile=os.path.normpath( os.path.join( path, projectConfigFileName ) )
    if os.path.exists( workspaceFile ) :
        workspaceExists=True
    
    #  Create workspace file :
    if not workspaceExists :
        P.info('Creating 3dsMax path configuration file...')
        workspace_text=mk_workspace( projectName, renPath )
        workspace_file=open( workspaceFile, 'w' )
        workspace_file.write( workspace_text )
        workspace_file.close
    
        #  Write out the render path :
        if renPath and os.path.isdir( renPath ) :
            try :
                nim_file=open( os.path.join( path, 'nim.mel' ), 'w' )
                nim_file.write( renPath )
                nim_file.close
            except : P.info( 'Sorry, unable to write the nim.mel file' )

    #  Set Project :
    try :
        pathToSet=path.replace('\\', '/')+'/'
        if os.path.isdir( pathToSet ) :
            MaxPlus.SetProjectFolderDir( pathToSet )
            P.info( 'nim_3dsmax - Current Project Set: %s\n' % pathToSet )
        else :
            P.info('Project not set!')
    except : pass
    
    return True
    



#  End

