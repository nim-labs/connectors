#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_api.py
# Version:  v2.5.1.161115
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  General Imports :
import json, os, re, sys, traceback
import urllib, urllib2
try :
    import ssl
except :
    print "NIM: Failed to load SSL - API"
    pass

import mimetools, mimetypes
import email.generator as email_gen
import cStringIO
import stat

#  NIM Imports :
import nim as Nim
import nim_api as Api
import nim_file as F
import nim_prefs as Prefs
import nim_print as P
import nim_tools
import nim_win as Win

#  Variables :
version='v2.5.0'
winTitle='NIM_'+version


# Get NIM Connection Information
def get_connect_info() :
    'Returns the connection information from preferences'

    _prefs=Prefs.read()

    if _prefs and 'NIM_URL' in _prefs.keys() :
        nim_apiURL=_prefs['NIM_URL']
    else :
        P.info( '"NIM_URL" not found in preferences!' )
        return False

    if _prefs and 'NIM_User' in _prefs.keys() :
        nim_apiUser=_prefs['NIM_User']
    else :
        P.info( '"NIM_User" not found in preferences!' )
        return False
        
    nim_apiKey = get_apiKey()

    connect_info = {'nim_apiURL':nim_apiURL, 'nim_apiUser':nim_apiUser, 'nim_apiKey':nim_apiKey}
    return connect_info


#  Get API Key for user
def get_apiKey() :
    key = ''
    key_fileName = 'nim.key'
    key_path = os.path.normpath( os.path.join( Prefs.get_home(), key_fileName ) )

    if os.path.isfile( key_path ) :
        try :
            #  Read NIM API KEY file :
            with open(key_path, 'r') as f:
                key = f.readline().strip()
        except Exception, e :
            P.error( 'Unable to read api key.' )
    else :
        P.warning( 'API Key not found.' )

    return key


def testAPI(nimURL=None, nim_apiUser='', nim_apiKey='') :
    sqlCmd={'q': 'testAPI'}
    cmd=urllib.urlencode(sqlCmd)
    _actionURL="".join(( nimURL, cmd ))
    request = urllib2.Request(_actionURL)
    try :
        request.add_header("X-NIM-API-USER", nim_apiUser)
        request.add_header("X-NIM-API-KEY", nim_apiKey)
        request.add_header("Content-type", "application/x-www-form-urlencoded; charset=UTF-8")
        try :
            myssl = ssl.create_default_context()
            myssl.check_hostname=False
            myssl.verify_mode=ssl.CERT_NONE
            _file = urllib2.urlopen(request,context=myssl)
        except :
            _file = urllib2.urlopen(request)
        fr=_file.read()
        try : result=json.loads( fr )
        except Exception, e :
            P.error( traceback.print_exc() )
        _file.close()
        return result
    except urllib2.URLError, e :
        P.error( '\nFailed to read NIM API' )
        P.error( '   %s' % _actionURL )
        url_error = e.reason
        P.error('URL ERROR: %s' % url_error)
        err_msg = 'NIM Connection Error:\n\n %s' %  url_error;
        Win.popup(msg=err_msg)
        P.debug( '    %s' % traceback.print_exc() )
        return False

#  Basic API query command :
#  DEPRECATED in 2.5 in favor of connect()
def get( sqlCmd=None, debug=True, nimURL=None ) :
    result=False
    result = connect( method='get', params=sqlCmd, nimURL=nimURL )
    return result

#  Basic API query command :
#  DEPRECATED in 2.5 in favor of connect()
def post( sqlCmd=None, debug=True, nimURL=None ) :
    result=False
    result = connect( method='post', params=sqlCmd, nimURL=nimURL )
    return result


def connect( method='get', params=None, nimURL=None ) :
    'Querys MySQL server and returns decoded json array'
    result=None
    
    connect_info = None
    if not nimURL :
        connect_info = get_connect_info()
    if connect_info :
        nimURL = connect_info['nim_apiURL']
        nim_apiUser = connect_info['nim_apiUser']
        nim_apiKey = connect_info['nim_apiKey']
    else :
        nim_apiUser = ''
        nim_apiKey = ''
    
    if params :
        if method == 'get':
            cmd=urllib.urlencode(params)
            _actionURL="".join(( nimURL, cmd ))
        elif method == 'post':
            cmd=urllib.urlencode(params)
            _actionURL = re.sub('[?]', '', nimURL)
        else :
            P.error('Connection method not defined in request.')
            Win.popup( title='NIM Connection Error', msg='NIM Connection Error:\n\n Connection method not defined in request.')
            return False

        try :
            if method == 'get':
                request = urllib2.Request(_actionURL)
            elif method == 'post':
                request = urllib2.Request(_actionURL, cmd)
            
            request.add_header("X-NIM-API-USER", nim_apiUser)
            request.add_header("X-NIM-API-KEY", nim_apiKey)
            request.add_header("Content-type", "application/x-www-form-urlencoded; charset=UTF-8")
            try :
                myssl = ssl.create_default_context()
                myssl.check_hostname=False
                myssl.verify_mode=ssl.CERT_NONE
                _file = urllib2.urlopen(request,context=myssl)
            except :
                _file = urllib2.urlopen(request)
            fr=_file.read()
            try : result=json.loads( fr )
            except Exception, e :
                P.error( traceback.print_exc() )
            _file.close()

            # Test for failed API Validation
            if type(result)==type(list()) and len(result)==1 :
                try :
                    error_msg = result[0]['error']
                    P.error( "API Error %s" % error_msg )
                    if(error_msg == 'API Key Not Found.') :
                        #Win.popup( title='NIM API Error', msg='NIM API Key Not Found.\n\nNIM Security is set to require the use of API Keys. \
                        #                                        Please contact your NIM Administrator to obtain a NIM API KEY.' )
                        api_result = Win.setApiKey()

                    if(error_msg == 'Failed to validate user.') :
                        #Win.popup( title='NIM API Error', msg='Failed to validate user.\n\nNIM Security is set to require the use of API Keys. \
                        #                                        Please obtain a valid NIM API KEY from your NIM Administrator.' )
                        api_result = Win.setApiKey()

                    if(error_msg == 'API Key Expired.') :
                        Win.popup( title='NIM API Error', msg='NIM API Key Expired.\n\nNIM Security is set to require the use of API Keys. \
                                                                Please contact your NIM Administrator to update your NIM API KEY expiration.' )
                        #return False <-- returning false loads reset prefs msgbox
                except :
                    pass
            
            return result

        except urllib2.URLError, e :
            P.error( '\nFailed to read URL for the following command...\n    %s' % params )
            P.error( '   %s' % _actionURL )
            url_error = e.reason
            P.error('URL ERROR: %s' % url_error)
            err_msg = 'NIM Connection Error:\n\n %s' %  url_error;
            P.debug( '    %s' % traceback.print_exc() )

            err_msg +='\n\n'+\
                '    Would you like to recreate your preferences?'
            P.error( err_msg )
            reply=Win.popup( title='NIM Error', msg=err_msg, type='okCancel' )
            #  Re-create preferences, if prompted :
            if reply=='OK' :
                prefsFile=Prefs.get_path()
                if os.path.exists( prefsFile ) :
                    os.remove( prefsFile )
                result = Prefs.mk_default()
                return False
            else :
                return
    else :
        P.error( 'No SQL command provided to run.' )
        return False


