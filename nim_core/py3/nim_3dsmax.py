#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_3dsmax.py
# Version:  v5.0.12.210802
#
# Copyright (c) 2014-2021 NIM Labs LLC
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
version='v5.0.12'
winTitle='NIM_'+version

def get_mainWin() :
    'Returns the name of the main 3dsMax window'
    #maxWin=rt.Win32_GetMAXHWnd()
    maxWin = rt.windows.getMAXHWND()
    return maxWin

def set_vars( nim=None ) :
    'Add variables to 3dsMax Globals'
    
    P.info( '\n3dsMax - Setting Globals variables...' )

    makeGlobalAttrs = False
    try:
        #TEST FOR EXISTING NIM DATA
        rt.execute("rootNodeDataCA.nim_user")
        rt.execute("sceneDataCA.nim_user")
    except:   
        makeGlobalAttrs = True
    

    if makeGlobalAttrs :
        P.info("NIM DATA Not Found.\nAdding Global Attributes")

        # clear custom attributes
        nimAttrDel = 'z=1 \n\
                        while z !=undefined do \n\
                        ( \n\
                            x = rootscene \n\
                            z = custattributes.getdef x 1 \n\
                            custAttributes.delete x z \n\
                        )'
        try :
            rt.execute(nimAttrDel)
            P.info("Root and Scene attributes cleared")
        except :
            P.error("Failed to clear global attributes")
            return

        # add custom attributes
        nimAttrCmd = 'sceneDataCADef = attributes sceneDataCADef version:1 attribID:#(0x4fb91dfa, 0x73284f9e) \n\
                        (   \n\
                            parameters main rollout:params \n\
                            ( \n\
                                nim_user type:#string ui:nim_user default:"" \n\
                                nim_userID type:#string ui:nim_userID default:"" \n\
                                nim_class type:#string ui:nim_class default:"" \n\
                                nim_server type:#string ui:nim_server default:"" \n\
                                nim_serverID type:#string ui:nim_serverID default:"" \n\
                                nim_jobName type:#string ui:nim_jobName default:"" \n\
                                nim_jobID type:#string ui:nim_jobID default:"" \n\
                                nim_showName type:#string ui:nim_showName default:"" \n\
                                nim_showID type:#string ui:nim_showID default:"" \n\
                                nim_shot type:#string ui:nim_shot default:"" \n\
                                nim_shotID type:#string ui:nim_shotID default:"" \n\
                                nim_asset type:#string ui:nim_asset default:"" \n\
                                nim_assetID type:#string ui:nim_assetID default:"" \n\
                                nim_fileID type:#string ui:nim_fileID default:"" \n\
                                nim_name type:#string ui:nim_name default:"" \n\
                                nim_basename type:#string ui:nim_basename default:"" \n\
                                nim_type type:#string ui:nim_type default:"" \n\
                                nim_typeID type:#string ui:nim_typeID default:"" \n\
                                nim_typeFolder type:#string ui:nim_typeFolder default:"" \n\
                                nim_tag type:#string ui:nim_tag default:"" \n\
                                nim_fileType type:#string ui:nim_fileType default:"" \n\
                            ) \n\
                            rollout params "Scene Data Parameters" \n\
                            (  \n\
                                edittext nim_user "NIM nim_user" \n\
                                edittext nim_userID "NIM UserID" \n\
                                edittext nim_class "NIM nim_class" \n\
                                edittext nim_server "NIM nim_server" \n\
                                edittext nim_serverID "NIM ServerID" \n\
                                edittext nim_jobName "NIM nim_jobName" \n\
                                edittext nim_jobID "NIM JobID" \n\
                                edittext nim_showName "NIM nim_showName" \n\
                                edittext nim_showID "NIM ShowID" \n\
                                edittext nim_shot "NIM nim_shot" \n\
                                edittext nim_shotID "NIM nim_shotID" \n\
                                edittext nim_asset "NIM nim_asset" \n\
                                edittext nim_assetID "NIM nim_assetID" \n\
                                edittext nim_fileID "NIM nim_fileID" \n\
                                edittext nim_name "NIM nim_name" \n\
                                edittext nim_basename "NIM nim_basename" \n\
                                edittext nim_type "NIM nim_type" \n\
                                edittext nim_typeID "NIM nim_typeID" \n\
                                edittext nim_typeFolder "NIM nim_typeFolder" \n\
                                edittext nim_tag "NIM nim_tag" \n\
                                edittext nim_fileType "NIM nim_fileType" \n\
                            ) \n\
                        ) \n\
                        thescene = (refs.dependents rootnode)[1] \n\
                        rootNodeDataCA = undefined \n\
                        if (custattributes.add rootnode sceneDataCADef) do \n\
                            rootNodeDataCA = rootnode.custAttributes[rootnode.custAttributes.count] \n\
                        sceneDataCA = undefined \n\
                        if (custattributes.add thescene sceneDataCADef) do \n\
                            sceneDataCA = thescene.custAttributes[thescene.custAttributes.count] \n'
        try:
            rt.execute(nimAttrCmd)
            P.info("Root and Scene attributes added")
        except:
            P.error("Failed to create global attributes")
            return

        # read custom attributes
        nimAttrReadCmd = 'thescene = (refs.dependents rootnode)[1] \n\
                          rootNodeDataCA = undefined \n\
                          if(rootnode.custAttributes.count != 0) do \n\
                             rootNodeDataCA = rootnode.custAttributes[rootnode.custAttributes.count] \n\
                          sceneDataCA = undefined \n\
                          if(thescene.custAttributes.count != 0) do \n\
                             sceneDataCA = thescene.custAttributes[thescene.custAttributes.count] \n'
        try:
            rt.execute(nimAttrReadCmd)
        except:
            P.error('Failed to read global attributes')
            return


    P.info("Reading Global Attributes")
    
    #  User :
    userInfo=nim.userInfo()
    
    '''
    if not mc.attributeQuery( 'nim_user', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_user', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_user', userInfo['name'], type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_user="'+str(userInfo['name'])+'"' )
    rt.execute('sceneDataCA.nim_user="'+str(userInfo['name'])+'"' )

    #  User ID :
    '''
    if not mc.attributeQuery( 'nim_userID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_userID', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_userID', userInfo['ID'], type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_userID="'+str(userInfo['ID'])+'"' )
    rt.execute('sceneDataCA.nim_userID="'+str(userInfo['ID'])+'"' )

    #  Tab/Class :
    '''
    if not mc.attributeQuery( 'nim_class', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_class', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_class', nim.tab(), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_class="'+str(nim.tab())+'"' )
    rt.execute('sceneDataCA.nim_class="'+str(nim.tab())+'"' )

    #  Server :
    '''
    if not mc.attributeQuery( 'nim_server', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_server', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_server', nim.server(), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_server="'+str(nim.server())+'"' )
    rt.execute('sceneDataCA.nim_server="'+str(nim.server())+'"' )

    #  Server ID :
    '''
    if not mc.attributeQuery( 'nim_serverID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_serverID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_serverID', str(nim.ID('server')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_serverID="'+str(nim.ID('server'))+'"' )
    rt.execute('sceneDataCA.nim_serverID="'+str(nim.ID('server'))+'"' )

    #  Job :
    '''
    if not mc.attributeQuery( 'nim_jobName', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_jobName', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_jobName', nim.name('job'), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_jobName="'+str(nim.name('job'))+'"' )
    rt.execute('sceneDataCA.nim_jobName="'+str(nim.name('job'))+'"' )

    #  Job ID :
    '''
    if not mc.attributeQuery( 'nim_jobID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_jobID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_jobID', str(nim.ID('job')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_jobID="'+str(nim.ID('job'))+'"' )
    rt.execute('sceneDataCA.nim_jobID="'+str(nim.ID('job'))+'"' )

    #  Show :
    '''
    if not mc.attributeQuery( 'nim_showName', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_showName', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_showName', nim.name('show'), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_showName="'+str(nim.name('show'))+'"' )
    rt.execute('sceneDataCA.nim_showName="'+str(nim.name('show'))+'"' )

    #  Show ID :
    '''
    if nim.tab()=='SHOT' :
        if not mc.attributeQuery( 'nim_showID', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_showID', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_showID', str(nim.ID('show')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_showID="'+str(nim.ID('show'))+'"' )
    rt.execute('sceneDataCA.nim_showID="'+str(nim.ID('show'))+'"' )

    #  Shot :
    '''
    if not mc.attributeQuery( 'nim_shot', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_shot', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_shot', str(nim.name('shot')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_shot="'+str(nim.name('shot'))+'"' )
    rt.execute('sceneDataCA.nim_shot="'+str(nim.name('shot'))+'"' )

    #  Shot ID :
    '''
    if not mc.attributeQuery( 'nim_shotID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_shotID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_shotID', str(nim.ID('shot')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_shotID="'+str(nim.ID('shot'))+'"' )
    rt.execute('sceneDataCA.nim_shotID="'+str(nim.ID('shot'))+'"' )

    #  Asset :
    '''
    if nim.tab()=='ASSET' :
        if not mc.attributeQuery( 'nim_asset', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_asset', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_asset', str(nim.name('asset')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_asset="'+str(nim.name('asset'))+'"' )
    rt.execute('sceneDataCA.nim_asset="'+str(nim.name('asset'))+'"' )

    #  Asset ID :
    '''
    if nim.tab()=='ASSET' :
        if not mc.attributeQuery( 'nim_assetID', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_assetID', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_assetID', str(nim.ID('asset')), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_assetID="'+str(nim.ID('asset'))+'"' )
    rt.execute('sceneDataCA.nim_assetID="'+str(nim.ID('asset'))+'"' )

    #  File ID :
    '''
    if not mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_fileID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_fileID', str(nim.ID('ver')), type='string' )
    '''
    P.info("FileID: %s" % str(nim.ID('ver')))
    rt.execute('rootNodeDataCA.nim_fileID="'+str(nim.ID('ver'))+'"' )
    rt.execute('sceneDataCA.nim_fileID="'+str(nim.ID('ver'))+'"' )

    #  Shot/Asset Name :
    '''
    if not mc.attributeQuery( 'nim_name', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_name', dt="string")
    '''
    if nim.tab()=='SHOT' :
        #mc.setAttr( 'defaultRenderGlobals.nim_name', nim.name('shot'), type='string' )
        rt.execute('rootNodeDataCA.nim_name="'+str(nim.name('shot'))+'"' )
        rt.execute('sceneDataCA.nim_name="'+str(nim.name('shot'))+'"' )
    elif nim.tab()=='ASSET' :
        #mc.setAttr( 'defaultRenderGlobals.nim_name', nim.name('asset'), type='string' )
        rt.execute('rootNodeDataCA.nim_name="'+str(nim.name('asset'))+'"' )
        rt.execute('sceneDataCA.nim_name="'+str(nim.name('asset'))+'"' )
    
    #  Basename :
    '''
    if not mc.attributeQuery( 'nim_basename', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_basename', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_basename', nim.name('base'), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_basename="'+str(nim.name('base'))+'"' )
    rt.execute('sceneDataCA.nim_basename="'+str(nim.name('base'))+'"' )

    #  Task :
    '''
    if not mc.attributeQuery( 'nim_type', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_type', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_type', nim.name( elem='task' ), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_type="'+str(nim.name( elem='task'))+'"' )
    rt.execute('sceneDataCA.nim_type="'+str(nim.name( elem='task'))+'"' )

    #  Task ID :
    '''
    if not mc.attributeQuery( 'nim_typeID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_typeID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_typeID', str(nim.ID( elem='task' )), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_typeID="'+str(nim.ID( elem='task' ))+'"' )
    rt.execute('sceneDataCA.nim_typeID="'+str(nim.ID( elem='task' ))+'"' )

    #  Task Folder :
    '''
    if not mc.attributeQuery( 'nim_typeFolder', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_typeFolder', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_typeFolder', str(nim.taskFolder()), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_typeFolder="'+str(nim.taskFolder())+'"' )
    rt.execute('sceneDataCA.nim_typeFolder="'+str(nim.taskFolder())+'"' )

    #  Tag :
    '''
    if not mc.attributeQuery( 'nim_tag', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_tag', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_tag', nim.name('tag'), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_tag="'+str(nim.name('tag'))+'"' )
    rt.execute('sceneDataCA.nim_tag="'+str(nim.name('tag'))+'"' )

    #  File Type :
    '''
    if not mc.attributeQuery( 'nim_fileType', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_fileType', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_fileType', nim.fileType(), type='string' )
    '''
    rt.execute('rootNodeDataCA.nim_fileType="'+str(nim.fileType())+'"' )
    rt.execute('sceneDataCA.nim_fileType="'+str(nim.fileType())+'"' )

    P.info('    Completed setting NIM attributes root node.')
    #nim.Print()
    
    return
    

def get_vars( nim=None ) :
    'Gets NIM settings from the defaultRenderGlobals node in 3dsMax.'
    P.info('3dsMax Getting information from NIM attributes...')
    
    #  User :
    try:
        nim_user = rt.execute("rootNodeDataCA.nim_user")
        if nim_user:
            nim.set_user( nim_user )
            P.info('Reading userName')
        else:
            P.error('Failed reading userName')
    except :
        P.error('Scene Data Not Found.  Please save the scene using NIM > Save As before updating the version.')
        return False

    #  User ID :
    nim_userID = rt.execute("rootNodeDataCA.nim_userID" )
    if nim_userID:
        nim.set_userID( nim_userID )
        P.error('Reading nim_userID')
    else:
        P.error('Failed reading nim_userID')


    #  Tab/Class :
    nim_class = rt.execute("rootNodeDataCA.nim_class" )
    if nim_class:
        nim.set_tab( nim_class )
        P.error('Reading nim_class')
    else:
        P.error('Failed reading nim_class')


    #  Server :
    nim_server = rt.execute("rootNodeDataCA.nim_server" )
    if nim_server:
        nim.set_server( path=nim_server )
        P.error('Reading nim_server')
    else:
        P.error('Failed reading nim_server')


    #  Server ID :
    nim_serverID = rt.execute("rootNodeDataCA.nim_serverID" )
    if nim_serverID:
        nim.set_ID( elem='server', ID=nim_serverID )
        P.error('Reading nim_serverID')
    else:
        P.error('Failed reading nim_serverID')


    #  Job :
    nim_jobName = rt.execute("rootNodeDataCA.nim_jobName" )
    if nim_jobName:
        nim.set_name( elem='job', name=nim_jobName )
        P.error('Reading nim_jobName')
    else:
        P.error('Failed reading nim_jobName')

    #  Job ID :
    nim_jobID = rt.execute("rootNodeDataCA.nim_jobID" )
    if nim_jobID:
        nim.set_ID( elem='job', ID=nim_jobID )
        P.error('Reading nim_jobID')
    else:
        P.error('Failed reading nim_jobID')


    #  Show :
    nim_showName = rt.execute("rootNodeDataCA.nim_showName" )
    if nim_showName:
        nim.set_name( elem='show', name=nim_showName )
        P.error('Reading nim_showName')
    else:
        P.error('Failed reading nim_showName')


    #  Show ID :
    nim_showID = rt.execute("rootNodeDataCA.nim_showID" )
    if nim_showID:
        nim.set_ID( elem='show', ID=nim_showID )
        P.error('Reading nim_showID')
    else:
        P.error('Failed reading nim_showID')

    
    #  Shot :
    nim_shot = rt.execute("rootNodeDataCA.nim_shot" )
    if nim_shot:
        nim.set_name( elem='shot', name=nim_shot )
        P.error('Reading nim_shot')
    else:
        P.error('Failed reading nim_shot')

    
    #  Shot ID :
    nim_shotID = rt.execute("rootNodeDataCA.nim_shotID" )
    if nim_shotID:
        nim.set_ID( elem='shot', ID=nim_shotID )
        P.error('Reading nim_shotID')
    else:
        P.error('Failed reading nim_shotID')

    
    #  Asset :
    nim_asset = rt.execute("rootNodeDataCA.nim_asset" )
    if nim_asset:
        nim.set_name( elem='asset', name=nim_asset )
        P.error('Reading nim_asset')
    else:
        P.error('Failed reading nim_asset')
    
    #  Asset ID :
    nim_assetID = rt.execute("rootNodeDataCA.nim_assetID" )
    if nim_assetID:
        nim.set_ID( elem='asset', ID=nim_assetID )
        P.error('Reading nim_assetID')
    else:
        P.error('Failed reading nim_assetID')
    
    #  File ID :
    nim_fileID = rt.execute("rootNodeDataCA.nim_fileID" )
    if nim_fileID:
        #nim.set_ID( elem='file', ID=nim_fileID.Get() )
        #nim.set_tab( tab=nim_fileID.Get() )
        #P.error('Reading nim_fileID')
        pass
    else:
        P.error('Failed reading nim_fileID')

    
    #  Shot/Asset Name :
    nim_name = rt.execute("rootNodeDataCA.nim_name" )
    if nim_name:
        if nim.tab()=='SHOT' :
            P.debug( 'Shot Name = %s' % nim_name )
            #nim.set_tab( nim_name.Get() )
        elif nim.tab()=='ASSET' :
            P.debug( 'Asset Name = %s' % nim_name )
            #nim.set_tab( nim_name.Get() )
    else:
        P.error('Failed reading nim_name')


    #  Basename :
    nim_basename = rt.execute("rootNodeDataCA.nim_basename" )
    if nim_basename:
        nim.set_name( elem='base', name=nim_basename )
        P.error('Reading nim_basename')
    else:
        P.error('Failed reading nim_basename')


    #  Task :
    nim_type = rt.execute("rootNodeDataCA.nim_type" )
    if nim_type:
        nim.set_name( elem='task', name=nim_type )
        P.error('Reading nim_type')
    else:
        P.error('Failed reading nim_type')


    #  Task ID :
    nim_typeID = rt.execute("rootNodeDataCA.nim_typeID" )
    if nim_typeID:
        nim.set_ID( elem='task', ID=nim_typeID )
        P.error('Reading nim_typeID')
    else:
        P.error('Failed reading nim_typeID')

    
    #  Task Folder :
    nim_typeFolder = rt.execute("rootNodeDataCA.nim_typeFolder" )
    if nim_typeFolder:
        nim.set_taskFolder( folder=nim_typeFolder )
        P.error('Reading nim_typeFolder')
    else:
        P.error('Failed reading nim_typeFolder')
    
    #  Tag :
    nim_tag = rt.execute("rootNodeDataCA.nim_tag" )
    if nim_tag:
        nim.set_name( elem='tag', name=nim_tag )
        P.error('Reading nim_tag')
    else:
        P.error('Failed reading nim_tag')
    
    #  File Type :
    nim_fileType = rt.execute("rootNodeDataCA.nim_fileType" )
    if nim_fileType:
        nim.set_name( elem='file', name=nim_fileType )
        P.error('Reading nim_fileType')
    else:
        P.error('Failed reading nim_fileType')


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

