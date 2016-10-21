/* ****************************************************************************
#
# Filename: Photoshop/nimMain.jsx
# Version:  v2.0.0.160511
#
# Copyright (c) 2016 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ************************************************************************** */


// Declare global variables
var os = getOperatingSystem(),
	userID,
	username,
	ranGetUserID = false,
	winUserPath = '';

if (os == 'win') {
	try { winUserPath = $.getenv('userprofile'); }
	catch (e) { winUserPath = ''; }
}


// Add String.trim() functionality, for some reason it's missing
String.prototype.trim = function () {  
    return this.replace(/^\s+/,'').replace(/\s+$/,'');  
}  


// Adds JSON parsing support; https://github.com/douglascrockford/JSON-js/blob/master/json_parse.js
var json_parse=(function(){var d;var b;var a={'"':'"',"\\":"\\","/":"/",b:"\b",f:"\f",n:"\n",r:"\r",t:"\t"};var m;var k=function(n){throw {name:"SyntaxError",message:n,at:d,text:m};};var g=function(n){if(n&&n!==b){k("Expected '"+n+"' instead of '"+b+"'");}b=m.charAt(d);d+=1;return b;};var f=function(){var o;var n="";if(b==="-"){n="-";g("-");}while(b>="0"&&b<="9"){n+=b;g();}if(b==="."){n+=".";while(g()&&b>="0"&&b<="9"){n+=b;}}if(b==="e"||b==="E"){n+=b;g();if(b==="-"||b==="+"){n+=b;g();}while(b>="0"&&b<="9"){n+=b;g();}}o=+n;if(!isFinite(o)){k("Bad number");}else{return o;}};var h=function(){var p;var o;var q="";var n;if(b==='"'){while(g()){if(b==='"'){g();return q;}if(b==="\\"){g();if(b==="u"){n=0;for(o=0;o<4;o+=1){p=parseInt(g(),16);if(!isFinite(p)){break;}n=n*16+p;}q+=String.fromCharCode(n);}else{if(typeof a[b]==="string"){q+=a[b];}else{break;}}}else{q+=b;}}}k("Bad string");};var j=function(){while(b&&b<=" "){g();}};var c=function(){switch(b){case"t":g("t");g("r");g("u");g("e");return true;case"f":g("f");g("a");g("l");g("s");g("e");return false;case"n":g("n");g("u");g("l");g("l");return null;}k("Unexpected '"+b+"'");};var l;var i=function(){var n=[];if(b==="["){g("[");j();if(b==="]"){g("]");return n;}while(b){n.push(l());j();if(b==="]"){g("]");return n;}g(",");j();}}k("Bad array");};var e=function(){var n;var o={};if(b==="{"){g("{");j();if(b==="}"){g("}");return o;}while(b){n=h();j();g(":");if(Object.hasOwnProperty.call(o,n)){k("Duplicate key '"+n+"'");}o[n]=l();j();if(b==="}"){g("}");return o;}g(",");j();}}k("Bad object");};l=function(){j();switch(b){case"{":return e();case"[":return i();case'"':return h();case"-":return f();default:return(b>="0"&&b<="9")?f():c();}};return function(q,o){var n;m=q;d=0;b=" ";n=l();j();if(b){k("Syntax error");}return(typeof o==="function")?(function p(u,t){var s;var r;var w=u[t];if(w&&typeof w==="object"){for(s in w){if(Object.prototype.hasOwnProperty.call(w,s)){r=p(w,s);if(r!==undefined){w[s]=r;}else{delete w[s];}}}}return o.call(u,t,w);}({"":n},"")):n;};}());


// ------------------------------------------
// Allow connecting to a host via SSL / HTTPS
// From: https://forums.adobe.com/message/5663594#5663594

/*
 * @method : either "POST" or "GET"
 * @endpoint:  a string representing an URI endpoint for any given API
 * @query: a string to be sent with the request (i.e. 'firstName=Arie&lastName=Stavchansky').
 */

