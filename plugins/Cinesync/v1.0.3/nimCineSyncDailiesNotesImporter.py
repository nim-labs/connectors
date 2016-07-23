#!/usr/bin/env python
"""
Filename: nimCinesyncDailiesNotesImporter.py

Description: This tool will provide bi-directional integration from NIM to Cinesync and back.

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
__version__ = '1.0.3'
__revisions__ = \
    """
    1.0.3 - Scott B - Split import and export tool into two separate tools
                      Removed need for NIM path in sys.path. Connector is self-contained
    1.0.2 - Scott B - Fixed closing of window when importing into Cinesync
                      Added ability to export Notes from Cinesync to NIM
    1.0.1 - Scott B - Fixed OSX temp dir pathing
    1.0.0 - Scott B - Initial development
    """

# @TODO: Make view log cross platform
# @TODO: Make taskbar icon cross platform
# @TODO: Present NIM config window if connection cannot be made to server
# @TODO: For some reason when switching users through the API, on the second switch the API slows considerably


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
UI_FILE = os.path.join(rootpath, 'ui/NIMImportDailiesNotesImporter.ui')
UIPREFSFILE = os.path.join(rootpath, 'ui/nimCinesyncImportPreferences.ui')
ASSETTAB, SHOTTAB = range(0, 2)
TASKNAME, TASKARTIST, TASKDESC = range(0, 3)
THUMBNAIL, NAME, MARKREVIEW, RENDERTIME, FRAMES, COMMENT = range(0, 6)
NOTENAME, NOTETHUMBNAIL, NOTEFRAME, NOTENOTE = range(0, 4)
THUMBNAILSMALL = QtCore.QSize(75, 42)
THUMBNAILMEDIUM = QtCore.QSize(125, 70)
THUMBNAILLARGE = QtCore.QSize(175, 98)

# Sample data from NIM
# Output:
# "ID":"586",
# "name":"TEST2 ",
# "filepath":null,
# "iconPath":"\/media\/jobs\/2588\/dailies\/14941\/OOPS_011_comp_v10_NIM795.jpg",
# "dailiesMP4":"media\/jobs\/2588\/dailies\/14941\/OOPS_011_comp_v10_NIM795_source.mov",
# "submitted":"0",
# "renderID":"795",
# "renderName":"OOPS_011_comp_v10",
# "frames":"2377",
# "avgTime":null,
# "totalTime":null,
# "renderDate":"2016-06-18 17:28:23",
# "renderIconPath":"\/media\/jobs\/2588\/dailies\/14941\/OOPS_011_comp_v10_NIM795.jpg"


class NIMCinesyncDailiesNotesImporter(QtGui.QMainWindow):
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

        # Signals
        self.actionView_Log.triggered.connect(self.viewLog)
        self.actionClear_Log.triggered.connect(self.clearLog)
        self.importDailiesPushButton.clicked.connect(self.importDailiesIntoCinesync)
        self.actionAbout.triggered.connect(self.about)
        self.actionNim_Support.triggered.connect(self.openNIMSupportURL)
        self.actionChanger_User.triggered.connect(self.changeUser)
        self.resetButton.released.connect(self.resetUi)
        self.jobsComboBox.currentIndexChanged.connect(self.toggleExecuteButton)
        self.showsComboBox.currentIndexChanged.connect(self.toggleExecuteButton)
        self.shotsComboBox.currentIndexChanged.connect(self.toggleExecuteButton)
        self.assetsComboBox.currentIndexChanged.connect(self.toggleExecuteButton)
        self.tasksTableWidget.itemSelectionChanged.connect(self.toggleExecuteButton)
        self.dailiesTableWidget.itemSelectionChanged.connect(self.toggleExecuteButton)
        self.actionClose.triggered.connect(self.close)
        self.actionPreferences.triggered.connect(self.prefsWin.exec_)

        self.updateJobs()
        self.toggleExecuteButton()

        self._restoreUserWinPrefs()

    # ===============================================================================
    # Import Dailies from NIM to Cinesync
    # ===============================================================================
    def importDailiesIntoCinesync(self):
        self.log.info('Importing Dailies to Cinesync')

        settings = QtCore.QSettings()

        # Get selected Dailies
        items = self.dailiesTableWidget.selectedItems()

        exportItems = []
        for item in items:
            if item.column() == 0:
                exportItems.append(item)

        self.progWin = self.progressWindow('Fetching Dailies Media')
        self.progWin.setMinimum(0)
        self.progWin.setMaximum(len(exportItems) + 1)
        try:
            dailiesMedia = []
            for exportItem in exportItems:
                data = exportItem.data(QtCore.Qt.UserRole)

                if not data.get('dailiesMP4'):
                    self.log.warning('Dailies (%s #%s) is missing dailies media, skipping..' % (data.get('name'),
                                                                                                data.get('ID')))
                    continue

                dailiesURL = '%s/%s' % (SERVER_ROOT, data.get('dailiesMP4'))
                self.log.debug('dailies URL: %s' % dailiesURL)
                tempDir = None
                # Store media in temp directory
                if 'win32' in sys.platform:
                    tempDir = settings.value("%s/windowsTempDir" % self.nimUser)

                elif 'darwin' in sys.platform:
                    tempDir = settings.value("%s/osxTempDir" % self.nimUser)

                elif 'linux' in sys.platform:
                    tempDir = settings.value("%s/linuxTempDir" % self.nimUser)

                dstDir = '%s/NIM/%s' % (tempDir, os.path.dirname(data.get('dailiesMP4')))

                if not os.path.exists(dstDir):
                    self.log.debug('Creating folder: %s' % dstDir)
                    os.makedirs(dstDir)
                dstMedia = ('%s/%s' % (dstDir, os.path.basename(dailiesURL))).replace('\\', '/')

                # Remove existing media
                if os.path.exists(dstMedia):
                    os.remove(dstMedia)
                    self.log.debug('Remove existing media: %s' % dstMedia)

                self.log.debug('Fetching dailies media: %s' % dstMedia)
                self.progWin.setLabelText('Fetching: %s' % data.get('name'))
                self.progWin.setValue(self.progWin.value() + 1)

                urllib.urlretrieve(dailiesURL, dstMedia)
                dailiesMedia.append({'id': data.get('ID'), 'media_path': dstMedia})
                self.log.debug('Retrieved dailies media: %s' % dstMedia)

            if not dailiesMedia:
                self.errorDialog('', '<h2>There is no media available. Please reselect dailies items.</h2>')
                return

            self.log.debug(
                'Sending media files to Cinesync: %s' % '\n'.join([x.get('media_path') for x in dailiesMedia]))

            # Create the session and add media from command-line arguments
            session = cinesync.Session()
            media = []
            for data in dailiesMedia:
                obj = cinesync.MediaFile(data.get('media_path'))
                obj.user_data = data.get('id')
                media.append(obj)

            session.media = media

            # Ask cineSync to add the session to its current state
            cinesync.commands.open_session(session)
            self.log.debug('Launched Cinesync session')

        except Exception as err:
            self.errorDialog(err, 'Failed to launch Cinesync session.')

        finally:
            self.progWin.close()
            settings = QtCore.QSettings()
            if settings.value('%s/closeConnector' % self.nimUser, True):
                self.deleteLater()

    def updateJobs(self):
        """Update the jobs comboBox with all NIM jobs"""

        self.resetUi()
        self.jobsComboBox.clear()

        try:
            user = self.nimUser
            userId = nimApi.get_userID(user)
            jobs = nimApi.get_jobs(userID=userId)

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Jobs</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support (support@nim-labs.com)</p>')
            return

        self.jobsComboBox.addItem(QtGui.QIcon(':/ui/icons/block.png'), 'Select Job', 0)

        for jobName, jobID in jobs.iteritems():
            self.jobsComboBox.addItem(QtGui.QIcon(':/ui/icons/jobs.png'), jobName, jobID)

        settings = QtCore.QSettings()
        job = settings.value('%s/currentJob' % self.nimUser, '')
        index = self.jobsComboBox.findText(job)
        if index >= 0:
            self.jobsComboBox.setCurrentIndex(index)

        self.jobsComboBox.currentIndexChanged.connect(self.updateShows)
        self.jobsComboBox.currentIndexChanged.connect(self.updateAssets)
        self.updateShows()

    def updateShows(self):
        """Update the shows comboBox with all shows for selected Job"""

        self.showsComboBox.setEnabled(True)
        self.showsComboBox.clear()

        try:
            jobId = self.jobsComboBox.itemData(self.jobsComboBox.currentIndex())
            shows = nimApi.get_shows(jobID=jobId)
            if not shows:
                return

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Shows</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support' +
                             '(support@nim-labs.com)</p>')
            return

        self.showsComboBox.addItem(QtGui.QIcon(':/ui/icons/block.png'), 'Select Show', 0)

        for show in shows:
            self.showsComboBox.addItem(QtGui.QIcon(':/ui/icons/shows.png'), show.get('showname'), show.get('ID'))

        settings = QtCore.QSettings()
        show = settings.value('%s/currentShow' % self.nimUser, '')
        index = self.showsComboBox.findText(show)
        if index >= 0:
            self.showsComboBox.setCurrentIndex(index)

        self.showsComboBox.currentIndexChanged.connect(self.updateShots)
        self.shotAssetTabWidget.currentChanged.connect(self.updateTasks)
        self.updateAssets()
        self.updateShots()

    def updateShots(self):
        """Update the shots comboBox with all shots for selected Show"""

        self.shotsComboBox.setEnabled(True)
        self.shotsComboBox.clear()

        try:
            showId = self.showsComboBox.itemData(self.showsComboBox.currentIndex())

            # Get Shots
            shots = nimApi.get_shots(showID=showId)

            if not shots:
                return

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Shots</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support' +
                             '(support@nim-labs.com)</p>')
            return

        self.shotsComboBox.addItem(QtGui.QIcon(':/ui/icons/block.png'), 'Select Shot', 0)

        for show in shots:
            self.shotsComboBox.addItem(QtGui.QIcon(':/ui/icons/shot.png'),
                                       show.get('name'),
                                       {'type': 'Shot', 'ID': show.get('ID')})

        settings = QtCore.QSettings()
        show = settings.value('%s/currentShot' % self.nimUser, '')
        index = self.shotsComboBox.findText(show)
        if index >= 0:
            self.shotsComboBox.setCurrentIndex(index)

        self.shotsComboBox.currentIndexChanged.connect(self.updateTasks)
        self.shotsComboBox.currentIndexChanged.connect(self.updateShotThumbnail)
        self.updateTasks()
        self.updateShotThumbnail()

    def updateAssets(self):
        """Update the assets comboBox with all assets for selected Show"""

        self.assetsComboBox.setEnabled(True)
        self.assetsComboBox.clear()

        try:
            jobId = self.jobsComboBox.itemData(self.jobsComboBox.currentIndex())

            # Get Assets
            assets = nimApi.get_assets(jobID=jobId)

            if not assets:
                return

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Assets</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support' +
                             '(support@nim-labs.com)</p>')
            return

        self.assetsComboBox.addItem(QtGui.QIcon(':/ui/icons/block.png'), 'Select Asset', 0)

        for asset in assets:
            self.assetsComboBox.addItem(QtGui.QIcon(':/ui/icons/asset.png'),
                                        asset.get('name'),
                                        {'type': 'Asset', 'ID': asset.get('ID')})

        settings = QtCore.QSettings()
        show = settings.value('%s/currentAsset' % self.nimUser, '')
        index = self.assetsComboBox.findText(show)
        if index >= 0:
            self.assetsComboBox.setCurrentIndex(index)

        self.assetsComboBox.currentIndexChanged.connect(self.updateTasks)
        self.assetsComboBox.currentIndexChanged.connect(self.updateAssetThumbnail)
        self.updateTasks()
        self.updateAssetThumbnail()

    def updateTasks(self):
        """Update the tasks comboBox with all Tasks for selected Shot or Asset"""

        self.tasksTableWidget.setEnabled(True)
        self.tasksTableWidget.clearContents()
        self.tasksTableWidget.setRowCount(0)

        try:
            tasks = None
            # Shot Task
            if self.shotAssetTabWidget.currentIndex() == SHOTTAB:
                shot = self.shotsComboBox.itemData(self.shotsComboBox.currentIndex())
                if not shot:
                    return

                tasks = nimApi.get_taskInfo('SHOT', shot.get('ID'))

            # Asset Task
            elif self.shotAssetTabWidget.currentIndex() == ASSETTAB:
                asset = self.assetsComboBox.itemData(self.assetsComboBox.currentIndex())
                if not asset:
                    return
                tasks = nimApi.get_taskInfo('ASSET', asset.get('ID'))

            if not tasks:
                return

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Tasks</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support' +
                             '(support@nim-labs.com)</p>')
            return

        self.tasksTableWidget.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            for key, val in task.iteritems():
                if key == 'taskName':
                    col = TASKNAME
                    item = QtGui.QTableWidgetItem(QtGui.QIcon(':/ui/icons/tasks.png'), val)
                    item.setData(QtCore.Qt.UserRole, task)
                    self.tasksTableWidget.setItem(row, col, item)

                elif key == 'username':
                    col = TASKARTIST
                    item = QtGui.QTableWidgetItem(QtGui.QIcon(':/ui/icons/user.png'), val)
                    item.setData(QtCore.Qt.UserRole, task)
                    self.tasksTableWidget.setItem(row, col, item)

                elif key == 'taskDesc':
                    col = TASKDESC
                    item = QtGui.QTableWidgetItem(val)
                    item.setData(QtCore.Qt.UserRole, task)
                    self.tasksTableWidget.setItem(row, col, item)

        self.tasksTableWidget.itemSelectionChanged.connect(self.updateDailies)
        self.updateDailies()

    def updateDailies(self):
        """Update the dailies comboBox with all Dailies for selected Task"""

        self.dailiesTableWidget.setEnabled(True)
        self.dailiesTableWidget.clearContents()
        self.dailiesTableWidget.setRowCount(0)

        try:
            task = self.tasksTableWidget.selectedItems()
            if not task:
                return

            task = task[0].data(QtCore.Qt.UserRole)

            dailies = nimApi.get_taskDailies(task.get('taskID'))

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Dailies</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support' +
                             '(support@nim-labs.com)</p>')
            return

        self.dailiesTableWidget.setRowCount(len(dailies))

        # Sort dailies by timestamp
        dailies.sort(key=lambda x: x.get('renderDate'))
        dailies.reverse()

        for row, daily in enumerate(dailies):
            for key, val in daily.iteritems():
                if key == 'iconPath':
                    icon = (SERVER_ROOT + val)
                    col = THUMBNAIL
                    item = nimTableWidgetItem('')
                    item.setTextAlignment(QtCore.Qt.AlignHCenter)
                    item.setData(QtCore.Qt.UserRole, daily)

                    self.dailiesTableWidget.setItem(row, col, item)

                    # Create thread to fetch thumbnail
                    worker = fetchThumbnail(icon)
                    self.threads.append(worker)
                    worker.thumbnailURL.connect(item.setThumbnail)
                    worker.start()

                elif key == 'name':
                    col = NAME
                    item = QtGui.QTableWidgetItem(val)
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setData(QtCore.Qt.UserRole, daily)
                    self.dailiesTableWidget.setItem(row, col, item)

                elif key == 'renderDate':
                    col = RENDERTIME
                    item = QtGui.QTableWidgetItem(val)
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setData(QtCore.Qt.UserRole, daily)
                    self.dailiesTableWidget.setItem(row, col, item)

                elif key == 'submitted':
                    if int(val):
                        col = MARKREVIEW
                        item = QtGui.QTableWidgetItem(QtGui.QIcon(':/ui/icons/markedForDailies.png'), '')
                        item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                        item.setData(QtCore.Qt.UserRole, daily)
                        self.dailiesTableWidget.setItem(row, col, item)

                elif key == 'frames':
                    col = FRAMES
                    item = QtGui.QTableWidgetItem(val)
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setData(QtCore.Qt.UserRole, daily)
                    self.dailiesTableWidget.setItem(row, col, item)

                elif key == 'comment':
                    col = COMMENT
                    item = QtGui.QTableWidgetItem(val)
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setData(QtCore.Qt.UserRole, daily)
                    self.dailiesTableWidget.setItem(row, col, item)

        self.dailiesTableWidget.setIconSize(self.thumbnailSize)
        self.dailiesTableWidget.horizontalHeader().stretchLastSection()
        self.dailiesTableWidget.resizeRowsToContents()
        self.dailiesTableWidget.resizeColumnsToContents()

        self.dailiesTableWidget.itemChanged.connect(self.updateThumbnailWidthHeight)

    def updateThumbnailWidthHeight(self, item):
        """Update the row/column size to fit thumbnail after being fetched"""
        if item.column() == 0:
            self.dailiesTableWidget.resizeRowToContents(item.row())
            self.dailiesTableWidget.resizeColumnToContents(item.column())

    def errorDialog(self, err, message):
        self.log.error(traceback.print_exc())
        self.log.error(str(err))
        QtGui.QMessageBox.critical(self,
                                   "Error!",
                                   '%s\n%s' % (message, str(err)))
        return

    def toggleExecuteButton(self):
        """ If any of the menus are set to the first index(0) (meaning they arent
        set, then disable the execute button."""

        if self.jobsComboBox.currentIndex() == 0 or self.showsComboBox.currentIndex() == 0 or \
                (self.shotAssetTabWidget.currentIndex() == SHOTTAB and self.shotsComboBox.currentIndex() == 0) or \
                (self.shotAssetTabWidget.currentIndex() == ASSETTAB and self.assetsComboBox.currentIndex() == 0) or \
                        len(self.tasksTableWidget.selectedItems()) == 0 or len(
            self.dailiesTableWidget.selectedItems()) == 0:
            self.importDailiesPushButton.setEnabled(False)
            self.importDailiesPushButton.setStyleSheet(
                'border: 2px solid red; border-radius: 6px; font: 75 12pt "Arial";')
        else:
            self.importDailiesPushButton.setEnabled(True)
            self.importDailiesPushButton.setStyleSheet(
                'border: 2px solid green; border-radius: 6px; font: 75 12pt "Arial";')

    def updateShotThumbnail(self):
        try:
            shot = self.shotsComboBox.itemData(self.shotsComboBox.currentIndex())
            if shot:
                icon = nimApi.get_shotIcon(shot.get('ID'))
                if icon:
                    icon = (SERVER_ROOT + icon[0].get('img_link'))
                    dstDir = '%s/NIM/thumbnails' % tempfile.gettempdir()
                    if not os.path.exists(dstDir):
                        os.makedirs(dstDir)
                    dsticon = ('%s/%s' % (dstDir, os.path.basename(icon))).replace('\\', '/')
                    urllib.urlretrieve(icon, dsticon)

                    self.shotThumbnail.setStyleSheet("image-position: top;image: url(%s);" % dsticon)
            else:
                raise ValueError()

        except ValueError as err:
            self.shotThumbnail.setStyleSheet('image-position: top;\nimage: url(":/ui/icons/noThumbnail.png");')

        except Exception as err:
            self.log.error('Failed to retrieve thumbnail: %s' % icon)
            self.log.error(str(err))
            self.shotThumbnail.setStyleSheet('image-position: top;\nimage: url(":/ui/icons/noThumbnail.png");')

    def updateAssetThumbnail(self):
        try:
            asset = self.assetsComboBox.itemData(self.assetsComboBox.currentIndex())
            if asset:
                icon = nimApi.get_assetIcon(asset.get('ID'))
                if icon:
                    icon = (SERVER_ROOT + icon[0].get('img_link'))
                    dstDir = '%s/NIM/thumbnails' % tempfile.gettempdir()
                    if not os.path.exists(dstDir):
                        os.makedirs(dstDir)
                    dsticon = ('%s/%s' % (dstDir, os.path.basename(icon))).replace('\\', '/')
                    urllib.urlretrieve(icon, dsticon)

                    self.assetThumbnail.setStyleSheet("image-position: top;image: url(%s);" % dsticon)
            else:
                raise ValueError()

        except ValueError as err:
            self.assetThumbnail.setStyleSheet('image-position: top;\nimage: url(":/ui/icons/noThumbnail.png");')

        except Exception as err:
            self.log.error('Failed to retrieve thumbnail: %s' % icon)
            self.log.error(str(err))
            self.assetThumbnail.setStyleSheet('image-position: top;\nimage: url(":/ui/icons/noThumbnail.png");')

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
        self.updateJobs()

    def resetUi(self, valid=True):
        """Set the UI back to its default state
        @param valid: bool - True reset UI widgets, False disable UI
        """
        if valid:
            self.log.debug('Reset UI widgets')
            self.setWindowTitle('NIM Import Dailies - v%s - NIM User: %s' % (__version__, self.nimUser))
            self.showsComboBox.setEnabled(False)
            self.showsLabel.setEnabled(False)
            self.shotsComboBox.setEnabled(False)
            self.shotsLabel.setEnabled(False)
            self.assetsComboBox.setEnabled(False)
            self.assetsLabel.setEnabled(False)
            self.tasksTableWidget.setEnabled(False)
            self.dailiesTableWidget.setEnabled(False)

            self.jobsComboBox.setCurrentIndex(0)
        else:
            self.dailiesTableWidget.setEnabled(False)

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

        except IOError, err:
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

        # Project
        if self.jobsComboBox.currentIndex() != 0:
            settings.setValue('%s/currentJob' % user, self.jobsComboBox.currentText())

        # Shot/Asset tab
        settings.setValue('%s/shotAssetTab' % user, self.shotAssetTabWidget.currentIndex())

        # Show
        if self.showsComboBox.currentIndex() != 0:
            settings.setValue('%s/currentShow' % user, self.showsComboBox.currentText())

        # Shot
        if self.shotsComboBox.currentIndex() != 0:
            settings.setValue('%s/currentShot' % user, self.shotsComboBox.currentText())

        # Asset
        if self.assetsComboBox.currentIndex() != 0:
            settings.setValue('%s/currentAsset' % user, self.assetsComboBox.currentText())

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

        # Shot/Asset tab
        self.shotAssetTabWidget.setCurrentIndex(settings.value('%s/shotAssetTab' % user, 0))

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


# ===============================================================================
# Preference Dialog
# ===============================================================================
class nimCinesyncPreferences(QtGui.QDialog):
    def __init__(self, mainWindow, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.mainWindow = mainWindow

        pyside_dynamic_ui.loadUi(UIPREFSFILE, self)
        self.setModal(True)

        # Logging action group
        self.tg = QtGui.QButtonGroup(self)
        self.tg.addButton(self.smallThumbnailRadioButton)
        self.tg.addButton(self.medThumbnailRadioButton)
        self.tg.addButton(self.largeThumbnailRadioButton)
        self.tg.buttonReleased.connect(self.changeThumbnailSize)

        settings = QtCore.QSettings()

        # Hide non-current OS widgets
        if 'win32' in sys.platform:
            self.osxLabel.setShown(False)
            self.osxTempDirLineEdit.setShown(False)
            self.osxTempDirBut.setShown(False)

            self.linuxLabel.setShown(False)
            self.linuxTempDirLineEdit.setShown(False)
            self.linuxTempDirBut.setShown(False)

            self.WINDOWSTEMPDIR = tempfile.gettempdir()

            value = settings.value("%s/windowsTempDir" % self.mainWindow.nimUser, self.WINDOWSTEMPDIR)
            self.windowsTempDirLineEdit.setText(value)

        elif 'darwin' in sys.platform:
            self.linuxLabel.setShown(False)
            self.linuxTempDirLineEdit.setShown(False)
            self.linuxTempDirBut.setShown(False)

            self.windowsLabel.setShown(False)
            self.windowsTempDirLineEdit.setShown(False)
            self.windowsTempDirBut.setShown(False)

            self.OSXTEMPDIR = '/private/var/tmp'

            value = settings.value("%s/osxTempDir" % self.mainWindow.nimUser, self.OSXTEMPDIR)
            self.osxTempDirLineEdit.setText(value)

        elif 'linux' in sys.platform:
            self.windowsLabel.setShown(False)
            self.windowsTempDirLineEdit.setShown(False)
            self.windowsTempDirBut.setShown(False)

            self.osxLabel.setShown(False)
            self.osxTempDirLineEdit.setShown(False)
            self.osxTempDirBut.setShown(False)

            self.LINUXTEMPDIR = tempfile.gettempdir()

            value = settings.value("%s/linuxTempDir" % self.mainWindow.nimUser, self.LINUXTEMPDIR)
            self.linuxTempDirLineEdit.setText(value)

        self.closeConnectorCheckBox.setChecked(settings.value("%s/closeConnector" % self.mainWindow.nimUser, True))

        value = settings.value('%s/thumbnailSize' % self.mainWindow.nimUser)
        if value == THUMBNAILLARGE:
            self.largeThumbnailRadioButton.setChecked(True)

        elif value == THUMBNAILSMALL:
            self.smallThumbnailRadioButton.setChecked(True)

        else:
            self.medThumbnailRadioButton.setChecked(True)

        # Signals
        self.windowsTempDirBut.released.connect(self.browseToTempDir)
        self.osxTempDirBut.released.connect(self.browseToTempDir)
        self.linuxTempDirBut.released.connect(self.browseToTempDir)
        self.resetPushButton.released.connect(self.resetToDefault)
        self.windowsTempDirLineEdit.textChanged.connect(self.__updatePrefs)
        self.osxTempDirLineEdit.textChanged.connect(self.__updatePrefs)
        self.linuxTempDirLineEdit.textChanged.connect(self.__updatePrefs)
        self.closeConnectorCheckBox.stateChanged.connect(self.__updatePrefs)
        self.tg.buttonReleased.connect(self.__updatePrefs)
        self.clearMediaBut.released.connect(self.clearMediaCache)

        self.__updatePrefs()

    def clearMediaCache(self):
        """Remove downloaded dailies media from temp directory.
        Note if user changes temp dir then some media will be left behind and not cleaned up"""

        self.mainWindow.log.info('User initiated media cache cleaning')

        settings = QtCore.QSettings()
        user = self.mainWindow.nimUser

        if 'win32' in sys.platform:
            tempDir = settings.value('%s/windowsTempDir' % user)

        elif 'darwin' in sys.platform:
            tempDir = settings.value('%s/osxTempDir' % user)

        elif 'linux' in sys.platform:
            tempDir = settings.value('%s/linuxTempDir' % user)

        tempDir += '/NIM/media'

        try:
            if os.path.exists(tempDir):
                for root, dirs, files in os.walk(tempDir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                self.mainWindow.log.info('Media temp dir deleted: %s' % tempDir)
        except Exception as err:
            self.mainWindow.errorDialog(err,
                                        '<h2>Failed to delete media cache directory:</h2>' +
                                        '<h3>%s</h3>' % tempDir)

    def browseToTempDir(self):
        settings = QtCore.QSettings()
        user = self.mainWindow.nimUser
        direct = tempfile.gettempdir()

        if 'win32' in sys.platform:
            if settings.contains('%s/windowsTempDir' % user):
                temp = settings.value('%s/windowsTempDir' % user)
                if os.path.exists(temp):
                    direct = temp

        elif 'darwin' in sys.platform:
            if settings.contains('%s/osxTempDir' % user):
                temp = settings.value('%s/osxTempDir' % user)
                if os.path.exists(temp):
                    direct = temp

        elif 'linux' in sys.platform:
            if settings.contains('%s/linuxTempDir' % user):
                temp = settings.value('%s/linuxTempDir' % user)
                if os.path.exists(temp):
                    direct = temp

        dlg = QtGui.QFileDialog(self, "Choose Upload Temp Directory", direct, '')
        dlg.setFileMode(QtGui.QFileDialog.Directory)
        dlg.setOptions(QtGui.QFileDialog.ShowDirsOnly)
        if dlg.exec_():
            if self.sender().objectName() == 'windowsTempDirBut':
                settings.setValue("%s/windowsTempDir" % user, dlg.selectedFiles()[0])
                self.windowsTempDirLineEdit.setText(dlg.selectedFiles()[0])

            elif self.sender().objectName() == 'osxTempDirBut':
                settings.setValue("%s/osxTempDir" % user, dlg.selectedFiles()[0])
                self.osxTempDirLineEdit.setText(dlg.selectedFiles()[0])

            elif self.sender().objectName() == 'linuxTempDirBut':
                settings.setValue("%s/linuxTempDir" % user, dlg.selectedFiles()[0])
                self.linuxTempDirLineEdit.setText(dlg.selectedFiles()[0])

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

        self.mainWindow.updateDailies()

    def resetToDefault(self):
        self.closeConnectorCheckBox.setChecked(True)
        self.medThumbnailRadioButton.setChecked(True)

        if 'win32' in sys.platform:
            self.windowsTempDirLineEdit.setText(self.WINDOWSTEMPDIR)

        elif 'darwin' in sys.platform:
            self.osxTempDirLineEdit.setText(self.OSXTEMPDIR)

        elif 'linux' in sys.platform:
            self.linuxTempDirLineEdit.setText(self.LINUXTEMPDIR)

        self.mainWindow.updateDailies()

        self.__updatePrefs()

    def __updatePrefs(self):
        user = self.mainWindow.nimUser
        settings = QtCore.QSettings()
        settings.setValue("%s/windowsTempDir" % user, self.windowsTempDirLineEdit.text())
        settings.setValue("%s/osxTempDir" % user, self.osxTempDirLineEdit.text())
        settings.setValue("%s/linuxTempDir" % user, self.linuxTempDirLineEdit.text())
        settings.setValue("%s/closeConnector" % user, int(self.closeConnectorCheckBox.isChecked()))

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
    app.setApplicationName("NIMCinesyncDailiesNotesImporter")

    win = NIMCinesyncDailiesNotesImporter()
    win.show()
    win.raise_()
    sys.exit(app.exec_())
