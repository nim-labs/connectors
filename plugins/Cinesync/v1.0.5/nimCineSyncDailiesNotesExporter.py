#!/usr/bin/env python
"""
Filename: nimCinesyncDailiesNotesExporter.py

Description: This tool will provide bi-directional integration from NIM to Cinesync and back.

Note: This tool is meant to be launched from Cinesync.

Created on: 6/22/2016

Authors: Andrew Singara, Scott Ballard
Contact: support@nim-labs.com

Copyright (c) 2016 NIM Labs LLC
All rights reserved.

Use of this software is subject to the terms of the NIM Labs license
agreement provided at the time of installation or download, or which
otherwise accompanies this software in either electronic or hard copy form.
"""

__authors__ = ['Andrew Singara', 'Scott Ballard']
__version__ = '1.0.0'
__revisions__ = \
    """
    1.0.0 - Scott B - Initial development
    """

# @TODO: Make view log cross platform (linux)


import sys
import os
import ctypes
import logging
import tempfile
import traceback
import urllib
import shutil
import webbrowser
from datetime import datetime, date
import getpass
from pprint import pprint, pformat


# UPDATE [NIM_CONNECTOR_ROOT] with the path to your NIM Connectors root folder
# @TODO: Find core by being relative to this location
nim_root = ''
# Windows NIM root
if 'win32' in sys.platform:
    nim_root = 'D:/Gdrive/Studios/NIM/NIM_Connectors'
# OSX NIM root
elif 'darwin' in sys.platform:
    nim_root = '/Users/andrew/Documents/NIM Labs/Repository/nim_connectors'
# Linux NIM root
elif 'linux' in sys.platform:
    nim_root = '/Volumes/NIM_Connectors'

if nim_root not in sys.path:
    sys.path.append(nim_root)

    
# Add current dir to path
rootpath = os.path.dirname(os.path.abspath(__file__))
if rootpath not in sys.path:
    sys.path.insert(0, rootpath)

# Load PySide library
try:
    from PySide import QtCore, QtGui, QtUiTools
    import resources_rc

except ImportError as err:
    import tkMessageBox

    tkMessageBox.showerror(title='PySide load failed',
                           message='The PySide library failed to load.\n' +
                                   'Please install PySide on this machine. '
                                   'Please contact your Supervisor, IT dept. or Pipeline TD with this error.\n' +
                                   '%s' % str(err))
    sys.exit(1)

# NIM Libraries
import nim_core.nim_prefs as nimPrefs
import nim_core.nim_api as nimApi
import nim_core.UI as nimUI
import pyside_dynamic_ui
from nimDarktheme import nim_darktheme
import cinesync

# ===============================================================================
# Global Variables
# ===============================================================================
UI_FILE = os.path.join(rootpath, 'ui/NIMImportDailiesNotesExporter.ui')
UIPREFSFILE = os.path.join(rootpath, 'ui/nimCinesyncExportPreferences.ui')
NOTENAME, NOTETHUMBNAIL, NOTEFRAME, NOTENOTE = range(0, 4)
THUMBNAILSMALL = QtCore.QSize(75, 42)
THUMBNAILMEDIUM = QtCore.QSize(125, 70)
THUMBNAILLARGE = QtCore.QSize(175, 98)


