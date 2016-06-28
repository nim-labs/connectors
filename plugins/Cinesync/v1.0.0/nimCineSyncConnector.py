#!/usr/bin/env python
# ******************************************************************************
#
# Filename: nimCinesyncConnector
#
# Description:
#
# Notes:
#
# Created on: 6/22/2016
#
# Authors: Andrew Singara, Scott Ballard
# Contact: support@nim-labs.com
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *****************************************************************************

__authors__ = ['Andrew Singara','Scott Ballard']
__version__ = '1.0.0'
__revisions__ = \
"""
1.0.0 - Scott B - Initial development
"""

# @todo:

import sys
import os
import ctypes
import logging
import tempfile
import traceback
import urllib
import webbrowser
from datetime import datetime, date
import getpass
from pprint import pprint

# UPDATE [NIM_CONNECTOR_ROOT] with the path to your NIM Connectors root folder
nim_root = 'Z:/VAULT/NIM/_dev/nim_dev'
sys.path.append(nim_root)

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
import nim_core.nim as nim
import nim_core.nim_api as nimApi
import nim_core.nim_file as nimFile
import nim_core.nim_print as nimPrint
import nim_core.nim_tools as nimTools
import nim_core.nim_win as nimWin
import nim_core.UI as nimUI
import pyside_dynamic_ui
from nimDarktheme import nim_darktheme

# ===============================================================================
# Global Variables
# ===============================================================================
UI_FILE = os.path.join(os.path.dirname(sys.argv[0]), 'ui/NIMImportDailiesUI.ui')
ASSETTAB, SHOTTAB = range(0,2)
SERVER_ROOT = 'http://%s' % nimPrefs.get_url().split('/')[2]
TASKNAME, TASKARTIST, TASKDESC = range(0, 3)
THUMBNAIL, NAME, RENDERTIME, FRAMES = range(0, 4)
THUMBNAILSMALL = 75
THUMBNAILMEDIUM = 125
THUMBNAILLARGE = 175


