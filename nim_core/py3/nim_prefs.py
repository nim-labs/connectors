#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_prefs.py
# Version:  v5.1.2.220314
#
# Copyright (c) 2014-2022 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import os, sys, re, traceback
import urllib.parse

#  NIM Imports :
from . import nim_api as Api
from . import nim_file as F
from . import nim_print as P
from . import nim_win as Win

isGUI = False
try :
    #Validate Against DCC Environment
    if F.get_app() is not None :
        isGUI = True
except :
    pass

#  Variables :
version='v5.1.2'
prefs_dirName='.nim'
prefs_fileName='prefs.nim'
winTitle='NIM_'+version
nim_URL='http://hostname/nimAPI.php'
nim_useSLL='False'
nim_scripts = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, os.pardir))
nim_user, nim_userID='', ''
nim_img='/img/nim_logo.png'
css_dir= nim_scripts+'/css'
css_dir= css_dir.replace('\\','/')
#http_srch=re.compile( '^http[s]?://' )
#ip_srch=re.compile( '[0-9\.]+' )
equal_srch=re.compile( '=' )


def get_user() :
    'Gets the user name from the NIM Preferences.'
    usr=False
    #_prefs=Prefs.read()
    _prefs=read()
    if _prefs and 'NIM_User' in list(_prefs.keys()) :
        usr=_prefs['NIM_User']
    return usr


def get_userInfo( url='' ) :
    'Retrieves the User ID to use for the window'
    #print "get_userInfo(%s)" % url
    #user=Api.get_user()
    #userID=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False, nimURL=url )
    user=None
    userID=None
    '''
    users=Api.get( sqlCmd={'q': 'getUsers'}, debug=False, nimURL=url )
        
    if not userID and users :
        
        userList=[]
        for u in users : 
            userList.append( u['username'] )
                
        #  Create window to get user name from :
        if F.get_app() !='C4D' :
            user=Win.popup( title='User Name Error', msg='Pick a username to use', type='comboBox', pyside=True, _list=userList )
        else :
            import nim4d_userWin as W
            userWin=W.GetUser()
            userWin.Open( dlgtype=W.c4d.DLG_TYPE_MODAL )
            user=userWin.get_user()
            print 'User = "%s"' % user
    '''
    if not userID :
        userInfo = Win.userInfo(url=url, newUser=True)
        if userInfo :
            #  Get user ID :
            print(userInfo)
            user=userInfo[0]
            userID=userInfo[1]

            if not userID :
                userResult=Api.get( sqlCmd={ 'q': 'getUserID', 'u': user}, debug=False, nimURL=url )

                if type(userResult)==type(list()) and len(userResult)==1 :
                    userID=userResult[0]['ID']
                    return (user, userID)
                else :
                    return False
            else :
                return (user, userID)
    else :
        return (user, userID)


def set_userInfo( ID=0, name='') :
    'Sets the user name in the NIM Prefereces'
    global nim_user
    global nim_userID
    nim_user = name
    nim_userID = ID
    return


def get_url() :
    'Retrieves the NIM URL from the NIM Preferences.'
    url=False
    global nim_URL
    
    if not nim_URL or nim_URL == 'http://hostname/nimAPI.php':
        _prefs=read()
        if _prefs and 'NIM_URL' in list(_prefs.keys()) :
            nim_URL=_prefs['NIM_URL']
    
    url = nim_URL
    return url


def get_home() :
    'Gets the NIM home directory'
    userHome=os.path.expanduser( '~' )
    if userHome.endswith( 'Documents' ) :
        userHome=userHome[:-9]
    return os.path.normpath( os.path.join( userHome, prefs_dirName ) )


