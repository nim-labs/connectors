#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_3dsmax.py
# Version:  v7.0.3.241009
#
# Copyright (c) 2014-2024 NIM Labs LLC
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
from . import nim_version as V

#  3dsMax Imports :
from pymxs import runtime as rt

#  Import Python GUI packages :
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
            pass

#  Variables :
version=V.version
winTitle='NIM '+version

def get_mainWin() :
    'Returns the name of the main 3dsMax window'
    #maxWin=rt.Win32_GetMAXHWnd()
    maxWin = rt.windows.getMAXHWND()
    return maxWin

def set_vars(nim=None):
    'Add custom attributes to 3dsMax Globals'

    # Migrate legacy NIM attributes to nimSceneData root location
    migrate_root_vars()

    P.info('\n3dsMax - Setting Globals Attributes...')

    makeGlobalAttrs = False
    try:
        # TEST FOR EXISTING NIM DATA
        rt.execute("rootnode.custAttributes[\"nimSceneData\"].nim_user")
    except:
        makeGlobalAttrs = True

    if makeGlobalAttrs:
        P.info("NIM data not found...\nAdding Global Attributes")
        
        # Add custom attributes only if they don't exist
        nimAttrCmd = '''
        if (custattributes.getdef rootnode "nimSceneData" == undefined) then (
            nimSceneData = attributes nimSceneData version:1 attribID:#(0x4748c18c, 0xc74245a1)
            (
                parameters main rollout:params
                (
                    nim_user type:#string default:""
                    nim_userID type:#string default:""
                    nim_class type:#string default:""
                    nim_server type:#string default:""
                    nim_serverID type:#string default:""
                    nim_jobName type:#string default:""
                    nim_jobID type:#string default:""
                    nim_showName type:#string default:""
                    nim_showID type:#string default:""
                    nim_shot type:#string default:""
                    nim_shotID type:#string default:""
                    nim_asset type:#string default:""
                    nim_assetID type:#string default:""
                    nim_fileID type:#string default:""
                    nim_name type:#string default:""
                    nim_basename type:#string default:""
                    nim_type type:#string default:""
                    nim_typeID type:#string default:""
                    nim_typeFolder type:#string default:""
                    nim_tag type:#string default:""
                    nim_fileType type:#string default:""
                )
                rollout params "Parameters" (
                    label ui_label "NIM Attributes"
                )
            )
            custattributes.add rootnode nimSceneData
        )
        '''
        try:
            rt.execute(nimAttrCmd)
            P.info("Global attributes added or updated")
        except Exception as e:
            P.error(f"Failed to create or update global attributes - {str(e)}")
            return

    P.info("Setting Global Attributes")

    # User:
    userInfo = nim.userInfo()
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_user="'+str(userInfo['name'])+'"')
    except:
        P.error('Failed to set nim_user')

    # User ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_userID="'+str(userInfo['ID'])+'"')
    except:
        P.error('Failed to set nim_userID')

    # Tab/Class:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_class="'+str(nim.tab())+'"')
    except:
        P.error('Failed to set nim_class')

    # Server:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_server="'+str(nim.server())+'"')
    except:
        P.error('Failed to set nim_server')

    # Server ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_serverID="'+str(nim.ID("server"))+'"')
    except:
        P.error('Failed to set nim_serverID')

    # Job:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_jobName="'+str(nim.name("job"))+'"')
    except:
        P.error('Failed to set nim_jobName')

    # Job ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_jobID="'+str(nim.ID("job"))+'"')
    except:
        P.error('Failed to set nim_jobID')

    # Show:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_showName="'+str(nim.name("show"))+'"')
    except:
        P.error('Failed to set nim_showName')

    # Show ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_showID="'+str(nim.ID("show"))+'"')
    except:
        P.error('Failed to set nim_showID')

    # Shot:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_shot="'+str(nim.name("shot"))+'"')
    except:
        P.error('Failed to set nim_shot')

    # Shot ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_shotID="'+str(nim.ID("shot"))+'"')
    except:
        P.error('Failed to set nim_shotID')

    # Asset:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_asset="'+str(nim.name("asset"))+'"')
    except:
        P.error('Failed to set nim_asset')

    # Asset ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_assetID="'+str(nim.ID("asset"))+'"')
    except:
        P.error('Failed to set nim_assetID')

    # File ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_fileID="'+str(nim.ID("ver"))+'"')
    except:
        P.error('Failed to set nim_fileID')

    # Shot/Asset Name:
    try:
        if nim.tab() == 'SHOT':
            rt.execute('rootnode.custAttributes["nimSceneData"].nim_name="'+str(nim.name("shot"))+'"')
        elif nim.tab() == 'ASSET':
            rt.execute('rootnode.custAttributes["nimSceneData"].nim_name="'+str(nim.name("asset"))+'"')
    except:
        P.error('Failed to set nim_name')

    # Basename:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_basename="'+str(nim.name("base"))+'"')
    except:
        P.error('Failed to set nim_basename')

    # Task:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_type="'+str(nim.name(elem="task"))+'"')
    except:
        P.error('Failed to set nim_type')

    # Task ID:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_typeID="'+str(nim.ID(elem="task"))+'"')
    except:
        P.error('Failed to set nim_typeID')

    # Task Folder:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_typeFolder="'+str(nim.taskFolder())+'"')
    except:
        P.error('Failed to set nim_typeFolder')

    # Tag:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_tag="'+str(nim.name("tag"))+'"')
    except:
        P.error('Failed to set nim_tag')

    # File Type:
    try:
        rt.execute('rootnode.custAttributes["nimSceneData"].nim_fileType="'+str(nim.fileType())+'"')
    except:
        P.error('Failed to set nim_fileType')

    P.info('Completed setting NIM attributes on root node.')
    return

