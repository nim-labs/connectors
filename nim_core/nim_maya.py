#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_maya.py
# Version:  v4.0.27.190418
#
# Copyright (c) 2014-2019 NIM Labs LLC
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
#  Maya Imports :
import maya.cmds as mc
import maya.mel as mm
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
            print "NIM: Failed to load UI Modules - Maya"

#  Variables :
version='v4.0.27'
winTitle='NIM_'+version

def get_mainWin() :
    'Returns the name of the main Maya window'
    import maya.OpenMayaUI as omUI
    #from PySide import QtGui
    try : 
        from PySide2 import QtWidgets as QtGui
    except ImportError :
        try : 
            from PySide import QtGui
        except ImportError :
            pass
    try:
        from shiboken2 import wrapInstance
    except ImportError :
        from shiboken import wrapInstance
    #  Get the main maya window as a QMainWindow instance :
    mayaWin=wrapInstance( long( omUI.MQtUtil.mainWindow() ), QtGui.QWidget )
    return mayaWin

def set_vars( nim=None ) :
    'Add variables to Maya Render Globals'
    
    mc.undoInfo(openChunk=True)

    P.info( '\nSetting Render Globals variables...' )
    
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
    
    mc.undoInfo(closeChunk=True)
    return


def get_vars( nim=None ) :
    'Gets NIM settings from the defaultRenderGlobals node in Maya.'
    
    mc.undoInfo(openChunk=True)

    P.info('Getting information from NIM attributes on the defaultRenderGlobals node...')
    
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
    if mc.attributeQuery( 'defaultRenderGlobals.nim_fileID' ) :
        value=mc.attributeQuery( 'nim_fileID', node='defaultRenderGlobals' )
        P.debug( 'Class = %s' % value )
        nim.set_tab( tab=value )
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
    mc.undoInfo(closeChunk=True)
    return