function webRequest(method, endpoint, query) {
	var response = null,
		tempFolderPath = '~/.nim/tmp/',
		winTempFolderPath = winUserPath + '\\.nim\\tmp\\',
		wincurl = nimScriptsPath + '\\nim_core\\curl.vbs',  // The path to the .vbs file
		curlCmd = '',
		userHeader,
		keyHeader;

	// If no username is set, check apiKeyRequired; if false, don't worry about lack of username
	if (!username) {
		// If "testAPI" query, run getUserID function
		// (which also checks the USER environment variable and tries to find a matching user in NIM)
		if (query == 'q=testAPI')
			userID = getUserID();
		// If "getUserID" query, ignore username
		else if (query.indexOf('q=getUserID') != -1)
			username = '';
		else if (apiKeyRequired) {
			// Get username from prefs
			username = getPref('NIM', 'User');
			if (!username)
				changeUserDialog();
		}
		else
			username = '';
	}

	try {
		var timestamp = Date.now(),
			nimTempFolder = new Folder(tempFolderPath),
			tempFilePath = tempFolderPath + timestamp,
			tempFile = new File(tempFilePath),
			winTempFilePath = winTempFolderPath + timestamp;

		if (!nimTempFolder.exists)
			nimTempFolder.create();

		if (os == 'win') {
			//if (username) userHeader = '/Username:"' + username + '" ';
			if (username) userHeader = '/Username:""' + username + '"" ';  // Double quotes needed for apiQuery VBScript
			else userHeader = '';
			//if (nimKey) keyHeader = '/ApiKey:"' + nimKey + '" ';
			if (nimKey) keyHeader = '/ApiKey:""' + nimKey + '"" ';  // Double quotes needed for apiQuery VBScript
			else keyHeader = '';

			//curlCmd = 'cscript "' + wincurl + '" /Method:"' + method + '" /URL:"' + endpoint + '" /Query:"' + query + '" /TempFilePath:"' + winTempFilePath + '" ' + userHeader + keyHeader + '//nologo';
			curlCmd = 'cscript ""' + wincurl + '"" /Method:""' + method + '"" /URL:""' + endpoint + '"" /Query:""' + query + '"" /TempFilePath:""' + winTempFilePath + '"" ' + userHeader + keyHeader + '//nologo';  // Double quotes needed for apiQuery VBScript
		}
		else {
			if (username) userHeader = '--header "X-NIM-API-USER: ' + username + '" ';
			else userHeader = '';
			if (nimKey) keyHeader = '--header "X-NIM-API-KEY: ' + nimKey + '" ';
			else keyHeader = '';

			if (method === "POST") {
				curlCmd = 'curl --silent --insecure ' + userHeader + keyHeader + '--data "' + query + '" ' + endpoint + ' > ' + tempFilePath;
			}
			else if (method === "GET") {
				curlCmd = 'curl --silent --get --insecure ' + userHeader + keyHeader + '--data "' + query + '" ' + endpoint + ' > ' + tempFilePath;
			}
		}

		if (os == 'win') {
			//app.system(curlCmd);
			//response = readFile(winTempFilePath);

			// Create apiQuery VBScript to run our curl VBScript instead of using app.system;
			// app.system flashes a command prompt (once for each query, which can occur frequently)
			var apiQueryFile = new File(winTempFolderPath + 'apiQuery.vbs'),
				winTempFile = new File(winTempFilePath);
			apiQueryFile.open('w');
			apiQueryFile.writeln('Set WshShell = CreateObject("WScript.Shell")');
			apiQueryFile.writeln('WshShell.Run "' + curlCmd + '", 0, True');
			apiQueryFile.close();
			apiQueryFile.execute();
			$.sleep(50);
			while (!winTempFile.exists) {
				//alert(query);
				$.sleep(100);
			}
			$.sleep(10);
			response = readFile(winTempFilePath);
			apiQueryFile.remove();
		}
		else {
			app.system(curlCmd);
			response = readFile(tempFilePath);
		}

		tempFile.remove();
	}
	catch (err) {
		alert(err);
		alert("Error\nUnable to make a `"+ method +"` request to the network endpoint.  Please try again.");
	}

	return response;
}

// ------------------------------------------


// Returns JS Object containing server response based on query;
// query argument is a JS object of parameters and values
function nimAPI(query) {
	var queryArray = [],
		queryString = '',
		reply = '',
		jsonData = null,
		jsonObject = null;

	for (var parameter in query)
		queryArray.push(parameter + '=' + encodeURIComponent(query[parameter]));
	if (queryArray.length)
		queryString = queryArray.join('&');
	else return false;

	var reply = webRequest('GET', nimAPIURL, queryString);
	if (!reply) return false;

	reply = reply.split('\n\n');
	if (reply.length)
		jsonData = reply[reply.length - 1];
	else return false;

	if (jsonData) {
		try {
			jsonObject = json_parse(jsonData);

			// Check first item in array to see if it resembles an error object.
			// If so, output appropriate message and return false.
			if (jsonObject.length && typeof jsonObject[0] == 'object') {

				if (jsonObject[0].keyRequired == 'true')
					apiKeyRequired = true;

				// 'API Key Not Found.' error returned on most API calls when key isn't sent but required;
				// when calling 'testAPI', this error is not returned, but 'keyRequired' and 'keyValid' can be tested
				if (jsonObject[0].error == 'API Key Not Found.' || (jsonObject[0].keyRequired == 'true' && jsonObject[0].keyValid == 'false')) {
					keyDialog('NIM API key not found.', 'NIM security is set to require the use of API keys. Please contact your NIM administrator to obtain a NIM API key.');
					return 'keyError';
				}
				else if (jsonObject[0].error) {
					var error = jsonObject[0].error;
					// If provided API key is incorrect or expired, these errors will ALWAYS be returned
					if (error == 'Failed to validate user.') {
						alert('Failed to validate user.\n\nPlease verify that both your username and API key are correct.');
						username = getPref('NIM', 'User');
						changeUserDialog();
						keyDialog();
					}
					else if (error == 'API Key Expired.')
						keyDialog('NIM API key expired!', 'NIM security is set to require the use of API keys. Please contact your NIM administrator to update your NIM API key.');
					else
						throw 'noResultNoError';
					return 'keyError';
				}
 			}

			return jsonObject;
 		}
		catch (e) {
			alert('Error: GET request to ' + nimAPIURL + '?' + queryString + ' returned the following:\n\n' + jsonData + '\n\nIf this looks correct, your script may not be recognizing how to convert JSON into a JavaScript object. This may be caused by an older version of After Effects. NIM has been tested with After Effects CS6 and above.');
 			return false;
		}
 	}
	else
		return false;
}