def mk_home() :
    'Creates the nim folder in the user\'s home directory'
    apps=F.get_apps()
    nimHome=get_home()
    
    #  Make NIM home directory :
    if not os.path.exists( nimHome ) :
        os.makedirs( nimHome )
    
    #  Make NIM subdirectories :
    nimHomeDirs=['scripts', 'imgs', 'css', 'apps']
    for subDir in nimHomeDirs :
        mk_dir=os.path.normpath( os.path.join( nimHome, subDir ) )
        if not os.path.exists( mk_dir ) :
            os.makedirs( mk_dir )
    
    #  Make Application subdirectories :
    for app in apps :
        mk_dir=os.path.normpath( os.path.join( nimHome, 'apps', app ) )
        if not os.path.exists( mk_dir ) :
            os.makedirs( mk_dir )
    
    return nimHome


def get_path() :
    'Derives the path to save preferences to/from'
    return os.path.normpath( os.path.join( get_home(), prefs_fileName ) )


def _inputURL() :
    'Gets the NIM API URL from the user, via a popup'
    global nim_URL, version

    isGUI = False
    try :
        #Validate Against DCC Environment
        if F.get_app() is not None :
            isGUI = True
    except :
        pass

    #  Prompt user to input URL :
    msg='Please input the NIM API URL :'
    if isGUI :
        url=Win.popup( title=winTitle+' - Get URL', msg=msg, type='input', defaultInput=nim_URL )
    else :
        url=input(msg)
    #P.info( 'NIM URL Set to: %s' % url ) 
    if url : 
        # Check for '/nimAPI.php?' at end of URL

        if url.endswith('nimAPI.php') :
            url = url+"?"
        
        '''
        if not url.endswith('/nimAPI.php?'):
            if not url.endswith('/'):
                url = url+"/nimAPI.php?"
            else :
                url = url+"nimAPI.php?"
        '''

        return url

    else : 
        return False


def _verifyURL( url='' ) :
    'Verifies a given URL as valid'
    #  Verify URL :
    if not url : return False

    # Validate URL Pattern
    parsedURL = urllib.parse.urlparse(url)
    min_attributes = ('scheme', 'netloc')
    if not all([getattr(parsedURL, attr) for attr in min_attributes]):
        #error = "'{url}' string has no scheme or netloc.".format(url=parsedURL.geturl())
        #print(error)
        print("URL Format is invalid")
        return False
    else:
        print("Valid URL Format Entered")


    result=Api.get( sqlCmd={'q': 'testAPI'}, debug=False, nimURL=url )
    P.info('Validating API: %s' % result)
    if result : 
        #setting global variable
        return url
    else : 
        return False


def _prefsFail() :
    'Determines course of action, after a user has input an invalid NIM URL'
    msg='Sorry, specified NIM URL is invalid.'
    P.error( msg )
    msg+='\n    Would you like to enter another one?'
    result=Win.popup( title='NIM - URL Error', msg=msg, type='okCancel' )
    #P.info( 'WINDOW RESULT: %s' % result)
    if result=='OK' :
        url=_inputURL()
        test=_verifyURL( url )
        P.info( 'NIM URL Verified: %s' % test)
        if test : return [result, url]
    return [result, False]


def _nimPrefs() :
    'Returns a dictionary of NIM preferences'
    nimDict={
        'NIM_URL': nim_URL,
        'NIM_User': nim_user,
        'NIM_Scripts': nim_scripts,
        'NIM_UserScripts': os.path.normpath(os.path.join( get_home(), 'scripts' ))+os.sep,
        'NIM_DebugMode': 'False',
        'NIM_Thumbnail': nim_img
    }
    return nimDict


def _nimPrefsList() :
    'Returns a list of keys from the NIM Prefs Dictionary, for orderly printing'
    nimList=['NIM_URL', 'NIM_User', 'NIM_Scripts', 'NIM_UserScripts', 'NIM_DebugMode', 'NIM_Thumbnail']
    return nimList


