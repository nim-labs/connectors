#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_print.py
# Version:  v4.0.47.200224
#
# Copyright (c) 2014-2020 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************


#  NIM Imports :
from . import nim_prefs as Prefs


def debug( msg='' ) :
    'Custom info printer'
    #  Get Debug setting :
    '''
    prefs=Prefs.read()
    if prefs and type(prefs)==type(dict()) :
        if 'NIM_DebugMode' in prefs :
            debug=prefs['NIM_DebugMode']
        elif 'DebugMode' in prefs :
            debug=prefs['DebugMode']
        else : debug='False'
    else : debug='False'
    '''
    debug = False
    #  Print :
    if debug =='True' and msg :
        tokens=msg.rstrip().split( '\n' )
        for toke in tokens :
            print(('NIM.D-bug ~> %s' % toke))
        if msg[-1:]=='\n' :
            print('NIM.D-bug ~>')
    return


def info( msg='' ) :
    'Custom info printer'
    tokens=msg.rstrip().split( '\n' )
    for toke in tokens :
        print(('NIM ~> %s' % toke))
    if msg[-1:]=='\n' :
        print('NIM ~>')
    return


def log( msg='' ) :
    'Custom info logger'
    tokens=msg.rstrip().split( '\n' )
    for toke in tokens :
        print(('NIM.Log ~> %s' % toke))
    if msg[-1:]=='\n' :
        print('NIM.Log ~>')
    return


def warning( msg='' ) :
    'Custom warning printer'
    tokens=msg.rstrip().split( '\n' )
    for toke in tokens :
        print(('NIM.Warning ~> %s' % toke))
    if msg[-1:]=='\n' :
        print('NIM.Warning ~>')
    return


def error( msg='' ) :
    'Custom error printer'
    if msg :
        tokens=msg.rstrip().split( '\n' )
        for toke in tokens :
            print(('NIM.Error ~> %s' % toke))
        if msg[-1:]=='\n' :
            print('NIM.Error ~>')
    else : 
        print('NIM.Error ~> An error was logged but no message was received.')
    return


#  End

