/* ****************************************************************************
#
# Filename: AE/nimMenu.jsx
# Version:  v2.0.0.160511
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *************************************************************************** */

function buildMenuUI(thisObj) {

	// If this panel already exists...
	if (thisObj instanceof Panel) {
		var menuButtons = thisObj.children,
			menuButtonsLength = menuButtons.length;

		// Remove any children (buttons) that already exist in the panel since we're rebuilding it
		for (var x = 0; x < menuButtonsLength; x++)
			thisObj.remove(menuButtons[0]);  // menuButtons[0] instead of [x] because when we remove the first item, 0 becomes the next
	}

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
			comment,
			fileID = getMetadata('fileID') || 0,
			maxVersion,
			version;

		if (!metadata.classID) {
			alert("Error: This file doesn't have any NIM metadata; please save it through the NIM menu before attempting to version up.");
			return;
		}

		// Need to get max version to know what version to version up / publish to
		maxVersion = nimAPI({ q: 'getMaxVersion', fileID: fileID }) || 0;
		if (maxVersion.length)
			maxVersion = parseInt(maxVersion[0].maxVersion) || 0;

		version = maxVersion + 1;
		
		commentDialog(function(comment) {
			if (comment === false) return;
			if (saveFile(metadata.classID, metadata.className, metadata.serverID, metadata.serverPath, metadata.taskID, metadata.taskName, metadata.taskFolder, metadata.basename, comment, false, version))
				alert('New version saved.');
			else
				alert('Error: Version up failed!');
		});
	}

	publishButton.onClick = function() {
		var metadata = getNimMetadata(),
			comment,
			fileID = getMetadata('fileID') || 0,
			maxVersion,
			version;

		if (!metadata.classID) {
			alert("Error: This file doesn't have any NIM metadata; please save it through the NIM menu before attempting to publish.");
			return;
		}

		// Need to get max version to know what version to version up / publish to
		maxVersion = nimAPI({ q: 'getMaxVersion', fileID: fileID }) || 0;
		if (maxVersion.length)
			maxVersion = parseInt(maxVersion[0].maxVersion) || 0;

		version = maxVersion + 1;

		commentDialog(function(comment) {
			if (comment === false) return;
			if (!saveFile(metadata.classID, metadata.className, metadata.serverID, metadata.serverPath, metadata.taskID, metadata.taskName, metadata.taskFolder, metadata.basename, comment, true, version))
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