#DEPRICATED
def mk_workspace( renPath='' ) :
    'Creates the NIM Project Workspace'
    
    workspace='//NIM Project Workspace File\n\n'
    workspace +='workspace -fr "scene" "scenes";\n'
    workspace +='workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";\n'
    workspace +='workspace -fr "eps" "data";\n'
    workspace +='workspace -fr "mel" "scripts";\n'
    workspace +='workspace -fr "particles" "cache/particles";\n'
    workspace +='workspace -fr "STEP_DC" "data";\n'
    workspace +='workspace -fr "CATIAV5_DC" "data";\n'
    workspace +='workspace -fr "sound" "sound";\n'
    workspace +='workspace -fr "furFiles" "renderData/fur/furFiles";\n'
    workspace +='workspace -fr "depth" "renderData/depth";\n'
    workspace +='workspace -fr "CATIAV4_DC" "data";\n'
    workspace +='workspace -fr "autoSave" "autosave";\n'
    workspace +='workspace -fr "diskCache" "data";\n'
    workspace +='workspace -fr "fileCache" "cache/nCache";\n'
    workspace +='workspace -fr "IPT_DC" "data";\n'
    workspace +='workspace -fr "SW_DC" "data";\n'
    workspace +='workspace -fr "DAE_FBX export" "data";\n'
    workspace +='workspace -fr "Autodesk Packet File" "data";\n'
    workspace +='workspace -fr "DAE_FBX" "data";\n'
    workspace +='workspace -fr "DXF_DCE" "data";\n'
    workspace +='workspace -fr "mayaAscii" "scenes";\n'
    workspace +='workspace -fr "iprImages" "renderData/iprImages";\n'
    workspace +='workspace -fr "move" "data";\n'
    workspace +='workspace -fr "mayaBinary" "scenes";\n'
    workspace +='workspace -fr "fluidCache" "cache/nCache/fluid";\n'
    workspace +='workspace -fr "clips" "clips";\n'
    workspace +='workspace -fr "templates" "assets";\n'
    workspace +='workspace -fr "DWG_DC" "data";\n'
    workspace +='workspace -fr "offlineEdit" "scenes/edits";\n'
    workspace +='workspace -fr "translatorData" "data";\n'
    workspace +='workspace -fr "DXF_DC" "data";\n'
    workspace +='workspace -fr "renderData" "renderData";\n'
    workspace +='workspace -fr "SPF_DCE" "data";\n'
    workspace +='workspace -fr "ZPR_DCE" "data";\n'
    workspace +='workspace -fr "furShadowMap" "renderData/fur/furShadowMap";\n'
    workspace +='workspace -fr "audio" "sound";\n'
    workspace +='workspace -fr "IV_DC" "data";\n'
    workspace +='workspace -fr "scripts" "scripts";\n'
    workspace +='workspace -fr "STL_DCE" "data";\n'
    workspace +='workspace -fr "furAttrMap" "renderData/fur/furAttrMap";\n'
    workspace +='workspace -fr "FBX export" "data";\n'
    workspace +='workspace -fr "JT_DC" "data";\n'
    workspace +='workspace -fr "sourceImages" "sourceimages";\n'
    workspace +='workspace -fr "DWG_DCE" "data";\n'
    workspace +='workspace -fr "FBX" "data";\n'
    workspace +='workspace -fr "movie" "movies";\n'
    workspace +='workspace -fr "Alembic" "data";\n'
    workspace +='workspace -fr "furImages" "renderData/fur/furImages";\n'
    workspace +='workspace -fr "IGES_DC" "data";\n'
    workspace +='workspace -fr "illustrator" "data";\n'
    workspace +='workspace -fr "furEqualMap" "renderData/fur/furEqualMap";\n'
    workspace +='workspace -fr "UG_DC" "data";\n'
    #  Add render images directory :
    if not renPath :
        workspace +='workspace -fr "images" "images";\n'
    else :
        renPath=renPath.replace('\\', '/')
        workspace +='workspace -fr "images" "'+renPath+'";\n'
    workspace +='workspace -fr "SPF_DC" "data";\n'
    workspace +='workspace -fr "PTC_DC" "data";\n'
    workspace +='workspace -fr "OBJ" "data";\n'
    workspace +='workspace -fr "CSB_DC" "data";\n'
    workspace +='workspace -fr "STL_DC" "data";\n'
    workspace +='workspace -fr "IGES_DCE" "data";\n'
    workspace +='workspace -fr "shaders" "renderData/shaders";\n'
    workspace +='workspace -fr "UG_DCE" "data";\n'
    
    return workspace

#DEPRICATED
def mk_proj( path='', renPath='' ) :
    'Creates a show project structure'
    workspaceExists=False
    
    #  Variables :
    projDirs=['assets', 'autosave', 'cache', 'cache/nCache', 'cache/nCache/fluid',
        'cache/particles', 'clips', 'data', 'images', 'movies', 'renderData',
        'renderData/depth', 'renderData/fur', 'renderData/fur/furAttrMap', 'renderData/fur/furEqualMap',
        'renderData/fur/furFiles', 'renderData/fur/furImages', 'renderData/fur/furShadowMap',
        'renderData/iprImages', 'renderData/shaders', 'scenes','scenes/edits', 'scripts', 'sound',
        'sourceimages', 'sourceimages/3dPaintTextures']
    
    #  Create Maya project directories :
    path=os.path.normpath(path)
    if os.path.isdir( path ) :
        P.info('Creating Project Folders...')
        for projDir in projDirs:
            _dir=os.path.normpath( os.path.join( path, projDir ) )
            if not os.path.isdir( _dir ) :
                try : os.mkdir( _dir )
                except Exception, e :
                    P.error( 'Failed creating the directory: %s' % _dir )
                    P.error( '    %s' % traceback.print_exc() )
                    return False
        P.info('Complete')

    #  Check for workspace file :
    workspaceFile=os.path.normpath( os.path.join( path, 'workspace.mel' ) )
    if os.path.exists( workspaceFile ) :
        workspaceExists=True
        P.info('Workspace exists!')


    #  Create workspace file :
    if not workspaceExists :
        P.info('Creating Maya workspace.mel file...')
        workspace_text=mk_workspace( renPath )
        #P.info(workspace_text)
        workspace_file=open( workspaceFile, 'w' )
        workspace_file.write( workspace_text )
        workspace_file.close
        P.info('Complete')

        #  Write out the render path :
        if renPath and os.path.isdir( renPath ) :
            try :
                nim_file=open( os.path.join(path,'nim.mel'),'w')
                nim_file.write( renPath )
                nim_file.close
            except : P.info( 'Sorry, unable to write the nim.mel file' )


    #  Set Project
    try :
        P.info('Setting Project...')
        pathToSet=path.replace('\\', '/')
        if os.path.isdir( pathToSet ) :
            mm.eval( 'setProject "%s"' % pathToSet )
            #mc.workspace( pathToSet, o=True)
            P.info( 'nim_maya: Current Project Set: %s\n' % pathToSet )
        else :
            P.info('Project not set!')
    except : pass



    return True


