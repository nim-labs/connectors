#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_houdini.py
# Version:  v6.0.0.230807
#
# Copyright (c) 2014-2023 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import os, sys, traceback
from . import nim as Nim
from . import nim_file as F
from . import nim_print as P
#  Houdini Imports :
import hou
#  Import Python GUI packages :
try : from PySide import QtCore, QtGui
except :
    try : 
        from PyQt4 import QtCore, QtGui
    except :
        try :
            from PyQt5 import QtWidgets as QtGui
            from PyQt5 import QtCore
        except : 
            pass

#  Variables :
version='v6.0.0'
winTitle='NIM_'+version

def get_mainWin() :
    'Returns the name of the main Houdini window'
    import hou
    #maxWin=MaxPlus.Win32_GetMAXHWnd()
    #return maxWin
    return True

def set_vars( nim=None ) :
    'Add variables to Houdini Globals'
    
    P.info( '\nHoudini - Setting Globals variables...' )

    #  User :
    userInfo=nim.userInfo()

    makeGlobalAttrs = False
    h_root = hou.node("/")
    
    h_root.setUserData("nim_user", str(userInfo['name'])) 
    h_root.setUserData("nim_userID", str(userInfo['ID'])) 
    h_root.setUserData("nim_class", str(nim.tab())) 
    h_root.setUserData("nim_server", str(nim.server())) 
    h_root.setUserData("nim_serverID", str(nim.ID('server'))) 
    h_root.setUserData("nim_jobName", str(nim.name('job'))) 
    h_root.setUserData("nim_jobID", str(nim.ID('job'))) 
    h_root.setUserData("nim_showName", str(nim.name('show'))) 
    h_root.setUserData("nim_showID", str(nim.ID('show'))) 
    h_root.setUserData("nim_shot", str(nim.name('shot'))) 
    h_root.setUserData("nim_shotID", str(nim.ID('shot'))) 
    h_root.setUserData("nim_asset", str(nim.name('asset'))) 
    h_root.setUserData("nim_assetID", str(nim.ID('asset'))) 
    h_root.setUserData("nim_fileID", str(nim.ID('ver')))

    if nim.tab()=='SHOT' :
        h_root.setUserData("nim_name", str(nim.name('shot')))
    elif nim.tab()=='ASSET' :
        h_root.setUserData("nim_name", str(nim.name('asset')))

    h_root.setUserData("nim_basename", str(nim.name('base'))) 
    h_root.setUserData("nim_type", str(nim.name( elem='task'))) 
    h_root.setUserData("nim_typeID", str(nim.ID( elem='task' ))) 
    h_root.setUserData("nim_typeFolder", str(nim.taskFolder())) 
    h_root.setUserData("nim_tag", str(nim.name('tag'))) 
    h_root.setUserData("nim_fileType", str(nim.fileType())) 
    P.info("Root attributes added")

    return
    

