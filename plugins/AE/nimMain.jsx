/* ****************************************************************************
#
# Filename: AE/nimMain.jsx
# Version:  v0.7.3.150625
#
# Copyright (c) 2015 NIM Labs LLC
# All rights reserved.
#
# Use of this software is subject to the terms of the NIM Labs license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ************************************************************************** */


// Declare global variables
var os, userID;


// Adds JSON parsing support; https://github.com/douglascrockford/JSON-js/blob/master/json2.js
if(typeof JSON!=="object"){JSON={}}(function(){"use strict";function f(e){return e<10?"0"+e:e}function quote(e){escapable.lastIndex=0;return escapable.test(e)?'"'+e.replace(escapable,function(e){var t=meta[e];return typeof t==="string"?t:"\\u"+("0000"+e.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+e+'"'}function str(e,t){var n,r,i,s,o=gap,u,a=t[e];if(a&&typeof a==="object"&&typeof a.toJSON==="function"){a=a.toJSON(e)}if(typeof rep==="function"){a=rep.call(t,e,a)}switch(typeof a){case"string":return quote(a);case"number":return isFinite(a)?String(a):"null";case"boolean":case"null":return String(a);case"object":if(!a){return"null"}gap+=indent;u=[];if(Object.prototype.toString.apply(a)==="[object Array]"){s=a.length;for(n=0;n<s;n+=1){u[n]=str(n,a)||"null"}i=u.length===0?"[]":gap?"[\n"+gap+u.join(",\n"+gap)+"\n"+o+"]":"["+u.join(",")+"]";gap=o;return i}if(rep&&typeof rep==="object"){s=rep.length;for(n=0;n<s;n+=1){if(typeof rep[n]==="string"){r=rep[n];i=str(r,a);if(i){u.push(quote(r)+(gap?": ":":")+i)}}}}else{for(r in a){if(Object.prototype.hasOwnProperty.call(a,r)){i=str(r,a);if(i){u.push(quote(r)+(gap?": ":":")+i)}}}}i=u.length===0?"{}":gap?"{\n"+gap+u.join(",\n"+gap)+"\n"+o+"}":"{"+u.join(",")+"}";gap=o;return i}}if(typeof Date.prototype.toJSON!=="function"){Date.prototype.toJSON=function(){return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(){return this.valueOf()}}var cx,escapable,gap,indent,meta,rep;if(typeof JSON.stringify!=="function"){escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;meta={"\b":"\\b","  ":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"};JSON.stringify=function(e,t,n){var r;gap="";indent="";if(typeof n==="number"){for(r=0;r<n;r+=1){indent+=" "}}else if(typeof n==="string"){indent=n}rep=t;if(t&&typeof t!=="function"&&(typeof t!=="object"||typeof t.length!=="number")){throw new Error("JSON.stringify")}return str("",{"":e})}}if(typeof JSON.parse!=="function"){cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;JSON.parse=function(text,reviver){function walk(e,t){var n,r,i=e[t];if(i&&typeof i==="object"){for(n in i){if(Object.prototype.hasOwnProperty.call(i,n)){r=walk(i,n);if(r!==undefined){i[n]=r}else{delete i[n]}}}}return reviver.call(e,t,i)}var j;text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(e){return"\\u"+("0000"+e.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,""))){j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}})()


// Returns JS Object containing server response based on query;
// query argument is a JS object of parameters and values
function nimAPI(query) {
	var nimAPIHostAndPort = nimAPIHost,
		queryArray = [],
		queryString = '',
		reply = '',
		conn = new Socket,
		jsonData = null,
		jsonObject = null;

	if (nimAPIHostAndPort.indexOf(':') == -1)
		nimAPIHostAndPort += ':80';

	// Access NIM
	if (conn.open(nimAPIHostAndPort)) {
		for (var parameter in query)
			queryArray.push(parameter + '=' + encodeURIComponent(query[parameter]));
		if (queryArray.length)
			queryString = '?' + queryArray.join('&');
		else return false;

		// send a HTTP GET request
		conn.write ('GET ' + nimAPIURL + queryString + ' HTTP/1.0\n\n');
		// and read the server's reply
		reply = conn.read(999999);
		conn.close();
		
		reply = reply.split('\n\n');
		if (reply.length)
			jsonData = reply[reply.length - 1];
		else return false;

		if (jsonData) {
			try {
				jsonObject = JSON.parse(jsonData);
				return jsonObject;
			}
			catch (e) {
				alert('Error: GET request to ' + nimAPIURL + queryString + ' returned the following:\n\n' + jsonData + '\n\nIf this looks correct, your script may not be recognizing how to convert JSON into a JavaScript object. This may be caused by an older version of After Effects. NIM has been tested with After Effects CS6 and above.');
				return false;
			}
		}
		else
			return false;
	}
}


// Self-explanatory
function getOperatingSystem() {
	var opSys = $.os;
	if (opSys.indexOf('Windows') == 0)
		return 'win';
	else if (opSys.indexOf('Macintosh') == 0)
		return 'mac';
}


// Looks first in preferences for userID; if not found, compares username (taken from "USER" environment variable)
// to all usernames and full_names in database; if match, save userID to prefs and return it; if not found, return false;
// passes 'buttonsToDisable' along to 'changeUserDialog' if no user is selected
function getUserID(buttonsToDisable) {
	var prefUser = getPref('NIM', 'User'),
		envUser,
		allUsers = nimAPI({ q: 'getUsers' }),
		allUsersLength = allUsers.length,
		guessedUserID = null;

	if (prefUser) {
		for (var x = 0; x < allUsersLength; x++) {
			if (allUsers[x].username == prefUser)
				return allUsers[x].ID;
		}
	}
	
	try { envUser = $.getenv('USER').toLowerCase(); }
	catch (e) { envUser = null; }

	if (envUser) {
		for (var x = 0; x < allUsersLength; x++) {
			if (envUser == allUsers[x].username.toLowerCase() || envUser == allUsers[x].full_name.toLowerCase()) {
				guessedUserID = allUsers[x].ID;
				setPref('NIM', 'User', envUser);
				alert('NIM has detected that you might be ' + allUsers[x].full_name + '; if not, manually select your username via the "Change Users" menu item.');
				return guessedUserID;
			}
		}
	}

	changeUserDialog(buttonsToDisable);
	return false;
}


// Creates dialogue window where user can enter a comment; calls "callback" function with comment as argument
function commentDialog(callback) {
	var commentDialog = new Window('dialog', 'NIM', undefined),
		commentGroup = commentDialog.add('group', undefined),
		commentLabel = commentGroup.add('statictext', undefined, 'Comment: '),
		commentInput = commentGroup.add('edittext', [0, 0, 250, 20]),
		buttonGroup = commentDialog.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'OK'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel'),
		comment;

	confirmButton.onClick = function() {
		callback(commentInput.text);
		commentDialog.close();
	}

	cancelButton.onClick = function() {
		commentDialog.close();
	}

	commentDialog.show();
}

// Prompts the user to select a username from a dropdown of all users;
// if passed an array of buttons, will disable them if no user has been selected
function changeUserDialog(buttonsToDisable) {
	function noUserSelected() {
		var buttonsToDisableLength = buttonsToDisable.length;
		alert("You'll need to select a user before you can use NIM.");
		for (var x = 0; x < buttonsToDisableLength; x++)
			buttonsToDisable[x].enabled = false;
	}

	function userSelected() {
		var buttonsToDisableLength = buttonsToDisable.length;
		alert('User changed to: ' + changeUserDropdown.selection.text);
		for (var x = 0; x < buttonsToDisableLength; x++)
			buttonsToDisable[x].enabled = true;
	}

	var allUsers = nimAPI({ q: 'getUsers' }),
		allUsersLength = allUsers.length,
		allUsernames = [],
		currentUserIndex = null,
		changeUserDialog = new Window('dialog', 'NIM', undefined),
		changeUserGroup = changeUserDialog.add('group', undefined),
		changeUserLabel = changeUserGroup.add('statictext', undefined, 'Change user: '),
		changeUserDropdown,
		buttonGroup = changeUserDialog.add('group', undefined),
		confirmButton = buttonGroup.add('button', undefined, 'OK'),
		cancelButton = buttonGroup.add('button', undefined, 'Cancel');

	for (var x = 0; x < allUsersLength; x++) {
		var thisUser = allUsers[x];
		allUsernames.push(thisUser.username);
		if (thisUser.ID == userID)
			currentUserIndex = x;
	}

	changeUserDropdown = changeUserGroup.add('dropdownlist', undefined, '', { items: allUsernames });
	changeUserDropdown.selection = currentUserIndex;

	confirmButton.onClick = function() {
		if (changeUserDropdown.selection === null) {
			noUserSelected();
			return;
		}
		var newUser = allUsers[changeUserDropdown.selection.index];
		userID = newUser.ID;
		setPref('NIM', 'User', newUser.username);
		userSelected();
		changeUserDialog.close();
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
	var proj = app.project,
		metaData, schemaNS, metaValue;
 
	if (ExternalObject.AdobeXMPScript == undefined)
		ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');

	metaData = new XMPMeta(proj.xmpPacket);
	schemaNS = XMPMeta.getNamespaceURI("NIM");
	if (schemaNS == "" || schemaNS == undefined) {
		return undefined;
	}
	metaValue = metaData.getProperty(schemaNS, property);
	if (!metaValue) return undefined;
	return metaValue.value;
}


// Gets NIM-related project metadata
function getNimMetadata() {
	return {
		classID: getMetadata('classID'),
		className: getMetadata('className'),
		serverID: getMetadata('serverID'),
		serverPath: getMetadata('serverPath'),
		taskID: getMetadata('taskID'),
		taskName: getMetadata('taskName'),
		taskFolder: getMetadata('taskFolder'),
		basename: getMetadata('basename')
	};
}


// Sets NIM-related project metadata
function setNimMetadata(data) {
	var proj = app.project,
		metaData, schemaNS;
 
	if (ExternalObject.AdobeXMPScript == undefined)
		ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');

	metaData = new XMPMeta(proj.xmpPacket);
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
	} catch(err) {
		alert(err.toString());
		return false;
	}
	proj.xmpPacket = metaData.serialize();
	return true;
}


// Sets NIM fileID in file metadata
function setNimFileIdMetadata(fileID) {
	var proj = app.project,
		metaData, schemaNS;
 
	if (ExternalObject.AdobeXMPScript == undefined)
		ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');

	metaData = new XMPMeta(proj.xmpPacket);
	schemaNS = XMPMeta.getNamespaceURI("NIM");
	if (schemaNS == "" || schemaNS == undefined) {
		XMPMeta.registerNamespace("NIM", "NIM");
		schemaNS = XMPMeta.getNamespaceURI("NIM");
	}
	try {
		metaData.setProperty(schemaNS, "NIM:fileID", fileID);
	} catch(err) {
		alert(err.toString());
		return false;
	}
	proj.xmpPacket = metaData.serialize();
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

	nimPrefsFile.lineFeed = 'Unix';
	nimPrefsFile.copy(nimPrefsFileTempPath);
	nimPrefsFileTemp = new File(nimPrefsFileTempPath);
	if (!nimPrefsFileTemp.open('r'))
		return false;
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


// Saves a file and writes it to NIM API; className = 'ASSET' or 'SHOT', classID = assetID or shotID
function saveFile(classID, className, serverID, serverPath, taskID, taskName, taskFolder, basename, comment, publish, version) {
	var path = serverPath,
		folder,
		newFile,
		itemPaths,
		isPub = 0,
		isWork = 1,
		newFileName = '',
		fullFilePath = '',
		metadataSet,
		newFileID,
		filesCreated = 0,
		workingFilePath = '';

	metadataSet = setNimMetadata({
		classID: classID,
		className: className,
		serverID: serverID,
		serverPath: serverPath,
		taskID: taskID,
		taskName: taskName,
		taskFolder: taskFolder,
		basename: basename,
		comment: comment
	});

	if (!metadataSet) {
		alert('Error setting metadata; project could not be saved!');
		return false;
	}

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

	newFileName = basename + '_v' + version + '.aep';
	fullFilePath = path + newFileName;
	newFile = new File(fullFilePath);

	while (newFile.exists) {
		version = parseInt(version) + 1;
		if (parseInt(version) < 10) version = '0' + parseInt(version);
		newFileName = basename + '_v' + version + '.aep';
		fullFilePath = path + newFileName;
		newFile = new File(fullFilePath);
	}

	while (filesCreated == 0 || (publish && filesCreated == 1)) {
		try {
			if (!app.project.save(newFile)) {
				alert('Error: Project failed to save!');
				return false;
			}
		}
		catch (e) {
			alert(e);
			return false;
		}
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
			ext: '.aep',
			version: version,
			note: comment,
			serverID: serverID,
			isPub: isPub,
			isWork: isWork
		});

		// Save this file's new fileID to its metadata
		setNimFileIdMetadata(newFileID);
		
		if (publish && filesCreated == 0) {
			isPub = 1;
			isWork = 0;
			workingFilePath = fullFilePath;
			if (parseInt(version) < 10) version = '0' + parseInt(version);
			newFileName = basename + '_v' + version + '_PUB.aep';
			fullFilePath = path + newFileName;
			newFile = new File(fullFilePath);
		}
		filesCreated++;
	}

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


var os, userID;
