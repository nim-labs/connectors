#!/usr/bin/env python
#******************************************************************************
#
# Filename: UI.py
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import glob, os, platform, re, sys, traceback, urllib, urllib2, time
#  NIM Imports :
import nim as Nim
import nim_api as Api
import nim_file as F
import nim_prefs as Prefs
import nim_print as P
import nim_win as Win
#  Import Python GUI packages :
try : from PySide import QtCore, QtGui
except :
    try : from PyQt4 import QtCore, QtGui
    except : pass

#  Variables :
WIN=''
startTime=''
version='v1.0.2'
winTitle='NIM_'+version
_os=platform.system().lower()
_osCap=platform.system()

#  Wrapper function :
def mk( mode='open', _import=False, _export=False, ref=False, pub=False ) :

    F.scripts_reload()
    
    'Wrapper that is used to ensure only one instance of the GUI is opened'
    global startTime, WIN
    startTime=time.time()
    app=F.get_app()
    success=False
    
    if not WIN :
        P.info( '\nCreating the NIM GUI...' )
        
        #  Maya :
        if app=='Maya' :
            try :
                import maya.OpenMayaUI as omUI
                import maya.cmds as mc
                from shiboken import wrapInstance
                import nim_maya as M
                win_parent=M.get_mainWin()
                WIN=GUI( parent=win_parent, mode=mode )
                #  Make the window dockable :
                #allowedAreas=['right', 'left']
                #mc.dockControl( area='left', content=str(Singleton._inst), \
                #    allowedAreas=allowedAreas )
            except Exception, e :
                P.error( 'Sorry, unable to retrieve variables from the NIM preference file.' )
                P.error( '    %s' % traceback.print_exc() )
                return False
        
        #  Nuke :
        elif app=='Nuke' :
            try :
                import nuke, nukescripts.panels
                win_parent=QtGui.QApplication.activeWindow()
                WIN=GUI( mode=mode, parent=win_parent )
                #  Make the window Dockable :
                #from nukescripts import panels
                #panels.registerWidgetAsPanel( WIN, 'NIM_v%s File UI' % version, \
                #    'usa.la.nim.fileUI' )
            except Exception, e :
                P.error( 'Sorry, unable to retrieve variables from the NIM preference file.' )
                P.error( '    %s' % traceback.print_exc() )
                return False
        
        #  Hiero :
        elif app=='Hiero' :
            try :
                import hiero.core
                WIN=GUI( mode=mode )
            except Exception, e :
                P.error( 'Sorry, unable to retrieve variables from the NIM preference file.' )
                P.error( '    %s' % traceback.print_exc() )
                return False
    
        # 3dsMax :
        elif app=='3dsMax' :
            try :
                import MaxPlus
                #win_parent=MaxPlus.Win32_GetMAXHWnd()
                #WIN=GUI( parent=win_parent, mode=mode )
                WIN=GUI( mode=mode )
                MaxPlus.CUI.DisableAccelerators()
            except Exception, e :
                P.error( 'Sorry, unable to retrieve variables from the NIM preference file.' )
                P.error( '    %s' % traceback.print_exc() )
                return False
    #  Set the window to one of five modes :
    if WIN.complete :
        P.info( '\nStarting up the NIM File Browser, in %s mode.' % mode )
        if mode.lower() in ['open', 'file'] :
            success=WIN.win_open()
        elif mode.lower() in ['load'] :
            success=WIN.win_load( _import=_import, ref=ref, pub=pub )
        elif mode.lower() in ['save'] :
            success=WIN.win_save( _export=_export )
        elif mode.lower() in ['ver', 'verup', 'version', 'versionup'] :
            success=WIN.win_verUp()
        elif mode.lower() in ['pub', 'publish'] :
            success=WIN.win_pub()
    
    #  Show the window :
    if success :
        WIN.show()
        #  Print success :
        P.info( '  Done making the window, in %.3f seconds\n' % (time.time()-startTime) )
    
    return


