#include "PPro_API_Constants.jsx"

if(typeof JSON!=='object'){JSON={};}(function(){'use strict';function f(n){return n<10?'0'+n:n;}if(typeof Date.prototype.toJSON!=='function'){Date.prototype.toJSON=function(){return isFinite(this.valueOf())?this.getUTCFullYear()+'-'+f(this.getUTCMonth()+1)+'-'+f(this.getUTCDate())+'T'+f(this.getUTCHours())+':'+f(this.getUTCMinutes())+':'+f(this.getUTCSeconds())+'Z':null;};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(){return this.valueOf();};}var cx,escapable,gap,indent,meta,rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function(a){var c=meta[a];return typeof c==='string'?c:'\\u'+('0000'+a.charCodeAt(0).toString(16)).slice(-4);})+'"':'"'+string+'"';}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==='object'&&typeof value.toJSON==='function'){value=value.toJSON(key);}if(typeof rep==='function'){value=rep.call(holder,key,value);}switch(typeof value){case'string':return quote(value);case'number':return isFinite(value)?String(value):'null';case'boolean':case'null':return String(value);case'object':if(!value){return'null';}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==='[object Array]'){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||'null';}v=partial.length===0?'[]':gap?'[\n'+gap+partial.join(',\n'+gap)+'\n'+mind+']':'['+partial.join(',')+']';gap=mind;return v;}if(rep&&typeof rep==='object'){length=rep.length;for(i=0;i<length;i+=1){if(typeof rep[i]==='string'){k=rep[i];v=str(k,value);if(v){partial.push(quote(k)+(gap?': ':':')+v);}}}}else{for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?': ':':')+v);}}}}v=partial.length===0?'{}':gap?'{\n'+gap+partial.join(',\n'+gap)+'\n'+mind+'}':'{'+partial.join(',')+'}';gap=mind;return v;}}if(typeof JSON.stringify!=='function'){escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;meta={'\b':'\\b','\t':'\\t','\n':'\\n','\f':'\\f','\r':'\\r','"':'\\"','\\':'\\\\'};JSON.stringify=function(value,replacer,space){var i;gap='';indent='';if(typeof space==='number'){for(i=0;i<space;i+=1){indent+=' ';}}else if(typeof space==='string'){indent=space;}rep=replacer;if(replacer&&typeof replacer!=='function'&&(typeof replacer!=='object'||typeof replacer.length!=='number')){throw new Error('JSON.stringify');}return str('',{'':value});};}if(typeof JSON.parse!=='function'){cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==='object'){for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v;}else{delete value[k];}}}}return reviver.call(holder,key,value);}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return'\\u'+('0000'+a.charCodeAt(0).toString(16)).slice(-4);});}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,'@').replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,']').replace(/(?:^|:|,)(?:\s*\[)+/g,''))){j=eval('('+text+')');return typeof reviver==='function'?walk({'':j},''):j;}throw new SyntaxError('JSON.parse');};}}());;  