def makeProject(projectLocation='', renderPath='') :
    'Create the new project and workspace setup'

    createDirectories = True

    # Get list of all standard file rules
    fileRules = mm.eval('np_getDefaultFileRuleWidgets')
    try:
        #Update with NIM Render Directory
        if renderPath:
            imageRuleIndex=fileRules.index(u'images'.replace('\\','/'))
            fileRules[imageRuleIndex+1]=unicode(renderPath)
    except:
        P.error('Could not set NIM render path in workspace.')

    mc.workspace( projectLocation, openWorkspace=True )

    if createDirectories :
        print "Creating Directories";
        # Set workspace current directory to the workspace root so relative paths created with -create are located correctly
        mc.workspace( dir=mc.workspace(q=True,rootDirectory=True) )

    items=len(fileRules)
    for i in range(0 ,items-1, 2) :
        # each rule has 2 entries: rulename, value
        ruleName  = fileRules[i]
        ruleValue = fileRules[i+1]
        mc.workspace(fr=(ruleName,ruleValue))
        if createDirectories :
            mc.workspace(create=ruleValue)

    #Adding images folder to project
    mc.workspace(create='images')

    mc.workspace(saveWorkspace=True)
    mc.workspace(projectLocation,o=True)
    mm.eval('if (`window -ex projectWindow`){print "Window Open"; deleteUI projectWindow;projectWindow;}')
    mm.eval('np_resetBrowserPrefs;');

    return True