def _appPrefs( app='Maya' ) :
    'Returns a dictionary of NIM Preferences Dictionary, common for all applications.'
    appDict={
        app+'_WinPosX': '250',
        app+'_WinPosY': '250',
        app+'_WinWidth': '600',
        app+'_WinHeight': '675',
        #app+'_Scripts':'',
        app+'_StyleSheetDir': css_dir,
        app+'_UseStyleSheet': 'None',
        app+'_Job': '',
        #app+'_DefaultServerPath': '',
        app+'_ServerPath': '',
        app+'_ServerID': '',
        app+'_Tab': 'SHOT',
        app+'_Asset': '',
        app+'_Show': '',
        app+'_Shot': '',
        app+'_Filter': '',
        app+'_Task': '',
        app+'_Basename': '',
        app+'_Version': ''
    }
    return appDict


def _appPrefsList( app='Maya' ) :
    'Returns a list of keys from the Application Preferences Dictionary, for orderly printing'
    appList=[app+'_WinPosX', app+'_WinPosY', app+'_WinWidth', app+'_WinHeight', \
        app+'_StyleSheetDir', app+'_UseStyleSheet', app+'_Job', \
        app+'_ServerPath', app+'_ServerID', app+'_Tab', app+'_Asset', app+'_Show', app+'_Shot', app+'_Filter', \
        app+'_Task', app+'_Basename', app+'_Version']
    return appList


def check() :
    'Ensures that all the necessary attributes exist in the NIM prefences file.'
    apps=F.get_apps()
    prefs=[]
    
    #  Construct list of required application preferences :
    prefs=_nimPrefsList()
    for app in apps :
        prefs.extend( _appPrefsList( app ) )
    
    #  Delete found preferences :
    for line in open(get_path()) :
        if  equal_srch.search( line ) :
            attr=line.lstrip().rstrip().split('=')[0]
            if attr in prefs :
                del prefs[prefs.index(attr)]
    
    if prefs :
        P.warning( '\nNIM preferences missing the following attributes :' )
        for pref in prefs :
            P.warning( '    %s' % pref )
        P.warning( '' )
        return prefs
    else :
        return False