def get_vars( nim=None ) :
    'Gets NIM settings from the root node in Houdini.'
    P.info('Getting information from NIM attributes on the root node...')
    
    h_root = hou.node("/")

    #  User :
    nim_user = h_root.userData("nim_user")
    if nim_user is not None:
        nim.set_user( userName=nim_user )
        P.info('Reading userName')
    else:
        P.error('Failed reading userName')

    '''
    if mc.objExists( 'defaultRenderGlobals.nim_user' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_user' )
        P.debug( 'User = %s' % value )
        nim.set_user( userName=value )
    '''


    #  User ID :
    nim_userID = h_root.userData("nim_userID")
    if nim_userID is not None:
        nim.set_userID( userID=nim_userID )
        P.info('Reading userID')
    else:
        P.error('Failed reading userID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_userID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_userID' )
        P.debug( 'User ID = %s' % value )
        nim.set_userID( userID=value )
    '''

    #  Tab/Class :
    nim_class = h_root.userData("nim_class")
    if nim_class is not None:
        nim.set_tab( nim_class )
        P.info('Reading nim_class')
    else:
        P.error('Failed reading nim_class')

    '''
    if mc.objExists( 'defaultRenderGlobals.nim_class' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_class' )
        P.debug( 'Tab = %s' % value )
        nim.set_tab( value )
    '''



    #  Server :
    nim_server = h_root.userData("nim_server")
    if nim_server is not None:
        nim.set_server( path=nim_server )
        P.info('Reading nim_server')
    else:
        P.error('Failed reading nim_server')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_server' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_server' )
        P.debug( 'Server = %s' % value )
        nim.set_server( path=value )
    '''


    #  Server ID :
    nim_serverID = h_root.userData("nim_serverID")
    if nim_serverID is not None:
        nim.set_ID( elem='server', ID=nim_serverID )
        P.info('Reading nim_serverID')
    else:
        P.error('Failed reading nim_serverID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_serverID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_serverID' )
        P.debug( 'Server ID = %s' % value )
        nim.set_ID( elem='server', ID=value )
    '''



    #  Job :
    nim_jobName = h_root.userData("nim_jobName")
    if nim_jobName is not None:
        nim.set_name( elem='job', name=nim_jobName )
        P.info('Reading nim_jobName')
    else:
        P.error('Failed reading nim_jobName')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_jobName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobName' )
        P.debug( 'Job = %s' % value )
        nim.set_name( elem='job', name=value )
    '''


    #  Job ID :
    nim_jobID = h_root.userData("nim_jobID")
    if nim_jobID is not None:
        nim.set_ID( elem='job', ID=nim_jobID )
        P.info('Reading nim_jobID')
    else:
        P.error('Failed reading nim_jobID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_jobID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobID' )
        P.debug( 'Job ID = %s' % value )
        nim.set_ID( elem='job', ID=value )
    '''



    #  Show :
    nim_showName = h_root.userData("nim_showName")
    if nim_showName is not None:
        nim.set_name( elem='show', name=nim_showName )
        P.info('Reading nim_showName')
    else:
        P.error('Failed reading nim_showName')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_showName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showName' )
        P.debug( 'Show = %s' % value )
        nim.set_name( elem='show', name=value )
    '''



    #  Show ID :
    nim_showID = h_root.userData("nim_showID")
    if nim_showID is not None:
        nim.set_ID( elem='show', ID=nim_showID )
        P.info('Reading nim_showID')
    else:
        P.error('Failed reading nim_showID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_showID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showID' )
        P.debug( 'Show ID = %s' % value )
        nim.set_ID( elem='show', ID=value )
    '''


    
    #  Shot :
    nim_shot = h_root.userData("nim_shot")
    if nim_shot is not None:
        nim.set_name( elem='shot', name=nim_shot )
        P.info('Reading nim_shot')
    else:
        P.error('Failed reading nim_shot')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_shot' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shot' )
        P.debug( 'Shot = %s' % value )
        nim.set_name( elem='shot', name=value )
    '''


    
    #  Shot ID :
    nim_shotID = h_root.userData("nim_shotID")
    if nim_shotID is not None:
        nim.set_ID( elem='shot', ID=nim_shotID )
        P.info('Reading nim_shotID')
    else:
        P.error('Failed reading nim_shotID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_shotID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shotID' )
        P.debug( 'Shot ID = %s' % value )
        nim.set_ID( elem='shot', ID=value )
    '''


    
    #  Asset :
    nim_asset = h_root.userData("nim_asset")
    if nim_asset is not None:
        nim.set_name( elem='asset', name=nim_asset )
        P.info('Reading nim_asset')
    else:
        P.error('Failed reading nim_asset')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_asset' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_asset' )
        P.debug( 'Asset = %s' % value )
        nim.set_name( elem='asset', name=value )
    '''

    
    #  Asset ID :
    nim_assetID = h_root.userData("nim_assetID")
    if nim_assetID is not None:
        nim.set_ID( elem='asset', ID=nim_assetID )
        P.info('Reading nim_assetID')
    else:
        P.error('Failed reading nim_assetID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_assetID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_assetID' )
        P.debug( 'Asset ID = %s' % value )
        nim.set_ID( elem='asset', ID=value )
    '''

    
    #  File ID :
    '''
    if mc.attributeQuery( 'defaultRenderGlobals.nim_fileID' ) :
        value=mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals' )
        P.debug( 'Class = %s' % value )
        nim.set_tab( tab=value )
    '''
    #TODO: Check if Maya code is error or intentional


    
    #  Shot/Asset Name :
    nim_name = h_root.userData("nim_name")
    if nim_name is not None:
        if nim.tab()=='SHOT' :
            P.debug( 'Shot Name = %s' % nim_name )
            #nim.set_tab( nim_name.Get() )
        elif nim.tab()=='ASSET' :
            P.debug( 'Asset Name = %s' % nim_name )
            #nim.set_tab( nim_name.Get() )
    else:
        P.error('Failed reading nim_name')
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



    #  Basename :
    nim_basename = h_root.userData("nim_basename")
    if nim_basename is not None:
        nim.set_name( elem='base', name=nim_basename )
        P.info('Reading nim_basename')
    else:
        P.error('Failed reading nim_basename')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_basename' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_basename' )
        P.debug( 'Basename = %s' % value )
        nim.set_name( elem='base', name=value )
    
    '''



    #  Task :
    nim_type = h_root.userData("nim_type")
    if nim_type is not None:
        nim.set_name( elem='task', name=nim_type )
        P.info('Reading nim_type')
    else:
        P.error('Failed reading nim_type')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_type' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_type' )
        P.debug( 'Task = %s' % value )
        nim.set_name( elem='task', name=value )
    
    '''



    #  Task ID :
    nim_typeID = h_root.userData("nim_typeID")
    if nim_typeID is not None:
        nim.set_ID( elem='task', ID=nim_typeID )
        P.info('Reading nim_typeID')
    else:
        P.error('Failed reading nim_typeID')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_typeID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeID' )
        P.debug( 'Task ID = %s' % value )
        nim.set_ID( elem='task', ID=value )
    
    '''


    
    #  Task Folder :
    nim_typeFolder = h_root.userData("nim_typeFolder")
    if nim_typeFolder is not None:
        nim.set_taskFolder( folder=nim_typeFolder )
        P.info('Reading nim_typeFolder')
    else:
        P.error('Failed reading nim_typeFolder')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_typeFolder' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeFolder' )
        P.debug( 'Task Folder = %s' % value )
        nim.set_taskFolder( folder=value )
    
    '''

    
    #  Tag :
    nim_tag = h_root.userData("nim_tag")
    if nim_tag is not None:
        nim.set_name( elem='tag', name=nim_tag )
        P.info('Reading nim_tag')
    else:
        P.error('Failed reading nim_tag')
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_tag' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_tag' )
        P.debug( 'Tag = %s' % value )
        nim.set_name( elem='tag', name=value )
    
    '''

    
    #  File Type :
    nim_fileType = h_root.userData("nim_fileType")
    if nim_fileType is not None:
        nim.set_name( elem='file', name=nim_fileType )
        P.info('Reading nim_fileType')
    else:
        P.error('Failed reading nim_fileType')

    '''
    if mc.objExists( 'defaultRenderGlobals.nim_fileType' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_fileType' )
        P.debug( 'File Type = %s' % value )
        nim.set_name( elem='file', name=value )
    '''

    #  Print dictionary :
    #P.info('\nNIM Dictionary from get vars...')
    #nim.Print()
    
    return
    

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

    return workspace
    