class Pub_Chex( QtGui.QWidget ) :
    
    def __init__( self, parent=None, nim=None ) :
        super(Pub_Chex, self).__init__(parent)
        self.setWindowTitle( 'Maya Publish Checks' )
        
        #  Widgets :
        
        #  Check Boxes :
        self.delUnselected=QtGui.QCheckBox()
        self.applyShaders=QtGui.QCheckBox()
        self.delUnusedShaders=QtGui.QCheckBox()
        self.delHist=QtGui.QCheckBox()
        #self.delNonDeformerHist=QtGui.QCheckBox()
        #  Set check boxes :
        self.delUnusedShaders.setChecked( True )
        self.delHist.setChecked( True )
        #  Store all check boxes :
        self.checkBoxes=[self.delUnselected, self.applyShaders,
            self.delUnusedShaders, self.delHist]
        
        #  Combo Boxes :
        self.delDeformers=QtGui.QComboBox()
        self.delConns=QtGui.QComboBox()
        self.delCurves=QtGui.QComboBox()
        self.delLocs=QtGui.QComboBox()
        self.delCams=QtGui.QComboBox()
        self.delIPlanes=QtGui.QComboBox()
        self.delLights=QtGui.QComboBox()
        self.delDispLayers=QtGui.QComboBox()
        self.delRenLayers=QtGui.QComboBox()
        #  Store all combo boxes :
        self.comboBoxes=[self.delDeformers, self.delConns, self.delCurves, self.delLocs,
            self.delCams, self.delIPlanes, self.delLights, self.delDispLayers, self.delRenLayers]
        #  Populate combo boxes :
        for comboBox in self.comboBoxes :
            comboBox.addItems( ['All', 'Unselected', 'None'] )
        
        #  Buttons :
        self.btn_sel=QtGui.QPushButton('Select All')
        self.btn_unsel=QtGui.QPushButton('Select None')
        self.btn_1=QtGui.QPushButton('Run Checks + Publish')
        self.btn_2=QtGui.QPushButton('Run Checks ONLY')
        #  Button Layouts :
        self.selBtnLayout=QtGui.QHBoxLayout()
        self.selBtnLayout.addWidget( self.btn_sel )
        self.selBtnLayout.addWidget( self.btn_unsel )
        self.btnLayout=QtGui.QHBoxLayout()
        self.btnLayout.addWidget( self.btn_1 )
        self.btnLayout.addWidget( self.btn_2 )
        
        #  Form Layout :
        self.form_layout=QtGui.QFormLayout()
        #  Add check boxes to layout :
        self.form_layout.addRow( 'Delete Un-selected Geometry:', self.delUnselected )
        self.form_layout.addRow( 'Delete Un-used Shaders:', self.delUnusedShaders )
        self.form_layout.addRow( 'Apply Default Shader:', self.applyShaders )
        self.form_layout.addRow( 'Delete History:', self.delHist )
        #  Add combo boxes to layout :
        self.form_layout.addRow( 'Delete Deformers:', self.delDeformers )
        self.form_layout.addRow( 'Delete Constraints:', self.delConns )
        self.form_layout.addRow( 'Delete Curves:', self.delCurves )
        self.form_layout.addRow( 'Delete Locators:', self.delLocs )
        self.form_layout.addRow( 'Delete Camers:', self.delCams )
        self.form_layout.addRow( 'Delete Image Planes:', self.delIPlanes )
        self.form_layout.addRow( 'Delete Lights:', self.delLights )
        self.form_layout.addRow( 'Delete Display Layers:', self.delDispLayers )
        self.form_layout.addRow( 'Delete Render Layers:', self.delRenLayers )
        
        #  Main Layout :
        self.layout=QtGui.QVBoxLayout( self )
        self.layout.addLayout( self.form_layout )
        self.layout.addLayout( self.selBtnLayout )
        self.layout.addLayout( self.btnLayout )
        
        #  Connections :
        self.btn_sel.clicked.connect( self.sel )
        self.btn_unsel.clicked.connect( self.unsel )
        self.btn_1.clicked.connect( lambda: self.run_checks( nim=nim, pub=True ) )
        self.btn_2.clicked.connect( lambda: self.run_checks( nim=nim, pub=False ) )
        
        #  Show the Window :
        self.show()
        
        return
    
    
    def sel(self) :
        'Turns on all check and combo boxes.'
        #  Set Check Boxes :
        for cb in self.checkBoxes :
            cb.setChecked( True )
        #  Set Combo Boxes :
        for cb in self.comboBoxes :
            cb.setCurrentIndex( 0 )
        return
    
    
    def unsel(self) :
        'Turns off all check and combo boxes.'
        #  Set Check Boxes :
        for cb in self.checkBoxes :
            cb.setChecked( False )
        #  Set Combo Boxes :
        for cb in self.comboBoxes :
            cb.setCurrentIndex( 2 )
        return
    
    
    def run_checks( self, pub=False, nim=None) :
        'Runs the checks with the values from the publish check window'
        
        #  Run publishing checks :
        self.pub_check()
        '''
            del_unselected=self.delUnselected,
            del_unusedShaders=self.delUnusedShaders, applyDefaultShaders=self.applyShaders,
            del_hist=self.delHist, deformer_opt=self.delDeformers.currentText(),
            conn_opt=self.delConns.currentText(), curves_opt=self.delCurves.currentText(),
            loc_opt=self.delLocs, cam_opt=self.delCams.currentText(),
            ip_opt=self.delIPlanes.currentText(), light_opt=self.delLights.currentText(),
            dl_opt=self.delDispLayers.currentText(), rl_opt=self.delRenLayers.currentText() )
        '''
        #  Version Up, Publish and Close the Window, if specified :
        if pub :
            if not nim :
                nim=Nim.NIM()
            Api.versionUp( nim=self.nim, win_launch=False, pub=True )
            self.close()
        
        return
    
    
    def pub_check(self) :
        'Cleans up a Maya file before publishing'
        
        #  Selection :
        sel=mc.ls( sl=True, long=True, transforms=True )
        #  Select entire hierarchy :
        if sel :
            hier=mc.listRelatives( sel, children=True, allDescendents=True, type='transform',
                fullPath=True )
            if hier :
                sel.extend( hier )
        
        
        #  Variables :
        #===------------
        
        non_linears=['deformBend','deformFlare','deformSine','deformSquash','deformTwist','deformWave']
        constraints=['pointConstraint', 'aimConstraint', 'orientConstraint', 'scaleConstraint', 'parentConstraint', \
            'geometryConstraint', 'normalConstraint', 'tangentConstraint', 'pointOnPolyConstraint']
        mayaLights=['ambientLight', 'directionalLight', 'areaLight', 'pointLight', 'spotLight', 'volumeLight']
        vrayLights=['VRayLightSphereShape', 'VRayLightDomeShape', 'VRayLightRectShape', 'VRayLightIESShape']
        
        
        #  Delete :
        #===-------
        
        #  Delete Unselected Geometry :
        if self.delUnselected.isChecked() :
            P.info('Deleting unselected geometry...')
            delGeo=[]
            objs=sel[:]
            allGeo=mc.listRelatives( mc.ls( geometry=True ), parent=True, fullPath=True )
            for obj in sel :
                prnts=mc.listRelatives( obj, allParents=True, fullPath=True )
                if prnts :
                    prnt=prnts[0]
                    while prnts :
                        objs.extend( prnts )
                        prnts=mc.listRelatives( prnt, allParents=True, fullPath=True )
                        if prnts : prnt=prnts[0]
            delGeo=[x for x in allGeo if x not in objs]
            mc.delete( delGeo )
            P.info('    Unselected geometry deleted successfully.')
        
        #  Apply Default Shader :
        if self.applyShaders.isChecked() :
            P.info('Applying default shaders...')
            mc.select( all=True )
            mm.eval( 'hyperShade -assign initialShadingGroup' )
            mc.select( sel, replace=True )
            P.info('    Default shaders applied successfully.')
        
        #  Delete Unused Shaders :
        if self.delUnusedShaders.isChecked() :
            P.info('Deleting unused shaders...')
            mm.eval( 'hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")' )
            P.info('    Unused shaders have been deleted successfully.')
        
        #  Delete history :
        if self.delHist.isChecked() :
            P.info( 'Deleteing all history...' )
            mm.eval( 'DeleteAllHistory' )
            P.info('    All history deleted successfully.')
        
        
        #  Clean File :
        #===-------------
        
        #  Delete Deformers :
        
        if self.delDeformers.currentText()=='All' :
            P.info( 'Deleting all deformers...' )
            #  FFD's :
            P.info('    Deleting FFDs...')
            try : mc.delete( mc.ls( type='ffd' ) )
            except : P.info('      No FFDs found.')
            #  Lattices :
            P.info( '    Deleting Latices...' )
            try : mc.delete( mc.ls( type='lattice' ) )
            except : P.info('      No Lattices found.')
            #  Clusters :
            P.info('    Deleting clusters...')
            try : mc.delete( mc.ls( type='cluster' ) )
            except : P.info('      No Clusters found.')
            #  Sculpt Deformers :
            P.info('    Deleting Sculpts...')
            try : mm.eval('DeleteAllSculptObjects')
            except : P.info('      No Sculpts found.')
            #  Non-Linear Deformers :
            P.info('    Deleting non-linear deformers...')
            try : mm.eval('DeleteAllNonLinearDeformers')
            except : P.info('      No non-linear deformers found.')
            #  Wire Defomers :
            P.info('    Deleting Wires...')
            try :mc.delete( mc.ls( type='wire' ) )
            except : P.info('      No Wires found.')
        elif self.delDeformers.currentText()=='Unselected' :
            delDeformers=[]
            deformers=['lattice','cluster','wire']
            for deformer in deformers :
                obj_deformers=mc.ls( type=deformer, long=True )
                if obj_deformers :
                    for obj_deformer in obj_deformers :
                        if deformer=='lattice' :
                            allDeformers=mc.listRelatives( obj_deformer, parent=True, type='transform',
                                fullPath=True )
                            if allDeformers :
                                for obj in allDeformers :
                                    if obj not in sel :
                                        delDeformers.append( obj )
                        elif deformer=='cluster' :
                            connections=mc.listConnections( obj_deformer, type='transform' )
                            for conn in connections :
                                cls_long=mc.ls( conn, long=True )
                                if cls_long :
                                    if cls_long[0] not in sel :
                                        delDeformers.append( obj_deformer )
                        else :
                            if obj_deformer not in sel :
                                delDeformers.append( obj_deformer )
            if delDeformers :
                mc.delete( delDeformers )
            
            '''
            P.info('    Deleteing Un-selected Deformers...')
            for deformer in deformers :
                try :
                    mc.select( mc.ls( type=deformer ) )
                    for obj in sel :
                        mc.select( obj, d=True )
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    mc.delete()
                except : P.info( '  No un-sel deformers found' )
            #  Try deleting un-necessary implicit spheres :
            try :
                mc.select( mc.ls( type='implicitSphere' ) )
                for select in sel :
                    mc.select( select, d=True )
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    P.info( 'Deleting un-necessary implicit spheres...' )
                    mc.delete()
            except : P.info( '  No un-sel implicit spheres found' )
            #  Try deleting non-linears :
            try :
                for non_linear in non_linears :
                    mc.select( mc.ls( type=non_linear ) )
                    for select in sel :
                        mc.select( select, d=True )
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    P.info( 'Deleting un-necessary non-linears...' )
                    mc.delete()
            except : P.info( '  No un-sel non-linears found' )
        
        #  Delete Constraints :
        if conn_opt=='All' :
            P.info( 'Deleteing all constraints....' )
            mm.eval('DeleteAllConstraints')
        elif conn_opt=='Unsel' :
            P.info( 'Deleting un-sel constraints....' )
            try :
                for constraint in constraints :
                    mc.select( mc.ls( type=constraint ) )
                    for select in sel :
                        mc.select( select, d=True )
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    mc.delete()
            except :
                P.info( '  No constraints found' )
        
        #  Delete Curves :
        if curves_opt=='All' :
            try :
                mc.select( mc.ls( type='nurbsCurve' ) )
                mc.select( mc.ls( type='bezierCurve' ), add=True )
                mc.select( ms.ls( transforms=True, sl=True) )
                P.info( 'Deleteing all curves....' )
                mc.delete()
            except :
                P.info( '  No curves found' )
        elif curves_opt=='Unsel' :
            try :
                mc.select( mc.ls( type='nurbsCurve' ) )
                mc.select( mc.ls( type='bezierCurve' ), add=True )
                for select in sel :
                    mc.select( select, d=True )
                mc.select( mc.ls( transforms=True, sl=True ) )
                P.info( 'Deleting un-sel curves....' )
                mc.delete()
            except :
                P.info( '  No curves found' )
        
        #  Delete Locators :
        #TO DO -> Make sure locators don't have any connections.
        if loc_opt=='All' :
            try :
                mc.select( mc.ls( type='locator' ) )
                mc.select( ms.ls( transforms=True, sl=True ) )
                P.info( 'Deleteing all locators....' )
                mc.delete()
            except :
                P.info( '  No Locators Found' )
        elif loc_opt=='Unsel' :
            try :
                mc.select( mc.ls( type='locator' ) )
                for select in sel :
                    mc.select( select, d=True )
                mc.select( mc.ls( transforms=True, sl=True ) )
                P.info( 'Deleting un-sel locators....' )
                mc.delete()
            except :
                P.info( '  No locators found' )
        
        #  Delete Cameras :
        if cam_opt=='All' :
            P.info( 'Deleteing all cameras....' )
            mm.eval( 'DeleteAllCameras' )
        elif cam_opt=='Unsel' :
            try :
                mc.select( mc.ls( type='camera' ) )
                for select in sel :
                    mc.select( select, d=True )
                mc.select( mc.ls( transforms=True, sl=True ) )
                P.info( 'Deleting un-sel cameras....' )
                mc.delete()
            except :
                P.info( '  No cameras found' )
        
        #  Delete Imageplanes :
        if ip_opt=='All' :
            P.info( 'Deleteing all ImagePlanes....' )
            mm.eval( 'DeleteAllImagePlanes' )
        elif ip_opt=='Unsel' :
            try :
                mc.select( mc.ls( type='imagePlane' ) )
                for select in sel :
                    mc.select( select, d=True )
                mc.select( mc.ls( transforms=True, sl=True ) )
                P.info( 'Deleting un-sel ImagePlanes....' )
                mc.delete()
            except :
                P.info('  No ImagePlanes found')
            
        #  Delete Lights :
        if light_opt=='All' :
            P.info( 'Deleteing all lights....' )
            mm.eval( 'DeleteAllLights' )
            for vrayLight in vrayLights :
                try :
                    mc.select( mc.ls( type=vrayLight ) )		    
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    P.info( 'Deleting VRay lights...' )
                    mc.delete()
                except :
                    P.info( '  No '+vrayLight+' found' )
        elif light_opt=='Unsel' :
            P.info( 'Deleting un-sel lights....' )
            #  Delete Maya Lights :
            for mayaLight in mayaLights :
                try :
                    mc.select( mc.ls( type=mayaLight ) )
                    for select in sel :
                        mc.select( select, d=True )
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    P.info( '  Deleting Maya lights...' )
                    mc.delete()
                except :
                    P.info( '    No '+mayaLight+' found' )
            #  Delete VRay Lights :
            for vrayLight in vrayLights :
                try :
                    mc.select( mc.ls( type=vrayLight ) )
                    for select in sel :
                        mc.select( select, d=True )
                    mc.select( mc.ls( transforms=True, sl=True ) )
                    P.info( 'Deleting VRay lights...' )
                    mc.delete()
                except :
                    P.info( '  No '+vrayLight+' found' )
        
        #  Delete Display Layers :
        if dl_opt=='All' :
            try :
                mc.select( mc.ls( type='displayLayer' ) )
                P.info( 'Deleteing all display layers....' )
                mc.delete()
            except :
                P.info( '  No display layers found' )
        elif dl_opt=='Unsel' :
            try :
                mc.select( mc.ls( type='displayLayer' ) )
                for select in sel :
                    mc.select( select, d=True )
                mc.select( mc.ls( transforms=True, sl=True ) )
                P.info( 'Deleting un-sel display layers....' )
                mc.delete()
            except :
                P.info( '  No display layers found' )
        
        #  Delete Render Layers :
        if rl_opt=='All' :
            try :
                mc.select( mc.ls( type='renderLayer' ) )
                P.info( 'Deleteing all render layers....' )
                mc.delete()
            except :
                P.info( '  No render layers found' )
        elif rl_opt=='Unsel' :
            try :
                mc.select( mc.ls( type='renderLayer' ) )
                for select in sel :
                    mc.select( select, d=True )
                mc.select( mc.ls( transforms=True, sl=True ) )
                P.info( 'Deleting un-sel render layers....' )
                mc.delete()
            except:
                P.info( '  No render layers found' )
        
        #  Delete empty group nodes ?
        '''
        P.info( '\n\nThe file is clean!\n' )
        
        return


#  End of Class


#  Fix for Maya Shift loosing focus
class MainWindow(QtGui.QMainWindow):
    def keyPressEvent(self, event):
        """Override keyPressEvent to keep focus on QWidget in Maya."""
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.shift = True
            pass # make silent

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
class UIUtils(MayaQWidgetBaseMixin, QtGui.QWidget):
    """Base class for UI constructors."""

    def window(self):
        """Defines basic window parameters."""
        parent = self.get_maya_window()
        window = MainWindow(parent)

        return window

    def get_maya_window(self):
        """Grabs the Maya window."""
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)


#  End