// Self-explanatory
function getOperatingSystem() {
	var opSys = $.os;
	if (opSys.indexOf('Windows') == 0)
		return 'win';
	else if (opSys.indexOf('Macintosh') == 0)
		return 'mac';
}


function saveKeyToPrefs() {
	var nimKeyFile = new File(nimKeyPath);
	nimKeyFile.open('w');
	nimKeyFile.writeln(nimKey);
	nimKeyFile.close();
	return true;
}


function keyDialog(messageTitle, message) {
	var createKeyDialog = new Window('dialog', 'NIM', undefined);

	if (messageTitle)
		var createKeyMessageTitle = createKeyDialog.add('statictext', undefined, messageTitle);
	
	if (message)
		var createKeyMessage = createKeyDialog.add('statictext', undefined, message);
		
	var keyGroup = createKeyDialog.add('group', undefined),
		keyLabel = keyGroup.add('statictext', undefined, 'NIM API Key: '),
		keyInput = keyGroup.add('edittext', [0, 0, 250, 20]),
		buttonGroup = createKeyDialog.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'OK'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel');

	//if (nimKey)
	//	keyInput.text = nimKey;

	confirmButton.onClick = function() {
		nimKey = keyInput.text;
		saveKeyToPrefs();
		createKeyDialog.close();
		var remoteScripts = getRemoteScripts(nimScriptsPath, thisObj);
		if (remoteScripts !== false)
			remoteScripts(thisObj);
	}

	cancelButton.onClick = function() {
		alert("You won't be able to connect to NIM until you enter a valid API key.");
		createKeyDialog.close();
	}

	createKeyDialog.show();
}


// Looks first in preferences for userID; if not found, compares username (taken from "USER" environment variable)
// to all usernames and full_names in database; if match, save userID to prefs and return it; if not found, return false
function getUserID() {
	var prefUser = getPref('NIM', 'User'),
		envUser;

	if (!buttonsToDisable) buttonsToDisable = [];

	if (prefUser) {
		var users = nimAPI({ q: 'getUserID', u: prefUser });
		if (users.length && users[0].ID) {
			ranGetUserID = true;
			username = prefUser;
			return users[0].ID;
		}
	}

	// If getUserID hasn't been run before, try to figure out user by looking at environment variables and by prompting user
	if (!ranGetUserID) {
		ranGetUserID = true;

		try { envUser = $.getenv('USER').toLowerCase(); }
		catch (e) { envUser = null; }

		if (envUser) {
			var users = nimAPI({ q: 'getUserID', u: envUser });
			if (users.length && users[0].ID) {
				setPref('NIM', 'User', envUser);
				username = envUser;
				alert('NIM has detected that you might be user "' + envUser + '"; if not, you can manually change your user.');
				return users[0].ID;
			}
		}

		changeUserDialog(buttonsToDisable);
	}
	else {
		var buttonsToDisableLength = buttonsToDisable.length;
		for (var x = 0; x < buttonsToDisableLength; x++)
			buttonsToDisable[x].enabled = false;
	}

	return false;
}


// Creates dialogue window where user can enter a comment; calls "callback" function with comment as argument
function commentDialog(callback) {
	var commentDialog = new Window('dialog', 'NIM', undefined),
		commentGroup = commentDialog.add('group', undefined),
		commentLabel = commentGroup.add('statictext', undefined, 'Comment: '),
		commentInput = commentGroup.add('edittext', [0, 0, 250, 20]),
		addElementCheckbox = commentGroup.add('checkbox', undefined, 'Add Element'),
		buttonGroup = commentDialog.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'OK'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel'),
		comment;

	confirmButton.onClick = function() {
		callback(commentInput.text, addElementCheckbox.value);
		commentDialog.close();
	}

	cancelButton.onClick = function() {
		commentDialog.close();
	}

	commentDialog.show();
}