def upload( params=None ) :

    connect_info = get_connect_info()
    nimURL = connect_info['nim_apiURL']
    nim_apiUser = connect_info['nim_apiUser']
    nim_apiKey = connect_info['nim_apiKey']

    _actionURL = nimURL.encode('ascii')

    P.info("Verifying API URL: %s" % _actionURL)

   # Create opener with extended form post support
    try:
        opener = urllib2.build_opener(FormPostHandler)
        #opener.addheaders = [('X-NIM-API-USER', nim_apiUser)]
        #opener.addheaders = [('X-NIM-API-KEY', nim_apiKey)]
    except:
        P.error( "Failed building url opener")
        P.error( traceback.format_exc() )
        return False

    # Test for SSL Redirection
    isRedirected = False
    try:
        testCmd = {'q': 'testAPI'}
        cmd=urllib.urlencode(testCmd)
        testURL="".join(( nimURL, cmd ))
        req = urllib2.Request(testURL)
        res = urllib2.urlopen(req)
        finalurl = res.geturl()
        if nimURL.startswith('http:') and finalurl.startswith('https'):
            isRedirected = True
            _actionURL = _actionURL.replace("http:","https:")
            P.info("Redirect: %s" % _actionURL)
    except:
        P.error("Failed to test for redirect.")

    try:
        result = opener.open(_actionURL, params).read()
        P.info( "Result: %s" % result )

        # Test for failed API Validation
        if type(result)==type(list()) and len(result)==1 :
            try :
                error_msg = result[0]['error']
                P.error( error_msg )
                if(error_msg == 'API Key Not Found.') :
                    #Win.popup( title='NIM API Error', msg='NIM API Key Not Found.\n\nNIM Security is set to require the use of API Keys. \
                    #                                        Please contact your NIM Administrator to obtain a NIM API KEY.' )
                    api_result = Win.setApiKey()

                if(error_msg == 'Failed to validate user.') :
                    #Win.popup( title='NIM API Error', msg='Failed to validate user.\n\nNIM Security is set to require the use of API Keys. \
                    #                                        Please obtain a valid NIM API KEY from your NIM Administrator.' )
                    api_result = Win.setApiKey()

                if(error_msg == 'API Key Expired.') :
                    Win.popup( title='NIM API Error', msg='NIM API Key Expired.\n\nNIM Security is set to require the use of API Keys. \
                                                            Please contact your NIM Administrator to update your NIM API KEY expiration.' )
                    #return False <-- returning false loads reset prefs msgbox
            except :
                pass

    except urllib2.HTTPError, e:
        if e.code == 500:
            P.error("Server encountered an internal error. \n%s\n(%s)\n%s\n\n" % (_actionURL, params, e))
            return False
        else:
            P.error("Unanticipated error occurred uploading image: %s" % (e))
            return False
    else:
        if params["file"] is not None:
            if not str(result).startswith("1"):
                P.error("Could not upload file successfully, but not sure why.\nUrl: %s\nError: %s" % (_actionURL, str(result)))
                return False
    
    return True


class FormPostHandler(urllib2.BaseHandler):
    """
    Handler for multipart form data
    """
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first
    
    def http_request(self, request):
        data = request.get_data()
        if data is not None and not isinstance(data, basestring):
            files = []
            params = []
            for key, value in data.items():
                if isinstance(value, file):
                    files.append((key, value))
                else:
                    params.append((key, value))
            if not files:
                data = urllib.urlencode(params, True) # sequencing on
            else:
                boundary, data = self.encode(params, files)
                content_type = 'multipart/form-data; boundary=%s' % boundary
                request.add_unredirected_header('Content-Type', content_type)
                connect_info = get_connect_info()
                nim_apiUser = connect_info['nim_apiUser']
                nim_apiKey = connect_info['nim_apiKey']
                request.add_header("X-NIM-API-USER", nim_apiUser)
                request.add_header("X-NIM-API-KEY", nim_apiKey)
                
            request.add_data(data)
        return request
    
    def encode(self, params, files, boundary=None, buffer=None):
        if boundary is None:
            #boundary = mimetools.choose_boundary()
            boundary = email_gen._make_boundary()
        if buffer is None:
            buffer = cStringIO.StringIO()
        for (key, value) in params:
            buffer.write('--%s\r\n' % boundary)
            buffer.write('Content-Disposition: form-data; name="%s"' % key)
            buffer.write('\r\n\r\n%s\r\n' % value)
        for (key, fd) in files:
            filename = fd.name.split('/')[-1]
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            buffer.write('--%s\r\n' % boundary)
            buffer.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buffer.write('Content-Type: %s\r\n' % content_type)
            buffer.write('Content-Length: %s\r\n' % file_size)
            fd.seek(0)
            buffer.write('\r\n%s\r\n' % fd.read())
        buffer.write('--%s--\r\n\r\n' % boundary)
        buffer = buffer.getvalue()
        return boundary, buffer
    
    def https_request(self, request):
        return self.http_request(request)


#  Job/Show/Shot data retrievers :
#===------------------------------------------

def get_app() :
    'Figure out what app is running.'
    app=''
    try :
        import maya.cmds as mc
        return 'Maya'
    except :pass
    try :
        import nuke
        return 'Nuke'
    except : pass
    try :
        import c4d
        return 'C4D'
    except : pass
    try :
        import hiero.ui
        return 'Hiero'
    except : pass
    try :
        import MaxPlus
        return '3dsMax'
    except : pass
    try :
        import hou
        return 'Houdini'
    except : pass
    try:
        import cinesync
        return 'Cinesync'
    except:
        pass
    return None

def get_user() :
    'Retrieves the current user\'s username'
    #  Get username :
    if os.getenv( 'USER' ) :
        _usr=os.getenv( 'USER' )
    elif os.getenv( 'USERNAME' ) :
        _usr=os.getenv( 'USERNAME' )
    if _usr :
        return _usr
    else :
        return False

def get_userID( user='' ) :
    'Retrieves the current user\'s user ID'
    print "get_userID: %s" % user
    if not user :
        user=get_user()
    try :
        userID=get( {'q': 'getUserID', 'u': str(user)} )
        print userID
        if type(userID)==type(list()) and len(userID)==1 :
            return userID[0]['ID']
        else :
            return userID
    except Exception, e :
        print traceback.print_exc()
        return False

def get_userList( url=None ) :
    'Retrieves the list of NIM Users from the NIM Preferences.'
    usrList=False
    if url:
        usrList=get( sqlCmd={'q': 'getUsers'}, nimURL=url )
    else:
        usrList=get( sqlCmd={'q': 'getUsers'} )
    return usrList

def get_jobs( userID=None, folders=False ) :
    'Builds a dictionary of all jobs for a given user'
    jobDict={}
    #  Build dictionary of jobs :
    _jobs=get( {'q': 'getUserJobs', 'u': userID} )
    try:
        for job in _jobs :
            if not folders :
                jobDict[str(job['number'])+'_'+str(job['jobname'])]=str(job['ID'])
            else :
                jobDict[str(job['number'])+'_'+str(job['folder'])]=str(job['ID'])
        return jobDict
    except :
        P.error("Failed to get jobs")
        return False

def get_servers( ID=None ) :
    'Retrieves servers associated with a specified job ID - does not match phpAPI'
    if ID :
        servers=get( {'q':'getJobServers', 'ID':ID} )
        return servers

def get_jobServers( ID=None ) :
    'Retrieves servers associated with a specified job ID - matches phpAPI'
    if ID :
        servers=get( {'q':'getJobServers', 'ID':ID} )
        return servers

def get_serverInfo( ID=None ) :
    'Retrieves servers information'
    if ID :
        serverInfo=get( {'q':'getServerInfo', 'ID':ID} )
        return serverInfo

def get_serverOSPath( ID=None, os='' ) :
    'Retrieves server path based on OS'
    if ID :
        serverOSPath=get( {'q':'get_serverOSPath', 'ID':ID, 'os':os} )
        return serverOSPath
    else:
        return "Server ID Missing"