def get_vars(nim=None):
    'Gets NIM settings from the defaultRenderGlobals node in 3dsMax.'

    # Migrate legacy NIM attributes to nimSceneData root location
    migrate_root_vars()

    P.info('3dsMax Getting information from NIM attributes...')
    
    # Helper function to read attributes safely
    def read_attr(attr_name):
        try:
            return rt.execute(f'rootnode.custAttributes["nimSceneData"].{attr_name}')
        except:
            P.error(f'Failed reading {attr_name}')
            return None

    # Read and set user info
    nim_user = read_attr("nim_user")
    if nim_user:
        nim.set_user(nim_user)
    
    nim_userID = read_attr("nim_userID")
    if nim_userID:
        nim.set_userID(nim_userID)

    # Tab/Class
    nim_class = read_attr("nim_class")
    if nim_class:
        nim.set_tab(nim_class)

    # Server Info
    nim_server = read_attr("nim_server")
    if nim_server:
        nim.set_server(path=nim_server)

    nim_serverID = read_attr("nim_serverID")
    if nim_serverID:
        nim.set_ID(elem='server', ID=nim_serverID)

    # Job Info
    nim_jobName = read_attr("nim_jobName")
    if nim_jobName:
        nim.set_name(elem='job', name=nim_jobName)

    nim_jobID = read_attr("nim_jobID")
    if nim_jobID:
        nim.set_ID(elem='job', ID=nim_jobID)

    # Show Info
    nim_showName = read_attr("nim_showName")
    if nim_showName:
        nim.set_name(elem='show', name=nim_showName)

    nim_showID = read_attr("nim_showID")
    if nim_showID:
        nim.set_ID(elem='show', ID=nim_showID)

    # Shot Info
    nim_shot = read_attr("nim_shot")
    if nim_shot:
        nim.set_name(elem='shot', name=nim_shot)

    nim_shotID = read_attr("nim_shotID")
    if nim_shotID:
        nim.set_ID(elem='shot', ID=nim_shotID)

    # Asset Info
    nim_asset = read_attr("nim_asset")
    if nim_asset:
        nim.set_name(elem='asset', name=nim_asset)

    nim_assetID = read_attr("nim_assetID")
    if nim_assetID:
        nim.set_ID(elem='asset', ID=nim_assetID)

    # Basename
    nim_basename = read_attr("nim_basename")
    if nim_basename:
        nim.set_name(elem='base', name=nim_basename)

    # Task Info
    nim_type = read_attr("nim_type")
    if nim_type:
        nim.set_name(elem='task', name=nim_type)

    nim_typeID = read_attr("nim_typeID")
    if nim_typeID:
        nim.set_ID(elem='task', ID=nim_typeID)

    # Task Folder
    nim_typeFolder = read_attr("nim_typeFolder")
    if nim_typeFolder:
        nim.set_taskFolder(folder=nim_typeFolder)

    # Tag
    nim_tag = read_attr("nim_tag")
    if nim_tag:
        nim.set_name(elem='tag', name=nim_tag)

    # File Type
    nim_fileType = read_attr("nim_fileType")
    if nim_fileType:
        nim.set_name(elem='file', name=nim_fileType)

    return