// Prompts the user to select a username from a dropdown of all users;
// if passed an array of buttons, will disable them if no user has been selected
function changeUserDialog() {
	if (!buttonsToDisable) buttonsToDisable = [];

	function noUserSelected() {
		alert("You'll need to enter your username before you can use NIM.");
	}

	function userSelected() {
		alert('User changed to: ' + changeUserInput.text);
	}

	if (!username) username = '';

	var changeUserDialog = new Window('dialog', 'NIM', undefined),
		changeUserGroup = changeUserDialog.add('group', undefined),
		changeUserLabel = changeUserGroup.add('statictext', undefined, 'Change user: '),
		changeUserInput = changeUserGroup.add('edittext', [0, 0, 250, 20], username),
		buttonGroup = changeUserDialog.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'OK'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel');

	confirmButton.onClick = function() {
		if (!changeUserInput.text) {
			noUserSelected();
			username = '';
			setPref('NIM', 'User', '');
			changeUserDialog.close();
			return;
		}

		var users = nimAPI({ q: 'getUserID', u: changeUserInput.text });
		if (users.length && users[0].ID) {
			userID = users[0].ID;
			userSelected();
			username = changeUserInput.text;
			setPref('NIM', 'User', username);
			changeUserDialog.close();
		}
		else
			alert("User not found!");
	}

	cancelButton.onClick = function() {
		if (!userID)
			noUserSelected();
		changeUserDialog.close();
	}

	changeUserDialog.show();
}

// Gets project metadata
function getMetadata(property) {
	var metaData, schemaNS, metaValue;

	if (ExternalObject.AdobeXMPScript == undefined)
		ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');
	try { metaData = new XMPMeta(activeDocument.xmpMetadata.rawData); }
	catch(e) {
		alert('Error: Cannot get metadata when no file is open!');
		return;
	}

	schemaNS = XMPMeta.getNamespaceURI("NIM");
	if (schemaNS == "" || schemaNS == undefined) {
		return undefined;
	}
	metaValue = metaData.getProperty(schemaNS, property);
	if (!metaValue) return undefined;
	return metaValue.value;
}


// Gets NIM-related project metadata; look first in file (with getMetadata),
// then in manually-created NIM text file metadata if not found
function getNimMetadata() {
	// Try getting classID from file metadata
	var classID = getMetadata('classID');
	// If that worked, everything else should also be there
	if (classID) {
		return {
			classID: classID,
			className: getMetadata('className'),
			serverID: getMetadata('serverID'),
			serverPath: getMetadata('serverPath'),
			taskID: getMetadata('taskID'),
			taskName: getMetadata('taskName'),
			taskFolder: getMetadata('taskFolder'),
			basename: getMetadata('basename'),
			fileID: getMetadata('fileID')
		};
	}
	// If not, look in NIM Photoshop metadata file
	else {
		var thisNimFolderPath = activeDocument.path.absoluteURI + '/.nim/',
			photoshopFilePath = thisNimFolderPath + 'photoshop-metadata.nim',
			thisNimFolder = new Folder(thisNimFolderPath),
			photoshopFile = new File(photoshopFilePath),
			fileString = activeDocument.name + ':',
			currentLine,
			fileStringPos,
			foundFileString = false,
			equalPos,
			keyValue,
			metadata = {};

		// Will get a "no metadata" error back in file that calls this function
		if (!thisNimFolder.exists || !photoshopFile.exists)
			return false;

		// More specific error + the "no metadata" error
		if (!photoshopFile.open('r')) {
			alert('Error reading the following file: ' + photoshopFilePath);
			return false;
		}

		while (!photoshopFile.eof) {
			currentLine = photoshopFile.readln();
			fileStringPos = currentLine.indexOf(fileString);
			if (fileStringPos == -1) continue;
			foundFileString = true;
			while (!photoshopFile.eof) {
				currentLine = photoshopFile.readln();
				equalPos = currentLine.indexOf('=');
				if (equalPos == -1) break;
				keyValue = currentLine.split('=');
				metadata[keyValue[0].trim()] = keyValue[1].trim();
			}
			break;
		}

		photoshopFile.close();

		if (!foundFileString)
			return false;
		
		return metadata;
	}
}