def mk_default( recreatePrefs=False, notify_success=True ) :
    'Makes default preferences'

    global apps
    global nim_api
    global nim_user, nim_userID
    global nim_URL

    isGUI = False
    try :
        #Validate Against DCC Environment
        if F.get_app() is not None :
            isGUI = True
    except :
        pass
    
    nimHome=mk_home()
    prefsFile=get_path()
    apps=F.get_apps()
    #nim_user=F.get_user()
    url, userID=1, ''
    
    #  Create home dir, if necessary :
    mk_home()
    
    #  Check to see if preferences need to be re-created :
    if os.path.exists( prefsFile ) :
        #  If preferences have missing attributes, add those attributes to prefs file:
        prefs_check=check()
        if prefs_check :
            #  Open NIM prefs file for appending :
            _prefFile=open( prefsFile, 'a' )
            _prefFile.write('\n')
            #  Write NIM preferences :
            nim_prefs=_nimPrefs()
            missing_at_least_one_nim_pref = False
            for key in prefs_check :
                if key in nim_prefs :
                    missing_at_least_one_nim_pref = True
                    _prefFile.write( key+'='+nim_prefs[key]+'\n' )
            if missing_at_least_one_nim_pref :
                _prefFile.write('\n')
            #  Write Application Preferences :
            for app in apps :
                app_prefs=_appPrefs( app )
                for key in prefs_check :
                    if key in app_prefs :
                        _prefFile.write( key+'='+app_prefs[key]+'\n' )
                _prefFile.write('\n')
            #  Close file :
            _prefFile.close()
        else :            
            #  Ask to recreate existing preferences :
            if recreatePrefs :
                if isGUI :
                    recreate=Win.popup( title=winTitle+' - Prefs Exist', \
                        msg='Preferences already exist.\nWould you like to re-create your preferences?', \
                        type='okCancel' )
                else :
                    recreate=input("Preferences already exist. Would you like to re-create your preferences? (Y/N) ")
                    if recreate == 'Y' or recreate == 'y':
                        recreate='OK'

                if recreate=='OK' :
                    P.info( 'Deleting previous preferences file...' )
                    try :
                        os.remove( prefsFile )
                    except Exception as e :
                        P.error( 'Unable to delete preferences' )
                        P.error( '    %s' % traceback.print_exc() )
                        return False
                else : return prefsFile
            else : return prefsFile
    
    #  URL :
    if not os.path.exists( prefsFile ) :
        #  Loop until valid URL found, or Cancel pressed :
        search_for_url = True
        search_for_user = False
        while search_for_url:
            url=_inputURL()
            result=_verifyURL( url )
            if result: 
                P.info('URL Valid')
                nim_URL = url
                search_for_url = False
                search_for_user = True
                break
            else:
                msg='The NIM API URL entered is invalid :\n %s \nTry Again?' % url
                if isGUI :
                    keepGoing=Win.popup( title=winTitle+' - Get URL', msg=msg, type='okCancel' )
                else :
                    keepGoing=input('The NIM API URL entered is invalid. Try Again? (Y/N):' )
                    if keepGoing == 'Y' or keepGoing == 'y' :
                        keepGoing = 'OK'

                if keepGoing != 'OK':
                    P.error('Exiting without setting NIM Preferences.')
                    search_for_url = False
                    search_for_user = False
                    return False
        
        #  Verify User :
        if search_for_user :
            P.info('Searching for NIM User')
            #Force input of username at preference creation
            result=get_userInfo( url=nim_URL )
            if type(result)==type(tuple()) and len(result)==2 :
                nim_user=result[0]
                nim_userID=result[1]

        #  Notify of failure if there is information missing :
        if not nim_URL or not nim_user or not nim_userID :
            P.warning( 'Could not derive the appropriate information for NIM.' )
            Win.popup( title=winTitle+' - URL Error', msg='Could not derive the appropriate information for NIM.' )
            return False
    

    #  Write Preferences :
    if not os.path.exists( prefsFile ) :
        #  Open NIM prefs file for writing :
        _prefFile=open( prefsFile, 'w' )
        #  Write NIM preferences :
        nim_prefs=_nimPrefs()
        nim_prefsList=_nimPrefsList()
        for key in nim_prefsList :
            if key in nim_prefs :
                _prefFile.write( key+'='+nim_prefs[key]+'\n' )
        _prefFile.write('\n')
        #  Write Application Preferences :
        for app in apps :
            app_prefs=_appPrefs( app )
            app_prefsList=_appPrefsList( app )
            for key in app_prefsList :
                if key in app_prefs :
                    _prefFile.write( key+'='+app_prefs[key]+'\n' )
            _prefFile.write('\n')
        #  Close file :
        _prefFile.close()
        
        #  Print success :
        P.info( '\nCreated NIM preference file :\n    %s' % os.path.normpath( prefsFile ) )
        if notify_success :
            Win.popup( title='Created NIM Preferences', \
                msg='Successfully created NIM directory and preferences.' )
    
    #  Notify user that Preferences already exist :
    else :
        P.info( '\nNIM Preferences already exist :\n    %s\n' % os.path.normpath( prefsFile ) )
    
    return os.path.normpath( prefsFile )


def read() :
    'Reads and stores preferences'

    #P.info('nim_prefs.read')

    prefsFile=get_path()
    _prefs={}
    
    #  Create preferences, if necessary :
    if not os.path.isfile( prefsFile ) :
        result = mk_default()
        if not result:
            P.error( 'Unable to create default preferences.' )
            return False
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
        return prefs
    except Exception as e :
        P.error( 'Unable to read preferences.' )
        return False