def get_osPath( fileID=None, os='' ) :
    'Retrieves file path based on OS'
    if fileID :
        fileOSPath=get( {'q':'getOSPath', 'fileID':fileID, 'os':os} )
        return fileOSPath
    else:
        #return "File ID Missing"
        return False
        
def get_assets( jobID=None ) :
    'Builds a dictionary of all assets for a given job'
    return get( {'q': 'getAssets', 'ID': str(jobID)} )

def get_assetInfo( assetID=None ) :
    'Retrieves information for a given asset'
    assetInfo=get( {'q': 'getAssetInfo', 'ID': assetID} )
    return assetInfo

def get_jobInfo( jobID=None ) :
    'Builds a dictionary of job information including ID, number, jobname, and folder'
    return get( {'q': 'getJobInfo', 'ID': str(jobID)} )

def get_shows( jobID=None ) :
    'Builds a dictionary of all shows for a given job'
    return get( {'q': 'getShows', 'ID': str(jobID)} )

def get_showInfo( showID=None ) :
    'Builds a dictionary of all shows for a given show'
    return get( {'q': 'getShowInfo', 'ID': str(showID)} )

def get_shots( showID=None ) :
    'Builds a dictionary of all shots for a given show'
    return get( {'q': 'getShots', 'ID': showID} )

def get_shotInfo( shotID=None ) :
    'Retrieves information for a given shot'
    shotInfo=get( {'q': 'getShotInfo', 'ID': shotID} )
    return shotInfo

def get_shotIcon( shotID=None ) :
    'Retrieves information for a given shot'
    shotIcon=get( {'q': 'getShotIcon', 'ID': shotID} )
    return shotIcon

def get_assetIcon( assetID=None ) :
    'Retrieves information for a given asset'
    assetIcon=get( {'q': 'getAssetIcon', 'ID': assetID} )
    return assetIcon

def get_tasks(app='all', userType='artist') :
    'Retrieves the dictionary of available tasks from the API'
    #tasks=get( {'q': 'getTaskTypes', 'type': 'artist'} )
    tasks=get( {'q': 'getTaskTypes', 'app': app, 'type': userType} )
    return tasks

def get_taskInfo(itemClass='', itemID=0) :
    'Retrieves a dictionary of task information for a given asset or shot item from the API'
    if itemID==0:
        return False
    else:
        taskInfo=get( {'q': 'getTaskInfo', 'class': itemClass, 'itemID': itemID } )
        return taskInfo

def get_bases( shotID=None, assetID=None, showID=None, task='', taskID=None, pub=False ) :
    'Retrieves the dictionary of available basenames from the API'
    '''
    if shotID and not assetID :
        ID=shotID
        _type='SHOT'
    else :
        ID=assetID
        _type='ASSET'
    '''
    if shotID :
        ID=shotID
        _type='SHOT'
    elif assetID :
        ID=assetID
        _type='ASSET'
    else :
        ID=showID
        _type='SHOW'

    if not pub :
        if task and not taskID :
            basenameDict=get( {'q': 'getBasenames', 'ID': str(ID), 'class': _type, 'type': task.upper()} )
        elif not task and taskID :
            basenameDict=get( {'q': 'getBasenames', 'ID': str(ID), 'class': _type, 'task_type_ID': taskID} )
    elif pub :
        if task and not taskID :
            basenameDict=get( {'q': 'getBasenameAllPub', 'ID': str(ID), 'class': _type, 'type': task.upper()} )
        elif not task and taskID :
            basenameDict=get( {'q': 'getBasenameAllPub', 'ID': str(ID), 'class': _type, 'task_type_ID': taskID} )
    return basenameDict

def get_basesPub( shotID=None, assetID=None, basename='' ) :
    'Retrieves the dictionary of available basenames from the API'
    if shotID and not assetID :
        ID=shotID
        _type='SHOT'
    else :
        ID=assetID
        _type='ASSET'
    basenameDict=get( {'q': 'getBasenamePub', 'itemID': ID, 'class': _type, 'basename': basename} )
    return basenameDict

def get_basesAllPub( shotID=None, assetID=None, task='', taskID=None ) :
    'Retrieves the dictionary of all available published basenames from the API'
    if shotID and not assetID :
        ID=shotID
        _type='SHOT'
    else :
        ID=assetID
        _type='ASSET'
    if task and not taskID :
        basenameDict=get( {'q': 'getBasenameAllPub', 'itemID': ID, 'class': _type, 'type': task.upper()} )
    elif not task and taskID :
        basenameDict=get( {'q': 'getBasenameAllPub', 'itemID': ID, 'class': _type,
            'task_type_ID': taskID} )
    return basenameDict

def get_baseInfo( shotID=None, assetID=None, basename='' ) :
    'Retrieves information for a given basename'
    if shotID and not assetID :
        ID=shotID
        _type='SHOT'
    else :
        ID=assetID
        _type='ASSET'
    baseInfo=get( {'q': 'getBasenameVersion', 'itemID': ID, 'class': _type, 'basename': basename} )
    return baseInfo

def get_baseVer( shotID=None, assetID=None, showID=None, basename='' ) :
    'Retrieves the highest version number for a given basename'
    '''
    if shotID and not assetID :
        ID=shotID
        _type='SHOT'
    else :
        ID=assetID
        _type='ASSET'
    '''
    if shotID :
        ID=shotID
        _type='SHOT'
    elif assetID :
        ID=assetID
        _type='ASSET'
    else :
        ID=showID
        _type='SHOW'
    basenameDict=get( {'q': 'getBasenameVersion', 'class': _type, 'itemID': ID, \
        'basename': basename} )
    return basenameDict

def get_vers( shotID=None, assetID=None, showID=None, basename=None, pub=False ) :
    'Retrieves the dictionary of available versions from the API'
    '''
    if shotID and not assetID :
        ID=shotID
        _type='SHOT'
    else :
        ID=assetID
        _type='ASSET'
    '''
    if shotID :
        ID=shotID
        _type='SHOT'
    elif assetID :
        ID=assetID
        _type='ASSET'
    else :
        ID=showID
        _type='SHOW'
    if pub :
        versionDict=get( { 'q':'getVersions', 'itemID':ID, 'type':_type, 'basename': basename, 'pub': 1 } )
    else :
        versionDict=get( { 'q':'getVersions', 'itemID':ID, 'type':_type, 'basename': basename, 'pub': 0 } )
    
    return versionDict

def get_verInfo( verID=None ) :
    'Retrieves the information for a given version ID'
    verInfo=get( {'q': 'getVersionInfo', 'ID': verID} )
    return verInfo

def clear_pubFlags( shotID=None, assetID=None, showID=None, fileID=None, basename='' ) :
    'Run before publishing to clear previous basename published flags'
    P.info('Clearing Published Flags')
    if shotID :
        ID=shotID
        _type='SHOT'
    elif assetID :
        ID=assetID
        _type='ASSET'
    elif showID:
        ID=showID
        _type='SHOW'
    elif fileID:
        ID=fileID
        _type='FILE'
    else:
        P.error ('clear_pubFlags: Missing ID')
        return False

    pubFlags=get( {'q': 'clearPubFlags', 'class': _type, 'itemID': ID, 'basename': basename} )
    return pubFlags

def get_paths( item='', ID=None) :
    'Retrieves nim path for project structure - items options: job / show / shot / asset'
    if ID :
        path=get( {'q':'getPaths', 'type':item, 'ID':ID} )
        return path
    else:
        P.error ('get_paths: Missing ID')
        return False