// Sets NIM-related project metadata
function setNimMetadata(data) {
	var proj = app.project,
		metaData, schemaNS;
 
	if (ExternalObject.AdobeXMPScript == undefined)
		ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');

	try { metaData = new XMPMeta(activeDocument.xmpMetadata.rawData); }
	catch(e) {
		alert('Error: Cannot set metadata when no file is open!');
		return;
	}

	schemaNS = XMPMeta.getNamespaceURI("NIM");
	if (schemaNS == "" || schemaNS == undefined) {
		XMPMeta.registerNamespace("NIM", "NIM");
		schemaNS = XMPMeta.getNamespaceURI("NIM");
	}
	try {
		metaData.setProperty(schemaNS, "NIM:classID", data.classID);
		metaData.setProperty(schemaNS, "NIM:className", data.className);
		metaData.setProperty(schemaNS, "NIM:serverID", data.serverID);
		metaData.setProperty(schemaNS, "NIM:serverPath", data.serverPath);
		metaData.setProperty(schemaNS, "NIM:taskID", data.taskID);
		metaData.setProperty(schemaNS, "NIM:taskName", data.taskName);
		metaData.setProperty(schemaNS, "NIM:taskFolder", data.taskFolder);
		metaData.setProperty(schemaNS, "NIM:basename", data.basename);
		metaData.setProperty(schemaNS, "NIM:fileID", data.fileID);
	} catch(err) {
		alert(err.toString());
		return false;
	}
	activeDocument.xmpMetadata.rawData = metaData.serialize();
	return true;
}


// Sets NIM-related project metadata in "thisfilefolder/.nim/photoshop-metadata.nim"; for files that might not allow metadata to be stored in them
function setNimManualMetadata(data, path, filename) {
	var thisNimFolderPath = path + '.nim/',
		photoshopFilePath = thisNimFolderPath + 'photoshop-metadata.nim',
		thisNimFolder = new Folder(thisNimFolderPath),
		photoshopFile = new File(photoshopFilePath),
		photoshopFileTempPath = thisNimFolderPath + 'photoshop-metadata-temp.nim',
		photoshopFileTemp,
		fileString = filename + ':',
		currentLine,
		fileStringPos,
		foundFileString = false,
		thisMetadataString = '';

	if (!thisNimFolder.exists) {
		if (!thisNimFolder.create()) {
			alert('Error creating the following directory to store NIM metadata: ' + thisNimFolderPath);
			return false;
		}
	}

	for (var key in data)
		thisMetadataString += '\n  ' + key + '=' + data[key];

	thisMetadataString += '\n';

	if (photoshopFile.exists) {
		if (!photoshopFile.open('e')) {
			alert('Error editing the following file: ' + photoshopFilePath);
			return false;
		}
		while (!photoshopFile.eof)  // Read lines until we get to end of file so we don't overwrite existing stuff
			photoshopFile.readln();
	}
	else {
		if (!photoshopFile.open('w')) {
			alert('Error creating the following file: ' + photoshopFilePath);
			return false;
		}
	}

	photoshopFile.lineFeed = 'Unix';

	// Write metadata for this new file
	photoshopFile.writeln(fileString + thisMetadataString);
	photoshopFile.close();
	return true;
}


// Gets a preference value from the NIM preferences file
function getPref(prefPrefix, prefName) {
	var nimPrefsFile = new File(nimPrefsPath),
		prefString = prefPrefix + '_' + prefName + '=',
		currentLine,
		prefPos,
		foundPref = false;

	if (!nimPrefsFile.exists)
		return false;

	nimPrefsFile.open('r');
	while (!nimPrefsFile.eof) {
		currentLine = nimPrefsFile.readln();
		prefPos = currentLine.indexOf(prefString);
		if (prefPos != -1) {
			foundPref = currentLine.substr(prefPos + prefString.length);
			break;
		}
	}
	nimPrefsFile.close();

	if (foundPref) return foundPref;
	else return false;
}


function setPref(prefPrefix, prefName, prefValue) {
	var nimPrefsFile = new File(nimPrefsPath),
		nimPrefsFileTemp,
		nimPrefsFileTempPath = nimPrefsPath + 'temp',
		prefString = prefPrefix + '_' + prefName + '=',
		currentLine,
		prefPos,
		foundBlock = false,
		foundPref = false;

	if (!nimPrefsFile.exists)
		createNimPrefsFile();

	nimPrefsFile.copy(nimPrefsFileTempPath);
	nimPrefsFileTemp = new File(nimPrefsFileTempPath);
	if (!nimPrefsFileTemp.open('r'))
		return false;

	nimPrefsFile.lineFeed = 'Unix';
	nimPrefsFile.open('w');
	while (!nimPrefsFileTemp.eof) {
		currentLine = nimPrefsFileTemp.readln();
		if (!foundPref) {
			prefPos = currentLine.indexOf(prefString);
			if (prefPos != -1) {
				foundBlock = true;
				foundPref = true;
				currentLine = currentLine.substr(0, prefPos + prefString.length) + prefValue;
			}
			else {
				prefPos = currentLine.indexOf(prefPrefix);
				if (prefPos != -1)
					foundBlock = true;
				else if (foundBlock) {   // If some correct-prefixed items were found but end of them was reached,
					nimPrefsFile.writeln(prefString + prefValue);  // add this key + value entry to end of block
					foundPref = true;
				}
			}
		}
		nimPrefsFile.writeln(currentLine);
	}

	if (!foundPref) {  // If no matching item was found, add new entry
		if (!foundBlock) nimPrefsFile.writeln('');  // If new block, skip a line
		nimPrefsFile.writeln(prefString + prefValue);
	}

	nimPrefsFileTemp.close();
	nimPrefsFile.close();
	nimPrefsFileTemp.remove();
	return true;
}


