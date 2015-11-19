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
    'Add variables to 3dsMax Globals'
    
    P.info( '\n3dsMax - Setting Globals variables...' )

    makeGlobalAttrs = False
    try:
        #TEST FOR EXISTING NIM DATA
        MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_user")
    except:   
        makeGlobalAttrs = True
    

    if makeGlobalAttrs :
        P.info("NIM DATA Not Found.\nAdding Global Attributes")
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
                                edittext nim_serverID "NIM UserID" \n\
                                edittext nim_jobName "NIM nim_jobName" \n\
                                edittext nim_jobID "NIM UserID" \n\
                                edittext nim_showName "NIM nim_showName" \n\
                                edittext nim_showID "NIM UserID" \n\
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
            MaxPlus.Core.EvalMAXScript(nimAttrCmd)
            P.info("Root and Scene attributes added")
        except:
            P.error("Failed to create global attributes")
            return

    P.info("Reading Global Attributes")
    nimAttrReadCmd = 'thescene = (refs.dependents rootnode)[1] \n\
                      rootNodeDataCA = undefined \n\
                      if(rootnode.custAttributes.count != 0) do \n\
                         rootNodeDataCA = rootnode.custAttributes[rootnode.custAttributes.count] \n\
                      sceneDataCA = undefined \n\
                      if(thescene.custAttributes.count != 0) do \n\
                         sceneDataCA = thescene.custAttributes[thescene.custAttributes.count] \n'
    try:
        MaxPlus.Core.EvalMAXScript(nimAttrReadCmd)
    except:
        P.error('Failed to read global attributes')
        return

    #  User :
    userInfo=nim.userInfo()
    
    '''
    if not mc.attributeQuery( 'nim_user', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_user', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_user', userInfo['name'], type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_user="'+str(userInfo['name'])+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_user="'+str(userInfo['name'])+'"' )

    #  User ID :
    '''
    if not mc.attributeQuery( 'nim_userID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_userID', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_userID', userInfo['ID'], type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_userID="'+str(userInfo['ID'])+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_userID="'+str(userInfo['ID'])+'"' )

    #  Tab/Class :
    '''
    if not mc.attributeQuery( 'nim_class', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_class', dt='string' )
    mc.setAttr( 'defaultRenderGlobals.nim_class', nim.tab(), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_class="'+str(nim.tab())+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_class="'+str(nim.tab())+'"' )

    #  Server :
    '''
    if not mc.attributeQuery( 'nim_server', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_server', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_server', nim.server(), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_server="'+str(nim.server())+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_server="'+str(nim.server())+'"' )

    #  Server ID :
    '''
    if not mc.attributeQuery( 'nim_serverID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_serverID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_serverID', str(nim.ID('server')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_serverID="'+str(nim.ID('server'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_serverID="'+str(nim.ID('server'))+'"' )

    #  Job :
    '''
    if not mc.attributeQuery( 'nim_jobName', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_jobName', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_jobName', nim.name('job'), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_jobName="'+str(nim.name('job'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_jobName="'+str(nim.name('job'))+'"' )

    #  Job ID :
    '''
    if not mc.attributeQuery( 'nim_jobID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_jobID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_jobID', str(nim.ID('job')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_jobID="'+str(nim.ID('job'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_jobID="'+str(nim.ID('job'))+'"' )

    #  Show :
    '''
    if not mc.attributeQuery( 'nim_showName', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_showName', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_showName', nim.name('show'), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_showName="'+str(nim.name('show'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_showName="'+str(nim.name('show'))+'"' )

    #  Show ID :
    '''
    if nim.tab()=='SHOT' :
        if not mc.attributeQuery( 'nim_showID', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_showID', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_showID', str(nim.ID('show')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_showID="'+str(nim.ID('show'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_showID="'+str(nim.ID('show'))+'"' )

    #  Shot :
    '''
    if not mc.attributeQuery( 'nim_shot', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_shot', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_shot', str(nim.name('shot')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_shot="'+str(nim.name('shot'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_shot="'+str(nim.name('shot'))+'"' )

    #  Shot ID :
    '''
    if not mc.attributeQuery( 'nim_shotID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_shotID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_shotID', str(nim.ID('shot')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_shotID="'+str(nim.ID('shot'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_shotID="'+str(nim.ID('shot'))+'"' )

    #  Asset :
    '''
    if nim.tab()=='ASSET' :
        if not mc.attributeQuery( 'nim_asset', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_asset', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_asset', str(nim.name('asset')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_asset="'+str(nim.name('asset'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_asset="'+str(nim.name('asset'))+'"' )

    #  Asset ID :
    '''
    if nim.tab()=='ASSET' :
        if not mc.attributeQuery( 'nim_assetID', node='defaultRenderGlobals', exists=True) :
            mc.addAttr( 'defaultRenderGlobals', longName='nim_assetID', dt="string")
        mc.setAttr( 'defaultRenderGlobals.nim_assetID', str(nim.ID('asset')), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_assetID="'+str(nim.ID('asset'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_assetID="'+str(nim.ID('asset'))+'"' )

    #  File ID :
    '''
    if not mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_fileID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_fileID', str(nim.ID('ver')), type='string' )
    '''
    P.info("FileID: %s" % str(nim.ID('ver')))
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_fileID="'+str(nim.ID('ver'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_fileID="'+str(nim.ID('ver'))+'"' )

    #  Shot/Asset Name :
    '''
    if not mc.attributeQuery( 'nim_name', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_name', dt="string")
    '''
    if nim.tab()=='SHOT' :
        #mc.setAttr( 'defaultRenderGlobals.nim_name', nim.name('shot'), type='string' )
        MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_name="'+str(nim.name('shot'))+'"' )
        MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_name="'+str(nim.name('shot'))+'"' )
    elif nim.tab()=='ASSET' :
        #mc.setAttr( 'defaultRenderGlobals.nim_name', nim.name('asset'), type='string' )
        MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_name="'+str(nim.name('asset'))+'"' )
        MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_name="'+str(nim.name('asset'))+'"' )
    
    #  Basename :
    '''
    if not mc.attributeQuery( 'nim_basename', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_basename', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_basename', nim.name('base'), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_basename="'+str(nim.name('base'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_basename="'+str(nim.name('base'))+'"' )

    #  Task :
    '''
    if not mc.attributeQuery( 'nim_type', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_type', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_type', nim.name( elem='task' ), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_type="'+str(nim.name( elem='task'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_type="'+str(nim.name( elem='task'))+'"' )

    #  Task ID :
    '''
    if not mc.attributeQuery( 'nim_typeID', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_typeID', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_typeID', str(nim.ID( elem='task' )), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_typeID="'+str(nim.ID( elem='task' ))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_typeID="'+str(nim.ID( elem='task' ))+'"' )

    #  Task Folder :
    '''
    if not mc.attributeQuery( 'nim_typeFolder', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_typeFolder', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_typeFolder', str(nim.taskFolder()), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_typeFolder="'+str(nim.taskFolder())+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_typeFolder="'+str(nim.taskFolder())+'"' )

    #  Tag :
    '''
    if not mc.attributeQuery( 'nim_tag', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_tag', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_tag', nim.name('tag'), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_tag="'+str(nim.name('tag'))+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_tag="'+str(nim.name('tag'))+'"' )

    #  File Type :
    '''
    if not mc.attributeQuery( 'nim_fileType', node='defaultRenderGlobals', exists=True) :
        mc.addAttr( 'defaultRenderGlobals', longName='nim_fileType', dt="string")
    mc.setAttr( 'defaultRenderGlobals.nim_fileType', nim.fileType(), type='string' )
    '''
    MaxPlus.Core.EvalMAXScript('rootNodeDataCA.nim_fileType="'+str(nim.fileType())+'"' )
    MaxPlus.Core.EvalMAXScript('sceneDataCA.nim_fileType="'+str(nim.fileType())+'"' )

    P.info('    Completed setting NIM attributes on the defaultRenderGlobals node.')
    #nim.Print()
    
    return
    

def get_vars( nim=None ) :
    'Gets NIM settings from the defaultRenderGlobals node in Maya.'
    P.info('3dsMax Getting information from NIM attributes on the defaultRenderGlobals node...')
    
    #  User :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_user' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_user' )
        P.debug( 'User = %s' % value )
        nim.set_user( userName=value )
    '''
    nim_user = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_user", nim_user )
    if success:
        nim.set_user( nim_user.Get() )
        P.info('Reading userName')
    else:
        P.error('Failed reading userName')

    #  User ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_userID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_userID' )
        P.debug( 'User ID = %s' % value )
        nim.set_userID( userID=value )
    '''
    nim_userID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_userID", nim_userID )
    if success:
        nim.set_userID( nim_userID.Get() )
        P.error('Reading nim_userID')
    else:
        P.error('Failed reading nim_userID')


    #  Tab/Class :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_class' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_class' )
        P.debug( 'Tab = %s' % value )
        nim.set_tab( value )
    '''
    nim_class = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_class", nim_class )
    if success:
        nim.set_tab( nim_class.Get() )
        P.error('Reading nim_class')
    else:
        P.error('Failed reading nim_class')


    #  Server :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_server' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_server' )
        P.debug( 'Server = %s' % value )
        nim.set_server( path=value )
    '''
    nim_server = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_server", nim_server )
    if success:
        nim.set_server( path=nim_server.Get() )
        P.error('Reading nim_server')
    else:
        P.error('Failed reading nim_server')


    #  Server ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_serverID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_serverID' )
        P.debug( 'Server ID = %s' % value )
        nim.set_ID( elem='server', ID=value )
    '''
    nim_serverID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_serverID", nim_serverID )
    if success:
        nim.set_ID( elem='server', ID=nim_serverID.Get() )
        P.error('Reading nim_serverID')
    else:
        P.error('Failed reading nim_serverID')


    #  Job :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_jobName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobName' )
        P.debug( 'Job = %s' % value )
        nim.set_name( elem='job', name=value )
    '''
    nim_jobName = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_jobName", nim_jobName )
    if success:
        nim.set_name( elem='job', name=nim_jobName.Get() )
        P.error('Reading nim_jobName')
    else:
        P.error('Failed reading nim_jobName')

    #  Job ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_jobID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_jobID' )
        P.debug( 'Job ID = %s' % value )
        nim.set_ID( elem='job', ID=value )
    '''
    nim_jobID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_jobID", nim_jobID )
    if success:
        nim.set_ID( elem='job', ID=nim_jobID.Get() )
        P.error('Reading nim_jobID')
    else:
        P.error('Failed reading nim_jobID')


    #  Show :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_showName' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showName' )
        P.debug( 'Show = %s' % value )
        nim.set_name( elem='show', name=value )
    '''
    nim_showName = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_showName", nim_showName )
    if success:
        nim.set_name( elem='show', name=nim_showName.Get() )
        P.error('Reading nim_showName')
    else:
        P.error('Failed reading nim_showName')


    #  Show ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_showID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_showID' )
        P.debug( 'Show ID = %s' % value )
        nim.set_ID( elem='show', ID=value )
    '''
    nim_showID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_showID", nim_showID )
    if success:
        nim.set_ID( elem='show', ID=nim_showID.Get() )
        P.error('Reading nim_showID')
    else:
        P.error('Failed reading nim_showID')

    
    #  Shot :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_shot' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shot' )
        P.debug( 'Shot = %s' % value )
        nim.set_name( elem='shot', name=value )
    '''
    nim_shot = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_shot", nim_shot )
    if success:
        nim.set_name( elem='shot', name=nim_shot.Get() )
        P.error('Reading nim_shot')
    else:
        P.error('Failed reading nim_shot')

    
    #  Shot ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_shotID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_shotID' )
        P.debug( 'Shot ID = %s' % value )
        nim.set_ID( elem='shot', ID=value )
    '''
    nim_shotID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_shotID", nim_shotID )
    if success:
        nim.set_ID( elem='shot', ID=nim_shotID.Get() )
        P.error('Reading nim_shotID')
    else:
        P.error('Failed reading nim_shotID')

    
    #  Asset :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_asset' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_asset' )
        P.debug( 'Asset = %s' % value )
        nim.set_name( elem='asset', name=value )
    '''
    nim_asset = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_asset", nim_asset )
    if success:
        nim.set_name( elem='asset', name=nim_asset.Get() )
        P.error('Reading nim_asset')
    else:
        P.error('Failed reading nim_asset')
    
    #  Asset ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_assetID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_assetID' )
        P.debug( 'Asset ID = %s' % value )
        nim.set_ID( elem='asset', ID=value )
    '''
    nim_assetID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_assetID", nim_assetID )
    if success:
        nim.set_ID( elem='asset', ID=nim_assetID.Get() )
        P.error('Reading nim_assetID')
    else:
        P.error('Failed reading nim_assetID')
    
    #  File ID :
    '''
    if mc.attributeQuery( 'defaultRenderGlobals.nim_fileID' ) :
        value=mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals' )
        P.debug( 'Class = %s' % value )
        nim.set_tab( tab=value )
    '''
    #TODO: Check if Maya code is error or intentional
    nim_fileID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_fileID", nim_fileID )
    if success:
        #nim.set_ID( elem='file', ID=nim_fileID.Get() )
        #nim.set_tab( tab=nim_fileID.Get() )
        #P.error('Reading nim_fileID')
        pass
    else:
        P.error('Failed reading nim_fileID')

    
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
    nim_name = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_name", nim_name )
    if success:
        if nim.tab()=='SHOT' :
            P.debug( 'Shot Name = %s' % nim_name.Get() )
            #nim.set_tab( nim_name.Get() )
        elif nim.tab()=='ASSET' :
            P.debug( 'Asset Name = %s' % nim_name.Get() )
            #nim.set_tab( nim_name.Get() )
    else:
        P.error('Failed reading nim_name')


    #  Basename :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_basename' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_basename' )
        P.debug( 'Basename = %s' % value )
        nim.set_name( elem='base', name=value )
    
    '''
    nim_basename = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_basename", nim_basename )
    if success:
        nim.set_name( elem='base', name=nim_basename.Get() )
        P.error('Reading nim_basename')
    else:
        P.error('Failed reading nim_basename')


    #  Task :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_type' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_type' )
        P.debug( 'Task = %s' % value )
        nim.set_name( elem='task', name=value )
    
    '''
    nim_type = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_type", nim_type )
    if success:
        nim.set_name( elem='task', name=nim_type.Get() )
        P.error('Reading nim_type')
    else:
        P.error('Failed reading nim_type')


    #  Task ID :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_typeID' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeID' )
        P.debug( 'Task ID = %s' % value )
        nim.set_ID( elem='task', ID=value )
    
    '''
    nim_typeID = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_typeID", nim_typeID )
    if success:
        nim.set_ID( elem='task', ID=nim_typeID.Get() )
        P.error('Reading nim_typeID')
    else:
        P.error('Failed reading nim_typeID')

    
    #  Task Folder :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_typeFolder' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_typeFolder' )
        P.debug( 'Task Folder = %s' % value )
        nim.set_taskFolder( folder=value )
    
    '''
    nim_typeFolder = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_typeFolder", nim_typeFolder )
    if success:
        nim.set_taskFolder( folder=nim_typeFolder.Get() )
        P.error('Reading nim_typeFolder')
    else:
        P.error('Failed reading nim_typeFolder')
    
    #  Tag :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_tag' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_tag' )
        P.debug( 'Tag = %s' % value )
        nim.set_name( elem='tag', name=value )
    
    '''
    nim_tag = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_tag", nim_tag )
    if success:
        nim.set_name( elem='tag', name=nim_tag.Get() )
        P.error('Reading nim_tag')
    else:
        P.error('Failed reading nim_tag')
    
    #  File Type :
    '''
    if mc.objExists( 'defaultRenderGlobals.nim_fileType' ) :
        value=mc.getAttr( 'defaultRenderGlobals.nim_fileType' )
        P.debug( 'File Type = %s' % value )
        nim.set_name( elem='file', name=value )
    '''
    nim_fileType = MaxPlus.FPValue()
    success = MaxPlus.Core.EvalMAXScript("rootNodeDataCA.nim_fileType", nim_fileType )
    if success:
        nim.set_name( elem='file', name=nim_fileType.Get() )
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
    mpPM = MaxPlus.PathManager
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
            mpPM.SetProjectFolderDir( pathToSet )
            P.info( 'nim_3dsmax - Current Project Set: %s\n' % pathToSet )
        else :
            P.info('Project not set!')
    except : pass
    
    return True
    



#  End