def migrate_root_vars():
    'Migrates old NIM attributes to new NIM attributes on the 3dsMax root node.'

    try:
        # Check if old NIM attributes (rootNodeDataCA) exist
        nim_user = None
        if hasattr(rt.rootnode, "custAttributes"):
            nim_user = rt.execute('rootnode.custAttributes["sceneDataCADef"].nim_user')
        
        if nim_user is not None:

            # Read each attribute from the old location and set it in the new location
            def migrate_attribute(attr_name):
                try:
                    old_value = rt.execute(f'rootnode.custAttributes["sceneDataCADef"].{attr_name}')

                    if old_value is not None and old_value != '':
                        P.info(f'Found NIM legacy attribute: {attr_name}')

                        # Ensure the new nimSceneData exists before writing to it
                        nimSceneData = rt.execute(f'rootnode.custAttributes["nimSceneData"]')
                        
                        # Define new custom attributes if they don't exist
                        if nimSceneData is None:
                            nimSceneDataCmd = '''
                                    nimSceneData = attributes nimSceneData version:1 attribID:#(0x4748c18c, 0xc74245a1)
                                    (
                                        parameters main rollout:params
                                        (
                                            nim_user type:#string default:""
                                            nim_userID type:#string default:""
                                            nim_class type:#string default:""
                                            nim_server type:#string default:""
                                            nim_serverID type:#string default:""
                                            nim_jobName type:#string default:""
                                            nim_jobID type:#string default:""
                                            nim_showName type:#string default:""
                                            nim_showID type:#string default:""
                                            nim_shot type:#string default:""
                                            nim_shotID type:#string default:""
                                            nim_asset type:#string default:""
                                            nim_assetID type:#string default:""
                                            nim_fileID type:#string default:""
                                            nim_name type:#string default:""
                                            nim_basename type:#string default:""
                                            nim_type type:#string default:""
                                            nim_typeID type:#string default:""
                                            nim_typeFolder type:#string default:""
                                            nim_tag type:#string default:""
                                            nim_fileType type:#string default:""
                                        )
                                        rollout params "Parameters" (
                                            label ui_label "NIM Attributes"
                                        )
                                    )
                                    custattributes.add rootnode nimSceneData
                                '''
                            rt.execute(nimSceneDataCmd)
                        
                        setattr(rt.rootnode.custAttributes["nimSceneData"], attr_name, old_value)
                        P.info(f'Migrated legacy attribute: {attr_name}')

                        # Remove old attribute from old location
                        try:
                            setattr(rt.rootnode.custAttributes["sceneDataCADef"], attr_name, '')
                            P.info(f'Removed legacy attribute: {attr_name}')
                        except Exception as e:
                            P.error(f'Failed to remove legacy attribute: {attr_name} : {str(e)}')

                except Exception as e:
                    P.error(f'Failed to migrate legacy attribute: {attr_name}: {str(e)}')

            # List of attributes to migrate
            attributes = [
                "nim_user", "nim_userID", "nim_class", "nim_server", "nim_serverID",
                "nim_jobName", "nim_jobID", "nim_showName", "nim_showID", "nim_shot",
                "nim_shotID", "nim_asset", "nim_assetID", "nim_fileID", "nim_name",
                "nim_basename", "nim_type", "nim_typeID", "nim_typeFolder", "nim_tag",
                "nim_fileType"
            ]

            # Migrate all attributes
            for attr in attributes:
                migrate_attribute(attr)

        else:
            P.info('NIM legacy attributes not found. Migration not needed.')

    except Exception as e:
        pass

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
    workspace +='[XReferenceDirs]\n'
    workspace +='Dir1=./scenes\n'

    #TODO: UPDATE WITH ACTIVE BITMAP DIRS
    maxLocation = rt.symbolicPaths.getPathValue('$max')

    workspace +='[BitmapDirs]\n'
    workspace +='Dir1='+maxLocation+'/Maps\n'
    workspace +='Dir2='+maxLocation+'/Maps/glare\n'
    workspace +='Dir3='+maxLocation+'/Maps/adskMtl\n'
    workspace +='Dir4='+maxLocation+'/Maps/Noise\n'
    workspace +='Dir5='+maxLocation+'/Maps/Substance/noises\n'
    workspace +='Dir6='+maxLocation+'/Maps/Substance/textures\n'
    workspace +='Dir7='+maxLocation+'/Maps/mental_mill\n'
    workspace +='Dir8='+maxLocation+'/Maps/fx\n'
    workspace +='Dir9='+maxLocation+'/Maps/Particle Flow Presets\n'
    workspace +='Dir10=./downloads\n'

    return workspace
    

def mk_proj( path='', renPath='' ) :
    'Creates a show project structure'
    from pymxs import runtime as maxRT
    mpPM = maxRT.pathConfig
    workspaceExists=False
    
    #  Variables :
    projDirs=['sceneassets','sceneassets/animations', 'archives', 'autoback', 'proxies', 'downloads',
        'export', 'express', 'sceneassets/images', 'import', 'materiallibraries', 'scenes',
        'sceneassets\photometric', 'previews', 'sceneassets/renderassets', 'renderoutput', 'renderpresets',
        'sceneassets/sound', 'vpost' ]
    
    projectName = os.path.basename(os.path.normpath(path))
    P.info('Project Folder: %s' % projectName)

    #  Create 3dsMax project directories :
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
            mpPM.setCurrentProjectFolder ( pathToSet )
            P.info( 'nim_3dsmax - Current Project Set: %s\n' % pathToSet )
        else :
            P.info('Project not set!')
    except : 
        P.error('Failed to set project.')
    
    return True
    



#  End

