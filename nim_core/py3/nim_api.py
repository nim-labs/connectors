#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_api.py
# Version:  v7.1.0.250206
#
# Copyright (c) 2014-2025 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


# EXAMPLE:
#   Adding a render to a task
#   uploading an icon to the render
#   uploading review items to a render
#   adding elements to a render
#
# import nim_core.nim_api as nimAPI
# result = nimAPI.add_render(taskID=14941, renderName='myRender')
# if result['success'] == True:
#    nimAPI.upload_renderIcon(renderID=result['ID'],img='/path/to/icon.jpeg')
#    nimAPI.upload_reviewItem(renderID=result['ID'],path='/path/to/movie/myImages.mov',submit=0)
#    nimAPI.add_element( parent='render', parentID=result['ID'], path='/path/to/frames', name='myImage.####.exr', \
#                           startFrame=1, endFrame=128, handles=12, isPublished=False )
#    nimAPI.add_element( parent='render', parentID=result['ID'], path='/path/to/frames', name='myImage_matte.####.exr', \
#                           startFrame=1, endFrame=128, handles=12, isPublished=False )
#



#  General Imports :
import json, os, re, sys, traceback
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse

try :
    import ssl
except :
    print("NIM API: Failed to load SSL")
    pass

import mimetypes
import email.generator as email_gen
from email.generator import _make_boundary as choose_boundary
import io
import stat

#  NIM Imports :
from . import nim as Nim
from . import nim_api as Api
from . import nim_file as F
from . import nim_prefs as Prefs
from . import nim_print as P
from . import nim_tools
from . import nim_win as Win
from . import nim_version as V

#  Variables :
version=V.version
winTitle='NIM '+version


isGUI = False
try :
    #Validate Against DCC Environment
    if F.get_app() is not None :
        isGUI = True
except :
    pass



def testAPI(nimURL=None, nim_apiUser='', nim_apiKey='') :
    sqlCmd={'q': 'testAPI'}
    cmd=urllib.parse.urlencode(sqlCmd)
    _actionURL="".join(( nimURL, cmd ))
    request = urllib.request.Request(_actionURL)
    try :
        request.add_header("X-NIM-API-USER", nim_apiUser)
        request.add_header("X-NIM-API-KEY", nim_apiKey)
        request.add_header("Content-type", "application/x-www-form-urlencoded; charset=UTF-8")
        try :
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname=False
            ssl_ctx.verify_mode=ssl.CERT_NONE
            _file = urllib.request.urlopen(request,context=ssl_ctx)
        except :
            _file = urllib.request.urlopen(request)
        fr=_file.read()
        try : result=json.loads( fr )
        except Exception as e :
            P.error( traceback.print_exc() )
        _file.close()
        return result
    except urllib.error.URLError as e :
        P.error( '\nFailed to read NIM API' )
        P.error( '   %s' % _actionURL )
        url_error = e.reason
        P.error('URL ERROR: %s' % url_error)
        err_msg = 'NIM Connection Error:\n\n %s' %  url_error;
        Win.popup(msg=err_msg)
        P.debug( '    %s' % traceback.print_exc() )
        return False


# Get NIM Connection Information
def get_connect_info() :
    'Returns the connection information from preferences'

    isGUI = False
    try :
        #Validate Against DCC Environment
        if F.get_app() is not None :
            isGUI = True
    except :
        pass

    _prefs=Prefs.read()

    if _prefs and 'NIM_URL' in list(_prefs.keys()) :
        nim_apiURL=_prefs['NIM_URL']
    else :
        print('"NIM_URL" not found in preferences!')
        err_msg ='Would you like to recreate your preferences?'
        if isGUI :
            reply=Win.popup( title='NIM Error', msg=err_msg, type='okCancel' )
        else :
            reply=input( 'Would you like to recreate your preferences? (Y/N): ')
            if reply == 'Y' or reply == 'y' :
                reply = 'OK'
                
        #  Re-create preferences, if prompted :
        if reply=='OK' :
            prefsFile=Prefs.get_path()
            if os.path.exists( prefsFile ) :
                os.remove( prefsFile )
            result = Prefs.mk_default()

            # Test Prefs 2nd Time... if fail after recreate then prompt for manual intervention
            _prefs=Prefs.read()
            if _prefs and 'NIM_URL' in list(_prefs.keys()) :
                nim_apiURL=_prefs['NIM_URL']
            else :
                print('Failed Recreating NIM preferences.\nPlease delete the .nim folder from your home directory and try again.')
                return False
        else :
            sys.exit( '"NIM_URL" not found in preferences! \nPlease create NIM Preferences before using the NIM API' )
            return False

    if _prefs and 'NIM_User' in list(_prefs.keys()) :
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
        except Exception as e :
            P.error( 'Unable to read api key.' )
    else :
        # P.warning( 'API Key not found.' )
        pass
    return key


#  DEPRECATED in 2.5 in favor of connect()
def get( sqlCmd=None, debug=True, nimURL=None ) :
    result=False
    result = connect( method='get', params=sqlCmd, nimURL=nimURL )
    return result


#  DEPRECATED in 2.5 in favor of connect()
def post( sqlCmd=None, debug=True, nimURL=None ) :
    result=False
    result = connect( method='post', params=sqlCmd, nimURL=nimURL )
    return result


#  API Query command
#       method options: get or post
#       params['q'] is required to define the HTML API query
#           Example:
#           params = {}
#           params['q'] = 'getShots'
#           params['showID'] = '100'
#       nimURL optional (not passing the nimURL will trigger a prefs read)
#       apiUser optional (required if passing nimURL and Require API Keys is enabled)
#       apiKey optional (required if passing nimURL and Require API Keys is enabled)
#
def connect( method='get', params=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Query URL with params and returns decoded json array'
    result=None
    
    isGUI = False
    try :
        #Validate Against DCC Environment
        if F.get_app() is not None :
            isGUI = True
    except :
        pass

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
    
    if apiUser :
        nim_apiUser = apiUser
    if apiKey :
        nim_apiKey = apiKey

    if params :
        if method == 'get':
            cmd=urllib.parse.urlencode(params)
            _actionURL="".join(( nimURL, cmd ))
        elif method == 'post':
            cmd=urllib.parse.urlencode(params)
            _actionURL = re.sub('[?]', '', nimURL)
        else :
            if isGUI :
                Win.popup( title='NIM Connection Error', msg='NIM Connection Error:\n\n Connection method not defined in request.')
            else :
                P.error('Connection method not defined in request.')
            
            return False

        try :
            if method == 'get':
                request = urllib.request.Request(_actionURL)
            elif method == 'post':
                request = urllib.request.Request(_actionURL, cmd)
            
            request.add_header("X-NIM-API-USER", nim_apiUser)
            request.add_header("X-NIM-API-KEY", nim_apiKey)
            request.add_header("Content-type", "application/x-www-form-urlencoded; charset=UTF-8")
            try :
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname=False
                ssl_ctx.verify_mode=ssl.CERT_NONE
                _file = urllib.request.urlopen(request,context=ssl_ctx)
            except :
                _file = urllib.request.urlopen(request)

            fr=_file.read()
            try : result=json.loads( fr )
            except Exception as e :
                P.error( traceback.print_exc() )
            _file.close()

            # Test for failed API Validation
            if type(result)==type(list()) and len(result)==1 :
                try :
                    error_msg = result[0]['error']
                    if error_msg != '':
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
                        if isGUI :
                            Win.popup( title='NIM API Error', msg='NIM API Key Expired.\n\nNIM Security is set to require the use of API Keys. \
                                                                    Please contact your NIM Administrator to update your NIM API KEY expiration.' )
                        else :
                            print('NIM API Key Expired.\nNIM Security is set to require the use of API Keys.\n \
                                    Please contact your NIM Administrator to update your NIM API KEY expiration.')
                        #return False <-- returning false loads reset prefs msgbox
                except :
                    pass
            
            return result

        except urllib.error.URLError as e :
            P.error( '\nFailed to read URL for the following command...\n    %s' % params )
            P.error( '   %s' % _actionURL )
            url_error = e.reason
            P.error('URL ERROR: %s' % url_error)
            err_msg = 'NIM Connection Error:\n\n %s' %  url_error;
            #P.debug( '    %s' % traceback.print_exc() )

            err_msg +='\n\n'+\
                'Would you like to recreate your preferences?'
            #P.error( err_msg )
            if isGUI :
                reply=Win.popup( title='NIM Error', msg=err_msg, type='okCancel' )
            else :
                reply=input( 'Would you like to recreate your preferences? (Y/N): ')
                if reply == 'Y' or reply == 'y' :
                    reply = 'OK'

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


#  API Upload command
#       Used with all commands HTML API commands that require a file to be uploaded
#           uploadShotIcon
#           uploadAssetIcon
#           uploadRenderIcon
#           uploadDailies
#           uploadDailiesNote
#
#       params['q'] is required to define the HTML API query
#       To upload a file params['file'] must be passed a file using open(myFile,'rb')
#            Example:
#            params = {}
#            params['q'] = 'uploadDailiesNote'
#            params['dailiesID'] = '100'
#            params['name'] = 'note name'
#            params['file'] = open(imageFile,'rb')
#       nimURL optional (not passing the nimURL will trigger a prefs read)
#       apiUser optional (required if passing nimURL and Require API Keys is enabled)
#       apiKey optional (required if passing nimURL and Require API Keys is enabled)
#
def upload( params=None, nimURL=None, apiUser=None, apiKey=None ) :

    isGUI = False
    try :
        #Validate Against DCC Environment
        if F.get_app() is not None :
            isGUI = True
    except :
        pass
    
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
    
    if apiUser :
        nim_apiUser = apiUser
    if apiKey :
        nim_apiKey = apiKey

    _actionURL = nimURL

    P.info("API URL: %s" % _actionURL)
    
    # Test for SSL Redirection
    isRedirected = False
    try:
        testCmd = {'q': 'testAPI'}
        cmd=urllib.parse.urlencode(testCmd)
        testURL="".join(( nimURL, cmd ))
        req = urllib.request.Request(testURL)

        try :
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname=False
            ssl_ctx.verify_mode=ssl.CERT_NONE
            res = urllib.request.urlopen(req, context=ssl_ctx)
        except :
            res = urllib.request.urlopen(req)
            #pass
        
        finalurl = res.geturl()
        #P.info("Request URL: %s" % finalurl)
        if nimURL.startswith('http:') and finalurl.startswith('https'):
            isRedirected = True
            _actionURL = _actionURL.replace("http:","https:")
            P.info("Redirect: %s" % _actionURL)
    except:
        P.error("Failed to test for redirect.")

    # Create opener with extended form post support
    try:
        try :
            P.info( "Opening Connection on HTTPS" )
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname=False
            ssl_ctx.verify_mode=ssl.CERT_NONE
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx), FormPostHandler)
        except :
            P.info( "Opening Connection on HTTP" )
            opener = urllib.request.build_opener(FormPostHandler)

        opener.addheaders = [('X-NIM-API-USER', nim_apiUser),('X-NIM-API-KEY', nim_apiKey)]
    except:
        P.error( "Failed building url opener")
        P.error( traceback.format_exc() )
        return False


    try:
        resource = opener.open(_actionURL, params)
        result =  resource.read().decode(resource.headers.get_content_charset())
        result = json.loads(result)

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
                    if isGUI :
                        Win.popup( title='NIM API Error', msg='NIM API Key Expired.\n\nNIM Security is set to require the use of API Keys. \
                                                            Please contact your NIM Administrator to update your NIM API KEY expiration.' )
                    else :
                        print('NIM API Key Expired.\nNIM Security is set to require the use of API Keys.\n \
                                Please contact your NIM Administrator to update your NIM API KEY expiration.')
                    #return False <-- returning false loads reset prefs msgbox
            except :
                pass

    except urllib.error.HTTPError as e:
        if e.code == 500:
            P.error("Server encountered an internal error. \n%s\n(%s)\n%s\n\n" % (_actionURL, params, e))
            return False
        else:
            P.error("Unanticipated error occurred uploading image: %s" % (e))
            return False

    return result

class FormPostHandler(urllib.request.BaseHandler):
    # needs to run first
    handler_order = urllib.request.HTTPHandler.handler_order - 10

    def http_request(self, request):
        try:
            data = request.get_data()
        except AttributeError:
            data = request.data
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                for(key, value) in list(data.items()):
                    if hasattr(value, 'read'):
                        v_files.append((key, value))
                    else:
                        v_vars.append((key, value))
            except TypeError:
                raise TypeError
            if len(v_files) == 0:
                data = urllib.parse.urlencode(v_vars, True)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                #if (
                #    request.has_header('Content-Type') and
                #    request.get_header('Content-Type').find(
                #        'multipart/form-data') != 0
                #):
                #    six.print_(
                #        "Replacing %s with %s" % (
                #            request.get_header('content-type'),
                #            'multipart/form-data'
                #        )
                #    )
                request.add_unredirected_header('Content-Type', contenttype)
            try:
                request.add_data(data)
            except AttributeError:
                request.data = data

        return request

    def multipart_encode(self, v_vars, files, boundary=None, buf=None):

        if boundary is None:
            boundary = choose_boundary()
        if buf is None:
            buf = io.BytesIO()
        for(key, value) in v_vars:
            buf.write(b'--' + boundary.encode("utf-8") + b'\r\n')
            buf.write(
                b'Content-Disposition: form-data; name="' +
                key.encode("utf-8") +
                b'"'
            )
            buf.write(b'\r\n\r\n' + str(value).encode("utf-8") + b'\r\n')
        for(key, fd) in files:
            try:
                filename = fd.name.split('/')[-1]
            except AttributeError:
                # Spoof a file name if the object doesn't have one.
                # This is designed to catch when the user submits
                # a StringIO object
                filename = 'temp.pdf'
            contenttype = mimetypes.guess_type(filename)[0] or b'application/octet-stream'
            try:
                contenttype = contenttype.encode("utf-8")
            except (UnicodeEncodeError, AttributeError):
                pass
            buf.write(b'--' + boundary.encode("utf-8") + b'\r\n')
            buf.write(
                b'Content-Disposition: form-data; ' +
                b'name="' + key.encode("utf-8") + b'"; ' +
                b'filename="' + filename.encode("utf-8") + b'"\r\n'
            )
            buf.write(
                b'Content-Type: ' +
                contenttype +
                b'\r\n'
            )
            fd.seek(0)
            buf.write(
                b'\r\n' + fd.read() + b'\r\n'
            )
        buf.write(b'--')
        buf.write(boundary.encode("utf-8"))
        buf.write(b'--\r\n\r\n')
        buf = buf.getvalue()
        return boundary, buf

    https_request = http_request