def get_lastShotRender( shotID=None ):
    'Retrieves the last render added to the shot'
    lastRender=get( {'q': 'getLastShotRender', 'ID': shotID} )
    return lastRender

def get_elementTypes():
    'Retrieves a dictionary of global element types'
    elementTypes=get( {'q': 'getElementTypes'} )
    return elementTypes

def get_elementType( ID=None):
    'Retrieves a dictionary of global element types'
    elementType=get( {'q': 'getElementType', 'ID': ID} )
    return elementType

def get_elements( parent='shot', parentID=None, elementTypeID=None, getLastElement=False, isPublished=False):
    ''' Retrieves a dictionary of elements for a particular type given parentID.
        If no elementTypeID is given will return elements for all types.
        parent is the parent of the element.  acceptable values are shot, asset, task, render.
        getLastElement will return only the last published element.
        isPublished will return only the published elements.'''
    publishedElements=get( {'q': 'getElements', 'parent': parent, 'parentID': parentID, 'elementTypeID': elementTypeID, 'getLastElement': getLastElement, 'isPublished': isPublished} )
    return publishedElements

def add_element( parent='shot', parentID=None, typeID='', path='', name='', startFrame=None, endFrame=None, handles=None, isPublished=False ):
    result=get( {'q': 'addElement', 'parent': parent, 'typeID': typeID, 'parentID': parentID, 'path': path, 'name': name, 'startFrame': startFrame, 'endFrame': endFrame, 'handles': handles, 'isPublished': isPublished} )
    return result

#  Files :
#===------

def to_nimDir( nim=None ) :
    'Derives the Project Directory to use for the current Asset/Shot'
    nimDir, assetPath, shotPath, taskFolder='', '', '', ''
    shotPlates, shotRenders, shotComps='', '', ''
    short_task=F.task_toAbbrev( task=nim.name('task') )
    
    #  Error Check :
    if not nim :
        P.error('Please pass api.to_nimDir() a NIM dictionary.')
        return False
    
    #  Set File Directory from the API :
    if nim.tab()=='SHOT' :
        if nim.ID('shot') :
            
            #  Asset Information :
            shotInfo=Api.get( {'q': 'getPaths', 'type': 'shot', 'ID' : str(nim.ID('shot'))} )
            if shotInfo and type(shotInfo)==type(dict()) and 'root' in shotInfo :
                shotPath=os.path.normpath( os.path.join( nim.server(), shotInfo['root'] ) )
                shotPlates=os.path.normpath( os.path.join( nim.server(), shotInfo['plates'] ) )
                shotRenders=os.path.normpath( os.path.join( nim.server(), shotInfo['renders'] ) )
                shotComps=os.path.normpath( os.path.join( nim.server(), shotInfo['comps'] ) )
            #  Task Information :
            taskDict=Api.get( {'q': 'getTaskTypes', 'app': nim.app().upper()} )
            if taskDict and type(taskDict)==type(list()) :
                for task in taskDict :
                    if 'name' in task.keys() and nim.name('task')==task['name'] :
                        taskFolder=task['folder']
            if shotPath and taskFolder :
                nimDir=os.path.join( nim.server( get='path' ), shotPath, taskFolder )
            elif shotPath and not taskFolder :
                nimDir=os.path.join( nim.server( get='path' ), shotPath )
            else :
                nimDir=os.path.normpath( os.path.join( nim.server( get='path' ), nim.name('job'),
                    '_DEV', 'ASSETS', nim.name('asset'), short_task ) )
                if not os.path.exists( nimDir ) :
                    P.error('Could not get Shot Information!')
                    return False
                else :
                    return nimDir
        else :
            P.error('Could not get Shot ID!')
    elif nim.tab()=='ASSET' :
        if nim.ID('asset') :
            #  Asset Information :
            assetInfo=Api.get( {'q': 'getPaths', 'type': 'asset', 'ID' : str(nim.ID('asset'))} )
            if assetInfo and type(assetInfo)==type(dict()) and 'root' in assetInfo :
                assetPath=assetInfo['root']
            #  Task Information :
            taskDict=Api.get( {'q': 'getTaskTypes', 'app': nim.app().upper()} )
            if taskDict and type(taskDict)==type(list()) :
                for task in taskDict :
                    if 'name' in task.keys() and nim.name('task')==task['name'] :
                        taskFolder=task['folder']
            if assetPath and taskFolder :
                nimDir=os.path.join( nim.server( get='path' ), assetPath, taskFolder )
            elif assetPath and not taskFolder :
                nimDir=os.path.join( nim.server( get='path' ), assetPath )
            else :
                nimDir=os.path.join( nim.server( get='path' ), nim.name('job'), '_DEV', 'ASSETS', \
                    nim.name('asset'), short_task )
                if not os.path.exists( nimDir ) :
                    P.error('Could not get Asset Information!')
                    return False
        else : P.error('Could not get Asset ID!')
    
    #  Returns :
    if nimDir : return os.path.normpath( nimDir )
    else :
        P.error('Function api.to_nimDir() was unable to derive a file directory')
        return False

def to_basename( nim=None ) :
    'Derives the basenme to use, given a populated NIM dictionary'
    basename=''
    
    #  Error Check :
    if not nim :
        P.error( 'Please pass api.to_basename() a NIM dictionary.' )
        return False
    
    short_task=F.task_toAbbrev( task=nim.name('task') )
    
    #  Derive basename :
    if not nim.name('tag') and nim.name('base') :
        basename=nim.name('base')
    else :
        if nim.tab()=='ASSET' :
            if nim.name('tag') :
                basename=nim.name('asset')+'_'+short_task+'_'+nim.name('tag')
            else :
                basename=nim.name('asset')+'_'+short_task
        elif nim.tab()=='SHOT' :
            if nim.name('tag') :
                basename=nim.name('shot')+'_'+short_task+'_'+nim.name('tag')
            else :
                basename=nim.name('shot')+'_'+short_task
    
    #  Returns :
    if basename :
        return basename
    else :
        P.error('Function api.to_basename() was unable to derive a basename')
        return False

def to_fileName( nim=None, padding=2, pub=False ) :
    'Derives the file name to use, given a populated NIM dictionary'
    fileName=''
    
    #  Error Check :
    if not nim :
        P.error( 'Please pass api.to_fileName() a NIM dictionary.' )
        return False
    
    #  Get Directory :
    
    #  Get Basename :
    basename=to_basename( nim=nim )
    
    #  Get next Version Number :
    baseInfo=''
    if nim.tab()=='SHOT' :
        baseInfo=get_baseInfo( shotID=nim.ID( 'shot' ), basename=basename )
    elif nim.tab()=='ASSET' :
        baseInfo=get_baseInfo( assetID=nim.ID( 'asset' ), basename=basename )
    if baseInfo and 'version' in baseInfo[0].keys() :
        verNum=int(baseInfo[0]['version'])+1
    else :
        verNum=1
    
    #  Derive file name :
    if basename :
        if not pub :
            fileName=basename+'_v'+str(verNum).zfill(int(padding))+nim.name( 'fileExt' )
        elif pub :
            fileName=basename+'_v'+str(verNum).zfill(int(padding))+'_PUB'+nim.name( 'fileExt' )
    
    #  Returns :
    if fileName :
        return fileName
    else :
        P.error( 'Function api.to_fileName() was unable to derive a file name' )
        return False

