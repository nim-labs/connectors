#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim.py
# Version:  v5.0.18.211109
#
# Copyright (c) 2014-2021 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import ntpath, os, traceback
from . import nim_api as Api
from . import nim_file as F
from . import nim_prefs as Prefs
from . import nim_print as P


class NIM( object ) :
    
    def __init__(self) :
        'Initializes the NIM attributes'
        # super( NIM, self ).__init__()
        self.nim={}
        
        #  Store preferences :
        self.prefs=Prefs.read()
        
        #  Store the different GUI elements to be populated :
        self.elements=['job', 'asset', 'show', 'shot', 'filter', 'task', 'base', 'ver']
        self.print_elements=['job', 'asset', 'show', 'shot', 'filter', 'task', 'basename', 'version']
        self.comboBoxes=['job', 'asset', 'show', 'shot', 'filter', 'task']
        self.listViews=['base', 'ver']
        
        #  Instantiate dictionary of settings :
        for elem in self.elements :
            self.clear( elem )
        
        #  Make image attributes :
        for elem in ['asset', 'shot'] :
            self.nim[elem]['img_pix']=''
            self.nim[elem]['img_label']=''
        
        #  Set file attributes :
        self.nim['file']={'path': '', 'filename': '', 'dir': '', 'basename': '', 'compPath': '', 'version': ''}
        self.set_filePath()
        
        #  Extra NIM attributes :
        for elem in ['comment', 'fileExt', 'tag'] :
            self.nim[elem]={'name': '', 'input': None}
        self.nim['server']={'name':'', 'path': '', 'input':'', 'ID': '', 'Dict': ''}
        self.nim['fileExt']['fileType']=''
        self.nim['app']=F.get_app()
        self.nim['class']=None
        self.nim['mode']=None
        self.nim['pub']=False
        
        #  Attempt to set User information :
        self.nim['user']={'name': '', 'ID': '' }
        if self.prefs :
            if 'NIM_User' in list(self.prefs.keys()) :
                self.nim['user']['name']=self.prefs['NIM_User']
                if self.nim['user']['name'] :
                    self.nim['user']['ID']=Api.get_userID( user=self.nim['user']['name'] )
        
        #  App Specific :
        if self.nim['app']=='C4D' :
            #  Group ID's :
            self.grpIDs={ 'main': 101, 'top': 102, 'jobAsset': 103, 'tab': 104, 'job': 105,
                'asset': 106, 'showShot': 107, 'taskBase': 108, 'ver': 109, 'btn': 110 }
            #  Input ID's :
            self.inputIDs={ 'job': 200, 'server': 201, 'asset': 202, 'show': 203, 'shot': 204, 'filter': 205,
                'task': 206, 'base': 207, 'tag': 208, 'comment': 209, 'ver': 210, 'verFilepath': 211,
                'verUser': 212, 'verDate': 213, 'verComment': 214 , 'checkbox': 215}
            #  Text ID's :
            self.textIDs={ 'job': 300, 'server': 301, 'asset': 302, 'show': 303, 'shot': 304, 'filter': 305,
                'task': 306, 'base': 307, 'tag': 308, 'comment': 309, 'ver': 310, 'verFilepath': 311,
                'verUser': 312, 'verDate': 313, 'verComment': 314 }
            #  Lowest Menu IDs :
            self.start_menuIDs={'job': 1000, 'asset': 2000, 'show': 3000, 'shot': 4000, 'filter': 5000,
                'task': 6000, 'base': 7000, 'ver': 8000}
            #  Menu ID's :
            self.menuIDs={ 'job': {}, 'asset': {}, 'show': {}, 'shot': {}, 'filter': {}, 'task': {}, 'base': {}, 'ver': {} }
            #  Button ID :
            self.btnID=10070
            self.cancelBtnID=10071
            
        
        return
    
    def Print( self, indent=4, debug=False ) :
        'Prints the NIM dictionary'
        
        if not debug :
            P.info( ' '*indent+'{' )
            if self.nim['server']['path'] :
                P.info( ' '*indent*2+'Server Path = "%s"' % self.nim['server']['path'] )
            if self.nim['server']['name'] :
                P.info( ' '*indent*2+'  Name = "%s"' % self.nim['server']['name'] )
            if self.nim['server']['ID'] :
                P.info( ' '*indent*2+'  ID = "%s"' % self.nim['server']['ID'] )
            if self.nim['server']['Dict'] :
                P.info( ' '*indent*2+'  Dict = "%s"' % self.nim['server']['Dict'] )
            if self.nim['server']['input'] :
                P.info( ' '*indent*2+'  Input = "%s"' % self.nim['server']['input'] )
            for elem in self.elements :
                P.info( ' '*indent*2+'%s = "%s"' % (self.get_printElem( elem ), self.name( elem )) )
                if self.Input( elem ) :
                    P.info( ' '*indent*2+'  Input = %s' % self.Input( elem ) )
                if self.ID( elem ) :
                    P.info( ' '*indent*2+'  ID = "%s"' % self.ID( elem ) )
                if self.Dict( elem ) :
                    P.info( ' '*indent*2+'  Dict = %s' % self.Dict( elem ) )
                if elem=='task' :
                    P.info( ' '*indent*2+'  Task Folder = "%s"' % self.taskFolder() )
            P.info( ' '*indent*2+'tab = "%s"' % self.nim['class'] )
            P.info( ' '*indent+'}' )
        elif debug :
            P.debug( ' '*indent+'{' )
            if self.nim['server']['name'] :
                P.debug( ' '*indent*2+'Server = "%s"' % self.nim['server']['name'] )
            if self.nim['server']['path'] :
                P.debug( ' '*indent*2+'  Path = "%s"' % self.nim['server']['path'] )
            if self.nim['server']['ID'] :
                P.debug( ' '*indent*2+'  ID = "%s"' % self.nim['server']['ID'] )
            if self.nim['server']['Dict'] :
                P.debug( ' '*indent*2+'  Dict = "%s"' % self.nim['server']['Dict'] )
            if self.nim['server']['input'] :
                P.debug( ' '*indent*2+'  Input = "%s"' % self.nim['server']['input'] )
            for elem in self.elements :
                P.debug( ' '*indent*2+'%s = "%s"' % (self.get_printElem( elem ), self.name( elem )) )
                if self.Input( elem ) :
                    P.debug( ' '*indent*2+'  Input = %s' % self.Input( elem ) )
                if self.ID( elem ) :
                    P.debug( ' '*indent*2+'  ID = "%s"' % self.ID( elem ) )
                if self.Dict( elem ) :
                    P.debug( ' '*indent*2+'  Dict = %s' % self.Dict( elem ) )
                if elem=='task' and self.taskFolder() :
                    P.debug( ' '*indent*2+'  Task Folder = "%s"' % self.taskFolder() )
            P.debug( ' '*indent*2+'tab = "%s"' % self.nim['class'] )
            P.debug( ' '*indent+'}' )
        
        return
    
    def clear( self, elem='job' ) :
        'Clears the dictionary of a given element'
        label, pic='', ''
        
        if elem in ['asset', 'shot'] and elem in list(self.nim.keys()) :
            if 'img_pix' in list(self.nim[elem].keys()) :
                pic=self.nim[elem]['img_pix']
            if 'img_label' in list(self.nim[elem].keys()) :
                label=self.nim[elem]['img_label']
        if elem in list(self.nim.keys()) and 'input' in list(self.nim[elem].keys()) and self.nim[elem]['input'] :
            #  Preserve job dictionary, if it exists :
            if elem=='job' and len(self.nim[elem]['Dict']) :
                self.nim[elem]={'name': '', 'ID': None, 'Dict': self.nim[elem]['input'], \
                    'input': self.nim[elem]['input'], 'inputID': None}
            else :
                self.nim[elem]={'name': '', 'ID': None, 'Dict': {}, 'input': self.nim[elem]['input'], 'inputID': None}
        else :
            self.nim[elem]={'name': '', 'ID': None, 'Dict': {}, 'input': None, 'inputID': None}
        #  Re-set image pixmap and label :
        if elem in ['asset', 'shot'] and elem in list(self.nim.keys()) :
            if pic : self.nim[elem]['img_pix']=pic
            if label : self.nim[elem]['img_label']=label
        #  Add Task folder :
        if elem=='task' :
            self.nim[elem]['folder']=''
        #  Initiate Filter :
        if elem=='filter' :
            self.nim[elem]['name']='Work'
        
        return
    
    def ingest_prefs(self) :
        'Sets NIM dictionary from preferences'
        self.app=F.get_app()
        self.prefs=Prefs.read()
        
        if not self.prefs :
            return False

        P.info( 'Preferences being read...' )

        #  Set User Information :
        user=self.prefs['NIM_User']
        userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False )
        if userID :
            if type(userID)==type(list()) and len(userID)==1 :
                userID=userID[0]['ID']
            try : self.nim['user']={'name': user, 'ID': str(userID) }
            except :
                self.nim['user']={'name': '', 'ID': ''}
                P.warning( 'Unable to set User information in NIM!' )
            
            #  Get Show/Shot Prefs :
            try :
                self.set_name( elem='job', name=self.prefs[self.app+'_Job'] )
                self.set_name( elem='asset', name=self.prefs[self.app+'_Asset'] )
                self.set_tab( _type=self.prefs[self.app+'_Tab'] )
                self.set_name( elem='show', name=self.prefs[self.app+'_Show'] )
                self.set_name( elem='shot', name=self.prefs[self.app+'_Shot'] )
                self.set_name( elem='filter', name=self.prefs[self.app+'_Filter'] )
                self.set_name( elem='task', name=self.prefs[self.app+'_Task'] )
                self.set_name( elem='base', name=self.prefs[self.app+'_Basename'] )
                self.set_name( elem='ver', name=self.prefs[self.app+'_Version'] )
            except :
                P.error( 'Sorry, unable to get NIM preferences, cannot run NIM GUI' )
                P.error( '    %s' % traceback.print_exc() )
                win.popup( title='NIM Error', msg='Sorry, unable to get NIM preferences, cannot run NIM GUI' )
                return False
            return self
        else :
            return False
    
    def ingest_filePath( self, filePath='', pub=False ) :
        'Sets NIM dictionary from current file path'
        jobFound, assetFound, showFound, shotFound=False, False, False, False
        taskFound, basenameFound, versionFound=False, False, False
        jobs, assets, shows, shots, tasks, basenames, version={}, {}, {}, {}, {}, {}, {}
        #  Get and set jobs dictionary :
        
        jobs=Api.get_jobs( userID=self.nim['user']['ID'], folders=True )
        #P.info('ingest_filePath')
        self.set_dict('job')
        
        #  Verify file path structure :
        if not filePath :
            filePath=F.get_filePath()
        if not filePath :
            P.debug( 'File must be saved with a filename that exists in NIM.' )
            return None
        if not os.path.isfile( os.path.normpath( filePath ) ) and os.path.isfile( \
                os.path.normpath( filePath ) ) :
            filePath=os.path.normpath( filePath )
        if not os.path.isfile( filePath ) :
            P.warning( 'Sorry, the given file path doesn\'t appear to exist...' )
            P.warning( '    %s' % filePath )
            return None
        
        P.debug( 'Attempting to gather API information from the following file path...' )
        P.debug( '    %s' % filePath )
        
        #  Tokenize file path :
        if len(filePath.split( '/' )) > len(filePath.split( '\\' )) :
            toks=filePath.split( '/' )
        elif len(filePath.split( '/' )) < len(filePath.split( '\\' )) :
            toks=filePath.split( '\\' )
            
        #  Initialize tab :
        self.set_tab( _type=None )
        
        #  Find Job :
        for tok in toks :
            if not jobFound :
                for job in jobs :
                    if tok==job :
                        self.set_name( elem='job', name=job )
                        self.set_ID( elem='job', ID=jobs[job] )
                        jobFound=True
                        self.set_dict('asset')
                        self.set_dict('show')
                        break
            else :
                #  Prevent Assets that might have the same name as a Shot :
                if tok in ['_DEV', 'ASSETS'] :
                    self.set_tab( _type='ASSET' )
                    continue
                #  Find Asset/Show, once Job is found :
                if not assetFound and not showFound :
                    if not assetFound and self.tab()=='ASSET' :
                        for asset in self.Dict('asset') :
                            if tok==asset['name'] :
                                self.set_name( elem='asset', name=asset['name'] )
                                self.set_ID( elem='asset', ID=asset['ID'] )
                                self.set_tab( _type='ASSET' )
                                assetFound=True
                                self.set_dict('filter')
                                if pub :
                                    self.set_name( elem='filter', name='Published' )
                                else :
                                    self.set_name( elem='filter', name='Work' )
                                self.set_dict('task')
                                break
                    if not assetFound and not showFound and self.tab() !='ASSET' :
                        for show in self.Dict('show') :
                            if tok==show['showname'] :
                                self.set_name( elem='show', name=show['showname'] )
                                self.set_ID( elem='show', ID=show['ID'] )
                                self.set_tab( _type='SHOT' )
                                showFound=True
                                self.set_dict('shot')
                                break
                #  Find Shot, once Show is found :
                if showFound and not taskFound :
                    if not shotFound :
                        for shot in self.Dict('shot') :
                            if tok==shot['name'] :
                                self.set_name( elem='shot', name=shot['name'] )
                                self.set_ID( elem='shot', ID=shot['ID'] )
                                shotFound=True
                                self.set_dict('filter')
                                if pub :
                                    self.set_name( elem='filter', name='Published' )
                                else :
                                    self.set_name( elem='filter', name='Work' )
                                self.set_dict('task')
                                break
                if assetFound or showFound :
                    if not taskFound :
                        for task in self.Dict('task') :
                            #  Substitute Task names, if necessary :
                            task_name=F.task_toAbbrev( task['name'] )
                            #  Try to find Tasks :
                            if tok==task_name or tok==task['name'] :
                                self.set_name( elem='task', name=task['name'] )
                                self.set_ID( elem='task', ID=task['ID'] )
                                taskFound=True
                                #  Get Basenames :
                                if taskFound and assetFound==True :
                                    basenames=Api.get_bases( assetID=self.ID( 'asset' ), \
                                        task=self.name( 'task' ).upper() )
                                elif taskFound and shotFound==True :
                                    basenames=Api.get_bases( shotID=self.ID( 'shot' ), \
                                        task=self.name( 'task' ).upper() )
                                break
                    elif not basenameFound :
                        for basename in basenames :
                            task_abbrev=F.task_toAbbrev( self.name( 'task' ) )
                            base_abbrev=basename['basename'].replace( '_'+self.name( 'task' )+'_', \
                                '_'+task_abbrev+'_' )
                            if tok==basename['basename'] or tok==base_abbrev :
                                self.set_name( elem='base', name=basename['basename'] )
                                basenameFound=True
                                if assetFound==True :
                                    versions=Api.get_vers( assetID=self.ID( 'asset' ), basename=self.name( 'base' ), username=self.userInfo()['name'] )
                                if shotFound==True :
                                    versions=Api.get_vers( shotID=self.ID( 'shot' ), basename=self.name( 'base' ), username=self.userInfo()['name'] )
                                break
                    elif not versionFound :
                        for version in versions :
                            task_abbrev=F.task_toAbbrev( self.name( 'task' ) )
                            ver_abbrev=version['filename'].replace( '_'+self.name( 'task' )+'_', \
                                '_'+task_abbrev+'_' )
                            if tok==version['filename'] or tok==ver_abbrev :
                                self.set_name( elem='ver', name=version['filename'] )
                                self.set_ID( elem='ver', ID=version['fileID'] )
                                versionFound=True
                                break
        
        #  Derive Server :
        if self.name( 'job' ) :
            self.set_name( elem='server', name=filePath.split( self.name( 'job' ) )[0] )
        
        #  Derive file extension :
        if F.get_ext( filePath ) :
            self.set_name( elem='fileExt', name=F.get_ext( filePath ) )
        
        P.debug( 'Derived the following API information from filepath...' )
        P.debug( '    %s' % self.Print( debug=True ) )
        
        return self
    
    #  Get Attribute Settings :
    #===------------------------------
    
    def get_elemList(self) :
        'Returns the list of valid GUI elements'
        return self.elements
    
    def get_printElemList(self) :
        'Returns the list of printable GUI element names'
        return self.print_elements
    
    def get_printElem( self, elem='job' ) :
        'Gets the printable name for a given element'
        return self.print_elements[self.elements.index( elem )]
    
    def get_comboBoxes(self) :
        'Returns the list of GUI combo box elements'
        return self.comboBoxes
    
    def get_listViews(self) :
        'Returns the list of GUI list view elements'
        return self.listViews
    
    def get_nim(self) :
        'Returns the current NIM dictionary'
        return self.nim
    
    def userInfo(self) :
        'Gets the user information - user name and ID'
        return self.nim['user']
    
    def server( self, get='' ) :
        'Gets server information'
        if get !='' :
            if get.lower() in ['input'] :
                return self.nim['server']['input']
            elif get.lower() in ['name'] :
                return self.nim['server']['name']
            elif get.lower() in ['path'] :
                return self.nim['server']['path']
            elif get.lower() in ['dict', 'dictionary'] :
                return self.nim['server']['Dict']
            elif get.lower() in ['id'] :
                return self.nim['server']['ID']
        else :
            return self.nim['server']['path']
    
    def Input( self, elem='job' ) :
        'Retrieves the input widget for a given element'
        return self.nim[elem]['input']
    
    def Dict( self, elem='job' ) :
        'Gets the dictionary associated with a given element'
        return self.nim[elem]['Dict']
    
    def name( self, elem='job' ) :
        'Gets the name of the item that an element is set to'
        return self.nim[elem]['name']
    
    def menuID( self, elem='job' ) :
        'Returns the dictionary of menu IDs.'
        return self.menuIDs[elem]
    
    def ID( self, elem='job' ) :
        'Returns the item ID of the specified element'
        return self.nim[elem]['ID']
    
    def app(self) :
        'Returns the application that NIM is running from'
        return self.nim['app']
    
    def pix( self, elem='asset' ) :
        'Retrieves the pixmap image associated with an element (only assets and shots)'
        img_pix = None
        try:
            img_pix = self.nim[elem]['img_pix']
        except:
            pass
        return img_pix
    
    def label( self, elem='asset' ) :
        'Retrieves the label that a pixmap is assigned to, for a given element (only assets and shots)'
        return self.nim[elem]['img_label']
    
    def tab(self) :
        'Retrieves whether the tab is set to "SHOT", or "ASSET"'
        return self.nim['class']
    
    def pub(self) :
        'Gets the state of the publishing checkbox'
        return self.nim['pub']
    
    def taskFolder(self) :
        'Returns the current task folder.'
        return self.nim['task']['folder']
    
    def mode(self) :
        'Gets the mode of the window'
        return self.nim['mode']
    
    def fileType(self) :
        'Returns the file extension setting'
        return self.nim['fileExt']['fileType']
    
    def filePath(self) :
        'Returns the file path'
        return self.nim['file']['path']
    
    def fileDir(self) :
        'Returns the file directory'
        return self.nim['file']['dir']
    
    def fileName(self) :
        'Returns the file name'
        return self.nim['file']['name']
    
    def version(self) :
        'Returns the file version number'
        return self.nim['file']['version']
    
    def compPath(self) :
        'Returns the comp directory path'
        return self.nim['file']['compPath']
    
    #  Set Attributes :
    #===------------------
    
    def set_userInfo( self, userName='', userID='' ) :
        'Sets the User Name and ID'
        self.nim['user']={'name': userName, 'ID': str(userID) }
        return
    
    def set_user( self, userName='' ) :
        'Sets the User Name'
        self.nim['user']['name']=userName
        return
    
    def set_userID( self, userID='' ) :
        'Sets the User ID'
        self.nim['user']['ID']=userID
        return
    
    def set_server( self, _input=None, name=None, path=None, Dict=None, ID=None ) :
        'Sets the server path in NIM'
        if _input !=None :
            self.nim['server']['input']=_input
        if name !=None :
            self.nim['server']['name']=name
        if path !=None :
            self.nim['server']['path']=path
        if Dict !=None :
            self.nim['server']['Dict']=Dict
        if ID !=None :
            self.nim['server']['ID']=ID
        return
    
    def set_input( self, elem='job', widget=None ) :
        'Sets the input widget for a given element'
        self.nim[elem]['input']=widget
        return
    
    def set_baseDict( self, Dict={} ) :
        'Sets the basename dictionary directly.'
        self.nim['base']['Dict']=Dict
        return
    
    def set_dict( self, elem='job', pub=False ) :
        'Sets the dictionary for a given element'
        #print "set_dict: %s" % elem
        dic={}
        
        if elem=='job' :
            #  Only update Job if the dictionary hasn't been set yet :
            if not self.nim[elem]['Dict'] or not len(self.nim[elem]['Dict']) :
                self.nim[elem]['Dict']=Api.get_jobs( userID=self.nim['user']['ID'] )
                if self.nim[elem]['Dict'] == False :
                    P.error("Failed to Set NIM Dictionary")
                    return False
        elif elem=='asset' :
            if self.nim['job']['ID'] :
                self.nim[elem]['Dict']=Api.get_assets( self.nim['job']['ID'] )
        elif elem=='show' :
            if self.nim['job']['ID'] :
                self.nim[elem]['Dict']=Api.get_shows( self.nim['job']['ID'] )
        elif elem=='shot' :
            if self.nim['show']['ID'] :
                self.nim[elem]['Dict']=Api.get_shots( self.nim['show']['ID'] )
        elif elem=='filter' :
            if self.nim['mode'] and self.nim['mode'].lower() in ['load', 'open', 'file'] :
                if self.nim['class']=='SHOT' :
                    if self.nim['shot']['name'] :
                        self.nim[elem]['Dict']=['Published', 'Work']
                elif self.nim['class']=='ASSET' :
                    if self.nim['asset']['name'] :
                        if self.nim['mode'].lower() not in ['file','open'] :
                            self.nim[elem]['Dict']=['Asset Master', 'Published', 'Work']
                        else :
                            self.nim[elem]['Dict']=['Published', 'Work']
            else :
                self.nim[elem]['Dict']=['Work']
        

        elif elem=='task' :
            #REMOVED AS REDUNDANT
            #if self.nim['mode'] and self.nim['mode'].lower() in ['load', 'open', 'file'] :
            
            # WAS INSIDE IF
            if self.nim['filter']['name'] not in ['Select...', 'None', ''] and self.nim['filter']['name'] !='Asset Master' :
                
                #NOT INCLUDING CLASS WHEN LOADING TASKS
                #self.nim[elem]['Dict']=Api.get( {'q': 'getTaskTypes', 'app': self.nim['app'].upper()} )

                #print "Loading %s tasks" % self.nim['class']

                if self.nim['class']=='SHOT' :
                    if self.nim['shot']['name'] not in ['Select...', 'None', ''] :
                        #self.nim[elem]['Dict']=Api.get( {'q': 'getTaskTypes', 'app': self.nim['app'].upper()} )
                        self.nim[elem]['Dict']=Api.get_tasks(app=self.nim['app'].upper(), shotID=self.nim['shot']['ID'])
                elif self.nim['class']=='ASSET' :
                    if self.nim['asset']['name'] not in ['Select...', 'None', ''] :
                        #self.nim[elem]['Dict']=Api.get( {'q': 'getTaskTypes', 'app': self.nim['app'].upper()} )
                        self.nim[elem]['Dict']=Api.get_tasks(app=self.nim['app'].upper(), assetID=self.nim['asset']['ID'])

            elif self.nim['filter']['name']=='Asset Master' :
                self.nim[elem]['Dict']={}

            # REMOVED AS REDUNDANT
            #else :
            #    if self.nim['class']=='SHOT' :
            #        if self.nim['shot']['name'] not in ['Select...', 'None', ''] :
            #            #self.nim[elem]['Dict']=Api.get( {'q': 'getTaskTypes', 'app': self.nim['app'].upper()} )
            #            self.nim[elem]['Dict']=Api.get_tasks(app=self.nim['app'].upper(), shotID=self.nim['shot']['ID'])
            #    elif self.nim['class']=='ASSET' :
            #        if self.nim['asset']['name'] not in ['Select...', 'None', ''] :
            #            #self.nim[elem]['Dict']=Api.get( {'q': 'getTaskTypes', 'app': self.nim['app'].upper()} )
            #            self.nim[elem]['Dict']=Api.get_tasks(app=self.nim['app'].upper(), assetID=self.nim['asset']['ID'])

        elif elem=='base' :
            if self.nim['filter']['name']=='Published' :
                if self.nim['class']=='SHOT' and self.nim['task']['name'] :
                    self.nim[elem]['Dict']=Api.get_basesAllPub( shotID=self.nim['shot']['ID'], taskID=self.nim['task']['ID'], username=self.userInfo()['name'] )
                elif self.nim['class']=='ASSET' and self.nim['task']['name'] :
                    self.nim[elem]['Dict']=Api.get_basesAllPub( assetID=self.nim['asset']['ID'], taskID=self.nim['task']['ID'], username=self.userInfo()['name'] )
            else :
                if self.nim['class']=='SHOT' and self.nim['task']['name'] :
                    self.nim[elem]['Dict']=Api.get_bases( shotID=self.nim['shot']['ID'], taskID=self.nim['task']['ID'] )
                elif self.nim['class']=='ASSET' and self.nim['task']['name'] :
                    self.nim[elem]['Dict']=Api.get_bases( assetID=self.nim['asset']['ID'], taskID=self.nim['task']['ID'] )
        elif elem=='ver' :
            if self.nim['filter']['name']=='Published' :
                if self.nim['mode'] and self.nim['mode'].lower()=='load' :
                    if self.nim['class']=='SHOT' and self.nim['base']['name'] :
                        self.nim[elem]['Dict']=Api.get_basesPub( shotID=self.nim['shot']['ID'], basename=self.nim['base']['name'], username=self.userInfo()['name'] )
                    elif self.nim['class']=='ASSET' and self.nim['base']['name'] :
                        self.nim[elem]['Dict']=Api.get_basesPub( assetID=self.nim['asset']['ID'], basename=self.nim['base']['name'], username=self.userInfo()['name'] )
                elif self.nim['mode'] and self.nim['mode'].lower() in ['open', 'file'] :
                    if self.nim['class']=='SHOT' and self.nim['base']['name']  :
                        self.nim[elem]['Dict']=Api.get_vers( shotID=self.nim['shot']['ID'], basename=self.nim['base']['name'], pub=True, username=self.userInfo()['name'] )
                    elif self.nim['class']=='ASSET' and self.nim['base']['name'] :
                        self.nim[elem]['Dict']=Api.get_vers( assetID=self.nim['asset']['ID'], basename=self.nim['base']['name'], pub=True, username=self.userInfo()['name'] )
            elif self.nim['filter']['name']=='Asset Master' :
                assetInfo=Api.get_assetInfo( assetID=self.ID('asset') )
                amrPath=os.path.normpath( assetInfo[0]['AMR_path'] )
                fileName=assetInfo[0]['AMR_filename']
                fileDir=os.path.normpath( os.path.join( self.server(get='path'), amrPath ) )
                filePath=os.path.normpath( os.path.join( fileDir, fileName ) )
                self.nim[elem]['Dict']=[{'username': '', 'filepath': fileDir, 'userID': '', 'filename': fileName,
                    'basename': '', 'ext': '', 'version': '', 'date': '', 'note': '', 'serverID': '', 'fileID': ''}]
            else :
                if self.nim['class']=='SHOT' and self.nim['base']['name']  :
                    self.nim[elem]['Dict']=Api.get_vers( shotID=self.nim['shot']['ID'], basename=self.nim['base']['name'], username=self.userInfo()['name'] )
                elif self.nim['class']=='ASSET' and self.nim['base']['name'] :
                    self.nim[elem]['Dict']=Api.get_vers( assetID=self.nim['asset']['ID'], basename=self.nim['base']['name'], username=self.userInfo()['name'] )
        
        return
    
    def set_name( self, elem='job', name=None ) :
        'Sets the name of the selected element item'
        self.nim[elem]['name']=name
        return
    
    def set_menuID( self, elem='job', Dict={} ) :
        ''
        self.menuIDs[elem]=Dict
        return
    
    def set_ID( self, elem='job', ID=None ) :
        'Sets the ID of the selected element item'
        self.nim[elem]['ID']=ID
        return
    
    def set_pic( self, elem='asset', widget=None ) :
        'Sets the pixmap image for a given element (only assets and shots)'
        self.nim[elem]['img_pix']=widget
        return
    
    def set_label( self, elem='asset', widget=None ) :
        'Sets the label, to apply a pixmap image to, for a given element (only assets and shots)'
        self.nim[elem]['img_label']=widget
        return
    
    def set_mode( self, mode='open' ) :
        'Sets the window mode'
        self.nim['mode']=mode
        return
    
    def set_tab( self, _type='SHOT' ) :
        'Sets whether tab is set to "SHOT", or "ASSET"'
        self.nim['class']=_type
        return
    
    def set_pub( self, pub=False ) :
        'Sets the publishing state'
        self.nim['pub']=pub
        return
    
    def set_taskFolder( self, folder='' ) :
        'Sets the Task Folder.'
        self.nim['task']['folder']=folder
        return
    
    def set_mode( self, mode='FILE' ) :
        'Sets the current mode that the window is in'
        self.nim['mode']=mode
        return
    
    def set_filePath(self) :
        'Sets the file path'
        self.nim['file']['path']=F.get_filePath()
        if self.nim['file']['path'] :
            self.nim['file']['name']=ntpath.basename( self.nim['file']['path'] )
            self.nim['file']['dir']=os.path.dirname( self.nim['file']['path'] )
        else :
            self.nim['file']['name']=''
            self.nim['file']['path']=''
        self.nim['file']['basename']=None
    
    def set_fileType( self, fileType='Maya Binary' ) :
        'Sets the current file type the window is set to'
        if fileType in ['Maya Binary', 'Maya Ascii'] :
            self.nim['fileExt']['fileType']=fileType
        return
    
    def set_version( self, version='' ) :
        'Sets the file version number'
        self.nim['file']['version']=version
        return
    
    def set_compPath( self, compPath='' ) :
        'Sets the comp directory path for the project'
        self.nim['file']['compPath']=compPath
        return


#  END

