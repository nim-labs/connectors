/* ****************************************************************************
#
# Filename: Photoshop/nimPanel.jsx
# Version:  v2.0.0.160511
#
# Copyright (c) 2014-2022 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# *************************************************************************** */

function buildPanelUI(userID, action, metadata) {

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
			for (var x = 0; x < dataArrayLength; x++) {
				var thisItemName = [];
				for (var y = 0; y < nameFieldLength; y++)
					thisItemName.push(dataArray[x][nameField[y]]);
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
		setPref('Photoshop', 'jobID', jobID);
		if (action == 'saveAs') setPref('Photoshop', 'serverID', serverID);
		setPref('Photoshop', 'assetID', assetID);
		setPref('Photoshop', 'showID', showID);
		setPref('Photoshop', 'shotID', shotID);
		setPref('Photoshop', 'taskID', taskID);
		setPref('Photoshop', 'showPub', showPub);
		setPref('Photoshop', 'basename', basename);
	}

	var nimPanel = new Window('dialog', 'NIM', undefined),
		jobs = nimAPI({ q: 'getUserJobs', u: userID }),
		servers,
		assets = [],
		shows = [],
		shots = [],
		tasks = nimAPI({ q: 'getTaskTypes', type: 'artist', app: 'Photoshop' }),
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
		fileID = 0,
		fileSettings,
		jobTaskInfo = nimPanel.add('group', undefined),
		jobInfo = jobTaskInfo.add('panel', undefined, 'Job Info'),
		jobDropdown = jobInfo.add('dropdownlist', undefined, '', { items: ['None'] }),
		serverDropdown = jobInfo.add('dropdownlist', undefined, '', { items: ['None'] }),
		jobTabPanel = jobInfo.add('tabbedpanel'),
		assetsTab = jobTabPanel.add('tab', undefined, 'Assets'),
		assetDropdown = assetsTab.add('dropdownlist', undefined, '', { items: ['None'] }),
		//assetMasterButton,
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
		outputFiles = nimPanel.add('tabbedpanel'),
		versionInfo = outputFiles.add('tab', undefined, 'Version Info'),
		versionGroup = versionInfo.add('group', undefined),
		versionListboxLabel = versionGroup.add('statictext', undefined, 'Versions: '),
		versionListbox = versionGroup.add('listbox', [0, 0, 550, 220], 'Versions'),
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
		//alternateCommentGroup = nimPanel.add('group', undefined),
		commentLabel = commentGroup.add('statictext', undefined, 'Comment: '),
		commentText,
		commentInput,
		allFileTypes = ['Photoshop (.psd)', 'EPS', 'JPEG (.jpg)', 'PNG', 'Targa (.tga)', 'TIFF (.tif)'],
		fileTypeGroup,
		fileTypeLabel,
		fileTypeDropdown,
		fileTypeEditButton,
		exportElementsDropdownGroup,
		exportElementsDropdown,
		elementsToAdd,
		elementSelectionGroup,
		elementButtonGroup,
		elementFileTypeDropdown,
		elementAddButton,
		elementEditButton,
		elementDeleteButton,
		elementListboxGroup,
		elementListboxLabel,
		elementListbox,
		elementDetailsDialog,
		elementDetailsPanel,
		elementDetailsText1,
		elementDetailsText2,
		elementDetailsText3,
		elementDetailsText4,
		elementDetailsText5,
		elementDetailsText6,
		elementDetailsText7,
		elementDetailsText8,
		elementDetailsText9,
		elementExports,
		elementTypes,
		elementTypesLength,
		elementTypeNames,
		documentBitDepth,
		documentResolution,
		elementTypeDropdown,
		bitDepthDropdown,
		resolutionDropdown,
		allDropdowns = [jobDropdown, serverDropdown, assetDropdown, showDropdown, shotDropdown, taskDropdown, filterDropdown],
		allDropdownsLength = allDropdowns.length,
		buttonGroup = nimPanel.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'Confirm'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel');

	jobDropdown.title = 'Job: ';
	//serverDropdown.title = 'Server: ';
	assetDropdown.title = 'Asset: ';
	showDropdown.title = 'Show: ';
	shotDropdown.title = 'Shot: ';
	taskDropdown.title = 'Task: ';
	//filterDropdown.title = 'Filter: ';

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
	versionInfo.alignChildren = 'right';
	jobTaskInfo.alignChildren = 'fill';
	taskInfo.alignChildren = 'right';
	basenameGroup.alignChildren = 'top';
	versionGroup.alignChildren = 'top';
	
	versionGroup.alignment = 'right';
	pathGroup.alignment = 'right';
	userGroup.alignment = 'right';
	dateGroup.alignment = 'right';
	commentGroup.alignment = 'right';
	//alternateCommentGroup.alignment = 'right';
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

	if (action == 'open' /*|| action == 'import'*/) {
		commentText = commentGroup.add('statictext', [0, 0, 550, 20], '');
		jobInfo.remove(serverDropdown);
		serverDropdown = null;	
		/*if (action == 'open')*/ confirmButton.text = 'Open File';
		/*
		else if (action == 'import') {
			confirmButton.text = 'Import File';
			assetMasterButton = assetsTab.add('button', undefined, 'Import Asset Master');
			assetMasterButton.enabled = false;
			assetMasterButton.alignment = 'fill';
		}
		*/
	}
	else if (action == 'saveAs' || action == 'versionUp' || action == 'publish') {

		// Functions for building dialogs to edit different file types

		function buildDialogEPS(dialog, settings, bitDepthGroup) {
			// Save all local function variables as keys on "dialogElements", which will be passed to "finishBuildingDialog" function
			var dialogElements = {},
				previewGroup = dialogElements.previewGroup = dialog.add('group', undefined),
				previewLabel = dialogElements.previewLabel = previewGroup.add('statictext', undefined, 'Preview:'),
				previewDropdown = dialogElements.previewDropdown = previewGroup.add('dropdownlist', undefined, '', { items: ['None', 'TIFF (1 bit/pixel)', 'TIFF (8 bits/pixel)'] }),
				encodingGroup = dialogElements.encodingGroup = dialog.add('group', undefined),
				encodingLabel = dialogElements.encodingLabel = encodingGroup.add('statictext', undefined, 'Encoding:'),
				encodingDropdown = dialogElements.encodingDropdown = encodingGroup.add('dropdownlist', undefined, '', { items: ['ASCII', 'Binary', 'JPEG (low quality)', 'JPEG (medium quality)', 'JPEG (high quality)', 'JPEG (maximum quality)'] }),
				halftoneCheckbox = dialogElements.halftoneCheckbox = dialog.add('checkbox', undefined, 'Include Halftone Screen'),
				transferFunctionCheckbox = dialogElements.transferFunctionCheckbox = dialog.add('checkbox', undefined, 'Include Transfer Function'),
				postScriptColorCheckbox = dialogElements.postScriptColorCheckbox = dialog.add('checkbox', undefined, 'PostScript Color Management'),
				vectorDataCheckbox = dialogElements.vectorDataCheckbox = dialog.add('checkbox', undefined, 'Include Vector Data'),
				interpolationCheckbox = dialogElements.interpolationCheckbox = dialog.add('checkbox', undefined, 'Image Interpolation');

			dialog.text = 'EPS Options';

			// bitDepthDropdown is a global variable; if no bitDepthGroup is passed, we don't have a bitDepthDropdown in this dialog
			if (bitDepthGroup) bitDepthDropdown = bitDepthGroup.add('dropdownlist', undefined, '', { items: ['8'] });

			previewDropdown.selection = settings.epsPreview;
			encodingDropdown.selection = settings.epsEncoding;

			halftoneCheckbox.value = (settings.epsHalftone == 0 ? false : true);
			transferFunctionCheckbox.value = (settings.epsTransferFunction == 0 ? false : true);
			postScriptColorCheckbox.value = (settings.epsPostScriptColor == 0 ? false : true);
			vectorDataCheckbox.value = (settings.epsVectorData == 0 ? false : true);
			interpolationCheckbox.value = (settings.epsInterpolation == 0 ? false : true);

			finishBuildingDialog(dialog, settings, dialogElements);
		}

		function buildDialogJPG(dialog, settings, bitDepthGroup) {
			// Save all local function variables as keys on "dialogElements", which will be passed to "finishBuildingDialog" function
			var dialogElements = {},
				imageOptions = dialogElements.imageOptions = dialog.add('panel', undefined, 'Image Options'),
				formatOptions = dialogElements.formatOptions = dialog.add('panel', undefined, 'Format Options'),
				qualityGroup = dialogElements.qualityGroup = imageOptions.add('group', undefined),
				qualityLabel = dialogElements.qualityLabel = qualityGroup.add('statictext', undefined, 'Quality:'),
				qualityTextbox = dialogElements.qualityTextbox = qualityGroup.add('edittext', undefined, settings.jpgQuality),
				qualitySlider = dialogElements.qualitySlider = qualityGroup.add('slider', [0, 0, 170, 13], settings.jpgQuality, 0, 12),
				baselineFormatRadio = dialogElements.baselineFormatRadio = formatOptions.add('radiobutton', undefined, 'Baseline ("Standard")'),
				optimizedFormatRadio = dialogElements.optimizedFormatRadio = formatOptions.add('radiobutton', undefined, 'Baseline Optimized'),
				progressiveFormatRadio = dialogElements.progressiveFormatRadio = formatOptions.add('radiobutton', undefined, 'Progressive'),
				scansGroup = dialogElements.scansGroup = formatOptions.add('group', undefined),
				scansLabel = dialogElements.scansLabel = scansGroup.add('statictext', undefined, 'Scans:'),
				scansDropdown = dialogElements.scansDropdown = scansGroup.add('dropdownlist', undefined, '', { items: ['3', '4', '5'] });

			dialog.text = 'JPEG Options';

			// bitDepthDropdown is a global variable; if no bitDepthGroup is passed, we don't have a bitDepthDropdown in this dialog
			if (bitDepthGroup) bitDepthDropdown = bitDepthGroup.add('dropdownlist', undefined, '', { items: ['16', '8'] });

			qualityGroup.orientation = 'row';

			qualityGroup.alignChildren = 'left';
			formatOptions.alignChildren = 'left';

			scansDropdown.selection = settings.jpgScans;
			scansDropdown.enabled = false;

			if (settings.jpgFormat == 0)
				baselineFormatRadio.value = true;
			else if (settings.jpgFormat == 1)
				optimizedFormatRadio.value = true;
			else if (settings.jpgFormat == 2) {
				progressiveFormatRadio.value = true;
				scansDropdown.enabled = true;
			}

			qualityTextbox.onChanging = function() {
				qualitySlider.value = Math.floor(qualityTextbox.text);
			}

			qualitySlider.onChanging = function() {
				qualityTextbox.text = Math.floor(qualitySlider.value);
			}

			baselineFormatRadio.onClick = function() {
				scansDropdown.enabled = false;
			}

			optimizedFormatRadio.onClick = function() {
				scansDropdown.enabled = false;
			}

			progressiveFormatRadio.onClick = function() {
				scansDropdown.enabled = true;
			}

			finishBuildingDialog(dialog, settings, dialogElements);
		}

		function buildDialogPNG(dialog, settings, bitDepthGroup) {
			// Save all local function variables as keys on "dialogElements", which will be passed to "finishBuildingDialog" function
			var dialogElements = {},
				compressionPanel = dialogElements.compressionPanel = dialog.add('panel', undefined, 'Compression'),
				interlacePanel = dialogElements.interlacePanel = dialog.add('panel', undefined, 'Interlace'),
				compressionRadio1 = dialogElements.compressionRadio1 = compressionPanel.add('radiobutton', undefined, 'None / Fast'),
				compressionRadio2 = dialogElements.compressionRadio2 = compressionPanel.add('radiobutton', undefined, 'Smallest / Slow'),
				interlaceRadio1 = dialogElements.interlaceRadio1 = interlacePanel.add('radiobutton', undefined, 'None'),
				interlaceRadio2 = dialogElements.interlaceRadio2 = interlacePanel.add('radiobutton', undefined, 'Interlaced');

			dialog.text = 'PNG Options';

			// bitDepthDropdown is a global variable; if no bitDepthGroup is passed, we don't have a bitDepthDropdown in this dialog
			if (bitDepthGroup) bitDepthDropdown = bitDepthGroup.add('dropdownlist', undefined, '', { items: ['16', '8'] });

			compressionPanel.alignChildren = 'left';
			interlacePanel.alignChildren = 'left';

			if (settings.pngCompression == 0)
				compressionRadio1.value = true;
			else if (settings.pngCompression == 1)
				compressionRadio2.value = true;

			if (settings.pngInterlaced == 0)
				interlaceRadio1.value = true;
			else if (settings.pngInterlaced == 1)
				interlaceRadio2.value = true;

			finishBuildingDialog(dialog, settings, dialogElements);
		}

		function buildDialogTGA(dialog, settings, bitDepthGroup) {
			// Save all local function variables as keys on "dialogElements", which will be passed to "finishBuildingDialog" function
			var dialogElements = {},
				resolutionPanel = dialogElements.resolutionPanel = dialog.add('panel', undefined, 'Resolution'),
				resolutionRadio1 = dialogElements.resolutionRadio1 = resolutionPanel.add('radiobutton', undefined, '16 bits/pixel'),
				resolutionRadio2 = dialogElements.resolutionRadio2 = resolutionPanel.add('radiobutton', undefined, '24 bits/pixel'),
				resolutionRadio3 = dialogElements.resolutionRadio3 = resolutionPanel.add('radiobutton', undefined, '32 bits/pixel'),
				compressCheckbox = dialogElements.compressCheckbox = dialog.add('checkbox', undefined, 'Compress (RLE)');

			dialog.text = 'Targa Options';

			// bitDepthDropdown is a global variable; if no bitDepthGroup is passed, we don't have a bitDepthDropdown in this dialog
			if (bitDepthGroup) bitDepthDropdown = bitDepthGroup.add('dropdownlist', undefined, '', { items: ['8'] });

			resolutionPanel.alignChildren = 'left';

			if (settings.tgaResolution == 0)
				resolutionRadio1.value = true;
			else if (settings.tgaResolution == 1)
				resolutionRadio2.value = true;
			else if (settings.tgaResolution == 2)
				resolutionRadio3.value = true;

			compressCheckbox.value = (settings.tgaCompress == 0 ? false : true);

			finishBuildingDialog(dialog, settings, dialogElements);
		}

		function buildDialogTIF(dialog, settings, bitDepthGroup) {
			// Save all local function variables as keys on "dialogElements", which will be passed to "finishBuildingDialog" function
			var dialogElements = {},
				twoColumnGroup = dialogElements.twoColumnGroup = dialog.add('group', undefined),
				column1 = dialogElements.column1 = twoColumnGroup.add('group', undefined),
				column2 = dialogElements.column2 = twoColumnGroup.add('group', undefined),
				imageCompressionPanel = dialogElements.imageCompressionPanel = column1.add('panel', undefined, 'Image Compression'),
				imageCompressionRadio1 = dialogElements.imageCompressionRadio1 = imageCompressionPanel.add('radiobutton', undefined, 'None'),
				imageCompressionRadio2 = dialogElements.imageCompressionRadio2 = imageCompressionPanel.add('radiobutton', undefined, 'LZW'),
				imageCompressionRadio3 = dialogElements.imageCompressionRadio3 = imageCompressionPanel.add('radiobutton', undefined, 'ZIP'),
				imageCompressionRadio4 = dialogElements.imageCompressionRadio4 = imageCompressionPanel.add('radiobutton', undefined, 'JPEG'),
				qualityGroup = dialogElements.qualityGroup = imageCompressionPanel.add('group', undefined),
				qualityLabel = dialogElements.qualityLabel = qualityGroup.add('statictext', undefined, 'Quality:'),
				qualityTextbox = dialogElements.qualityTextbox = qualityGroup.add('edittext', undefined, settings.jpgQuality),
				qualitySlider = dialogElements.qualitySlider = imageCompressionPanel.add('slider', [0, 0, 170, 13], settings.jpgQuality, 0, 12),
				saveImagePyramidCheckbox = dialogElements.saveImagePyramidCheckbox = column1.add('checkbox', undefined, 'Save Image Pyramid'),
				saveTransparencyCheckbox = dialogElements.saveTransparencyCheckbox = column1.add('checkbox', undefined, 'Save Transparency'),
				pixelOrderPanel = dialogElements.pixelOrderPanel = column2.add('panel', undefined, 'Pixel Order'),
				pixelOrderRadio1 = dialogElements.pixelOrderRadio1 = pixelOrderPanel.add('radiobutton', undefined, 'Interleaved (RGBRGB)'),
				pixelOrderRadio2 = dialogElements.pixelOrderRadio2 = pixelOrderPanel.add('radiobutton', undefined, 'Per Channel (RRGGBB)'),
				byteOrderPanel = dialogElements.byteOrderPanel = column2.add('panel', undefined, 'Byte Order'),
				byteOrderRadio1 = dialogElements.byteOrderRadio1 = byteOrderPanel.add('radiobutton', undefined, 'IBM PC'),
				byteOrderRadio2 = dialogElements.byteOrderRadio2 = byteOrderPanel.add('radiobutton', undefined, 'Macintosh'),
				layerCompressionPanel = dialogElements.layerCompressionPanel = column2.add('panel', undefined, 'Layer Compression'),
				layerCompressionRadio1 = dialogElements.layerCompressionRadio1 = layerCompressionPanel.add('radiobutton', undefined, 'RLE (faster saves, bigger files)'),
				layerCompressionRadio2 = dialogElements.layerCompressionRadio2 = layerCompressionPanel.add('radiobutton', undefined, 'ZIP (slower saves, smaller files)'),
				layerCompressionRadio3 = dialogElements.layerCompressionRadio3 = layerCompressionPanel.add('radiobutton', undefined, 'Discard Layers and Save a Copy');

			dialog.text = 'TIFF Options';

			// bitDepthDropdown is a global variable; if no bitDepthGroup is passed, we don't have a bitDepthDropdown in this dialog
			if (bitDepthGroup) bitDepthDropdown = bitDepthGroup.add('dropdownlist', undefined, '', { items: ['32', '16', '8'] });

			twoColumnGroup.alignChildren = 'fill';
			column1.orientation = 'column';
			column1.alignChildren = 'fill';
			column2.orientation = 'column';
			column2.alignChildren = 'fill';
			imageCompressionPanel.alignChildren = 'left';
			pixelOrderPanel.alignChildren = 'left';
			byteOrderPanel.alignChildren = 'left';
			layerCompressionPanel.alignChildren = 'left';

			qualityLabel.enabled = false;
			qualityTextbox.enabled = false;
			qualitySlider.enabled = false;

			if (settings.tifImageCompression == 0)
				imageCompressionRadio1.value = true;
			else if (settings.tifImageCompression == 1)
				imageCompressionRadio2.value = true;
			else if (settings.tifImageCompression == 2)
				imageCompressionRadio3.value = true;
			else if (settings.tifImageCompression == 3) {
				imageCompressionRadio4.value = true;
				qualityLabel.enabled = true;
				qualityTextbox.enabled = true;
				qualitySlider.enabled = true;
			}

			saveImagePyramidCheckbox.value = (settings.tifSaveImagePyramid == 0 ? false : true);
			saveTransparencyCheckbox.value = (settings.tifSaveTransparency == 0 ? false : true);

			if (settings.tifPixelOrder == 0)
				pixelOrderRadio1.value = true;
			else if (settings.tifPixelOrder == 1)
				pixelOrderRadio2.value = true;

			if (settings.tifByteOrder == 0)
				byteOrderRadio1.value = true;
			else if (settings.tifByteOrder == 1)
				byteOrderRadio2.value = true;

			if (settings.tifLayerCompression == 0)
				layerCompressionRadio1.value = true;
			else if (settings.tifLayerCompression == 1)
				layerCompressionRadio2.value = true;
			else if (settings.tifLayerCompression == 2)
				layerCompressionRadio3.value = true;

			qualityTextbox.onChanging = function() {
				qualitySlider.value = Math.floor(qualityTextbox.text);
			}

			qualitySlider.onChanging = function() {
				qualityTextbox.text = Math.floor(qualitySlider.value);
			}

			imageCompressionRadio1.onClick = function() {
				qualityLabel.enabled = false;
				qualityTextbox.enabled = false;
				qualitySlider.enabled = false;
			}

			imageCompressionRadio2.onClick = function() {
				qualityLabel.enabled = false;
				qualityTextbox.enabled = false;
				qualitySlider.enabled = false;
			}

			imageCompressionRadio3.onClick = function() {
				qualityLabel.enabled = false;
				qualityTextbox.enabled = false;
				qualitySlider.enabled = false;
			}

			imageCompressionRadio4.onClick = function() {
				qualityLabel.enabled = true;
				qualityTextbox.enabled = true;
				qualitySlider.enabled = true;
			}

			finishBuildingDialog(dialog, settings, dialogElements);
		}

		// Adds OK and Cancel buttons to bottom of file-type-specific saving dialog;
		// makes OK button save all appropriate settings to "settings" object;
		// all relevant dialog UI elements are keys in "dialogElements"
		function finishBuildingDialog(dialog, settings, dialogElements) {
			var dialogButtonGroup = dialog.add('group', undefined),
				dialogOkButton = dialogButtonGroup.add('button', undefined, 'OK'),
				dialogCancelButton = dialogButtonGroup.add('button', undefined, 'Cancel');

			dialogOkButton.onClick = function() {
				var thisExtension = settings.extension;

				if (elementTypeDropdown && elementTypes.length)
					settings.elementTypeID = elementTypes[elementTypeDropdown.selection.index].ID;

				if (resolutionDropdown) {
					if (resolutionDropdown.selection.index == 0)
						settings.resolution = 1;
					else if (resolutionDropdown.selection.index == 1)
						settings.resolution = 0.5;
					else if (resolutionDropdown.selection.index == 2)
						settings.resolution = 0.25;
				}

				if (thisExtension == 'psd') {
					if (bitDepthDropdown) settings.bitDepth = (bitDepthDropdown.selection.index == 0 ? 32 : (bitDepthDropdown.selection.index == 1 ? 16 : 8));
				}
				else if (thisExtension == 'eps') {
					settings.epsPreview = dialogElements.previewDropdown.selection.index;
					settings.epsEncoding = dialogElements.encodingDropdown.selection.index;
					settings.epsHalftone = (dialogElements.halftoneCheckbox.value == true ? 1 : 0);
					settings.epsTransferFunction = (dialogElements.transferFunctionCheckbox.value == true ? 1 : 0);
					settings.epsPostScriptColor = (dialogElements.postScriptColorCheckbox.value == true ? 1 : 0);
					settings.epsVectorData = (dialogElements.vectorDataCheckbox.value == true ? 1 : 0);
					settings.epsInterpolation = (dialogElements.interpolationCheckbox.value == true ? 1 : 0);
				}
				else if (thisExtension == 'jpg') {
					if (bitDepthDropdown) settings.bitDepth = (bitDepthDropdown.selection.index == 0 ? 16 : 8);
					settings.jpgQuality = Math.floor(dialogElements.qualitySlider.value);
					if (dialogElements.baselineFormatRadio.value == true)
						settings.jpgFormat = 0;
					else if (dialogElements.optimizedFormatRadio.value == true)
						settings.jpgFormat = 1;
					else if (dialogElements.progressiveFormatRadio.value == true)
						settings.jpgFormat = 2;
					
					settings.jpgScans = dialogElements.scansDropdown.selection.index;
				}
				else if (thisExtension == 'png') {
					if (bitDepthDropdown) settings.bitDepth = (bitDepthDropdown.selection.index == 0 ? 16 : 8);
					settings.pngCompression = (dialogElements.compressionRadio1.value == true ? 0 : 1);
					settings.pngInterlaced = (dialogElements.interlaceRadio1.value == true ? 0 : 1);
				}
				else if (thisExtension == 'tga') {
					if (dialogElements.resolutionRadio1.value == true)
						settings.tgaResolution = 0;
					else if (dialogElements.resolutionRadio2.value == true)
						settings.tgaResolution = 1;
					else if (dialogElements.resolutionRadio3.value == true)
						settings.tgaResolution = 2;
					
					settings.tgaCompress = (dialogElements.compressCheckbox.value == true ? 1 : 0);
				}
				else if (thisExtension == 'tif') {
					if (bitDepthDropdown) settings.bitDepth = (bitDepthDropdown.selection.index == 0 ? 32 : (bitDepthDropdown.selection.index == 1 ? 16 : 8));
					if (dialogElements.imageCompressionRadio1.value == true)
						settings.tifImageCompression = 0;
					else if (dialogElements.imageCompressionRadio2.value == true)
						settings.tifImageCompression = 1;
					else if (dialogElements.imageCompressionRadio3.value == true)
						settings.tifImageCompression = 2;
					else if (dialogElements.imageCompressionRadio4.value == true)
						settings.tifImageCompression = 3;

					settings.jpgQuality = Math.floor(dialogElements.qualitySlider.value);
					settings.tifSaveImagePyramid = (dialogElements.saveImagePyramidCheckbox.value == true ? 1 : 0);
					settings.tifSaveTransparency = (dialogElements.saveTransparencyCheckbox.value == true ? 1 : 0);

					if (dialogElements.pixelOrderRadio1.value == true)
						settings.tifPixelOrder = 0;
					else if (dialogElements.pixelOrderRadio2.value == true)
						settings.tifPixelOrder = 1;

					if (dialogElements.byteOrderRadio1.value == true)
						settings.tifByteOrder = 0;
					else if (dialogElements.byteOrderRadio2.value == true)
						settings.tifByteOrder = 1;

					if (dialogElements.layerCompressionRadio1.value == true)
						settings.tifLayerCompression = 0;
					else if (dialogElements.layerCompressionRadio2.value == true)
						settings.tifLayerCompression = 1;
					else if (dialogElements.layerCompressionRadio3.value == true)
						settings.tifLayerCompression = 2;
				}

				// If there are bit depth and resolution dropdowns, change element list item on OK
				if (bitDepthDropdown && resolutionDropdown) {
					var elementListboxLength = elementListbox.items.length;

					for (var x = 0; x < elementListboxLength; x++) {
						var thisExtension = elementExports[x].extension,
							thisExtensionName = thisExtension,
							thisBitDepth = elementExports[x].bitDepth,
							thisResolution = elementExports[x].resolution;

						if (thisResolution == 1)
							thisResolution = 'Full';
						else if (thisResolution == 0.5)
							thisResolution = '1/2';
						else if (thisResolution == 0.25)
							thisResolution = '1/4';

						if (thisExtension == 'psd')
							thisExtensionName = 'Photoshop (.psd)';
						else if (thisExtension == 'eps')
							thisExtensionName = 'EPS';
						else if (thisExtension == 'jpg')
							thisExtensionName = 'JPEG (.jpg)';
						else if (thisExtension == 'png')
							thisExtensionName = 'PNG';
						else if (thisExtension == 'tga')
							thisExtensionName = 'Targa (.tga)';
						else if (thisExtension == 'tif')
							thisExtensionName = 'TIFF (.tif)';

						thisExtensionName += ' - ' + thisBitDepth + '-bit - ' + thisResolution + ' Res';
						elementListbox.items[x].text = thisExtensionName;
					}

					elementListbox.onChange();
				}

				dialog.close();
			}

			dialogCancelButton.onClick = function() {
				dialog.close();
			}

		}  // function finishBuildingDialog(dialog, settings, dialogElements)


		// Other stuff to do when action == saveAs or versionUp or publish
		taskInfo.remove(filterDropdown);
		filterDropdown = null;
		tagGroup = taskInfo.add('group', undefined);
		tagLabel = tagGroup.add('statictext', undefined, 'Tag: ');
		tagInput = tagGroup.add('edittext', [0, 0, 250, 20]);
		versionInfo.remove(pathGroup);
		versionInfo.remove(userGroup);
		versionInfo.remove(dateGroup);
		fileTypeGroup = versionInfo.add('group', undefined);
		fileTypeLabel = fileTypeGroup.add('statictext', undefined, 'File Type: ');
		fileTypeDropdown = fileTypeGroup.add('dropdownlist', undefined, '', { items: allFileTypes });
		fileTypeDropdown.selection = 0;
		fileTypeEditButton = fileTypeGroup.add('button', undefined, 'Edit Settings');
		exportElementsDropdownGroup = versionInfo.add('group', undefined);
		exportElementsDropdownLabel = exportElementsDropdownGroup.add('statictext', undefined, 'Export Elements: ');
		exportElementsDropdown = exportElementsDropdownGroup.add('dropdownlist', [0, 0, 250, 20], '', { items: ['Never', 'Always', 'Only on Publish'] });
		pathText = null;
		userText = null;
		dateText = null;
		elementsToAdd = outputFiles.add('tab', [0, 0, 687, 265], 'Export Elements');
		elementsToAdd.orientation = 'row';
		elementsToAdd.alignChildren = 'fill';
		elementSelectionGroup = elementsToAdd.add('group', undefined);
		elementSelectionGroup.orientation = 'column';
		elementSelectionGroup.alignChildren = 'left';
		elementButtonGroup = elementSelectionGroup.add('group', undefined);
		elementFileTypeDropdown = elementButtonGroup.add('dropdownlist', undefined, '', { items: allFileTypes });
		elementFileTypeDropdown.selection = 0;
		elementAddButton = elementButtonGroup.add('button', undefined, 'Add Element');
		fileID = (metadata ? (metadata.fileID ? metadata.fileID : getMetadata('fileID')) : getMetadata('fileID'));
		fileSettings = nimAPI({ q: 'getFileSettings', fileID: fileID || 0 });
		elementExports = nimAPI({ q: 'getElementExports', fileID: fileID || 0 }) || [];
		elementTypes = nimAPI({ q: 'getElementTypes' });
		elementTypesLength = elementTypes.length;
		elementTypeNames = [];
		documentResolution = activeDocument.resolution;

		// If no fileSettings row is found with this fileID, make new fileSettings object
		if (!fileSettings.length) {
			fileSettings = {
				elementTypeID: 0,
				'export': 1,
				extension: 'psd',
				epsPreview: 0,
				epsEncoding: 0,
				epsHalftone: 0,
				epsTransferFunction: 0,
				epsPostScriptColor: 0,
				epsVectorData: 0,
				epsInterpolation: 0,
				jpgQuality: 3,
				jpgFormat: 0,
				jpgScans: 0,
				pngCompression: 0,
				pngInterlaced: 0,
				tgaResolution: 1,
				tgaCompress: 1,
				tifImageCompression: 0,
				tifSaveImagePyramid: 0,
				tifSaveTransparency: 0,
				tifPixelOrder: 0,
				tifByteOrder: 0,
				tifLayerCompression: 0
			};
		}
		else
			fileSettings = fileSettings[0];

		if (fileTypeDropdown) {
			if (fileSettings.extension == 'psd') {
				fileTypeDropdown.selection = 0;
				fileTypeEditButton.enabled = false;
			}
			else if (fileSettings.extension == 'eps')
				fileTypeDropdown.selection = 1;
			else if (fileSettings.extension == 'jpg')
				fileTypeDropdown.selection = 2;
			else if (fileSettings.extension == 'png')
				fileTypeDropdown.selection = 3;
			else if (fileSettings.extension == 'tga')
				fileTypeDropdown.selection = 4;
			else if (fileSettings.extension == 'tif')
				fileTypeDropdown.selection = 5;
		}

		if (exportElementsDropdown)
			exportElementsDropdown.selection = parseInt(fileSettings.export);

		if (activeDocument.bitsPerChannel == BitsPerChannelType.THIRTYTWO)
			documentBitDepth = 32;
		else if (activeDocument.bitsPerChannel == BitsPerChannelType.SIXTEEN)
			documentBitDepth = 16;
		else if (activeDocument.bitsPerChannel == BitsPerChannelType.EIGHT)
			documentBitDepth = 8;

		var psdMaxBitDepth = 32,
			epsMaxBitDepth = 8,
			jpgMaxBitDepth = 16,
			pngMaxBitDepth = 16,
			tgaMaxBitDepth = 8,
			tifMaxBitDepth = 32;

		elementListboxGroup = elementSelectionGroup.add('group', undefined);
		elementListboxGroup.alignChildren = 'top';
		elementListboxLabel = elementListboxGroup.add('statictext', undefined, 'Elements: ');
		elementListbox = elementListboxGroup.add('listbox', [0, 0, 250, 210], 'Elements');

		elementDetailsGroup = elementsToAdd.add('group', undefined);
		elementDetailsGroup.orientation = 'column';
		elementDetailsGroup.alignChildren = 'fill';
		elementDetailsGroup.margins = [10, 0, 0, 10];

		elementDetailsButtonGroup = elementDetailsGroup.add('group', undefined);

		elementEditButton = elementDetailsButtonGroup.add('button', undefined, 'Edit Element');
		elementDeleteButton = elementDetailsButtonGroup.add('button', undefined, 'Delete Element');
		elementEditButton.enabled = false;
		elementDeleteButton.enabled = false;

		elementDetailsPanel = elementDetailsGroup.add('panel', [0, 0, 345, 210], 'Element Details');
		elementDetailsPanel.margins = [15, 15, 0, 10];
		elementDetailsPanel.spacing = 2;
		elementDetailsPanel.alignChildren = 'fill';

		elementDetailsText1 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText2 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText3 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText4 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText5 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText6 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText7 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText8 = elementDetailsPanel.add('statictext', undefined, '');
		elementDetailsText9 = elementDetailsPanel.add('statictext', undefined, '');

		// Populate element exports list
		var elementExportsLength = elementExports.length;

		for (var x = 0; x < elementExportsLength; x++) {
			var thisExtension = elementExports[x].extension,
				thisExtensionName = thisExtension,
				thisBitDepth = elementExports[x].bitDepth,
				thisResolution = elementExports[x].resolution;

			if (thisResolution == 1)
				thisResolution = 'Full';
			else if (thisResolution == 0.5)
				thisResolution = '1/2';
			else if (thisResolution == 0.25)
				thisResolution = '1/4';

			if (thisExtension == 'psd')
				thisExtensionName = 'Photoshop (.psd)';
			else if (thisExtension == 'eps')
				thisExtensionName = 'EPS';
			else if (thisExtension == 'jpg')
				thisExtensionName = 'JPEG (.jpg)';
			else if (thisExtension == 'png')
				thisExtensionName = 'PNG';
			else if (thisExtension == 'tga')
				thisExtensionName = 'Targa (.tga)';
			else if (thisExtension == 'tif')
				thisExtensionName = 'TIFF (.tif)';

			thisExtensionName += ' - ' + thisBitDepth + '-bit - ' + thisResolution + ' Res';
			elementListbox.add('item', thisExtensionName);
		}

		// Populate elementTypeNames array
		for (var x = 0; x < elementTypesLength; x++)
			elementTypeNames.push(elementTypes[x].name);

		if (action == 'versionUp' || action == 'publish') {
			nimPanel.remove(jobTaskInfo);
			//outputFiles.remove(versionInfo);
			versionInfo.remove(versionGroup);
			jobDropdown = null;
			serverDropdown = null;
			showDropdown = null;
			assetDropdown = null;
			shotDropdown = null;
			taskDropdown = null;
			basenameListbox = null;
			versionListbox = null;
			tagInput = null;
			//commentGroup = alternateCommentGroup,
			//commentLabel = commentGroup.add('statictext', undefined, 'Comment: ');
			outputFiles.selection = versionInfo;
			confirmButton.enabled = true;
			if (action == 'versionUp')
				confirmButton.text = 'Version Up';
			else if (action == 'publish')
				confirmButton.text = 'Publish';

			// Need to get max version to know what version to version up / publish to
			if (metadata) {
				maxVersion = nimAPI({ q: 'getMaxVersion', fileID: fileID });
				if (maxVersion.length)
					maxVersion = parseInt(maxVersion[0].maxVersion) || 0;
			}
		}
		else if (action == 'saveAs') {
			outputFiles.selection = versionInfo;
			confirmButton.text = 'Save As';
		}

		commentInput = commentGroup.add('edittext', [0, 0, 550, 20]);
	
	}  // if (action == 'saveAs' || action == 'versionUp' || action == 'publish')

	// Add events to elements
	if (jobDropdown) {
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
	}

	if (serverDropdown) {
		serverDropdown.title = 'Server: ';
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

	if (showDropdown) {
		showDropdown.onChange = function() {
			if (!this.selection || !this.selection.index) {
				showID = 0;
				populateDropdown(shotDropdown, [], '', '');
				return;
			}
			showID = shows[this.selection.index].ID;
			shots = nimAPI({ q: 'getShots', ID: showID });
			populateDropdown(shotDropdown, shots, 'name', 'Select a shot...');
			//if (assetMasterButton)
			//	assetMasterButton.enabled = false;
		}
	}

	if (assetDropdown) {
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
			//if (assetMasterButton)
			//	assetMasterButton.enabled = true;
		}
	}

	/*
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
	*/

	if (shotDropdown) {
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
	}

	if (taskDropdown) {
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
	}

	if (filterDropdown) {
		filterDropdown.title = 'Filter: ';
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

	if (basenameListbox) {
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

	if (versionListbox) {
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
	}

	if (fileTypeDropdown) {
		fileTypeDropdown.onChange = function() {
			if (this.selection.index == 0) {
				fileTypeEditButton.enabled = false;
				fileSettings.extension = 'psd';
			}
			else
				fileTypeEditButton.enabled = true;

			if (this.selection.index == 1)
				fileSettings.extension = 'eps';
			else if (this.selection.index == 2)
				fileSettings.extension = 'jpg';
			else if (this.selection.index == 3)
				fileSettings.extension = 'png';
			else if (this.selection.index == 4)
				fileSettings.extension = 'tga';
			else if (this.selection.index == 5)
				fileSettings.extension = 'tif';
		}
	}

	if (fileTypeEditButton) {
		fileTypeEditButton.onClick = function() {
			var fileSettingsDialog = new Window('dialog', 'File Settings', undefined);
			fileSettingsDialog.alignChildren = 'fill';

			if (fileTypeDropdown.selection.index == 1)
				buildDialogEPS(fileSettingsDialog, fileSettings);
			else if (fileTypeDropdown.selection.index == 2)
				buildDialogJPG(fileSettingsDialog, fileSettings);
			else if (fileTypeDropdown.selection.index == 3)
				buildDialogPNG(fileSettingsDialog, fileSettings);
			else if (fileTypeDropdown.selection.index == 4)
				buildDialogTGA(fileSettingsDialog, fileSettings);
			else if (fileTypeDropdown.selection.index == 5)
				buildDialogTIF(fileSettingsDialog, fileSettings);

			fileSettingsDialog.show();
		}
	}

	if (exportElementsDropdown) {
		exportElementsDropdown.onChange = function() {
			fileSettings.export = this.selection.index;
		}
	}

	if (elementsToAdd) {
		elementAddButton.onClick = function() {
			var thisExtension = 'psd',
				thisExtensionText = 'Photoshop (.psd)',
				thisExtensionMaxBitDepth = psdMaxBitDepth,
				firstElementTypeID = 0;

			if (elementFileTypeDropdown.selection.index == 1) {
				thisExtension = 'eps';
				thisExtensionText = 'EPS';
				thisExtensionMaxBitDepth = epsMaxBitDepth;
			}
			else if (elementFileTypeDropdown.selection.index == 2) {
				thisExtension = 'jpg';
				thisExtensionText = 'JPEG (.jpg)';
				thisExtensionMaxBitDepth = jpgMaxBitDepth;
			}
			else if (elementFileTypeDropdown.selection.index == 3) {
				thisExtension = 'png';
				thisExtensionText = 'PNG';
				thisExtensionMaxBitDepth = pngMaxBitDepth;
			}
			else if (elementFileTypeDropdown.selection.index == 4) {
				thisExtension = 'tga';
				thisExtensionText = 'Targa (.tga)';
				thisExtensionMaxBitDepth = tgaMaxBitDepth;
			}
			else if (elementFileTypeDropdown.selection.index == 5) {
				thisExtension = 'tif';
				thisExtensionText = 'TIFF (.tif)';
				thisExtensionMaxBitDepth = tifMaxBitDepth;
			}

			thisExtensionText += ' - ' + Math.min(documentBitDepth, thisExtensionMaxBitDepth) + '-bit - Full Res';
			elementListbox.add('item', thisExtensionText);

			if (elementTypesLength)
				firstElementTypeID = elementTypes[0].ID;

			// Add this item to the elementExports array
			elementExports.push({
				elementTypeID: firstElementTypeID,
				'export': 1,
				extension: thisExtension,
				bitDepth: Math.min(documentBitDepth, thisExtensionMaxBitDepth),
				resolution: 1,
				epsPreview: 0,
				epsEncoding: 0,
				epsHalftone: 0,
				epsTransferFunction: 0,
				epsPostScriptColor: 0,
				epsVectorData: 0,
				epsInterpolation: 0,
				jpgQuality: 3,
				jpgFormat: 0,
				jpgScans: 0,
				pngCompression: 0,
				pngInterlaced: 0,
				tgaResolution: 1,
				tgaCompress: 1,
				tifImageCompression: 0,
				tifSaveImagePyramid: 0,
				tifSaveTransparency: 0,
				tifPixelOrder: 0,
				tifByteOrder: 0,
				tifLayerCompression: 0
			});
		}

		elementEditButton.onClick = function() {
			elementDetailsDialog = new Window('dialog', 'Element Details', undefined);
			elementDetailsDialog.alignChildren = 'fill';

			var thisElement = elementExports[elementListbox.selection.index],
				thisElementText = elementListbox.selection.text,
				elementTypeGroup = elementDetailsDialog.add('group', undefined),
				elementTypeLabel = elementTypeGroup.add('statictext', undefined, 'Element Type:'),
				sizePanel = elementDetailsDialog.add('panel', undefined, 'Size'),
				bitDepthGroup = sizePanel.add('group', undefined),
				bitDepthLabel = bitDepthGroup.add('statictext', undefined, 'Bit Depth:'),
				resolutionGroup = sizePanel.add('group', undefined),
				resolutionLabel = resolutionGroup.add('statictext', undefined, 'Resolution:');

			elementTypeDropdown = elementTypeGroup.add('dropdownlist', undefined, '', { items: elementTypeNames });

			if (elementTypesLength) {
				elementTypeDropdown.selection = 0;
				var thisElementTypeID = thisElement.elementTypeID;
				for (var x = 0; x < elementTypesLength; x++) {
					if (thisElementTypeID == elementTypes[x].ID) {
						elementTypeDropdown.selection = x;
						break;
					}
				}
			}

			sizePanel.alignChildren = 'right';
			resolutionDropdown = resolutionGroup.add('dropdownlist', undefined, '', { items: ['Full', '1/2', '1/4'] });

			if (thisElementText.substring(0, 16) == 'Photoshop (.psd)') {
				elementDetailsDialog.text = 'Photoshop Options';
				bitDepthDropdown = bitDepthGroup.add('dropdownlist', undefined, '', { items: ['32', '16', '8'] });
				finishBuildingDialog(elementDetailsDialog, thisElement);
			}
			else if (thisElementText.substring(0, 3) == 'EPS') {
				buildDialogEPS(elementDetailsDialog, thisElement, bitDepthGroup);
			}
			else if (thisElementText.substring(0, 11) == 'JPEG (.jpg)') {
				buildDialogJPG(elementDetailsDialog, thisElement, bitDepthGroup);
			}
			else if (thisElementText.substring(0, 3) == 'PNG') {
				buildDialogPNG(elementDetailsDialog, thisElement, bitDepthGroup);
			}
			else if (thisElementText.substring(0, 12) == 'Targa (.tga)') {
				buildDialogTGA(elementDetailsDialog, thisElement, bitDepthGroup);
			}
			else if (thisElementText.substring(0, 11) == 'TIFF (.tif)') {
				buildDialogTIF(elementDetailsDialog, thisElement, bitDepthGroup);
			}

			// Set values for UI elements that all file types have in common
			bitDepthDropdown.selection = 0;

			var bitDepthDropdownLength = bitDepthDropdown.items.length;

			for (var x = 0; x < bitDepthDropdownLength; x++) {
				if (thisElement.bitDepth == bitDepthDropdown.items[x].text) {
					bitDepthDropdown.selection = x;
					break;
				}
			}

			if (thisElement.resolution == 1)
				resolutionDropdown.selection = 0;
			else if (thisElement.resolution == 0.5)
				resolutionDropdown.selection = 1;
			else if (thisElement.resolution == 0.25)
				resolutionDropdown.selection = 2;

			elementDetailsDialog.show();
		}

		elementDeleteButton.onClick = function() {
			var indexToRemove = elementListbox.selection.index,
				newElementListboxLength = elementListbox.items.length - 1;
			
			// Remove this item from the elementExports array
			elementExports.splice(indexToRemove, 1);

			elementListbox.remove(elementListbox.selection);
			elementEditButton.enabled = false;
			elementDeleteButton.enabled = false;

			if (indexToRemove >= newElementListboxLength)
				elementListbox.selection = indexToRemove - 1;
			else
				elementListbox.selection = indexToRemove;
		}

		elementListbox.onChange = function() {
			if (!this.selection) {
				elementEditButton.enabled = false;
				elementDeleteButton.enabled = false;

				elementDetailsText1.text = '';
				elementDetailsText2.text = '';
				elementDetailsText3.text = '';
				elementDetailsText4.text = '';
				elementDetailsText5.text = '';
				elementDetailsText6.text = '';
				elementDetailsText7.text = '';
				elementDetailsText8.text = '';
				elementDetailsText9.text = '';
				return;
			}

			var thisElement = elementExports[this.selection.index],
				thisExtension = thisElement.extension,
				thisElementTypeID = thisElement.elementTypeID,
				thisElementTypeName = '';

			for (var x = 0; x < elementTypesLength; x++) {
				if (thisElementTypeID == elementTypes[x].ID) {
					thisElementTypeName = elementTypes[x].name;
					break;
				}
			}

			elementEditButton.enabled = true;
			elementDeleteButton.enabled = true;

			if (thisExtension == 'psd') {
				elementDetailsText1.text = 'File Type: PSD';
				elementDetailsText2.text = 'Element Type: ' + thisElementTypeName;
				elementDetailsText3.text = '';
				elementDetailsText4.text = '';
				elementDetailsText5.text = '';
				elementDetailsText6.text = '';
				elementDetailsText7.text = '';
				elementDetailsText8.text = '';
				elementDetailsText9.text = '';
				//elementEditButton.enabled = false;
			}
			else if (thisExtension == 'eps') {
				var thisPreview = 'None',
					thisEncoding = 'ASCII';

				if (thisElement.epsPreview == 1)
					thisPreview = 'TIFF (1 bit/pixel)';
				else if (thisElement.epsPreview == 2)
					thisPreview = 'TIFF (8 bits/pixel)';

				if (thisElement.epsEncoding == 1)
					thisEncoding = 'Binary';
				else if (thisElement.epsEncoding == 2)
					thisEncoding = 'JPEG (low quality)';
				else if (thisElement.epsEncoding == 3)
					thisEncoding = 'JPEG (medium quality)';
				else if (thisElement.epsEncoding == 4)
					thisEncoding = 'JPEG (high quality)';
				else if (thisElement.epsEncoding == 5)
					thisEncoding = 'JPEG (maximum quality)';

				elementDetailsText1.text = 'File Type: EPS';
				elementDetailsText2.text = 'Element Type: ' + thisElementTypeName;
				elementDetailsText3.text = 'Preview: ' + thisPreview;
				elementDetailsText4.text = 'Encoding: ' + thisEncoding;
				elementDetailsText5.text = 'Include Halftone Screen: ' + (thisElement.epsHalftone == 0 ? 'No' : 'Yes');
				elementDetailsText6.text = 'Include Transfer Function: ' + (thisElement.epsTransferFunction == 0 ? 'No' : 'Yes');
				elementDetailsText7.text = 'PostScript Color Management: ' + (thisElement.epsPostScriptColor == 0 ? 'No' : 'Yes');
				elementDetailsText8.text = 'Include Vector Data: ' + (thisElement.epsVectorData == 0 ? 'No' : 'Yes');
				elementDetailsText9.text = 'Image Interpolation: ' + (thisElement.epsInterpolation == 0 ? 'No' : 'Yes');
			}
			else if (thisExtension == 'jpg') {
				var thisFormat = 'Baseline ("Standard")',
					thisScans = '';

				if (thisElement.jpgFormat == 1)
					thisFormat = 'Baseline Optimized';
				else if (thisElement.jpgFormat == 2)
					thisFormat = 'Progressive';

				if (thisElement.jpgFormat == 2)
					thisScans = 'Scans: ' + (parseInt(thisElement.jpgScans) + 3);

				elementDetailsText1.text = 'File Type: JPEG (.jpg)';
				elementDetailsText2.text = 'Element Type: ' + thisElementTypeName;
				elementDetailsText3.text = 'Quality: ' + thisElement.jpgQuality;
				elementDetailsText4.text = 'Format: ' + thisFormat;
				elementDetailsText5.text = thisScans;
				elementDetailsText6.text = '';
				elementDetailsText7.text = '';
				elementDetailsText8.text = '';
				elementDetailsText9.text = '';
			}
			else if (thisExtension == 'png') {
				var thisCompression = 'None / Fast',
					thisInterlace = 'None';

				if (thisElement.pngCompression == 1)
					thisCompression = 'Smallest / Slow';

				if (thisElement.pngInterlaced == 1)
					thisInterlace = 'Interlaced';

				elementDetailsText1.text = 'File Type: PNG';
				elementDetailsText2.text = 'Element Type: ' + thisElementTypeName;
				elementDetailsText3.text = 'Compression: ' + thisCompression;
				elementDetailsText4.text = 'Interlace: ' + thisInterlace;
				elementDetailsText5.text = '';
				elementDetailsText6.text = '';
				elementDetailsText7.text = '';
				elementDetailsText8.text = '';
				elementDetailsText9.text = '';
			}
			else if (thisExtension == 'tga') {
				var thisResolution = '16 bits/pixel';

				if (thisElement.tgaResolution == 1)
					thisResolution = '24 bits/pixel';
				else if (thisElement.tgaResolution == 2)
					thisResolution = '32 bits/pixel';

				elementDetailsText1.text = 'File Type: Targa (.tga)';
				elementDetailsText2.text = 'Element Type: ' + thisElementTypeName;
				elementDetailsText3.text = 'Resolution: ' + thisResolution;
				elementDetailsText4.text = 'Compress (RLE): ' + (thisElement.tgaCompress == 0 ? 'No' : 'Yes');
				elementDetailsText5.text = '';
				elementDetailsText6.text = '';
				elementDetailsText7.text = '';
				elementDetailsText8.text = '';
				elementDetailsText9.text = '';
			}
			else if (thisExtension == 'tif') {
				var thisImageCompression = 'None',
					thisPixelOrder = 'Interleaved (RGBRGB)',
					thisByteOrder = 'IBM PC',
					thisLayerCompression = 'RLE (faster saves, bigger files)';

				if (thisElement.tifImageCompression == 1)
					thisImageCompression = 'LZW';
				else if (thisElement.tifImageCompression == 2)
					thisImageCompression = 'ZIP';
				else if (thisElement.tifImageCompression == 3)
					thisImageCompression = 'JPEG';

				if (thisElement.tifPixelOrder == 1)
					thisPixelOrder = 'Per Channel (RRGGBB)';

				if (thisElement.tifByteOrder == 1)
					thisByteOrder = 'Macintosh';

				if (thisElement.tifLayerCompression == 1)
					thisLayerCompression = 'ZIP (slower saves, smaller files)';
				else if (thisElement.tifLayerCompression == 2)
					thisLayerCompression = 'Discard Layers and Save a Copy';

				elementDetailsText1.text = 'File Type: TIFF (.tif)';
				elementDetailsText2.text = 'Element Type: ' + thisElementTypeName;
				elementDetailsText3.text = 'Image Compression: ' + thisImageCompression;
				elementDetailsText4.text = (thisElement.tifImageCompression == 3 ? 'Quality: ' + thisElement.jpgQuality : '');
				elementDetailsText5.text = 'Save Image Pyramid: ' + (thisElement.tifSaveImagePyramid == 0 ? 'No' : 'Yes');
				elementDetailsText6.text = 'Save Transparency: ' + (thisElement.tifSaveTransparency == 0 ? 'No' : 'Yes');
				elementDetailsText7.text = 'Pixel Order: ' + thisPixelOrder;
				elementDetailsText8.text = 'Byte Order: ' + thisByteOrder;
				elementDetailsText9.text = 'Layer Compression: ' + thisLayerCompression;
			}
		}
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
			setPanelPrefs();
		}
		else if (action == 'saveAs' || action == 'versionUp' || action == 'publish') {
			
			if (action == 'saveAs') {
				if (!serverID) {
					alert('Error: No server specified!');
					return;
				}
				var newFileBasename = '',
					classID, className, saveOptions, extension;

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
			}

			var thisVersion = parseInt(maxVersion) + 1,
				thisComment = commentInput.text;

			if (action == 'saveAs') {
				if (saveFile(classID, className, serverID, serverPath, taskID, taskName, taskFolder, newFileBasename, thisComment, false, elementExports, fileSettings, thisVersion))
					alert('Save successful.');
				else
					alert('Error: Save failed!');

				setPanelPrefs();
			}
			else if (action == 'versionUp') {
				if (saveFile(metadata.classID, metadata.className, metadata.serverID, metadata.serverPath, metadata.taskID, metadata.taskName, metadata.taskFolder, metadata.basename, thisComment, false, elementExports, fileSettings, thisVersion))
					alert('New version saved.');
				else
					alert('Error: Version up failed!');
			}
			else if (action == 'publish') {
				if (!saveFile(metadata.classID, metadata.className, metadata.serverID, metadata.serverPath, metadata.taskID, metadata.taskName, metadata.taskFolder, metadata.basename, thisComment, true, elementExports, fileSettings, thisVersion))
					alert('Error: Publish failed!');
			}
		}
		/*
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
		*/

		nimPanel.close();
	}

	cancelButton.onClick = function() {
		if (action == 'open' || action == 'saveAs')
			setPanelPrefs();
		nimPanel.close();
	}

	if (action == 'open' || action == 'saveAs') {

		// Set starting values based on NIM preferences file
		jobID = parseInt(getPref('Photoshop', 'jobID')) || 0;
		setInitialSelection('ID', jobID, jobs, jobDropdown);

		if (serverDropdown) {
			serverID = parseInt(getPref('Photoshop', 'serverID')) || 0;
			setInitialSelection('ID', serverID, servers, serverDropdown);
		}

		assetID = parseInt(getPref('Photoshop', 'assetID')) || 0;
		setInitialSelection('ID', assetID, assets, assetDropdown);

		showID = parseInt(getPref('Photoshop', 'showID')) || 0;
		setInitialSelection('ID', showID, shows, showDropdown);

		shotID = parseInt(getPref('Photoshop', 'shotID')) || 0;
		setInitialSelection('ID', shotID, shots, shotDropdown);
		if (shotID) jobTabPanel.selection = shotsTab;

		taskID = parseInt(getPref('Photoshop', 'taskID')) || 0;
		setInitialSelection('ID', taskID, tasks, taskDropdown);

		if (filterDropdown) {
			showPub = parseInt(getPref('Photoshop', 'showPub')) || 0;
			filterDropdown.selection = showPub;
			filterDropdown.onChange();
		}

		basename = getPref('Photoshop', 'basename');
		setInitialSelection('basename', basename, basenames, basenameListbox);
	}
	else {
		var className = metadata.className;
		if (className == 'ASSET') {
			assetID = metadata.classID;
			shotID = 0;
		}
		else if (className == 'SHOT') {
			assetID = 0;
			shotID = metadata.classID;
		}
		jobID = 0;
		showID = 0;
		serverID = metadata.serverID;
		serverPath = metadata.serverPath;
		taskID = metadata.taskID;
		taskName = metadata.taskName;
		taskFolder = metadata.taskFolder;
		basename = metadata.basename;
	}

	if (loadingPanel) loadingPanel.close();
	nimPanel.show();
	return nimPanel;
}