class NIMCinesyncDailiesNotesExporter(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        # Member variables
        self.logfile = None
        self.log = None
        self.nimUser = None
        self.thumbnailSize = THUMBNAILMEDIUM
        self.threads = []

        pyside_dynamic_ui.loadUi(UI_FILE, self)

        # Logging action group
        self.ag = QtGui.QActionGroup(self)
        self.ag.addAction(self.actionDebug)
        self.ag.addAction(self.actionInfo)
        self.ag.addAction(self.actionWarning)
        self.ag.addAction(self.actionError)
        self.ag.addAction(self.actionCritical)
        self.actionWarning.setChecked(True)
        self.connect(self.ag, QtCore.SIGNAL("triggered(QAction *)"), self.setLogLevel)

        # Initiate logging
        self.logger('DEBUG')
        self.log.debug('Initiate: %s' % os.path.basename(__file__))

        self.log.info('Using version: %s' % __version__)

        self.getNIMUser()

        # Preferences dialog
        self.prefsWin = nimCinesyncPreferences(mainWindow=self)

        # notesTreeWidget context menu
        actionSelectAll = QtGui.QAction(QtGui.QIcon(':/ui/icons/markedForDailies.png'), "Check All", self)
        actionSelectAll.triggered.connect(self.checkAllRows)

        actionSelectNone = QtGui.QAction(QtGui.QIcon(':/ui/icons/blueblock.png'), "Check None", self)
        actionSelectNone.triggered.connect(self.uncheckAllRows)

        self.notesTreeWidget.addAction(actionSelectAll)
        self.notesTreeWidget.addAction(actionSelectNone)
        self.notesTreeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Signals
        self.actionView_Log.triggered.connect(self.viewLog)
        self.actionClear_Log.triggered.connect(self.clearLog)
        self.actionAbout.triggered.connect(self.about)
        self.actionNim_Support.triggered.connect(self.openNIMSupportURL)
        self.actionChanger_User.triggered.connect(self.changeUser)
        self.actionClose.triggered.connect(self.close)
        self.actionPreferences.triggered.connect(self.prefsWin.exec_)
        self.exportDailiesPushButton.released.connect(self.exportNotesToNim)
        self.notesTreeWidget.itemChanged.connect(self.updateExportNotesButton)

        self._restoreUserWinPrefs()

        self.syncNotesFromCinesync()

    # ===============================================================================
    # Export Notes and Annotations From Cinesync to NIM
    # ===============================================================================
    def syncNotesFromCinesync(self):
        self.log.info('Sync Notes from current Cinesync session')

        self.notesTreeWidget.clear()

        # Capture notes and annotations from current Cinesync sesssion
        media = []
        with cinesync.EventHandler() as evt:
            self.log.debug('Got notes from Cinesync session')

            if evt.is_offline():
                self.log.debug('offline session')
            else:
                self.log.debug('online session')

            if not evt or not evt.session or not evt.session.media:
                self.log.info('No media found from current Cinesync session.')
                return

            annCnt = 1
            for i, media_file in enumerate(evt.session.media):
                # if media_file.notes:
                self.log.debug('playlist #:%s' % i)
                self.log.debug('playlist data:\nname:%s\nnotes:%s\nuser data:%s' % (media_file.name,
                                                                                    media_file.notes,
                                                                                    media_file.user_data))
                data = {'name': media_file.name,
                        'notes': media_file.notes,
                        'user_data': media_file.user_data,
                        # 'saved_frame_path': None, # No thumbnail available for playlist note
                         'annotations': []}

                # Iterate by frame in sorted order
                # (iterating over a dict would otherwise have undefined order)
                for frame in sorted(media_file.annotations.keys()):
                    ann = media_file.annotations[frame]
                    if ann.notes or evt.saved_frame_path:
                        image_path = evt.saved_frame_path(media_file, frame)
                        self.log.debug('annotation # %s' % i)
                        self.log.debug('annotation data:\nname:%s\nimage:%s\nframe:%s\nnote:%s\nuser data%s' % (media_file.name,
                                                                                                                image_path,
                                                                                                                ann.frame,
                                                                                                                ann.notes,
                                                                                                                media_file.user_data))
                        temp = {'name': media_file.name,
                                'frame': ann.frame,
                                'notes': ann.notes,
                                'user_data': media_file.user_data,
                                'saved_frame_path': image_path}
                        data['annotations'].append(temp)
                        annCnt += 1
                media.append(data)


        # TEST DATA
        # media = [{'name': 'ProofCam3_NIM16.mp4',
        #           'notes': 'This shot is looking great',
        #           'user_data': 1,
        #           'saved_frame_path': None,
        #           'annotations': [{'name': 'ProofCam3_NIM16.mp4',
        #                            'frame': 1,
        #                            'notes': 'this is a note',
        #                            'user_data': 1,
        #                            'saved_frame_path': r'C:\Users\scott\Desktop\cineSync-Reviews\2016-07-12-NIMLAB2891\ProofCam3_NIM16_mp4.00009.jpg'},
        #                           {'name': 'ProofCam3_NIM16.mp4',
        #                            'frame': 99,
        #                            'notes': 'this is a note',
        #                            'user_data': 1,
        #                            'saved_frame_path': r'C:\Users\scott\Desktop\cineSync-Reviews\2016-07-12-NIMLAB2891\ProofCam3_NIM16_mp4.00009.jpg'},
        #                           {'name': 'ProofCam3_NIM16.mp4',
        #                            'frame': 16,
        #                            'notes': 'this is a note',
        #                            'user_data': 1,
        #                            'saved_frame_path': r'C:\Users\scott\Desktop\cineSync-Reviews\2016-07-12-NIMLAB2891\ProofCam3_NIM16_mp4.00009.jpg'},
        #                           ]
        #           },
        #          {'name': 'This is some test file',
        #           'notes': 'This shot is looking great',
        #           'user_data': 1,
        #           'saved_frame_path': None,
        #           'annotations': [{'name': 'ProofCam3_NIM16.mp4',
        #                            'frame': 1,
        #                            'notes': 'this is a note',
        #                            'user_data': 1,
        #                            'saved_frame_path': r'C:\Users\scott\Desktop\cineSync-Reviews\2016-07-12-NIMLAB2891\ProofCam3_NIM16_mp4.00009.jpg'},
        #                           {'name': 'ProofCam3_NIM16.mp4',
        #                            'frame': 99,
        #                            'notes': 'this is a note',
        #                            'user_data': 1,
        #                            'saved_frame_path': r'C:\Users\scott\Desktop\cineSync-Reviews\2016-07-12-NIMLAB2891\ProofCam3_NIM16_mp4.00009.jpg'},
        #                           {'name': 'ProofCam3_NIM16.mp4',
        #                            'frame': 16,
        #                            'notes': 'this is a note',
        #                            'user_data': 1,
        #                            'saved_frame_path': r'C:\Users\scott\Desktop\cineSync-Reviews\2016-07-12-NIMLAB2891\ProofCam3_NIM16_mp4.00009.jpg'},
        #                           ]
        #           },
        #          ]

        settings = QtCore.QSettings()
        self.notesTreeWidget.setIconSize(settings.value('%s/thumbnailSize' % self.nimUser, THUMBNAILLARGE))

        self.notesTreeWidget.itemDoubleClicked.connect(self.editSelectedNote)

        for data in media:
            item = QtGui.QTreeWidgetItem(self.notesTreeWidget)
            item.setForeground(NOTENAME, QtGui.QBrush(QtGui.QColor(103, 153, 204), QtCore.Qt.SolidPattern))
            item.setData(NOTENAME, QtCore.Qt.UserRole, data)
            font = QtGui.QFont('Arial', 12)
            item.setFont(NOTENAME, font)
            item.setText(NOTENAME, os.path.splitext(data.get('name'))[0])

            item.setCheckState(NOTENAME, QtCore.Qt.Unchecked)

            # Currently no thumbnail is available from Cinesync API for playlist
            item.setIcon(NOTETHUMBNAIL, QtGui.QIcon(':/ui/icons/blankImage.png'))
            item.setText(NOTENOTE, data.get('notes'))

            for aData in data.get('annotations'):
                noteItem = QtGui.QTreeWidgetItem(item)

                noteItem.setCheckState(NOTENAME, QtCore.Qt.Unchecked)

                noteItem.setData(NOTENAME, QtCore.Qt.UserRole, aData)

                noteItem.setTextAlignment(NOTENAME, QtCore.Qt.AlignHCenter)

                if aData.get('saved_frame_path'):
                    noteItem.setIcon(NOTETHUMBNAIL, QtGui.QIcon(aData.get('saved_frame_path')))
                else:
                    noteItem.setIcon(NOTETHUMBNAIL, QtGui.QIcon(':/ui/icons/noAnnotation.png'))

                noteItem.setText(NOTEFRAME, str(aData.get('frame')))
                noteItem.setTextAlignment(NOTEFRAME, (QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))

                noteItem.setText(NOTENOTE, aData.get('notes'))

        self.notesTreeWidget.expandAll()
        for i in range(0, self.notesTreeWidget.columnCount()):
            self.notesTreeWidget.resizeColumnToContents(i)

    def editSelectedNote(self, widget, column):
        if column != NOTENOTE:
            return

        dialog = QtGui.QDialog(widget.treeWidget())
        ui = NotesDialog()
        ui.setupUi(dialog)
        ui.setNotes(widget.text(NOTENOTE))
        if dialog.exec_():
            notes = ui.ctl_Notes.toPlainText()
            data = widget.data(NOTENAME, QtCore.Qt.UserRole)

            if 'notes' in data:
                data['notes'] = notes
                widget.setData(NOTENAME, QtCore.Qt.UserRole, data)
                widget.setText(NOTENOTE, notes)

    def exportNotesToNim(self):
        """Export notes back to NIM from connector."""
        self.log.info('Exporting Notes to NIM')

        try:
            # Find number of children
            itemCnt = 0
            for i in range(0, self.notesTreeWidget.topLevelItemCount()):
                topItem = self.notesTreeWidget.topLevelItem(i)
                if topItem.checkState == QtCore.Qt.Checked:
                    itemCnt += 1

                childCount = topItem.childCount()
                for index in range(0, childCount):
                    child = topItem.child(index)
                    if child.checkState(NOTENAME) == QtCore.Qt.Checked:
                        itemCnt += 1

            self.progWin = self.progressWindow('Exporting Notes To NIM')
            self.progWin.setMinimum(0)
            self.progWin.setMaximum(itemCnt + 1)

            # Get all items from notesTreeWidget
            cnt = 0
            for i in range(0, self.notesTreeWidget.topLevelItemCount()):
                topItem = self.notesTreeWidget.topLevelItem(i)
                if topItem.checkState(NOTENAME) == QtCore.Qt.Checked:
                    cnt += 1
                    data = topItem.data(NOTENAME, QtCore.Qt.UserRole)
                    nimApi.upload_dailiesNote(dailiesID=data.get('user_data'),
                                              name=os.path.splitext(data.get('name'))[0],
                                              # img=data.get('saved_frame_path'),
                                              frame=-1,
                                              # time=.1,
                                              userID=self.nimUserId,
                                              note=data.get('notes'))

                    self.log.info('Created Playlist Note:\nDailies ID:%sName:%s\n' % (data.get('user_data'),
                                                                                      os.path.splitext(data.get('name'))[0],) +
                                  'image:%s\nuserID:%snote:%s' % (data.get('saved_frame_path'),
                                                                                     # data.get('frame'),
                                                                                     # float(data.get('frame')) / 24.0,
                                                                                     self.nimUserId,
                                                                                     data.get('notes')))
                    self.progWin.setLabelText('Exporting note %s of %s' % (cnt, itemCnt))
                    self.progWin.setValue(self.progWin.value() + 1)

                childCount = topItem.childCount()
                for index in range(0, childCount):
                    child = topItem.child(index)
                    if child.checkState(NOTENAME) == QtCore.Qt.Checked:
                        cnt += 1
                        data = child.data(NOTENAME, QtCore.Qt.UserRole)
                        self.log.debug('annotation data: %s' % data)
                        nimApi.upload_dailiesNote(dailiesID=data.get('user_data'),
                                                  name=os.path.splitext(data.get('name'))[0],
                                                  img=data.get('saved_frame_path'),
                                                  frame=data.get('frame'),
                                                  time=float(data.get('frame')) / 24.0,
                                                  userID=self.nimUserId,
                                                  note=data.get('notes'))

                        self.log.info('Created frame Note:\nDailies ID:%sName:%s\n' % (data.get('user_data'),
                                                                                       os.path.splitext(data.get('name'))[0]) +
                                      'image:%s\nframe:%s\ntime:%s\nuserID:%snote:%s' % (data.get('saved_frame_path'),
                                                                                         data.get('frame'),
                                                                                         float(data.get('frame')) / 24.0,
                                                                                         self.nimUserId,
                                                                                         data.get('notes')))

                        self.progWin.setLabelText('Exporting note/annotation %s of %s' % (cnt, itemCnt))
                        self.progWin.setValue(self.progWin.value() + 1)

            self.notesTreeWidget.clear()
            self.log.info('Exported %s Cinesync notes to NIM' % cnt)
            self.updateExportNotesButton()
            QtGui.QMessageBox.information(self,
                                          "Success!",
                                          '<h2>%s dailies notes have been created in NIM!</h2>' % cnt)
            self.deleteLater()

        except Exception as err:
            self.errorDialog(err, 'Failed to export dailies notes to NIM.')

        finally:
            self.progWin.close()

    def checkAllRows(self):
        """Check all rows in notesTreeWidget"""

        for i in range(0, self.notesTreeWidget.topLevelItemCount()):
            topItem = self.notesTreeWidget.topLevelItem(i)
            topItem.setCheckState(NOTENAME, QtCore.Qt.Checked)
            childCount = topItem.childCount()
            for index in range(0, childCount):
                child = topItem.child(index)
                child.setCheckState(NOTENAME, QtCore.Qt.Checked)

    def uncheckAllRows(self):
        """Check all rows in notesTreeWidget"""

        for i in range(0, self.notesTreeWidget.topLevelItemCount()):
            topItem = self.notesTreeWidget.topLevelItem(i)
            topItem.setCheckState(NOTENAME, QtCore.Qt.Unchecked)
            childCount = topItem.childCount()
            for index in range(0, childCount):
                child = topItem.child(index)
                child.setCheckState(NOTENAME, QtCore.Qt.Unchecked)

    def updateExportNotesButton(self):
        """When user checks an item then turn button green, else red."""

        match = False
        for i in range(0, self.notesTreeWidget.topLevelItemCount()):
            topItem = self.notesTreeWidget.topLevelItem(i)
            state = topItem.checkState(NOTENAME)
            if state == QtCore.Qt.Checked:
                match = True
                break
            childCount = topItem.childCount()
            for index in range(0, childCount):
                child = topItem.child(index)
                state = child.checkState(NOTENAME)
                if state == QtCore.Qt.Checked:
                    match = True
                    break

        if match:
            self.exportDailiesPushButton.setEnabled(True)
            self.exportDailiesPushButton.setStyleSheet('border: 2px solid green;font: 75 12pt "Arial";')
        else:
            self.exportDailiesPushButton.setStyleSheet('border: 2px solid red;font: 75 12pt "Arial";')
            self.exportDailiesPushButton.setEnabled(False)

    def errorDialog(self, err, message):
        self.log.error(traceback.print_exc())
        self.log.error(str(err))
        QtGui.QMessageBox.critical(self,
                                   "Error!",
                                   '%s\n%s' % (message, str(err)))
        return

    def getNIMUser(self):
        prefs = nimPrefs.read()
        self.nimUser = prefs.get('NIM_User')
        self.nimUserId = nimApi.get_userID(self.nimUser)
        self.log.debug('User set to: %s' % self.nimUser)
        if not self.nimUser:
            self.changeUser()

    def changeUser(self):
        nimUI.GUI().update_user()
        if not self.getNIMUser():
            self.getNIMUser()

        self.resetUi()
        self._restoreUserWinPrefs()

    def resetUi(self, valid=True):
        """Set the UI back to its default state
        @param valid: bool - True reset UI widgets, False disable UI
        """
        if valid:
            self.log.debug('Reset UI widgets')
            self.setWindowTitle('NIM Export Dailies Notes - v%s - NIM User: %s' % (__version__, self.nimUser))

        else:
            pass

    def openNIMSupportURL(self):
        webbrowser.open('http://nim-labs.com/support/')

    def progressWindow(self, comment):
        progWin = QtGui.QProgressDialog(comment, None, 0, 100, parent=self)
        # font = QtGui.QFont('Arial', 24)
        # progWin.setFont(font)
        progWin.setWindowModality(QtCore.Qt.WindowModal)
        progWin.forceShow()
        QtGui.QApplication.processEvents()

        return progWin

    def about(self):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setText('%s\nVersion: %s\n\n%s' % (__doc__, __version__, __revisions__))
        msgBox.setWindowTitle('About')
        msgBox.setIconPixmap(QtGui.QPixmap(':ui/icons/nimLogo_small.png'))
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        msgBox.exec_()

    def logger(self, level):
        # Create log
        self.logfile = "%s/NIM/logs/nimCinesyncConnector/%s/%s_%s.log" % (tempfile.gettempdir(),
                                                                          date.today(),
                                                                          getpass.getuser(),
                                                                          datetime.now().strftime('%I%M%p'))
        self.createLogFile(self.logfile)

        # logging
        self.log = logging.getLogger('cinesync')
        self.setLogLevel(level)
        self.log.propagate = 0  # So that console messages wont propagate up to other loggers

        # create file handler logConsole logs even debug messages
        logHandle = logging.FileHandler(self.logfile)

        # create console handler with a higher log level
        logConsole = logging.StreamHandler()

        # create formatter and add it to the handlers
        formatter = logging.Formatter("%(levelname)s: %(asctime)s - %(message)s", "%Y-%m-%d %H:%M%p")
        logHandle.setFormatter(formatter)
        logConsole.setFormatter(formatter)

        # add the handlers to the log
        self.log.addHandler(logHandle)
        self.log.addHandler(logConsole)

    def closeEvent(self, event):
        self.log.debug('Closing Cinesync connector')
        self._saveUserWinPrefs()
        QtGui.QMainWindow.closeEvent(self, event)

    def createLogFile(self, logfile):
        """Create log file"""
        try:
            if not os.path.exists(os.path.dirname(logfile)):
                os.makedirs(os.path.dirname(logfile))
            if not os.path.exists(logfile):
                open(logfile, 'w').close()
            else:
                os.remove(logfile)

        except IOError as err:
            print'Couldnt open log file:', err
            return

    def viewLog(self):
        if not os.path.exists(self.logfile):
            raise IOError("Can't find log file: " + self.logfile)
            return
        if 'win32' in sys.platform:
            os.system('notepad.exe %s' % self.logfile)
        elif 'darwin' in sys.platform:
            os.system('open -a /Applications/TextEdit.app/Contents/MacOS/TextEdit %s' % self.logfile)
        elif 'linux' in sys.platform:
            # @TODO: Implement Linux log view handling
            pass

    def clearLog(self):
        if not os.path.exists(self.logfile):
            raise IOError('Cant find log file:' + self.logfile)
        open(self.logfile, 'w').close()

    def setLogLevel(self, level):
        if isinstance(level, QtGui.QAction):
            level = level.text().upper()

        log_levels = {'DEBUG': logging.DEBUG,
                      'INFO': logging.INFO,
                      'WARNING': logging.WARNING,
                      'ERROR': logging.ERROR,
                      'CRITICAL': logging.CRITICAL}

        if level in log_levels:
            self.log.setLevel(log_levels.get(level))

    def _saveUserWinPrefs(self):
        settings = QtCore.QSettings()
        user = self.nimUser

        settings.setValue("%s/geometry" % user, self.saveGeometry())
        settings.setValue("%s/windowState" % user, self.saveState())
        value = self.ag.actions().index(self.ag.checkedAction())
        settings.setValue('%s/logDebugLevel' % user, value)

        self.log.info('Saved all user preferences')

    def _restoreUserWinPrefs(self):
        """Restore user window preferences"""

        settings = QtCore.QSettings()
        user = self.nimUser

        geo = settings.value("%s/geometry" % user)
        if geo:
            self.restoreGeometry(geo)
        state = settings.value("%s/windowState" % user)
        if state:
            self.restoreState(state)

        # Thumbnail size
        value = settings.value('%s/thumbnailSize' % user, THUMBNAILLARGE)
        if value == THUMBNAILSMALL:
            self.actionSmall.setChecked(True)

        elif value == THUMBNAILMEDIUM:
            self.actionMedium.setChecked(True)

        elif value == THUMBNAILLARGE:
            self.actionLarge.setChecked(True)
        else:
            self.actionMedium.setChecked(True)

        self.thumbnailSize = value

        # Debug values
        value = int(settings.value('%s/logDebugLevel' % user, 1))
        if value == 0:
            self.actionDebug.setChecked(True)
            self.setLogLevel('DEBUG')
        elif value == 1:
            self.actionInfo.setChecked(True)
            self.setLogLevel('INFO')
        elif value == 2:
            self.actionWarning.setChecked(True)
            self.setLogLevel('WARNING')
        elif value == 3:
            self.actionError.setChecked(True)
            self.setLogLevel('ERROR')
        else:
            self.actionCritical.setChecked(True)
            self.setLogLevel('CRITICAL')

        self.log.debug('User preferences restored')


class fetchThumbnail(QtCore.QThread):
    thumbnailURL = QtCore.Signal(str)

    def __init__(self, url):
        QtCore.QThread.__init__(self)
        self.url = url

    def run(self):
        icon = self.url
        # Store icon in temp directory
        dstDir = '%s/NIM/thumbnails' % tempfile.gettempdir()
        if not os.path.exists(dstDir):
            os.makedirs(dstDir)
        dsticon = ('%s/%s' % (dstDir, os.path.basename(icon))).replace('\\', '/')
        urllib.urlretrieve(icon, dsticon)
        self.thumbnailURL.emit(dsticon)


class nimTableWidgetItem(QtGui.QTableWidgetItem):
    def __init__(self, text):
        super(nimTableWidgetItem, self).__init__(text)

    def setThumbnail(self, thumbnailPath):
        """
        Set the stylesheet for the QTableWidgetItem
        @param thumbnailPath: str - path to the thumbnail on disk
        @return: None
        """

        icon = QtGui.QIcon(thumbnailPath)
        self.setIcon(icon)

class NotesDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 300)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ctl_Label = QtGui.QLabel(Dialog)
        self.ctl_Label.setStyleSheet("font: 75 12pt \"Arial\";\n""color: rgb(30, 167, 224);")
        self.ctl_Label.setObjectName("ctl_Label")
        self.verticalLayout_2.addWidget(self.ctl_Label)
        self.ctl_Notes = QtGui.QPlainTextEdit(Dialog)
        self.ctl_Notes.setObjectName("ctl_Notes")
        self.verticalLayout_2.addWidget(self.ctl_Notes)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Notes Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.ctl_Label.setText(QtGui.QApplication.translate("Dialog", "Edit Note", None, QtGui.QApplication.UnicodeUTF8))

    def setNotes(self, value):
        self.ctl_Notes.setPlainText(value)


