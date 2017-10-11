#!/usr/bin/env python
#******************************************************************************
#
# Filename: nim_hiero.py
# Version:  v2.7.26.171011
#
# Copyright (c) 2017 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

import os, sys
import hiero.core
from hiero.core import nuke
from hiero.exporters import FnShotExporter
from hiero.exporters import FnShotProcessor
from hiero.exporters import FnNukeShotExporter
from hiero.exporters import FnNukeShotExporterUI
from hiero.exporters import FnTranscodeExporter

from PySide import QtGui, QtCore

class NIM_Exporter(FnNukeShotExporterUI.NukeShotExporterUI) :
    
    self.head_offset=1000
    
    def __init__(self) :
        super(NIM_Exporter, self).__init__()
        
        return
    
    def output_path(self) :
        ''
        
        return

#  End Class


#  END

