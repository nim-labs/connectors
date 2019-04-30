/* ****************************************************************************
#
# Filename: AE/nimPanel.jsx
# Version:  v2.0.0.160511
#
# Copyright (c) 2014-2019 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *************************************************************************** */

function buildPanelUI(userID, action) {

	// Populates a dropdown with the strings stored under the nameField key in the objects
	// contained in dataArray; defaultMessage will be the first dropdown item if items exist
	function populateDropdown(dropdown, dataArray, nameField, defaultMessage) {
		var dataArrayLength = dataArray.length;
		dropdown.removeAll();
		dropdown.add('item', defaultMessage);
		if (dataArrayLength && dataArray[0].ID == 0) {
			dataArray.shift();
			dataArrayLength = dataArray.length;
		}
		if (nameField instanceof Array) {
			var nameFieldLength = nameField.length;
			for (var x = 0; x < dataArrayLength && x < 40; x++) {
				var thisItemName = [];
				for (var y = 0; y < nameFieldLength; y++)
					thisItemName.push(dataArray[x][nameField[y]]);
				//dropdown.add('item', thisItemName.join('_'));
				dropdown.add('item', thisItemName.join('_'));
			}
		}
		else {
			for (var x = 0; x < dataArrayLength; x++)
				dropdown.add('item', dataArray[x][nameField]);
		}
		if (dropdown.items.length == 1) {
			dropdown.removeAll();
			dropdown.add('item', 'None');
			dropdown.enabled = false;
		}
		else {
			dropdown.enabled = true;
			dataArray.unshift({ ID: 0 });
		}
		dropdown.selection = 0;
	}

	// Populates a listbox with the strings stored under the nameField key in the objects
	// contained in dataArray
	function populateListbox(listbox, dataArray, nameField) {
		var dataArrayLength = dataArray.length;
		listbox.removeAll();
		if (nameField instanceof Array) {
			var nameFieldLength = nameField.length;
			for (var x = 0; x < dataArrayLength; x++) {
				var thisItemName = [];
				for (var y = 0; y < nameFieldLength; y++) {
					var thisNamePiece = dataArray[x][nameField[y]];
					if (thisNamePiece)
						thisItemName.push(thisNamePiece);
				}
				listbox.add('item', thisItemName.join(' - '));
			}
		}
		else {
			for (var x = 0; x < dataArrayLength; x++)
				listbox.add('item', dataArray[x][nameField]);
		}
		if (!listbox.items.length)
			listbox.enabled = false;
		else
			listbox.enabled = true;
	}

	// Clears text fields in versionInfo panel (and saved filepath variable), disable confirm button
	function clearVersionInfo() {
		filepath = '';
		if (pathText) pathText.text = '';
		if (userText) userText.text = '';
		if (dateText) dateText.text = '';
		if (commentText) commentText.text = '';
	}

	// Sets initial dropdown or listbox ('container') selection to item with 'property' equal to 'value' within 'array'
	// (of objects that initially populated dropdown or listbox)
	function setInitialSelection(property, value, array, container) {
		if (property && value && array && container) {
			var arrayLength = array.length;
			for (var x = 0; x < arrayLength; x++) {
				if (array[x][property] == value) {
					container.selection = x;
					container.onChange();
					return true;
				}
			}
		}
		return false;
	}

	function setPanelPrefs() {
		setPref('AE', 'jobID', jobID);
		if (action == 'saveAs') setPref('AE', 'serverID', serverID);
		setPref('AE', 'assetID', assetID);
		setPref('AE', 'showID', showID);
		setPref('AE', 'shotID', shotID);
		setPref('AE', 'taskID', taskID);
		setPref('AE', 'showPub', showPub);
		setPref('AE', 'basename', basename);
	}

	var nimPanel = new Window('dialog', 'NIM', undefined),
		jobs = nimAPI({ q: 'getUserJobs', u: userID }),
		servers,
		assets = [],
		shows = [],
		shots = [],
		tasks = nimAPI({ q: 'getTaskTypes', type: 'artist', app: 'AE' }),
		basenames = [],
		versions = [],
		jobID = 0,
		serverID = 0,
		serverPath = '',
		assetID = 0,
		assetName = '',
		showID = 0,
		shotID = 0,
		shotName = '',
		taskID = 0,
		taskName = '',
		taskFolder = '',
		showPub = 0,
		basename = '',
		maxVersion = 0,
		filepath = '',
		jobTaskInfo = nimPanel.add('group', undefined),
		jobInfo = jobTaskInfo.add('panel', undefined, 'Job Info'),
		jobDropdown = jobInfo.add('dropdownlist', undefined, '', { items: ['None'] }),
		serverDropdown = jobInfo.add('dropdownlist', undefined, '', { items: ['None'] }),
		jobTabPanel = jobInfo.add('tabbedpanel'),
		assetsTab = jobTabPanel.add('tab', undefined, 'Assets'),
		assetDropdown = assetsTab.add('dropdownlist', undefined, '', { items: ['None'] }),
		assetMasterButton,
		shotsTab = jobTabPanel.add('tab', undefined, 'Shots'),
		showDropdown = shotsTab.add('dropdownlist', undefined, '', { items: ['None'] }),
		shotDropdown = shotsTab.add('dropdownlist', undefined, '', { items: ['None'] }),
		taskInfo = jobTaskInfo.add('panel', undefined, 'Task Info'),
		filterDropdown = taskInfo.add('dropdownlist', undefined, '', { items: ['Work', 'Published'] }),
		taskDropdown = taskInfo.add('dropdownlist', undefined, '', { items: ['None'] }),
		basenameGroup = taskInfo.add('group', undefined),
		basenameListboxLabel = basenameGroup.add('statictext', undefined, 'Basename: '),
		basenameListbox = basenameGroup.add('listbox', [0, 0, 250, 200], 'Basename'),
		tagGroup,
		tagLabel,
		tagInput,
		versionInfo = nimPanel.add('panel', undefined, 'Version Info'),
		versionGroup = versionInfo.add('group', undefined),
		versionListboxLabel = versionGroup.add('statictext', undefined, 'Versions: '),
		versionListbox = versionGroup.add('listbox', [0, 0, 550, 250], 'Versions'),
		pathGroup = versionInfo.add('group', undefined),
		pathLabel = pathGroup.add('statictext', undefined, 'Path: '),
		pathText = pathGroup.add('statictext', [0, 0, 550, 20], ''),
		userGroup = versionInfo.add('group', undefined),
		userLabel = userGroup.add('statictext', undefined, 'User: '),
		userText = userGroup.add('statictext', [0, 0, 550, 20], ''),
		dateGroup = versionInfo.add('group', undefined),
		dateLabel = dateGroup.add('statictext', undefined, 'Date: '),
		dateText = dateGroup.add('statictext', [0, 0, 550, 20], ''),
		commentGroup = versionInfo.add('group', undefined),
		commentLabel = commentGroup.add('statictext', undefined, 'Comment: '),
		commentText,
		commentInput,
		allDropdowns = [jobDropdown, serverDropdown, assetDropdown, showDropdown, shotDropdown, taskDropdown, filterDropdown],
		allDropdownsLength = allDropdowns.length,
		buttonGroup = nimPanel.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'Confirm'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel');

	jobDropdown.title = 'Job: ';
	serverDropdown.title = 'Server: ';
	assetDropdown.title = 'Asset: ';
	showDropdown.title = 'Show: ';
	shotDropdown.title = 'Shot: ';
	taskDropdown.title = 'Task: ';
	filterDropdown.title = 'Filter: ';

	serverDropdown.enabled = false;
	assetDropdown.enabled = false;
	showDropdown.enabled = false;
	shotDropdown.enabled = false;
	taskDropdown.enabled = false;
	filterDropdown.enabled = false;
	basenameListbox.enabled = false;
	versionListbox.enabled = false;
	confirmButton.enabled = false;

	nimPanel.alignChildren = 'fill';
	jobTaskInfo.alignChildren = 'fill';
	taskInfo.alignChildren = 'right';
	basenameGroup.alignChildren = 'top';
	versionGroup.alignChildren = 'top';
	
	versionGroup.alignment = 'right';
	pathGroup.alignment = 'right';
	userGroup.alignment = 'right';
	dateGroup.alignment = 'right';
	commentGroup.alignment = 'right';
	buttonGroup.alignment = 'right';

	populateDropdown(jobDropdown, jobs, ['number', 'jobname'], 'Select a job...');

	for (var x = 0; x < allDropdownsLength; x++) {
		allDropdowns[x].preferredSize[0] = 289;
		allDropdowns[x].selection = 0;
	}

	assetDropdown.preferredSize[0] = 250;
	showDropdown.preferredSize[0] = 250;
	shotDropdown.preferredSize[0] = 250;


	// Customize panel based on action
	if (!action)
		action = 'open';

	if (action == 'open' || action == 'import') {
		commentText = commentGroup.add('statictext', [0, 0, 550, 20], '');
		jobInfo.remove(serverDropdown);
		serverDropdown = null;
		if (action == 'open') confirmButton.text = 'Open File';
		else if (action == 'import') {
			confirmButton.text = 'Import File';
			assetMasterButton = assetsTab.add('button', undefined, 'Import Asset Master');
			assetMasterButton.enabled = false;
			assetMasterButton.alignment = 'fill';
		}
	}
	else if (action == 'saveAs') {
		taskInfo.remove(filterDropdown);
		filterDropdown = null;
		tagGroup = taskInfo.add('group', undefined);
		tagLabel = tagGroup.add('statictext', undefined, 'Tag: ');
		tagInput = tagGroup.add('edittext', [0, 0, 250, 20]);
		versionInfo.remove(pathGroup);
		versionInfo.remove(userGroup);
		versionInfo.remove(dateGroup);
		pathText = null;
		userText = null;
		dateText = null;
		commentInput = commentGroup.add('edittext', [0, 0, 550, 20]);
		confirmButton.text = 'Save As';
	}


	// Add events to elements
	jobDropdown.onChange = function() {
		if (!this.selection || !this.selection.index) {
			jobID = 0;
			if (serverDropdown) {
				populateDropdown(serverDropdown, [], '', '');
				serverDropdown.enabled = false;
			}
			populateDropdown(assetDropdown, [], '', '');
			populateDropdown(showDropdown, [], '', '');
			return;
		}
		jobID = jobs[this.selection.index].ID;
		assets = nimAPI({ q: 'getAssets', ID: jobID });
		shows = nimAPI({ q: 'getShows', ID: jobID });
		populateDropdown(assetDropdown, assets, 'name', 'Select an asset...');
		populateDropdown(showDropdown, shows, 'showname', 'Select a show...');
		if (serverDropdown) {
			servers = nimAPI({ q: 'getJobServers', ID: jobID });
			populateDropdown(serverDropdown, servers, 'server', 'Select a server...');
			if (serverDropdown.items.length == 1)
				serverDropdown.enabled = false;
			else
				serverDropdown.enabled = true;
		}
	}

	if (serverDropdown) {
		serverDropdown.onChange = function() {
			if (!this.selection || !this.selection.index) {
				serverID = 0;
				serverPath = '';
				confirmButton.enabled = false;
				return;
			}
			serverID = servers[this.selection.index].ID;
			if (os == 'win')
				serverPath = servers[this.selection.index].winPath;
			else if (os == 'mac')
				serverPath = servers[this.selection.index].osxPath;
			else
				serverPath = servers[this.selection.index].path;
			if (taskID)
				confirmButton.enabled = true;
		}
	}

	showDropdown.onChange = function() {
		if (!this.selection || !this.selection.index) {
			showID = 0;
			populateDropdown(shotDropdown, [], '', '');
			return;
		}
		showID = shows[this.selection.index].ID;
		shots = nimAPI({ q: 'getShots', ID: showID });
		populateDropdown(shotDropdown, shots, 'name', 'Select a shot...');
		if (assetMasterButton)
			assetMasterButton.enabled = false;
	}

	assetDropdown.onChange = function() {
		if (!this.selection || !this.selection.index) {
			assetID = 0;
			assetName = '';
			if (!shotID) {
				populateDropdown(taskDropdown, [], '', '');
				if (filterDropdown) filterDropdown.enabled = false;
			}
			return;
		}
		shotID = 0;
		shotName = '';
		shotDropdown.selection = 0;
		assetID = assets[this.selection.index].ID;
		assetName = assets[this.selection.index].name;
		populateDropdown(taskDropdown, tasks, 'name', 'Select a task...');
		if (filterDropdown)
			filterDropdown.enabled = true;
		if (assetMasterButton)
			assetMasterButton.enabled = true;
	}

	if (assetMasterButton) {
		assetMasterButton.onClick = function() {
			var assetMaster = nimAPI({ q: 'getAssetMasterOSPath', assetID: assetID, os: os }),
				assetMasterPath,
				assetMasterFile;
			if (assetMaster == 0) {
				alert('Error: No asset master found!');
				return;
			}
			assetMasterPath = assetMaster.path;
			assetMasterFile = new File(assetMasterPath);
			if (!assetMasterFile.exists) {
				alert('Error: Asset master symbolic link not found at "' + assetMasterPath + '"!');
				return;
			}
			try { app.project.importFile(new ImportOptions(assetMasterFile)); }
			catch (e) {
				alert(e);
				return;
			}
			nimPanel.close();
		}
	}

	shotDropdown.onChange = function() {
		if (!this.selection || !this.selection.index) {
			shotID = 0;
			shotName = '';
			if (!assetID) {
				populateDropdown(taskDropdown, [], '', '');
				if (filterDropdown) filterDropdown.enabled = false;
			}
			return;
		}
		assetID = 0;
		assetName = '';
		assetDropdown.selection = 0;
		shotID = shots[this.selection.index].ID;
		shotName = shots[this.selection.index].name;
		populateDropdown(taskDropdown, tasks, 'name', 'Select a task...');
		if (filterDropdown)
			filterDropdown.enabled = true;
	}

	taskDropdown.onChange = function() {
		if (!this.selection || !this.selection.index) {
			taskID = 0;
			taskName = '';
			taskFolder = '';
			basename = '';
			maxVersion = 0;
			populateListbox(basenameListbox, [], '');
			populateListbox(versionListbox, [], '');
			clearVersionInfo();
			confirmButton.enabled = false;
			return;
		}
		var classID, className;
		if (assetID) {
			classID = assetID;
			className = 'ASSET';
		}
		else if (shotID) {
			classID = shotID;
			className = 'SHOT';
		}
		taskID = tasks[this.selection.index].ID;
		taskName = tasks[this.selection.index].name;
		taskFolder = tasks[this.selection.index].folder;
		if (showPub)
			basenames = nimAPI({ q: 'getBasenameAllPub', task_type_ID: taskID, itemID: classID, 'class': className, username: username });
		else
			basenames = nimAPI({ q: 'getBasenamesInfo', task_type_ID: taskID, ID: classID, 'class': className });
		populateListbox(basenameListbox, basenames, 'basename');
		populateListbox(versionListbox, [], '');
		if (serverID) {
			if (tagInput && tagInput.text)
				basenameListbox.enabled = false;
			confirmButton.enabled = true;
		}
		else confirmButton.enabled = false;
	}

	if (filterDropdown) {
		filterDropdown.onChange = function() {
			var classID, className;
			if (assetID) {
				classID = assetID;
				className = 'ASSET';
			}
			else if (shotID) {
				classID = shotID;
				className = 'SHOT';
			}
			if (this.selection.text == 'Published') {
				showPub = 1;
				if (!taskID) return;
				basenames = nimAPI({ q: 'getBasenameAllPub', task_type_ID: taskID, itemID: classID, 'class': className, username: username });
			}
			else {
				showPub = 0;
				if (!taskID) return;
				basenames = nimAPI({ q: 'getBasenames', task_type_ID: taskID, ID: classID, 'class': className });
			}
			basename = '';
			maxVersion = 0;
			populateListbox(basenameListbox, basenames, 'basename');
			populateListbox(versionListbox, [], '');
			clearVersionInfo();
			confirmButton.enabled = false;
		}
	}

	basenameListbox.onChange = function() {
		if (!this.selection) {
			basename = '';
			maxVersion = 0;
			populateListbox(versionListbox, [], '');
			clearVersionInfo();
			if (action != 'saveAs') confirmButton.enabled = false;
			return;
		}
		var classID, className;
		if (assetID) {
			classID = assetID;
			className = 'ASSET';
		}
		else if (shotID) {
			classID = shotID;
			className = 'SHOT';
		}
		basename = basenames[this.selection.index].basename;
		maxVersion = basenames[this.selection.index].maxVersion;
		versions = nimAPI({ q: 'getVersions', itemID: classID, type: className, basename: basename, pub: showPub, username: username });
		populateListbox(versionListbox, versions, ['filename', 'note']);
		if (serverID && action == 'saveAs')
			versionListbox.enabled = false;
		// Select published version if published filter is on
		else if (filterDropdown && showPub) {
			var publishedFile = basenames[this.selection.index],
				publishedFileName = publishedFile.filename,
				versionListboxChildren = versionListbox.children,
				versionListboxChildrenLength = versionListboxChildren.length;
			for (var x = 0; x < versionListboxChildrenLength; x++) {
				if (versionListboxChildren[x].text.indexOf(publishedFileName) != -1) {
					versionListbox.selection = versionListboxChildren[x];
					versionListbox.selection.text += ' (PUBLISHED)';
					break;
				}
			}
		}
	}

	if (tagInput) {
		tagInput.onChanging = function() {
			if (!this.text) {
				if (serverID && taskID) basenameListbox.enabled = true;
				return;
			}
			basenameListbox.selection = null;
			basenameListbox.enabled = false;
		}
	}

	versionListbox.onChange = function() {
		if (!this.selection) {
			clearVersionInfo();
			confirmButton.enabled = false;
			return;
		}
		var thisVersion = versions[this.selection.index],
			thisFilepath,
			filepathObj = nimAPI({ q: 'getOSPath', fileID: thisVersion.fileID, os: os });
		if (filepathObj == 0)
			thisFilepath = thisVersion.filepath;
		else
			thisFilepath = filepathObj.path;
		filepath = thisFilepath + thisVersion.filename;
		pathText.text = thisFilepath;
		userText.text = thisVersion.username;
		dateText.text = thisVersion.date;
		if (commentText) commentText.text = thisVersion.note;
		confirmButton.enabled = true;
	}

	confirmButton.onClick = function() {
		if (action == 'open') {
			if (!filepath) {
				alert('Error: No filepath specified!');
				return;
			}
			var fileToOpen = new File(filepath);
			if (!fileToOpen.exists) {
				alert('Error: "' + filepath + '" doesn\'t exist!');
				return;
			}
			try { app.open(fileToOpen); }
			catch (e) {
				alert(e);
				return;
			}
		}
		else if (action == 'saveAs') {
			if (!serverID) {
				alert('Error: No server specified!');
				return;
			}
			var newFileBasename = '',
				classID, className;
			if (assetID) {
				classID = assetID;
				className = 'ASSET';
				newFileBasename = assetName + '_' + taskName;
			}
			else if (shotID) {
				classID = shotID;
				className = 'SHOT';
				newFileBasename = shotName + '_' + taskName;
			}
			if (basenameListbox.selection)
				newFileBasename = basename;
			else if (tagInput.text)
				newFileBasename += '_' + tagInput.text.replace(/ /g, '_');

			var thisVersion = parseInt(maxVersion) + 1;

			if (saveFile(classID, className, serverID, serverPath, taskID, taskName, taskFolder, newFileBasename, commentInput.text, false, thisVersion))
				alert('Save successful.');
			else
				alert('Error: Save failed!');
		}
		else if (action == 'import') {
			if (!filepath) {
				alert('Error: No filepath specified!');
				return;
			}
			var fileToImport = new File(filepath);
			if (!fileToImport.exists) {
				alert('Error: "' + filepath + '" doesn\'t exist!');
				return;
			}
			try { app.project.importFile(new ImportOptions(fileToImport)); }
			catch (e) {
				alert(e);
				return;
			}
		}
		setPanelPrefs();
		nimPanel.close();
	}

	cancelButton.onClick = function() {
		setPanelPrefs();
		nimPanel.close();
	}

	// Set starting values based on NIM preferences file
	jobID = parseInt(getPref('AE', 'jobID')) || 0;
	setInitialSelection('ID', jobID, jobs, jobDropdown);

	if (serverDropdown) {
		serverID = parseInt(getPref('AE', 'serverID')) || 0;
		setInitialSelection('ID', serverID, servers, serverDropdown);
	}

	assetID = parseInt(getPref('AE', 'assetID')) || 0;
	setInitialSelection('ID', assetID, assets, assetDropdown);

	showID = parseInt(getPref('AE', 'showID')) || 0;
	setInitialSelection('ID', showID, shows, showDropdown);

	shotID = parseInt(getPref('AE', 'shotID')) || 0;
	setInitialSelection('ID', shotID, shots, shotDropdown);
	if (shotID) jobTabPanel.selection = shotsTab;

	taskID = parseInt(getPref('AE', 'taskID')) || 0;
	setInitialSelection('ID', taskID, tasks, taskDropdown);

	if (filterDropdown) {
		showPub = parseInt(getPref('AE', 'showPub')) || 0;
		filterDropdown.selection = showPub;
		filterDropdown.onChange();
	}

	basename = getPref('AE', 'basename');
	setInitialSelection('basename', basename, basenames, basenameListbox);

	nimPanel.show();
	return nimPanel;
}