class NIMImportDailies(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        # Member variables
        self.logfile = None
        self.log = None
        self.nimUser = None
        self.thumbnailSize = THUMBNAILMEDIUM

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

        # Logging action group
        self.tg = QtGui.QActionGroup(self)
        self.tg.addAction(self.actionSmall)
        self.tg.addAction(self.actionMedium)
        self.tg.addAction(self.actionLarge)
        self.actionWarning.setChecked(True)
        self.connect(self.tg, QtCore.SIGNAL("triggered(QAction *)"), self.changeThumbnailSize)

        # Initiate logging
        self.logger('INFO')
        self.log.debug('Initiate: %s' % os.path.basename(__file__))

        # Signals
        self.actionView_Log.triggered.connect(self.viewLog)
        self.actionClear_Log.triggered.connect(self.clearLog)
        self.importDailiesPushButton.clicked.connect(self.importDailies)
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

        self.updateJobs()
        self.toggleExecuteButton()

        self._restoreUserWinPrefs()

    def importDailies(self):
        self.log.info('Importing Dailies')

    def updateJobs(self):
        """Update the jobs comboBox with all NIM jobs"""

        self.resetUi()
        self.jobsComboBox.clear()

        try:
            user = nimApi.get_user()
            userId = nimApi.get_userID(user)
            jobs = nimApi.get_jobs(userID=2)

        except Exception as err:
            self.errorDialog(err,
                             '<h4>Failed to get NIM Jobs</h4>' +
                             '<p>Error: Please contact your Supervisor or NIM Support' +
                             '(support@nim-labs.com)</p>')
            return

        self.jobsComboBox.addItem(QtGui.QIcon(':/ui/icons/block.png'), 'Select Job', 0)

        for jobName, jobID in jobs.iteritems():
            self.jobsComboBox.addItem(QtGui.QIcon(':/ui/icons/jobs.png'), jobName, jobID)

        settings = QtCore.QSettings()
        job = settings.value('currentJob', '')
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
        show = settings.value('currentShow', '')
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
        show = settings.value('currentShot', '')
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
        show = settings.value('currentAsset', '')
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
        actualSize = None
        for row, daily in enumerate(dailies):
            for key, val in daily.iteritems():
                if key == 'iconPath':
                    icon = (SERVER_ROOT + val)
                    dstDir = '%s/NIM/thumbnails' % tempfile.gettempdir()
                    if not os.path.exists(dstDir):
                        os.makedirs(dstDir)
                    dsticon = ('%s/%s' % (dstDir, os.path.basename(icon))).replace('\\', '/')
                    urllib.urlretrieve(icon, dsticon)

                    actualSize = QtGui.QIcon(dsticon).actualSize(QtCore.QSize(self.thumbnailSize, self.thumbnailSize))

                    col = THUMBNAIL
                    item = QtGui.QTableWidgetItem('')
                    item.setTextAlignment(QtCore.Qt.AlignHCenter)
                    item.setIcon(QtGui.QIcon(dsticon))
                    item.setData(QtCore.Qt.UserRole, daily)
                    item.setSizeHint(actualSize)
                    self.dailiesTableWidget.setItem(row, col, item)

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

                elif key == 'frames':
                    col = FRAMES
                    item = QtGui.QTableWidgetItem(val)
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setData(QtCore.Qt.UserRole, daily)
                    self.dailiesTableWidget.setItem(row, col, item)


        if actualSize:
            self.dailiesTableWidget.setIconSize(actualSize)
        self.dailiesTableWidget.horizontalHeader().stretchLastSection()
        self.dailiesTableWidget.resizeRowsToContents()
        self.dailiesTableWidget.resizeColumnsToContents()


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
                    len(self.tasksTableWidget.selectedItems()) == 0 or len(self.dailiesTableWidget.selectedItems()) == 0:
                self.importDailiesPushButton.setEnabled(False)
                self.importDailiesPushButton.setStyleSheet('border: 2px solid red; border-radius: 6px; font: 75 12pt "Arial";')
        else:
            self.importDailiesPushButton.setEnabled(True)
            self.importDailiesPushButton.setStyleSheet('border: 2px solid green; border-radius: 6px; font: 75 12pt "Arial";')

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

    def changeUser(self):
        nimUI.GUI().update_user()
        self.resetUi()
        self._restoreUserWinPrefs()
        self.updateJobs()

    def changeThumbnailSize(self):
        settings = QtCore.QSettings()
        user = self.nimUser

        index = self.tg.actions().index(self.tg.checkedAction())

        if index == 0:
            self.thumbnailSize = THUMBNAILSMALL
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILSMALL)

        elif index == 1:
            self.thumbnailSize = THUMBNAILMEDIUM
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILMEDIUM)

        elif index == 2:
            self.thumbnailSize = THUMBNAILLARGE
            settings.setValue('%s/thumbnailSize' % user, THUMBNAILLARGE)

        self.updateDailies()

    def resetUi(self):
        """Set the UI back to its default state"""

        self.nimUser = nimApi.get_user()
        #@TODO: Find out why user is not changing in NIM Api
        print self.nimUser
        self.setWindowTitle('NIM Import Dailies - %s - user: %s' % (__version__, self.nimUser))

        self.showsComboBox.setEnabled(False)
        self.showsLabel.setEnabled(False)
        self.shotsComboBox.setEnabled(False)
        self.shotsLabel.setEnabled(False)
        self.assetsComboBox.setEnabled(False)
        self.assetsLabel.setEnabled(False)
        self.tasksTableWidget.setEnabled(False)
        self.dailiesTableWidget.setEnabled(False)

        self.jobsComboBox.setCurrentIndex(0)

    def openNIMSupportURL(self):
        webbrowser.open('http://nim-labs.com/support/')

    def about(self):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setText('Version: %s\n\n%s' % (__version__, __revisions__))
        msgBox.setWindowTitle('About')
        msgBox.setIconPixmap(QtGui.QPixmap(':ui/icons/nimLogo_small.png'))
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        msgBox.exec_()

    def logger(self, level):
        # Create log
        self.logfile = "%s/logs/nimCinesyncConnector/%s/%s_%s.log" % (tempfile.gettempdir(),
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

        except IOError, err:
            print'Couldnt open log file:', err
            return

    def viewLog(self):
        if not os.path.exists(self.logfile):
            raise IOError("Can't find log file: " + self.logfile)

        os.system('notepad.exe ' + self.logfile)

    def clearLog(self):
        if not os.path.exists(self.logfile):
            raise IOError('Cant find log file:' + self.logfile)
        open(self.logfile, 'w').close()

    def setLogLevel(self, level):
        if isinstance(level, QtGui.QAction):
            level = level.text().upper()

        log_levels = {'DEBUG':logging.DEBUG,
                      'INFO':logging.INFO,
                      'WARNING':logging.WARNING,
                      'ERROR':logging.ERROR,
                      'CRITICAL':logging.CRITICAL}

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
        elif value == 1:
            self.actionInfo.setChecked(True)
        elif value == 2:
            self.actionWarning.setChecked(True)
        elif value == 3:
            self.actionError.setChecked(True)
        else:
            self.actionCritical.setChecked(True)

        self.log.debug('User preferences restored')


# ===============================================================================
# MAIN
# ===============================================================================
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    # Allow Windows to display the application icon instead of the Python icon on taskbar
    myappid = u'nim.nimCinesyncConnector.%s' % __version__  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Set dark theme
    nim_darktheme()

    # Establish connection to NIM
    nimPrefs.mk_default(notify_success=True)

    # Used to store user preferences
    app.setOrganizationName("NIM Labs")
    app.setOrganizationDomain("http://nim-labs.com/")
    app.setApplicationName("NIMCinesyncConnector")

    win = NIMImportDailies()
    win.show()
    win.raise_()
    app.exec_()