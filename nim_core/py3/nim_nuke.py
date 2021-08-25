#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_nuke.py
# Version:  v5.0.13.210825
#
# Copyright (c) 2014-2021 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import os, re, sys
#  NIM Imports :
from . import nim_api as Api
from . import nim_print as P
#  Nuke Imports :
import nuke, nukescripts

#  Import Python GUI packages :
try : 
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtGui as QtGui2
    from PySide2 import QtCore
except ImportError :
    try : 
        from PySide import QtCore, QtGui
    except ImportError :
        try : 
            from PyQt4 import QtCore, QtGui
        except ImportError : 
            try :
                from PyQt5 import QtWidgets as QtGui
                from PyQt5 import QtGui as QtGui2
                from PyQt5 import QtCore
            except :
                print("NIM: Failed to UI Modules - UI")


def get_mainWin() :
    'Returns the name of the main Nuke window'
    
    return

def _knobInfo( nim=None ) :
    'Returns a dictionary of information needed for creating custom NIM knobs in Nuke'
    userInfo=nim.userInfo()
    knobNames=( 'nim_tab', 'nim_server', 'nim_serverID', 'nim_user', 'nim_userID',
        'nim_job', 'nim_jobID', 'nim_asset', 'nim_assetID', 'nim_show', 'nim_showID',
        'nim_shot', 'nim_shotID', 'nim_basename', 'nim_task', 'nim_taskID', 'nim_taskFolder',
        'nim_compPath', 'nim_version' )
    knobLabels=( 'Tab', 'Server Path', 'Server ID', 'User Name', 'User ID',
        'Job Name', 'Job ID', 'Asset Name', 'Asset ID', 'Show Name', 'Show ID',
        'Shot Name', 'Shot ID', 'Basename', 'Task Name', 'Task ID', 'Task Folder',
        'Comp Path', 'Version' )
    knobCmds=( nim.tab(), nim.server(), nim.ID('server'), userInfo['name'], userInfo['ID'],
        nim.name('job'), nim.ID('job'), nim.name('asset'), nim.ID('asset'), nim.name('show'),
        nim.ID('show'), nim.name('shot'), nim.ID('shot'), nim.name('base'), nim.name('task'),
        nim.ID('task'), nim.taskFolder(), nim.compPath(), nim.version() )
    return ( knobNames, knobLabels, knobCmds )

def set_vars( nim=None ) :
    'Sets the environment variables inside of Nuke, for Deadline to pick up'
    
    P.info( 'Setting Nuke Vars...' )
    
    tabName='NIM'
    knobInfo=_knobInfo( nim )
    knobNames, knobLabels, knobCmds=knobInfo[0], knobInfo[1],knobInfo[2]
    #  Get Project Settings Node :
    PS=nuke.root()
    
    #  Create NIM Tab, if it doesn't exist :
    if not PS.knob( tabName ) :
        PS.addKnob( nuke.Tab_Knob( tabName ) )
    
    #  Create Knobs :
    for x in range(len(knobNames)) :
        if not PS.knob( knobNames[x] ) :
            PS.addKnob( nuke.String_Knob( knobNames[x], knobLabels[x] ) )
        #  Set Knob :
        P.debug( '%s - %s' % (knobNames[x], knobCmds[x]) )
        knob=PS.knob( knobNames[x] )
        knob.setEnabled( True )
        if knobCmds[x] :
            #  Convert backslashes to forwardslashes for Nuke :
            if knobNames[x]=='nim_compPath' :
                correctedPath=knobCmds[x].replace( '\\', '/' )
                knob.setValue( correctedPath )
            #  Otherwise, set the knob as normal :
            else :
                knob.setValue( knobCmds[x] )
        knob.setEnabled( False )
    
    P.info( '    Done setting Nuke Vars.' )
    
    return

