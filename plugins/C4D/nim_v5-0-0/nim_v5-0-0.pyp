#! /usr/bin/python
#******************************************************************************
#
# Filename: C4D/nim_v5-0-0.py
# Version:  v5.0.0.210602
#
# Copyright (c) 2014-2022 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import os, sys
#  C4D Imports :
import c4d
from c4d import bitmaps, gui, plugins

#  NIM Imports :
_prefs={}
prefs_dirName='.nim'
prefs_fileName='prefs.nim'

'Gets the NIM home directory'
userHome=os.path.expanduser( '~' )
if userHome.endswith( 'Documents' ) :
    userHome=userHome[:-9]
user_home = os.path.normpath( os.path.join( userHome, prefs_dirName ) )
prefsFile=os.path.normpath( os.path.join( user_home, prefs_fileName ) )
print('NIM ~> NIM preferences:     %s' % prefsFile)

'Reads and stores preferences'
#  Create preferences, if necessary :
prefsFound = os.path.exists( prefsFile )
print('NIM ~> NIM preferences found:     %s' % prefsFound)

scriptFindPath=True
scriptInputPath=''
scriptPathValid=False
loadNIM=False

if not prefsFound :
    #  Prompt user to input Scripts Path :
    msg='Please input the NIM Scripts Path :\n'
    
    while scriptFindPath:
        scriptInputPath=gui.InputDialog( msg )
        print('NIM ~> NIM Scripts Set to:     %s' % scriptInputPath)
        print('NIM ~> Validating Path:')
        scriptPathValid = os.path.exists(os.path.join(scriptInputPath,"nim_core"))
        if not scriptPathValid:
            userInput=gui.QuestionDialog( 'Path to NIM Scripts is Invalid:\n %s \nTry again?' % scriptInputPath )
            if userInput :
                userInput='OK'
            else:
                scriptFindPath = False
                print("Exiting without setting NIM Script Path")

        else:
            scriptFindPath = False
            loadNIM=True
else:
    try :
        #  Read NIM preferences file :
        for line in open( prefsFile ) :
            name, var=line.partition("=")[::2]
            #  Changed "rstrip" method to "replace", so as not to replace spaces at the end
            var=var.replace( '\n', '' )
            var=var.replace( '\r', '' )
            if name !='' and name !='\n' :
                _prefs[name.strip()]=var
        #  Remove empty dictionary entries :
        prefs=dict( [(k,v) for k,v in list(_prefs.items()) if len(k)>0])
        if _prefs and 'NIM_Scripts' in list(_prefs.keys()) :
            scriptInputPath=_prefs['NIM_Scripts']
            loadNIM=True
        else:
            print("NIM Scripts location not found in preference file.")
            loadNIM=False

    except Exception as e :
        print("Unable to read preferences.")
        loadNIM=False


if loadNIM:
    nim_path=scriptInputPath
    if not nim_path in sys.path :
        sys.path.append( nim_path )
        print('NIM ~> Appended NIM Python directory to system paths...\nNIM ~>     %s' % nim_path)

    print('NIM ~> Importing NIM Libraries')

    import nim_core.nim_api as Api
    import nim_core.nim_file as F
    import nim_core.nim_print as P
    import nim_core.nim_c4d as C
    import nim_core.nim_prefs as Prefs
    import nim_core.nim_win as Win

    print('NIM ~> Loading NIM Variables')

    #  Variables :
    version='v2.6.0'
    winTitle='NIM_'+version+' - '
    nim_plugin_ID=1032427
    nim_openUI_ID=1032462
    nim_saveUI_ID=1032463
    nim_loadUI_ID=1032464
    nim_refUI_ID=1032521
    nim_pubUI_ID=1032465
    nim_verUp_ID=1032466
    nim_reloadScripts_ID=1032467
    nim_changeUser_ID=1032468

    print('NIM ~> Reading NIM Preferences')
    _prefs=Prefs.read()

    if not _prefs:
        loadNIM = False

