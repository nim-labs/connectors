//******************************************************************************
//
// Filename: nimPremiere.jsx
// Version:  v5.3.0.221027
//
// Copyright (c) 2014-2022 NIM Labs LLC
// All rights reserved.
//
// Use of this software is subject to the terms of the NIM Labs license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// *****************************************************************************

#include "PPro_API_Constants.jsx"

if(typeof JSON!=='object'){JSON={};}(function(){'use strict';function f(n){return n<10?'0'+n:n;}if(typeof Date.prototype.toJSON!=='function'){Date.prototype.toJSON=function(){return isFinite(this.valueOf())?this.getUTCFullYear()+'-'+f(this.getUTCMonth()+1)+'-'+f(this.getUTCDate())+'T'+f(this.getUTCHours())+':'+f(this.getUTCMinutes())+':'+f(this.getUTCSeconds())+'Z':null;};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(){return this.valueOf();};}var cx,escapable,gap,indent,meta,rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function(a){var c=meta[a];return typeof c==='string'?c:'\\u'+('0000'+a.charCodeAt(0).toString(16)).slice(-4);})+'"':'"'+string+'"';}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==='object'&&typeof value.toJSON==='function'){value=value.toJSON(key);}if(typeof rep==='function'){value=rep.call(holder,key,value);}switch(typeof value){case'string':return quote(value);case'number':return isFinite(value)?String(value):'null';case'boolean':case'null':return String(value);case'object':if(!value){return'null';}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==='[object Array]'){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||'null';}v=partial.length===0?'[]':gap?'[\n'+gap+partial.join(',\n'+gap)+'\n'+mind+']':'['+partial.join(',')+']';gap=mind;return v;}if(rep&&typeof rep==='object'){length=rep.length;for(i=0;i<length;i+=1){if(typeof rep[i]==='string'){k=rep[i];v=str(k,value);if(v){partial.push(quote(k)+(gap?': ':':')+v);}}}}else{for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?': ':':')+v);}}}}v=partial.length===0?'{}':gap?'{\n'+gap+partial.join(',\n'+gap)+'\n'+mind+'}':'{'+partial.join(',')+'}';gap=mind;return v;}}if(typeof JSON.stringify!=='function'){escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;meta={'\b':'\\b','\t':'\\t','\n':'\\n','\f':'\\f','\r':'\\r','"':'\\"','\\':'\\\\'};JSON.stringify=function(value,replacer,space){var i;gap='';indent='';if(typeof space==='number'){for(i=0;i<space;i+=1){indent+=' ';}}else if(typeof space==='string'){indent=space;}rep=replacer;if(replacer&&typeof replacer!=='function'&&(typeof replacer!=='object'||typeof replacer.length!=='number')){throw new Error('JSON.stringify');}return str('',{'':value});};}if(typeof JSON.parse!=='function'){cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==='object'){for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v;}else{delete value[k];}}}}return reviver.call(holder,key,value);}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return'\\u'+('0000'+a.charCodeAt(0).toString(16)).slice(-4);});}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,'@').replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,']').replace(/(?:^|:|,)(?:\s*\[)+/g,''))){j=eval('('+text+')');return typeof reviver==='function'?walk({'':j},''):j;}throw new SyntaxError('JSON.parse');};}}());;  