def get_vars( nim=None ) :
    'Populates a NIM dictionary with settings from custom NIM Nuke knobs'
    
    knobInfo=_knobInfo( nim )
    knobNames, knobLabels, knobCmds=knobInfo[0], knobInfo[1],knobInfo[2]
    #  Get Project Settings Node :
    PS=nuke.root()
    
    #  Get knob values :
    for x in range(len(knobNames)) :
        if knobNames[x] in list(PS.knobs().keys()) :
            if PS.knob( knobNames[x] ) :
                knob=PS.knob( knobNames[x] )
                #  Tab :
                if knobNames[x]=='nim_tab' :
                    nim.set_tab( _type=knob.value() )
                #  Server :
                elif knobNames[x]=='nim_server' :
                    nim.set_server( path=knob.value() )
                #  Server ID :
                elif knobNames[x]=='nim_serverID' :
                    nim.set_ID( elem='server', ID=knob.value() )
                #  User :
                elif knobNames[x]=='nim_user' :
                    nim.set_user( userName=knob.value() )
                elif knobNames[x]=='nim_userID' :
                    nim.set_userID( userID=knob.value() )
                #  Job :
                elif knobNames[x]=='nim_job' :
                    nim.set_name( elem='job', name=knob.value() )
                elif knobNames[x]=='nim_jobID' :
                    nim.set_ID( elem='job', ID=knob.value() )
                #  Asset :
                elif knobNames[x]=='nim_asset' :
                    nim.set_name( elem='asset', name=knob.value() )
                elif knobNames[x]=='nim_assetID' :
                    nim.set_ID( elem='asset', ID=knob.value() )
                #  Show :
                elif knobNames[x]=='nim_show' :
                    nim.set_name( elem='show', name=knob.value() )
                elif knobNames[x]=='nim_showID' :
                    nim.set_ID( elem='show', ID=knob.value() )
                #  Shot :
                elif knobNames[x]=='nim_shot' :
                    nim.set_name( elem='shot', name=knob.value() )
                elif knobNames[x]=='nim_shotID' :
                    nim.set_ID( elem='shot', ID=knob.value() )
                #  Basename :
                elif knobNames[x]=='nim_basename' :
                    nim.set_name( elem='base', name=knob.value() )
                #  Task :
                elif knobNames[x]=='nim_task' :
                    nim.set_name( elem='task', name=knob.value() )
                elif knobNames[x]=='nim_taskID' :
                    nim.set_ID( elem='task', ID=knob.value() )
                elif knobNames[x]=='nim_taskFolder' :
                    nim.set_taskFolder( folder=knob.value() )
                #  Comp Path :
                elif knobNames[x]=='nim_compPath' :
                    nim.set_compPath( compPath=knob.value() )
                #  Version :
                elif knobNames[x]=='nim_version' :
                    nim.set_version( version=knob.value() )
    
    return nim


def print_vars() :
    ''
    
    return

def rndr_mkDir() :
    'Creates the output path for images, if not already existant'
    
    if rndr_dir :
        if not os.path.exists( rndr_dir ) :
            os.makedirs( rndr_dir )
    
    '''
    views=nuke.views()
    file=nuke.filename( nuke.thisNode() )
    dir=os.path.dirname( file )
    osdir=nuke.callbacks.filenameFilter( dir )
    viewdirs=[]
    
    try:
        #  Replacing %V with view name :
        if re.search('%V', dir).group():
            for v in views :
                viewdirs.append(re.sub('%V', v, dir))
    except :
        pass
    
    if len(viewdirs)==0 :
        osdir=nuke.callbacks.filenameFilter(dir)
        if not os.path.isdir( osdir ) :
            os.makedirs( osdir )
    else :
        for vd in viewdirs :
            osdir = nuke.callbacks.filenameFilter( vd )
            if not os.path.isdir(osdir) :
                os.makedirs (osdir)
                print 'Directory (with viewname) created: %s' % (osdir)
    
    #nuke.addBeforeRender(createWriteDir)
    '''
    return



#  Create Custom NIM Node :
#===-----------------------------------