// Given a file (an object with all the properties that an item in the "element_exports" table has),
// returns an appropriate saveOptions object to pass to Photoshop's "save as" function
function getFileSaveOptions(file) {
	var fileExtension = file.extension,
		fileSaveOptions;

	if (fileExtension == 'psd') {
		fileSaveOptions = new PhotoshopSaveOptions();
	}
	else if (fileExtension == 'eps') {
		var preview = Preview.NONE,
			encoding = SaveEncoding.ASCII;

		if (file.epsPreview == 1)
			preview = Preview.MONOCHROMETIFF;
		else if (file.epsPreview == 2)
			preview = Preview.EIGHTBITTIFF;

		if (file.epsEncoding == 1)
			encoding = SaveEncoding.BINARY;
		else if (file.epsEncoding == 2)
			encoding = SaveEncoding.JPEGLOW;
		else if (file.epsEncoding == 3)
			encoding = SaveEncoding.JPEGMEDIUM;
		else if (file.epsEncoding == 4)
			encoding = SaveEncoding.JPEGHIGH;
		else if (file.epsEncoding == 5)
			encoding = SaveEncoding.JPEGMAXIMUM;

		fileSaveOptions = new EPSSaveOptions({
			preview: preview,
			encoding: encoding,
			halftoneScreen: (file.epsHalftone == 0 ? false : true),
			transferFunction: (file.epsTransferFunction == 0 ? false : true),
			psColorManagement: (file.epsPostScriptColor == 0 ? false : true),
			vectorData: (file.epsVectorData == 0 ? false : true),
			interpolation: (file.epsInterpolation == 0 ? false : true)
		});
	}
	else if (fileExtension == 'jpg') {
		var formatOptions = FormatOptions.STANDARDBASELINE; 

		if (file.jpgFormat == 1)
			formatOptions = FormatOptions.OPTIMIZEDBASELINE;
		else if (file.jpgFormat == 2)
			formatOptions = FormatOptions.PROGRESSIVE;

		fileSaveOptions = new JPEGSaveOptions({
			jpegQuality: parseInt(file.jpgQuality),
			formatOptions: formatOptions,
			scans: parseInt(file.jpgScans) + 3
		});
	}
	else if (fileExtension == 'png') {
		fileSaveOptions = new PNGSaveOptions({
			compression: (file.pngCompression == 0 ? 0 : 9),
			interlaced: (file.pngInterlaced == 0 ? false : true)
		});
	}
	else if (fileExtension == 'tga') {
		var resolution = TargaBitsPerPixels.SIXTEEN;

		if (file.tgaResolution == 1)
			resolution = TargaBitsPerPixels.TWENTYFOUR;
		else if (file.tgaResolution == 2)
			resolution = TargaBitsPerPixels.THIRTYTWO;

		fileSaveOptions = new TargaSaveOptions({
			resolution: resolution,
			rleCompression: (file.tgaCompress == 1 ? true : false)
		});
	}
	else if (fileExtension == 'tif') {
		var imageCompression = TIFFEncoding.NONE;

		if (file.tifImageCompression == 1)
			imageCompression = TIFFEncoding.TIFFLZW;
		else if (file.tifImageCompression == 2)
			imageCompression = TIFFEncoding.TIFFZIP;
		else if (file.tifImageCompression == 3)
			imageCompression = TIFFEncoding.JPEG;

		fileSaveOptions = new TiffSaveOptions({
			imageCompression: imageCompression,
			jpegQuality: parseInt(file.jpgQuality),
			saveImagePyramid: (file.tifSaveImagePyramid == 1 ? true : false),
			transparency: (file.tifSaveTransparency == 1 ? true : false),
			interleaveChannels: (file.tifPixelOrder == 0 ? true : false),
			byteOrder: (file.tifByteOrder == 1 ? ByteOrder.MACOS : ByteOrder.IBM),
			layers: (file.tifLayerCompression == 2 ? false : true),
			layerCompression: (file.tifLayerCompression == 1 ? LayerCompression.ZIP : LayerCompression.RLE)
		});
	}

	return fileSaveOptions;
}