#  API Functions  #

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
        # import MaxPlus
        import pymxs
        return '3dsMax'
    except : pass
    try :
        import hou
        return 'Houdini'
    except : pass
    try:
        import cinesync
        return 'Cinesync'
    except : pass
    try :
        nim_app = os.environ.get('NIM_APP', '-1')
        if nim_app == 'Flame':
            return 'Flame'
    except: pass
    return None

def get_cultureCodes(nimURL=None, apiUser=None, apiKey=None) :
    '''
    Returns a dictionary of active culture codes

    Return:
      Returns an associative array in the format
      result->success        True/False
      result->error          Includes any error or security messaging    
      result->rows           An array of returned data
      result->totalRows      The total count of returned rows in the array
    
    '''
    params = {'q': 'getCultureCodes'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Users  #

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

def get_userID( user='', nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the current user\'s user ID'
    if not user :
        user=get_user()
    try :
        params = {'q': 'getUserID', 'u': str(user)}
        userID = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
        if type(userID)==type(list()) and len(userID)==1 :
            return userID[0]['ID']
        else :
            return userID
    except Exception as e :
        print((traceback.print_exc()))
        return False

def get_userList( nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of NIM Users from the NIM Preferences.'
    usrList=False
    params = {'q': 'getUsers'}
    usrList = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return usrList

def get_userInfo( ID=None, username=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves information for a given user by userID or username'
    params = {}
    params["q"] = "getUserInfo"
    if ID is not None : params['ID'] = ID
    if username is not None : params['username'] = username
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

#  Locations  #

def get_locations( nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Get all defined locations
    
    Parameters
    	None
    
    Return:
    	Returns a list of locations in the format:
            ID
            name
            description
    '''
    result=False
    params = {'q': 'getLocations'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Contacts  #

def get_contacts( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Get Contacts based on search parameters
    
    Parameters
        Parameters need to be passed as keyword arguments
        Example:
            get_contacts( first_name='John', last_name='Doe' )

        Required:
            none 									    Will return all contacts the requesting user has access to 
    
        Optional:
            ID 					integer 				The ID of a contact item to query
            first_name 		 	string 		 			Will return all contact items matching the first name
            last_name 			string					Will return all contact items matching the last name
            email 				string 					Will return all contact items matching the email
            title 				string 					Will return all contact items matching the title
            company 			string 					Will return all contact items matching the company name
            website 			string 					Will return all contact items matching the website
            work_phone 			string 					Will return all contact items matching the work phone number
            work_fax 			string 					Will return all contact items matching the work fax number
            mobile_phone 		string 					Will return all contact items matching the mobile phone number
            home_phone 			string 					Will return all contact items matching the home phone number
            address1 			string 					Will return all contact items matching the address1 field
            address2 			string 					Will return all contact items matching the address2 field
            city 				string 					Will return all contact items matching the city
            state 				string 					Will return all contact items matching the state
            zip 				string 					Will return all contact items matching the zip
            description 		string 					Will return all contact items partially matching the description
            keywords 			string 					A comma separated list of keywords
                                                        Will return all contact items matching the keywords
            groups 				string 					A comma separated list of groups
                                                        Will return all contact items matching the groups
            customKeys 	        dictionary 				A dictionary of custom field names and values
                                                        Will return all contact items matching the custom field value
            limit  				integer					Specifies the maximum number of rows to return
                                                        Default 0 (no limit)
            offset 				integer					Specifies the number of rows to skip before starting to return rows.
                                                        Default 0
    Return:
        Returns a dictionary in the format
        result->success 		True/False
        result->error 			Includes any error or security messaging
        result->total_count	    The total number of rows that match the search criteria
        result->data 			An array of returned data
    '''

    params = {'q': 'getContacts'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_contact( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Add Contact
    
    Parameters
        Parameters need to be passed as keyword arguments
        Example:
            get_contacts( first_name='John', last_name='Doe' )

    	Required:
    		none
    
    	Optional:
    		is_company			bool					0/1
    		first_name 		 	string 		 			The first name of the contact	
    		last_name 		 	string 		 			The last name of the contact		
    		email 		 		string 		 			The email of the contact		
    		title 		 		string 		 			The title of the contact		
    		company 		 	string 		 			The company name for the contact		
    		website 		 	string 		 			The website of the contact		
    		work_phone 		 	string 		 			The work phone number of the contact		
    		work_fax 		 	string 		 			The fax number of the contact		
    		mobile_phone 		string 		 			The mobile phone number of the contact		
    		home_phone 		 	string 		 			The home phone number of the contact		
    		address1 		 	string 		 			The first address line of the contact		
    		address2 		 	string 		 			The second address line of the contact		
    		city 		 		string 		 			The city for the contact		
    		state 		 		string 		 			The state for the contact		
    		zip 		 		string 		 			The zip code for the contact		
    		description 		string 		 			The description for the contact		
    		keywords 			string 					Format ["keyword1","keyword2"]
    		groups 				string 					Format ["group1","group2"]
    		contact_link_IDs 	string 					Format 1,2,3 - a comma separated list of contact IDs
    													Will replace all linked contacts for this contact
            customKeys          dictionary              A dictionary of custom field names and values
                                                        {"My Custom Key Name":"Some text"}

    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging	
    	result->ID 			    The ID of the newly created item
    '''

    params = {'q': 'addContact'}
    params.update(kwargs)

    if 'keywords' in params :
        params['keywords'] = json.dumps(params['keywords'])
    
    if 'groups' in params :
        params['groups'] = json.dumps(params['groups'])

    if 'customKeys' in params :
        params['customKeys'] = json.dumps(params['customKeys'])

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_contact( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Update A Contact
    
    Parameters
        Parameters need to be passed as keyword arguments
        Example:
            update_contact( ID=1, first_name='John', last_name='Doe' )

    	Required:
    		ID 					integer					The ID of the contact to update
    
    	Optional: 										(If an optional field is not passed, the value for that field will remain unchanged)
    		first_name 		 	string 		 			The first name of the contact	
    		last_name 		 	string 		 			The last name of the contact		
    		email 		 		string 		 			The email of the contact		
    		title 		 		string 		 			The title of the contact		
    		company 		 	string 		 			The company name for the contact		
    		website 		 	string 		 			The website of the contact		
    		work_phone 		 	string 		 			The work phone number of the contact		
    		work_fax 		 	string 		 			The fax number of the contact		
    		mobile_phone 		string 		 			The mobile phone number of the contact		
    		home_phone 		 	string 		 			The home phone number of the contact		
    		address1 		 	string 		 			The first address line of the contact		
    		address2 		 	string 		 			The second address line of the contact		
    		city 		 		string 		 			The city for the contact		
    		state 		 		string 		 			The state for the contact		
    		zip 		 		string 		 			The zip code for the contact		
    		description 		string 		 			The description for the contact		
    		keywords 			string 					Format ["keyword1","keyword2"]
    		groups 				string 					Format ["group1","group2"]
    		contact_link_IDs 	string 					Format 1,2,3 - a comma separated list of contact IDs
    													Will replace all linked contacts for this contact
    		customKeys          dictionary              A dictionary of custom field names and values
                                                        {"My Custom Key Name":"Some text"}
    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''

    params = {'q': 'updateContact'}
    params.update(kwargs)

    if 'keywords' in params :
        params['keywords'] = json.dumps(params['keywords'])
    
    if 'groups' in params :
        params['groups'] = json.dumps(params['groups'])

    if 'customKeys' in params :
        params['customKeys'] = json.dumps(params['customKeys'])

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_contact( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Delete Contact
    
    Parameters
    	Required:
    		ID 					integer         The ID of the contact to delete
    
    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''

    params = {'q': 'deleteContact'}
    if ID is not None : params['ID'] = ID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Schedule Events  #

def get_scheduleEvents( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Get Schedule Events based on search parameters
    
    Parameters
        Parameters need to be passed as keyword arguments
        Example:
            get_scheduleEvents( statusName='BOOKED', userIDs=1 )
    
        Required:
            none 										Will return all schedule events the requesting user has access to 
    
        Optional:
            ID 							integer 		The ID of a schedule event to query
            title 						string 			Will return all schedule events matching the title
            description 				string 			Will return all schedule events partially matching the description
            statusName 					string 			Will return all schedule events matching the statusName
            locationName 				string 			Will return all schedule events matching the locationName
            jobName 					string 			Will return all schedule events matching the jobName
            jobNumber 					string 			Will return all schedule events matching the jobNumber
            userIDs 					string 			Will return all schedule events matching the userIDs (comma separated list of IDs)
            users 						string 			Will return all schedule events matching the users (comma separated list of names)
            resourceIDs 				string 			Will return all schedule events matching the resourceIDs (comma separated list of IDs)
            resources 					string 			Will return all schedule events matching the resources (comma separated list of names)
            start 						datetime 		Will return all schedule events matching the start 
                                                        (yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
            end 						datetime 		Will return all schedule events matching the end 
                                                        (yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
            startRange 					datetime 		Will return all schedule events (and event recurrences) AFTER the startRange 
                                                        (yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
            endRange 					datetime 		Will return all schedule events (and event recurrences) BEFORE the endRange
                                                        (yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
            startTimezone 				string 			Will return all schedule events matching the startTimezone
            endTimezone 				string 			Will return all schedule events matching the endTimezone
            isAllDay 					bool 			Will return all schedule events matching the isAllDay (0/1)
            recurrenceId 				integer 		Will return all schedule events matching the recurrenceId
            recurrenceRule 				string 			Will return all schedule events matching the recurrenceRule
            recurrenceException 		string 			Will return all schedule events matching the recurrenceException
            userUtilizationTypeID 		integer 		Will return all schedule events matching the userUtilizationTypeID
            userUtilizationType 		string 			Will return all schedule events matching the userUtilizationType
            userUtilizationValue 		string 			Will return all schedule events matching the userUtilizationValue
            resourceUtilizationTypeID 	integer 		Will return all schedule events matching the resourceUtilizationTypeID
            resourceUtilizationType 	string 			Will return all schedule events matching the resourceUtilizationType
            resourceUtilizationValue 	string 			Will return all schedule events matching the resourceUtilizationValue

            limit  						integer			Specifies the maximum number of rows to return
                                                        Default 0 (no limit)
            offset 						integer			Specifies the number of rows to skip before starting to return rows.
                                                        Default 0
    
    
    Return:
    		Returns an associative array in the format
    		$result->success 		True/False
    		$result->error 			Includes any error or security messaging
            $result->total_count	The total number of rows that match the search criteria
     		$result->data 			An array of returned data
    			
    Notes:
    	yyyy: 4-digit year (2024)
    	mm: 2-digit month (07 for July)
    	dd: 2-digit day of the month (10)
    	T: A delimiter separating the date and time components
    	hh: 2-digit hour in 24-hour format (07)
    	mm: 2-digit minutes (00)
    	ss: 2-digit seconds (00)
    	.sss: Milliseconds (000), representing fractions of a second
    	Z: Indicates that the time is in Coordinated Universal Time (UTC)
    	
    	Examples of valid datetime strings include: 
    		2024-07-10T07:00:00.000Z
    		Represents July 10, 2024, 7:00:00 AM UTC
    
    		2024-07-10 07:00:00.000 America/Los_Angeles 
    		Represents July 10, 2024, 7:00:00 AM in the America/Los_Angeles timezone
    '''

    params = {'q': 'getScheduleEvents'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_scheduleEvent( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Add Schedule Event
        Parameters
            Parameters need to be passed as keyword arguments
            Example:
                add_scheduleEvent( start='2024-07-10 10:00:00.000 America/Los_Angeles',
                                   end='2024-07-10 19:00:00.000 America/Los_Angeles', 
                                   statusName='BOOKED', userIDs=1 )
    	
        Required:
            start 						datetime 			Date if isAllDay = 1; datetime otherwise
                                                            (yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
            end 						datetime 			Date if isAllDay = 1; datetime otherwise
                                                            (yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
        At least one of:
            jobID 					    integer             A job ID to associate with the event
            userIDs 				    string				Comma-separated list of user IDs
            resourceIDs 			    string				Comma-separated list of resource IDs

        Optional:
            title 						string              The title of the event
            description 				string              The description of the event
            statusID 					integer             The ID of the status to associate with the event
            statusName 					string              The name of the status to associate with the event
            locationID 					integer             The ID of the location to associate with the event         
            jobID 						integer             The ID of the job to associate with the event
            userIDs 					string				Comma-separated list of user IDs
            resourceIDs 				string				Comma-separated list of resource IDs
            startTimezone 				string 				A valid timezone identifier; example: America/Los_Angeles
            endTimezone 				string 				A valid timezone identifier; example: America/Los_Angeles
            isAllDay 					bool 				0 or 1
            recurrenceId 				integer 			ID of this schedule event's parent; this should only exist if this event is an EXCEPTION to a recurring event's ruleset
            recurrenceRule 				string 				Recurring event ruleset string; see https://datatracker.ietf.org/doc/html/rfc5545
            recurrenceException 		string 				A list of comma-separated start datetimes for all exceptions to this recurring event's rules
            userUtilizationTypeID 		integer             The ID of the user utilization type to associate with the event
            userUtilizationType 		string              The name of the user utilization type to associate with the event
                                                            "hours per day", "percent per day", "total hours"
            userUtilizationValue 		string              The value of the user utilization type to associate with the event
            resourceUtilizationTypeID 	integer             The ID of the resource utilization type to associate with the event
            resourceUtilizationType 	string              The name of the resource utilization type to associate with the event
                                                            "units per day", "percent per day"
            resourceUtilizationValue 	string              The value of the resource utilization type to associate with the event

        Return:
            Returns a dictionary in the format
            result->success 		True/False
            result->error 			Includes any error or security messaging	
            result->ID 			    The ID of the newly created item
    '''

    params = {'q': 'addScheduleEvent'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_scheduleEvent( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Update Schedule Event
        Parameters
            Parameters need to be passed as keyword arguments
            Example:
                update_scheduleEvent( ID=3391, statusName='1st Hold' )

    	Required:
    		ID                          integer         The ID of the schedule event to update
        
        Optional:
    		title 						string
    		description 				string
    		statusID 					integer
    		statusName 					string
    		locationID 					integer
    		jobID 						integer
    		userIDs 					string				Comma-separated list of user IDs
    		resourceIDs 				string				Comma-separated list of resource IDs
    		start 						datetime 			Date if isAllDay = 1; datetime otherwise
    														(yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
    		end 						datetime 			Date if isAllDay = 1; datetime otherwise
    														(yyyy-mm-ddThh:mm:ss.sssZ or yyyy-mm-dd hh:mm:ss.sss timezone)
    		startTimezone 				string 				A valid timezone identifier; example: America/Los_Angeles
    		endTimezone 				string 				A valid timezone identifier; example: America/Los_Angeles
    		isAllDay 					bool 				0 or 1
    		recurrenceId 				integer 			ID of this schedule event's parent; this should only exist if this event is an EXCEPTION to a recurring event's ruleset
    		recurrenceRule 				string 				Recurring event ruleset string; see https://datatracker.ietf.org/doc/html/rfc5545
    		recurrenceException 		string 				A list of comma-separated start datetimes for all exceptions to this recurring event's rules
    		userUtilizationTypeID 		integer
    		userUtilizationType 		string
    		userUtilizationValue 		string
    		resourceUtilizationTypeID 	integer
    		resourceUtilizationType 	string
    		resourceUtilizationValue 	string

    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''

    params = {'q': 'updateScheduleEvent'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_scheduleEvent( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Delete Schedule Event
    
    Parameters
    	
        Required:
    		ID 					integer         The ID of the schedule event to delete
    
    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''

    params = {'q': 'deleteScheduleEvent'}
    if ID is not None : params['ID'] = ID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_scheduleEventStatuses( nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Get Schedule Statuses
    
    Parameters
    	nimURL                  string          Override for nimURL setting in prefs                                                             
                                                Including nimURL will override the default 
                                                NIM API url and skip the reading of saved 
                                                user preferences.
        apiUser                 string          Required if nimURL is set
                                                and Require API Keys is enabled in NIM
        apiKey                  string          Required if nimURL is set
                                                and Require API Keys is enabled in NIM
    
    Return:
    	Returns an associative array in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''
    result=False
    params = {'q': 'getScheduleEventStatuses'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Resources  #

def get_resources( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Get Resources based on search parameters
    
    Parameters
        Parameters need to be passed as keyword arguments
        Example:
            get_resources( locationName='Los Angeles', resourceGroups='Workstations,Licenses' )

    	Required:
    		none 										Will return all resources the requesting user has access to 
    
    	Optional:
    		ID 							integer 		The ID of a resource to query
    		name 						string 			Will return all resources matching the name
    		description 				string 			Will return all resources partially matching the description
    		color 						string 			Will return all resources matching the color
    		locationID 					integer			Will return all resources matching the location ID
    		locationName 				string 			Will return all resources matching the locationName
    		keywordIDs 					string 			Will return all resources matching the keywordIDs (comma separated list of IDs)
    		keywords 					string 			Will return all resources matching the keywords (comma separated list of names)
    		resourceGroupIDs 			string 			Will return all resources matching the resourceGroupIDs (comma separated list of IDs)
    		resourceGroups 				string 			Will return all resources matching the resourceGroups (comma separated list of names)
        	
            limit  						integer			Specifies the maximum number of rows to return
    		   											Default 0 (no limit)
    		offset 						integer			Specifies the number of rows to skip before starting to return rows.
    		   											Default 0
    
    Return:
    	Returns a dictionary in the format
    	result->success 		    True/False
    	result->error 			    Includes any error or security messaging
        result->total_count	        The total number of rows that match the search criteria
    	result->data 			    An array of returned data
    '''

    params = {'q': 'getResources'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_resource( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
     Add Resource
    
     Parameters
        Required:
            name 						string 				The resource name

        Optional:
            description 				string              The resource description
            color 						string              The resource color
            locationID					integer             The location ID
            keywords 					string 				Comma-separated list of keywords
            keywordIDs 					string				Comma-separated list of keyword IDs
            resourceGroups 				string 				Comma-separated list of resource groups
            resourceGroupIDs 			string 				Comma-separated list of resource group IDs

    Return:
        Returns a dictionary in the format
        result->success 		True/False
        result->error 			Includes any error or security messaging	
        result->ID 			    The ID of the newly created item
    '''

    params = {'q': 'addResource'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_resource( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Update Resource
        
    Parameters
    	Required:
    		ID                          integer             The ID of the resource to update
        
        Optional:
    		name 						string              The resource name
    		description 				string              The resource description
    		color 						string              The resource color
    		locationID					integer             The location ID
    		keywords 					string 				Comma-separated list of keywords
    		keywordIDs 					string				Comma-separated list of keyword IDs
    		resourceGroups 				string 				Comma-separated list of resource groups
    		resourceGroupIDs 			string 				Comma-separated list of resource group IDs

    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''

    params = {'q': 'updateResource'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_resource( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Delete Resource
    
    Parameters
    	
        Required:
    		ID 					integer         The ID of the resource to delete
    
    Return:
    	Returns a dictionary in the format
    	result->success 		True/False
    	result->error 			Includes any error or security messaging
    '''

    params = {'q': 'deleteResource'}
    if ID is not None : params['ID'] = ID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Jobs  #

def get_jobs( userID=None, folders=False, nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of all jobs for a given user'
    jobDict={}
    #  Build dictionary of jobs :
    params = {'q': 'getUserJobs', 'u': userID}
    _jobs = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    try:
        for job in _jobs :
            if not folders :
                jobDict[ ' '.join((job['number'],job['jobname'])) ] = job['ID']
            else :
                jobDict[ ' '.join((job['number'],'_',job['folder'])) ] = job['ID']
        return jobDict
    except :
        P.error("Failed to get jobs")
        P.error( traceback.print_exc() )
        return False

def get_crew( jobID=None, getData=None, limit=None, offset=None, \
              nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of crew members for a given job or list of jobs'
    params = {}
    params["q"] = "getCrew"
    
    if jobID is not None : params['jobID'] = jobID
    if getData is not None : params['getData'] = getData
    if limit is not None : params['limit'] = limit
    if offset is not None : params['offset'] = offset
    
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_job( name=None, number=None, numberTemplate=None, description=None, client_details=None, agency=None, producer=None, agency_producer=None, \
    phone=None, email=None, prod_co=None, prod_director=None, prod_contact=None, prod_phone=None, prod_email=None, \
    prod_shoot_date=None, prod_location=None, prod_supervised=None, editorial=None, editor=None, grading=None, colorist=None, \
    music=None, mix=None, sound=None, creative_lead=None, projectStatus=None, folder=None, projectStructureID=None, projectStructure=None, \
    jobStatusID=None, jobStatus=None, biddingLocationID=None, biddingLocation=None, \
    assignedLocationID=None, assignedLocation=None, startDate=None, endDate=None, currency=None, cultureID=None, customKeys=None, keywords=None, \
    contactIDs=None, nimURL=None, apiUser=None, apiKey=None) :
    '''
    Creates a new job. 

    If no default job number template is set, either number or numberTemplate must be included.

    ___________________________________________________________________________________

        Parameters              Type            Values                      Default

    Required:
        name                    string

    Optional:
        number                  string
        numberTemplate          string
        description             string
        client_details          string
        agency                  string
        producer                string
        agency_producer         string
        phone                   string
        email                   string
        prod_co                 string
        prod_director           string
        prod_contact            string
        prod_phone              string
        prod_email              string
        prod_shoot_date         date            YYYY-mm-dd
        prod_location           string
        prod_supervised         boolean         0/1                         0
        editorial               string
        editor                  string
        grading                 string
        colorist                string
        music                   string
        mix                     string
        sound                   string
        creative_lead           string
        
        projectStatus           string          ACTIVE / INACTIVE           ACTIVE

        folder                  string

        projectStructureID OR projectStructure
            projectStructureID  integer
            projectStructure    string  
        
        jobStatusID OR jobStatus
            jobStatusID         integer
            jobStatus           string

        biddingLocationID OR biddingLocation
            biddingLocationID   integer
            biddingLocation     string

        assignedLocationID OR assignedLocation
            assignedLocationID  integer
            assignedLocation    string
        
        start_date              date            YYYY-mm-dd
        end_date                date            YYYY-mm-dd
        currency                string          3 digit currency code (DEPRECATED)
                                                cultureID should be used instead of currency
                                                If currency is set instead of cultureID, NIM will use the first matching cultureID
        cultureID               integer         
        customKeys              dictionary      {"Custom Key Name" : "Value"}
        keywords                list            ["keyword1", "keyword2"]
        contactIDs 	            string          A comma separated list of contact IDs
                                                Example: 1,2,3
        
    '''
    params = {'q': 'addJob'}

    if name is not None : params['name'] = name
    if number is not None : params['number'] = number
    if numberTemplate is not None : params['numberTemplate'] = numberTemplate
    if description is not None : params['description'] = description
    if client_details is not None : params['client_details'] = client_details
    if agency is not None : params['agency'] = agency
    if producer is not None : params['producer'] = producer
    if agency_producer is not None : params['agency_producer'] = agency_producer
    if phone is not None : params['phone'] = phone
    if email is not None : params['email'] = email
    if prod_co is not None : params['prod_co'] = prod_co
    if prod_director is not None : params['prod_director'] = prod_director
    if prod_contact is not None : params['prod_contact'] = prod_contact
    if prod_phone is not None : params['prod_phone'] = prod_phone
    if prod_email is not None : params['prod_email'] = prod_email
    if prod_shoot_date is not None : params['prod_shoot_date'] = prod_shoot_date
    if prod_location is not None : params['prod_location'] = prod_location
    if prod_supervised is not None : params['prod_supervised'] = prod_supervised
    if editorial is not None : params['editorial'] = editorial
    if editor is not None : params['editor'] = editor
    if grading is not None : params['grading'] = grading
    if colorist is not None : params['colorist'] = colorist
    if music is not None : params['music'] = music
    if mix is not None : params['mix'] = mix
    if sound is not None : params['sound'] = sound
    if creative_lead is not None : params['creative_lead'] = creative_lead
    if projectStatus is not None : params['projectStatus'] = projectStatus
    if folder is not None : params['folder'] = folder
    if projectStructureID is not None : params['projectStructureID'] = projectStructureID
    if projectStructure is not None : params['projectStructure'] = projectStructure
    if jobStatusID is not None : params['jobStatusID'] = jobStatusID
    if jobStatus is not None : params['jobStatus'] = jobStatus
    if biddingLocationID is not None : params['biddingLocationID'] = biddingLocationID
    if biddingLocation is not None : params['biddingLocation'] = biddingLocation
    if assignedLocationID is not None : params['assignedLocationID'] = assignedLocationID
    if assignedLocation is not None : params['assignedLocation'] = assignedLocation
    if startDate is not None : params['start_date'] = startDate
    if endDate is not None : params['end_date'] = endDate
    if currency is not None : params['currency'] = currency
    if cultureID is not None : params['cultureID'] = cultureID
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)
    if keywords is not None : params['keywords'] = json.dumps(keywords)
    if contactIDs is not None : params['contactIDs'] = contactIDs

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_job( jobID=None, name=None, number=None, description=None, client_details=None, agency=None, producer=None, agency_producer=None, \
    phone=None, email=None, prod_co=None, prod_director=None, prod_contact=None, prod_phone=None, prod_email=None, \
    prod_shoot_date=None, prod_location=None, prod_supervised=None, editorial=None, editor=None, grading=None, colorist=None, \
    music=None, mix=None, sound=None, creative_lead=None, projectStatus=None, folder=None, projectStructureID=None, projectStructure=None, \
    jobStatusID=None, jobStatus=None, biddingLocationID=None, biddingLocation=None, \
    assignedLocationID=None, assignedLocation=None, startDate=None, endDate=None, currency=None, cultureID=None, customKeys=None, keywords=None, \
    contactIDs=None, nimURL=None, apiUser=None, apiKey=None) :
    '''
    Updates an existing job based on the jobID.

    The following values will only be updated if the job is offline:
        folder
        projectStructureID
        projectStructure

    ___________________________________________________________________________________

        Parameters              Type            Values                      Default

    Required:
        jobID                   integer

    Optional:
        name                    string
        number                  string
        description             string
        client_details          string
        agency                  string
        producer                string
        agency_producer         string
        phone                   string
        email                   string
        prod_co                 string
        prod_director           string
        prod_contact            string
        prod_phone              string
        prod_email              string
        prod_shoot_date         string          YYYY-mm-dd
        prod_location           string
        prod_supervised         boolean         0 / 1                       0
        editorial               string
        editor                  string
        grading                 string
        colorist                string
        music                   string
        mix                     string
        sound                   string
        creative_lead           string

        projectStatus           string          ACTIVE / INACTIVE           ACTIVE

        folder                  string

        projectStructureID OR projectStructure
            projectStructureID  integer
            projectStructure    string                  

        jobStatusID OR jobStatus
            jobStatusID         integer
            jobStatus           string

        biddingLocationID OR biddingLocation
            biddingLocationID   integer
            biddingLocation     string

        assignedLocationID OR assignedLocation
            assignedLocationID  integer
            assignedLocation    string

        start_date              date            YYYY-mm-dd
        end_date                date            YYYY-mm-dd
        currency                string          3 digit currency code (DEPRECATED)
                                                cultureID should be used instead of currency
                                                If currency is set instead of cultureID, NIM will use the first matching cultureID
        cultureID               integer
        customKeys              dictionary      {"Custom Key Name" : "Value"}
        keywords                list            ["keyword1", "keyword2"]
        contactIDs 	            string          A comma separated list of contact IDs
                                                Example: 1,2,3
    '''
    params = {'q': 'updateJob'}

    if jobID is not None : params['jobID'] = jobID
    if name is not None : params['name'] = name
    if number is not None : params['number'] = number
    if description is not None : params['description'] = description
    if client_details is not None : params['client_details'] = client_details
    if agency is not None : params['agency'] = agency
    if producer is not None : params['producer'] = producer
    if agency_producer is not None : params['agency_producer'] = agency_producer
    if phone is not None : params['phone'] = phone
    if email is not None : params['email'] = email
    if prod_co is not None : params['prod_co'] = prod_co
    if prod_director is not None : params['prod_director'] = prod_director
    if prod_contact is not None : params['prod_contact'] = prod_contact
    if prod_phone is not None : params['prod_phone'] = prod_phone
    if prod_email is not None : params['prod_email'] = prod_email
    if prod_shoot_date is not None : params['prod_shoot_date'] = prod_shoot_date
    if prod_location is not None : params['prod_location'] = prod_location
    if prod_supervised is not None : params['prod_supervised'] = prod_supervised
    if editorial is not None : params['editorial'] = editorial
    if editor is not None : params['editor'] = editor
    if grading is not None : params['grading'] = grading
    if colorist is not None : params['colorist'] = colorist
    if music is not None : params['music'] = music
    if mix is not None : params['mix'] = mix
    if sound is not None : params['sound'] = sound
    if creative_lead is not None : params['creative_lead'] = creative_lead
    if projectStatus is not None : params['projectStatus'] = projectStatus
    if folder is not None : params['folder'] = folder
    if projectStructureID is not None : params['projectStructureID'] = projectStructureID
    if projectStructure is not None : params['projectStructure'] = projectStructure
    if jobStatusID is not None : params['jobStatusID'] = jobStatusID
    if jobStatus is not None : params['jobStatus'] = jobStatus
    if biddingLocationID is not None : params['biddingLocationID'] = biddingLocationID
    if biddingLocation is not None : params['biddingLocation'] = biddingLocation
    if assignedLocationID is not None : params['assignedLocationID'] = assignedLocationID
    if assignedLocation is not None : params['assignedLocation'] = assignedLocation
    if startDate is not None : params['start_date'] = startDate
    if endDate is not None : params['end_date'] = endDate
    if currency is not None : params['currency'] = currency
    if cultureID is not None : params['cultureID'] = cultureID
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)
    if keywords is not None : params['keywords'] = json.dumps(keywords)
    if contactIDs is not None : params['contactIDs'] = contactIDs

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_job( jobID=None, nimURL=None, apiUser=None, apiKey=None) :
    '''
    Deletes a job based on jobID. This is a soft delete and these jobs can be recovered or permanently deleted from the Admin UI.

        Parameters      Type

    Required:
        jobID           integer

    '''
    params = {'q': 'deleteJob'}

    if jobID is not None : params['jobID'] = jobID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def upload_jobIcon( jobID=None, img=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Upload job icon'
    params = {}
    params["q"] = "uploadJobIcon"
    params["jobID"] = jobID
    
    if img is not None :
        img = os.path.normpath( img )
        if os.path.isfile(img) :
            params["file"] = open(img,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Image file not defined"
        return result

    if img is not None :
        result = upload(params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    return result

def get_jobInfo( jobID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of job information including ID, number, jobname, and folder'
    params = {}
    params["q"] = "getJobInfo"
    if jobID is not None : params['ID'] = jobID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_jobStatuses( nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available job statuses.'
    result=False
    params = {'q': 'getJobStatuses'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def find_jobs( nimURL=None, apiUser=None, apiKey=None, **kwargs ) :
    '''
    Returns a dictionary of job IDs or full job data based on the search criteria
        Optional: 
        getData    				0 / 1 		- if 0 returns IDs (default)
                                            - if 1 returns full data for items
                                            Returns limited data if user does not have permission to view job details
        ID						int			Allows comma separated list
        name					string	
        number					string
        description				string		Will partially match the job description
        startDate				date		YYYY-MM-DD
        endDate 				date		YYYY-MM-DD
        jobStatusID				int 		Job Status ID
        jobStatus				string 		Job Status Name
        folder                  string      The job folder name
        client_contactID		int			The ID of a linked contact
											Allows comma separated list
        client_details			string		Will partially match the client details 
        biddingLocationID		int 		ID of the corresponding locations
                                            Allows comma separated list
        biddingLocation			string 		Name of the bidding location
        assignedLocationID		int 		ID of the corresponding locations
                                            Allows comma separated list
        assignedLocation		string 		Name of the assigned location
        currency				string 		Currency code (USD, EUR, etc)
        is_private              int         (0, 1)
        agency					string		Agency
        agency_producer			string		Agency Producer
        agency_phone			string		Agency Phone
        agency_email			string		Agency Email
        production_company		string		Production Company
        director				string		Directory
        prod_contact			string		Production Contact
        prod_phone				string		Production Phone
        prod_email				string		Production Email
        producer				string		Producer
        creative_lead			string		Creative Lead
        grading					string		Grading
        colorist				string		Colorist
        editorial				string		Editorial
        editor					string		Editor
        mix						string		Mix
        music					string		Music
        sound_design			string		Sound Design
        shoot_date				date 		YYYY-MM-DD
        shoot_location			string		Shoot Location
        supervised				int 		(0, 1)
        proj_status				string		(ONLINE, OFFLINE)
        activity 				string 		(ACTIVE, INACTIVE)
        keywords 				array 		Allows comma separated list
                                            Example: keyword1,keyword2
        customKeys			    dictionary 	A dictionary of custom key names and values
                                            {"My Custom Key Name":"Some text","Another Custom Key":"Some other text"}

            Example:
            .../nimAPI.php?q=findJobs&getContacts={"My Custom Key Name":"Some text","Another Custom Key":"Some other text"}

        include_deleted - if 1 includes deleted jobs

        limit   - specifies the maximum number of rows to return
                - default 0 (no limit)
        offset  - specifies the number of rows to skip before starting to return rows.
                - default 0

        Note:
        This query can return a large amount of data.  
        Use the limit and offset values to paginate your return data.

    Return :
        success:        true/false
        error:          error message
        total_count:    total number of rows that match the search criteria
        data:           array of job data
    '''

    params = {'q': 'findJobs'}
    params.update(kwargs)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

#  Servers & Project Structures  #

def get_allServers( locationID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves all servers optionally filtered by locationID'
    params = {}
    params["q"] = "getServers"
    if locationID is not None : params['ID'] = locationID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_servers( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves servers associated with a specified job ID - does not match phpAPI'
    params = {}
    params["q"] = "getJobServers"
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_jobServers( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves servers associated with a specified job ID - matches phpAPI'
    params = {}
    params["q"] = "getJobServers"
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_serverInfo( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves servers information'
    params = {}
    params["q"] = "getServerInfo"
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_serverOSPath( ID=None, os=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves server path based on OS'
    params = {}
    params["q"] = "getServerOsPath"
    if ID is not None : 
        params['ID'] = ID
    else:
        return "Server ID Missing"
    if os is not None : params['os'] = os
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_osPath( fileID=None, os=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves file path based on OS'
    params = {}
    params["q"] = "getOSPath"
    if fileID is not None : 
        params['fileID'] = fileID
    else:
        return False
    if os is not None : params['os'] = os
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_paths( item='', ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves nim path for project structure - items options: job / show / shot / asset'
    params = {}
    params["q"] = "getPaths"
    if ID is not None : 
        params['ID'] = ID
    else:
        P.error ('get_paths: Missing ID')
        return False
    if item is not None : params['type'] = item
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def resolve_OsPath( os=None, path=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves server path based on OS'
    params = {}
    params["q"] = "resolveOsPath"
    if os is not None : 
        params['os'] = os
    else:
        return "OS Missing"
    if path is not None : 
        params['path'] = path
    else:
        return "Path Missing"
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def can_bringOnline( item='shot', jobID=0, assetID=0, showID=0, shotID=0, \
                    nimURL=None, apiUser=None, apiKey=None ) :
    'Tests item against variable based project structure to see if it can be brought online'
    'Item types can be asset or shot'
    '   -if asset, jobID OR assetID must be passed'
    '   -if shot, showID or shotID must be passed'

    params = {}
    params["q"] = 'canBringOnline'
    params["type"] = str(item)
    if int(jobID) > 0 :
        params["jobID"] = str(jobID)
    if int(assetID) > 0 :
        params["assetID"] = str(assetID)
    if int(showID) > 0 :
        params["showID"] = str(showID)
    if int(shotID) > 0 :
        params["shotID"] = str(shotID)
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def bring_online( item='shot', assetID=0, shotID=0, \
                  nimURL=None, apiUser=None, apiKey=None ) :
    'Brings assets and shots online creating folders from project structure'
    'Item types can be asset or shot'
    '   -if asset, assetID must be passed'
    '   -if shot, shotID must be passed'

    params = {}
    params["q"] = 'bringOnline'
    params["type"] = str(item)
    if int(assetID) > 0 :
        params["assetID"] = str(assetID)
    if int(shotID) > 0 :
        params["shotID"] = str(shotID)
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Assets  #

def get_assets( jobID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of all assets for a given job'
    params = {}
    params["q"] = "getAssets"
    if jobID is not None : params['ID'] = jobID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_asset( jobID=None, name=None, assetStatusID=None, assetStatus=None, description=None, customKeys=None, \
               nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Adds a new asset to a job and returns the new assetID.

    If an asset with the specified name already exists, NIM wil update 
    the existing asset instead of creating a new one with a duplicate name.

    An asset status can be passed by either name or ID. If both are passed the ID will be used.

        Parameters      Type

    Required:
        jobID           integer
        name            string

    Optional:
        assetStatusID   integer
        assetStatus     string
        description     string
        customKeys      dictionary {"Custom Key Name" : "Value"}

    '''
    params = {'q': 'addAsset'}

    if jobID is not None : params['jobID'] = jobID
    if name is not None : params['name'] = name
    if assetStatusID is not None : params['assetStatusID'] = assetStatusID
    if assetStatus is not None : params['assetStatus'] = assetStatus
    if description is not None : params['description'] = description
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_asset( assetID=None, assetStatusID=None, assetStatus=None, description=None, customKeys=None, \
                  nimURL=None, apiUser=None, apiKey=None) :
    '''
    Updates an existing asset based on the assetID.

    An asset status can be passed by either name or ID. If both are passed the ID will be used.

        Parameters      Type

    Required:
        assetID         integer

    Optional:
        assetStatusID   integer
        assetStatus     string
        description     string
        customKeys      dictionary {"Custom Key Name" : "Value"}
    '''
    params = {'q': 'updateAsset'}

    if assetID is not None : params['assetID'] = assetID
    if assetStatusID is not None : params['assetStatusID'] = assetStatusID
    if assetStatus is not None : params['assetStatus'] = assetStatus
    if description is not None : params['description'] = description
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_asset( assetID=None, nimURL=None, apiUser=None, apiKey=None) :
    '''
    Deletes an asset based on assetID.

        Parameters      Type

    Required:
        assetID           integer

    '''
    params = {'q': 'deleteAsset'}
    
    if assetID is not None : params['assetID'] = assetID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey  )
    return result

def upload_assetIcon( assetID=None, img=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Upload asset icon'
    params = {}
    params["q"] = "uploadAssetIcon"
    params["assetID"] = assetID

    if img is not None :
        img = os.path.normpath( img )
        if os.path.isfile(img) :
            params["file"] = open(img,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Image file not defined"
        return result

    if img is not None :
        result = upload(params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    return result

def get_assetInfo( assetID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves information for a given asset'
    params = {}
    params["q"] = "getAssetInfo"
    if assetID is not None : params['ID'] = assetID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def get_assetIcon( assetID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves information for a given asset'
    params = {}
    params["q"] = "getAssetIcon"
    if assetID is not None : params['ID'] = assetID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result   

def get_assetStatuses( nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available asset statuses.'
    result=False
    params = {'q': 'getAssetStatuses'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

#  Shows  #

def get_shows( jobID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of all shows for a given job'
    params = {}
    params["q"] = "getShows"
    if jobID is not None : params['ID'] = jobID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def get_showInfo( showID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of all shows for a given show'
    params = {}
    params["q"] = "getShowInfo"
    if showID is not None : params['ID'] = showID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def add_show( jobID=None, name=None, trt=None, has_previs=None, \
              nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Adds a new show to a job and returns the new showID

        Parameters      Type        Value

    Required:
        jobID           integer
        name            string

    Optional:
        trt             string
        has_previs      boolean      0/1   (a value of 1 will create an associated previs show)
    '''
    params = {'q': 'addShow'}

    if jobID is not None : params['jobID'] = jobID
    if name is not None : params['name'] = name
    if trt is not None : params['trt'] = trt
    if has_previs is not None : params['has_previs'] = has_previs

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_show( showID=None, name=None, trt=None, \
                 nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Updates an existing show based on the showID.

        Parameters      Type        Value

    Required:
        showID          integer

    Optional:
        name            string
        trt             string
    '''
    params = {'q': 'updateShow'}

    if showID is not None : params['showID'] = showID
    if name is not None : params['name'] = name
    if trt is not None : params['trt'] = trt

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_show( showID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Deletes an existing show based on the showID.

        Parameters      Type

    Required:
        showID          integer
    '''
    params = {'q': 'deleteShow'}

    if showID is not None : params['showID'] = showID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey  )
    return result


#  Shots  #

def get_shots( showID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Builds a dictionary of all shots for a given show'
    params = {}
    params["q"] = "getShots"
    if showID is not None : params['ID'] = showID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_shot( showID=None, shotName=None, name=None, shotStatusID=None, shotStatus=None, description=None, vfx=None, fps=None, frames=None, \
    shotDuration=None, handles=None, heads=None, tails=None, height=None, pan=None, tilt=None, roll=None, lens=None, fstop=None, filter=None, \
    dts=None, focus=None, ia=None, convergence=None, cam_roll=None, stock=None, format=None, crop=None, protect=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Adds a shot to a show and returns the new ID.

    If a shot with the specified name already exists, NIM wil update 
    the existing shot instead of creating a new one with a duplicate name.

    A shot status can be passed by either name or ID. If both are passed the ID will be used.

        Parameters              Type

    Required:
        showID                  integer
        shotName/name           string

    Optional:
        shotStatusID            integer
        shotStatus              string
        description             string
        vfx                     string
        fps                     string
        frames/shotDuration     string
        handles                 string
        heads                   string
        tails                   string
        height                  string
        pan                     string
        tilt                    string
        roll                    string
        lens                    string
        fstop                   string
        filter                  string
        dts                     string
        focus                   string
        ia                      string
        convergence             string
        cam_roll                string
        stock                   string
        format                  string
        crop                    string
        protect                 string
        customKeys              dictionary {"Custom Key Name" : "Value"}

    '''
    params = {'q': 'addShot'}

    if showID is not None : params['showID'] = showID
    if shotName is not None : params['name'] = shotName
    if shotStatusID is not None : params['shotStatusID'] = shotStatusID
    if shotStatus is not None : params['shotStatus'] = shotStatus
    if name is not None : params['name'] = name
    if description is not None : params['description'] = description
    if vfx is not None : params['vfx'] = vfx
    if fps is not None : params['fps'] = fps
    if shotDuration is not None : params['frames'] = shotDuration
    if frames is not None : params['frames'] = frames
    if handles is not None : params['handles'] = handles
    if heads is not None : params['heads'] = heads
    if tails is not None : params['tails'] = tails
    if height is not None : params['height'] = height
    if pan is not None : params['pan'] = pan
    if tilt is not None : params['tilt'] = tilt
    if roll is not None : params['roll'] = roll
    if lens is not None : params['lens'] = lens
    if fstop is not None : params['fstop'] = fstop
    if filter is not None : params['filter'] = filter
    if dts is not None : params['dts'] = dts
    if focus is not None : params['focus'] = focus
    if ia is not None : params['ia'] = ia
    if convergence is not None : params['convergence'] = convergence
    if cam_roll is not None : params['cam_roll'] = cam_roll
    if stock is not None : params['stock'] = stock
    if format is not None : params['format'] = format
    if crop is not None : params['crop'] = crop
    if protect is not None : params['protect'] = protect
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_shot( shotID=None, shotStatusID=None, shotStatus=None, description=None, vfx=None, fps=None, frames=None, duration=None, \
    handles=None, heads=None, tails=None, height=None, pan=None, tilt=None, roll=None, lens=None, fstop=None, filter=None, \
    dts=None, focus=None, ia=None, convergence=None, cam_roll=None, stock=None, format=None, crop=None, protect=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Updates an existing shot based on the shotID.

    A shot status can be passed by either name or ID. If both are passed the ID will be used.

        Parameters          Type

    Required:
        shotID              integer
    
    Optional:
        shotStatusID        integer
        shotStatus          string
        description         string
        vfx                 string
        fps                 string
        frames/duration     string
        handles             string
        heads               string
        tails               string
        height              string
        pan                 string
        tilt                string
        roll                string
        lens                string
        fstop               string
        filter              string
        dts                 string
        focus               string
        ia                  string
        convergence         string
        cam_roll            string
        stock               string
        format              string
        crop                string
        protect             string
        customKeys          dictionary {"Custom Key Name" : "Value"}
    '''
    params = {'q': 'updateShot'}

    if shotID is not None : params['shotID'] = shotID
    if shotStatusID is not None : params['shotStatusID'] = shotStatusID
    if shotStatus is not None : params['shotStatus'] = shotStatus
    if description is not None : params['description'] = description
    if vfx is not None : params['vfx'] = vfx
    if fps is not None : params['fps'] = fps
    if duration is not None : params['frames'] = duration
    if frames is not None : params['frames'] = frames
    if handles is not None : params['handles'] = handles
    if heads is not None : params['heads'] = heads
    if tails is not None : params['tails'] = tails
    if height is not None : params['height'] = height
    if pan is not None : params['pan'] = pan
    if tilt is not None : params['tilt'] = tilt
    if roll is not None : params['roll'] = roll
    if lens is not None : params['lens'] = lens
    if fstop is not None : params['fstop'] = fstop
    if filter is not None : params['filter'] = filter
    if dts is not None : params['dts'] = dts
    if focus is not None : params['focus'] = focus
    if ia is not None : params['ia'] = ia
    if convergence is not None : params['convergence'] = convergence
    if cam_roll is not None : params['cam_roll'] = cam_roll
    if stock is not None : params['stock'] = stock
    if format is not None : params['format'] = format
    if crop is not None : params['crop'] = crop
    if protect is not None : params['protect'] = protect
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_shot( shotID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Deletes a shot based on shotID.

        Parameters      Type

    Required:
        shotID           integer

    '''
    params = {'q': 'deleteShot'}
    
    if shotID is not None : params['shotID'] = shotID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def upload_shotIcon( shotID=None, img=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Upload shot icon'
    params = {}
    params["q"] = "uploadShotIcon"
    params["shotID"] = shotID
    
    if img is not None :
        img = os.path.normpath( img )
        if os.path.isfile(img) :
            params["file"] = open(img,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Image file not defined"
        return result

    if img is not None :
        result = upload(params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    return result

def get_shotInfo( shotID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves information for a given shot'
    params = {}
    params["q"] = "getShotInfo"
    if shotID is not None : params['ID'] = shotID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def get_shotIcon( shotID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves information for a given shot'
    params = {}
    params["q"] = "getShotIcon"
    if shotID is not None : params['ID'] = shotID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def get_shotStatuses( nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available shot statuses.'
    result=False
    params = {'q': 'getShotStatuses'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

#  Tasks  #

#  get_tasks() DEPRECATED in 2.9 in favor of get_taskTypes() to match REST API
def get_tasks( app='all', userType='artist', assetID=None, shotID=None, onlyWithFiles=None, \
               nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the dictionary of available tasks types.

    Default app value returns tasks for all application types. Pass a valid application type to filter the task types returned.

    userType will filter tasks by their associated userType

    If an asset or shot ID is passed, these will include in-use tasks on the asset or shot.

    The onlyWithFiles flag works in conjunction with an asset or shot ID to return only task types that have files associated.

        Parameters          Type            Values
    Optional:
        app                 string          MAYA / C4D / AE / PHOTOSHOP / NUKE / HIERO / 3DSMAX / HOUDINI / FLAME 

        userType            string          artist / producer / edit / management

        assetID or shotID
            assetID         integer
            shotID          integer

        onlyWithFiles       boolean         0 / 1

    '''
    params = {'q': 'getTaskTypes'}

    if app is not None : params['app'] = app
    if userType is not None : params['type'] = userType
    if assetID is not None : params['assetID'] = assetID
    if shotID is not None : params['shotID'] = shotID
    if onlyWithFiles is not None : 
        if onlyWithFiles == True : onlyWithFiles = 1
        else : onlyWithFiles = 0
        params['onlyWithFiles'] = onlyWithFiles

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_taskTypes( app='all', userType='artist', assetID=None, shotID=None, onlyWithFiles=None, pub=None, \
                   nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the dictionary of available tasks types.

    Default app value returns tasks for all application types. Pass a valid application type to filter the task types returned.

    userType will filter tasks by their associated userType

    If an asset or shot ID is passed, these will include in-use tasks on the asset or shot.

    The onlyWithFiles flag works in conjunction with an asset or shot ID to return only task types that have files associated.

        Parameters          Type            Values
    Optional:
        app                 string          MAYA / C4D / AE / PHOTOSHOP / NUKE / HIERO / 3DSMAX / HOUDINI / FLAME 

        userType            string          artist / producer / edit / management

        assetID or shotID
            assetID         integer
            shotID          integer

        onlyWithFiles       boolean         0 / 1

    '''
    params = {'q': 'getTaskTypes'}

    if app is not None : params['app'] = app
    if userType is not None : params['type'] = userType
    if assetID is not None : params['assetID'] = assetID
    if shotID is not None : params['shotID'] = shotID
    if onlyWithFiles is not None : 
        if onlyWithFiles == True : onlyWithFiles = 1
        else : onlyWithFiles = 0
        params['onlyWithFiles'] = onlyWithFiles
    if pub is not None : 
        if pub == True : pub = 1
        else : pub = 0
        params['pub'] = pub

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_task( assetID=None, shotID=None, taskTypeID=None, taskTypeName=None, userID=None, username=None, \
    taskStatusID=None, taskStatus=None, description=None, estimatedHours=None, startDate=None, endDate=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Adds a new task to an asset or shot.

    AssetID or shotID can be passed. If both are passed, assetID will be used.

    The task type can be determined by passing taskTypeID or taskTypeName. If both are passed, taskTypeID will be used.

    A user can be attached to the task by passing either userID or username. If both are passed, userID will be used.
    
        Parameters              Type
    Required:
        assetID or shotID
            assetID             integer
            shotID              integer

        taskTypeID or taskTypeName
            taskTypeID          integer
            taskTypeName        string

    Optional:
        userID OR username
            userID              integer
            username            string

        taskStatusID OR taskStatus
            taskStatusID        integer
            taskStatus          string

        description             string
        estimated_hours         float
        startDate               (UTC datetime string: "2017-01-01 08:00:00")
        endDate                 (UTC datetime string: "2017-01-01 08:00:00")
        customKeys              dictionary {"Custom Key Name" : "Value"}
    '''
    params = {'q': 'addTask'}

    if assetID is not None : params['assetID'] = assetID
    if shotID is not None : params['shotID'] = shotID
    if taskTypeID is not None : params['taskTypeID'] = taskTypeID
    if taskTypeName is not None : params['taskTypeName'] = taskTypeName
    if userID is not None : params['userID'] = userID
    if username is not None : params['username'] = username
    if taskStatusID is not None : params['taskStatusID'] = taskStatusID
    if taskStatus is not None : params['taskStatus'] = taskStatus
    if description is not None : params['description'] = description
    if estimatedHours is not None : params['estimated_hours'] = estimatedHours
    if startDate is not None : params['startDate'] = startDate
    if endDate is not None : params['endDate'] = endDate
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_task( taskID=None, taskTypeID=None, taskTypeName=None, userID=None, username=None, \
    taskStatusID=None, taskStatus=None, description=None, estimatedHours=None, startDate=None, endDate=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Updates an existing task based on taskID.

    The task type can be determined by passing taskTypeID or taskTypeName. If both are passed, taskTypeID will be used.

    A user can be attached to the task by passing either userID or username. If both are passed, userID will be used.

        Parameters              Type
    Required:
        taskID                  integer

    Optional:
        taskTypeID or taskTypeName
            taskTypeID          integer
            taskTypeName        string
        userID OR username
            userID              integer
            username            string

        taskStatusID OR taskStatus
            taskStatusID        integer
            taskStatus          string

        description             string
        estimated_hours         float
        startDate               (UTC datetime string: "2017-01-01 08:00:00")
        endDate                 (UTC datetime string: "2017-01-01 08:00:00")
        customKeys              dictionary {"Custom Key Name" : "Value"}
    '''
    params = {'q': 'updateTask'}

    if taskID is not None : params['taskID'] = taskID
    if taskTypeID is not None : params['taskTypeID'] = taskTypeID
    if taskTypeName is not None : params['taskTypeName'] = taskTypeName
    if userID is not None : params['userID'] = userID
    if username is not None : params['username'] = username
    if taskStatusID is not None : params['taskStatusID'] = taskStatusID
    if taskStatus is not None : params['taskStatus'] = taskStatus
    if description is not None : params['description'] = description
    if estimatedHours is not None : params['estimated_hours'] = estimatedHours
    if startDate is not None : params['startDate'] = startDate
    if endDate is not None : params['endDate'] = endDate
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_task( taskID=None, nimURL=None, apiUser=None, apiKey=None) :
    '''
    Deletes a task based on taskID.

        Parameters      Type

    Required:
        taskID           integer

    '''
    params = {'q': 'deleteTask'}
    if taskID is not None : params['taskID'] = taskID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_taskInfo( ID=None, itemClass=None, itemID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves a dictionary of task information for a given asset or shot item from the API'

    params = {'q': 'getTaskInfo'}
    if ID is not None : params['ID'] = ID
    if itemClass is not None : params['class'] = itemClass
    if itemID is not None : params['itemID'] = itemID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_taskStatuses( nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available task statuses.'
    result=False
    params = {'q': 'getTaskStatuses'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

#  Files  #

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
                    if 'name' in list(task.keys()) and nim.name('task')==task['name'] :
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
                    if 'name' in list(task.keys()) and nim.name('task')==task['name'] :
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
        baseInfo=get_baseVer( shotID=nim.ID( 'shot' ), basename=basename )
    elif nim.tab()=='ASSET' :
        baseInfo=get_baseVer( assetID=nim.ID( 'asset' ), basename=basename )
    if baseInfo and 'version' in list(baseInfo[0].keys()) :
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


def get_bases( shotID=None, assetID=None, showID=None, task='', taskType=None, taskID=None, taskTypeID=None, pub=False, \
               nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the dictionary of basenames for a show, shot or asset.

    def get_bases( shotID=None, assetID=None, showID=None, task='', taskType=None, taskID=None, taskTypeID=None, pub=False )

        Parameters              Description                                  Type            Values                      Default        Required
    _____________________________________________________________________________________________________________________________________________

        shotID, assetID, or showID                                                                                                      YES
            shotID              The shot ID to find basenames                integer                                                    ---
            assetID             The asset ID to find basenames               integer                                                    ---
            showID              The show ID to find basenames                integer                                                    ---
        task / taskType         Task Type Name to filter results             string
        taskID / taskTypeID     Task Type ID to filter results               integer
        pub                     Filter to only return published basenames    boolean         True/False                  False

    Return:
        dictionary
    '''

    # Alternative variable name entries for clarity
    if taskType is not None : task = taskType
    if taskTypeID is not None : taskID = taskTypeID

    if shotID :
        ID=shotID
        _type='SHOT'
    elif assetID :
        ID=assetID
        _type='ASSET'
    else :
        ID=showID
        _type='SHOW'

    params = {}

    if not pub :
        params["q"] = "getBasenames"
        if ID is not None : params['ID'] = ID
    elif pub :
        params["q"] = "getBasenameAllPub"
        if ID is not None : params['itemID'] = ID

    if _type is not None : params['class'] = _type

    if task and not taskID :
        if task.upper() is not None : params['type'] = task.upper()
    elif not task and taskID :
        if taskID is not None : params['task_type_ID'] = taskID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_basesPub( shotID=None, assetID=None, basename='', username=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the dictionary of the published file for a given basename.
    The optional username is used to return the date information in the users seleted timezone.

        Parameters              Type

    Required:
        shotID OR assetID
        shotID                  integer
        assetID                 integer
        basename                string

    Optional:
        username                string
    '''

    params = {'q': 'getBasenamePub'}

    if shotID is not None : 
        params['itemID'] = shotID
        params['class'] = 'SHOT'

    elif assetID is not None : 
        params['itemID'] = assetID
        params['class'] = 'ASSET'

    if basename is not None : params['basename'] = basename
    if username is not None : params['username'] = username

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_basesAllPub( shotID=None, assetID=None, task=None, taskID=None, username=None, \
                     nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the dictionary of all available published basenames for a given asset or shot.
    The optional username is used to return the date information in the users selected timezone.

        Parameters              Type

    Required:
        shotID OR assetID
            shotID              integer
            assetID             integer

        task OR taskID
            task                string
            taskID              integer

    Optional:
        username                string
    '''

    params = {'q': 'getBasenameAllPub'}

    if shotID is not None : 
        params['itemID'] = shotID
        params['class'] = 'SHOT'

    if assetID is not None : 
        params['itemID'] = assetID
        params['class'] = 'ASSET'

    if task is not None : params['type'] = task.upper()
    if taskID is not None: params['task_type_ID'] = taskID
    if username is not None : params['username'] = username

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_baseInfo( shotID=None, assetID=None, showID=None, taskTypeID=None, \
                  nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves all basenames and their max version for given asset, shot, or show based on ID
    
        Parameters              Type

    Required:
        shotID, assetID, or showID
            shotID              integer
            assetID             integer
            showID              integer

        taskTypeID              integer
    '''

    params = {'q': 'getBasenamesInfo'}

    if shotID is not None : 
        params['ID'] = shotID
        params['class'] = 'SHOT'

    if assetID is not None : 
        params['ID'] = assetID
        params['class'] = 'ASSET'

    if showID is not None : 
        params['ID'] = showID
        params['class'] = 'SHOW'

    if taskTypeID is not None : params['task_type_ID'] = taskTypeID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_baseVer( shotID=None, assetID=None, showID=None, basename='', \
                 nimURL=None, apiUser=None, apiKey=None ) :
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

    params = {}
    params["q"] = "getBasenameVersion"
    if _type is not None : params['class'] = _type
    if ID is not None : params['itemID'] = ID
    if basename is not None : params['basename'] = basename
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 


def get_vers( shotID=None, assetID=None, showID=None, basename=None, pub=False, username=None, \
              nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the dictionary of available versions from the API.
    The optional username is used to return the date information in the users selected timezone.

        Parameters              Type            Value       Default

    Required:
        shotID OR assetID OR showID
        shotID                  integer
        assetID                 integer
        showID                  integer
        basename                string

    Optional:
        pub                     boolean         0/1         0
        username                string
    
    '''
        
    params = {'q': 'getVersions'}

    if shotID is not None : 
        params['itemID'] = shotID
        params['type'] = 'SHOT'

    elif assetID is not None : 
        params['itemID'] = assetID
        params['type'] = 'ASSET'
    
    else :
        params['itemID'] = showID
        params['type'] = 'SHOW'

    if basename is not None : params['basename'] = basename

    if pub :
        params['pub'] = 1
    else :
        params['pub'] = 0

    if username is not None : params['username'] = username

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_verInfo( verID=None, username=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves the information for a given version ID.
    The optional username is used to return the date information in the users selected timezone.

        Parameters              Type

    Required:
        verID                   integer

    Optional:
        username                string
    
    '''

    params = {'q': 'getVersionInfo'}

    if verID is not None : params['ID'] = verID
    if username is not None : params['username'] = username

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def versionUp( nim=None, padding=2, selected=False, win_launch=False, pub=False, symLink=True ) :
    'NIM Connector Function used to save/publish/version up files'
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
            from . import nim_maya as M
            M.get_vars( nim=nim )
        elif nim.app()=='Nuke' :
            from . import nim_nuke as N
            N.get_vars( nim=nim )
        elif nim.app()=='C4D' :
            from . import nim_c4d as C
            nim_plugin_ID=1032427
            C.get_vars( nim=nim, ID=nim_plugin_ID )
        elif nim.app()=='3dsMax' :
            from . import nim_3dsmax as Max
            Max.get_vars( nim=nim )
        elif nim.app()=='Houdini' :
            from . import nim_houdini as Houdini
            Houdini.get_vars( nim=nim )
        elif nim.app()=='Flame' :
            from . import nim_flame as Flame
            Flame.get_vars( nim=nim )
    
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
            msg +='\n  Please try saving from the NIM > Save As menu.'
        P.error( '\n'+msg )
        P.error( '    File Path = %s' % nim.filePath() )
        nim.Print()
        Win.popup( title=winTitle+' - Filename Error', msg=msg )
        return False
    
    #  Version Up File :
    #  [AS] returning nim object from verUp to update if loading exported file
    verUpResult=F.verUp( nim=nim, padding=padding, selected=selected, win_launch=win_launch, pub=pub, symLink=symLink )

    if verUpResult :
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
                                from . import nim_maya as M
                                M.set_vars( nim=verUpNim )
                                nim = verUpNim
                                
                            except Exception as e :
                                P.error( 'Failed reading the file: %s' % filePath )
                                P.error( '    %s' % traceback.print_exc() )
                                return False
                        #  Nuke :
                        elif nim.app()=='Nuke' :
                            import nuke
                            try :
                                #  Prompt to Save :
                                if nuke.root().modified() :
                                    from . import nim_nuke as N
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
                                from . import nim_nuke as N
                                N.set_vars( nim=verUpNim )
                                nim = verUpNim
                                
                            except Exception as e :
                                P.error( 'Failed reading the file: %s' % filePath )
                                P.error( '    %s' % traceback.print_exc() )
                                return False
                            try :
                                P.info( 'Setting Nuke environment variables...' )
                                from . import nim_nuke as N
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
                            except Exception as e :
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
                                from . import nim_c4d as C
                                C.set_vars( nim=verUpNim, ID=nim_plugin_ID )
                                nim = verUpNim
                                
                            except Exception as e :
                                P.error( 'Failed reading the file: %s' % filePath )
                                P.error( '    %s' % traceback.print_exc() )
                                return False
                        
                        elif nim.app()=='3dsMax' :
                            from pymxs import runtime as maxRT
                            try :
                                maxRT.loadMaxFile(filePath)
                                #  Set env vars brought over from nim_file
                                P.info('Setting Environment Variables')
                                P.info('NIM: %s \n' % verUpNim.name(elem='base'))
                                from . import nim_3dsmax as Max
                                Max.set_vars( nim=verUpNim )
                                nim = verUpNim
                                
                            except Exception as e :
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
                                from . import nim_houdini as Houdini
                                Houdini.set_vars( nim=verUpNim )
                                nim = verUpNim
                                
                            except Exception as e :
                                P.error( 'Failed reading the file: %s' % filePath )
                                P.error( '    %s' % traceback.print_exc() )
                                return False
                
                return filePath
        
        #  If not successful, fail :
        else :
            P.error( 'Failed to log the file to NIM.' )
            Win.popup( title=winTitle+' - Version Up Failure', \
                msg='Failed to log the file to NIM.\n\nPlease check the application logs for more details.' )
            return False

    #  If not successful, fail :
    else :
        P.error( 'Failed to save the file.' )
        Win.popup( title=winTitle+' - Version Up Failure', \
            msg='Failed to save the file.\n\nPlease check the application logs for more details.' )
        return False


def clear_pubFlags( shotID=None, assetID=None, showID=None, fileID=None, basename='', \
                    nimURL=None, apiUser=None, apiKey=None ) :
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

    params = {}
    params["q"] = "clearPubFlags"
    if _type is not None : params['class'] = _type
    if ID is not None : params['itemID'] = ID
    if basename is not None : params['basename'] = basename
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def publish_symLink( fileID=None, elementID=None, forceLink=1, \
                     nimURL=None, apiUser=None, apiKey=None ) :
    '''Creates the symbolic link for a published file'''
    params = {}
    params["q"] = "publishSymlink"
    if fileID :
        P.info('Creating SymLink for Published File')
        if fileID is not None : params['fileID'] = fileID
        if forceLink is not None : params['forceLink'] = forceLink
    elif elementID :
        P.info('Creating SymLink for Published Element')
        if elementID is not None : params['elementID'] = elementID
        if forceLink is not None : params['forceLink'] = forceLink
    else :
        P.error( 'Missing Item ID.' )
        return False
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


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
        if prefs and app+'_ServerPath' in list(prefs.keys()) :
            projPath=prefs[app+'_ServerPath']
            #P.error( 'AS - projPath: %s' % prefs[app+'_ServerPath'] )

        if prefs and app+'_ServerID' in list(prefs.keys()) :
            projPath=prefs[app+'_ServerID']


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
        '''
        #  Error check dictionaries :
        if not shotInfo or not basenameInfo or not len(shotInfo) or not len(basenameInfo) :
            P.warning( '\nProblem retrieving Shot/Basename information from the database.' )
            P.warning( 'Shot Info = %s' % shotInfo )
            P.warning( 'Basename Info = %s' % basenameInfo )
        '''
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
        
        print(('Task Folder = %s' % nim.taskFolder()))
        
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

def save_file( parent='SHOW', parentID=0, task_type_ID=0, task_folder='', userID=0, basename='', filename='', \
    path='', ext=None, version=None, comment=None, serverID=0, pub=False, forceLink=1, work=True, metadata=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None) :
    '''General Purpose Save File Function that Adds a File to the NIM Database with brute force data.

       Required Parameters:
           parent ('asset', 'shot', 'show')
           parentID (assetID, shotID, showID)
           task_type_ID
           task_folder
           userID
           basename
           filename
           path
           serverID
       Optional Parameters:
           ext
           version
           comment
           pub True/False
           work True/False
           customKeys
           metadata
           forceLink
    '''


    parent = parent.upper()

    if not pub :
        #result=get( {'q': 'addFile', 'class': parent, 'itemID': str(parentID), 
        #    'task_type_ID': str(task_type_ID), 'task_type_folder': task_folder,
        #    'userID': str(userID), 'basename': basename, 'filename': filename,
        #    'filepath': path, 'ext': ext, 'version': str(version), 'note': comment,
        #    'serverID': str(serverID), 'metadata': metadata } )

        params = {'q': 'addFile'}

        if parent is not None : params['class'] = parent
        if parentID is not None : params['itemID'] = parentID
        if task_type_ID is not None : params['task_type_ID'] = task_type_ID
        if task_folder is not None : params['task_type_folder'] = task_folder
        if userID is not None : params['userID'] = userID
        if basename is not None : params['basename'] = basename
        if filename is not None : params['filename'] = filename
        if path is not None : params['filepath'] = path
        if ext is not None : params['ext'] = ext
        if version is not None : params['version'] = version
        if comment is not None : params['note'] = comment
        if serverID is not None : params['serverID'] = serverID
        if metadata is not None : params['metadata'] = metadata
        if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    elif pub :
        if parent == "SHOW":
            clear_pubFlags( showID=parentID, basename=basename, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
        elif parent == 'SHOT':
            clear_pubFlags( shotID=parentID, basename=basename, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
        elif parent == 'ASSET' :
            clear_pubFlags( assetID=parentID, basename=basename, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
        else:
            P.error( 'A parent of proper type was not defined. Available options are SHOW, SHOT, & ASSET.' )
            return False

        is_work = 0
        if work:
            is_work = 1

        #result=get( {'q': 'addFile', 'class': parent, 'itemID': str(parentID),
        #    'task_type_ID': str(task_type_ID), 'task_type_folder': task_folder,
        #    'userID': str(userID), 'basename': basename, 'filename': filename,
        #    'filepath': path, 'ext': ext, 'version': str(version), 'note': comment,
        #    'serverID': str(serverID), 'isPub': 1, 'isWork': is_work, 'metadata': metadata } )

        params = {'q': 'addFile'}

        if parent is not None : params['class'] = parent
        if parentID is not None : params['itemID'] = parentID
        if task_type_ID is not None : params['task_type_ID'] = task_type_ID
        if task_folder is not None : params['task_type_folder'] = task_folder
        if userID is not None : params['userID'] = userID
        if basename is not None : params['basename'] = basename
        if filename is not None : params['filename'] = filename
        if path is not None : params['filepath'] = path
        if ext is not None : params['ext'] = ext
        if version is not None : params['version'] = version
        if comment is not None : params['note'] = comment
        if serverID is not None : params['serverID'] = serverID
        params['isPub'] = 1
        params['isWork'] = is_work
        if metadata is not None : params['metadata'] = metadata
        if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
        
    if result['success'] == False :
        P.error( 'There was a problem writing to the NIM database.' )
        P.error( '    Database has not been populated with your file.' )
        P.error( result['error'] )
        return result
    else :
        P.info( 'NIM API updated with new file.' )
        P.info( '      File ID = %s' % result['ID'] )

        if pub:
            ID = result['ID']
            #Create symlink for published files
            pub_result = publish_symLink(fileID=ID, forceLink=forceLink, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
            P.error('pub_result: %s' % pub_result)
            if pub_result == True:
                P.info('...Success')
            else:
                P.error('There was a problem creating the symlink for the published file\n \
                        Please check to make sure the file exists on disk.')
    return result

def update_file( ID=None, task_type_ID=None, task_folder=None, userID=None, basename=None, filename=None, path=None, ext=None, \
    version=None, comment=None, serverID=None, pub=None, forceLink=None, work=None, metadata=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    '''General Purpose Update File Function that Updates and existing File in the NIM Database'''
    
    is_work = 1
    if work is not None and work == False:
        is_work = 0
    
    is_pub = 0
    if pub is not None:
        clear_pubFlags( fileID=ID, basename=basename, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
        if pub == True:
            is_pub = 1
    
    params = {'q': 'updateFile'}

    if ID is not None : params['ID'] = ID
    if task_type_ID is not None : params['task_type_ID'] = task_type_ID
    if task_folder is not None : params['task_type_folder'] = task_folder
    if userID is not None : params['userID'] = userID
    if basename is not None : params['basename'] = basename
    if filename is not None : params['filename'] = filename
    if path is not None : params['filepath'] = path
    if ext is not None : params['ext'] = ext
    if version is not None : params['version'] = version
    if comment is not None : params['note'] = comment
    if serverID is not None : params['serverID'] = serverID
    if pub is not None : params['isPub'] = is_pub
    if work is not None : params['isWork'] = is_work
    if metadata is not None : params['metadata'] = metadata
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    if result['success'] == False :
        P.error( 'There was a problem writing to the NIM database.' )
        P.error( '    Database has not been updated with your file.' )
        P.error( result['error'] )
        return result
    else :
        P.info( 'NIM API updated existing file.' )
        P.info( '      File ID = %s' % result['ID'] )
        if pub == True:
            #Create symlink for published files
            pub_result = publish_symLink(fileID=ID, forceLink=forceLink, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
            if pub_result == 'true':
                P.info('...Success')
            else:
                P.error('There was a problem creating the symlink for the published file \
                        Please check to make sure the file exists on disk.')
    return result

def find_files( parent='shot', parentID=None, name='', path='', metadata='', \
                nimURL=None, apiUser=None, apiKey=None ):
    '''
    Finds files based on the passed parameters
    Returns an array of files found

        Parameters          Type            Values
    Optional:
        parent              string          'asset' OR 'shot'
        parentID            integer         The ID of the parent item
        name                string
        path                string
        metadata            json            A key/value pair array in JSON format {"keyword01" : "value01", "keyword02" : "value02"}
    '''
    params = {'q': 'findFiles'}

    if parent is not None : params['parent'] = parent
    if parentID is not None : params['parentID'] = parentID
    if name is not None : params['name'] = name
    if path is not None : params['path'] = path
    if metadata is not None : params['metadata'] = metadata

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Elements  #

def get_elementTypes( nimURL=None, apiUser=None, apiKey=None ):
    'Retrieves a dictionary of global element types'
    params = {}
    params["q"] = "getElementTypes"
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_elementType( ID=None, nimURL=None, apiUser=None, apiKey=None ):
    'Retrieves a dictionary of global element types'
    params = {}
    params["q"] = "getElementType"
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def find_elements( name=None, path=None, jobID=None, showID=None, shotID=None, assetID=None, \
                   taskID=None, renderID=None, elementTypeID=None, ext=None, metadata=None, \
                   nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves a dictionary of elements matching one of the included IDs plus name, path, elementTypeID, ext, or metadata'

    params = {}
    params["q"] = "findElements"
    if name is not None : params['name'] = name
    if path is not None : params['path'] = path
    if jobID is not None : params['jobID'] = jobID
    if showID is not None : params['showID'] = showID
    if shotID is not None : params['shotID'] = shotID
    if assetID is not None : params['assetID'] = assetID
    if taskID is not None : params['taskID'] = taskID
    if renderID is not None : params['renderID'] = renderID
    if elementTypeID is not None : params['elementTypeID'] = elementTypeID
    if ext is not None : params['ext'] = ext
    if metadata is not None : params['metadata'] = metadata
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_elements( parent='shot', parentID=None, elementTypeID=None, getLastElement=False, isPublished=False, \
                  nimURL=None, apiUser=None, apiKey=None ):
    ''' Retrieves a dictionary of elements for a particular type given parentID.
        If no elementTypeID is given will return elements for all types.
        parent is the parent of the element.  acceptable values are shot, asset, task, render.
        getLastElement will return only the last published element.
        isPublished will return only the published elements.'''

    params = {}
    params["q"] = "getElements"
    if parent is not None : params['parent'] = parent
    if parentID is not None : params['parentID'] = parentID
    if elementTypeID is not None : params['elementTypeID'] = elementTypeID
    if getLastElement is not None : params['getLastElement'] = getLastElement
    if isPublished is not None : params['isPublished'] = isPublished
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def add_element( parent='shot', parentID=None, userID=None, typeID='', path='', name='', startFrame=None, endFrame=None, \
    handles=None, isPublished=False, metadata='', nimURL=None, apiUser=None, apiKey=None ) :
    'Adds an element to an asset, shot, task, or render'
    # nimURL and apiKey are optional for Render API Key override
    params = {}
    params["q"] = "addElement"
    if parent is not None : params['parent'] = parent
    if parentID is not None : params['parentID'] = parentID
    if userID is not None : params['userID'] = userID
    if typeID is not None : params['typeID'] = typeID
    if path is not None : params['path'] = path
    if name is not None : params['name'] = name
    if startFrame is not None : params['startFrame'] = startFrame
    if endFrame is not None : params['endFrame'] = endFrame
    if handles is not None : params['handles'] = handles
    if isPublished is not None : params['isPublished'] = isPublished
    if metadata is not None : params['metadata'] = metadata
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_element(ID=None, userID=None, jobID=None, assetID=None, shotID=None, taskID=None, renderID=None, elementTypeID=None, \
    name=None, path=None, startFrame=None, endFrame=None, handles=None, isPublished=None, metadata=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    'Updates an existing element by element ID'
    # nimURL and apiKey are optional for Render API Key override
    params = {'q': 'updateElement'}

    if ID is not None : params['ID'] = ID
    if userID is not None : params['userID'] = userID
    if jobID is not None : params['jobID'] = jobID
    if assetID is not None : params['assetID'] = assetID
    if shotID is not None : params['shotID'] = shotID
    if taskID is not None : params['taskID'] = taskID
    if renderID is not None : params['renderID'] = renderID
    if elementTypeID is not None : params['elementTypeID'] = elementTypeID
    if name is not None : params['name'] = name
    if path is not None : params['path'] = path
    if startFrame is not None : params['startFrame'] = startFrame
    if endFrame is not None : params['endFrame'] = endFrame
    if handles is not None : params['handles'] = handles
    if isPublished is not None : params['isPublished'] = isPublished
    if metadata is not None : params['metadata'] = metadata

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_element(ID=None, nimURL=None, apiUser=None, apiKey=None):
    'Deletes an existing element by element ID'
    # nimURL and apiKey are optional for Render API Key override

    params = {'q': 'deleteElement'}
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  Renders  #

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

def add_render( jobID=0, itemType='shot', taskID=0, fileID=0, \
    renderKey='', renderName='', renderType='', renderComment='', \
    outputDirs=None, outputFiles=None, elementTypeID=0, start_datetime=None, end_datetime=None, \
    avgTime='', totalTime='', frame=0, nimURL=None, apiUser=None, apiKey=None ) :
    'Add a render to a task'
    # nimURL and apiKey are optional for Render API Key overrride
    params = {'q': 'addRender', 'jobID': str(jobID), 'ID': str(itemType), 'taskID': str(taskID), 'fileID': str(fileID), \
                'renderKey':str(renderKey), 'renderName':str(renderName), 'renderType':str(renderType), 'renderComment':str(renderComment), \
                'outputDirs':str(outputDirs), 'outputFiles':str(outputFiles), 'elementTypeID':str(elementTypeID), \
                'start_datetime':str(start_datetime), 'end_datetime':str(end_datetime), \
                'avgTime':str(avgTime), 'totalTime':str(totalTime), 'frames':str(frame) }
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def upload_renderIcon( renderID=None, renderKey='', img=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Upload Render Icon'
    # nimURL and apiKey are optional for Render API Key overrride
    # 2 required fields:
    #      renderID or renderKey
    #      img

    params = {}
    params["q"] = "uploadRenderIcon"
    params["renderID"] = renderID
    params["renderKey"] = renderKey
    
    if img is not None :
        img = os.path.normpath( img )
        if os.path.isfile(img) :
            params["file"] = open(img,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Image file not defined"
        return result

    if img is not None :
        result = upload(params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    return result

def get_lastShotRender( shotID=None, nimURL=None, apiUser=None, apiKey=None ):
    'Retrieves the last render added to the shot'

    params = {}
    params["q"] = "getLastShotRender"
    if shotID is not None : params['ID'] = shotID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 


#  Review  #

def get_reviewItemTypes( nimURL=None, apiUser=None, apiKey=None ):
    'Retrieves a dictionary of global review item types'
    params = {}
    params["q"] = "getReviewItemTypes"
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_taskReviewItems( taskID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the dictionary of review items for the specified taskID from the API'

    params = {}
    params["q"] = "getTaskDailies"
    if taskID is not None : params['taskID'] = taskID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

# DEPRECATED - get_taskDailies() #
def get_taskDailies( taskID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the dictionary of dailies for the specified taskID from the API'

    params = {}
    params["q"] = "getTaskDailies"
    if taskID is not None : params['taskID'] = taskID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result  

# DEPRECATED - upload_edit() #
def upload_edit( showID=None, path=None, nimURL=None, apiKey=None ) :
    'Upload Edit - 2 required fields: showID and path to movie'
    # nimURL and apiKey are optional for Render API Key overrride
    params = {}

    params["q"] = "uploadEdit"
    params["showID"] = showID

    if path is not None :
        path = os.path.normpath( path )
        if os.path.isfile(path) :
            params["file"] = open(path,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Path not defined"
        return result

    if path is not None :
        result = upload(params=params, nimURL=nimURL, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiKey=apiKey )
    return result

# DEPRECATED - upload_dailies() #
def upload_dailies( taskID=None, renderID=None, renderKey=None, itemID=None, itemType=None, path=None, submit=None, nimURL=None, apiKey=None ) :
    'Upload Dailies - 2 required fields: (taskID, renderID, or renderKey) and path to movie'
    # nimURL and apiKey are optional for Render API Key overrride
    #
    #   Required:
    #      itemID
    #      itemType - options user, job, asset, show, shot, task, render
    #               - after consolidation group, object
    #      $_FILE[]
    #
    #
    # 2 option fields for backwards compatibility:
    #      renderID or renderKey or taskID
    #      $_FILE[]
    #
    # renderKey is passed for association from render manager (deadlineID)
    # free association is made with render based on renderKey 
    #      should look up jobID and taskID from renderKey and set based on render
    #
    # if taskID is passed look up jobID and create render to associate dailies
    #
    # submit is optional to mark uploaded dailies for review - value is either: 0  or 1 

    params = {}

    params["q"] = "uploadMovie"
 
    if taskID is not None : params['taskID'] = taskID
    if renderID is not None : params['renderID'] = renderID
    if renderKey is not None : params['renderKey'] = renderKey

    if path is not None :
        path = os.path.normpath( path )
        if os.path.isfile(path) :
            params["file"] = open(path,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Path not defined"
        return result

    if submit is not None : params['submit'] = submit
    if itemID is not None : params['itemID'] = itemID
    if itemType is not None : params['itemType'] = itemType

    if path is not None :
        result = upload(params=params, nimURL=nimURL, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiKey=apiKey )

    return result

# DEPRECATED - upload_dailies() #
def upload_dailiesNote( dailiesID=None, name='', img=None, note='', frame=0, time=-1, userID=None, nimURL=None, apiKey=None ) :
    'Upload dailiesNote'
    params = {}
    params["q"] = "uploadDailiesNote"
    params["dailiesID"] = dailiesID
    params["name"] = name

    if img is not None :
        img = os.path.normpath( img )
        if os.path.isfile(img) :
            params["file"] = open(img,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Image file not defined"
        return result

    params["note"] = note
    params["frame"] = frame
    params["time"] = time
    params["userID"] = userID

    if img is not None :
        result = upload(params=params, nimURL=nimURL, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiKey=apiKey )
    return result


# Review Items #
def get_reviewItem( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the dictionary of details for the specified review item ID from the API'

    params = {}
    params["q"] = "getReviewItem"
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result 

def get_reviewItems( parentType=None, parentID=None, allChildren=None, name=None, description=None, date=None, type=None, typeID=None,
                     status=None, statusID=None, keyword=None, keywordID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves a dictionary of review items matching the search criteria - 2 required fields: parentType, parentID'
    #       Parameters          Type            Values                  Note
    # Required Parameters:
    #   parentType              string                                  user, job, dev, asset, show, shot, task, render
    #   parentID                integer                                 ID of the parent; jobID if "dev"
    # Optional Parameters:                              
    #   allChildren             integer         0 or 1                  Determines if we return review items associated with child items or not;
    #                                                                    for example, if parent is show, would return review items on the show as well as
    #                                                                    children shots, tasks, and renders
    #   name                    string                                  Filters the returned review items by the given name
    #   description             string                                  Filters the returned review items to items that contain the given string
    #   date                    date            format: yyyy-mm-dd      Filters the returned review items by the given date
    #   type                    string                                  Filters the returned review items by the given type name
    #   typeID                  integer                                 Filters the returned review items by the given typeID
    #   status                  string                                  Filters the returned review items by the given status name
    #   statusID                integer                                 Filters the returned review items by the given statusID
    #   keyword                 string                                  Filters the returned review items by the given keyword name
    #   keywordID               integer                                 Filters the returned review items by the given keywordID
    #
    # Example:
    #   .../nimAPI.php?q=getReviewItems&parentType=asset&parentID=1

    params = {}

    params["q"] = "getReviewItems"
 
    if parentType is not None : params['parentType'] = parentType
    if parentID is not None : params['parentID'] = parentID
    if allChildren is not None : params['allChildren'] = allChildren
    if name is not None : params['name'] = name
    if description is not None : params['description'] = description
    if date is not None : params['date'] = date
    if type is not None : params['type'] = type
    if typeID is not None : params['typeID'] = typeID
    if status is not None : params['status'] = status
    if statusID is not None : params['statusID'] = statusID
    if keyword is not None : params['keyword'] = keyword
    if keywordID is not None : params['keywordID'] = keywordID

    result = connect(method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
    return result

def get_reviewItemNotes( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the dictionary of notes for the specified review item ID from the API'

    params = {}
    params["q"] = "getReviewNotes"
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def upload_reviewItem( taskID=None, renderID=None, renderKey=None, itemID=None, itemType=None, path=None, submit=None, \
    name=None, description=None, reviewItemTypeID=0, reviewItemStatusID=0, keywords=None, username=None, userID=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    # nimURL and apiKey are optional for Render API Key override
    #
    #   Required:
    #      itemID       integer         the ID of the parent to attach the review item
    #      itemType     string          options user, job, asset, show, shot, task, render
    #      path         string          the path of the item to upload
    #
    #
    # 2 option fields for backwards compatibility:
    #      renderID or renderKey or taskID
    #      $_FILE[]
    #
    # renderKey is passed for association from render manager (deadlineID)
    # free association is made with render based on renderKey 
    #      should look up jobID and taskID from renderKey and set based on render
    #
    # If taskID is passed, NIM will create a new render to associate with the review item
    #
    # # Optional
    #
    # submit is optional to mark uploaded dailies for review - value is either: 0  or 1 (DEPRECATED)
    # name                string      The NIM name for the review item - if empty will use filename
    # description         string      Description for the review item
    # reviewItemTypeID    integer     The review item type ID
    # reviewItemStatusID  integer     The review status ID
    # keywords            list        ["keyword1", "keyword2"]
    # username            string      The NIM username for the owner of the review item
    # userID              integer     The userID for the owner of the review item 
    #                                 * userID takes precedence over username if both are supplied

    params = {}

    params["q"] = "uploadReviewItem"
 
    if taskID is not None : params['taskID'] = taskID
    if renderID is not None : params['renderID'] = renderID
    if renderKey is not None : params['renderKey'] = renderKey


    if path is not None :
        path = os.path.normpath( path )
        if os.path.isfile(path) :
            path = os.path.normpath( path )
            params["file"] = open(path,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Path not defined"
        return result


    if submit is not None : params['submit'] = submit
    if itemID is not None : params['itemID'] = itemID
    if itemType is not None : params['itemType'] = itemType
    if name is not None : params['name'] = name
    if description is not None : params['description'] = description
    if reviewItemTypeID is not None : params['reviewItemTypeID'] = reviewItemTypeID
    if reviewItemStatusID is not None : params['reviewItemStatusID'] = reviewItemStatusID
    if keywords is not None : params['keywords'] = json.dumps(keywords)
    if username is not None : params['username'] = username
    if userID is not None : params['userID'] = userID

    if path is not None :
        result = upload(params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def upload_reviewNote( ID=None, name='', img=None, note='', frame=0, time=-1, userID=None, \
                       nimURL=None, apiUser=None, apiKey=None ) :
    'Upload reviewNote'
    # 
    #
    #   Required:
    #       ID                  integer     The ID of the review item to attach the note
    #
    #   Optional Fields: 
    #       name                string      Image name
    #       note                string      The body of the note
    #       img                 string      Path to the image to use
    #       frame               integer     The frame number of the note
    #       time                float       The time of the note 
    #       userID              integer     The userID to associate with the note
    #       nimURL              string      optional for Render API Key overrride
    #       apiKey              string      optional for Render API Key overrride

    params = {}

    params["q"] = "uploadReviewNote"
    params["ID"] = ID
    params["name"] = name


    if img is not None :
        img = os.path.normpath( img )
        if os.path.isfile(img) :
            params["file"] = open(img,'rb')
        else :
            result = {}
            result['success'] = False
            result['error'] = "File does not exist"
            return result
    else :
        result = {}
        result['success'] = False
        result['error'] = "Image file not defined"
        return result


    params["note"] = note
    params["frame"] = frame
    params["time"] = time
    params["userID"] = userID

    if img is not None :
        result = upload(params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey)
    else :
        result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )

    return result

def get_reviewStatuses( nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'getReviewStatuses'}
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_reviewBins( context=None, contextID=None, limit=None, offset=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'getReviewBins'}
    if context is not None : params['context'] = context
    if contextID is not None : params['contextID'] = contextID
    if limit is not None : params['limit'] = limit
    if offset is not None : params['offset'] = offset
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_reviewBin( context=None, contextID=None, name=None, autoUpdateVersions=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'addReviewBin'}
    if context is not None : params['context'] = context
    if contextID is not None : params['contextID'] = contextID
    if name is not None : params['name'] = name
    if autoUpdateVersions is not None : params['autoUpdateVersions'] = autoUpdateVersions
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_reviewBin( ID=None, name=None, autoUpdateVersions=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'updateReviewBin'}
    if ID is not None : params['ID'] = ID
    if name is not None : params['name'] = name
    if autoUpdateVersions is not None : params['autoUpdateVersions'] = autoUpdateVersions
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_reviewBin( ID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'updateReviewBin'}
    if ID is not None : params['ID'] = ID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_reviewBinItem( binID=None, itemID=None, position=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'addReviewBinItem'}
    if binID is not None : params['binID'] = binID
    if itemID is not None : params['itemID'] = itemID
    if position is not None : params['position'] = position
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def remove_reviewBinItem( binID=None, itemID=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'removeReviewBinItem'}
    if binID is not None : params['binID'] = binID
    if itemID is not None : params['itemID'] = itemID
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def position_reviewBinItem( binID=None, itemID=None, position=None, nimURL=None, apiUser=None, apiKey=None ) :
    'Retrieves the list of available review statuses.'
    result=False
    params = {'q': 'positionReviewBinItem'}
    if binID is not None : params['binID'] = binID
    if itemID is not None : params['itemID'] = itemID
    if position is not None : params['position'] = position
    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

#  Timecards  #

def get_timecards( startDate=None, endDate=None, jobID=None, userID=None, username=None, \
                   taskTypeID=None, taskType=None, taskID=None, locationID=None, location=None, \
                   nimURL=None, apiUser=None, apiKey=None ):
    '''
    Retrieves a timecard, or array of timecards based on search criteria

    A user can be passed by either username or userID. If both are passed the userID will be used.
    A taskType can be passed by either the name using taskType or ID with taskTypeID. If both are passed the taskTypeID will be used.
    A location can be passed by either the name using location or ID with locationID. If both are passed the locationID will be used.

        Parameters          Type            Values                  Note
    Required:
        startDate           date            format: 2017-11-30      not required if jobID provided
        endDate             date            format: 2017-11-30      not required if jobID provided
    Optional:
        jobID               integer
        userID              integer         
        username            string
        taskTypeID          integer
        taskType            string
        taskID              integer
        locationID          integer
        location            string
    '''
    params = {'q': 'getTimecards'}

    if startDate is not None : params['startDate'] = startDate
    if endDate is not None : params['endDate'] = endDate
    if jobID is not None : params['jobID'] = jobID
    if userID is not None : params['userID'] = userID
    if username is not None : params['username'] = username
    if taskTypeID is not None : params['taskTypeID'] = taskTypeID
    if taskType is not None : params['taskType'] = taskType
    if taskID is not None : params['taskID'] = taskID
    if locationID is not None : params['locationID'] = locationID
    if location is not None : params['location'] = location

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def add_timecard( date=None, userID=None, username=None, jobID=None, taskTypeID=None, taskType=None, taskID=None, \
    startTime=None, endTime=None, hrs=None, breakHrs=None, ot=None, dt=None, \
    locationID=None, location=None, description=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Adds a new timecard
    
    A user can be passed by either username or userID. If both are passed the userID will be used.
    A taskType can be passed by either the name using taskType or ID with taskTypeID. If both are passed the taskTypeID will be used.
    A location can be passed by either the name using location or ID with locationID. If both are passed the locationID will be used.

    If a taskID is passed, the tasks values will override userID, jobID, and taskTypeID 

        Parameters          Type            Values
    Required:
        date                date            format: 2017-11-30

    Optional:
        userID              integer
        username            string
        jobID               integer
        taskTypeID          integer
        taskType            string
        taskID              integer
        startTime           string          range: 00:00:00 to 23:59:59
        endTime             string          range: 00:00:00 to 23:59:59
        hrs                 decimal         hours between start_time and end_time, including break_hrs, ot, and dt; max 24
        breakHrs            decimal         must fit within hrs
        ot                  decimal         must fit within hrs - break_hrs
        dt                  decimal         must fit within hrs - (break_hrs + ot)
        locationID          integer
        location            string
        description         string
        customKeys          dictionary {"Custom Key Name" : "Value"}
    '''
    params = {'q': 'addTimecard'}

    if date is not None : params['date'] = date
    if userID is not None : params['userID'] = userID
    if username is not None : params['username'] = username
    if jobID is not None : params['jobID'] = jobID
    if taskTypeID is not None : params['taskTypeID'] = taskTypeID
    if taskType is not None : params['taskType'] = taskType
    if taskID is not None : params['taskID'] = taskID
    if startTime is not None : params['start_time'] = startTime
    if endTime is not None : params['end_time'] = endTime
    if hrs is not None : params['hrs'] = hrs
    if breakHrs is not None : params['break_hrs'] = breakHrs
    if ot is not None : params['ot'] = ot
    if dt is not None : params['dt'] = dt
    if locationID is not None : params['locationID'] = locationID
    if location is not None : params['location'] = location
    if description is not None : params['description'] = description
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def update_timecard( timecardID=None, date=None, userID=None, username=None, jobID=None, taskTypeID=None, taskType=None, taskID=None, \
    startTime=None, endTime=None, hrs=None, breakHrs=None, ot=None, dt=None, \
    locationID=None, location=None, description=None, customKeys=None, \
    nimURL=None, apiUser=None, apiKey=None ):
    '''
    Updates an existing timecard

    A user can be passed by either username or userID. If both are passed the userID will be used.
    A taskType can be passed by either the name using taskType or ID with taskTypeID. If both are passed the taskTypeID will be used.
    A location can be passed by either the name using location or ID with locationID. If both are passed the locationID will be used.

    If a taskID is passed, the tasks values will override userID, jobID, and task_types_ID 

        Parameters          Type            Values
    Required:
        timecardID          integer         

    Optional:
        date                date            format: 2017-11-30
        userID              integer
        username            string
        jobID               integer
        taskTypeID          integer
        taskType            string
        taskID              integer
        startTime           string          range: 00:00:00 to 23:59:59
        endTime             string          range: 00:00:00 to 23:59:59
        hrs                 decimal         hours between start_time and end_time, including break_hrs, ot, and dt; max 24
        breakHrs            decimal         must fit within hrs
        ot                  decimal         must fit within hrs - break_hrs
        dt                  decimal         must fit within hrs - (break_hrs + ot)
        locationID          integer
        location            string
        description         string
        customKeys          dictionary {"Custom Key Name" : "Value"}
    '''
    params = {'q': 'updateTimecard'}

    if timecardID is not None : params['timecardID'] = timecardID
    if date is not None : params['date'] = date
    if userID is not None : params['userID'] = userID
    if username is not None : params['username'] = username
    if jobID is not None : params['jobID'] = jobID
    if taskTypeID is not None : params['taskTypeID'] = taskTypeID
    if taskType is not None : params['taskType'] = taskType
    if taskID is not None : params['taskID'] = taskID
    if startTime is not None : params['start_time'] = startTime
    if endTime is not None : params['end_time'] = endTime
    if hrs is not None : params['hrs'] = hrs
    if breakHrs is not None : params['break_hrs'] = breakHrs
    if ot is not None : params['ot'] = ot
    if dt is not None : params['dt'] = dt
    if locationID is not None : params['locationID'] = locationID
    if location is not None : params['location'] = location
    if description is not None : params['description'] = description
    if customKeys is not None : params['customKeys'] = json.dumps(customKeys)

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def delete_timecard( timecardID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Deletes an existing timecard

        Parameters          Type
    Required:
        timecardID          integer         
    '''
    params = {'q': 'deleteTimecard'}

    if timecardID is not None : params['timecardID'] = timecardID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result

def get_timecardInfo( timecardID=None, nimURL=None, apiUser=None, apiKey=None ) :
    '''
    Retrieves information for an existing timecard

        Parameters          Type
    Required:
        timecardID          integer         
    '''
    params = {'q': 'getTimecardInfo'}

    if timecardID is not None : params['timecardID'] = timecardID

    result = connect( method='get', params=params, nimURL=nimURL, apiUser=apiUser, apiKey=apiKey )
    return result


#  End