class NIM_Node() :
    
    def __init__( self, nodeType='read' ) :
        'Creates a custom NIM Read/Write node'
        
        if nodeType.lower() in ['write'] :
            nodeType='Write'
            nodeName='NIM_WriteNode'
        elif nodeType.lower() in ['read'] :
            nodeType='Read'
            nodeName='NIM_ReadNode'
        
        P.info( '\nCreating %s node\n' % nodeType )
        
        #  Create node :
        node=nuke.createNode( nodeType )
        
        count=1
        #  Get unique node name :
        while nuke.exists( '%s_%03d' % ( nodeName, count ) ) :
            count +=1
        node.knob( 'name' ).setValue( '%s_%03d' % ( nodeName, count ) )
        
        #  Create a Tab :
        tab=nuke.Tab_Knob( 'NIM' )
        node.addKnob( tab )
        
        self.nim={}
        #  Initialize the main dictionary :
        self.elements=['job', 'show', 'shot', 'task', 'base', 'ver']
        for elem in self.elements :
            elemDict={}
            elemDict['name']=''
            elemDict['ID']=None
            elemDict['IDs']=[]
            elemDict['list']=[]
            elemDict['input']=None
            self.nim[elem]=elemDict
        
        #  Add custom knobs :
        self.nim['job']['input']=nuke.Enumeration_Knob( 'job_input', 'Job:', \
            ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'] )
        self.nim['show']['input']=nuke.Enumeration_Knob( 'show_input', 'Show:', \
            ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'] )
        self.nim['shot']['input']=nuke.Enumeration_Knob( 'shot_input', 'Shot:', \
            ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'] )
        self.nim['task']['input']=nuke.Enumeration_Knob( 'task_input', 'Task:', \
            ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'] )
        self.nim['base']['input']=nuke.Enumeration_Knob( 'base_input', 'Basename:', \
            ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'] )
        self.nim['ver']['input']=nuke.Enumeration_Knob( 'ver_input', 'Version', \
            ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'] )
        
        #  Add knobs to tab :
        for knob in [self.nim['job']['input'], self.nim['show']['input'], self.nim['shot']['input'], self.nim['task']['input'], \
            self.nim['base']['input'], self.nim['ver']['input']] :
            node.addKnob( knob )
        
        self.elem_populate( 'job' )
        self.elem_populate( 'show' )
        self.elem_populate( 'shot' )
        self.elem_populate( 'task' )
        self.elem_populate( 'base' )
        self.elem_populate( 'ver' )
        
        #  Hook up knobs :
        nuke.addKnobChanged( self.knob_changed )
        
        return
    
    
    def elem_populate( self, elem='' ) :
        'Populates each of the combo boxes, when specified'
        
        if elem is not 'job' :
            prevElem=self.elements[self.elements.index(elem)-1]
        
        if elem=='job' :
            #  Get jobs :
            jobs=Api.get_jobs()
            if jobs and len(jobs) :
                P.log( 'Jobs Dictionary = %s' % jobs ) 
                #  List of IDs will always be one behind index of 'list', due to "Select..." :
                self.nim[elem]['list'].append( 'Select...' )
                for job in jobs :
                    self.nim[elem]['list'].append( job )
                    self.nim[elem]['IDs'].append( jobs[job] )
                #  Populate combo box :
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
            else :
                self.nim[elem]['IDs']=[]
                self.nim[elem]['list']=['None']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
        
        if elem=='show' :
            self.nim[prevElem]['name']=self.nim[prevElem]['list'][int(self.nim[prevElem]['input'].getValue())]
            if self.nim[prevElem]['name'] not in ['Select...', 'None', ''] :
                self.nim[prevElem]['ID']=self.nim[prevElem]['IDs'][int(self.nim[prevElem]['input'].getValue())-1]
                P.log( 'Job = %s, JobID = %s' % ( self.nim[prevElem]['name'], self.nim[prevElem]['ID'] ) )
                shows=Api.get_shows( self.nim[prevElem]['name'] )
                if shows and len(shows) :
                    P.log( 'Shows Dictionary = %s' % shows ) 
                    self.nim[elem]['list']=[]
                    self.nim[elem]['IDs']=[]
                    #  List of IDs will always be one behind index of 'list', due to "Select..." :
                    self.nim[elem]['list'].append( 'Select...' )
                    for show in shows :
                        self.nim[elem]['list'].append( show )
                        self.nim[elem]['IDs'].append( shows[show] )
                    #  Populate combo box :
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
                else :
                    self.nim[elem]['IDs']=[]
                    self.nim[elem]['list']=['None']
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
            else :
                self.nim[prevElem]['ID']=None
                self.nim[elem]['IDs']=[]
                self.nim[elem]['list']=['None']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                self.nim[elem]['input'].setValue(0)
        
        if elem=='shot' :
            self.nim[prevElem]['name']=self.nim[prevElem]['list'][int(self.nim[prevElem]['input'].getValue())]
            if self.nim[prevElem]['name'] not in ['Select...', 'None', ''] :
                self.nim[prevElem]['ID']=self.nim[prevElem]['IDs'][int(self.nim[prevElem]['input'].getValue())-1]
                P.log( 'Show = %s, ShowID = %s' % ( self.nim[prevElem]['name'], self.nim[prevElem]['ID'] ) )
                shots=Api.get_shots( self.nim[prevElem]['ID'] )
                if shots and len(shots) :
                    P.log( 'Shot Dictionary = %s' % shots ) 
                    self.nim[elem]['list']=[]
                    self.nim[elem]['IDs']=[]
                    #  List of IDs will always be one behind index of 'list', due to "Select..." :
                    self.nim[elem]['list'].append( 'Select...' )
                    for shot in shots :
                        self.nim[elem]['list'].append( shot['name'] )
                        self.nim[elem]['IDs'].append( shot['ID'] )
                    #  Populate combo box :
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
                else :
                    self.nim[elem]['IDs']=[]
                    self.nim[elem]['list']=['None']
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
            else :
                self.nim[prevElem]['ID']=None
                self.nim[elem]['IDs']=[]
                self.nim[elem]['list']=['None']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                self.nim[elem]['input'].setValue(0)
        
        if elem=='task' :
            self.nim[prevElem]['name']=self.nim[prevElem]['list'][int(self.nim[prevElem]['input'].getValue())]
            if self.nim[prevElem]['name'] not in ['Select...', 'None', ''] :
                self.nim[prevElem]['ID']=self.nim[prevElem]['IDs'][int(self.nim[prevElem]['input'].getValue())-1]
                P.log( 'Shot = %s, ShotID = %s' % ( self.nim[prevElem]['name'], self.nim[prevElem]['ID'] ) )
                self.nim[elem]['list']=['Comp']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                self.nim[elem]['input'].setValue(1)
            else :
                self.nim['show']['ID']=None
                self.nim[elem]['IDs']=[]
                self.nim[elem]['list']=['None']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                self.nim[elem]['input'].setValue(1)
        
        if elem=='base' :
            self.nim[prevElem]['name']=self.nim[prevElem]['list'][int(self.nim[prevElem]['input'].getValue())]
            if self.nim[prevElem]['name'] not in ['Select...', 'None', ''] :
                bases=Api.get_bases( shotID=self.nim['shot']['ID'], task='COMP' )
                if bases and len(bases) :
                    self.nim[elem]['list']=[]
                    if len(bases)>1 :
                        P.log( 'Basenames Dictionary = %s' % bases ) 
                        #  List of IDs will always be one behind index of 'list', due to "Select..." :
                        self.nim[elem]['list'].append( 'Select...' )
                        for base in bases :
                            self.nim[elem]['list'].append( base['basename'] )
                        #  Populate combo box :
                        self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                        self.nim[elem]['input'].setValue(0)
                    else :
                        self.nim[elem]['list']=[bases[0]['basename']]
                        self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                        self.nim[elem]['input'].setValue(0)
                else :
                    self.nim[elem]['IDs']=[]
                    self.nim[elem]['list']=['None']
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
            else :
                self.nim[prevElem]['ID']=None
                self.nim[elem]['IDs']=[]
                self.nim[elem]['list']=['None']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                self.nim[elem]['input'].setValue(0)
        
        if elem=='ver' :
            self.nim[prevElem]['name']=self.nim[prevElem]['list'][int(self.nim[prevElem]['input'].getValue())]
            if self.nim[prevElem]['name'] not in ['Select...', 'None', ''] :
                vers=Api.get_vers( shotID=self.nim['shot']['ID'], basename=self.nim['base']['name'] )
                if vers and len(vers) :
                    self.nim[elem]['list']=[]
                    #  List of IDs will always be one behind index of 'list', due to "Select..." :
                    self.nim[elem]['list'].append( 'Select...' )
                    for ver in vers :
                        print(ver)
                        if nuke.env['nc'] :
                            srch=re.search( '_[v]?[0-9]+.nknc$', ver['filename'] )
                        else :
                            srch=re.search( '_[v]?[0-9]+.nk$', ver['filename'] )
                        if srch :
                            verNum=re.search( '[0-9]+', srch.group() )
                            if verNum :
                                self.nim[elem]['list'].append( str(int(verNum.group())) )
                                self.nim[elem]['IDs'].append( ver['fileID'] )
                    #  Populate combo box :
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
                else :
                    self.nim[elem]['IDs']=[]
                    self.nim[elem]['list']=['None']
                    self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                    self.nim[elem]['input'].setValue(0)
            else :
                self.nim[prevElem]['ID']=None
                self.nim[elem]['IDs']=[]
                self.nim[elem]['list']=['None']
                self.nim[elem]['input'].setValues( self.nim[elem]['list'] )
                self.nim[elem]['input'].setValue(0)
        
        return
    
    
    def knob_changed( self ) :
        'Run every time a knob is manipulated.'
        
        if nuke.thisKnob()==self.nim['job']['input'] :
            self.elem_populate( 'show' )
            self.elem_populate( 'shot' )
            self.elem_populate( 'task' )
            self.elem_populate( 'base' )
            self.elem_populate( 'ver' )
        if nuke.thisKnob()==self.nim['show']['input'] :
            self.elem_populate( 'shot' )
            self.elem_populate( 'task' )
            self.elem_populate( 'base' )
            self.elem_populate( 'ver' )
        if nuke.thisKnob()==self.nim['shot']['input'] :
            self.elem_populate( 'task' )
            self.elem_populate( 'base' )
            self.elem_populate( 'ver' )
        if nuke.thisKnob()==self.nim['task']['input'] :
            self.elem_populate( 'base' )
            self.elem_populate( 'ver' )
        if nuke.thisKnob()==self.nim['base']['input'] :
            self.elem_populate( 'ver' )
        if nuke.thisKnob()==self.nim['ver']['input'] :
            pass
            #self.elem_populate( '' )
        
        nuke.callbacks.updateUI()
        
        return


#  Custom Windows :
#===------------------------

class Win_SavePySide( QtGui.QDialog ) :
    
    def __init__(self, parent=None) :
        'Creates a popup window, prompting the user to save the current scene file.'
        super( Win_SavePySide, self ).__init__(parent)
        self.value=None
        
        #  Layouts :
        self.layout=QtGui.QVBoxLayout()
        self.setLayout( self.layout )
        
        #  Text :
        self.text=QtGui.QLabel('Current file is about to be closed...  Save first?')
        self.layout.addWidget( self.text )
        
        #  Create Buttons :
        self.save=QtGui.QPushButton('Save')
        self.verUp=QtGui.QPushButton('Version Up + Save')
        self.no=QtGui.QPushButton('Don\'t Save')
        self.cancel=QtGui.QPushButton('Cancel')
        
        #  Button Layout :
        self.btn_layout=QtGui.QHBoxLayout()
        self.layout.addLayout( self.btn_layout )
        #  Add Buttons to Layout :
        for btn in [self.save, self.verUp, self.no, self.cancel] :
            self.btn_layout.addWidget( btn )
        
        #  Connections :
        self.save.clicked.connect( lambda : self.set_value( btn='save' ) )
        self.verUp.clicked.connect( lambda : self.set_value( btn='verUp' ) )
        self.no.clicked.connect( lambda : self.set_value( btn='no' ) )
        self.cancel.clicked.connect( lambda : self.set_value( btn='cancel' ) )
        
        self.show()
        
        return
    
    def set_value( self, btn='' ) :
        'Sets the value to be returned, when a button is pushed'
        if btn.lower()=='save' :
            self.value='Save'
        if btn.lower()=='verup' :
            self.value='VerUp'
        elif btn.lower()=='no' :
            self.value='No'
        elif btn.lower()=='cancel' :
            self.value='Cancel'
        self.close()
        return
    
    def btn(self) :
        'Returns the button that was pushed'
        return self.value
    
    @staticmethod
    def get_btn(parent=None) :
        'Returns the name of the button that was pushed'
        dialog=Win_SavePySide(parent)
        result=dialog.exec_()
        value=dialog.btn()
        return value


#  End of Class


#  End