def PluginMessage(id, data) :
    'Run every time the plugin starts up.'
    
    #  Construct custom NIM menu, when menus are built :
    if id==c4d.C4DPL_BUILDMENU :
        
        mainMenu=gui.GetMenuResource('M_EDITOR')
        pluginMenu=gui.SearchPluginMenuResource()
        
        #  NIM Menu :
        menu=c4d.BaseContainer()
        menu.InsData( c4d.MENURESOURCE_SUBTITLE, 'NIM' )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032462' )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032464' )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032463' )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032466' )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032465' )
        #menu.InsData( c4d.MENURESOURCE_SEPERATOR, True )
        #  XRef command :
        #menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032521' )
        menu.InsData( c4d.MENURESOURCE_SEPERATOR, True )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032468' )
        menu.InsData( c4d.MENURESOURCE_COMMAND, 'PLUGIN_CMD_1032467' )
                
        #  Place Menu :
        if pluginMenu :
            mainMenu.InsDataAfter( c4d.MENURESOURCE_STRING, menu, pluginMenu )
        else :
            mainMenu.InsData( c4d.MENURESOURCE_STRING, menu )
    
    #  Reload scripts, when the plugin is reloaded :
    elif id==c4d.C4DPL_RELOADPYTHONPLUGINS  :
        P.info('\nReloading NIM scripts...')
        F.scripts_reload()
        
    return

def print_plugins() :
    'Prints all of the loaded plugins and their ID numbers.'
    #  Print C4D Plugins :
    for plugin in plugins.FilterPluginList(c4d.PLUGINTYPE_SCENESAVER, True) :
        P.info( 'Plugin "%s" (ID #%s)' % (plugin.GetName(), plugin.GetID()) )
    return


#  START - Classes to register plugins :
class nim_openUI_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute( self, doc ) :
        'Run whenever the user activates the plugin.'
        P.info('\n\nBuilding UI...')
        win=C.nim_fileUI( mode='open', doc=doc )
        return win.Open( dlgtype=c4d.DLG_TYPE_MODAL, pluginid=nim_openUI_ID )


class nim_saveUI_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Run whenever the user activates the plugin.'
        P.info('\n\nBuilding UI...')
        win=C.nim_fileUI( mode='save' )
        return win.Open( dlgtype=c4d.DLG_TYPE_MODAL, pluginid=nim_plugin_ID )


class nim_loadUI_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Run whenever the user activates the plugin.'
        P.info('\n\nBuilding UI...')
        win=C.nim_fileUI( mode='load' )
        return win.Open( dlgtype=c4d.DLG_TYPE_MODAL, pluginid=nim_loadUI_ID )


class nim_refUI_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Run whenever the user activates the plugin.'
        P.info('\n\nBuilding UI...')
        win=C.nim_fileUI( mode='ref' )
        return win.Open( dlgtype=c4d.DLG_TYPE_MODAL, pluginid=nim_refUI_ID )


class nim_pubUI_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Run whenever the user activates the plugin.'
        P.info('\n\nBuilding UI...')
        win=C.nim_fileUI( mode='pub' )
        return win.Open( dlgtype=c4d.DLG_TYPE_MODAL, pluginid=nim_pubUI_ID )


class nim_verUp_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Version Up the current file.'
        Api.versionUp()
        return True


class nim_reloadScripts_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Reloads NIM scripts.'
        F.scripts_reload()
        return True


class nim_changeUser_cmd( plugins.CommandData ) :
    'Registers the plugin with C4D.'
    def Execute(self, doc) :
        'Selects a new NIM user for the connector.'
        P.info('Selecting NIM User...')
        userInfo = Win.userInfo()
        userName = userInfo[0]
        P.info('User = "%s"' % userName)
        #  Update Preferences :
        Prefs.update( attr='NIM_User', value=userName )
        return True

#  END - Classes to register plugins.


