#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_c4d.py
# Version:  v2.7.26.171011
#
# Copyright (c) 2017 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import ntpath, os, platform, re, sys
#  C4D Imports :
import c4d
from c4d import bitmaps, gui, plugins
#  NIM Imports :
import nim as Nim
import nim_api as Api
import nim_c4d as C
import nim_file as F
import nim_prefs as Prefs
import nim_print as P
import nim_win as Win

#  Variables :
version='v2.7.26'
winTitle='NIM_'+version+' - '
_os=platform.system().lower()
nim_plugin_ID=1032427


def set_vars( nim=None, ID=None ) :
    'Get variables from a C4D file.'
    
    doc=c4d.documents.GetActiveDocument()
    container=c4d.BaseContainer()
    
    #nim.Print()
    P.info('\nSetting file variables...')
    
    #  Server :
    serverString=container.SetString( 9111, nim.server() )
    serverID=container.SetString( 9112, str(nim.ID('server')) )
    P.debug( '    Server = "%s"' % container.GetString( 9111 ) )
    P.debug( '    Server ID = %s' % container.GetString( 9112 ) )
    #  Job :
    jobString=container.SetString( 9113, nim.name('job') )
    jobID=container.SetString( 9114, str(nim.ID('job')) )
    P.debug( '    Job = "%s"' % container.GetString( 9113 ) )
    P.debug( '    Job ID = %s' % container.GetString( 9114 ) )
    #  Tab :
    tabString=container.SetString( 9115, nim.tab() )
    P.debug( '    Tab = "%s"' % container.GetString( 9115 ) )
    #  Asset :
    assetString=container.SetString( 9116, nim.name('asset') )
    assetID=container.SetString( 9117, str(nim.ID('asset')) )
    P.debug( '    Asset = "%s"' % container.GetString( 9116 ) )
    P.debug( '    Asset ID = %s' % container.GetString( 9117 ) )
    #  Show :
    showString=container.SetString( 9118, nim.name('show') )
    showID=container.SetString( 9119, str(nim.ID('show')) )
    P.debug( '    Show = "%s"' % container.GetString( 9118 ) )
    P.debug( '    Show ID = %s' % container.GetString( 9119 ) )
    #  Shot :
    shotString=container.SetString( 9120, nim.name('shot') )
    shotID=container.SetString( 9121, str(nim.ID('shot')) )
    P.debug( '    Shot = "%s"' % container.GetString( 9120 ) )
    P.debug( '    Shot ID = %s' % container.GetString( 9121 ) )
    #  Filter :
    filterString=container.SetString( 9122, nim.name('filter') )
    filterID=container.SetString( 9123, str(nim.ID('filter')) )
    P.debug( '    Filter = "%s"' % container.GetString( 9122 ) )
    P.debug( '    Filter ID = %s' % container.GetString( 9123 ) )
    #  Task :
    taskString=container.SetString( 9124, nim.name('task') )
    taskFolder=container.SetString( 9128, nim.taskFolder() )
    taskID=container.SetString( 9125, str(nim.ID('task')) )
    P.debug( '    Task = "%s"' % container.GetString( 9124 ) )
    P.debug( '    Task ID = %s' % container.GetString( 9125 ) )
    P.debug( '    Task Folder = "%s"' % container.GetString( 9128 ) )
    #  Basename :
    baseString=container.SetString( 9126, nim.name('base') )
    P.debug( '    Basename = "%s"' % container.GetString( 9126 ) )
    #  Version :
    verString=container.SetString( 9127, nim.name('ver') )
    verID=container.SetString( 9128, str(nim.ID('ver')) )
    P.debug( '    Version = "%s"' % container.GetString( 9127 ) )
    P.debug( '    Version ID = "%s"' % container.GetString( 9128 ) )

    #  Assign container to the document :
    doc[ID]=container
    
    P.debug('NIM values after setting C4D attributes...')
    nim.Print()
    
    return


def get_vars( nim=None, ID=None ) :
    'Get variables from a C4D file.'
    
    doc=c4d.documents.GetActiveDocument()
    container=doc.GetDataInstance()
    
    #  Server :
    serverString=container[ID].GetData( 9111 )
    nim.set_server( path=serverString )
    serverID=container[ID].GetData( 9112)
    nim.set_server( ID=serverID )
    #  Job :
    jobString=container[ID].GetData( 9113 )
    nim.set_name( elem='job', name=jobString )
    jobID=container[ID].GetData( 9114 )
    nim.set_ID( elem='job', ID=str(jobID) )
    #  Tab :
    tabString=container[ID].GetData( 9115 )
    nim.set_tab( tabString )
    #  Asset :
    assetString=container[ID].GetData( 9116 )
    nim.set_name( elem='asset', name=assetString )
    assetID=container[ID].GetData( 9117 )
    nim.set_ID( elem='asset', ID=str(assetID) )
    #  Show :
    showString=container[ID].GetData( 9118 )
    nim.set_name( elem='show', name=showString )
    showID=container[ID].GetData( 9119 )
    nim.set_ID( elem='show', ID=str(showID) )
    #  Shot :
    shotString=container[ID].GetData( 9120 )
    nim.set_name( elem='shot', name=shotString )
    shotID=container[ID].GetData( 9121 )
    nim.set_ID( elem='shot', ID=str(shotID) )
    #  Filter :
    filterString=container[ID].GetData( 9122 )
    nim.set_name( elem='filter', name=filterString )
    filterID=container[ID].GetData( 9123 )
    nim.set_ID( elem='filter', ID=str(filterID) )
    #  Task :
    taskString=container[ID].GetData( 9124 )
    nim.set_name( elem='task', name=taskString )
    taskFolder=container[ID].GetData( 9128 )
    nim.set_taskFolder( folder=taskFolder )
    taskID=container[ID].GetData( 9125 )
    nim.set_ID( elem='task', ID=str(taskID) )
    #  Basename :
    baseString=container[ID].GetData( 9126 )
    nim.set_name( elem='base', name=baseString )
    #  Version :
    verString=container[ID].GetData( 9127 )
    nim.set_name( elem='ver', name=verString )
    verID=container[ID].GetData( 9128 )
    nim.set_ID( elem='ver', ID=str(verID) )
    P.debug('NIM values after reading C4D attributes...')
    nim.Print()
    
    return nim