def to_fileDir( nim=None ) :
    'Derives the file directory to use, given a populated NIM dictionary'
    fileDir=''
    
    #  Error Check :
    if not nim :
        P.error('Please pass api.to_fileDir() a NIM dictionary.')
        return False
    
    #  Set Basename and Project Directory from NIM :
    basename=to_basename( nim=nim )
    nimDir=to_nimDir( nim=nim )
    
    if nimDir :
        if basename :
            #  Derive File Directory from NIM :
            if nim.app()=='Maya' : fileDir=os.path.join( nimDir, basename, 'scenes' )
            elif nim.app()=='3dsMax' : fileDir=os.path.join( nimDir, basename, 'scenes' )
            else : fileDir=os.path.join( nimDir, basename )
            #  Return :
            if fileDir : return os.path.normpath( fileDir )
            else :
                P.error('Function api.to_fileDir() was unable to derive a file directory.')
                return False
        else :
            P.error('Function api.to_fileDir() was unable to derive a basename.')
            return False
    else :
        P.error('nim_api.to_fileDir() could not get the NIM directory.')
        return False

def to_filePath( nim=None, padding=2, pub=False ) :
    'Derives a file path, from a NIM dictionary'
    filePath=''
    
    #  Error Check :
    if not nim :
        P.error( 'Please pass nim.api.to_filePath() a NIM dictionary.' )
        return False
    
    #  Derive file path :
    fileDir=to_fileDir( nim=nim )
    fileName=to_fileName( nim=nim, padding=padding, pub=pub )
    filePath=os.path.join( fileDir, fileName )
    
    #  Returns :
    if filePath :
        return os.path.normpath( filePath )
    else :
        P.error( 'Function api.to_filePath() was unable to derive a file path' )
        return False

def to_renPath( nim=None ) :
    'Derives a render path, from a NIM dictionary'
    renPath=''
    #  Error Check :
    if not nim :
        P.error( 'Please pass nim_api.to_filePath a nim dictionary.' )
        return False
    #  Derive file path :
    try :
        if nim.tab()=='SHOT' :
            renPath=os.path.join( nim.server(), nim.name('job'), nim.name('show'), \
                'IMG', nim.name('shot'), 'RENDER' )
        elif nim.tab()=='ASSET' :
            renPath=os.path.join( nim.server(), nim.name('job'), '_DEV', 'IMG', \
                nim.name('asset'), 'RENDER' )
        return os.path.normpath( renPath )
    except :
        return False

def add_file( nim=None, filePath='', comment='', pub=False ) :
    'Adds a file to the NIM API'
    
    #  Get nim info from filepath :
    if filePath and not nim :
        nim=filePath2API( filePath=filePath )
    if not filePath and not nim :
        P.error( 'Unable to derive filepath/API information, sorry.' )
        Win.popup( title='NIM Error', msg='Unable to derive filepath, sorry.' )
        return False
    fileDir=os.path.normpath( os.path.dirname( filePath ) )+os.sep
    
    #  Get user information :
    usrID=nim.userInfo()['ID']
    if not usrID :
        P.error( 'Sorry, unable to retrieve user information.' )
        Win.popup( title='NIM Error', msg='Sorry, unable to retrieve user information.' )
        return False
    
    projPath=nim.name( 'server' )

    # When saving a version - nim.name('server') does not exist
    # Need to load from file info

    if not projPath :
        projPath = nim.server(get='path')
        #P.error( 'AS - projPath: %s' % projPath )

    # If info not found on server check prefs for a serverPath
    if not projPath :
        app=F.get_app()
        prefs=Prefs.read()
        ''' DEPREICATED - REMOVING DEFAULT SERVER PATH FROM PREFS
        if prefs and app+'_DefaultServerPath' in prefs.keys() :
            projPath=prefs[app+'_DefaultServerPath']
        '''
        # TODO: VERIFY AS REPLACE FOR _DefaultServerPath
        if prefs and app+'_ServerPath' in prefs.keys() :
            projPath=prefs[app+'_ServerPath']
            #P.error( 'AS - projPath: %s' % prefs[app+'_ServerPath'] )


    ver=F.get_ver( filePath )
    ext=F.get_ext( filePath )
    app=get_app()
    
    #  Get basename :
    fileBase=to_basename( nim=nim )
    
    #  Error check input :
    if not projPath or not app or not nim.name( 'task' ) or not fileBase or not ext or not ver :
        P.error( 'api.add_file function did not get the proper variables passed to it...  Exiting.' )
        return False
    if not nim.ID( 'asset' ) and not nim.ID( 'shot' ) :
        P.error( 'api.add_file function needs to be given either a shot, or asset, ID number...  Exiting.' )
        return False
    if not nim.name( 'comment' ) :
        nim.set_name( elem='comment', name=nim_tools.get_comment( app=app, num_requests=1 ) )
        if not nim.name( 'comment' ) :
            P.warning( '\nNo comment entered.  Tsk, tsk...\n' )
    
    #  Get Asset information :
    if nim.ID( 'asset' ) and nim.ID( 'asset' ) != 'None' :
        P.info('Retrieving Asset Information')
        assetInfo=get( {'q': 'getAssetInfo', 'ID': nim.ID( 'asset' )} )
        basenameInfo=get( {'q':'getBasenameVersion', 'class':'ASSET', \
            'itemID': nim.ID( 'asset' ), 'basename': nim.name( 'base' )} )
        #  Error check dictionaries :
        if not assetInfo or not basenameInfo or not len(assetInfo) or not len(basenameInfo) :
            P.warning( 'Problem retrieving Asset/Basename information from the database.' )
        if assetInfo[0]['jobFolder']=='NULL' :
            P.error( 'Selected Job is not online, sorry.' )
            return False
        #  Construct variables :
        jobName=assetInfo[0]['jobNumber']+'_'+assetInfo[0]['jobName']
        if assetInfo[0]['jobFolder'] :
            jobFolder=assetInfo[0]['jobNumber']+'_'+assetInfo[0]['jobFolder']
        else :
            jobFolder=assetInfo[0]['jobNumber']+'_'+assetInfo[0]['jobName']
        assetName=assetInfo[0]['assetName']
    
    #  Get Shot information :
    elif nim.ID( 'shot' ) and nim.ID( 'shot' ) != 'None' :
        P.info('Retrieving Shot Information')
        shotInfo=get( {'q': 'getShotInfo', 'ID':nim.ID( 'shot' )} )
        basenameInfo=get( {'q': 'getBasenameVersion', 'class': 'SHOT', \
            'itemID': nim.ID( 'shot' ), 'basename': nim.name('base')} )
        #  Error check dictionaries :
        if not shotInfo or not basenameInfo or not len(shotInfo) or not len(basenameInfo) :
            P.warning( '\nProblem retrieving Shot/Basename information from the database.' )
            P.warning( 'Shot Info = %s' % shotInfo )
            P.warning( 'Basename Info = %s' % basenameInfo )
        if shotInfo[0]['jobFolder']=='NULL' or shotInfo[0]['showFolder']=='NULL' :
            P.error( 'Specified Job/Show is not online, sorry.' )
            return False
        #  Construct variables :
        jobName=shotInfo[0]['jobNumber']+'_'+shotInfo[0]['jobName']
        if shotInfo[0]['jobFolder'] :
            jobFolder=shotInfo[0]['jobNumber']+'_'+shotInfo[0]['jobFolder']
        else :
            jobFolder=shotInfo[0]['jobNumber']+'_'+shotInfo[0]['jobName']
        showName=shotInfo[0]['showName']
        showFolder=shotInfo[0]['showFolder']
        shotName=shotInfo[0]['shotName']
    
    #  API call :
    if nim.tab()=='ASSET' :
        _task=F.task_toAbbrev( nim.name( 'task' ) )
        
        print 'Task Folder = %s' % nim.taskFolder()
        
        if not pub :
            result=get( {'q': 'addFile', 'class': 'ASSET', 'itemID': nim.ID( 'asset' ), 
                'task_type_ID': str(nim.ID('task')), 'task_type_folder': nim.taskFolder(),
                'userID': str(usrID), 'basename': fileBase, 'filename': os.path.basename(filePath),
                'filepath': fileDir, 'ext': ext, 'version': str(ver), 'note': nim.name( 'comment' ),
                'serverID': str(nim.server( get='ID' ))} )
        elif pub :
            clear_pubFlags( assetID=nim.ID( 'asset' ), basename=fileBase )
            result=get( {'q': 'addFile', 'class': 'ASSET', 'itemID': nim.ID( 'asset' ),
                'task_type_ID': str(nim.ID('task')), 'task_type_folder': nim.taskFolder(),
                'userID': str(usrID), 'basename': fileBase, 'filename': os.path.basename(filePath),
                'filepath': fileDir, 'ext': ext, 'version': str(ver), 'note': nim.name( 'comment' ),
                'serverID': str(nim.server( get='ID' )), 'isPub': 1, 'isWork': 0} )
    elif nim.tab()=='SHOT' :
        if not pub :
            result=get( {'q': 'addFile', 'class': 'SHOT', 'itemID': nim.ID( 'shot' ),
                'task_type_ID': str(nim.ID('task')), 'task_type_folder': nim.taskFolder(),
                'userID': str(usrID), 'basename': fileBase, 'filename': os.path.basename(filePath),
                'filepath': fileDir, 'ext': ext, 'version': str(ver), 'note': nim.name( 'comment' ),
                'serverID': str(nim.server( get='ID' ))} )
        elif pub :
            clear_pubFlags( shotID=nim.ID( 'shot' ), basename=fileBase )
            result=get( {'q': 'addFile', 'class': 'SHOT', 'itemID': nim.ID( 'shot' ),
                'task_type_ID': str(nim.ID('task')), 'task_type_folder': nim.taskFolder(),
                'userID': str(usrID), 'basename': fileBase, 'filename': os.path.basename(filePath),
                'filepath': fileDir, 'ext': ext, 'version': str(ver), 'note': nim.name( 'comment' ),
                'serverID': str(nim.server( get='ID' )), 'isPub': 1, 'isWork': 0} )
    if  not result :
        P.error( 'File saved, but there was a problem writing to the NIM database.' )
        P.error( '    Database has not been populated with your file.' )
        P.error( str(result) )
        return False
    else :
        P.info( 'NIM API updated with new file.' )
        P.info( '      File ID = %s' % result )
    
    return True