# ===============================================================================
# Preference Dialog
# ===============================================================================
class nimCinesyncPreferences(QtGui.QDialog):
    def __init__(self, mainWindow, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.mainWindow = mainWindow
        self.setModal(True)

        pyside_dynamic_ui.loadUi(UIPREFSFILE, self)
        self.setModal(True)

        # Logging action group
        self.tg = QtGui.QButtonGroup(self)
        self.tg.addButton(self.smallThumbnailRadioButton)
        self.tg.addButton(self.medThumbnailRadioButton)
        self.tg.addButton(self.largeThumbnailRadioButton)
        self.tg.buttonReleased.connect(self.changeThumbnailSize)

        settings = QtCore.QSettings()

        value = settings.value('%s/thumbnailSize' % self.mainWindow.nimUser)
        if value == THUMBNAILLARGE:
            self.largeThumbnailRadioButton.setChecked(True)

        elif value == THUMBNAILSMALL:
            self.smallThumbnailRadioButton.setChecked(True)

        else:
            self.medThumbnailRadioButton.setChecked(True)

        # Signals
        self.resetPushButton.released.connect(self.resetToDefault)
        self.tg.buttonReleased.connect(self.__updatePrefs)

        self.__updatePrefs()

    def changeThumbnailSize(self, checkedButton):
        settings = QtCore.QSettings()
        user = self.mainWindow.nimUser

        if checkedButton.objectName() == 'smallThumbnailRadioButton':
            self.mainWindow.thumbnailSize = THUMBNAILSMALL
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILSMALL)

        elif checkedButton.objectName() == 'medThumbnailRadioButton':
            self.mainWindow.thumbnailSize = THUMBNAILMEDIUM
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILMEDIUM)

        elif checkedButton.objectName() == 'largeThumbnailRadioButton':
            self.mainWindow.thumbnailSize = THUMBNAILLARGE
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILLARGE)

    def resetToDefault(self):
        self.medThumbnailRadioButton.setChecked(True)

        self.__updatePrefs()

    def __updatePrefs(self):
        user = self.mainWindow.nimUser
        settings = QtCore.QSettings()

        button = self.tg.checkedButton().objectName()
        if button == 'largeThumbnailRadioButton':
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILLARGE)
        elif button == 'smallThumbnailRadioButton':
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILSMALL)
        else:
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILMEDIUM)


# ===============================================================================
# MAIN
# ===============================================================================
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    # Set dark theme
    nim_darktheme()

    SERVER_ROOT = 'http://%s' % nimPrefs.get_url().split('/')[2]

    # Allow Windows to display the application icon instead of the Python icon on taskbar
    if 'win32' in sys.platform:
        myappid = u'nim.nimCinesyncConnector.%s' % __version__  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Establish connection to NIM
    nimPrefs.mk_default(notify_success=True)

    # Used to store user preferences
    app.setOrganizationName("NIM Labs")
    app.setOrganizationDomain("http://nim-labs.com/")
    app.setApplicationName("NIMCinesyncDailiesNotesExporter")

    win = NIMCinesyncDailiesNotesExporter()
    win.show()
    win.raise_()
    sys.exit(app.exec_())