#  START - General UI Class :
class nim_fileUI( gui.GeDialog ) :
    'Main class, used to create the NIM File I/O Window.'
    
    def __init__( self, mode='open', doc=None ) :
        'Initializes values.'
        
        self.app = 'C4D'
        #  Store Document Information :
        self.doc=doc
        
        #  Set Button Name :
        if mode.lower() in ['open', 'file'] :
            self.btn_name='Open'
        elif mode.lower() in ['import', 'load'] :
            self.btn_name='Merge'
        elif mode.lower() in ['ref', 'reference', 'xref'] :
            self.btn_name='XRef'
        elif mode.lower() in ['save', 'saveas'] :
            self.btn_name='Save'
        elif mode.lower() in ['pub', 'publish'] :
            self.btn_name='Publish'
        self.mode=mode
                             
        #  Initialize NIM dictionary :
        self.nim=Nim.NIM()
        self.nim.set_mode( mode=self.mode )
        

        #  Preferences :
        self.prefs=Prefs.read()
        if not self.prefs :
            print 'Preferences not read'

        print 'Preferences being read...'
        
        #  Get Show/Shot Prefs :
        try :
            self.pref_serverPath=self.prefs[self.app+'_ServerPath']
            self.pref_serverID=self.prefs[self.app+'_ServerID']
        except :
            print "Failed to read preferences..."
        
        #  Get Variables/Preferences :
        self.nimPrefs=Nim.NIM().ingest_prefs()
        if self.mode.lower() in ['pub', 'publish', 'ver', 'version', 'verup'] :
            C.get_vars( nim=self.nimPrefs, ID=nim_plugin_ID )
        if self.mode.lower() in ['pub', 'publish'] :
            C.get_vars( nim=self.nim, ID=nim_plugin_ID )
        

        # Set server child index initial value
        self.serverChildIndex = 800

        return
    
    
    def CreateLayout(self):
        'Creates the UI elements.'
        self.SetTitle( '%s%s' % (winTitle, self.mode.title()) )
        
        #  Begin Main Vertical Group :
        self.GroupBegin( self.nim.grpIDs['main'], c4d.BFH_SCALEFIT, cols=1, rows=3 )
        #  Begin Top Group :
        self.GroupBegin( self.nim.grpIDs['top'], c4d.BFH_SCALE, cols=2, rows=1 )
        
        #  Job/Asset/Show/Shot :
        
        #  Begin Job/Asset/Show/Shot Group :
        self.GroupBegin( self.nim.grpIDs['jobAsset'], c4d.BFH_SCALE, 1, 2, inith=95 )
        self.GroupBorder( c4d.BORDER_GROUP_IN )
        self.GroupBorderSpace(5,5,5,5)
        #  Begin Job Group :
        self.GroupBegin( self.nim.grpIDs['job'], c4d.BFH_SCALE, cols=2, rows=1 )
        #  Job :
        self.AddStaticText( self.nim.textIDs['job'], c4d.BFH_SCALE, initw=95, name='Job :' )
        self.AddComboBox( self.nim.inputIDs['job'], c4d.BFH_SCALEFIT, initw=250 )
        if self.mode.lower() in ['save', 'saveas'] :
            self.AddStaticText( self.nim.textIDs['server'], c4d.BFH_SCALE, initw=95, name='Server :' )
            self.AddComboBox( self.nim.inputIDs['server'], c4d.BFH_SCALEFIT, initw=250 )
        #  End Job Group :
        self.GroupEnd()
        
        #  Tab :
        
        #  Begin Tab group :
        self.TabGroupBegin( self.nim.grpIDs['tab'], c4d.BFH_SCALE, tabtype=c4d.TAB_TABS )
        #  Begin Asset group :
        self.GroupBegin( self.nim.grpIDs['asset'], c4d.BFH_SCALE, title='Asset', cols=2, rows=1 )
        #  Asset :
        self.AddStaticText( self.nim.textIDs['asset'], c4d.BFH_SCALE, initw=95, name='Asset :' )
        self.AddComboBox( self.nim.inputIDs['asset'], c4d.BFH_SCALE, initw=250 )
        #  End Asset group ;
        self.GroupEnd()
        
        #  Begin Show/Shot :
        self.GroupBegin( self.nim.grpIDs['showShot'], c4d.BFH_SCALE, title='Show/Shot', cols=2, rows=2 )
        #  Show :
        self.AddStaticText( self.nim.textIDs['show'], c4d.BFH_SCALE, initw=95, name='Show :' )
        self.AddComboBox( self.nim.inputIDs['show'], c4d.BFH_SCALE, initw=250 )
        #  Shot :
        self.AddStaticText( self.nim.textIDs['shot'], c4d.BFH_SCALE, initw=95, name='Shot :' )
        self.AddComboBox( self.nim.inputIDs['shot'], c4d.BFH_SCALE, initw=250 )
        
        #  Set Tab from preferences :
        if self.nimPrefs.tab()=='SHOT' :
            self.SetLong( self.nim.grpIDs['tab'], self.nim.grpIDs['showShot'] )
            self.nim.set_tab( 'SHOT' )
        elif self.nimPrefs.tab()=='ASSET' :
            self.SetLong( self.nim.grpIDs['tab'], self.nim.grpIDs['asset'] )
            self.nim.set_tab( 'ASSET' )
        
        #  End Show/Shot group:
        self.GroupEnd()
        #  End Tab group :
        self.GroupEnd()
        #  End Job/Asset/Show/Shot :
        self.GroupEnd()
        
        #  Task/Basename :
        
        #  Begin Task/Basename group :
        self.GroupBegin( self.nim.grpIDs['taskBase'], c4d.BFH_SCALE, cols=2, rows=2, inith=95 )
        self.GroupBorder( c4d.BORDER_GROUP_IN )
        self.GroupBorderSpace(5,5,5,5)
        #  Filter :
        if self.mode.lower() not in ['pub', 'publish', 'save', 'saveas', 'ver', 'verup', 'version'] :
            self.AddStaticText( self.nim.textIDs['filter'], c4d.BFH_SCALE, initw=95, name='Filter :' )
            self.AddComboBox( self.nim.inputIDs['filter'], c4d.BFH_SCALEFIT, initw=250 )
        #  Task :
        self.AddStaticText( self.nim.textIDs['task'], c4d.BFH_SCALE, initw=95, name='Task :' )
        self.AddComboBox( self.nim.inputIDs['task'], c4d.BFH_SCALEFIT, initw=250 )
        # Basename :
        self.AddStaticText( self.nim.textIDs['base'], c4d.BFH_SCALE, initw=95, name='Basename :' )
        self.AddComboBox( self.nim.inputIDs['base'], c4d.BFH_SCALEFIT, initw=250 )
        #  Tag :
        if self.mode.lower() in ['save', 'saveas'] :
            self.AddStaticText( self.nim.textIDs['tag'], c4d.BFH_SCALE, initw=95, name='Tag:' )
            self.AddEditText( id=self.nim.inputIDs['tag'], flags=c4d.BFH_SCALEFIT, initw=95 )
        
        #  End Task Group :
        self.GroupEnd()
        #  End Top Group :
        self.GroupEnd()
        
        #  Version :
        
        self.GroupBegin( self.nim.grpIDs['ver'], c4d.BFH_SCALEFIT, cols=2, rows=4 )
        self.GroupBorder( c4d.BORDER_GROUP_IN )
        self.GroupBorderSpace(5,5,5,5)
        #  Version Box :
        self.AddStaticText( self.nim.textIDs['ver'], c4d.BFH_SCALE, initw=95,
            name='Versions :' )
        self.AddComboBox( self.nim.inputIDs['ver'], c4d.BFH_SCALEFIT, initw=700 )
        #  Filepath :
        self.AddStaticText( self.nim.textIDs['verFilepath'], c4d.BFH_SCALE, initw=95,
            name='Filepath :')
        self.AddStaticText( self.nim.inputIDs['verFilepath'], c4d.BFH_SCALE, initw=700,
            name='<filepath>')
        #  User :
        self.AddStaticText( self.nim.textIDs['verUser'], c4d.BFH_SCALE, initw=95,
            name='User :' )
        self.AddStaticText( self.nim.inputIDs['verUser'], c4d.BFH_SCALE, initw=700,
            name='<user>' )
        #  Date :
        self.AddStaticText( self.nim.textIDs['verDate'], c4d.BFH_SCALE, initw=95,
            name='Date :' )
        self.AddStaticText( self.nim.inputIDs['verDate'], c4d.BFH_SCALE, initw=700,
            name='<date>' )
        #  Comment :
        if self.mode.lower() not in ['pub', 'publish', 'save', 'saveas', 'ver', 'verup', 'version'] :
            self.AddStaticText( self.nim.textIDs['verComment'], c4d.BFH_SCALE, initw=95,
                name='Comment :' )
            self.AddStaticText( self.nim.inputIDs['verComment'], c4d.BFH_SCALE, initw=700,
                name='<comment>' )
            for obj in ['verFilepath', 'verUser', 'verDate'] :
                self.Enable( self.nim.inputIDs[obj], False )
        else :
            self.AddStaticText( self.nim.textIDs['comment'], c4d.BFH_SCALE, initw=95,
                name='Comment :' )
            self.AddEditText( self.nim.inputIDs['comment'], c4d.BFH_SCALEFIT, initw=95 )
            for obj in ['verFilepath', 'verUser', 'verDate'] :
                self.Enable( self.nim.inputIDs[obj], True )
        
        #  End Version Group :
        self.GroupEnd()
        
        #  Buttons Group :
        if self.mode.lower() in ['save', 'saveas'] :
            self.GroupBegin( self.nim.grpIDs['btn'], c4d.BFH_SCALEFIT, cols=3,rows=1 )
        else :
            self.GroupBegin( self.nim.grpIDs['btn'], c4d.BFH_SCALEFIT, cols=2, rows=1 )
        self.GroupBorder( c4d.BORDER_GROUP_IN )
        self.GroupBorderSpace(5,5,5,5)
        #  Button :
        self.AddButton( self.nim.btnID, c4d.BFH_SCALEFIT, name=self.btn_name )
        self.AddButton( self.nim.cancelBtnID, c4d.BFH_SCALEFIT, name='Cancel' )
        #  Save Selected :
        if self.mode.lower() in ['save', 'saveas'] :
            self.AddCheckbox( self.nim.inputIDs['checkbox'], flags=c4d.BFH_CENTER,
                initw=150, inith=12, name='Save Selected' )
        
        

        #  End Buttons Group :
        self.GroupEnd()
        #  End Main Vertical Group :
        self.GroupEnd()
        
        #  Populate UI Elements :
        for elem in self.nim.elements :
            response = self.populate_elem( elem=elem )

        #  Lock Elements :
        if self.mode.lower() in ['pub', 'publish', 'verup', 'ver', 'version'] :
            for elem in self.nim.elements :
                self.Enable( self.nim.inputIDs[elem], False )
            self.Enable( self.nim.grpIDs['tab'], False )
        
        return True
    
    
    def Command( self, id, msg ) :
        'Executed every time a user input is given'
        elem=''
        
        if id not in [self.nim.inputIDs['server'], self.nim.inputIDs['tag'], self.nim.inputIDs['comment']] :
            P.info( '~*~*~*~>' )
        
        #  Derive element :
        if id==self.nim.inputIDs['job'] : elem='job'
        elif id==self.nim.inputIDs['asset'] : elem='asset'
        elif id==self.nim.inputIDs['show'] : elem='show'
        elif id==self.nim.inputIDs['shot'] : elem='shot'
        elif id==self.nim.inputIDs['task'] : elem='task'
        elif id==self.nim.inputIDs['filter'] : elem='filter'
        elif id==self.nim.inputIDs['base'] : elem='base'
        elif id==self.nim.inputIDs['ver'] : elem='ver'
        
        #  Update drop-down menu elements :
        if elem in self.nim.elements :
            
            #  Clear variables :
            self.nim.clear(elem)
            self.nim.set_dict(elem)
            
            #  Iterate over drop-down contents :
            for key in self.nim.menuID( elem ) :
                
                #  If combo box is set to "None" or "Select..." :
                if self.GetLong( id )==self.nim.start_menuIDs[elem] :
                    if elem=='ver' :
                        self.SetString( self.nim.inputIDs['verFilepath'], '<filepath>' )
                        self.SetString( self.nim.inputIDs['verUser'], '<user>' )
                        self.SetString( self.nim.inputIDs['verDate'], '<date>' )
                        self.SetString( self.nim.inputIDs['verComment'], '<comment>' )
                
                #  Find the selected ID and it's C4D Menu ID Number :
                elif key==self.GetLong( id ) :
                    #  Update element selection's name :
                    self.nim.set_name( elem=elem, name=self.nim.menuID( elem )[key] )
                    P.info( '%s name is "%s"' % (elem.upper(), self.nim.name( elem )) )
                    #  Enable :
                    self.Enable( id, True )
                    #  Update current ID :
                    if type(self.nim.Dict(elem))==type(dict()) :
                        self.nim.set_ID( elem=elem, ID=self.nim.Dict( elem )[self.nim.name( elem )] )
                    if type(self.nim.Dict( elem ))==type(list()) :
                        for listItem in self.nim.Dict( elem ) :
                            #  Skip Filter, which has no ID :
                            if type(listItem) is type(str) :
                                break
                            #  Set ID and Task Folder :
                            elif type(listItem) is type(dict()) :
                                #  Set Task Folder :
                                if elem=='task' :
                                    self.nim.set_taskFolder( folder=listItem['folder'] )
                                #  Set IDs :
                                if 'name' in listItem.keys() and listItem['name']==self.nim.name( elem ) :
                                    self.nim.set_ID( elem=elem, ID=listItem['ID'] )
                                    break
                                elif 'basename' in listItem.keys() and listItem['basename']==self.nim.name( elem ) :
                                    self.nim.set_ID( elem=elem, ID=None )
                                    break
                                elif 'showname' in listItem.keys() and listItem['showname']==self.nim.name( elem ) :
                                    self.nim.set_ID( elem=elem, ID=listItem['ID'] )
                                    break
                    
                    #  Print :
                    if self.nim.ID( elem ) :
                        P.info( '%s="%s", %s ID="%s"' % (elem.upper(), self.nim.name( elem ), elem.upper(), self.nim.ID( elem )) )
                    else : P.info( '%s="%s"' % (elem.upper(), self.nim.name( elem )) )
                    
                    #  Update version information :
                    if elem=='ver' :
                        for option in self.nim.Dict( elem ) :
                            if re.search( '^'+option['filename']+' - ', self.nim.name( elem ) ) :
                                self.SetString( self.nim.inputIDs['verFilepath'], option['filepath'] )
                                self.SetString( self.nim.inputIDs['verUser'], option['username'] )
                                self.SetString( self.nim.inputIDs['verDate'], option['date'] )
                                self.SetString( self.nim.inputIDs['verComment'], option['note'] )
                                if self.nim.mode() not in ['pub', 'publish', 'save', 'saveas', 'ver', 'version', 'verup'] :
                                    self.Enable( self.nim.inputIDs['verFilepath'], True )
                                    self.Enable( self.nim.inputIDs['verUser'], True )
                                    self.Enable( self.nim.inputIDs['verDate'], True )
                                    self.Enable( self.nim.inputIDs['verComment'], True )
                                else :
                                    self.Enable( self.nim.inputIDs['verFilepath'], False )
                                    self.Enable( self.nim.inputIDs['verUser'], False )
                                    self.Enable( self.nim.inputIDs['verDate'], False )
                                    self.Enable( self.nim.inputIDs['verComment'], False )
                                break 
            
            #print 'NIM Dictionary after updating.'
            #self.nim.Print()
            
            #  Populate dependent elements :
            index=self.nim.elements.index( elem )+1
            if elem=='asset' : index=4
            while index<len(self.nim.elements) :
                self.populate_elem( self.nim.elements[index] )
                index +=1
        
        #  Update Servers :
        if elem == 'job' :
            self.FreeChildren( self.nim.inputIDs["server"] )
            jobServers=Api.get_servers( self.nim.ID('job') )
            self.nim.set_server( Dict=jobServers )
            P.info("NIM jobServers: %s" % jobServers)
            serverOptNum=self.serverChildIndex

            if self.mode.lower() in ['save', 'saveas'] :
                if jobServers and len(jobServers) :
                    for js in jobServers :
                        if  _os in ['windows', 'win32'] :
                            serverName=js['winPath']+' - ("'+js['server']+'")'
                            self.AddChild( self.nim.inputIDs['server'], serverOptNum, serverName )
                            if serverOptNum==800 :
                                self.SetLong( self.nim.inputIDs['server'], 800 )
                                self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['winPath']) )
                            if self.pref_serverID == js['ID'] :
                                self.SetLong( self.nim.inputIDs['server'], serverOptNum)
                                self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['winPath']) )

                            serverOptNum+=1

                        elif _os in ['darwin', 'mac'] :
                            serverName=js['osxPath']+' - ("'+js['server']+'")'
                            self.AddChild( self.nim.inputIDs['server'], serverOptNum, serverName )
                            if serverOptNum==800 :
                                self.SetLong( self.nim.inputIDs['server'], 800 )
                                self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['osxPath']) )
                            if self.pref_serverID == js['ID'] :
                                self.SetLong( self.nim.inputIDs['server'], serverOptNum)
                                self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['osxPath']) )

                            serverOptNum+=1

                        elif _os in ['linux', 'linux2'] :
                            serverName=js['path']+' - ("'+js['server']+'")'
                            self.AddChild( self.nim.inputIDs['server'], serverOptNum, serverName )
                            if serverOptNum==800 :
                                self.SetLong( self.nim.inputIDs['server'], 800 )
                                self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['path']) )
                            if self.pref_serverID == js['ID'] :
                                self.SetLong( self.nim.inputIDs['server'], serverOptNum)
                                self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['path']) )

                            serverOptNum+=1

        # END UPDATE SERVER

        #  Update Tab dependent elements :
        if id==self.nim.grpIDs['tab'] :
            if self.GetLong( self.nim.grpIDs['tab'] )==self.nim.grpIDs['asset'] :
                self.nim.set_tab( _type='ASSET' )
            elif self.GetLong( self.nim.grpIDs['tab'] )==self.nim.grpIDs['showShot'] :
                self.nim.set_tab( _type='SHOT' )
            #  Update task, basename and version information :
            for index in range(4,7) :
                self.populate_elem( elem=self.nim.elements[index] )
        
        #  Update Tag :
        if id==self.nim.inputIDs['tag'] :
            tagText=self.GetString( self.nim.inputIDs['tag'] )
            self.nim.set_name( elem='tag', name=tagText.replace( ' ', '_' ) )
            if self.nim.name('tag') :
                self.Enable( self.nim.inputIDs['base'], False )
            else :
                self.Enable( self.nim.inputIDs['base'], True )
                return True
        
        #  Update Comment :
        if id==self.nim.inputIDs['comment'] :
            commentText=self.GetString( self.nim.inputIDs['comment'] )
            self.nim.set_name( elem='comment', name=commentText )
            return True
        
        #  Button :
        if id==self.nim.btnID :
            self.btn_action()
        
        if id==self.nim.cancelBtnID :
            self.btn_cancel()

        return True
    
    
    def AskClose(self) :
        'Used to write out preferences when the window is closed'
        
        #  Check the UI Mode :
        if self.mode.lower() not in ['pub', 'publish', 'save', 'saveas', 'ver', 'verup', 'version', 'versionup'] :
            P.info('Writing C4D preferences...')
            
            #  Write element preferences :
            for index in range(len(self.nim.elements)) :
                Prefs.update( app='C4D', attr=self.nim.print_elements[index], \
                    value=self.nim.name( self.nim.elements[index] ) )
            #  Write tab preferences :
            Prefs.update( app='C4D', attr='tab', value=self.nim.tab() )
        return False
    

    def populate_server(self) :
        'Populates the server field, when the Job is set'
        print "***************************populate_server*******************************"
        index=0
        #  Get Server Dictionary :
        serverDict=Api.get_servers( self.nim.ID('job') )
        
        if serverDict :
            if 'success' in serverDict :
                if serverDict['success'] == 'false' :
                    P.warning(serverDict['error'])
                    self.nim.Input('server').clear()
                    self.nim.Input('server').addItem('None')
                    self.nim.Input('server').setEnabled( False )
                    self.nim.set_server( name='', path='', Dict={}, ID='' )
                    return

        #  Populate the combo box :
        if serverDict and len(serverDict) :
            P.info( '   Job Servers = %s' % serverDict )

            self.nim.set_server( Dict=serverDict )
            
            #  Populate drop box :
            #self.nim.Input('server').setEnabled( True )
            #self.nim.Input('server').clear()

            print( '   self.pref_serverID = %s' % self.pref_serverID )

            for js in self.nim.Dict('server') :
                if _os in ['windows', 'win32'] :
                    self.nim.Input('server').addItem( js['winPath']+' - ("'+js['server']+'")' )
                    if js['ID'] !=self.pref_serverID :
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), path=str(js['path']) )
                        index+=1
                    else :
                        self.nim.Input('server').setCurrentIndex( index )
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), path=str(js['winPath']) )
                elif _os in ['darwin', 'mac'] :
                    self.nim.Input('server').addItem( js['osxPath']+' - ("'+js['server']+'")' )
                    if js['ID'] !=self.pref_serverID :
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), path=str(js['path']) )
                        index +=1
                    else :
                        self.nim.Input('server').setCurrentIndex( index )
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), path=str(js['osxPath']) )
                elif _os in ['linux', 'linux2'] :
                    self.nim.Input('server').addItem( js['path']+' - ("'+js['server']+'")' )
                    if js['ID'] !=self.pref_serverID :
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), path=str(js['path']) )
                        index +=1
                    else :
                        self.nim.Input('server').setCurrentIndex( index )
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), path=str(js['path']) )
        else :
            self.nim.Input('server').clear()
            self.nim.Input('server').addItem('None')
            self.nim.Input('server').setEnabled( False )
            self.nim.set_server( name='', path='', Dict={}, ID='' )
            if self.nim.ID('job') :
                P.warning( 'No servers found for job, "%s"' % self.nim.name('job') )
        return
    

    def populate_elem( self, elem='' ) :
        'Populates an element combo box'
        
        #  Initialize dictionary and fields :
        self.nim.clear( elem )
        self.FreeChildren( self.nim.inputIDs[elem] )
        response = self.nim.set_dict( elem )
        if response == False:
            print 'Failed to populate elements.'
            self.Close()

        #  Clear fields :
        if not self.nim.Dict( elem ) or not len(self.nim.Dict( elem )) :
            P.debug( 'No %s dictionary!' % elem )
            #  Clear Task and Basename, if Asset Master is selected :
            if self.nim.name('filter')=='Asset Master' :
                if elem in ['task', 'base'] :
                    P.info('Disabling Task and Basename, for Asset Master.')
                    self.FreeChildren( self.nim.inputIDs[elem] )
                    self.Enable( self.nim.inputIDs[elem], False )
            #  Clear regular fields :
            self.Enable( self.nim.start_menuIDs[elem], False )
            self.AddChild( self.nim.inputIDs[elem], self.nim.start_menuIDs[elem], 'None' )
            self.SetLong( self.nim.inputIDs[elem], self.nim.start_menuIDs[elem] )
            self.nim.set_ID( elem=elem, ID=None )
            self.nim.set_name( elem=elem, name='' )
            self.nim.set_dict( elem=elem )
            #  Clear version related text :
            if elem=='ver' :
                self.SetString( self.nim.inputIDs['verFilepath'], '<filepath>' )
                self.SetString( self.nim.inputIDs['verUser'], '<user>' )
                self.SetString( self.nim.inputIDs['verDate'], '<date>' )
                self.SetString( self.nim.inputIDs['verComment'], '<comment>' )
            return False
        #  Print :
        else :
            P.debug( '%s Dictionary = %s' % (elem.upper(), self.nim.Dict( elem )) )
        
        #  Initialize :
        P.debug( 'Enabling %s' % elem.upper() )
        self.Enable( self.nim.inputIDs[elem], True )
        self.AddChild( self.nim.inputIDs[elem], self.nim.start_menuIDs[elem], 'Select...' )
        self.SetLong( self.nim.inputIDs[elem], self.nim.start_menuIDs[elem] )
        
        jobList=[]
        if elem=='job' :
            for key in self.nim.Dict(elem).keys() : jobList.append(key)
            jobList=sorted(jobList, reverse=True )
        

        #  Populate :
        #===------------
        
        
        itemNum=int(self.nim.start_menuIDs[elem])+1
        
        #  Populate from lists :
        if elem=='job' :
            for item in jobList :
                self.AddChild( self.nim.inputIDs[elem], itemNum, item )
                tempDict=self.nim.menuID( elem )
                tempDict[itemNum]=item
                self.nim.set_menuID( elem=elem, Dict=tempDict )
                #  Set from Preferences :
                if self.nimPrefs.name( elem )==item :
                    self.SetLong( self.nim.inputIDs[elem], itemNum )
                    self.nim.set_name( elem=elem, name=item )
                    try : self.nim.set_ID( elem=elem, ID=self.nim.Dict( elem )[item] )
                    except : P.warning('Could not set ID for Job')
                    
                    #  Update Servers :
                    jobServers=Api.get_servers( self.nim.ID('job') )
                    self.nim.set_server( Dict=jobServers )

                    P.info("NIM jobServers: %s" % jobServers)
                    serverOptNum=self.serverChildIndex # default 800
                    
                    if self.mode.lower() in ['save', 'saveas'] :
                        if jobServers and len(jobServers) :
                            for js in jobServers :
                                if  _os in ['windows', 'win32'] :
                                    serverName=js['winPath']+' - ("'+js['server']+'")'
                                    self.AddChild( self.nim.inputIDs['server'], serverOptNum, serverName )
                                    if serverOptNum==800 :
                                        self.SetLong( self.nim.inputIDs['server'], 800 )
                                        self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['winPath']) )
                                    if self.pref_serverID == js['ID'] :
                                        self.SetLong( self.nim.inputIDs['server'], serverOptNum)
                                        self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['winPath']) )
                                    
                                    serverOptNum+=1

                                elif _os in ['darwin', 'mac'] :
                                    serverName=js['osxPath']+' - ("'+js['server']+'")'
                                    self.AddChild( self.nim.inputIDs['server'], serverOptNum, serverName )
                                    if serverOptNum==800 :
                                        self.SetLong( self.nim.inputIDs['server'], 800 )
                                        self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['osxPath']) )
                                    if self.pref_serverID == js['ID'] :
                                        self.SetLong( self.nim.inputIDs['server'], serverOptNum)
                                        self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['osxPath']) )

                                    serverOptNum+=1

                                elif _os in ['linux', 'linux2'] :
                                    serverName=js['path']+' - ("'+js['server']+'")'
                                    self.AddChild( self.nim.inputIDs['server'], serverOptNum, serverName )
                                    if serverOptNum==800 :
                                        self.SetLong( self.nim.inputIDs['server'], 800 )
                                        self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['path']) )
                                    if self.pref_serverID == js['ID'] :
                                        self.SetLong( self.nim.inputIDs['server'], serverOptNum)
                                        self.nim.set_server( name=serverName, ID=str(js['ID']), path=str(js['path']) )

                                    serverOptNum+=1
                
                #  Increment count :
                itemNum+=1
            
            #  Update Servers :
            
        else :
            #  Iterate element dictionary :
            #P.debug("elements: %s" % self.nim.Dict(elem))
            
            for item in self.nim.Dict(elem) :
               # P.debug("item: %s" % item)
                #P.debug("item type: %s" % type(item))
                if type(item) is type(dict()) :
                    #  General Elements :
                    if 'name' in item :
                        self.AddChild( self.nim.inputIDs[elem], itemNum, item['name'] )
                        tempDict=self.nim.menuID( elem )
                        tempDict[itemNum]=item['name']
                        self.nim.set_menuID( elem=elem, Dict=tempDict )
                        #  Set from Preferences :
                        if self.nimPrefs.name( elem )==item['name'] :
                            self.SetLong( self.nim.inputIDs[elem], itemNum )
                            self.nim.set_name( elem=elem, name=item['name'] )
                            try : self.nim.set_ID( elem=elem, ID=item['ID'] )
                            except : P.warning( 'Could not set ID for %s!' % elem )
                            #  Save Task Folder :
                            if elem=='task' :
                                self.nim.set_taskFolder( folder=item['folder'] )
                                if self.nim.name('task')=='Asset Master' : 
                                    print 'Asset Master Found'
                    #  Shows :
                    elif 'showname' in item :
                        self.AddChild( self.nim.inputIDs[elem], itemNum, item['showname'] )
                        tempDict=self.nim.menuID( elem )
                        tempDict[itemNum]=item['showname']
                        self.nim.set_menuID( elem=elem, Dict=tempDict )
                        #  Set from Preferences :
                        if self.nimPrefs.name( elem )==item['showname'] :
                            self.SetLong( self.nim.inputIDs[elem], itemNum )
                            self.nim.set_name( elem=elem, name=item['showname'] )
                            try : self.nim.set_ID( elem=elem, ID=item['ID'] )
                            except : P.warning('Could not set ID for Show!')
                    #  Versions :
                    elif 'filename' in item :
                        #P.debug("filename item: %s" % item)
                        if self.mode.lower() not in ['save', 'saveas', 'pub', 'publish'] :
                            #  Derive the text to populate the combo box with :
                            if 'note' in item.keys() : verItem=item['filename']+' - '+item['note']
                            else : verItem=item['filename']+' -  '
                            #  Populate the combo box :
                            self.AddChild( self.nim.inputIDs[elem], itemNum, verItem )
                            P.debug("verItem: %s" % verItem)
                            #  Store the updated list of Menu IDs :
                            tempDict=self.nim.menuID( elem )
                            tempDict[itemNum]=verItem
                            self.nim.set_menuID( elem=elem, Dict=tempDict )
                            #  Set from Preferences :
                            if self.nimPrefs.name( elem )==verItem :
                                self.SetLong( self.nim.inputIDs[elem], itemNum )
                                self.nim.set_name( elem=elem, name=verItem )
                                try :self.nim.set_ID( elem=elem, ID=item['fileID'] )
                                except : P.warning( 'Could not set ID for %s!' % elem )
                                #  Set Version related text fields :
                                if 'filepath' in item.keys() and item['filepath'] :
                                    self.SetString( self.nim.inputIDs['verFilepath'], item['filepath'] )
                                if 'username' in item.keys() and item['username'] :
                                    self.SetString( self.nim.inputIDs['verUser'], item['username'] )
                                if 'date' in item.keys() and item['date'] :
                                    self.SetString( self.nim.inputIDs['verDate'], item['date'] )
                                if 'note' in item.keys() and item['note'] :
                                    self.SetString( self.nim.inputIDs['verComment'], item['note'] )
                                #REMOVED - was stopping full list from loading
                                #break
                            else :
                                #  Set when Asset Master is specified :
                                if self.nim.name('filter')=='Asset Master' :
                                    #  Set Version related text fields :
                                    if 'filepath' in item.keys() and item['filepath'] :
                                        self.SetString( self.nim.inputIDs['verFilepath'], item['filepath'] )
                                        self.SetString( self.nim.inputIDs['verUser'], '<user>' )
                                        self.SetString( self.nim.inputIDs['verDate'], '<date>' )
                                        self.SetString( self.nim.inputIDs['verComment'], '<note>' )
                                #  Set fields to default otherwise :
                                else :
                                    #  Set Version related text fields :
                                    self.SetString( self.nim.inputIDs['verFilepath'], '<filepath>' )
                                    self.SetString( self.nim.inputIDs['verUser'], '<user>' )
                                    self.SetString( self.nim.inputIDs['verDate'], '<date>' )
                                    self.SetString( self.nim.inputIDs['verComment'], '<note>' )
                    #  Basenames :
                    elif 'basename' in item :
                        self.AddChild( self.nim.inputIDs[elem], itemNum, item['basename'] )
                        tempDict=self.nim.menuID( elem )
                        tempDict[itemNum]=item['basename']
                        self.nim.set_menuID( elem=elem, Dict=tempDict )
                        #  Set from Preferences :
                        if self.nimPrefs.name( elem )==item['basename'] :
                            self.SetLong( self.nim.inputIDs[elem], itemNum )
                            self.nim.set_name( elem=elem, name=item['basename'] )
                            #  NOTE : Basenames have no ID
                            try : self.nim.set_ID( elem=elem, ID=item['ID'] )
                            except :
                                if elem !='base' : P.warning( 'Could not set ID for %s!' % elem )
                        else :
                            pass
                            #self.Enable( self.nim.inputIDs[elem], False )
                #  Filter :
                elif type(item) is type(str()) :
                    self.AddChild( self.nim.inputIDs[elem], itemNum, item )
                    tempDict=self.nim.menuID( elem )
                    tempDict[itemNum]=item
                    self.nim.set_menuID( elem=elem, Dict=tempDict )
                    #  Set from Preferences :
                    if self.nimPrefs.name( elem )==item :
                        self.SetLong( self.nim.inputIDs[elem], itemNum )
                        self.nim.set_name( elem=elem, name=item )
                
                #  Increment count :
                itemNum+=1
        
        return True
    

    def btn_action(self) :
        'Action executed when the button is pushed'
        
        # Get OS Path to file :
        upper_os = platform.system()
        P.info('OS: %s' % upper_os)
        
        filePath=''
        file_osPath=''
        version_id = None
        self.saveServerPref = False

        #print ("dict: %s" % self.nim.Dict('ver') )

        #  Derive file path :
        srch_result=re.search( ' - ', self.nim.name('ver') )
        if srch_result :
            index=self.nim.name('ver').find(' - ')

            if self.nim.name('ver'):
                nim_version_name = self.nim.name('ver')[0:index]
                P.debug('name from index: %s' % nim_version_name )
                
                for version_item in self.nim.Dict('ver'):
                    if 'fileID' in version_item and 'filename' in version_item :
                        if nim_version_name == version_item['filename']:
                            P.debug('Found the file')
                            version_id = version_item['fileID']
                            break

                #get the fileID from the dict
                if version_id:
                    file_osPath = Api.get_osPath( version_id, upper_os )
                    P.info('OS Path: %s' % file_osPath)

            if file_osPath:
                '''OS PATH RESOLUTION'''
                filepath=os.path.join( file_osPath['path'], self.nim.name('ver')[0:index] )
                filePath=os.path.normpath( filepath )
            else:
                P.error('Failed to resolve os path')


        #  Error Check :
        if self.mode.lower() in ['open', 'load', 'ref', 'reference', 'xref', 'import'] and not filePath :
            msg='Sorry, unable to derive a file path to use.'
            P.error( msg )
            Win.popup( title=winTitle+' - File Error', msg=msg )
            return False
        if self.mode.lower() in ['open', 'load', 'ref', 'reference', 'xref', 'import'] and \
            not os.path.isfile( filePath ) :
            msg='Sorry, specified file path does not exist.'
            P.error( msg )
            P.error( '    %s' % filePath )
            Win.popup( title=winTitle+'File Error', msg=msg )
            return False
        
        #  Open :
        if self.mode.lower() in ['file', 'open'] :
            
            # Get Server OS Path from server ID
            open_file_versionInfo = Api.get_verInfo( version_id )
            if open_file_versionInfo :
                open_file_serverID = open_file_versionInfo[0]['serverID']
                P.info("ServerID: %s" % open_file_serverID)
                serverOsPathInfo = Api.get_serverOSPath( open_file_serverID, platform.system() )
                P.info("Server OS Path Info: %s" % serverOsPathInfo)
                serverOSPath = serverOsPathInfo[0]['serverOSPath']
                P.info("Server OS Path: %s" % serverOSPath)
                self.nim.set_server( path=serverOSPath, ID=open_file_serverID )
                self.saveServerPref = True
            else :
                #  Derive Server Path from File Name :
                self.nim.set_server( Dict=Api.get_servers( self.nim.ID('job') ) )
                if not self.nim.server() :
                    for sp in ['winPath', 'osxPath', 'path'] :
                        if self.nim.Dict('server') and len(self.nim.Dict('server')) :
                            for item in self.nim.Dict('server') :
                                prefix=os.path.normpath( item[sp] )
                                if prefix==os.path.normpath( filePath[:len(prefix)] ) :
                                    self.nim.set_server( path=prefix, ID=item['ID'] )
                                    break

            #  Open File :
            P.info( 'Opening file...\n    %s' % filePath )
            c4d.documents.LoadFile( str(filePath) )
            #  Set Variables :
            C.set_vars( nim=self.nim, ID=nim_plugin_ID )
        
        #  Load :
        elif self.mode.lower() in ['import', 'load'] :
            
            #  Check filepath :
            if F.get_ext( str(filePath) ) !='.c4d' :
                msg='Invalid filetype (needs to be ".c4d"), cannot load.'
                P.error(msg)
                Win.popup( title='File Error', msg=msg )
                return
            
            curFile=c4d.documents.GetActiveDocument()
            P.info( 'Merging file...\n    %s' % filePath )
            c4d.documents.MergeDocument( curFile, str(filePath), 1 )
        
        #  Ref :
        elif self.mode.lower() in ['reference', 'ref', 'xref'] :
            curFile=c4d.documents.GetActiveDocument()
            P.info( 'Referencing file...\n    %s' % filePath )
            c4d.documents.MergeDocument( curFile, str(filePath), 1 )
        
        #  Save :
        if self.mode.lower() in ['save', 'saveas'] :
            # Get serverID from dropdown
            # SERVER subID starts at self.serverChildIndex... 
            #   subtract self.serverChildIndex from server_subID to get dict index
            server_subID = self.GetInt32(self.nim.inputIDs['server'])
            serverIndex = server_subID - self.serverChildIndex;
            jobServers = self.nim.Dict('server')
            if jobServers and len(jobServers):
                serverID = jobServers[serverIndex]['ID']
                serverName = jobServers[serverIndex]['server']
                P.info('Server Name: %s' % serverName)
                P.info('Server ID: %s' % str(serverID))
                serverOsPathInfo = Api.get_serverOSPath( serverID, platform.system() )
                P.info("Server OS Path Info: %s" % serverOsPathInfo)
                serverOSPath = serverOsPathInfo[0]['serverOSPath']
                P.info("Server OS Path: %s" % serverOSPath)
                self.nim.set_server( name=serverName, path=serverOSPath, ID=serverID )
                self.saveServerPref = True

            checkState=self.GetLong( self.nim.inputIDs['checkbox'] )
            #  Save Selected :
            if checkState :
                P.info('Saving Selected Objects...')
                Api.versionUp( nim=self.nim, selected=True, win_launch=True )
            #  Save File :
            elif not checkState :
                P.info('Saving C4D file...')
                Api.versionUp( nim=self.nim, win_launch=True )
                
        
        #  Publish :
        if self.mode.lower() in ['pub', 'publish'] :
            #  Version Up file :
            P.info('Publishing the file...')
                     
            ver_filePath=Api.versionUp( nim=self.nim, win_launch=True )
            #  Publish file :
            P.info('Publishing C4D file...')
            pub_filePath=Api.versionUp( nim=self.nim, win_launch=True, pub=True, symLink=True )
            #  Prompt to open work file :
            result=Win.popup( title=winTitle+'Open work file?',
                msg='Version Up and Publish complete!  Open work file?', type='okCancel' )
            if result :
                P.info('Opening work file...')
                c4d.documents.LoadFile( str(ver_filePath) )
                #  Set Variables :
                C.set_vars( nim=self.nim, ID=nim_plugin_ID )
        

        #  Version Up : # NOT IMPLEMENTED
        if self.mode.lower() in ['verup', 'version'] :
            P.info('About to Version Up C4D file...')
            Api.versionUp( nim=self.nim, win_launch=True )
            C.set_vars( nim=self.nim, ID=nim_plugin_ID )


        if self.saveServerPref == True:
            P.info('Saving server setting to prefs...')
            P.info('    serverPath: %s' % self.nim.server( get='path') )
            P.info('    serverID: %s' % self.nim.server( get='ID') )
            Prefs.update( attr='ServerPath', app='C4D', value=self.nim.server( get='path') )
            Prefs.update( attr='ServerID', app='C4D', value=self.nim.server( get='ID') )
            self.saveServerPref = False

        self.Close()
        
        return

    def btn_cancel(self) :
        'Cancel the action and close the window'
        self.Close()

        return


#  END - UI Class.


#  END

