/* ****************************************************************************
#
# Filename: AE/nimMenu.jsx
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *************************************************************************** */

function buildMenuUI(thisObj) {
    var nimMenuPanel = (thisObj instanceof Panel) ? thisObj : new Window('palette', 'NIM', undefined),
        nimPanel = null,
        openButton = nimMenuPanel.add('button', undefined, 'Open'),
        importButton = nimMenuPanel.add('button', undefined, 'Import'),
        saveAsButton = nimMenuPanel.add('button', undefined, 'Save As'),
        versionUpButton = nimMenuPanel.add('button', undefined, 'Version Up'),
        publishButton = nimMenuPanel.add('button', undefined, 'Publish'),
        changeUserButton = nimMenuPanel.add('button', undefined, 'Change User'),
        primaryButtons = [openButton, importButton, saveAsButton, versionUpButton, publishButton],
        foundUserID = false;

    openButton.onClick = function() {
        nimPanel = buildPanelUI(userID, 'open');
    }

    importButton.onClick = function() {
        nimPanel = buildPanelUI(userID, 'import');
    }

    saveAsButton.onClick = function() {
        nimPanel = buildPanelUI(userID, 'saveAs');
    }

    versionUpButton.onClick = function() {
        var metadata = getNimMetadata(),
            comment;
        if (!metadata.classID) {
            alert("Error: This file doesn't have any NIM metadata; please save it through the NIM menu before attempting to version up.");
            return;
        }
        commentDialog(function(comment) {
            if (comment === false) return;
            if (saveFile(metadata.classID, metadata.className, metadata.serverID, metadata.serverPath, metadata.taskID, metadata.taskFolder, metadata.basename, comment, false))
                alert('New version saved.');
            else
                alert('Error: Version up failed!');
        });
    }

    publishButton.onClick = function() {
        var metadata = getNimMetadata(),
            comment;
        if (!metadata.classID) {
            alert("Error: This file doesn't have any NIM metadata; please save it through the NIM menu before attempting to publish.");
            return;
        }
        commentDialog(function(comment) {
            if (comment === false) return;
            if (!saveFile(metadata.classID, metadata.className, metadata.serverID, metadata.serverPath, metadata.taskID, metadata.taskFolder, metadata.basename, comment, true))
                alert('Error: Publish failed!');
        });
    }

    changeUserButton.onClick = function() {
        changeUserDialog(primaryButtons);
    }

    nimMenuPanel.layout.layout(true);

    os = getOperatingSystem();
    foundUserID = getUserID(primaryButtons);
    if (foundUserID)
        userID = foundUserID;

    return nimMenuPanel;
}