def mk_proj( path='', renPath='' ) :
    'Creates a show project structure'
    import hou
    workspaceExists=False
    
    #  Variables :
    projDirs=['abc','audio', 'comp', 'desk', 'flip', 'geo',
        'hda', 'render', 'scripts', 'sim', 'tex', 'video']
    
    projectName = os.path.basename(os.path.normpath(path))
    P.info('Project Folder: %s' % projectName)

    #  Create Houdini project directories :
    if os.path.isdir( path ) :
        for projDir in projDirs:
            _dir=os.path.normpath( os.path.join( path, projDir ).replace('\\', '/') )
            if not os.path.isdir( _dir ) :
                P.info("DIR: %s" % _dir)
                try : os.mkdir( _dir )
                except Exception as e :
                    P.error( 'Failed creating the directory: %s' % _dir )
                    P.error( '    %s' % traceback.print_exc() )
                    return False
    
    '''
    #  Check for workspace file :
    projectConfigFileName = projectName+'.mxp'
    workspaceFile=os.path.normpath( os.path.join( path, projectConfigFileName ) )
    if os.path.exists( workspaceFile ) :
        workspaceExists=True
    
    #  Create workspace file :
    if not workspaceExists :
        P.info('Creating Houdini path configuration file...')
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
    '''

    #  Set Project :
    try :
        pathToSet=path.replace('\\', '/')+'/'
        if os.path.isdir( pathToSet ) :
            # update the environment variables
            os.environ.update({"JOB": str(pathToSet)})
            # update JOB using hscript
            hou.hscript("set -g JOB = '" + str(pathToSet) + "'")
            hou.allowEnvironmentToOverwriteVariable("JOB", True)
            P.info( 'Current Project Set: %s\n' % pathToSet )
        else :
            P.info('Project not set!')
    except : pass
    
    return True
    



#  End