def update( attr=None, app='', value='' ) :
    'Updates the preferences file with whatever attribute is specified'
    #P.info('nim_prefs.update')

    #  Variables :
    _prefsFile=get_path()
    _prefs=read()
    
    if not os.path.isfile( _prefsFile ) :
        mk_default()
    if not attr :
        P.info( 'Error : At least one preference attribute must be specified to write out' )
        return
    _pre, _txt='', ''
    _skip=False
    if app :
        _pre=app+'_'
    _clearable=[_pre+'Job', _pre+'Asset', _pre+'Show', _pre+'Shot', _pre+'Task', _pre+'Basename', _pre+'Version']
    
    #  Retrieve old preferences :
    _old=open( _prefsFile, 'r' )
    
    #  Write out preferences :
    for line in _old :
        #  Operate on lines matching the application and attribute names specified :
        if re.search( '^'+_pre+attr[0].upper()+attr[1:]+'=', line ) :
            #  Don't store "Select.." or "None" combo box options :
            if value not in ['Select..', 'Select...', 'None', ''] and value :
                _txt+=_pre+attr[0].upper()+attr[1:]+'='+str(value)+'\n'
                #  Print :
                P.debug( 'Writing "%s=%s" to preferences...' % ( _pre+attr[0].upper()+attr[1:], value ) )
            else :
                #  Write out Shot/Asset for the tab :
                if re.search( '^'+_pre+'Tab', line ) :
                    _txt+=_pre+attr[0].upper()+attr[1:]+'=SHOT\n'
                else :
                    _txt+=_pre+attr[0].upper()+attr[1:]+'=\n'
            _skip=True
            continue
        
        #  Operate on lines without the application/attribute names specified :
        else :
            srch=re.search( '^'+_pre+'[a-zA-Z]+', line )
            #  Operate on lines related to the given attribute :
            if _skip and srch :
                if not re.search( '^'+_pre+'Tab', line ) :
                    if srch.group() in _clearable and attr in _clearable :
                        _txt+=srch.group()+'=\n'
                    else : _txt+=line
                #  Deal with assetIndex attributes :
                else : _txt+=line
            else : _txt+=line
     
     #  Close old preference file, so it can be over-written :
    _old.close()
    
    #  Write new preferences :
    _old=open( _prefsFile, 'w' )
    _old.write( _txt )
    _old.close()
    
    return


def Dbug_toggle() :
    'Toggles debug mode on/off, inside of Maya'
    import maya.cmds as mc
    import maya.mel as mm
    
    P.info( 'Toggling debug mode...' )
    prefs=read()
    try : debugMode=prefs['NIM_DebugMode']
    except : debugMode=prefs['DebugMode']
    P.info( '    Debug mode is currently set to %s.' % debugMode )
    
    #  Turn D-bug mode Off, if it is On :
    if debugMode=='True' :
        update( attr='NIM_DebugMode', value='False' )
        shelf=mm.eval( '$tempVar=`tabLayout -q -st $gShelfTopLevel`' )
        shelf_icons=mc.shelfLayout( shelf, query=True, childArray=True )
        for icon in shelf_icons :
            shelf_btn=mc.shelfButton( icon, query=True, label=True )
            if shelf_btn=='Dbug' :
                iconPath='I:/VAULT/NIM/NIM_v5.1/imgs/maya_shelf_icons/debugOff_icon.png'
                mc.shelfButton( icon, edit=True, image=iconPath )
        P.info( '  D-bug mode has been turned off!' )
    
    #  Turn D-bug mode On, if it is Off :
    elif debugMode=='False' :
        update( attr='NIM_DebugMode', value='True' )
        shelf=mm.eval( '$tempVar=`tabLayout -q -st $gShelfTopLevel`' )
        shelf_icons=mc.shelfLayout( shelf, query=True, childArray=True )
        for icon in shelf_icons :
            shelf_btn=mc.shelfButton( icon, query=True, label=True )
            if shelf_btn=='Dbug' :
                iconPath='I:/VAULT/NIM/NIM_v5.1/imgs/maya_shelf_icons/debugOn_icon.png'
                mc.shelfButton( icon, edit=True, image=iconPath )
        P.info( '  D-bug mode has been turned on!' )
    
    return


#  End