$._nim_PPP_={
	
	debug : false,
	exportJobs : {},
	
	getProjectPath: function(){
		return app.project.path;
	},

	getActiveSequenceName : function(){
		return app.project.activeSequence.name;
	},

	selectFileDialog : function(dlgTitle,filterString){
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
		var outFolder = Folder.selectDialog();
		var fsName = '';
		if(outFolder){
			fsName = outFolder.fsName;
		}
		return fsName;
	},

	getProjectMetadata : function(data){
		data = JSON.parse(data);
		if (app.isDocumentOpen()) {
			//var projectItem = app.project.activeSequence.projectItem;
			var projectItem	= app.project.rootItem.children[0]; // just grabs first projectItem.
			if (projectItem) {
				if (ExternalObject.AdobeXMPScript === undefined) {
					ExternalObject.AdobeXMPScript = new ExternalObject('lib:AdobeXMPScript');
				}
				if (ExternalObject.AdobeXMPScript !== undefined) {
					var kPProPrivateProjectMetadataURI	= "http://ns.adobe.com/premierePrivateProjectMetaData/1.0/";
					var projectMetadata	= projectItem.getProjectMetadata();
					var xmp	= new XMPMeta(projectMetadata);

					for (var key in data) {
						$._nim_PPP_.debugLog('Reading Property: '+key);
						if(xmp.doesPropertyExist(kPProPrivateProjectMetadataURI, key)){
							var property = xmp.getProperty(kPProPrivateProjectMetadataURI, key);
							$._nim_PPP_.debugLog('Property Found: '+property.value);
							data[key] = property.value;
						}
						$._nim_PPP_.debugLog('--------------------------------------');
					}

					data["nim_pproProjectPath"] = app.project.path;
					return JSON.stringify(data);
				}
			}
		}
		return false;
	},

	setProjectMetadata : function(data) {
		$._nim_PPP_.debugLog('setProjectMetadata: '+data);
		data = JSON.parse(data);

		if (app.isDocumentOpen()) {
			//var projectItem = app.project.activeSequence.projectItem;
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
								$._nim_PPP_.debugLog('Property Found: '+key);
								xmp.setProperty(kPProPrivateProjectMetadataURI, key, data[key]);
								$._nim_PPP_.debugLog('Property Set: '+key);
							}
							else{
								var successfullyAdded = app.project.addPropertyToProjectMetadataSchema(key, key, 2);
								$._nim_PPP_.debugLog('Adding Property: '+key);
								if(successfullyAdded){
									$._nim_PPP_.debugLog('Property Added');
									xmp.setProperty(kPProPrivateProjectMetadataURI, key, data[key]);
									$._nim_PPP_.debugLog('Property Set: '+key+ ' : '+data[key]);
								}
								else {
									$._nim_PPP_.debugLog('Failed to Add Property: '+key);
								}
							}
							$._nim_PPP_.debugLog('--------------------------------------');
							fieldArray.push(key);
						}
					}
					
					$._nim_PPP_.debugLog('FieldArray: '+JSON.stringify(fieldArray));

					var str = xmp.serialize();
					projectItem.setProjectMetadata(str, fieldArray);
					return true;
				}
			}
		}
		return false;
	},

	projectOpen : function(projToOpen) {
		$._nim_PPP_.debugLog('projectOpen - projToOpen: ' + projToOpen);
		if (projToOpen) {
			var result = app.openDocument(	projToOpen,
											1,					// suppress 'Convert Project' dialogs
											1,					// suppress 'Locate Files' dialogs
											1);					// suppress warning dialogs
			$._nim_PPP_.debugLog('projectOpen - result: ' + JSON.stringify(result));
		}	
		else {
			alert("Project Not Found");
		}
	},

	projectSaveAs : function(projToSave) {
		$._nim_PPP_.debugLog('projectSaveAs - projToSave: ' + projToSave);
		if (projToSave) {
			var result = app.project.saveAs( projToSave );
			$._nim_PPP_.debugLog('projectSaveAs - result: ' + JSON.stringify(result));
		}	
		else {
			alert("Project Not Found");
		}
	},

	projectPublish : function() {
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

		app.encoder.bind('onEncoderJobComplete',	$._nim_PPP_.onEncoderJobComplete);
		app.encoder.bind('onEncoderJobError', 		$._nim_PPP_.onEncoderJobError);
		app.encoder.bind('onEncoderJobProgress', 	$._nim_PPP_.onEncoderJobProgress);
		app.encoder.bind('onEncoderJobQueued', 		$._nim_PPP_.onEncoderJobQueued);
		app.encoder.bind('onEncoderJobCanceled',	$._nim_PPP_.onEncoderJobCanceled);

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

		$._nim_PPP_.debugLog('exportEdit - outputPath:' + outputPath);
		$._nim_PPP_.debugLog('exportEdit - presetPath:' + presetPath);
		$._nim_PPP_.debugLog('exportEdit - range:' + range);

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

			        $._nim_PPP_.debugLog('exportEdit - marker.name:' + current_marker.name);
			        $._nim_PPP_.debugLog('exportEdit - marker.comments:' + current_marker.comments);
			        
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

		$._nim_PPP_.exportJobs[encodeJobID] = { jobID : encodeJobID, sequenceID : sequenceID, context : context, itemID : itemID, name : name, 
												desc : desc, typeID : typeID, statusID : statusID, 
												keywords : keywords, preset : preset, presetPath : presetPath, 
												range : range, diskID : diskID, disk : disk, keep : keep, markers : markers, markerData: markerData };

		return JSON.stringify($._nim_PPP_.exportJobs[encodeJobID]);
	},

	message : function (msg) {
		$.writeln(msg);	 // Using '$' object will invoke ExtendScript Toolkit, if installed.
	},

	debugLog : function (msg) {
		if($._nim_PPP_.debug){
			$.writeln(msg);	 // Using '$' object will invoke ExtendScript Toolkit, if installed.
		}
	},

	onEncoderJobComplete : function (jobID, outputFilePath) {
		var eoName;
		if (Folder.fs == 'Macintosh') {
			eoName = "PlugPlugExternalObject";							
		} else {
			eoName = "PlugPlugExternalObject.dll";
		}
		var mylib = new ExternalObject('lib:' + eoName);
				
		var jobData = $._nim_PPP_.exportJobs[jobID];
		jobData['outputFilePath'] = outputFilePath;
		delete $._nim_PPP_.exportJobs[jobID];

		var nimEvent = new CSXSEvent();
		nimEvent.type = "com.nim-labs.events.PProExportEditComplete";
		nimEvent.data = JSON.stringify(jobData);
		nimEvent.dispatch();
	},

	onEncoderJobError : function (jobID, errorMessage) {
		var eoName; 

		if (Folder.fs === 'Macintosh') {
			eoName	= "PlugPlugExternalObject";							
		} else {
			eoName	= "PlugPlugExternalObject.dll";
		}
				
		var mylib		= new ExternalObject('lib:' + eoName);
		var eventObj	= new CSXSEvent();

		eventObj.type	= "com.nim-labs.events.PProExportEditError";
		eventObj.data	= "Job " + jobID + " failed, due to " + errorMessage + ".";
		eventObj.dispatch();
	},
	
	onEncoderJobProgress : function (jobID, progress) {
		$._nim_PPP_.debugLog('onEncoderJobProgress called. jobID = ' + jobID + '. progress = ' + progress + '.');

		var eoName;
		if (Folder.fs == 'Macintosh') {
			eoName = "PlugPlugExternalObject";							
		} else {
			eoName = "PlugPlugExternalObject.dll";
		}
		var mylib = new ExternalObject('lib:' + eoName);
		
		var jobData = { jobID: jobID, progress: progress };
		var nimEvent = new CSXSEvent();
		nimEvent.type = "com.nim-labs.events.PProExportEditProgress";
		nimEvent.data = JSON.stringify(jobData);
		nimEvent.dispatch();
	},

	onEncoderJobQueued : function (jobID) {

		var eoName;
		if (Folder.fs == 'Macintosh') {
			eoName = "PlugPlugExternalObject";							
		} else {
			eoName = "PlugPlugExternalObject.dll";
		}
		var mylib = new ExternalObject('lib:' + eoName);
		
		//$._nim_PPP_.exportJobs[jobID]['jobID'] = jobID;
		var jobData = $._nim_PPP_.exportJobs[jobID];

		var nimEvent = new CSXSEvent();
		nimEvent.type = "com.nim-labs.events.PProExportEditQueued";
		nimEvent.data = JSON.stringify(jobData);
		nimEvent.dispatch();

		app.encoder.startBatch();
	},

	onEncoderJobCanceled : function (jobID) {
		$._nim_PPP_.debugLog('OnEncoderJobCanceled called. jobID = ' + jobID +  '.');
	},

};

