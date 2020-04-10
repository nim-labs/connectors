#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_core/nim_hiero.py
# Version:  v4.0.49.200410
#
# Copyright (c) 2014-2020 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import os,sys

pythonVersion = sys.version_info.major

if pythonVersion == 3 :
    # Import nim_core for Python3
    from .py3.nim_hiero import *

else :
    # Import nim_core for Python2
    from py2.nim_hiero import *