$._nim_PPP_={
	
	version : '5.3.0',
	debug : false,
	debug_level : 0,
	exportJobs : {},
	nimTempDirectory : '~/.nim/tmp',
	
	getExtensionVersion: function(){
		$._nim_PPP_.updateEventPanel('FUNCTION: getExtensionVersion ',2);

		return $._nim_PPP_.version;
	},

	setNimTempDirectory: function(folder){
		$._nim_PPP_.nimTempDirectory = folder;
	},

	getProjectPath: function(){
		$._nim_PPP_.updateEventPanel('FUNCTION: getProjectPath',2);

		return app.project.path;
	},

	getActiveSequenceName : function(){
		$._nim_PPP_.updateEventPanel('FUNCTION: getActiveSequenceName',2);

		return app.project.activeSequence.name;
	},

	selectFileDialog : function(dlgTitle,filterString){
		$._nim_PPP_.updateEventPanel('FUNCTION: selectFileDialog',2);

		filter = 0;
		if(filterString){
			filter = filterString;
		}
		var selectedFile = File.openDialog (dlgTitle, filter, false);
		var fsName = '';
		if(selectedFile){
			fsName = selectedFile.fsName;
		}
		return fsName;
	},

	selectFolderDialog : function(){
		$._nim_PPP_.updateEventPanel('FUNCTION: selectFolderDialog',2);

		var outFolder = Folder.selectDialog();
		var fsName = '';
		if(outFolder){
			fsName = outFolder.fsName;
		}
		return fsName;
	},

	getProjectMetadata : function(data){
		$._nim_PPP_.updateEventPanel('FUNCTION: getProjectMetadata',2);
		$._nim_PPP_.updateEventPanel(data,2);
		
		try {
			data = JSON.parse(data);
		}
		catch(e){
			$._nim_PPP_.updateEventPanel('Failed to read data in getProjectMetadata.',1);
			return false;
		}

		if (app.isDocumentOpen()) {
			//var projectItem = app.project.activeSequence.projectItem;
			var projectChildren = app.project.rootItem.children;
			if(projectChildren.numItems > 0){
				var projectItem	= app.project.rootItem.children[0]; 	// just grabs first projectItem.
				if (projectItem) {
					if (ExternalObject.AdobeXMPScript === undefined) {
						ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');
					}
					if (ExternalObject.AdobeXMPScript !== undefined) {
						var kPProPrivateProjectMetadataURI	= "http://ns.adobe.com/premierePrivateProjectMetaData/1.0/";
						var projectMetadata	= projectItem.getProjectMetadata();
						var xmp	= new XMPMeta(projectMetadata);

						for (var key in data) {
							$._nim_PPP_.updateEventPanel('Reading Property: '+key,2);
							if(xmp.doesPropertyExist(kPProPrivateProjectMetadataURI, key)){
								var property = xmp.getProperty(kPProPrivateProjectMetadataURI, key);
								$._nim_PPP_.updateEventPanel('Property Found: '+property.value,2);
								data[key] = property.value;
								data[key] = data[key] == " " ? "" : data[key];
							}
							$._nim_PPP_.updateEventPanel('--------------------------------------',2);
						}

						data["nim_pproProjectPath"] = app.project.path;
						return JSON.stringify(data);
					}
				}
			}
		}
		return false;
	},

	setProjectMetadata : function(data) {
		$._nim_PPP_.updateEventPanel('FUNCTION: setProjectMetadata:',2);
		$._nim_PPP_.updateEventPanel(data,2);
		
		try {
			data = JSON.parse(data);
		}
		catch(e){
			$._nim_PPP_.updateEventPanel('Failed to read data in setProjectMetadata.',1);
			return false;
		}

		if (app.isDocumentOpen()) {
			//var projectItem = app.project.activeSequence.projectItem;
			var projectChildren = app.project.rootItem.children;
			if(projectChildren.numItems > 0){
				var projectItem	= app.project.rootItem.children[0]; // just grabs first projectItem.
				if (projectItem) {
					if (ExternalObject.AdobeXMPScript === undefined) {
						ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');
					}
					if (ExternalObject.AdobeXMPScript !== undefined) {
						var kPProPrivateProjectMetadataURI	= "http://ns.adobe.com/premierePrivateProjectMetaData/1.0/";
						var projectMetadata	= projectItem.getProjectMetadata();
						var xmp	= new XMPMeta(projectMetadata);

						var fieldArray	= [];

						// Define Project Properties
						for( var key in data){
							if( data[key] !== undefined ){
								if (xmp.doesPropertyExist(kPProPrivateProjectMetadataURI, key)){
									$._nim_PPP_.updateEventPanel('Property Found: '+key,2);
									$._nim_PPP_.updateEventPanel('Property Data: '+data[key],2);
									$._nim_PPP_.updateEventPanel('Property Type: '+typeof data[key],2);
									data[key] = data[key] == "" ? " " : data[key];
									xmp.setProperty(kPProPrivateProjectMetadataURI, key, data[key]);
									$._nim_PPP_.updateEventPanel('Property Set: '+key,2);
								}
								else{
									var successfullyAdded = app.project.addPropertyToProjectMetadataSchema(key, key, 2);
									$._nim_PPP_.updateEventPanel('Adding Property: '+key,2);
									if(successfullyAdded){
										$._nim_PPP_.updateEventPanel('Property Added',2);
										data[key] = data[key] == "" ? " " : data[key];
										xmp.setProperty(kPProPrivateProjectMetadataURI, key, data[key]);
										$._nim_PPP_.updateEventPanel('Property Set: '+key+ ' : '+data[key],2);
									}
									else {
										$._nim_PPP_.updateEventPanel('Failed to Add Property: '+key,2);
									}
								}
								$._nim_PPP_.updateEventPanel('--------------------------------------',2);
								fieldArray.push(key);
							}
						}
						$._nim_PPP_.updateEventPanel('FieldArray: '+JSON.stringify(fieldArray),2);

						var str = xmp.serialize();
						projectItem.setProjectMetadata(str, fieldArray);
						return true;
					}
				}
			}
		}
		return false;
	},

	projectOpen : function(projToOpen) {
		$._nim_PPP_.updateEventPanel('FUNCTION: projectOpen',2);

		$._nim_PPP_.updateEventPanel('projectOpen - projToOpen: ' + projToOpen,2);
		
		if (projToOpen) {
			var result = app.openDocument(	projToOpen,
											1,					// suppress 'Convert Project' dialogs
											1,					// suppress 'Locate Files' dialogs
											1);					// suppress warning dialogs
			$._nim_PPP_.updateEventPanel('projectOpen - result: ' + JSON.stringify(result),2);
		}	
		else {
			alert("Project Not Found");
		}
	},

	projectSaveAs : function(projToSave) {
		$._nim_PPP_.updateEventPanel('FUNCTION: projectSaveAs',2);

		$._nim_PPP_.updateEventPanel('projectSaveAs - projToSave: ' + projToSave,2);

		if (projToSave) {
			var result = app.project.saveAs( projToSave );
			$._nim_PPP_.updateEventPanel('projectSaveAs - result: ' + JSON.stringify(result),2);
		}	
		else {
			$._nim_PPP_.updateEventPanel("Project Not Found",0);
		}
	},

	projectPublish : function() {
		$._nim_PPP_.updateEventPanel('FUNCTION: projectPublish',2);

		var ogPath = app.project.path;
		var ogPathWithoutExt = ogPath.substr(0, ogPath.length - 7);
		var projToPub = ogPathWithoutExt+'_PUB'+'.prproj';
		app.project.saveAs(projToPub);

		for (var a = 0; a < app.projects.numProjects; a++){ 
			var currentProject = app.projects[a]; 
			if (currentProject.path === projToPub){ 
				app.openDocument(ogPath);
				currentProject.closeDocument(); 
			} 
		}
	},

	exportEdit : function(context, itemID, name, desc, typeID, statusID, keywords, preset, presetPath, range, diskID, disk, keep, markers) {

		$._nim_PPP_.updateEventPanel("FUNCTION: Export Edit",2);

		var ameStatus = BridgeTalk.getStatus("ame");
		if (ameStatus == "ISNOTINSTALLED"){
			$._nim_PPP_.updateEventPanel("AME is not installed.",0);
			return "Adobe Media Encoder is not installed.";
		}
		if (ameStatus == "ISNOTRUNNING"){
			app.encoder.launchEncoder(); // This can take a while; let's get the ball rolling.
		}
		
		try {
			app.encoder.bind('onEncoderJobComplete',	$._nim_PPP_.onEncoderJobComplete);
			app.encoder.bind('onEncoderJobError', 		$._nim_PPP_.onEncoderJobError);
			app.encoder.bind('onEncoderJobProgress', 	$._nim_PPP_.onEncoderJobProgress);
			app.encoder.bind('onEncoderJobQueued', 		$._nim_PPP_.onEncoderJobQueued);
			app.encoder.bind('onEncoderJobCanceled',	$._nim_PPP_.onEncoderJobCanceled);
		}
		catch (e) {
			$._nim_PPP_.updateEventPanel("AME Binds Failed",0);
		}
		
		$._nim_PPP_.updateEventPanel("Binds Complete",2);

		app.encoder.launchEncoder(); // This can take a while; let's get the ball rolling.
		
		$._nim_PPP_.updateEventPanel("launchEncoder",2);

		var activeSequence = app.project.activeSequence;
		var sequenceID = activeSequence.sequenceID;
		var sequenceName = activeSequence.name;
		var outputPath = sequenceName+'.mov';
		
		var projectPath = app.project.path;
		var pathArray = projectPath.split(/[\\\/]/);
		var basename = pathArray.pop();
		projectPath = projectPath.substring(0,projectPath.indexOf(basename));

		if(diskID == 0){
			outputPath = projectPath+outputPath;
		}
		if(diskID == 1){
			outputPath = disk+outputPath;
		}
		if(diskID == 2){
			outputPath = disk+outputPath;
		}

		$._nim_PPP_.updateEventPanel('exportEdit - outputPath:' + outputPath,2);
		$._nim_PPP_.updateEventPanel('exportEdit - presetPath:' + presetPath,2);
		$._nim_PPP_.updateEventPanel('exportEdit - range:' + range,2);

		var workArea = parseInt(range);
		var removeOnComplete = 1;

		// Attach marker info
		var markerData = [];
		if(markers == 1){
			markerData = activeSequence.markers;

			var numMarkers	= markerData.numMarkers;
			if (numMarkers > 0) {
				var m = 0;
				for(var current_marker	=	markerData.getFirstMarker();
						current_marker	!==	undefined; 
						current_marker 	=	markerData.getNextMarker(current_marker)){

					$._nim_PPP_.updateEventPanel('exportEdit - marker.name:' + current_marker.name,2);
					$._nim_PPP_.updateEventPanel('exportEdit - marker.comments:' + current_marker.comments,2);
					
					var markerItem = { name : current_marker.name,
									   comments: current_marker.comments,
									   type : current_marker.type,
									   start : current_marker.start,
									   end : current_marker.end };
					markerData[m] = (markerItem);
					m = m + 1;
				}    
			}
		}

		var encodeJobID = app.encoder.encodeSequence(activeSequence, outputPath, presetPath, workArea, removeOnComplete);

		$._nim_PPP_.exportJobs[encodeJobID] = { encode : "sequence", jobID : encodeJobID, sequenceID : sequenceID, context : context, 
												itemID : itemID, name : name, desc : desc, typeID : typeID, statusID : statusID, 
												keywords : keywords, preset : preset, presetPath : presetPath, range : range, 
												diskID : diskID, disk : disk, keep : keep, markers : markers, markerData: markerData };

		return JSON.stringify($._nim_PPP_.exportJobs[encodeJobID]);
	},

	exportClip : function(sequenceID, trackID, clipID, itemID, name, typeID, preset, presetPath, 
		outputPath, length, handles, exportAE, exportAeSource, exportAeServer, task_type_ID, serverID, framerate) {

		$._nim_PPP_.updateEventPanel("FUNCTION: Export Clip",2);

		var ameStatus = BridgeTalk.getStatus("ame");
		if (ameStatus == "ISNOTINSTALLED"){
			$._nim_PPP_.updateEventPanel("AME is not installed.",0);
			return "Adobe Media Encoder is not installed.";
		}
		if (ameStatus == "ISNOTRUNNING"){
			app.encoder.launchEncoder(); // This can take a while; let's get the ball rolling.
		}

		try {
			app.encoder.bind('onEncoderJobComplete',	$._nim_PPP_.onEncoderJobComplete);
			app.encoder.bind('onEncoderJobError', 		$._nim_PPP_.onEncoderJobError);
			app.encoder.bind('onEncoderJobProgress', 	$._nim_PPP_.onEncoderJobProgress);
			app.encoder.bind('onEncoderJobQueued', 		$._nim_PPP_.onEncoderJobQueued);
			app.encoder.bind('onEncoderJobCanceled',	$._nim_PPP_.onEncoderJobCanceled);
		}
		catch (e) {
			$._nim_PPP_.updateEventPanel("AME Binds Failed",0);
		}

		$._nim_PPP_.updateEventPanel('exportEdit - trackID:' + trackID,2);
		$._nim_PPP_.updateEventPanel('exportEdit - clipID:' + clipID,2);
		$._nim_PPP_.updateEventPanel('exportEdit - itemID:' + itemID,2);
		$._nim_PPP_.updateEventPanel('exportEdit - name:' + name,2);
		$._nim_PPP_.updateEventPanel('exportEdit - typeID:' + typeID,2);
		$._nim_PPP_.updateEventPanel('exportEdit - preset:' + preset,2);
		$._nim_PPP_.updateEventPanel('exportEdit - presetPath:' + presetPath,2);
		$._nim_PPP_.updateEventPanel('exportEdit - outputPath:' + outputPath,2);
		$._nim_PPP_.updateEventPanel('exportEdit - length:' + length,2);
		$._nim_PPP_.updateEventPanel('exportEdit - handles:' + handles,2);
		$._nim_PPP_.updateEventPanel('exportEdit - exportAE:' + exportAE,2);
		$._nim_PPP_.updateEventPanel('exportEdit - exportAeSource:' + exportAeSource,2);
		$._nim_PPP_.updateEventPanel('exportEdit - exportAeServer:' + exportAeServer,2);
		$._nim_PPP_.updateEventPanel('exportEdit - task_type_ID:' + task_type_ID,2);
		$._nim_PPP_.updateEventPanel('exportEdit - serverID:' + serverID,2);

		
		var sequences = app.project.sequences;
		var targetSequence = app.project.activeSequence;	// Set to active sequence by default

		// Find sequence by ID targeted for export at time export button was pressed
		for(var i=0; i<sequences.numItems; i++){
			if(sequences[i].sequenceID == sequenceID){
				targetSequence = sequences[i];
			}
		}

		var clip = targetSequence.videoTracks[trackID].clips[clipID];
		var projectItem = clip.projectItem;

		var workArea = 0;
		var removeOnComplete = 1;
		
		

		if(length == "0"){	// CUT + HANDLES

			// May need to test for projectItem type
			//$._nim_PPP_.message("projectItem.type: "+projectItem.type);

			var ticksPerSecond = 254016000000; 							// Ticks per second
			var ticksPerFrame = targetSequence.timebase; 				// Ticks per frame
			//var ticksPerFrame = app.project.activeSequence.timebase; 	// Ticks per frame
			//var framerate = ticksPerSecond/ticksPerFrame;				// Passed From getSequenceItems
			
			var inPoint = clip.inPoint.seconds - ((parseInt(handles) * ticksPerFrame)/ticksPerSecond);		// Convert handles from frames to seconds
			inPoint = inPoint < 0 ? 0 : inPoint; // Keep from going negative

			var outPoint = clip.outPoint.seconds + ((parseInt(handles) * ticksPerFrame)/ticksPerSecond);	// Convert handles from frames to seconds
			
			var mediaFile = projectItem.getMediaPath();

			if(mediaFile !== undefined){
				var encodeJobID = app.encoder.encodeFile(mediaFile, outputPath, presetPath, removeOnComplete, inPoint, outPoint);

				$._nim_PPP_.exportJobs[encodeJobID] = { encode : "clip", jobID : encodeJobID, trackID : trackID, clipID : clipID, itemID : itemID, 
														name : name, typeID : typeID, preset : preset, presetPath : presetPath, outputPath : outputPath,
														length : length, handles : handles, exportAE : exportAE, exportAeSource : exportAeSource, 
														exportAeServer : exportAeServer, task_type_ID : task_type_ID, serverID : serverID, framerate : framerate };

				return JSON.stringify($._nim_PPP_.exportJobs[encodeJobID]);
			}
		}
		else if(length == "1"){ // SOURCE CLIP
			var encodeJobID = app.encoder.encodeProjectItem(projectItem, outputPath, presetPath, workArea, removeOnComplete);

			$._nim_PPP_.exportJobs[encodeJobID] = { encode : "clip", jobID : encodeJobID, trackID : trackID, clipID : clipID, itemID : itemID, 
													name : name, typeID : typeID, preset : preset, presetPath : presetPath, outputPath : outputPath,
													length : length, handles : handles, exportAE : exportAE, exportAeSource : exportAeSource, 
													exportAeServer : exportAeServer, task_type_ID : task_type_ID, serverID : serverID, framerate : framerate };

			return JSON.stringify($._nim_PPP_.exportJobs[encodeJobID]);
		}
		
		$._nim_PPP_.updateEventPanel("An invalid length was defined.",0);
		return "An invalid length was defined.";
	},

	getSequenceItems : function (rename, nameTemplate, layerOption){
		// Retrives all video trackItems in a sequence
		// optionally renames clips based on nameTemplate

		$._nim_PPP_.updateEventPanel('FUNCTION: getSequenceItems',2);

		var sequenceObj = {};

		try {
			var activeSequence = app.project.activeSequence;
			sequenceObj['sequenceID'] = activeSequence.sequenceID;
			sequenceObj['sequenceName'] = activeSequence.name;
		}
		catch (e) {
			message = "Failed to retrieve active sequence.<br />Please load a sequence onto the timeline.";
			$._nim_PPP_.updateEventPanel(message,0);
			// alert(message);
			return message;
		}
		
		try {
			sequenceObj['framerate'] = 0;
			var pxmp = new XMPMeta(activeSequence.projectItem.getProjectMetadata());
			var kPProPrivateProjectMetadataURI	= "http://ns.adobe.com/premierePrivateProjectMetaData/1.0/";
			// Pull framerate from sequence metadata
	        if (pxmp.doesPropertyExist(kPProPrivateProjectMetadataURI, 'Column.Intrinsic.MediaTimebase') == true) {  
	          sequenceObj['framerate'] = pxmp.getProperty(kPProPrivateProjectMetadataURI, 'Column.Intrinsic.MediaTimebase');
	          sequenceObj['framerate'] = parseFloat(sequenceObj['framerate']);
	        }
	        // Calculate framerate
	        else{
	        	sequenceObj['framerate'] = $._nim_PPP_.getActiveSequenceFramerate();
	        }
	    }
	    catch (e) {
			message = "Failed to get project metadata.";
			// alert(message);
			return message;
		}

		try {
			var videoTracks = activeSequence.videoTracks;
			$._nim_PPP_.updateEventPanel('videoTracks: '+JSON.stringify(videoTracks),2);
		}
		catch (e) {
			message = "Failed to update event panel with video tracks.";
			// alert(message);
			return message;
		}

		var tracks = [];
		var firstTrack = true;
		for(var i=0; i<videoTracks.numTracks; i++){
			var trackInfo = {};
			trackInfo['name'] = videoTracks[i].name;
			trackInfo['ID'] = videoTracks[i].id;
			trackInfo['mediaType'] = videoTracks[i].mediaType;

			try {
				var trackClips = videoTracks[i].clips;
				$._nim_PPP_.updateEventPanel('trackClips: '+JSON.stringify(trackClips),2);
			}
			catch (e) {
				message = "Failed to update event panel with track clips.";
				// alert(message);
				return message;
			}

			var clips = [];
			for(var j=0; j<trackClips.numItems; j++){
				var clipInfo = {};

				// Use first track as basis for rename (should be first track with clips if track 0 is empty)
				if(rename == "1"){
					if(firstTrack==true){
						trackClips[j].name = $._nim_PPP_.renameClip(nameTemplate,j);
						$._nim_PPP_.updateEventPanel("renameClip: "+trackClips[j].name,2);
					}
					else{
						trackClips[j].name = $._nim_PPP_.getVerticalTrackName(trackClips[j], i, layerOption);
						$._nim_PPP_.updateEventPanel("getVerticalTrackName: "+trackClips[j].name,2);
					}
				}
				clipInfo['name'] = trackClips[j].name;
				clipInfo['duration'] = trackClips[j].duration;
				clipInfo['start'] = trackClips[j].start;
				clipInfo['end'] = trackClips[j].end;
				clipInfo['inPoint'] = trackClips[j].inPoint;
				clipInfo['outPoint'] = trackClips[j].outPoint;
				clipInfo['mediaType'] = trackClips[j].mediaType;
				clipInfo['projectItem'] = trackClips[j].projectItem;
				clipInfo['mediaPath'] = clipInfo['projectItem'].getMediaPath();
				clips.push(clipInfo);	
			}
			if(trackClips.numItems >  0){
				firstTrack = false;
			}
			trackInfo['clips'] = clips;
			tracks.push(trackInfo);
			
		}
		sequenceObj['tracks'] = tracks;

		return JSON.stringify(sequenceObj);
	},

	renameClip : function(nameTemplate, clipIndex){

		$._nim_PPP_.updateEventPanel('FUNCTION: renameClip',2);

		$._nim_PPP_.updateEventPanel("Renaming Clip Index: "+clipIndex,2);

		var frameReg = /^([^\<\>]*)<(#*)(?:x(\d*))?(?:@(\d*))?>(.*)$/g;
		var frameItems = frameReg.exec(nameTemplate);
		var prefix = frameItems[1] !== undefined ? frameItems[1] : "";
		var padding = frameItems[2] !== undefined ? (frameItems[2].match(/#/g) || []).length : 0;
		var skip = frameItems[3] !== undefined ? parseInt(frameItems[3]) : 1;
		skip = skip <= 0 ? 1 : skip;	// Skip must be at least 1
		var start = frameItems[4] !== undefined ? parseInt(frameItems[4]) : 0;
		var suffix = frameItems[5] !== undefined ? frameItems[5] : "";
		var number = ((clipIndex*skip)+start).toString();
        
        number = $._nim_PPP_.padNumber(number, padding);
        var shotName = prefix+number+suffix;
		return shotName;
	},

	exportClipIcon : function(clip) {

		$._nim_PPP_.updateEventPanel('FUNCTION: exportClipIcon',2);

		$._nim_PPP_.updateEventPanel('In Clip: '+clip,2);

		try {
			clip = JSON.parse(clip);
		}
		catch (e) {
			message = "Failed to parse clip data in ExportClipIcon: "+clip;
			alert(message);
			return message;
		}

		try {
			app.project.openSequence(clip['sequenceID']);	// Sequence Must be active to export PNG
		}
		catch (e) {
			message = "Failed to open sequence: "+clip['sequenceID'];
			alert(message);
			return message;
		}

		try {
			$._nim_PPP_.setPlayerPosition(clip.start.ticks);
		}
		catch (e) {
			message = "Failed to set player position @: "+clip.start.ticks;
			alert(message);
			return message;
		}

		try {
			var outputFileName = $._nim_PPP_.exportCurrentFrameAsPNG();
		}
		catch (e) {
			message = "Failed to export current frame as PNG";
			alert(message);
			return message;
		}

		clip["outputFileName"] = outputFileName;

		$._nim_PPP_.updateEventPanel('Out Clip: '+clip,2);

		return JSON.stringify(clip);
	},

	getVerticalTrackName : function(clip, trackNumber, layerOption){

		$._nim_PPP_.updateEventPanel('FUNCTION: getVerticalTrackName',2);

		var inClipStartTicks = parseInt(clip.start.ticks);
		var inClipEndTicks = parseInt(clip.end.ticks);
		$._nim_PPP_.updateEventPanel("inClipStartTicks: "+inClipStartTicks,2);
		$._nim_PPP_.updateEventPanel("inClipEndTicks: "+inClipEndTicks,2);

		var activeSequence = app.project.activeSequence;
		var videoTracks = activeSequence.videoTracks;
		var clipName = "";
		
		// TODO:  Build array and count number of lower items, optionally append suffix based on track (ie SH001A)
		trackLoop:
		for(var i=0; i<trackNumber; i++){
			var trackClips = videoTracks[i].clips;
			
			for(var j=0; j<trackClips.numItems; j++){
				$._nim_PPP_.updateEventPanel("trackClip name: "+trackClips[j].name,2);
				var clipStartTicks = parseInt(trackClips[j].start.ticks);
				var clipEndTicks =parseInt( trackClips[j].end.ticks);

				$._nim_PPP_.updateEventPanel("clipStartTicks: "+clipStartTicks,2);
				$._nim_PPP_.updateEventPanel("clipEndTicks: "+clipEndTicks,2);

				if(layerOption == 0){	// Match First Frame
					if(clipStartTicks <= inClipStartTicks && clipEndTicks > inClipStartTicks){
						$._nim_PPP_.updateEventPanel("Match Found: "+trackClips[j].name,2);
						clipName = trackClips[j].name;
						break trackLoop;
					}
				}
				else {	// Match End Frame
					if(clipStartTicks < inClipEndTicks && clipEndTicks >= inClipEndTicks){
						$._nim_PPP_.updateEventPanel("Match Found: "+trackClips[j].name,2);
						clipName = trackClips[j].name;
						break trackLoop;
					}
				}
			}
		}

		$._nim_PPP_.updateEventPanel("clipName: "+clipName,2);

		if(clipName == ""){
			clipName = clip.name;
		}

		return clipName;
	},

	setPlayerPosition : function(ticks) {

		$._nim_PPP_.updateEventPanel('FUNCTION: setPlayerPosition',2);

		var activeSequence = app.project.activeSequence;

		try {
			activeSequence.setPlayerPosition(ticks);
		}
		catch (e) {
			message = "Failed to set player position in setPlayerPosition: "+ticks;
			alert(message);
			return message;
		}
	},

	exportCurrentFrameAsPNG : function() {

		$._nim_PPP_.updateEventPanel('FUNCTION: exportCurrentFrameAsPNG',2);

		try {
			app.enableQE();
		}
		catch (e) {
			message = "Failed to enable QE";
			alert(message);
			return message;
		}

		try {
			var activeSequence	= qe.project.getActiveSequence(); 	// note: make sure a sequence is active in PPro UI
		}
		catch (e) {
			message = "Failed to retrieve active sequence.<br />Please load a sequence onto the timeline.";
			$._nim_PPP_.updateEventPanel(message,0);
			// alert(message);
			return message;
		}

		if (activeSequence) {
			// Create a file name based on timecode of frame.
			var time			= activeSequence.CTI.timecode; 	// CTI = Current Time Indicator.
			var removeThese 	= /:|;/ig;    					// Why? Because Windows chokes on colons.
			var timeName = time.replace(removeThese, '_');
			var outputPath = new File($._nim_PPP_.nimTempDirectory);

			var outputName 		= activeSequence.name+"_"+timeName+"_"+$._nim_PPP_.guid();
			outputName = outputName.replace(/\s|\.|\ /g, '_'); 	// Remove all spaces and periods

			var outputFileName	= outputPath.fsName + $._nim_PPP_.getSep() + outputName;

			try {
				activeSequence.exportFramePNG(time, outputFileName);
			}
			catch (e) {
				message = "Failed to execute exportFramePNG with the following settings: "+time+" - "+outputFileName;
				alert(message);
				return message;
			}

			outputFileName += ".png";
			return outputFileName;
		} else {
			$._nim_PPP_.updateEventPanel("No active sequence",0);
		}
		return false;
	},

	importReviewItem : function(reviewPath){

		$._nim_PPP_.updateEventPanel("FUNCTION: importReviewItem",2);
		
		var result = false;

		if(reviewPath){
			if (app.project) {	
				var importBin = app.project.getInsertionBin();	
				result = app.project.importFiles([reviewPath], 
													0,								// suppress warnings 
													importBin, 						// - projectItem
													0);								// import as numbered stills
				
				if(result){
					matchingMediaItems = importBin.findItemsMatchingMediaPath(reviewPath, 1);
					$._nim_PPP_.updateEventPanel("matchingMediaItems: "+JSON.stringify(matchingMediaItems),2);

					if(matchingMediaItems.length > 0){
						$._nim_PPP_.updateEventPanel("matchingMediaItems[0]: "+JSON.stringify(matchingMediaItems[0]),2);
						var nodeId = matchingMediaItems[0]['nodeId'];
						$._nim_PPP_.updateEventPanel("nodeId: "+JSON.stringify(nodeId),2);
						result = nodeId;
					}
					else{
						result = false;
					}
				}
				return JSON.stringify(result);
			}
		}
		return "false";
	},

	importElements : function(shotTree, destination, binName) {

		$._nim_PPP_.updateEventPanel("FUNCTION: importElements",2);
		
		var result = false;

		if (app.project) {
			var binMade = false;
			var projectRootItem = app.project.rootItem;
			var nimBin = projectRootItem;
			if(destination == "1"){
				nimBin = app.project.getInsertionBin();
			}
			if(destination == "2"){
				// Create NIM Root Bin
				nimBin = $._nim_PPP_.findBin(projectRootItem, binName);
				if(nimBin === false){
					binMade = projectRootItem.createBin("NIM Elements");
					nimBin = $._nim_PPP_.findBin(projectRootItem, binName);
				}
			}

			try {
				shotTree = JSON.parse(shotTree);
			}
			catch (e) {
				$._nim_PPP_.updateEventPanel("Failed to read shot tree in importElements.",1);
			}

			if (shotTree) 
			{
				for(var i=0; i<shotTree.length; i++){
					var shotData = shotTree[i];
					var shotName = shotData['shotName'];

					var shotBin = $._nim_PPP_.findBin(nimBin, shotName);
					if(shotBin === false){
						binMade = nimBin.createBin(shotName);
						shotBin = $._nim_PPP_.findBin(nimBin, shotName);
					}
					
					if(shotBin !== false){
						var elementFiles = [];
						for(var j=0;j<shotData['elements'].length; j++){
							var element = shotData['elements'][j];
							var elementPath = element['full_path'];
							var elementName = element['name'];

							// Check for existing element in project and skip if found
							var fileFound = $._nim_PPP_.findFile(nimBin, elementName);
							if(fileFound === false){
								elementFiles.push(elementPath);
							}
						}
						if(elementFiles){
							result = app.project.importFiles(elementFiles, 
													0,								// suppress warnings 
													shotBin, 						// app.project.getInsertionBin(),  // - projectItem
													1);								// import as numbered stills	
						}
					}
					
				}
			} 
			else {
				$._nim_PPP_.updateEventPanel("No files to import.",1);
				result = false;
			} 
		}
		return JSON.stringify(result);
	},

	findBin : function(rootBin, binName) {

		$._nim_PPP_.updateEventPanel('FUNCTION: findBin',2);

		var binFound = false;
		var bin = null;
		if (app.project) {
			var projectChildren = rootBin.children;
			for(var i=0; i<projectChildren.numItems; i++){
				var projectChild = projectChildren[i];
				if(projectChild.type == 2){				// 'BIN'
					if(projectChild.name == binName){
						binFound = true;
						bin = projectChild;
						break;
					}
					else {
						var childFound = $._nim_PPP_.findBin(projectChild, binName);
						if( childFound !== false ){
							binFound = true;
							bin = projectChild;
							break;
						}
					}
				}
			}
		}
		if(binFound){
			return bin;
		}
		else {
			return false;
		}
	},

	findFile : function(rootBin, fileName) {

		$._nim_PPP_.updateEventPanel('FUNCTION: findFile',2);

		var fileFound = false;
		var fileItem = null;
		if (app.project) {
			var projectChildren = rootBin.children;
			for(var i=0; i<projectChildren.numItems; i++){
				var projectChild = projectChildren[i];
				if(projectChild.type == 1 || projectChild.type == 4){				// 'CLIP' or 'FILE'
					if(projectChild.name == fileName){
						fileFound = true;
						fileItem = projectChild;
						break;
					}
				}
				else if(projectChild.type == 2) {		// 'BIN'
					var childFound = $._nim_PPP_.findFile(projectChild, fileName);
					if( childFound !== false ){
						fileFound = true;
						fileItem = projectChild;
						break;
					}
				}
			}
		}
		if(fileFound){
			return fileItem;
		}
		else {
			return false;
		}
	},

	getProjectPath : function() {

		$._nim_PPP_.updateEventPanel('FUNCTION: getProjectPath',2);

		var projectPath = app.project.path;
		var pathArray = projectPath.split(/[\\\/]/);
		var basename = pathArray.pop();
		projectPath = projectPath.substring(0,projectPath.indexOf(basename));
		return projectPath;
	},

	getActiveSequenceFramerate : function() {

		$._nim_PPP_.updateEventPanel('FUNCTION: getActiveSequenceFramerate',2);

		var ticksPerSecond = 254016000000; 							// Ticks per second
		var ticksPerFrame = app.project.activeSequence.timebase; 	// Ticks per frame
		var framerate = 0;
		if(ticksPerFrame !== undefined && ticksPerFrame > 0){
			framerate = ticksPerSecond/ticksPerFrame;
		}
		return framerate;
	},

	createSequenceMarker : function(nodeID, startTime, endTime, name, comment) {

		$._nim_PPP_.updateEventPanel("FUNCTION: createSequenceMarker: ",2);
		$._nim_PPP_.updateEventPanel("nodeID: "+nodeID,2);

		var projectItem = '';
		if(nodeID == 0){
			projectItem = app.project.activeSequence;
		}
		else{
			// Find projectItem with nodeID
			if (app.project) {
				var projectChildren = app.project.rootItem.children;
				$._nim_PPP_.updateEventPanel("projectChildren: "+JSON.stringify(projectChildren),2);

				for(var i=0; i<projectChildren['numItems']; i++){
					$._nim_PPP_.updateEventPanel("projectChildren[i].nodeId: "+projectChildren[i].nodeId,2);
					$._nim_PPP_.updateEventPanel("looking for nodeID: "+nodeID,2);

					if(projectChildren[i].nodeId == nodeID){
						$._nim_PPP_.updateEventPanel("target projectItem found: "+nodeID,2);
						projectItem = projectChildren[i];
						break;
					}
				}

			}
		}
		
		if(projectItem){
			$._nim_PPP_.updateEventPanel("projectItem: "+JSON.stringify(projectItem),2);
			if(nodeID == 0){
				var markers = projectItem.markers;
			}
			else {
				var markers = projectItem.getMarkers();
			}
			if(markers){
				var  newCommentMarker = markers.createMarker(parseFloat(startTime));
				newCommentMarker.name = name;
				newCommentMarker.comments = comment;
				newCommentMarker.end = parseFloat(endTime);
				return "true";
			}
			else{
				$._nim_PPP_.updateEventPanel("Failed to get markers for project item",0);
				return "false";
			}
		}
		else{
			$._nim_PPP_.updateEventPanel("createSequenceMarker: No Item Found",1);
			return "false";
		}
	},

	guid : function() {

		$._nim_PPP_.updateEventPanel("FUNCTION: guid: ",2);

		function s4() {
			return Math.floor((1 + Math.random()) * 0x10000)
			.toString(16)
			.substring(1);
		}
		//return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
		return s4() + s4() + s4() + s4() + s4() + s4() + s4() + s4();
	},

	padNumber : function( number, padding) {

		$._nim_PPP_.updateEventPanel("FUNCTION: padNumber: ",2);

		var width = padding - number.length;
		if(width > 0){
			for(var i=0;i<width;i++){
				number = "0"+number;
			}
		}
		return number;
	},

	getSep : function() {

		$._nim_PPP_.updateEventPanel("FUNCTION: getSep: ",2);

		if (Folder.fs == 'Macintosh') {
			return '/';
		} else {
			return '\\';
		}
	},

	message : function (msg) {

		$._nim_PPP_.updateEventPanel("FUNCTION: message: ",2);

		// Using '$' object will invoke ExtendScript Toolkit, if installed.
		$.writeln(msg);	 
	},

	setDebugLevel : function (level) {

		$._nim_PPP_.updateEventPanel("FUNCTION: setDebugLevel: ",2);

		if(!level){
			level = 0;
		}
		$._nim_PPP_.debug_level = parseInt(level);

		if($._nim_PPP_.debug_level > 0){
			app.setSDKEventMessage("NIM Debug Level Set: "+$._nim_PPP_.debug_level, 'info');
		}

		var result = "Debug Level Set: "+$._nim_PPP_.debug_level;
		return result;
	},

	debugLog : function (msg) {

		$._nim_PPP_.updateEventPanel("FUNCTION: debugLog: ",2);

		if($._nim_PPP_.debug){
			//$.writeln(msg);	 // Using '$' object will invoke ExtendScript Toolkit, if installed.
			app.setSDKEventMessage(message, 'info');
		}
	},

	updateEventPanel : function (message, level) {

		// SET MESSAGE HEADER
		var level_type = 'ERROR';
		if(level == 0){
			level_type = 'ERROR';
		}
		if(level == 1){
			level_type = 'WARNING';
		}
		if(level == 2){
			level_type = 'INFO';
		}

		try {
			// SEND TO EVENT LOG

			try {
				message = String(message);
			}
			catch (e) {
				level_type = 'ERROR';
				message = 'Failed to stringify event panel message.';
				app.setSDKEventMessage(message, 'error');
			}

			if(level == 0){
				app.setSDKEventMessage(message, 'error');
				level_type = 'ERROR';
			}
			if(level == 1 && $._nim_PPP_.debug_level >= 1){
				app.setSDKEventMessage(message, 'warning');
				level_type = 'WARNING';
			}
			if(level == 2 &&  $._nim_PPP_.debug_level >= 2){
				app.setSDKEventMessage(message, 'info');
				level_type = 'INFO';
			}
		} 
		catch (e) {
			level_type = 'ERROR';
			message = "Error updating the event panel - Exception: " + e;
			alert(message);
		}
		
		// RETURN RESULT FOR console.log
		result = level_type+": "+message;
		return result;
	},

	// Callbacks
	onEncoderJobComplete : function (jobID, outputFilePath) {

		try {
			$._nim_PPP_.updateEventPanel("CALLBACK: onEncoderJobComplete: ",2);

			var eoName;
			if (Folder.fs == 'Macintosh') {
				eoName = "PlugPlugExternalObject";							
			} else {
				eoName = "PlugPlugExternalObject.dll";
			}
			var mylib = new ExternalObject('lib:' + eoName);

			if(typeof $._nim_PPP_.exportJobs[jobID] !== "undefined"){
				var jobData = $._nim_PPP_.exportJobs[jobID];
				jobData['outputFilePath'] = outputFilePath;
				delete $._nim_PPP_.exportJobs[jobID];

				var nimEvent = new CSXSEvent();
				nimEvent.type = "com.nim-labs.events";
				if( jobData["encode"] == "sequence"){
					nimEvent.type = "com.nim-labs.events.PProExportEditComplete";
				}
				else if( jobData["encode"] == "clip"){
					nimEvent.type = "com.nim-labs.events.PProExportShotComplete";
				}

				nimEvent.data = JSON.stringify(jobData);
				nimEvent.dispatch();
			}
			else {
				$._nim_PPP_.updateEventPanel("onEncoderJobComplete: Job does not exist.",1);
			}
		}
		catch(e){
			$._nim_PPP_.updateEventPanel("FAILED: onEncoderJobComplete: "+e,0);
		}
	},

	onEncoderJobError : function (jobID, errorMessage) {

		try {
			$._nim_PPP_.updateEventPanel("CALLBACK: onEncoderJobError: "+errorMessage,0);

			var eoName;
			if (Folder.fs == 'Macintosh') {
				eoName = "PlugPlugExternalObject";							
			} else {
				eoName = "PlugPlugExternalObject.dll";
			}
			var mylib = new ExternalObject('lib:' + eoName);

			if(typeof $._nim_PPP_.exportJobs[jobID] !== "undefined"){
				var jobData = $._nim_PPP_.exportJobs[jobID];

				var nimEvent	= new CSXSEvent();
				nimEvent.type = "com.nim-labs.events";
				if( jobData["encode"] == "sequence"){
					nimEvent.type = "com.nim-labs.events.PProExportEditError";
				}
				else if( jobData["encode"] == "clip"){
					nimEvent.type = "com.nim-labs.events.PProExportShotError";
				}
				nimEvent.data	= "Job " + jobID + " failed, due to " + errorMessage + ".";
				nimEvent.dispatch();
			}
			else {
				$._nim_PPP_.updateEventPanel("onEncoderJobError: Job does not exist.",1);
			}
		}
		catch (e) {
			$._nim_PPP_.updateEventPanel("FAILED: onEncoderJobError: "+e,0);
		}
	},
	
	onEncoderJobProgress : function (jobID, progress) {

		try {
			$._nim_PPP_.updateEventPanel('CALLBACK: onEncoderJobProgress called. jobID = ' + jobID + '. progress = ' + progress + '.',2);

			var eoName;
			if (Folder.fs == 'Macintosh') {
				eoName = "PlugPlugExternalObject";							
			} else {
				eoName = "PlugPlugExternalObject.dll";
			}
			var mylib = new ExternalObject('lib:' + eoName);

			if(typeof $._nim_PPP_.exportJobs[jobID] !== "undefined"){
				var jobData = $._nim_PPP_.exportJobs[jobID];

				var jobProgress = { jobID: jobID, progress: progress, encode: jobData["encode"], itemID: jobData["itemID"] };

				var nimEvent = new CSXSEvent();
				nimEvent.type = "com.nim-labs.events";
				if( jobData["encode"] == "sequence"){
					nimEvent.type = "com.nim-labs.events.PProExportEditProgress";
				}
				else if( jobData["encode"] == "clip"){
					nimEvent.type = "com.nim-labs.events.PProExportShotProgress";
				}
				nimEvent.data = JSON.stringify(jobProgress);
				nimEvent.dispatch();
			}
			else {
				$._nim_PPP_.updateEventPanel("onEncoderJobProgress: Job does not exist.",1);
			}
			
		}
		catch(e){
			$._nim_PPP_.updateEventPanel("FAILED: onEncoderJobProgress: "+e,0);
		}
	},

	onEncoderJobQueued : function (jobID) {

		try {
			$._nim_PPP_.updateEventPanel("CALLBACK: onEncoderJobQueued: ",2);

			var eoName;
			if (Folder.fs == 'Macintosh') {
				eoName = "PlugPlugExternalObject";							
			} else {
				eoName = "PlugPlugExternalObject.dll";
			}
			var mylib = new ExternalObject('lib:' + eoName);

			if(typeof $._nim_PPP_.exportJobs[jobID] !== "undefined"){
				var jobData = $._nim_PPP_.exportJobs[jobID];

				var nimEvent = new CSXSEvent();
				nimEvent.type = "com.nim-labs.events";
				if( jobData["encode"] == "sequence"){
					nimEvent.type = "com.nim-labs.events.PProExportEditQueued";
				}
				else if( jobData["encode"] == "clip"){
					nimEvent.type = "com.nim-labs.events.PProExportShotQueued";
				}
				nimEvent.data = JSON.stringify(jobData);
				nimEvent.dispatch();

				app.encoder.startBatch();
			}
			else {
				$._nim_PPP_.updateEventPanel("onEncoderJobQueued: Job does not exist.",1);
			}
		}
		catch (e) {
			$._nim_PPP_.updateEventPanel("FAILED: onEncoderJobQueued: "+e,0);
		}
	},

	onEncoderJobCanceled : function (jobID) {

		try {
			$._nim_PPP_.updateEventPanel("CALLBACK: OnEncoderJobCanceled: " + jobID, 2);

			var eoName;
			if (Folder.fs == 'Macintosh') {
				eoName = "PlugPlugExternalObject";							
			} else {
				eoName = "PlugPlugExternalObject.dll";
			}
			var mylib = new ExternalObject('lib:' + eoName);
			
			if(typeof $._nim_PPP_.exportJobs[jobID] !== "undefined"){
				var jobData = $._nim_PPP_.exportJobs[jobID];

				var nimEvent = new CSXSEvent();
				nimEvent.type = "com.nim-labs.events";
				if( jobData["encode"] == "sequence"){
					nimEvent.type = "com.nim-labs.events.PProExportEditCanceled";
				}
				else if( jobData["encode"] == "clip"){
					nimEvent.type = "com.nim-labs.events.PProExportShotCanceled";
				}
				nimEvent.data = JSON.stringify(jobData);
				nimEvent.dispatch();
			}
			else {
				$._nim_PPP_.updateEventPanel("OnEncoderJobCanceled: Job does not exist.",1);
			}
		}
		catch (e) {
			$._nim_PPP_.updateEventPanel("FAILED: OnEncoderJobCanceled: "+e,0);
		}
	},

};