def versionUp( nim=None, padding=2, selected=False, win_launch=False, pub=False, symLink=True ) :
    'Function used to save/publish/version up files'
    user, job, asset, show, shot, basename, task='', '', '', '', '', '', ''
    userID, jobID, assetID, showID, shotID='', '', '', '', ''
    shotCheck, assetCheck=False, False
    
    #  If not passed a NIM dictionary, get values from the file name :
    if not nim :
        nim=Nim.NIM()
        #nim.ingest_filePath( pub=pub )
        if not nim.mode() :
            nim.set_mode('ver')
        #  Set Publish state :
        if pub : nim.set_name( elem='filter', name='Published' )
        else : nim.set_name( elem='filter', name='Work' )
    
    #  Print :
    action=''
    if nim.mode().lower() in ['pub', 'publish'] :
        action='Publishing'
    elif nim.mode().lower() in ['save', 'saveas'] :
        action='Saving'
    elif nim.mode().lower() in ['ver', 'verup', 'version', 'versionup'] :
        action='Versioning Up'
    P.info( '\n%s the current file...' % action )
    
    #  Get application variables, when Version'ing Up :
    if not win_launch :
        if nim.app()=='Maya' :
            import nim_maya as M
            M.get_vars( nim=nim )
        elif nim.app()=='Nuke' :
            import nim_nuke as N
            N.get_vars( nim=nim )
        elif nim.app()=='C4D' :
            import nim_c4d as C
            nim_plugin_ID=1032427
            C.get_vars( nim=nim, ID=nim_plugin_ID )
        elif nim.app()=='3dsMax' :
            import nim_3dsmax as Max
            Max.get_vars( nim=nim )
        elif nim.app()=='Houdini' :
            import nim_houdini as Houdini
            Houdini.get_vars( nim=nim )
    
    #  Error check :
    try :
        int(nim.ID('shot'))
        shotCheck=True
    except : pass
    try :
        int(nim.ID('asset'))
        assetCheck=True
    except : pass
    if not shotCheck and not assetCheck :
        msg='Sorry, unable to retrieve Shot/Asset IDs from the current file.'
        if not win_launch :
            msg +='\n  Please try saving from the NIM GUI'
        P.error( '\n'+msg )
        P.error( '    File Path = %s' % nim.filePath() )
        nim.Print()
        Win.popup( title=winTitle+' - Filename Error', msg=msg )
        return False
    
    #  Version Up File :
    #  [AS] returning nim object from verUp to update if loading exported file
    verUpResult=F.verUp( nim=nim, padding=padding, selected=selected, win_launch=win_launch, pub=pub, symLink=symLink )
    filePath = verUpResult['filepath']
    verUpNim = verUpResult['nim']
    P.info('Filepath: %s' % filePath)
    P.info('NIM Basename: %s \n' % verUpNim.name(elem='base'))
    #  [AS] END
    
    #  Add file to API :
    if filePath and os.path.isfile( filePath ) :
        result_addFile=add_file( nim=nim, filePath=filePath, comment=nim.name( 'comment' ), pub=pub )
        if result_addFile :
            action=''
            if nim.mode().lower() in ['pub', 'publish'] :
                action='Published'
            elif nim.mode().lower() in ['save', 'saveas'] :
                action='Saved'
            elif nim.mode().lower() in ['ver', 'verup', 'version', 'versionup'] :
                action='Versioned Up'
            P.info( 'File has been %s successfully.\n' % action )
            if not pub :
                if nim.mode().lower() in ['save', 'saveas'] :
                    Win.popup( title=winTitle+' - Versioned Up', msg='File has been Saved successfully.' )
                elif nim.mode().lower() in ['ver', 'verup', 'version', 'versionup'] :
                    Win.popup( title=winTitle+' - Versioned Up', msg='File has been Versioned Up successfully.' )
            else :
                #Win.popup( title=winTitle+' - Version\'ed Up', msg='File has been Published successfully.' )
                pass
            
            #  Publish Sym-Links :
            if pub and symLink :
                P.info( 'Initiating Sym-Link Publish...' )
                fileID, versInfo=None, None
                basename=to_basename( nim=nim )
                if nim.tab()=='SHOT' :
                    versInfo=get_vers( shotID=nim.ID( 'shot' ), basename=basename, pub=True )
                elif nim.tab()=='ASSET' :
                    versInfo=get_vers( assetID=nim.ID( 'asset' ), basename=basename, pub=True )
                for verInfo in versInfo :
                    temp_path=os.path.normpath( os.path.join( verInfo['filepath'], verInfo['filename'] ) )
                    if temp_path==filePath :
                        fileID=verInfo['fileID']
                        P.info( 'File ID = %s' % fileID )
                        P.info( 'Publishing Sym-Link...' )
                        #  Publish sym link, if necessary :
                        if fileID :
                            result=get( {'q': 'publishSymlink', 'fileID': str(fileID)} )
                            P.info( '    Sym-Link Published!' )
                            #Win.popup( title=winTitle+' - Publish', msg='Sym-Link Published!' )
                        else :
                            Win.popup( title=winTitle+' - Publish Error', msg='Problem publishing Sym-Link!!!' )
                            P.error( 'Sorry!  Problem retrieving File ID.' )
                        break
            
            #  Prompt to open exported file :
            if selected :
                result=Win.popup( title='NIM - Open Export?', type='okCancel', \
                    msg='Would you like to open your newly exported file?' )
                if result=='OK' :
                    #  Maya :
                    if nim.app()=='Maya' :
                        import maya.cmds as mc
                        try :
                            mc.file( filePath, force=True, open=True, ignoreVersion=True, prompt=False )
                            #  Set env vars brought over from nim_file
                            P.info('Setting Environment Variables')
                            P.info('NIM: %s \n' % verUpNim.name(elem='base'))
                            import nim_maya as M
                            M.set_vars( nim=verUpNim )
                            nim = verUpNim
                            
                        except Exception, e :
                            P.error( 'Failed reading the file: %s' % filePath )
                            P.error( '    %s' % traceback.print_exc() )
                            return False
                    #  Nuke :
                    elif nim.app()=='Nuke' :
                        import nuke
                        try :
                            #  Prompt to Save :
                            if nuke.root().modified() :
                                import nim_nuke as N
                                result=N.Win_SavePySide.get_btn()
                                if result.lower()=='save' :
                                    P.info('\nSaving file...\n')
                                    cur_filePath=F.get_filePath()
                                    nuke.scriptSaveAs( cur_filePath )
                                elif result.lower()=='verup' :
                                    P.info('\nVersioning file up...\n')
                                    try : versionUp()
                                    except :
                                        P.error('Problem running version up command.  Nothing done.')
                                        return False
                                elif result.lower()=='no' :
                                    P.info( '\nFile not saved before openning.\n' )
                                elif result.lower()=='cancel' :
                                    P.info('\nCancelling file operation.\n')
                                    return None
                            #  Clear the scene, load file and rename :
                            nuke.scriptClear()
                            nuke.scriptOpen( filePath )
                            PS=nuke.root()
                            knob=PS.knob('name')
                            knob.setValue( filePath.replace( '\\', '/' ) )
                            
                            #  Set env vars brought over from nim_file
                            P.info('Setting Environment Variables')
                            P.info('NIM: %s \n' % verUpNim.name(elem='base'))
                            import nim_nuke as N
                            N.set_vars( nim=verUpNim )
                            nim = verUpNim
                            
                        except Exception, e :
                            P.error( 'Failed reading the file: %s' % filePath )
                            P.error( '    %s' % traceback.print_exc() )
                            return False
                        try :
                            P.info( 'Setting Nuke environment variables...' )
                            import nim_nuke as N
                            N.set_vars( nim )
                        except :
                            P.warning( 'Unable to set Nuke environment variables.  Dealine may be affected' )
                            P.warning( '    %s' % traceback.print_exc() )
                            Win.popup( title='NIM - ENV VARS, not set', \
                                msg='Unable to set Nuke environment variables.  Dealine may be affected' )
                    #  Hiero :
                    elif nim.app()=='Hiero' :
                        import hiero.core
                        try : hiero.core.openProject( filePath )
                        except Exception, e :
                            P.error( 'Failed reading the file: %s' % filePath )
                            P.error( '    %s' % traceback.print_exc() )
                            return False
                    
                    elif nim.app()=='C4D' :
                        import c4d
                        P.info( 'Opening file...\n    %s' % filePath )
                        try:
                            c4d.documents.LoadFile( str(filePath) )
                            #  Set Variables :
                            nim_plugin_ID=1032427
                            import nim_c4d as C
                            C.set_vars( nim=verUpNim, ID=nim_plugin_ID )
                            nim = verUpNim
                            
                        except Exception, e :
                            P.error( 'Failed reading the file: %s' % filePath )
                            P.error( '    %s' % traceback.print_exc() )
                            return False
                    
                    elif nim.app()=='3dsMax' :
                        import MaxPlus
                        maxFM = MaxPlus.FileManager
                        try :
                            maxFM.Open(filePath)
                            #  Set env vars brought over from nim_file
                            P.info('Setting Environment Variables')
                            P.info('NIM: %s \n' % verUpNim.name(elem='base'))
                            import nim_3dsmax as Max
                            Max.set_vars( nim=verUpNim )
                            nim = verUpNim
                            
                        except Exception, e :
                            P.error( 'Failed reading the file: %s' % filePath )
                            P.error( '    %s' % traceback.print_exc() )
                            return False

                    elif nim.app()=='Houdini' :
                        import hou
                        try :
                            #TODO: check unsaved changed RuntimeError
                            #if hou.hipFile.hasUnsavedChanges():
                            #    raise RuntimeError
                            #hou.hipFile.load(file_name=str(filePath), suppress_save_prompt=True)
                            P.error('Loading File in nim_api')
                            filePath = filePath.replace('\\','/')
                            hou.hipFile.load(file_name=str(filePath))
                            #  Set env vars brought over from nim_file
                            P.info('Setting Environment Variables')
                            P.info('NIM: %s \n' % verUpNim.name(elem='base'))
                            import nim_houdini as Houdini
                            Houdini.set_vars( nim=verUpNim )
                            nim = verUpNim
                            
                        except Exception, e :
                            P.error( 'Failed reading the file: %s' % filePath )
                            P.error( '    %s' % traceback.print_exc() )
                            return False
            
            return filePath
    
    #  If not successful, fail :
    else :
        P.error( 'FAILED to Version Up the file.' )
        Win.popup( title=winTitle+' - Version Up Failure', \
            msg='FAILED to Version Up the file.' )
        return False

