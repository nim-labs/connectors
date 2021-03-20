#!/usr/bin/env python

import os,sys

pythonVersion = sys.version_info.major

if pythonVersion == 3 :
    # Import nim_core for Python3
    from .py3.nim_flame import *

else :
    # Import nim_core for Python2
    from py2.nim_flame import *