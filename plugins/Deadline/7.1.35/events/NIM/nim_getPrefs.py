'''
Copyright (c) 2015, NIM Labs LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
'''
#  General Imports :
import os, sys

def getNimScriptPath():
    #  NIM Imports :
    _prefs={}
    prefs_dirName='.nim'
    prefs_fileName='prefs.nim'

    'Gets the NIM home directory'
    userHome=os.path.expanduser( '~' )
    if userHome.endswith( 'Documents' ) :
        userHome=userHome[:-9]
    user_home = os.path.normpath( os.path.join( userHome, prefs_dirName ) )

    # TODO - read path from prefs file:
    prefsFile=os.path.normpath( os.path.join( user_home, prefs_fileName ) )
    print 'NIM ~> NIM preferences:     %s' % prefsFile

    'Reads and stores preferences'
    #  Create preferences, if necessary :
    prefsFound = os.path.exists( prefsFile )
    print 'NIM ~> NIM preferences found:     %s' % prefsFound

    scriptFindPath=True
    scriptInputPath=''
    scriptPathValid=False
    loadNIM=False

    if not prefsFound :
        #  Prompt user to input Scripts Path :
        '''
        msg='Please input the NIM Scripts Path :\n'
        
        while scriptFindPath:
            scriptInputPath=gui.InputDialog( msg )
            print 'NIM ~> NIM Scripts Set to:     %s' % scriptInputPath
            print 'NIM ~> Validating Path:'
            scriptPathValid = os.path.exists(os.path.join(scriptInputPath,"nim_core"))
            if not scriptPathValid:
                userInput=gui.QuestionDialog( 'Path to NIM Scripts is Invalid:\n %s \nTry again?' % scriptInputPath )
                if userInput :
                    userInput='OK'
                else:
                    scriptFindPath = False
                    print "Exiting without setting NIM Script Path"

            else:
                scriptFindPath = False
                loadNIM=True
        '''
        return False
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
            prefs=dict( [(k,v) for k,v in _prefs.items() if len(k)>0])
            if _prefs and 'NIM_Scripts' in _prefs.keys() :
                scriptInputPath=_prefs['NIM_Scripts']
                loadNIM=True
            else:
                print "NIM Scripts location not found in preference file."
                loadNIM=False

        except Exception, e :
            print "Unable to read preferences."
            loadNIM=False


    if loadNIM:
        '''
        nim_path=scriptInputPath
        if not nim_path in sys.path :
            sys.path.append( nim_path )
            print 'NIM ~> Appended NIM Python directory to system paths...\nNIM ~>     %s' % nim_path

        print 'NIM ~> Importing NIM Libraries'

        #import nim_core.nim_api as Api
        #import nim_core.nim_file as F
        #import nim_core.nim_print as P
        #import nim_core.nim_c4d as C
        import nim_core.nim_prefs as Prefs

        print 'NIM ~> Loading NIM Variables'

        #  Variables :
        version='v0_5_6.r01'

        print 'NIM ~> Reading NIM Preferences'
        _prefs=Prefs.read()

        if not _prefs:
            return False
        else:
            return _prefs
        '''

        return scriptInputPath