#  Run automatically :
if loadNIM:
    if __name__=='__main__' :
    
        #  Get File Information :
        nim4d_dir, nim4d_file=os.path.split(__file__)
        
        
        #  Icons :
        #===------
        
        #  Open Icon :
        nim_open_icon=bitmaps.BaseBitmap()
        nim_open_icon_path=os.path.join( nim4d_dir, 'res', 'nim_open_icon.tif' )
        nim_open_icon.InitWith( nim_open_icon_path )
        #  Save Icon :
        nim_save_icon=bitmaps.BaseBitmap()
        nim_save_icon_path=os.path.join( nim4d_dir, 'res', 'nim_save_icon.tif' )
        nim_save_icon.InitWith( nim_save_icon_path )
        #  Import Icon :
        nim_load_icon=bitmaps.BaseBitmap()
        nim_load_icon_path=os.path.join( nim4d_dir, 'res', 'nim_load_icon.tif' )
        nim_load_icon.InitWith( nim_load_icon_path )
        #  Ref Icon :
        nim_ref_icon=bitmaps.BaseBitmap()
        nim_ref_icon_path=os.path.join( nim4d_dir, 'res', 'nim_load_icon.tif' )
        nim_ref_icon.InitWith( nim_ref_icon_path )
        #  Publish Icon :
        nim_pub_icon=bitmaps.BaseBitmap()
        nim_pub_icon_path=os.path.join( nim4d_dir, 'res', 'nim_pub_icon.tif' )
        nim_pub_icon.InitWith( nim_pub_icon_path )
        #  Version Up Icon :
        nim_verUp_icon=bitmaps.BaseBitmap()
        nim_verUp_icon_path=os.path.join( nim4d_dir, 'res', 'nim_verUp_icon.tif' )
        nim_verUp_icon.InitWith( nim_verUp_icon_path )
        #  Reload Scripts Icon :
        nim_reloadScripts_icon=bitmaps.BaseBitmap()
        nim_reloadScripts_icon_path=os.path.join( nim4d_dir, 'res', 'nim_reloadScripts_icon.tif' )
        nim_reloadScripts_icon.InitWith( nim_reloadScripts_icon_path )
        #  Change User Icon :
        nim_changeUser_icon=bitmaps.BaseBitmap()
        nim_changeUser_icon_path=os.path.join( nim4d_dir, 'res', 'nim_changeUser_icon.tif' )
        nim_changeUser_icon.InitWith( nim_changeUser_icon_path )
        
        
        #  Register Plugins :
        #===----------------------
        
        #  NIM Open UI :
        plugins.RegisterCommandPlugin(
            id=nim_openUI_ID,
            str='Open...',
            info=0,
            icon=nim_open_icon,
            help='Opens files that have been added to the NIM API.',
            dat=nim_openUI_cmd()
        )
        #  NIM Save UI :
        plugins.RegisterCommandPlugin(
            id=nim_saveUI_ID,
            str='Save As...',
            info=0,
            icon=nim_save_icon,
            help='Saves files to the NIM API.',
            dat=nim_saveUI_cmd()
        )
        #  NIM Load UI :
        plugins.RegisterCommandPlugin(
            id=nim_loadUI_ID,
            str='Merge...',
            info=0,
            icon=nim_load_icon,
            help='Merges files into the current scene that have been added to the NIM API.',
            dat=nim_loadUI_cmd()
        )
        '''
        #  NIM Ref UI :
        plugins.RegisterCommandPlugin(
            id=nim_refUI_ID,
            str='XRef',
            info=0,
            icon=nim_ref_icon,
            help='References files that have been added to the NIM API.',
            dat=nim_refUI_cmd()
        )
        '''
        #  NIM Publish UI :
        plugins.RegisterCommandPlugin(
            id=nim_pubUI_ID,
            str='Publish...',
            info=0,
            icon=nim_pub_icon,
            help='Publishes files to the NIM API.',
            dat=nim_pubUI_cmd()
        )
        #  NIM Version Up :
        plugins.RegisterCommandPlugin(
            id=nim_verUp_ID,
            str='Version Up',
            info=0,
            icon=nim_verUp_icon,
            help='Versions Up and adds files to the NIM API.',
            dat=nim_verUp_cmd()
        )
        #  Reload NIM Scripts :
        plugins.RegisterCommandPlugin(
            id=nim_reloadScripts_ID,
            str='Reload NIM scripts',
            info=0,
            icon=nim_reloadScripts_icon,
            help='Reloads NIM scripts.',
            dat=nim_reloadScripts_cmd()
        )
        #  Reload NIM Scripts :
        plugins.RegisterCommandPlugin(
            id=nim_changeUser_ID,
            str='Change User',
            info=0,
            icon=nim_changeUser_icon,
            help='Select a NIM user.',
            dat=nim_changeUser_cmd()
        )

#  END