// Saves a file and writes it to NIM API; className = 'ASSET' or 'SHOT', classID = assetID or shotID
function saveFile(classID, className, serverID, serverPath, taskID, taskName, taskFolder, basename, comment, publish, elementExports, fileSettings, version) {
	var oldDocument = activeDocument,
		path = serverPath,
		folder,
		newFile,
		itemPaths,
		isPub = 0,
		isWork = 1,
		newFileName = '',
		fullFilePath = '',
		nimMetadata,
		metadataSet,
		newFileID,
		filesCreated = 0,
		workingFilePath = '',
		extension = fileSettings.extension,
		fileSaveOptions,
		elementExportsLength = elementExports.length,
		elementExportPrefix;

	itemPaths = nimAPI({ q: 'getPaths', type: className.toLowerCase(), ID: classID });
	if (!itemPaths || !itemPaths['root']) {
		alert('Error: Could not find root path for selected ' + className + ' in database!');
		return false;
	}
	path += (os == 'win' ? '\\' : '/') + itemPaths['root'];
	folder = new Folder(path);
	if (!folder.exists) {
		alert('Error: The folder ' + path + ' does not exist!');
		return false;
	}
	path += '/' + taskFolder + '/' + basename + '/';
	if (os == 'win') path = path.replace(/\//g, '\\');
	else path = path.replace(/\\/g, '/');
	folder = new Folder(path);
	if (!folder.exists) {
		if (!folder.create()) {
			alert('Error creating the following directory: ' + path);
			return false;
		}
	}

	if (parseInt(version) < 10) version = '0' + parseInt(version);
	newFileName = basename + '_v' + version + '.' + extension;
	fullFilePath = path + newFileName;
	newFile = new File(fullFilePath);
	elementExportPrefix = basename + '_v' + version + '_e';

	while (newFile.exists) {
		version = parseInt(version) + 1;
		if (parseInt(version) < 10) version = '0' + parseInt(version);
		newFileName = basename + '_v' + version + '.' + extension;
		fullFilePath = path + newFileName;
		newFile = new File(fullFilePath);
		elementExportPrefix = basename + '_v' + version + '_e';
	}

	while (filesCreated == 0 || (publish && filesCreated == 1)) {

		// Add file to files table in NIM and get new fileID
		newFileID = nimAPI({
			q: 'addFile',
			itemID: classID,
			'class': className,
			task_type_ID: taskID,
			task_type_folder: taskFolder,
			userID: userID,
			basename: basename,
			filename: newFileName,
			filepath: path,
			ext: '.' + extension,
			version: version,
			note: comment,
			serverID: serverID,
			isPub: isPub,
			isWork: isWork
		});

		nimMetadata = {
			classID: classID,
			className: className,
			serverID: serverID,
			serverPath: serverPath,
			taskID: taskID,
			taskName: taskName,
			taskFolder: taskFolder,
			basename: basename,
			fileID: newFileID
		};

		metadataSet = setNimMetadata(nimMetadata);

		if (!metadataSet)
			metadataSet = setNimManualMetadata(nimMetadata, path, newFileName);

		if (!metadataSet) {
			alert('Error setting metadata; project could not be saved!');
			return false;
		}

		// Generate a fileSaveOptions object
		fileSaveOptions = getFileSaveOptions(fileSettings);

		// Actually save the file
		try {
			activeDocument.saveAs(newFile, fileSaveOptions, true, Extension.LOWERCASE);
		}
		catch (e) {
			alert(e);
			return false;
		}

		// Save this file's save options
		nimAPI({ q: 'setFileSettings', fileID: newFileID, fileSettings: fileSettings });

		// Save this file's element export options
		nimAPI({ q: 'setElementExports', fileID: newFileID, exports: elementExports });

		// SAVE ALL ELEMENT EXPORTS HERE IF WE WANT TO SAVE THEM TWICE WHEN PUBLISHING (once for normal version, once for published)
		// Currently saving element exports after this while loop

		// If publishing, prepare to save another version
		if (publish && filesCreated == 0) {
			isPub = 1;
			isWork = 0;
			workingFilePath = fullFilePath;
			if (parseInt(version) < 10) version = '0' + parseInt(version);
			newFileName = basename + '_v' + version + '_PUB.' + extension;
			elementExportPrefix = basename + '_v' + version + '_PUB_e';
			fullFilePath = path + newFileName;
			newFile = new File(fullFilePath);
		}
		filesCreated++;
	}

	// Open newly-saved file, since Save As seems to be treated like Export in Photoshop
	oldDocument.close(SaveOptions.DONOTSAVECHANGES);
	app.open(newFile);

	// Save all element exports
	// Check file export settings to make sure elements should be exported
	if (elementExportsLength && (fileSettings.export == 1 || (publish && fileSettings.export == 2))) {
		var originalBitDepth = activeDocument.bitsPerChannel,
			originalWidth = activeDocument.width.value,
			elementVersion = 0,
			bitDepthAndResolution = {
				'32': {
					'1': [],
					'0.5': [],
					'0.25': []
				},
				'16': {
					'1': [],
					'0.5': [],
					'0.25': []
				},
				'8': {
					'1': [],
					'0.5': [],
					'0.25': []
				},
			};

		if (originalBitDepth == BitsPerChannelType.THIRTYTWO)
			originalBitDepth = 32;
		else if (originalBitDepth == BitsPerChannelType.SIXTEEN)
			originalBitDepth = 16;
		else if (originalBitDepth == BitsPerChannelType.EIGHT)
			originalBitDepth = 8;

		// Save elementExports array into bitDepthAndResolution object to organize the elements by their bit depth and resolution
		for (var x = 0; x < elementExportsLength; x++) {
			var element = elementExports[x];
			bitDepthAndResolution[parseFloat(element.bitDepth).toString()][parseFloat(element.resolution).toString()].push(element);
		}

		app.displayDialogs = DialogModes.NO;

		// Go through each category of bitDepthAndResolution object
		for (var bitDepth in bitDepthAndResolution) {
			var thisBitDepthObj = bitDepthAndResolution[bitDepth];
			for (var resolution in thisBitDepthObj) {
				var thisResolutionArray = thisBitDepthObj[resolution],
					thisResolutionArrayLength = thisResolutionArray.length;
			
				// Ignore empty arrays
				if (!thisResolutionArrayLength) continue;

				// Convert document to correct bit depth
				if (bitDepth == '32')
					activeDocument.bitsPerChannel = BitsPerChannelType.THIRTYTWO;
				else if (bitDepth == '16')
					activeDocument.bitsPerChannel = BitsPerChannelType.SIXTEEN;
				else if (bitDepth == '8')
					activeDocument.bitsPerChannel = BitsPerChannelType.EIGHT;

				// Convert document to correct resolution
				var newWidth = activeDocument.width,
					newHeight = activeDocument.height;

				if (resolution == '0.5') {
					newWidth.value = newWidth.value / 2;
					newHeight.value = newHeight.value / 2;
				}
				else if (resolution == '0.25') {
					newWidth.value = newWidth.value / 4;
					newHeight.value = newHeight.value / 4;
				}

				if (newWidth.value != activeDocument.width.value)
					activeDocument.resizeImage(newWidth, newHeight);

				// Save all elements with this bit depth / resolution combo
				for (var x = 0; x < thisResolutionArrayLength; x++) {
					var element = thisResolutionArray[x],
						elementExtension = element.extension,
						elementSaveOptions = getFileSaveOptions(element);

					elementVersion++;
					if (elementVersion < 10) elementVersion = '0' + elementVersion;
					
					var newElementName = elementExportPrefix + elementVersion + '.' + elementExtension,
						fullElementFilePath = path + newElementName;
						newElementFile = new File(fullElementFilePath);
					
					nimAPI({ q: 'addElement', parent: className.toLowerCase(), parentID: classID, userID: userID, typeID: element.elementTypeID, path: path, name: newElementName, isPublished: (publish == 1 ? 'True' : 'False') });

					try {
						activeDocument.saveAs(newElementFile, elementSaveOptions, true, Extension.LOWERCASE);
					}
					catch (e) {
						alert(e);
						return false;
					}
				}

				// If bit depth and/or resolution isn't same as original, close this document and
				// re-open original, just-saved-before-all-these-elements file
				if (bitDepth != originalBitDepth || activeDocument.width.value != originalWidth) {
					activeDocument.close(SaveOptions.DONOTSAVECHANGES);
					app.open(newFile);
				}
			}
		}  // for (var bitDepth in bitDepthAndResolution)

		app.displayDialogs = DialogModes.ERROR;

	}  // if (elementExportsLength)

	if (publish) {
		nimAPI({ q: 'publishSymlink', fileID: newFileID });
		if (confirm('Project published. Revert to working version?')) {
			newFile = new File(workingFilePath);
			if (!newFile.exists) {
				alert("Error: Working file wasn't successfully created!");
				return;
			}
			try { app.open(newFile); }
			catch (e) {
				alert(e);
				return;
			}
		}
	}

	return true;
}

os = getOperatingSystem();
var foundUserID = getUserID();
if (foundUserID)
	userID = foundUserID;