def save_file( parent='SHOW', parentID=0, task_type_ID=0, task_folder='', userID=0, basename='', filename='', path='', ext='', version='', comment='', serverID=0, pub=False, forceLink=1, work=True ):
    '''General Purpose Save File Function that Adds a File to the NIM Database with brute force data'''
    parent = parent.upper()

    if not pub :
        result=get( {'q': 'addFile', 'class': parent, 'itemID': str(parentID), 
            'task_type_ID': str(task_type_ID), 'task_type_folder': task_folder,
            'userID': str(userID), 'basename': basename, 'filename': filename,
            'filepath': path, 'ext': ext, 'version': str(version), 'note': comment,
            'serverID': str(serverID)} )
    elif pub :
        if parent == "SHOW":
            clear_pubFlags( showID=parentID, basename=basename )
        elif parent == 'SHOT':
            clear_pubFlags( shotID=parentID, basename=basename )
        elif parent == 'ASSET' :
            clear_pubFlags( assetID=parentID, basename=basename )
        else:
            P.error( 'A parent of proper type was not defined. Available options are SHOW, SHOT, & ASSET.' )
            return False

        is_work = 0
        if work:
            is_work = 1

        result=get( {'q': 'addFile', 'class': parent, 'itemID': str(parentID),
            'task_type_ID': str(task_type_ID), 'task_type_folder': task_folder,
            'userID': str(userID), 'basename': basename, 'filename': filename,
            'filepath': path, 'ext': ext, 'version': str(version), 'note': comment,
            'serverID': str(serverID), 'isPub': 1, 'isWork': is_work} )
        

    if  not result :
        P.error( 'There was a problem writing to the NIM database.' )
        P.error( '    Database has not been populated with your file.' )
        P.error( str(result) )
        return False
    else :
        P.info( 'NIM API updated with new file.' )
        P.info( '      File ID = %s' % result )

        if pub:
            ID = result
            #Create symlink for published files
            pub_result = publish_symLink(fileID=ID, forceLink=forceLink)
            P.error('pub_result: %s' % pub_result)
            if pub_result == True:
                P.info('...Success')
            else:
                P.error('There was a problem creating the symlink for the published file\n \
                        Please check to make sure the file exists on disk.')
    return result