#  Main Window Constructor :
class GUI(QtGui.QMainWindow) :
    
    def __init__( self, parent=None, mode='Open' ) :
        'Initializes main window'
        super( GUI, self ).__init__( parent )
        global startTime, winTitle
        self.mode=mode
        self.winTitle=winTitle
        self.complete=False
        self.baseUpdated=False
        #  Start timer :
        startTime=time.time()
        
        self.saveServerPref = False

        #  Instantiate Variables :
        try :
            stored=self.mk_vars()
        except Exception, e :
            P.error( 'Sorry, unable to get NIM preferences, cannot run NIM GUI' )
            P.error( '    %s' % traceback.print_exc() )
            return
        
        #  Error Check :
        if not stored :
            msg='Sorry, unable to get all necessary NIM preferences, cannot run NIM GUI\n'+\
                '    Would you like to recreate your preferences?'
            P.error( msg )
            reply=Win.popup( title='NIM Error', msg=msg, type='okCancel' )
            #  Re-create preferences, if prompted :
            if reply=='OK' :
                prefsFile=Prefs.get_path()
                if os.path.exists( prefsFile ) :
                    os.remove( prefsFile )
                Prefs.mk_default()
                self.mk_vars()
            else :
                return
        
        #  Position window :
        self.move( int(self.pref_posX), int(self.pref_posY) )
        #  Size window :
        self.resize( int(self.pref_sizeX), int(self.pref_sizeY) )
        
        #  Make main window widget :
        self.mainWidg=QtGui.QWidget(self)
        self.setCentralWidget( self.mainWidg )
        
        #  Construct the window :
        self.mk_win()
        
        #  Populate Fields :
        for elem in self.nim.elements :
            self.populate_elem( elem )
        P.debug(' ')
        
        #  Print :
        self.nim.Print( debug=True )
        
        #  Make connections :
        #self.mk_connections()
        
        self.complete=True
        return
    
    
    #  Variables :
    def mk_vars( self ) :
        'Instantiates variables'
        self.app=F.get_app()
        P.debug( '\n%.3f => Starting to read preferences' % (time.time()-startTime) )
        
        #  Preferences :
        self.prefs=Prefs.read()
        P.debug( '%.3f =>     Preference file done reading' % (time.time()-startTime) )
        if not self.prefs :
            return False
        #  Get debug mode :
        if 'NIM_DebugMode' in self.prefs.keys() : self.debug=self.prefs['NIM_DebugMode']
        elif 'DebugMode' in self.prefs.keys() : self.debug=self.prefs['DebugMode']
        else : return False
        if self.debug : P.debug( 'Preferences being read...' )
        
        #  Get Show/Shot Prefs :
        try :
            self.user=self.prefs['NIM_User']
            self.pref_nimScripts=self.prefs['NIM_Scripts']
            self.pref_userScripts=self.prefs['NIM_UserScripts']
            #self.pref_appScripts=self.prefs[self.app+'_Scripts']
            self.pref_posX=self.prefs[self.app+'_WinPosX']
            self.pref_posY=self.prefs[self.app+'_WinPosY']
            self.pref_sizeX=self.prefs[self.app+'_WinWidth']
            self.pref_sizeY=self.prefs[self.app+'_WinHeight']
            self.pref_styleSheetDir=self.prefs[self.app+'_StyleSheetDir']
            self.pref_useStyleSheet=self.prefs[self.app+'_UseStyleSheet']
            self.pref_job=self.prefs[self.app+'_Job']
            #self.pref_defaultServerPath=self.prefs[self.app+'_DefaultServerPath']
            self.pref_serverPath=self.prefs[self.app+'_ServerPath']
            self.pref_asset=self.prefs[self.app+'_Asset']
            self.pref_tab=self.prefs[self.app+'_Tab']
            self.pref_show=self.prefs[self.app+'_Show']
            self.pref_shot=self.prefs[self.app+'_Shot']
            self.pref_filter=self.prefs[self.app+'_Filter']
            self.pref_task=self.prefs[self.app+'_Task']
            self.pref_basename=self.prefs[self.app+'_Basename']
            self.pref_version=self.prefs[self.app+'_Version']
            #self.pref_imgDefault=self.prefs['NIM_Thumbnail']
            self.pref_imgDefault=self.pref_nimScripts+'/img/nim_logo.png'
        except : return False
        P.debug( '%.3f =>     Preferences stored' % (time.time()-startTime) )
        
        #  Instantiate NIM Dictionary :
        self.nim=Nim.NIM()
        P.debug( '%.3f =>     NIM Instantiated' % (time.time()-startTime) )
        if self.mode.lower() in ['ver', 'verup', 'version', 'versionup', 'pub', 'publish'] :
            self.nimPrefs=Nim.NIM()
            if self.app=='Maya' :
                import nim_maya as M
                M.get_vars( nim=self.nimPrefs )
            elif self.app=='Nuke' :
                import nim_nuke as N
                N.get_vars( nim=self.nimPrefs )
            elif self.app=='3dsMax' :
                import nim_3dsmax as Max
                Max.get_vars( nim=self.nimPrefs )
        else :
            self.nimPrefs=Nim.NIM().ingest_prefs()
            #self.nimPrefs.Print()
        #  Get and set User Information :
        info=self.nimPrefs.userInfo()
        self.user=info['name']
        self.userID=info['ID']
        self.nim.set_userInfo( userName=self.user, userID=self.userID )
        
        P.debug( '%.3f =>     NIM Preferences Instantiated' % (time.time()-startTime) )
        
        #  Set mode :
        self.nim.set_mode( self.mode )
        
        #  Print success :
        P.debug( '%.3f => Preferences done reading' % (time.time()-startTime) )
        
        return True
    
    
    #  GUI Element Creation :
    def mk_win(self) :
        'Creates UI Elements'
        self.mk_layouts()
        self.mk_groupBoxes()
        self.mk_jobWidgets()
        self.mk_taskWidgets()
        self.mk_verWidgets()
        self.mk_btnWidgets()
        self.mk_menuBar()
    
    
    def mk_layouts(self) :
        'Makes the central layouts for the GUI'
        #  Horizontal Splitter :
        self.horiz_splitter=QtGui.QSplitter(QtCore.Qt.Vertical)
        #  Vertical Splitter :
        self.vert_splitter=QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.horiz_splitter.addWidget( self.vert_splitter )
        
        #  Main layout :
        self.mainLayout=QtGui.QVBoxLayout( self.mainWidg )
        self.mainLayout.setSpacing(4)
        self.mainLayout.setContentsMargins(4,4,4,4)
        #  Add Layouts/Widgets :
        self.mainLayout.addWidget( self.horiz_splitter )
        #  Set Main Layout :
        self.setLayout( self.mainLayout )
        
        #  Print success :
        P.debug( '%.3f => Layouts created' % (time.time()-startTime) )
    
    
    def mk_groupBoxes(self) :
        'Makes group boxes for the main layout'
        
        #  Job box :
        self.jobBox=QtGui.QGroupBox('Job Info')
        #  Job Layout :
        self.jobLayout=QtGui.QVBoxLayout( self.jobBox )
        #  Job Form Layout :
        self.jobForm=QtGui.QFormLayout()
        self.jobLayout.addLayout( self.jobForm )
        
        #  Task box :
        self.taskBox=QtGui.QGroupBox('Task Info')
        #  Task Form Layout :
        self.taskForm=QtGui.QFormLayout( self.taskBox )
        
        #  Version box :
        self.verBox=QtGui.QGroupBox('Version Info')
        #  Version Form Layout :
        self.verForm=QtGui.QFormLayout( self.verBox )
        
        #  Button box :
        self.btnBox=QtGui.QGroupBox()
        self.btnBox.setMaximumHeight(55)
        self.mainLayout.addWidget( self.btnBox )
        #  Button Layout :
        self.btnLayout=QtGui.QHBoxLayout( self.btnBox )
        
        #  Add elements to Splitters :
        self.vert_splitter.addWidget( self.jobBox )
        self.vert_splitter.addWidget( self.taskBox )
        self.horiz_splitter.addWidget( self.verBox )
        
        #  Print success :
        P.debug( '%.3f => Group boxes created' % (time.time()-startTime) )
    
    
    def mk_jobWidgets(self) :
        'Constructs all elements of the Job group box'
        self.img_size=self.width()/2.25
        
        #  Job :
        self.nim.set_input( elem='job', widget=QtGui.QComboBox() )
        self.nim.Input('job').setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.nim.Input('job').setMinimumSize(240,20)
        self.jobForm.addRow( 'Job:', self.nim.Input('job') )
        
        #  Server :
        self.nim.set_input( elem='server', widget=QtGui.QComboBox() )
        self.nim.Input('server').setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.nim.Input('server').setMinimumSize(240,20)
        self.jobForm.addRow( 'Server:', self.nim.Input('server') )
        
        #  Asset :
        self.nim.set_input( elem='asset', widget=QtGui.QComboBox() )
        self.nim.Input('asset').setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.nim.Input('asset').setMinimumSize(240,20)
        #  Asset thumbnail :
        self.nim.set_pic( elem='asset', widget=QtGui.QPixmap().fromImage( \
            QtGui.QImage( self.pref_imgDefault ) ) )
        self.nim.set_pic( elem='asset', widget=self.nim.pix( 'asset' ).scaled( \
            self.img_size, self.img_size, QtCore.Qt.KeepAspectRatio ) )
        self.nim.set_label( elem='asset', widget=QtGui.QLabel() )
        self.nim.label('asset').setPixmap( self.nim.pix('asset') )
        self.nim.label('asset').setScaledContents( True )
        #  Asset Tab :
        self.assetTab=QtGui.QWidget()
        #  Asset Tab Layouts :
        self.assetLayout=QtGui.QVBoxLayout( self.assetTab )
        self.assetForm=QtGui.QFormLayout()
        self.assetLayout.addLayout( self.assetForm )
        self.assetLayout.addWidget( self.nim.label('asset'), QtCore.Qt.AlignTop )
        #  Populate Asset Tab :
        self.assetForm.addRow( 'Asset:', self.nim.Input('asset') )
        
        #  Show :
        self.nim.set_input( elem='show', widget=QtGui.QComboBox() )
        self.nim.Input('show').setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.nim.Input('show').setMinimumSize(240,20)
        
        #  Shot :
        self.nim.set_input( elem='shot', widget=QtGui.QComboBox() )
        self.nim.Input('shot').setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.nim.Input('shot').setMinimumSize(240,20)
        #  Shot thumbnail :
        self.nim.set_pic( elem='shot', widget=QtGui.QPixmap().fromImage( \
            QtGui.QImage( self.pref_imgDefault ) ) )
        self.nim.set_pic( elem='shot', widget=self.nim.pix( 'shot' ).scaled(
            self.img_size, self.img_size, QtCore.Qt.KeepAspectRatio ) )
        self.nim.set_label( elem='shot', widget=QtGui.QLabel() )
        self.nim.label('shot').setPixmap( self.nim.pix( 'shot' ) )
        self.nim.label('shot').setScaledContents( True )
        
        #  Show/Shot Tab :
        self.showTab=QtGui.QWidget()
        
        #  Show Tab Layouts :
        self.showLayout=QtGui.QVBoxLayout( self.showTab )
        self.showForm=QtGui.QFormLayout()
        self.showLayout.addLayout( self.showForm )
        self.showLayout.addWidget( self.nim.label('shot'), QtCore.Qt.AlignTop )
        #  Populate Show/Shot Tab :
        self.showForm.addRow( 'Show:', self.nim.Input('show') )
        self.showForm.addRow( 'Shot:', self.nim.Input('shot') )
        
        #  Tab :
        self.jobTab=QtGui.QTabWidget()
        self.jobLayout.addWidget( self.jobTab )
        self.vert_splitter.setSizes([10,150])
        #  Add tabs to tab widget :
        self.jobTab.addTab( self.assetTab, 'Assets' )
        self.jobTab.addTab( self.showTab, 'Show/Shot' )
        
        #  Set tab from preferences :
        if self.pref_tab=='ASSET' :
            self.jobTab.setCurrentIndex(0)
            self.nim.set_tab('ASSET')
        elif self.pref_tab=='SHOT' :
            self.jobTab.setCurrentIndex(1)
            self.nim.set_tab('SHOT')
        
        #  Print success :
        P.debug( '%.3f => Job widgets created' % (time.time()-startTime) )
    
    
    def mk_taskWidgets(self) :
        'Constructs all elements of the Task group box'
        
        #  File Filter widget :
        self.nim.set_input( elem='filter', widget=QtGui.QComboBox() )
        self.nim.Input('filter').setSizePolicy( QtGui.QSizePolicy.Expanding, \
            QtGui.QSizePolicy.Minimum )
        self.nim.Input('filter').setMinimumSize(240,20)
        self.taskForm.addRow( 'Filter:', self.nim.Input('filter') )
        
        #  Task widgets :
        self.nim.set_input( elem='task', widget=QtGui.QComboBox() )
        self.nim.Input('task').setSizePolicy( QtGui.QSizePolicy.Expanding, \
            QtGui.QSizePolicy.Minimum )
        self.nim.Input('task').setMinimumSize(240,20)
        self.taskForm.addRow( 'Task:', self.nim.Input('task') )
        
        #  Basename widget :
        self.nim.set_input( elem='base', widget=QtGui.QListWidget() )
        baseSP=self.nim.Input('base').sizePolicy()
        baseSP.setVerticalStretch(1)
        self.nim.Input('base').setSizePolicy( baseSP )
        self.taskForm.addRow( 'Basename:', self.nim.Input('base') )
        
        #  Tag widget :
        self.nim.set_input( elem='tag', widget=QtGui.QLineEdit() )
        self.taskForm.addRow( 'Tag:', self.nim.Input('tag') )
        
        #  Deselect basename button :
        self.btn_deselect=QtGui.QPushButton('Deselect Basenames')
        self.btn_deselect.clicked.connect( self.base_deselect )
        self.taskForm.addRow( self.btn_deselect )
        
        #  Print success :
        P.debug( '%.3f => Task widgets created' % (time.time()-startTime) )
    
    
    def mk_verWidgets(self) :
        'Constructs all elements of the Version group box'
        
        #  Version Widgets :
        self.nim.set_input( elem='ver', widget=QtGui.QListWidget() )
        self.nim.Input('ver').setMinimumHeight(40)
        verSP=self.nim.Input('ver').sizePolicy()
        verSP.setVerticalStretch(1)
        self.nim.Input('ver').setSizePolicy( verSP )
        self.verPath=QtGui.QLabel('<path>')
        self.verUser=QtGui.QLabel('<user>')
        self.verDate=QtGui.QLabel('<date>')
        self.verNote=QtGui.QLabel('<comment>')
        self.nim.set_input( elem='comment', widget=QtGui.QLineEdit() )
        #  Add widgets to form :
        self.verForm.addRow( 'Versions:', self.nim.Input('ver') )
        self.verForm.addRow( 'Path:', self.verPath )
        self.verForm.addRow( 'User:', self.verUser )
        self.verForm.addRow( 'Date:', self.verDate )
        self.verForm.addRow( 'Comment:', self.verNote )
        self.verForm.addRow( 'Comment:', self.nim.Input('comment') )
        
        #  Print success :
        P.debug( '%.3f => Version widgets created' % (time.time()-startTime) )
    
    
    def mk_btnWidgets(self) :
        'Constructs all elements of the Button group box'
        
        #  Buttons :
        self.btn_1=QtGui.QPushButton()
        self.btn_2=QtGui.QPushButton()
        #  Add to form :
        self.btnLayout.addWidget( self.btn_1 )
        self.btnLayout.addWidget( self.btn_2 )
        
        #  File Extension :
        self.fileExtText=QtGui.QLabel('File Extension:')
        self.fileExtText.setMaximumWidth(70)
        self.nim.set_input( elem='fileExt', widget=QtGui.QComboBox() )
        self.nim.Input('fileExt').setMaximumWidth(55)
        self.nim.Input('fileExt').addItem('.ma')
        self.nim.Input('fileExt').addItem('.mb')
        self.nim.Input('fileExt').setCurrentIndex(1)
        #  Add to layout :
        self.btnLayout.addWidget( self.fileExtText )
        self.btnLayout.addWidget( self.nim.Input('fileExt') )
        
        #  Check Boxes :
        self.checkBox=QtGui.QCheckBox('Group')
        self.checkBox.setMaximumWidth(68)
        #  Create layout :
        self.btnVLayout=QtGui.QVBoxLayout()
        self.btnVLayout.addWidget( self.checkBox )
        #  Add to layout :
        self.btnLayout.addLayout( self.btnVLayout )
        
        #  Print success :
        P.debug( '%.3f => Button widgets created' % (time.time()-startTime) )
    
    
    def mk_menuBar(self) :
        'Creates the menu bar for the window'
        
        
        #  User Menu Drop-Down :
        #===-------------------------------
        
        userMenu=QtGui.QMenu( 'User', self )
        self.changeUserAction=QtGui.QAction( 'Change User', self )
        self.changeUser=userMenu.addAction( self.changeUserAction )
        self.menuBar().addMenu( userMenu )
        #  Make Connections :
        self.changeUserAction.triggered.connect( self.update_user )
        
        #  Mode Menu Drop-Down :
        #===--------------------------------
        
        modeMenu=QtGui.QMenu( 'Mode', self )
        modeGroup=QtGui.QActionGroup( self, exclusive=True )
        #  Make menu items :
        self.openWin=modeGroup.addAction( QtGui.QAction( 'Open', self, checkable=True ) )
        self.loadWin=modeGroup.addAction( QtGui.QAction( 'Load', self, checkable=True ) )
        self.saveWin=modeGroup.addAction( QtGui.QAction( 'Save', self, checkable=True ) )
        self.verWin=modeGroup.addAction( QtGui.QAction( 'Version Up', self, checkable=True ) )
        self.pubWin=modeGroup.addAction( QtGui.QAction( 'Publish', self, checkable=True ) )
        #  Set shortcuts :
        self.openWin.setShortcut('Ctrl+O')
        self.loadWin.setShortcut('Ctrl+L')
        self.saveWin.setShortcut('Ctrl+S')
        self.verWin.setShortcut('Ctrl+V')
        self.pubWin.setShortcut('Ctrl+P')
        #  Add menu items to menu :
        modeMenu.addAction( self.openWin )
        modeMenu.addAction( self.loadWin )
        modeMenu.addAction( self.saveWin )
        modeMenu.addAction( self.verWin )
        modeMenu.addAction( self.pubWin )
        self.menuBar().addMenu( modeMenu )
        
        #  Make Connections :
        self.openWin.triggered.connect( self.win_open )
        self.loadWin.triggered.connect( self.win_load )
        self.saveWin.triggered.connect( self.win_save )
        self.verWin.triggered.connect( self.win_verUp )
        self.pubWin.triggered.connect( self.win_pub )
        
        
        #  Style Sheet Menu :
        #===------------------------
        
        self.cssFiles=glob.glob( self.pref_styleSheetDir+'*.css' )
        self.cssFiles.append('None')
        #  Add menu items to menu :
        if self.cssFiles :
            nimSrch=re.compile('^nim_')
            
            #  Make the Style Sheet menu and group :
            styleMenu=QtGui.QMenu( 'Style', self )
            self.styleGroup=QtGui.QActionGroup( self, exclusive=True )
            #  Add the menu to the menu bar :
            self.menuBar().addMenu( styleMenu )
            
            #  Iterate over CSS files :
            self.menuItems, self.menuItemsText=[], []
            for index in range(len(self.cssFiles)) :
                fileName=os.path.basename( self.cssFiles[index] )
                #  Add menu item :
                if nimSrch.match( fileName ) :
                    self.menuItemsText.append( re.sub( '([a-z])([A-Z])', '\g<1> \g<2>', fileName[4:-4] ).title() )
                    self.menuItems.append( self.styleGroup.addAction( QtGui.QAction( \
                        self.menuItemsText[-1], self, checkable=True ) ) )
                elif self.cssFiles[index] != 'None' :
                    self.menuItemsText.append( fileName[:-4] )
                    self.menuItems.append( self.styleGroup.addAction( QtGui.QAction( \
                        self.menuItemsText[-1], self, checkable=True ) ) )
                else :
                    self.menuItems.append( self.styleGroup.addAction( QtGui.QAction( 'None', self, \
                        checkable=True ) ) )
                styleMenu.addAction( self.menuItems[-1] )
                #  Connect menu item :
                self.menuItems[-1].triggered.connect( self.update_styleSheet )
        
        #  Print success :
        P.debug( '%.3f => Menu bar created' % (time.time()-startTime) )
    
    
    #  Customize Window :
    def win_open(self) :
        'Modifies the GUI to function as a File Browser'
        self.complete=False
        
        self.setWindowTitle( '%s - Open Files' % self.winTitle )
        self.nim.set_mode('open')
        #  Check menu item :
        self.openWin.setChecked( True )
        #  Populate the window elements :
        self.nim.set_filePath()
        self.nimPrefs=Nim.NIM().ingest_prefs()
        
        #  Refresh the window :
        self.del_connections()
        self.update_elem('job')
        self.mk_connections()
        
        #  Print :
        self.nim.Print( debug=True )
        
        #  Server :
        self.nim.Input('server').setVisible( False )
        self.jobForm.labelForField( self.nim.Input('server') ).setVisible( False )
        
        #  Filter :
        self.nim.Input('filter').setVisible( True )
        self.taskForm.labelForField( self.nim.Input('filter') ).setVisible( True )
        
        #  Enable Basenames :
        self.nim.Input('base').setEnabled( True )
        for index in range( self.nim.Input('base').count() ) :
            self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
        self.nim.Input('base').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Tag elements :
        self.taskForm.labelForField( self.nim.Input('tag') ).setVisible( False )
        self.nim.Input('tag').setVisible( False )
        
        #  Enable Versions :
        self.nim.Input('ver').setEnabled( True )
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Comment :
        self.verNote.setVisible( True )
        self.verForm.labelForField( self.verNote ).setVisible( True )
        self.verForm.labelForField( self.nim.Input('comment') ).setVisible( False )
        self.nim.Input('comment').setVisible( False )
        
        #  Check Boxes :
        self.checkBox.setVisible( False )
        
        #  Buttons :
        if self.app=='Nuke' : self.btn_1.setText('Open Comp')
        else : self.btn_1.setText('Open')
        self.btn_1.setVisible( True )
        self.btn_2.setVisible( False )
        
        #  File Extension elements :
        self.fileExtText.setVisible( False )
        self.nim.Input('fileExt').setVisible( False )
        
        #  Enable :
        for elem in ['job', 'server', 'asset', 'show', 'shot', 'task', 'base'] :
            self.nim.Input( elem ).setEnabled( True )
        self.jobTab.setEnabled( True )
        
        #  Enable version picker :
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Make Connections :
        try : self.btn_1.clicked.disconnect()
        except : pass
        self.btn_1.clicked.connect( self.file_open )
        
        self.complete=True
        return True
    
    
    def win_save(self, _export=False) :
        'Modifies the GUI to function as a Save As window'
        self.complete=False
        
        self.setWindowTitle( '%s - Save Files' % self.winTitle )
        self.nim.set_mode('save')
        #  Check menu item :
        self.saveWin.setChecked( True )
        #  Populate the window elements :
        self.nim.set_filePath()
        self.nimPrefs=Nim.NIM().ingest_prefs()
        #  Refresh the window :
        self.del_connections()
        self.update_elem('job')
        self.mk_connections()
        
        #  Print :
        self.nim.Print( debug=True )
        
        #  Server :
        self.nim.Input('server').setVisible( True )
        self.jobForm.labelForField( self.nim.Input('server') ).setVisible( True )
        
        #  Filter :
        self.nim.Input('filter').setVisible( False )
        self.taskForm.labelForField( self.nim.Input('filter') ).setVisible( False )
        
        #  Enable Basenames :
        self.nim.Input('base').setEnabled( True )
        for index in range( self.nim.Input('base').count() ) :
            self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
        self.nim.Input('base').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Tag elements :
        self.taskForm.labelForField( self.nim.Input('tag') ).setVisible( True )
        self.nim.Input('tag').clear()
        self.nim.Input('tag').setVisible( True )
        
        #  Disable Versions :
        self.nim.Input('ver').setEnabled( False )
        for index in range( self.nim.Input('ver').count() ) :
            self.nim.Input('ver').item( index ).setFlags( QtCore.Qt.ItemIsEditable )
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.NoSelection )
        
        #  Comment :
        self.verNote.setVisible( False )
        self.verForm.labelForField( self.verNote ).setVisible( False )
        self.verForm.labelForField( self.nim.Input('comment') ).setVisible( True )
        self.nim.Input('comment').setVisible( True )
        self.nim.Input('comment').clear()
        
        #  Check Boxes :
        self.checkBox.setText( 'Selected' )
        self.checkBox.setMaximumWidth( 68 )
        self.checkBox.setVisible( True )
        if _export :
            self.checkBox.setCheckState( QtCore.Qt.Checked )
        else :
            self.checkBox.setCheckState( QtCore.Qt.Unchecked )
        
        #  Buttons :
        self.btn_1.setText( 'Save As' )
        self.btn_1.setVisible( True )
        self.btn_2.setVisible( False )
        
        #  File Extension elements :
        if self.app=='Maya' :
            self.nim.set_fileType( fileType='Maya Binary' )
            self.nim.set_name( elem='fileExt', name=self.nim.Input( 'fileExt' ).currentText() )
            self.fileExtText.setVisible( True )
            self.nim.Input('fileExt').setVisible( True )
        else :
            self.fileExtText.setVisible( False )
            self.nim.Input('fileExt').setVisible( False )
        if self.app=='Nuke' :
            self.nim.set_name( elem='fileExt', name='.nk' )
        elif self.app=='C4D' :
            self.nim.set_name( elem='fileExt', name='.c4d' )
        elif self.app=='3dsMax' :
            self.nim.set_name( elem='fileExt', name='.max' )
        
        #  Enable :
        for elem in ['job', 'server', 'asset', 'show', 'shot', 'task', 'base'] :
            self.nim.Input( elem ).setEnabled( True )
        self.jobTab.setEnabled( True )
        
        #  Enable version picker :
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Make Connections :
        try : self.btn_1.clicked.disconnect()
        except : pass
        self.btn_1.clicked.connect( self.file_saveAs )
        
        self.complete=True
        return True
    
    
    def win_load(self, _import=False, ref=False, pub=False) :
        'Modifies the GUI to function as a File Loader'
        self.complete=False
        
        self.setWindowTitle( '%s - Load Files' % self.winTitle )
        self.nim.set_mode('load')
        #  Check menu item :
        self.loadWin.setChecked( True )
        #  Populate the window elements :
        self.nim.set_filePath()
        self.nimPrefs=Nim.NIM().ingest_prefs()
        #  Refresh the window :
        self.del_connections()
        self.update_elem('job')
        self.mk_connections()
        
        #  Print :
        self.nim.Print( debug=True )
        
        #  Server :
        self.nim.Input('server').setVisible( False )
        self.jobForm.labelForField( self.nim.Input('server') ).setVisible( False )
        
        #  Filter :
        self.nim.Input('filter').setVisible( True )
        self.taskForm.labelForField( self.nim.Input('filter') ).setVisible( True )
        
        #  Enable Basenames :
        self.nim.Input('base').setEnabled( True )
        for index in range( self.nim.Input('base').count() ) :
            self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
        self.nim.Input('base').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Tag elements :
        self.taskForm.labelForField( self.nim.Input('tag') ).setVisible( False )
        self.nim.Input('tag').setVisible( False )
        
        #  Enable Versions :
        self.nim.Input('ver').setEnabled( True )
        for index in range( self.nim.Input('ver').count() ) :
            self.nim.Input('ver').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Comment :
        self.verNote.setVisible( True )
        self.verForm.labelForField( self.verNote ).setVisible( True )
        self.verForm.labelForField( self.nim.Input('comment') ).setVisible( False )
        self.nim.Input('comment').setVisible( False )
        
        #  Check Boxes :
        if self.app=='Maya' :
            self.checkBox.setText('Group')
            self.checkBox.setMaximumWidth(68)
            self.checkBox.setVisible( True )
        elif self.app=='3dsMax' :
            self.checkBox.setText('Group')
            self.checkBox.setMaximumWidth(68)
            self.checkBox.setVisible( True )
        else :
            self.checkBox.setVisible( False )
        
        #  Buttons :
        self.btn_1.setText('Import')
        self.btn_2.setText('Reference')
        if _import and not ref :
            self.btn_1.setVisible( True )
            self.btn_2.setVisible( False )
        elif not _import and ref :
            self.btn_1.setVisible( False )
            self.btn_2.setVisible( True )
        else :
            self.btn_1.setVisible( True )
            if self.app=='Maya' :
                self.btn_2.setVisible( True )
            elif self.app=='Nuke' :
                self.btn_2.setVisible( False )
            elif self.app=='3dsMax' :
                self.btn_2.setVisible( True )
        
        #  File Extension elements :
        self.fileExtText.setVisible( False )
        self.nim.Input( 'fileExt' ).setVisible( False )
        
        #  Enable :
        for elem in ['job', 'server', 'asset', 'show', 'shot', 'task', 'base'] :
            if elem=='task' and self.nim.name('filter')=='Asset Master' : pass
            else : self.nim.Input( elem ).setEnabled( True )
        self.jobTab.setEnabled( True )
        
        #  Enable version picker :
        self.nim.Input( 'ver' ).setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Make Connections :
        try : self.btn_1.clicked.disconnect()
        except : pass
        try : self.btn_2.clicked.disconnect()
        except : pass
        self.btn_1.clicked.connect( self.file_import )
        if self.app=='Maya' :
            self.btn_2.clicked.connect( self.maya_fileReference )
        if self.app=='3dsMax' :
            #TODO
            pass

        self.complete=True
        return True
    
    
    def win_verUp(self) :
        'Modifies the GUI to function as a Version Up window'
        
        self.setWindowTitle( '%s - Version Up Files' % self.winTitle )
        
        self.nim.set_mode( mode='verup' )
        
        self.nim.set_filePath()
        
        #  Print :
        self.nim.Print( debug=True )
        
        #  Button elements :
        self.btn_1.setText( 'Version Up' )
        self.btn_2.setVisible( False )
        
        return True
    
    
    def win_pub( self, mode='', run_update=True ) :
        'Modifies the GUI to function as a Publish window'
        self.complete=False
        
        self.setWindowTitle( '%s - Publish Files' % self.winTitle )
        self.nim.set_mode( mode='publish' )
        #  Check menu item :
        self.pubWin.setChecked( True )
        
        if self.nim.app()=='Maya' :
            import nim_maya as M
            M.get_vars( nim=self.nim )
            M.get_vars( nim=self.nimPrefs )
        elif self.nim.app()=='Nuke' :
            import nim_nuke as N
            N.get_vars( nim=self.nim )
            N.get_vars( nim=self.nimPrefs )
        if self.nim.app()=='3dsMax' :
            import nim_3dsmax as Max
            Max.get_vars( nim=self.nim )
            Max.get_vars( nim=self.nimPrefs )

        #  Populate the window elements :
        self.nim.set_filePath()
        
        #  Refresh the window :
        self.del_connections()
        self.update_elem('job')
        self.mk_connections()
        
        #  Server :
        self.nim.Input('server').setVisible( True )
        self.jobForm.labelForField( self.nim.Input('server') ).setVisible( True )
        
        #  Filter :
        self.nim.Input('filter').setVisible( False )
        self.taskForm.labelForField( self.nim.Input('filter') ).setVisible( False )
        
        #  Enable basenames :
        self.nim.Input('base').setEnabled( True )
        for index in range( self.nim.Input('base').count() ) :
            self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
        self.nim.Input('base').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        
        #  Tag elements :
        self.taskForm.labelForField( self.nim.Input('tag') ).setVisible( False )
        self.nim.Input('tag').setVisible( False )
        
        #  Disable :
        for elem in ['job', 'server', 'asset', 'show', 'shot', 'task', 'base'] :
            self.nim.Input( elem ).setEnabled( False )
        self.jobTab.setEnabled( False )
        
        #  Disable Versions :
        self.nim.Input('ver').setEnabled( False )
        for index in range( self.nim.Input('ver').count() ) :
            self.nim.Input('ver').item( index ).setFlags( QtCore.Qt.ItemIsEditable )
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.NoSelection )
        
        #  Comment :
        self.verNote.setVisible( False )
        self.verForm.labelForField( self.verNote ).setVisible( False )
        self.verForm.labelForField( self.nim.Input('comment') ).setVisible( True )
        self.nim.Input('comment').setVisible( True )
        self.nim.Input('comment').clear()
        
        #  Check Boxes :
        self.checkBox.setText('Pub SymLink')
        self.checkBox.setMaximumWidth(90)
        self.checkBox.setCheckState( QtCore.Qt.Checked )
        self.checkBox.setVisible( True )
        
        #  Button elements :
        self.btn_1.setText('Publish')
        self.btn_1.setVisible( True )
        self.btn_2.setVisible( False )
        
        #  File Extension elements :
        if self.app=='Maya' :
            self.fileExtText.setVisible( True )
            self.nim.Input('fileExt').setVisible( True )
        elif self.app=='Nuke' :
            self.nim.set_name( elem='fileExt', name='.nk' )
            self.fileExtText.setVisible( False )
            self.nim.Input('fileExt').setVisible( False )
        elif self.app=='C4D' :
            self.nim.set_name( elem='fileExt', name='.c4d' )
            self.fileExtText.setVisible( False )
            self.nim.Input('fileExt').setVisible( False )
        elif self.app=='3dsMax' :
            self.nim.set_name( elem='fileExt', name='.max' )
            self.fileExtText.setVisible( False )
            self.nim.Input('fileExt').setVisible( False )
        
        #  Disable version picker :
        self.nim.Input('ver').setSelectionMode( QtGui.QAbstractItemView.NoSelection )
        
        #  Connections :
        try : self.btn_1.clicked.disconnect()
        except : pass
        self.btn_1.clicked.connect( self.file_pub )
        
        self.complete=True
        return True
    
    
    def win_code(self) :
        ''
        self.setWindowTitle( '%s - Code' % self.winTitle )
        
        return

    
    #  Update :
    def populate_elem( self, elem='job', _print=False ) :
        'Populates a given GUI element'
        P.debug( '%.3f => %s started' % ((time.time()-startTime), elem.upper() ) )
        
        
        #  Clear :
        #===------
        
        #  Clear and Set Dictionaries :
        self.nim.clear( elem )
        self.nim.set_dict( elem )
        
        #  Clear Fields for Empty Dictionaries :
        if not self.nim.Dict( elem ) or not len(self.nim.Dict( elem )) :
            if elem in self.nim.comboBoxes :
                self.nim.Input( elem ).clear()
                self.nim.Input( elem ).addItem( 'None' )
                self.nim.Input( elem ).setEnabled( False )
            elif elem in self.nim.listViews :
                self.nim.Input( elem ).clear()
                if elem=='ver' :
                    self.verPath.setText('<path>')
                    self.verUser.setText('<user>')
                    self.verDate.setText('<date>')
                    self.verNote.setText('<comment>')
            #  Print Time :
            try :
                P.debug( '  Text = "%s"' % self.nim.Input( elem ).currentText() )
                P.debug( '%.3f => %s finished' % ((time.time()-startTime), elem.upper() ) )
            except : pass
            return
        #  Clear tasks, if necessary :
        if elem=='task' :
            if self.nim.name('filter')=='Asset Master' : clear=True
            else : clear=False
            if self.nim.tab()=='SHOT' :
                if self.nim.Input('shot').currentText() in ['Select...', 'None', ''] : clear=True
            elif self.nim.tab()=='ASSET' :
                if self.nim.Input('asset').currentText() in ['Select...', 'None', ''] : clear=True
            if clear :
                self.nim.Input( elem ).clear()
                self.nim.Input( elem ).addItem('None')
                self.nim.Input( elem ).setEnabled( False )
                return
        
        
        #  Print Population Start :
        if _print : P.info( '  Populating %s...' % self.nim.get_printElem( elem ).upper() )
        else : P.debug( '  Populating %s...' % self.nim.get_printElem( elem ).upper() )
        
        
        #  Combo Boxes :
        #===-------------------
        
        if elem in self.nim.comboBoxes :
            num=1
            elemList=[]
            #  Initialize Combo Box :
            self.nim.Input( elem ).setEnabled( True )
            self.nim.Input( elem ).clear()
            self.nim.Input( elem ).addItem( 'Select...' )
            #  Make List of Element Items :
            for option in self.nim.Dict( elem ) :
                #  Assets, Shots and Tasks :
                if elem in ['asset', 'shot', 'task'] :
                    elemList.append( option['name'] )
                    #  Store Name, ID and Task Folder :
                    if option['name']==self.nimPrefs.name( elem ) :
                        self.nim.set_name( elem=elem, name=option['name'] )
                        self.nim.set_ID( elem=elem, ID=option['ID'] )
                        P.info( '  %s Name = "%s"' % (elem.upper(), self.nim.name(elem)) )
                        P.info( '  %s ID = "%s"' % (elem.upper(), self.nim.ID()) )
                        if elem=='task' :
                            self.nim.set_taskFolder( folder=option['folder'] )
                #  Shows :
                elif elem in ['show'] :
                    elemList.append( option['showname'] )
                    #  Store Name and ID :
                    if option['showname']==self.nimPrefs.name( elem ) :
                        self.nim.set_name( elem=elem, name=option['showname'] )
                        self.nim.set_ID( elem=elem, ID=option['ID'] )
                        P.info( '  %s Name = "%s"' % (elem.upper(), self.nim.name(elem)) )
                        P.info( '  %s ID = "%s"' % (elem.upper(), self.nim.ID(elem)) )
                #  Jobs, Tasks and Filters :
                else :
                    elemList.append( option )
                    #  Store Name and ID :
                    if option==self.nimPrefs.name( elem ) :
                        self.nim.set_name( elem=elem, name=option )
                        P.info( '  %s Name = "%s"' % (elem.upper(), self.nim.name(elem)) )
                        if elem not in ['task', 'filter'] :
                            self.nim.set_ID( elem=elem, ID=self.nim.Dict( elem )[option] )
                            P.info( '  %s ID = "%s"' % (elem.upper(), self.nim.ID()) )
                num +=1
            
            #  Sort Combo Box Item Names :
            elemList=sorted(elemList)
            if elem=='job' :
                elemList=sorted(elemList, reverse=True)
            
            #  Populate :
            self.nim.Input( elem ).addItems( elemList )
            
            #  Set Combo Box :
            if self.nim.name( elem ) :
                for num in range(len(elemList)) :
                    if elemList[num]==self.nim.name( elem ) :
                        self.nim.Input( elem ).setEnabled( True )
                        self.nim.Input( elem ).setCurrentIndex( num+1 )
                        break
            #  Set Filter - ("Work") :
            if elem=='filter' and self.nim.mode().lower() not in ['file', 'open', 'load'] :
                self.nim.Input( elem ).setCurrentIndex(1)
            #  Populate Server :
            if elem=='job' :
                self.populate_server()
        
        
        #  List Views :
        #===-------------
        
        elif elem in self.nim.listViews :
            #  Initialize :
            self.nim.Input( elem ).clear()
            
            #  Basenames :
            if elem=='base' :
                for option in self.nim.Dict( elem ) :
                    #  Populate :
                    item=QtGui.QListWidgetItem( self.nim.Input( elem ) )
                    item.setText( option['basename'] )
                    if self.nim.name('filter') !='Asset Master' :
                        item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                            | QtCore.Qt.ItemIsEnabled )
                    #  Select item, if it matches the preferences :
                    if option['basename']==self.nimPrefs.name( elem ) :
                        self.nim.Input( elem ).setCurrentItem( item )
                        #  Set variables :
                        self.nim.set_name( elem=elem, name=option['basename'] )
            
            #  Versions :
            elif elem=='ver' :
                for option in self.nim.Dict( elem ) :
                    #  Populate "Load" Publish File :
                    if self.nim.pub() and self.nim.mode().lower() in ['load'] :
                        nimDir=Api.to_nimDir( nim=self.nim )
                        basename=Api.to_basename( nim=self.nim )
                        files=[]
                        if os.path.isdir( nimDir ) and os.listdir( nimDir ) :
                            if self.app=='Maya' :
                                temp_files=os.listdir( nimDir )
                                for _file in temp_files :
                                    if re.search( '^'+basename+'.(ma|mb)$', _file ) :
                                        if _file not in files :
                                            files.append( _file )
                            elif self.app=='Nuke' :
                                temp_files=os.listdir( nimDir )
                                for _file in temp_files :
                                    if re.search( '^'+basename+'.nk$', _file ) :
                                        if _file not in files :
                                            files.append( _file )
                            elif self.app=='C4D' :
                                temp_files=os.listdir( nimDir )
                                for _file in temp_files :
                                    if re.search( '^'+basename+'.c4d$', _file ) :
                                        if _file not in files :
                                            files.append( _file )
                            if self.app=='3dsMax' :
                                temp_files=os.listdir( nimDir )
                                for _file in temp_files :
                                    if re.search( '^'+basename+'.max$', _file ) :
                                        if _file not in files :
                                            files.append( _file )
                        if files :
                            for _file in files :
                                item=QtGui.QListWidgetItem( self.nim.Input( elem ) )
                                item.setText( _file )
                            break
                    
                    #  Add normal versions :
                    else :
                        if self.nim.name('filter')=='Asset Master' :
                            assetInfo=Api.get_assetInfo( assetID=self.nim.ID('asset') )
                            amrPath=os.path.normpath( assetInfo[0]['AMR_path'] )
                            fileName=assetInfo[0]['AMR_filename']
                            #fileDir=os.path.normpath( os.path.join( self.nim.server(get='path'), amrPath ) )
                            serverOsPathInfo = Api.get_serverOSPath( self.nim.server(get='ID'), platform.system() )
                            #P.info("SERVER OS PATH: %s" % serverOsPathInfo)
                            serverOSPath = serverOsPathInfo[0]['serverOSPath']
                            fileDir=os.path.normpath( os.path.join( serverOSPath, amrPath ) )
                            filePath=os.path.normpath( os.path.join( fileDir, fileName ) )
                            if os.path.isfile( filePath ) :
                                #  Disable Elements :
                                self.nim.Input('task').setEnabled( False )
                                self.nim.Input('base').setEnabled( False )
                                #  Clear basename selection :
                                for i in range( self.nim.Input('base').count() ) :
                                    item=self.nim.Input('base').item(i)
                                    item.setSelected( False )
                                #  Clear Versions :
                                self.del_connections()
                                self.nim.Input('ver').clear()
                                self.mk_connections()
                                #  Add item to list view :
                                item=QtGui.QListWidgetItem( self.nim.Input('ver') )
                                item.setText( fileName )
                                item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                                    | QtCore.Qt.ItemIsEnabled )
                                ext=F.get_ext( fileName )
                                #  Filter file types :
                                if self.app=='Maya' :
                                    if ext not in ['.ma', '.mb'] : item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='Nuke' :
                                    if ext !='.nk' : item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='C4D' :
                                    if ext !='.c4d' : item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='3dsMax' :
                                    if ext !='.max' : item.setFlags( QtCore.Qt.ItemIsEditable )
                                #  Select the item :
                                self.nim.Input('ver').setCurrentItem( item )
                                self.verPath.setText( fileDir )
                                self.verUser.setText( '<user>' )
                                self.verDate.setText( '<date>' )
                                self.verNote.setText( '<note>' )
                                return
                            else :
                                #  Disable Basename :
                                self.nim.Input('base').clear()
                                self.nim.Input('base').setEnabled( False )
                                #  Clear Versions :
                                self.del_connections()
                                self.nim.Input('ver').clear()
                                self.mk_connections()
                                #  Reset fields :
                                self.verPath.setText( '<path>' )
                                self.verUser.setText( '<user>' )
                                self.verDate.setText( '<date>' )
                                self.verNote.setText( '<note>' )
                                P.warning( 'Sorry, no Asset Master found at the following path:' )
                                P.warning( '    %s' % filePath )
                                return
                        
                        #  Add Published version :
                        elif self.nim.name('filter')=='Published' :
                            if self.nim.mode().lower()=='load' :
                                #self.del_connections()
                                fileDir=os.path.normpath( option['filepath'] )
                                if os.path.basename( os.path.normpath( fileDir ) )=='scenes' :
                                    fileDir=os.path.dirname( fileDir )
                                nimDir=os.path.dirname( fileDir )
                                fileName=option['basename']+option['ext']
                                filePath=os.path.normpath( os.path.join( nimDir, fileName ) )
                                if os.path.isfile( filePath ) :
                                    #  Add item to list view :
                                    item=QtGui.QListWidgetItem( self.nim.Input( elem ) )
                                    item.setText( fileName )
                                    item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                                        | QtCore.Qt.ItemIsEnabled )
                                    #  Filter file types :
                                    if self.app=='Maya' :
                                        if option['ext'] not in ['.ma', '.mb'] :
                                            item.setFlags( QtCore.Qt.ItemIsEditable )
                                    elif self.app=='Nuke' :
                                        if option['ext'] !='.nk' :
                                            item.setFlags( QtCore.Qt.ItemIsEditable )
                                    elif self.app=='C4D' :
                                        if option['ext'] !='.c4d' :
                                            item.setFlags( QtCore.Qt.ItemIsEditable )
                                    elif self.app=='3dsMax' :
                                        if option['ext'] !='.max' :
                                            item.setFlags( QtCore.Qt.ItemIsEditable )
                                    #  Select the item :
                                    #self.nim.Input( elem ).setCurrentItem( item )
                                    self.verPath.setText( nimDir )
                                    self.verUser.setText( option['username'] )
                                    self.verDate.setText( option['date'] )
                                    self.verNote.setText( '<note>' )
                                #self.mk_connections()
                            elif self.nim.mode().lower() in ['open', 'file'] :
                                item=QtGui.QListWidgetItem( self.nim.Input( elem ) )
                                item.setText( option['filename']+' - '+option['note'] )
                                if self.nim.mode().lower() in ['save', 'saveas'] :
                                    item.setFlags( QtCore.Qt.ItemIsEditable )
                                else :
                                    item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                                        | QtCore.Qt.ItemIsEnabled )
                                #  Filter file types :
                                if self.app=='Maya' :
                                    ext=F.get_ext( filePath=option['filename'] )
                                    if ext not in ['.ma', '.mb'] :
                                        item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='Nuke' :
                                    ext=F.get_ext( filePath=option['filename'] )
                                    if ext !='.nk' :
                                        item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='C4D' :
                                    ext=F.get_ext( filePath=option['filename'] )
                                    if ext !='.c4d' :
                                        item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='3dsMax' :
                                    ext=F.get_ext( filePath=option['filename'] )
                                    if ext !='.max' :
                                        item.setFlags( QtCore.Qt.ItemIsEditable )
                                #  Set from preferences :
                                if option['filename']+' - '+option['note']==self.pref_version and \
                                    self.nim.mode() is not 'publish' :
                                    self.nim.Input( elem ).setCurrentItem( item )
                                    #  Set variables :
                                    self.nim.set_name( elem=elem, name=option['filename']+' - '+option['note'] )
                                    self.nim.set_ID( elem=elem, ID=option['fileID'] )
                                    #  Set notes section :
                                    self.verPath.setText( option['filepath'] )
                                    self.verUser.setText( option['username'] )
                                    self.verDate.setText( option['date'] )
                                    self.verNote.setText( option['note'] )
                        #  Add Work versions :
                        elif self.nim.name('filter')=='Work' :
                            item=QtGui.QListWidgetItem( self.nim.Input( elem ) )
                            item.setText( option['filename']+' - '+option['note'] )
                            if self.nim.mode().lower() in ['save', 'saveas'] :
                                item.setFlags( QtCore.Qt.ItemIsEditable )
                            else :
                                item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                                    | QtCore.Qt.ItemIsEnabled )
                            #  Filter file types :
                            if self.app=='Maya' :
                                ext=F.get_ext( filePath=option['filename'] )
                                if ext not in ['.ma', '.mb'] :
                                    item.setFlags( QtCore.Qt.ItemIsEditable )
                            elif self.app=='Nuke' :
                                ext=F.get_ext( filePath=option['filename'] )
                                if ext !='.nk' :
                                    item.setFlags( QtCore.Qt.ItemIsEditable )
                            elif self.app=='C4D' :
                                ext=F.get_ext( filePath=option['filename'] )
                                if ext !='.c4d' :
                                    item.setFlags( QtCore.Qt.ItemIsEditable )
                            elif self.app=='3dsMax' :
                                ext=F.get_ext( filePath=option['filename'] )
                                if ext !='.max' :
                                    item.setFlags( QtCore.Qt.ItemIsEditable )
                            #  Set from preferences :
                            if option['filename']+' - '+option['note']==self.pref_version and \
                                self.nim.mode() is not 'publish' :
                                self.nim.Input( elem ).setCurrentItem( item )
                                #  Set variables :
                                self.nim.set_name( elem=elem, name=option['filename']+' - '+option['note'] )
                                self.nim.set_ID( elem=elem, ID=option['fileID'] )
                                #  Set notes section :
                                self.verPath.setText( option['filepath'] )
                                self.verUser.setText( option['username'] )
                                self.verDate.setText( option['date'] )
                                self.verNote.setText( option['note'] )
        
        
        P.debug( '%.3f => %s finished' % ((time.time()-startTime), elem.upper() ) )
        
        return

    
    def populate_server(self) :
        'Populates the server field, when the Job is set'
        index=0
        #  Get Server Dictionary :
        serverDict=Api.get_servers( self.nim.ID('job') )
        self.nim.set_server( Dict=serverDict )
        
        #  Populate the combo box :
        if serverDict and len(serverDict) :
            P.debug( '   Job Servers = %s' % serverDict )
            #  Populate drop box :
            self.nim.Input('server').setEnabled( True )
            self.nim.Input('server').clear()

            P.debug( '    _os = %s' % _os)
            for js in self.nim.Dict('server') :
                if _os in ['windows', 'win32'] :
                    self.nim.Input('server').addItem( js['winPath']+' - ("'+js['server']+'")' )
                    #if js['winPath'] !=self.pref_defaultServerPath :
                    if js['winPath'] !=self.pref_serverPath :
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                            #path=str(js['path']) )
                            path=str(js['winPath']) )
                        index+=1
                    else :
                        self.nim.Input('server').setCurrentIndex( index )
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                            path=str(js['winPath']) )

                elif _os in ['darwin', 'mac'] :
                    self.nim.Input('server').addItem( js['osxPath']+' - ("'+js['server']+'")' )
                    #if js['osxPath'] !=self.pref_defaultServerPath :
                    if js['osxPath'] !=self.pref_serverPath :
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                            #path=str(js['path']) )
                            path=str(js['osxPath']) )
                        index +=1
                    else :
                        self.nim.Input('server').setCurrentIndex( index )
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                            path=str(js['osxPath']) )

                elif _os in ['linux', 'linux2'] :
                    self.nim.Input('server').addItem( js['path']+' - ("'+js['server']+'")' )
                    #if js['path'] !=self.pref_defaultServerPath :
                    if js['path'] !=self.pref_serverPath :
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                            path=str(js['path']) )
                        index +=1
                    else :
                        self.nim.Input('server').setCurrentIndex( index )
                        self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                            path=str(js['path']) )
        else :
            self.nim.Input('server').clear()
            self.nim.Input('server').addItem('None')
            self.nim.Input('server').setEnabled( False )
            self.nim.set_server( name='', path='', Dict={}, ID='' )
            if self.nim.ID('job') :
                P.warning( 'No servers found for job, "%s"' % self.nim.name('job') )
        return
    
    
    def update_elem( self, elem='job' ) :
        'Updates a given GUI element, along with its dependent fields'
        
        
        #  Combo Boxes :
        #===-------------------
        
        if elem in self.nim.comboBoxes :
            #  Update Name and ID in NIM dictionary :
            if self.nim.Input( elem ).currentText() not in ['Select...', 'None', ''] :
                
                #  Update Name dictionary key :
                self.nim.set_name( elem=elem, name=self.nim.Input( elem ).currentText() )
                
                #  Update ID :
                for option in self.nim.Dict( elem ) :
                    if elem in ['asset', 'shot'] :
                        if option['name']==self.nim.Input( elem ).currentText() :
                            self.nim.set_ID( elem=elem, ID=option['ID'] )
                            break
                    elif elem in ['show'] :
                        if option['showname']==self.nim.Input( elem ).currentText() :
                            self.nim.set_ID( elem=elem, ID=option['ID'] )
                            break
                    elif elem !='filter' :
                        if elem=='task' :
                            if option['name']==self.nim.Input( elem ).currentText() :
                                self.nim.set_name( elem=elem, name=option['name'] )
                                self.nim.set_ID( elem=elem, ID=option['ID'] )
                                self.nim.set_taskFolder( folder=option['folder'] )
                                break
                        if option==self.nim.Input( elem ).currentText() :
                            self.nim.set_ID( elem=elem, ID=self.nim.Dict( elem )[str(self.nim.name( elem ))] )
                            break
                #  Print :
                if not self.nim.ID( elem ) :
                    P.info( '%s = "%s"' % (elem.upper(), self.nim.name( elem )) )
                else :
                    P.info( '%s = "%s" (ID #%s)' % (elem.upper(), self.nim.name( elem ), self.nim.ID( elem )) )
            #  Clear variables, if field not set :
            else :
                self.nim.set_name( elem=elem, name='' )
                self.nim.set_ID( elem=elem, ID=None )
            
            #  Populate Server :
            if elem=='job' :
                self.populate_server()
            
            #  Update for Asset Master Filter :
            if elem=='filter' :
                #  Set Asset Master :
                if self.nim.name( elem )=='Asset Master' :
                    assetInfo=Api.get_assetInfo( assetID=self.nim.ID('asset') )
                    amrPath=os.path.normpath( assetInfo[0]['AMR_path'] )
                    fileName=assetInfo[0]['AMR_filename']
                    #fileDir=os.path.normpath( os.path.join( self.nim.server(get='path'), amrPath ) )
                    serverOsPathInfo = Api.get_serverOSPath( self.nim.server(get='ID'), platform.system() )
                    #P.info(serverOsPathInfo)
                    serverOSPath = serverOsPathInfo[0]['serverOSPath']
                    fileDir=os.path.normpath( os.path.join( serverOSPath, amrPath ) )
                    filePath=os.path.normpath( os.path.join( fileDir, fileName ) )
                    if os.path.isfile( filePath ) :
                        #  Disable Elements :
                        self.nim.Input('task').setEnabled( False )
                        self.nim.Input('base').setEnabled( False )
                        #  Clear basename selection :
                        for i in range( self.nim.Input('base').count() ) :
                            item=self.nim.Input('base').item(i)
                            item.setSelected( False )
                        #  Clear Versions :
                        self.del_connections()
                        self.nim.Input('ver').clear()
                        self.mk_connections()
                        #  Add item to list view :
                        item=QtGui.QListWidgetItem( self.nim.Input('ver') )
                        item.setText( fileName )
                        item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                            | QtCore.Qt.ItemIsEnabled )
                        ext=F.get_ext( fileName )
                        #  Filter file types :
                        if self.app=='Maya' :
                            if ext not in ['.ma', '.mb'] : item.setFlags( QtCore.Qt.ItemIsEditable )
                        elif self.app=='Nuke' :
                            if ext !='.nk' : item.setFlags( QtCore.Qt.ItemIsEditable )
                        elif self.app=='C4D' :
                            if ext !='.c4d' : item.setFlags( QtCore.Qt.ItemIsEditable )
                        elif self.app=='3dsMax' :
                            if ext !='.max' : item.setFlags( QtCore.Qt.ItemIsEditable )
                        #  Select the item :
                        self.nim.Input('ver').setCurrentItem( item )
                        self.verPath.setText( fileDir )
                        self.verUser.setText('<user>')
                        self.verDate.setText('<date>')
                        self.verNote.setText('<note>')
                        return
                    else :
                        #  Disable Task :
                        self.nim.Input('task').clear()
                        self.nim.Input('task').addItem('None')
                        self.nim.Input('task').setEnabled( False )
                        #  Disable Basename :
                        self.nim.Input('base').clear()
                        self.nim.Input('base').setEnabled( False )
                        #  Clear Versions :
                        self.del_connections()
                        self.nim.Input('ver').clear()
                        self.mk_connections()
                        #  Reset fields :
                        self.verPath.setText('<path>')
                        self.verUser.setText('<user>')
                        self.verDate.setText('<date>')
                        self.verNote.setText('<note>')
                        P.warning('Sorry, no Asset Master found at the following path:')
                        P.warning( '    %s' % filePath )
                        return
                else :
                    self.nim.Input('task').setEnabled( True )
                    self.nim.Input('base').setEnabled( True )
            
            if elem=='task' :
                self.nimPrefs.set_name( elem='task', name=self.nim.name('task') )
        
        
        #  List Views :
        #===-------------
        
        elif elem in self.nim.listViews :
            
            #  Basenames :
            if elem=='base' :
                for option in self.nim.Dict( elem ) :
                    if self.nim.Input( elem ).currentItem() :
                        if option['basename']==self.nim.Input( elem ).currentItem().text() :
                            #  Set variables :
                            self.nim.set_name( elem=elem, name=self.nim.Input( elem ).currentItem().text() )
                if self.nim.name('filter') !='Asset Master' :
                    self.nim.Input( elem ).setEnabled( True )
                else :
                    #  Enable Basename, if Filter not set to Asset Master :
                    for index in range( self.nim.Input('base').count() ) :
                        self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                            | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
            
            #  Versions :
            elif elem=='ver' :
                for option in self.nim.Dict( elem ) :
                    #  File Filters :
                    if self.nim.name('filter')=='Asset Master' :
                        break
                    #  Add Published version :
                    elif self.nim.name('filter')=='Published' :
                        if self.nim.mode().lower()=='load' :
                            fileDir=os.path.normpath( option['filepath'] )
                            if os.path.basename( os.path.normpath( fileDir ) )=='scenes' :
                                fileDir=os.path.dirname( fileDir )
                            nimDir=os.path.dirname( fileDir )
                            fileName=option['basename']+option['ext']
                            filePath=os.path.normpath( os.path.join( nimDir, fileName ) )
                            if os.path.isfile( filePath ) and not self.nim.Input('ver').findItems( fileName, QtCore.Qt.MatchExactly ) :
                                #  Add item to list view :
                                item=QtGui.QListWidgetItem( self.nim.Input( elem ) )
                                item.setText( fileName )
                                item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                                    | QtCore.Qt.ItemIsEnabled )
                                #  Filter file types :
                                if self.app=='Maya' :
                                    if option['ext'] not in ['.ma', '.mb'] : item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='Nuke' :
                                    if option['ext'] !='.nk' : item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='C4D' :
                                    if option['ext'] !='.c4d' : item.setFlags( QtCore.Qt.ItemIsEditable )
                                elif self.app=='3dsMax' :
                                    if option['ext'] !='.max' : item.setFlags( QtCore.Qt.ItemIsEditable )
                                #  Select the item :
                                self.nim.Input( elem ).setCurrentItem( item )
                                self.verPath.setText( nimDir )
                                self.verUser.setText( option['username'] )
                                self.verDate.setText( option['date'] )
                                self.verNote.setText( '<note>' )
                        elif self.nim.mode().lower() in ['open', 'file'] :
                            if self.nim.Input( elem ).currentItem() :
                                if option['filename']+' - '+option['note']==self.nim.Input( elem ).currentItem().text() :
                                    #  Set variables :
                                    self.nim.set_name( elem=elem, name=option['filename']+' - '+option['note'] )
                                    self.nim.set_ID( elem=elem, ID=option['fileID'] )
                                    #  Set notes section :
                                    self.verPath.setText( option['filepath'] )
                                    self.verUser.setText( option['username'] )
                                    self.verDate.setText( option['date'] )
                                    self.verNote.setText( option['note'] )
                    #  Work Filter :
                    elif self.nim.name('filter')=='Work' :
                        if self.nim.pub() and self.nim.mode() in ['LOAD', 'Load', 'load'] :
                            if self.nim.Input( elem ).currentItem() :
                                nimDir=Api.to_nimDir( nim=self.nim )
                                fileName=self.nim.Input( elem ).currentItem().text()
                                filePath=os.path.join( nimDir, fileName )
                                stat_info=os.stat( filePath )
                                usrID=stat_info.st_uid
                                self.verPath.setText( filePath )
                                self.verUser.setText( '<user>' )
                                self.verDate.setText( time.ctime( os.path.getmtime( filePath ) ) )
                                self.verNote.setText( '<comment>' )
                            else :
                                self.verPath.setText( '<path>' )
                                self.verUser.setText( '<user>' )
                                self.verDate.setText( '<date>' )
                                self.verNote.setText( '<comment>' )
                        else :
                            for option in self.nim.Dict( elem ) :
                                if self.nim.Input( elem ).currentItem() :
                                    if option['filename']+' - '+option['note']==self.nim.Input( elem ).currentItem().text() :
                                        #  Set variables :
                                        self.nim.set_name( elem=elem, name=option['filename']+' - '+option['note'] )
                                        self.nim.set_ID( elem=elem, ID=option['fileID'] )
                                        #  Set notes section :
                                        self.verPath.setText( option['filepath'] )
                                        self.verUser.setText( option['username'] )
                                        self.verDate.setText( option['date'] )
                                        self.verNote.setText( option['note'] )
        
        
        #  Print :
        #===-----
        
        if elem in ['shot', 'asset'] :
            work, pub={}, {}
            #  Iterate over all possible Tasks :
            for task in Api.get_tasks() :
                task_work, task_pub=[], []
                valid_bases, valid_basesPub, valid_basesAllPub=[], [], []
                task_bases, task_basesAllPub, item_name=None, None, None
                #  Get Shot Basenames :
                if self.nim.tab()=='SHOT' :
                    task_bases=Api.get_bases( shotID=self.nim.ID('shot'), \
                        task=task['name'].upper() )
                    task_basesAllPub=Api.get_basesAllPub( shotID=self.nim.ID('shot'), \
                        task=task['name'].upper() )
                #  Get Asset Basenames :
                elif self.nim.tab()=='ASSET' :
                    task_bases=Api.get_bases( assetID=self.nim.ID( 'asset' ), \
                        task=task['name'].upper() )
                    task_basesAllPub=Api.get_basesAllPub( assetID=self.nim.ID( 'asset' ), \
                        task=task['name'].upper() )
                #  Get Work Basenames :
                if task_bases :
                    for base in task_bases :
                        task_work.append( base['basename'] )
                    work[task['name']]=task_work
                #  Get Published Basenames :
                if task_basesAllPub :
                    for base in task_basesAllPub :
                        task_pub.append( base['basename'] )
                    pub[task['name']]=task_work
            if work :
                P.info( '    Valid WORK tasks/basenames...' )
                for key in work.keys() : P.info( '      %s - %s' % (key, ', '.join( work[key]) ) )
            else : P.info( '    NO valid WORK tasks/basenames.' )
            if pub :
                P.info( '    Valid PUBLISHED tasks/basenames...' )
                for key in pub.keys() : P.info( '      %s - %s' % (key, ', '.join( pub[key]) ) )
            else : P.info( '    NO valid PUBLISHED tasks/basenames.' )
        
        
        #  Finish :
        #===-------
        
        #  Populate dependent elements :
        index=self.nim.elements.index( elem )+1
        if elem=='asset' :
            index=4
        while index<len(self.nim.elements) :
            self.populate_elem( elem=self.nim.elements[index] )
            if self.nim.elements[index]=='ver' :
                index+=1
            index +=1
        
        return
    
    
    def update_styleSheet(self) :
        'Sets the style sheet for the window'
        for index in range(len(self.menuItems)) :
            if self.menuItems[index].isChecked() :
                if self.cssFiles[index] in ['None', ''] :
                    self.setStyleSheet('')
                    #  Update preferences :
                    Prefs.update( attr='useStyleSheet', app=self.app, value='None' )
                #  Set stylesheet :
                if self.cssFiles[index] and os.path.isfile( self.cssFiles[index] ) :
                    self.setStyleSheet('')
                    with open( self.cssFiles[index], 'r' ) as fh :
                        self.setStyleSheet( fh.read() )
                    #  Update preferences :
                    Prefs.update( attr='useStyleSheet', app=self.app, value=self.cssFiles[index] )
                else :
                    self.setStyleSheet('')

    
    def update_server(self) :
        'Updates the server path when the combo box is changed'
        '''TEST'''
        print 'THIS IS THE SERVER: %s' % self.nim.Input('server').currentText()
        self.nim.set_server( name=self.nim.Input('server').currentText() )
        for js in self.nim.Dict('server') :

            if _os in ['windows', 'win32'] :    #js['winPath']+' - ("'+js['server']+'")'
                ''' #REMOVED TO FIX FOR ADDITIONAL INFO IN SERVER DROPDOWN
                if self.nim.Input('server').currentText()==self.nim.server( get='name' ) :
                    self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                        path=str(js['winPath']) )
                '''
                serverTitle = js['winPath']+' - ("'+js['server']+'")'
                if self.nim.Input('server').currentText()==serverTitle :
                    self.nim.set_server( name=js['server'], ID=str(js['ID']), path=str(js['winPath']) )
                    self.pref_serverPath = str(js['winPath'])

            elif _os in ['darwin', 'mac'] :
                ''' #REMOVED TO FIX FOR ADDITIONAL INFO IN SERVER DROPDOWN
                if self.nim.Input('server').currentText()==self.nim.server( get='name' ) :
                    self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                        path=str(js['osxPath']) )
                '''
                serverTitle = js['osxPath']+' - ("'+js['server']+'")'
                if self.nim.Input('server').currentText()==serverTitle :
                    self.nim.set_server( name=js['server'], ID=str(js['ID']), path=str(js['osxPath']) )
                    self.pref_serverPath = str(js['osxPath'])

            elif _os in ['linux', 'linux2'] :
                ''' #REMOVED TO FIX FOR ADDITIONAL INFO IN SERVER DROPDOWN
                if self.nim.Input('server').currentText()==self.nim.server( get='name' ) :
                    self.nim.set_server( name=self.nim.Input('server').currentText(), ID=str(js['ID']), \
                        path=str(js['path']) )
                '''
                serverTitle = js['path']+' - ("'+js['server']+'")'
                if self.nim.Input('server').currentText()==serverTitle :
                    self.nim.set_server( name=js['server'], ID=str(js['ID']), path=str(js['path']) )
                    self.pref_serverPath = str(js['path'])


        print 'Server ID set to %s' % self.nim.server( get='ID')
        
        P.debug( 'Server set to - %s' % self.nim.name('server') )
        
        return

    
    def update_tab(self) :
        'Updates elements when the Show/Asset tab is changed'
        #  Update NIM dictionary :
        if self.jobTab.currentIndex()==0 :
            self.nim.set_tab('ASSET')
        elif self.jobTab.currentIndex()==1 :
            self.nim.set_tab('SHOT')
        P.info( 'Tab has been set to "%s"' % self.nim.tab() )
        #  Update elements :
        self.update_elem( elem=self.nim.tab().lower() )
    
    
    def update_img(self) :
        'Displays shot and asset thumbnail images, or a default image'
        self.img_size=self.width()/2.25
        img, img_loc, _type='', '', ''
        _set=False
        
        #  Get Asset/Shot Thumbnail NIM URL relative path :
        if self.nim.tab()=='ASSET' and self.nim.ID( 'asset' ) :
            _type='asset'
            img=Api.get( {'q':'getAssetIcon', 'ID': self.nim.ID( 'asset' )} )
        elif self.nim.tab()=='SHOT' and self.nim.ID( 'shot' ) :
            _type='shot'
            img=Api.get( {'q':'getShotIcon', 'ID': self.nim.ID( 'shot' )} )
        
        #  Set default image, if Shot/Asset ID's have not been set yet :
        if _type and not self.nim.ID( 'asset' ) and not self.nim.ID( 'shot' ) :
            self.nim.set_pic( elem=_type, widget=QtGui.QPixmap().fromImage( \
                QtGui.QImage( self.pref_imgDefault ) ) )
            self.nim.pix( _type ).fromImage( QtGui.QImage( self.pref_imgDefault ) )
            self.nim.set_pic( elem=_type, widget=self.nim.pix( _type ).scaled( \
                self.img_size, self.img_size, QtCore.Qt.KeepAspectRatio ) )
            self.nim.label( _type ).setPixmap( self.nim.pix( _type ) )
            return None
        
        # Get domain name from URL
        from urlparse import urlparse
        parsed_uri = urlparse( self.prefs['NIM_URL'] )
        nim_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        print( 'NIM Domain: %s' % nim_domain)

        try :
            img_loc=nim_domain+img[0]['img_link']
            img_dir=os.path.dirname( img_loc )+'/'
            print('img_loc: %s' % img_loc)
            print('img_dir: %s' % img_dir)
        except :
            #Failed to build img path
            print('Failed to build icon path')
            img_loc=''
            print('Using default img: %s' % img_loc)

        #  Ensure the Thumbnail exists :
        '''
        #REMOVED: Directory verification to failed due to security on folder browsing
        if _type and img and len(img) :
            if img[0]['img_link'] :
                httpSrch=re.search( '^http[s]?://', nim_domain )
                if httpSrch :
                    img_loc=nim_domain+img[0]['img_link']
                    img_dir=os.path.dirname( img_loc )+'/'
                    print('img_loc: %s' % img_loc)
                    print('img_dir: %s' % img_dir)
                    
                    if img_loc and img_dir :
                        #  Ensure that the image directory exists :
                        try :
                            urllib2.urlopen( img_dir )
                            #  Ensure that the image exists :
                            try :
                                urllib2.urlopen( img_loc )
                            except :
                                P.debug( '%s image URL doesn\'t exist : "%s".' % \
                                    (_type.upper(), img_loc) )
                                img_loc=''
                        except :
                            P.debug( '%s image URL directory doesn\'t exist : "%s".' % \
                                (_type.upper(), img_loc) )
                            img_loc=''
        '''
        
        print ('type: %s' % _type)
        print ('set: %s' % _set)

        #  Set Shot/Asset image :
        if _type and img_loc :
            print("set image")
            _data=urllib.urlopen( img_loc ).read()
            self.nim.pix( _type ).loadFromData( _data )
            self.nim.set_pic( elem=_type, widget=self.nim.pix( _type ).scaled( \
                self.img_size, self.img_size, QtCore.Qt.KeepAspectRatio ) )
            self.nim.label( _type ).setPixmap( self.nim.pix( _type ) )
            _set=True
            P.debug( '%s image URL = "%s"' % (_type.upper(), img_loc) )
        
        #  Set default image :
        if _type and not _set :
            print("default image")
            self.nim.set_pic( elem=_type, widget=QtGui.QPixmap().fromImage( \
                QtGui.QImage( self.pref_imgDefault ) ) )
            self.nim.pix( _type ).fromImage( QtGui.QImage( self.pref_imgDefault ) )
            self.nim.set_pic( elem=_type, widget=self.nim.pix( _type ).scaled( \
                self.img_size, self.img_size, QtCore.Qt.KeepAspectRatio ) )
            self.nim.label( _type ).setPixmap( self.nim.pix( _type ) )
            P.debug( '%s image URL set to default : "%s"' % (_type.upper(), self.pref_imgDefault) )
        
        if not _type and not _set :
            print("default image")
            _type = 'shot'
            self.nim.set_pic( elem=_type, widget=QtGui.QPixmap().fromImage( \
                QtGui.QImage( self.pref_imgDefault ) ) )
            self.nim.pix( _type ).fromImage( QtGui.QImage( self.pref_imgDefault ) )
            self.nim.set_pic( elem=_type, widget=self.nim.pix( _type ).scaled( \
                self.img_size, self.img_size, QtCore.Qt.KeepAspectRatio ) )
            self.nim.label( _type ).setPixmap( self.nim.pix( _type ) )
            P.debug( '%s image URL set to default : "%s"' % (_type.upper(), self.pref_imgDefault) )

        return
    
    
    def update_tag(self) :
        'Updates the tag string in the main NIM dictionary'
        #  Update NIM dictionary entry :
        self.nim.set_name( elem='tag', name=self.nim.Input('tag').text().replace( ' ', '_' ) )
        #  Disable Basename window if necessary :
        if self.nim.name('tag') :
            self.nim.Input('base').setEnabled( False )
            for index in range( self.nim.Input('base').count() ) :
                self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsEditable )
            self.nim.Input('base').setSelectionMode( QtGui.QAbstractItemView.NoSelection )
        #  Otherwise, enable Basename window :
        else :
            self.nim.Input('base').setEnabled( True )
            for index in range( self.nim.Input('base').count() ) :
                self.nim.Input('base').item( index ).setFlags( QtCore.Qt.ItemIsSelectable \
                    | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled )
            self.nim.Input('base').setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        return
    
    
    def update_comment(self) :
        'Updates the comment string in the main NIM dictionary'
        self.nim.set_name( elem='comment', name=self.nim.Input('comment').text() )
    
    
    def update_fileExt(self) :
        'Updates the file extension information in the main NIM dictionary'
        self.nim.set_name( elem='fileExt', name=self.nim.Input('fileExt').currentText() )
        if self.nim.name('fileExt')=='.mb' :
            self.nim.set_fileType( fileType='Maya Binary' )
        elif self.nim.name('fileExt')=='.ma' :
            self.nim.set_fileType( fileType='Maya Ascii' )

    
    def update_user(self) :
        'Updates the currently set user name and ID within NIM'
        #  Get User Information :
        info=Win.userInfo()
        userName=info[0]
        userID=info[1]
        #  Set User :
        self.nim.set_userInfo( userName=userName, userID=userID )
        self.nimPrefs.set_userInfo( userName=userName, userID=userID )
        #  Update window :
        self.update_elem('job')
        return

    
    #  Connections :
    def mk_connections(self) :
        'Connects dynamic elements of the GUI'
        self.nim.Input('job').activated.connect( lambda: self.update_elem('job') )
        self.jobTab.currentChanged.connect( self.update_tab )
        self.nim.Input('asset').activated.connect( lambda: self.update_elem('asset') )
        self.nim.Input('asset').activated.connect( self.update_img )
        self.nim.Input('show').activated.connect( lambda: self.update_elem('show') )
        self.nim.Input('show').activated.connect( self.update_img )
        self.nim.Input('shot').activated.connect( lambda: self.update_elem('shot') )
        self.nim.Input('shot').activated.connect( self.update_img )
        self.nim.Input('filter').activated.connect( lambda: self.update_elem('filter') )
        self.nim.Input('task').activated.connect( lambda: self.update_elem('task') )
        self.nim.Input('base').itemClicked.connect( lambda: self.update_elem('base') )
        self.nim.Input('tag').textChanged.connect( self.update_tag )
        self.nim.Input('ver').currentItemChanged.connect( lambda: self.update_elem('ver') )
        self.nim.Input('comment').textChanged.connect( self.update_comment )
        self.nim.Input('fileExt').activated.connect( self.update_fileExt )
        self.nim.Input('server').activated.connect( self.update_server )
        return
    
    
    def del_connections(self) :
        'Connects dynamic elements of the GUI'
        try : self.nim.Input('job').activated.disconnect()
        except : pass
        try : self.jobTab.currentChanged.disconnect()
        except : pass
        try : self.nim.Input('asset').activated.disconnect()
        except : pass
        try : self.nim.Input('asset').activated.disconnect()
        except : pass
        try : self.nim.Input('show').activated.disconnect()
        except : pass
        try : self.nim.Input('shot').activated.disconnect()
        except : pass
        try : self.nim.Input('shot').activated.disconnect()
        except : pass
        try : self.nim.Input('filter').activated.disconnect()
        except : pass
        try : self.nim.Input('task').activated.disconnect()
        except : pass
        try : self.nim.Input('base').currentItemChanged.disconnect()
        except : pass
        try : self.nim.Input( 'tag' ).textChanged.disconnect()
        except : pass
        try : self.nim.Input('ver').currentItemChanged.disconnect()
        except : pass
        try : self.nim.Input('comment').textChanged.disconnect()
        except : pass
        try : self.nim.Input('fileExt').activated.disconnect()
        except : pass
        try : self.nim.Input('server').activated.disconnect()
        except : pass
        return

    
    def base_deselect(self) :
        'Deselects all Basenames.'
        for i in range( self.nim.Input('base').count() ) :
            item=self.nim.Input('base').item(i)
            item.setSelected( False )
        for i in range( self.nim.Input('ver').count() ) :
            item=self.nim.Input('ver').item(i)
            item.setSelected( False )
        self.nim.set_name( elem='base', name='' )
        self.nim.set_ID( elem='base', ID=None )
        self.nim.set_name( elem='ver', name='' )
        self.nim.set_ID(elem='ver', ID=None )
        self.nim.Input('ver').clear()
        return

    
    #  Write Preferences :
    def closeEvent( self, e ) :
        'Function is run every time the window is closed - writes out window preferences'
        P.debug(' ')
        #  Export window position :
        Prefs.update( attr='winPosX', app=self.app, value=str(self.x()) )
        Prefs.update( attr='winPosY', app=self.app, value=str(self.y()) )
        #  Export window size :
        Prefs.update( attr='winWidth', app=self.app, value=str(self.width()) )
        Prefs.update( attr='winHeight', app=self.app, value=str(self.height()) )

        # Export Server Prefs
        # TODO: modify to recognize different servers with the same path
        #       if the path is the same, no difference in operations ... just the name in the UI
        #
        # TODO: Only update server prefs on actual save.. .not just random close
        if self.saveServerPref == True:
            Prefs.update( attr='ServerPath', app=self.app, value=self.nim.server( get='path') )
            self.saveServerPref = False

        #  Don't write preferences for Publish or Version Up windows :
        if self.nim.mode().lower() not in ['pub', 'publish', 'ver', 'verup', 'version', 'versionup'] :
            #  Export tab setting :
            Prefs.update( attr='tab', app=self.app, value=self.nim.tab() )
            


            #  Export main comb box settings :
            for elem in self.nim.comboBoxes :
                Prefs.update( attr=elem, app=self.app, value=self.nim.Input( elem ).currentText() )
            #  Export list view settings :
            for elem in self.nim.listViews :
                if self.nim.Input( elem ).currentItem() :
                    if elem=='base' :
                        Prefs.update( attr='basename', app=self.app, \
                            value=self.nim.Input( elem ).currentItem().text() )
                    elif elem=='ver' :
                        Prefs.update( attr='version', app=self.app, \
                            value=self.nim.Input( elem ).currentItem().text() )
            P.debug(' ')
            self.nim.Print( debug=True )
            P.debug(' ')

        # Return focus to Main Window for 3dsMax
        '''
        if self.app=='3dsMax' :
            import MaxPlus
            MaxPlus.CUI.EnableAccelerators()
        '''
    
    
    #  File Operations :
    def set_fromFilePath(self) :
        'Populates the browser, based on the current filename'
        
        filePath=''
        #  Get file path :
        if self.app=='Maya' :
            import maya.cmds as mc
            filePath=mc.file( query=True, sn=True )
        elif self.app=='Nuke' :
            import nuke
            filePath=nuke.root().name()
        elif self.app=='Hiero' :
            import hiero.core
            projects=hiero.core.projects()
            filePath=projects[0].path()
        elif self.app=='3dsMax' :
            import MaxPlus
            filePath=MaxPlus.FileManager.GetFileNameAndPath()
        
        #  Error check file path :
        if not filePath :
            msg='Sorry, unable to retrieve API information from current file name.\n'+\
                '    Please save the file to add it to the API, before attempting a publish.'
            P.error( msg+'  :\'(' )
            Win.popup( title=self.winTitle+' - File name not set', msg=msg )
            return False
        else :
            P.debug( 'Attempting to retrieve API information from the following filepath...' )
            P.debug( '    %s' % filePath )
        
        
        #  Get API values from file name :
        nimFile=Nim.NIM().ingest_filePath()
        
        if nimFile :
            #  Set Combo Boxes :
            for elem in self.nim.get_comboBoxes() :
                if nimFile.name( elem ) :
                    index=self.nim.Input( elem ).findText( nimFile.name( elem ) )
                    if index > -1 :
                        self.nim.Input( elem ).setCurrentIndex( index )
                        self.update_elem( elem )
            #  Set Basenames :
            if nimFile.name( 'base' ) :
                baseIndex=self.nim.Input( 'base' ).findItems( nimFile.name( 'base' ), QtCore.Qt.MatchExactly )
                if baseIndex :
                    self.nim.Input( 'base' ).setCurrentItem( baseIndex[0] )
            #  Set Versions :
            if nimFile.name( 'ver' ) :
                verIndex=self.nim.Input( 'ver' ).findItems( '^'+nimFile.name( 'ver' ), QtCore.Qt.MatchRegExp )
                if verIndex :
                    self.nim.Input( 'ver' ).setCurrentItem( verIndex[0] )
            #  Set Tab :
            if nimFile.tab() :
                if nimFile.tab()=='ASSET' :
                    self.jobTab.setCurrentIndex( 0 )
                elif nimFile.tab()=='SHOT' :
                    self.jobTab.setCurrentIndex( 1 )
            return True
        else :
            return False
    
    
    def get_filePath(self) :
        'Gets the file path from the window'
        if self.nim.Input('ver') and self.nim.Input('ver').currentItem() and \
            self.nim.Input('ver').currentItem().text() :
            if re.search( ' - ', self.nim.Input('ver').currentItem().text() ) :
                index=self.nim.Input('ver').currentItem().text().find(' - ')
                filePath=os.path.normpath( os.path.join(self.verPath.text(),self.nim.Input('ver').currentItem().text()[0:index] ))
                P.debug("if: %s" % filePath)
            else :
                filePath=os.path.normpath( os.path.join( self.verPath.text(), \
                    self.nim.Input('ver').currentItem().text() ) )
                P.debug("else: %s" % filePath)
            return filePath
        else :
            return False
    
    
    def file_open(self) :
        'Function called when Open button is pressed'
        filePath=self.get_filePath()
        pathInfo, prefix='', ''
        
        P.debug('file_open - filePath: %s' % filePath)
         
        '''THIS CODE SHOULD BE DEPRICATED'''
        #  Derive Server Path from File Name :
        if not self.nim.server() :
            for sp in ['winPath', 'osxPath', 'path'] :
                prefix=os.path.normpath( self.nim.Dict('server')[0][sp] )
                if prefix==os.path.normpath( filePath[:len(prefix)] ) :
                    self.nim.set_server( path=prefix )
                    break
        '''END DEPRICATED'''

        '''TEST: FIXING BAD PATH CALLS ABOVE'''
        # Get Server OS Path from server ID
        P.info("FileID: %s" % self.nim.ID('ver'))
        
        open_file_versionInfo = Api.get_verInfo( self.nim.ID('ver') )

        if open_file_versionInfo:
            open_file_serverID = open_file_versionInfo[0]['serverID']
            P.info("ServerID: %s" % open_file_serverID)
            serverOsPathInfo = Api.get_serverOSPath( open_file_serverID, platform.system() )
            P.info("Server OS Path Info: %s" % serverOsPathInfo)
            serverOSPath = serverOsPathInfo[0]['serverOSPath']
            P.info("Server OS Path: %s" % serverOSPath)
            self.nim.set_server( path=serverOSPath )
            self.saveServerPref = True

        #  Convert file path :
        filePath=F.os_filePath( path=filePath, nim=self.nim )
        P.debug("filePath: %s" % filePath)

        #  Set File Version :
        ver=F.get_ver( filePath=filePath )
        self.nim.set_version( version=str(ver) )
        
        #  Comp Path :
        if self.nim.tab()=='SHOT' and self.nim.ID('shot') :
            pathInfo=Api.get( {'q': 'getPaths', 'type': 'shot', 'ID' : str(self.nim.ID('shot'))} )
        elif self.nim.tab()=='ASSET' and self.nim.ID('asset') :
            pathInfo=Api.get( {'q': 'getPaths', 'type': 'asset', 'ID' : str(self.nim.ID('asset'))} )
        if not pathInfo :
            P.warning( 'No Path Information found in the NIM API!' )
        
        #  Set Comp Path :
        if pathInfo and type(pathInfo)==type(dict()) and 'comps' in pathInfo :
            compPath=os.path.normpath( os.path.join( self.nim.server(), pathInfo['comps'] ) )
            self.nim.set_compPath( compPath=compPath )
        
        #  Error check :
        if not filePath :
            P.error('Sorry, no file specified, aborting.')
            Win.popup( title='NIM Error', msg='Sorry, no file specified, aborting.' )
            return False
        if not os.path.isfile( filePath ) :
            P.error( 'Sorry, it looks like the following file path doesn\'t exist on disk...\n    %s' \
                % os.path.normpath( filePath ) )
            P.error('    Shot not set.')
            Win.popup( title='NIM Error', msg='Sorry, it looks like the following '+
                'file path doesn\'t exist on disk...\n    %s\n    Shot not set.' % os.path.normpath( filePath ) )
            return False
        
        
        #  Maya :
        if self.app=='Maya' :
            #  Open :
            try :
                import maya.cmds as mc
                import maya.mel as mm
                import nim_maya as M
                mc.file( filePath, force=True, open=True, ignoreVersion=True, prompt=False )
            except Exception, e :
                P.error( 'Failed reading the file: %s' % filePath )
                P.error( '    %s' % traceback.print_exc() )
                return False
            
            #  Set Project :
            projPath=os.path.dirname( os.path.normpath( filePath ) ).replace( 'scenes', '' )
            if _os=='windows' :
                projPath=projPath.replace( '\\', '/' )
            if os.path.isdir( projPath ) :
                mm.eval( 'setProject "%s"' % projPath )
                P.info( '\nUI - Project set to...\n    %s\n' % projPath )
            else :
                P.warning('\nProject was not set!\n')
            
            #  Set Variables :
            try :
                import nim_maya as M
                M.set_vars( nim=self.nim )
            except Exception, e :
                P.error( 'Failed adding NIM attributes to Project Settings node...' )
                P.error( '    %s' % traceback.print_exc() )
                return False
            
        #  Nuke :
        elif self.app=='Nuke' :
            #  Open :
            try :
                import nuke
                import nim_nuke as N
                #  Attempt to get Variables from the current file :
                nimCheck=Nim.NIM()
                N.get_vars( nim=nimCheck )
                mod=nuke.root().modified()
                #  Prompt to manually save the file, if modified and no variables present :
                if mod and not nimCheck.ID('shot') and not nimCheck.ID('asset') :
                    msg='Please Save your current file first'
                    P.error( msg )
                    Win.popup( title='NIM - Import Error', msg=msg )
                    self.close()
                    return False
                #  Prompt to Save the current file :
                elif mod :
                    result=N.Win_SavePySide.get_btn()
                    if result.lower()=='save' :
                        P.info('\nSaving file...\n')
                        cur_filePath=F.get_filePath()
                        nuke.scriptSaveAs( cur_filePath )
                    elif result.lower()=='verup' :
                        P.info('\nVersioning file up...\n')
                        try :
                            Api.versionUp()
                        except :
                            P.error('Problem running version up command.  Nothing done.')
                            return False
                    elif result.lower()=='no' :
                        P.info( '\nFile not saved before opening.\n' )
                    elif result.lower()=='cancel' :
                        P.info('\nCancelling file operation.\n')
                        return None
                #  Clear the scene, load file and rename :
                nuke.scriptClear()
                #nuke.nodePaste( filePath ) #ERROR - causing Nuke to import scene with default project settings
                nuke.scriptOpen( filePath )
                PS=nuke.root()
                knob=PS.knob('name')
                knob.setValue( filePath.replace( '\\', '/' ) )
            except Exception, e :
                P.error( 'Failed reading the file: %s' % filePath )
                P.error( '    %s' % traceback.print_exc() )
                return False
            
            #  Set Variables :
            try :
                import nim_nuke as N
                N.set_vars( nim=self.nim )
            except Exception, e :
                P.error( 'Failed adding NIM attributes to Project Settings node...' )
                P.error( '    %s' % traceback.print_exc() )
                return False
        
        #  Hiero :
        elif self.app=='Hiero' :
            try :
                import hiero.core
                hiero.core.openProject( filePath )
            except Exception, e :
                P.error( 'Failed reading the file: %s' % filePath )
                P.error( '    %s' % traceback.print_exc() )
                return False
        
        #  3dsMax :
        if self.app=='3dsMax' :
            #  Open :
            try :
                import MaxPlus
                mpFM = MaxPlus.FileManager
                import nim_3dsmax as Max
                mpFM.Open(filePath)
            except Exception, e :
                P.error( 'Failed reading the file: %s' % filePath )
                P.error( '    %s' % traceback.print_exc() )
                return False
            
            #  Set Project :
            projPath=os.path.dirname( os.path.normpath( filePath ) ).replace( 'scenes', '' )
            if _os=='windows' :
                projPath=projPath.replace( '\\', '/' )
            if os.path.isdir( projPath ) :
                MaxPlus.SetProjectFolderDir( projPath )
                P.info( '\nUI - Project set to...\n    %s\n' % projPath )
            else :
                P.warning('\nProject was not set!\n')
            
            #  Set Variables :
            try :
                import nim_3dsmax as Max
                Max.set_vars( nim=self.nim )
            except Exception, e :
                P.error( 'Failed adding NIM attributes to Project Settings node...' )
                P.error( '    %s' % traceback.print_exc() )
                return False

        P.info( 'File, %s, opened!' % filePath )
        self.close()
        
        return

    
    def file_import(self) :
        'Imports elements into a Maya or Nuke scene file'
        
        #  Get file path :
        path=self.get_filePath()
        filePath=F.os_filePath( path=path, nim=self.nim )
        
        #  Maya Import :
        if self.app=='Maya' :
            import maya.cmds as mc
            
            #  Derive file name to use for namespace :
            index=self.nim.Input('ver').currentItem().text().find(' - ')
            fileName=self.nim.Input('ver').currentItem().text()[0:index]
            grpName=os.path.splitext( fileName )[0]
            
            #  Import the file :
            if os.path.isfile( filePath ) :
                P.info('File found, importing the following file...')
                P.info( '    %s' % filePath )
                if self.checkBox.checkState() :
                    #  Import file as a group :
                    mc.file( filePath, i=True, force=True, groupReference=True,
                        groupName=grpName+'_GRP' )
                else :
                    #  Import file :
                    mc.file( filePath, i=True, force=True )
            else :
                msg='Sorry, file to import doesn\'t exist...\n    %s' % filePath
                P.error( msg )
                Win.popup( title='NIM - Import Error', msg=msg )
                return
        
        #  Nuke Import :
        elif self.app=='Nuke' :
            import nuke
            nuke.nodePaste( filePath )
        
        #  3dsMax Merge :
        if self.app=='3dsMax' :
            import MaxPlus
            mpFM = MaxPlus.FileManager
            #  Derive file name to use for namespace :
            index=self.nim.Input('ver').currentItem().text().find(' - ')
            fileName=self.nim.Input('ver').currentItem().text()[0:index]
            grpName=os.path.splitext( fileName )[0]
            
            #  Import the file :
            if os.path.isfile( filePath ) :
                P.info('File found, importing the following file...')
                P.info( '    %s' % filePath )
                if self.checkBox.checkState() :
                    #  Import file as a group :
                    #mc.file( filePath, i=True, force=True, groupReference=True, groupName=grpName+'_GRP' )
                    mpFM.Merge( filePath, True )
                else :
                    #  Import file :
                    #mc.file( filePath, i=True, force=True )
                    mpFM.Merge( filePath, True )
            else :
                msg='Sorry, file to import doesn\'t exist...\n    %s' % filePath
                P.error( msg )
                Win.popup( title='NIM - Import Error', msg=msg )
                return

        #  Close window upon completion :
        self.close()
        
        return

    
    def file_saveAs(self) :
        'Function called when Save As button is activated.'
        
        #  Set Selected flag for saving only the selected objects :
        selected=False
        if self.app in ['Maya', 'Nuke', '3dsMax'] :
            selected=self.checkBox.checkState()
        
       
        #  Variables :
        tag=self.nim.Input('tag').text()
        task=self.nim.Input('task').currentText()
        basename=Api.to_basename( nim=self.nim )
        if self.app=='Maya' : ext=self.nim.Input('fileExt').currentText()
        elif self.app=='Nuke' : ext='.nk'
        elif self.app=='C4D' : ext='.c4d'
        elif self.app=='3dsMax' : ext='.max'
        
        #  Ensure that if tag has been entered, that the Basename doesn't already exist :
        if self.nim.name('tag') :
            for item in self.nim.Dict('base') :
                if item['basename']==basename :
                    msg='Specified basename, generated by the tag field ("%s"), already exists.\n' % basename
                    msg+='    Please either select an existing basename, or use a tag that isn\'t already in use.\n'
                    msg+='    Nothing done.'
                    P.error( msg )
                    Win.popup( title='NIM - Tag Error', msg=msg )
                    return False
        
        
        #  Version up file and add to API :
        Api.versionUp( nim=self.nim, selected=selected, win_launch=True )
        
        self.saveServerPref = True

        #  Refresh the Window :
        self.win_save()
        
        #  Close the window :
        self.close()
        
        return
    
    
    def file_verUp(self) :
        'Versions up the file, when the Version Up button is pressed'
        #  Get File Extension :
        if self.app=='Maya' : ext=self.nim['fileExt']['input'].currentText()
        elif self.app=='Nuke' : ext='.nk'
        elif self.app=='C4D' : ext='.c4d'
        elif self.app=='3dsMax' : ext='.max'
        #  Version Up :
        if self.nim.tab()=='SHOT' :
            Api.versionUp( projPath=self.nim.Input('server').currentText(), app=self.app, shotID=self.nim.ID('shot'), \
                task=self.nim.name('task'), basename=self.nim.name('base'), ext=ext )
        elif self.nim.tab()=='ASSET' :
            Api.versionUp( projPath=self.nim.Input('server').currentText(), app=self.app, assetID=self.nim.ID('asset'), \
                task=self.nim.name('task'), basename=self.nim.name('base'), ext=ext )
        #  Close window upon completion :
        self.close()
        return
    
    
    def file_pub(self) :
        'Publishes the current file, when the Publish button is pressed'
        #  Get File Extension :
        if self.app=='Maya' : ext=self.nim.Input('fileExt').currentText()
        elif self.app=='Nuke' : ext='.nk'
        elif self.app=='C4D' :  ext='.c4d'
        elif self.app=='3dsMax' : ext='.max'
        #  Version Up File :
        P.info('\nPublish Step #1 - Versioning Up the file...')
        ver_filePath=Api.versionUp( nim=self.nim, win_launch=True )
        if ver_filePath :
            #  Run Checks :
            P.info('\nPublishing Step #2 - Running publish checks...')
            #  TO DO -> Insert publish checks.
            
            #  Publish :
            P.info('\nPublishing Step #3 - Publishing work file and sym-link...\n')
            symLink=self.checkBox.isChecked()
            pub_filePath=Api.versionUp( nim=self.nim, win_launch=True, pub=True, symLink=symLink )
            #  Prompt to open work version :
            P.info('\nPublishing Step #4 - Prompting to open work file...\n')
            result=Win.popup( title=winTitle+' - Open Work File?', type='okCancel', \
                msg='Version Up and Publish complete!  Open work file?' )
            #  Open :
            if result=='OK' :
                if self.nim.app().lower()=='maya' :
                    P.info( 'Publishing Step #5 - Opening work file...\n    %s' % ver_filePath )
                    import maya.cmds as mc
                    mc.file( ver_filePath, force=True, open=True, ignoreVersion=True, prompt=False )
                elif self.nim.app().lower()=='nuke' :
                    P.info( 'Publishing Step #5 - Opening work file...\n    %s' % ver_filePath )
                    import nuke
                    #  Clear the scene, load file and rename :
                    nuke.scriptClear()
                    nuke.nodePaste( ver_filePath )
                    PS=nuke.root()
                    knob=PS.knob('name')
                    knob.setValue( ver_filePath.replace( '\\', '/' ) )
                elif self.nim.app().lower()=='c4d' :
                    print ver_filePath
                    print 'No Open protocal defined yet'
                elif self.nim.app().lower()=='hiero' :
                    print ver_filePath
                    print 'No Open protocal defined yet'
                if self.nim.app().lower()=='3dsmax' :
                    P.info( 'Publishing Step #5 - Opening work file...\n    %s' % ver_filePath )
                    import MaxPlus
                    mpFM = MaxPlus.FileManager
                    mpFM.Open( ver_filePath )
            
            #  Set Variables :
            if self.nim.app().lower()=='maya' :
                import nim_maya as M
                M.set_vars( nim=self.nim )
            elif self.nim.app().lower()=='nuke' :
                import nim_nuke as N
                N.set_vars( nim=self.nim )
            elif self.nim.app().lower()=='3dsmax' :
                import nim_3dsmax as Max
                Max.set_vars( nim=self.nim )
            
            #  Close window upon completion :
            P.info('\nClosing NIM Publish Window.\n')
            self.close()
            return True
        else :
            P.error('Unable to Version up the file, not added to the NIM API')
            return False
    
    
    #  Maya File Operations :
    def maya_fileReference(self) :
        'References a given Maya file'
        import maya.cmds as mc
        
        #  Get File Path :
        filePath=self.get_filePath()
        
        #  Derive file name to use for namespace :
        index=self.nim.Input('ver').currentItem().text().find(' - ')
        fileName=self.nim.Input('ver').currentItem().text()[0:index]
        #  Remove file extension from file name :
        fileName=os.path.splitext( fileName )[0]
        
        #  Reference the file :
        if self.checkBox.checkState() :
            mc.file( filePath, force=True, reference=True, namespace=fileName, groupReference=True, \
                groupName=fileName+'_GRP' )
        else :
            mc.file( filePath, force=True, reference=True, namespace=fileName )
        
        #  Close window upon completion :
        self.close()
        return

    #  Maya File Operations :
    def max_fileReference(self) :
        'References a given 3dsMax file'
        import MaxPlus

        #  Get File Path :
        filePath=self.get_filePath()
        
        #  Derive file name to use for namespace :
        index=self.nim.Input('ver').currentItem().text().find(' - ')
        fileName=self.nim.Input('ver').currentItem().text()[0:index]
        #  Remove file extension from file name :
        fileName=os.path.splitext( fileName )[0]
        
        #  Reference the file :
        if self.checkBox.checkState() :
            #GROUPED
            '''
            mc.file( filePath, force=True, reference=True, namespace=fileName, groupReference=True, \
                groupName=fileName+'_GRP' )
            '''
            #MaxPlus.SceneSetIgnoreFlag()
            pass
        else :
            #NOT GROUPED
            #mc.file( filePath, force=True, reference=True, namespace=fileName )
            #MaxPlus.SceneSetIgnoreFlag()
            pass

        #  Close window upon completion :
        self.close()
        return

#  End of Class


#  END