def update_file( ID=0, task_type_ID=0, task_folder='', userID=0, basename='', filename='', path='', ext='', version='', comment='', serverID=0, pub=False, forceLink=1, work=True ):
    '''General Purpose Update File Function that Updates and existing File in the NIM Database'''
    is_work = 0
    if work:
        is_work = 1
    
    if not pub :
        result=get( {'q': 'updateFile', 'ID': str(ID),
                    'task_type_ID': str(task_type_ID), 'task_type_folder': task_folder,
                    'userID': str(userID), 'basename': basename, 'filename': filename,
                    'filepath': path, 'ext': ext, 'version': str(version), 'note': comment,
                    'serverID': str(serverID)} )
    elif pub :
        P.info('')
        clear_pubFlags( fileID=ID, basename=basename )

        is_work = 0
        if work:
            is_work = 1

        result=get( {'q': 'updateFile', 'ID': str(ID),
                    'task_type_ID': str(task_type_ID), 'task_type_folder': task_folder,
                    'userID': str(userID), 'basename': basename, 'filename': filename,
                    'filepath': path, 'ext': ext, 'version': str(version), 'note': comment,
                    'serverID': str(serverID), 'isPub': 1, 'isWork': is_work} )

    if  not result :
        P.error( 'There was a problem writing to the NIM database.' )
        P.error( '    Database has not been updated with your file.' )
        P.error( str(result) )
        return False
    else :
        P.info( 'NIM API updated existing file.' )
        P.info( '      File ID = %s' % result )
        if pub:
            #Create symlink for published files
            pub_result = publish_symLink(fileID=ID, forceLink=forceLink)
            if pub_result == 'true':
                P.info('...Success')
            else:
                P.error('There was a problem creating the symlink for the published file \
                        Please check to make sure the file exists on disk.')
    return result

def publish_symLink( fileID=None, elementID=None, forceLink=1 ) :
    '''Creates the symbolic link for a published file'''
    result = ''
    if fileID :
        P.info('Creating SymLink for Published File')
        result=get( {'q': 'publishSymlink', 'fileID': str(fileID), 'forceLink': str(forceLink) } )
    elif elementID :
        P.info('Creating SymLink for Published Element')
        result=get( {'q': 'publishSymlink', 'elementID': str(elementID), 'forceLink': str(forceLink) } )
    else :
        P.error( 'Sorry!  Problem retrieving Item ID.' )
        return False
    return result

#  Shots :
#===------
def can_bringOnline( item='shot', jobID=0, assetID=0, showID=0, shotID=0 ) :
    'Tests item against variable based project structure to see if it can be brought online'
    'Item types can be asset or shot'
    '   -if asset, jobID OR assetID must be passed'
    '   -if shot, showID or shotID must be passed'

    params = {}
    params["q"] = 'canBringOnline'
    params["type"] = str(item)
    if jobID > 0 :
        params["jobID"] = str(jobID)
    if assetID > 0 :
        params["assetID"] = str(assetID)
    if showID > 0 :
        params["showID"] = str(showID)
    if shotID > 0 :
        params["shotID"] = str(shotID)
    result = connect( method='get', params=params )
    return result

def bring_online( item='shot', assetID=0, shotID=0 ) :
    'Brings assets and shots online creating folders from project structure'
    'Item types can be asset or shot'
    '   -if asset, assetID must be passed'
    '   -if shot, shotID must be passed'

    params = {}
    params["q"] = 'bringOnline'
    params["type"] = str(item)
    if assetID > 0 :
        params["assetID"] = str(assetID)
    if shotID > 0 :
        params["shotID"] = str(shotID)
    result = connect( method='get', params=params )
    return result

def add_shot( showID=None, shotName=None, shotDuration=None ) :
    'Adds a shot to a show and returns the new ID'
    return get( {'q': 'addShot', 'showID': str(showID), 'name': str(shotName), 'duration': str(shotDuration) } )

def update_shot( shotID=None, duration=None) :
    'Update current shot information'
    return get( {'q': 'updateShot', 'shotID': str(shotID), 'duration': str(duration) } )

def upload_shotIcon( shotID=None, img=None ) :
    'Upload shot icon'
    params = {}
    action = "uploadShotIcon"
    shot_str = str(shotID)

    params["q"] = action.encode('ascii')
    params["shotID"] = shot_str.encode('ascii')
    params["file"] = open(img,'rb')

    result = upload(params=params)
    return result

def upload_assetIcon( assetID=None, img=None ) :
    'Upload asset icon'
    params = {}
    action = "uploadAssetIcon"
    asset_str = str(assetID)

    params["q"] = action.encode('ascii')
    params["assetID"] = asset_str.encode('ascii')
    params["file"] = open(img,'rb')

    result = upload(params=params)
    return result

def add_render( jobID=0, itemType='shot', taskID=0, fileID=0, \
    renderKey='', renderName='', renderType='', renderComment='', \
    outputDirs=None, outputFiles=None, elementTypeID=0, start_datetime=None, end_datetime=None, \
    avgTime='', totalTime='', frame=0 ) :
    'Add a render to a task'

    params = {'q': 'addRender', 'jobID': str(jobID), 'class': str(itemType), 'taskID': str(taskID), 'fileID': str(fileID), \
                'renderKey':str(renderKey), 'renderName':str(renderName), 'renderType':str(renderType), 'renderComment':str(renderComment), \
                'outputDirs':str(outputDirs), 'outputFiles':str(outputFiles), 'elementTypeID':str(elementTypeID), \
                'start_datetime':str(start_datetime), 'end_datetime':str(end_datetime), \
                'avgTime':str(avgTime), 'totalTime':str(totalTime), 'frame':str(frame) }
    result = connect( method='get', params=params )
    return result

def upload_renderIcon( renderID=None, renderKey='', img=None ) :
    'Upload Render Icon'
    #  2 required fields:
    #      renderID or renderKey
    #      img

    params = {}
    params["q"] = "uploadRenderIcon"
    params["renderID"] = renderID
    params["renderKey"] = renderKey
    if img is not None:
        params["file"] = open(img,'rb')
    else :
        params["file"] = ''

    result = upload(params=params)
    return result

def get_taskDailies( taskID=None) :
    'Retrieves the dictionary of dailies for the specified taskID from the API'
    #tasks=get( {'q': 'getTaskTypes', 'type': 'artist'} )
    dailies=get( {'q': 'getTaskDailies', 'taskID': taskID} )
    return dailies

def upload_dailies( taskID=None, renderID=None, renderKey='', path=None ) :
    'Upload Dailies - 2 required fields: (taskID, renderID, or renderKey) and path to movie'
    params = {}

    params["q"] = "uploadMovie"
    params["taskID"] = taskID
    params["renderID"] = renderID
    params["renderKey"] = renderKey
    if path is not None:
        path = os.path.normpath( path )
        params["file"] = open(path,'rb')
    else :
        params["file"] = ''

    result = upload(params=params)
    return result

def upload_dailiesNote( dailiesID=None, name='', img=None, note='', frame=0, time=-1, userID=None, nimURL=None ) :
    'Upload dailiesNote'
    params = {}
    action = "uploadDailiesNote"
    shot_str = str(dailiesID)
    name = str(name)

    params["q"] = action.encode('ascii')
    params["dailiesID"] = shot_str.encode('ascii')
    params["name"] = name.encode('ascii')
    if img is not None:
        params["file"] = open(img,'rb')
    else :
        params["file"] = ''
    params["note"] = note.encode('ascii')
    params["frame"] = frame
    params["time"] = time
    params["userID"] = userID

    result = upload(params=params)
    return result

#  End

