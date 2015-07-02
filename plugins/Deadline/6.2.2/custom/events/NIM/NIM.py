#Python.NET

###############################################################
'''
	NIM.py
	NimEventListener
	v_1.0.26
	
	Andrew Sinagra
	11.01.12

	04.03.13	v_1.0.21	Added png to sRGB conversion
	06.04.13	v_1.0.22	Updated for Deadline 6
	02.12.14	v_1.0.23	Updated for Deadline 6.1
					Updated for NIM 5.0
	09.08.14	v_1.0.24	Added taskID variable to work with new upload paths
	10.20.14	v_1.0.25	Added Cleanup event
	01.06.15	v_1.0.26	Updated call to be non-deadline specfic
							variables updated to pass JSON for output arrays
							updated to call non deadline specific api functions
'''
###############################################################

###############################################################
## Imports
###############################################################
from System.Diagnostics import *
from System.IO import *
from System import TimeSpan
from System import DateTime

from Deadline.Events import *
from Deadline.Scripting import *
import re, sys, os
import traceback

import string
import urllib, urllib2
import mimetools
import mimetypes
import cStringIO
import stat
try: import simplejson as json
except ImportError: import json
from itertools import izip
import datetime

nim_URL = None;
nim_version = None;
nim_class = None;
nim_taskID = None;
nim_fileID = None;
nim_jobID = None;
nim_encodeSRGB = None;

###############################################################
## This is the function called by Deadline to get an instance of the event listener.
###############################################################
def GetDeadlineEventListener():
	return NimEventListener()

def CleanupDeadlineEventListener( eventListener ):
    eventListener.Cleanup()
    
###############################################################
## The Draft event listener class.
###############################################################
class NimEventListener (DeadlineEventListener):
	
	def __init__( self ):
		#self.OnJobSubmittedEvent += self.OnJobSubmitted
		#self.OnJobStartedEvent += self.OnJobStarted
		self.OnJobFinishedCallback += self.OnJobFinished
		#self.OnJobRequeuedEvent += self.OnJobRequeued
		#self.OnJobFailedEvent += self.OnJobFailed
	
	def Cleanup( self ):
		del self.OnJobFinishedCallback
	
	def getSqlData(self, sqlCmd):
		
		'''Querys mySQL server and returns decoded json array'''
		'''
		   Problem with json.loads in IronPython
		   Need to write method to parse return string into list
		   *** DOES EVENT NEED TO RECIEVE DATA OTHER THAN CONFIRMATION OF TRANSMIT ***
		   *** SERVER CAN JUST RETURN true/false
		'''
		actionURL = self.nim_URL+urllib.urlencode(sqlCmd)
		ClientUtils.LogText( 'Query URL: %s' % actionURL)
		try:
			f = urllib2.urlopen(actionURL)
		except urllib2.HTTPError, e:
			ClientUtils.LogText( "ErrorCode: %s" % (e.code,) )
		except urllib2.URLError, e:
			ClientUtils.LogText( "Args: %s" % (e.args,) )
		
		ClientUtils.LogText( 'Result: '+ f.read())
		result = json.loads( f.read() )
		f.close()
		ClientUtils.LogText( 'Result: '+ result)
		return result
		
	def sendSqlData(self, sqlCmd):
		'''Querys mySQL server and returns decoded json array'''
		actionURL = self.nim_URL+urllib.urlencode(sqlCmd)
		ClientUtils.LogText( 'Query URL: %s' % actionURL)
		try:
			f = urllib2.urlopen(actionURL)
		except urllib2.HTTPError, e:
			ClientUtils.LogText( "ErrorCode: %s" % (e.code,) )
		except urllib2.URLError, e:
			ClientUtils.LogText( "Args: %s" % (e.args,) )
		return
	

	#Uses Draft to convert an image to a given format, to prepare for uploading
	def ConvertThumbnail( self, pathToFrame, format ):
		ClientUtils.LogText( "ConvertThumbnail:" )
		#first figure out where the Draft folder is on the repo
		draftRepoPath = Path.Combine( RepositoryUtils.GetRootDirectory(), "Draft" )
		
		if SystemUtils.IsRunningOnMac():
			draftRepoPath = Path.Combine( draftRepoPath, "Mac" )
		else:
			if SystemUtils.IsRunningOnLinux():
				draftRepoPath = Path.Combine( draftRepoPath, "Linux" )
			else:
				draftRepoPath = Path.Combine( draftRepoPath, "Windows" )
			
			if SystemUtils.Is64Bit():
				draftRepoPath = Path.Combine( draftRepoPath, "64bit" )
			else:
				draftRepoPath = Path.Combine( draftRepoPath, "32bit" )
		
		#import Draft and do the actual conversion
		ClientUtils.LogText( "Appending '%s' to Python search path" % draftRepoPath )	
		if not str(draftRepoPath) in sys.path:
			sys.path.append( draftRepoPath )
		
		ClientUtils.LogText( "Importing Draft to perform Thumbnail conversion..."  )
		try:
			import Draft

			#ClientUtils.LogText( "RELOAD DRAFT" )
			Draft = reload( Draft )			#fix to find proper draft module
			
			ClientUtils.LogText("Successfully imported Draft!")
			ClientUtils.LogText(Draft.__file__)
		except:
			ClientUtils.LogText("Failed to import Draft!")
			ClientUtils.LogText(traceback.format_exc())
		
		
		try:
			ClientUtils.LogText( "Reading in image '%s'"  % pathToFrame )
			originalImage = Draft.Image.ReadFromFile( str(pathToFrame) )
		except:
			ClientUtils.LogText("Failed to read image")
			ClientUtils.LogText(traceback.format_exc())

		# APPLY SRGB LUT
		try:
			if self.nim_encodeSRGB == "True":
				displayLut = Draft.LUT.CreateSRGB()
				displayLut.Apply( originalImage )
				ClientUtils.LogText( 'Encoding sRGB...' )
		except:
			ClientUtils.LogText('Failed to Apply LUT')
			ClientUtils.LogText(traceback.format_exc())
			
		try:
			ClientUtils.LogText( "Converting image to type '%s'"  % format )
			tempPath = Path.Combine( ClientUtils.GetDeadlineTempPath(), "%s.%s" % (Path.GetFileNameWithoutExtension(pathToFrame), format) )
			ClientUtils.LogText( "Writing converted image to temp path '%s'..."  % tempPath )
		except:
			ClientUtils.LogText('Failed to convert image.')
			ClientUtils.LogText(traceback.format_exc())
			
		try:
			originalImage.WriteToFile( str(tempPath) )
			ClientUtils.LogText( "Done!" )
		except:
			ClientUtils.LogText('Failed to write file.')
			ClientUtils.LogText(traceback.format_exc())
		
		try:
			del sys.modules["Draft"]
			del Draft
			ClientUtils.LogText('Unloaded the Draft Module')
		except:
			ClientUtils.LogText('Failed to unload the Draft Module')
			
		return tempPath


	def upload(self, renderKey, path, item_type=None, display_name=None):
		"""
		Upload a file as an attachment/thumbnail to the entity_type and entity_id
		
		@param entity_id: id for given entity to attach to
		@param path: path to file on disk
		"""
		ClientUtils.LogText("NIM upload:")
		is_thumbnail = (item_type == "thumb_image")
		is_mov = (item_type == "draft")
		
		params = {}
		params["q"] = "uploadThumb"
		params["renderKey"] = renderKey
		params["jobID"] = self.nim_jobID
		params["taskID"] = self.nim_taskID

		if not os.path.isfile(path):
		    ClientUtils.LogText("Path must be a valid file.")
		
		url = self.nim_URL
		
		if is_thumbnail:
			params["q"] = "uploadThumb"
			params["file"] = open(path, "rb")
			ClientUtils.LogText("Uploading Thumb...")
		elif is_mov:
			params["q"] = "uploadMovie"
			params["file"] = open(path, "rb")
			ClientUtils.LogText("Uploading Movie...")
			ClientUtils.LogText("NIM jobID: "+params["jobID"])
			ClientUtils.LogText("NIM taskID: "+params["taskID"])
		else:
			if display_name is None:
				display_name = os.path.basename(path)
			params["file"] = open(path, "rb")
		
		# Create opener with extended form post support
		opener = urllib2.build_opener(FormPostHandler)
		
		# Perform the request
		try:
			result = opener.open(url, params).read()
			print "RESULT: "
			print result
		except urllib2.HTTPError, e:
			if e.code == 500:
				ClientUtils.LogText("Server encountered an internal error. \n%s\n(%s)\n%s\n\n" % (url, params, e))
			else:
				ClientUtils.LogText("Unanticipated error occurred uploading %s: %s" % (path, e))
		else:
			if not str(result).startswith("1"):
				ClientUtils.LogText("Could not upload file successfully, but not sure why.\nPath: %s\nUrl: %s\nError: %s" % (path, url, str(result)))
		
		 
	## This is called when the job finishes rendering.
	def OnJobFinished( self, job ):
		ClientUtils.LogText("OnJobFinished:")
		
		self.nim_URL = self.GetConfigEntry("NimURL")
		ClientUtils.LogText( 'NIM URL: %s' % self.nim_URL)
		
		# If this job has a nimJob then Log to NIM
		nim_jobName = job.GetJobExtraInfoKeyValue( "nimJob" )
		
		nim_jobPlugin = job.JobPlugin
		nim_draftUpload = job.GetJobExtraInfoKeyValue( "DraftUploadToNim" )
		ClientUtils.LogText( "NIM_5.0 - Plugin Type: %s" % nim_jobPlugin )
		ClientUtils.LogText( "NIM_5.0 - Draft Upload: %s" % nim_draftUpload )
		
		if nim_jobName != "":
			ClientUtils.LogText( "Found NIM Job: '%s'" % nim_jobName )
			
			#Get all the other Draft-related KVPs
			self.nim_class = job.GetJobExtraInfoKeyValue( "nimClass" )
			self.nim_taskID = job.GetJobExtraInfoKeyValue( "nimTaskID" )
			self.nim_fileID = job.GetJobExtraInfoKeyValue( "nimFileID" )
			self.nim_jobID = job.GetJobExtraInfoKeyValue( "nimJobID" )
			self.nim_encodeSRGB = job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" )
			
			ClientUtils.LogText("NIM jobID: "+self.nim_jobID )
			ClientUtils.LogText("NIM taskID: "+self.nim_taskID )
			ClientUtils.LogText("NIM encodeSRGB: "+self.nim_encodeSRGB )

			deadlineTemp = ClientUtils.GetDeadlineTempPath()
			
			jobID = job.JobId
			jobName = job.JobName
			jobComment = job.JobComment
			jobPlugin = job.JobPlugin
			jobFrames = job.JobFrames
			outputDirectories = job.JobOutputDirectories
			outputFilenames = job.JobOutputFileNames
			
			jobStartDate = job.JobStartedDateTime.Date.ToString('yyyy-MM-dd HH:mm:ss')
			jobEndDate = job.JobCompletedDateTime.Date.ToString('yyyy-MM-dd HH:mm:ss')
			
			outputDirs = []
			for outDir in outputDirectories:
				outDir = outDir.replace('\\','/')
				outDir = outDir.replace("//","/")
				outputDirs.append(outDir)
			outputDirs = json.dumps(outputDirs)

			outputFiles = []
			for outFile in outputFilenames:
				outFile = outFile.replace('\\','/')
				outFile = outFile.replace("//","/")
				outputFiles.append(outFile)
			outputFiles = json.dumps(outputFiles)

						
			# CODE TO GET TOTAL AND AVERAGE TASK RENDER TIMES
			avgTime = None
			totalTime = None
			
			# format is 00d 00h 00m 00s
			timePattern = ".*?=(?P<days>\d\d)d\s*(?P<hours>\d\d)h\s*(?P<minutes>\d\d)m\s*(?P<seconds>\d\d)s"
			
			tempStr = ClientUtils.ExecuteCommandAndGetOutput( ("GetJobTaskTotalTime", job.JobId) ).strip( "\r\n" )
			timeParts = re.match( timePattern, tempStr )			
			if ( timeParts != None ):
				#Converts the days, hours, mins into seconds:
				#((days * 24h + hours) * 60m + minutes) * 60s + seconds
				totalTime = ( ( int(timeParts.group('days')) * 24 + int(timeParts.group('hours')) ) * 60 + int(timeParts.group('minutes')) ) * 60 + int(timeParts.group('seconds'))
			
			tempStr = ClientUtils.ExecuteCommandAndGetOutput( ("GetJobTaskAverageTime", job.JobId) ).strip( "\r\n" )				
			timeParts = re.match( timePattern, tempStr)
			if ( timeParts != None ):
				avgTime = ( ( int(timeParts.group('days')) * 24 + int(timeParts.group('hours')) ) * 60 + int(timeParts.group('minutes')) ) * 60 + int(timeParts.group('seconds'))
				
			
			ClientUtils.LogText('JobID: %s' % jobID)
			ClientUtils.LogText('JobName: %s' % jobName)
			ClientUtils.LogText('JobPlugin: %s' % jobPlugin)
			ClientUtils.LogText('JobFrames: %s' % jobFrames)
			ClientUtils.LogText('Output Dirs: %s' % outputDirs)
			ClientUtils.LogText('Output Files: %s' % outputFiles)
			ClientUtils.LogText('Start Date: %s' % jobStartDate)
			ClientUtils.LogText('End Date: %s' % jobEndDate)
			
			self.nim_version = self.GetConfigEntry("NimVersion")
			ClientUtils.LogText( 'Formatting for NIM Version %s' % self.nim_version )
			sqlCmd = {	'q' : 'addRender',
						'jobID' : self.nim_jobID,
						'class' : self.nim_class,
						'taskID' : self.nim_taskID,
						'fileID' : self.nim_fileID,
						'renderKey' : jobID,
						'renderName' : jobName,
						'renderType' : jobPlugin,
						'renderComment' : jobComment,
						'outputDirs' : outputDirs,
						'outputFiles' : outputFiles,
						'start_datetime' : jobStartDate,
						'end_datetime' : jobEndDate,
						'avgTime' : avgTime,
						'totalTime' : totalTime,
						'frames' : jobFrames
					}
		
			sql_result = self.sendSqlData(sqlCmd)

			'''
			CHANGE TO GET ID OF ITEM ADDED TO DATABASE
			STILL LOG INCASE ICON CONVERSION CRASHES OUT
			
			if sql_result[0]['result'] == False:
			    sql_query = sql_result[0]['query']
			    #self.infoPrint(sql_query)
			    #msg = 'There was an error when writing to NIM.'
			    ClientUtils.LogText( "There was an error when writing to NIM\nQuery: '%s'" % sql_query )
			    return
			else:
			    ClientUtils.LogText( 'Succesfully published to NIM.' )
			    return
			'''   
			ClientUtils.LogText( 'Succesfully published to NIM.' )
			
			
			### CREATE AND UPLOAD ICON TO NIM


			# Upload a thumbnail if necessary.
			thumbnailFrame = self.GetConfigEntryWithDefault( "ThumbnailFrame", "" )
			if thumbnailFrame != "" and thumbnailFrame != "None":
				frameList = job.JobFramesList
				
				
				# Figure out which frame to upload.
				frameNum = -1
				if len(frameList) > 1:
					if thumbnailFrame == 'First Frame' :
						frameNum = frameList[0]
					elif thumbnailFrame == 'Last Frame' :
						frameNum = frameList[-1]
					elif thumbnailFrame == 'Middle Frame' :
						frameNum = frameList[len(frameList)/2]
					else :
						print ("ERROR: Unknown thumbnail frame option: '" + thumbnailFrame + "'")
						return
				else:
					frameNum = frameList[0]
				
				# Get the output path for the frame.
				outputPath = Path.Combine(job.JobOutputDirectories[0], job.JobOutputFileNames[0]).replace("//","/")
				
				# Pad the frame as required.
				paddingRegex = re.compile("[^\\?#]*([\\?#]+).*")
				m = re.match(paddingRegex,outputPath)
				if( m != None):
					padding = m.group(1)
					frame = StringUtils.ToZeroPaddedString(frameNum,len(padding),False)
					outputPath = outputPath.replace( padding, frame )
				
				#Try to use Draft to convert the frame to a different format
				upload_successful = False
				if( self.GetConfigEntryWithDefault( "EnableThumbnailConversion", "false" ).lower() == "true" ):
					format = self.GetConfigEntryWithDefault( "ConvertedThumbnailFormat", "JPEG" ).lower()
					
					try:
						convertedThumb = self.ConvertThumbnail( outputPath, format )
						if File.Exists( convertedThumb ):
							outputPath = convertedThumb
							upload_successful = True
						else:
							ClientUtils.LogText( "WARNING: Could not find converted thumbnail." )
					except:
						ClientUtils.LogText( "WARNING: Failed to convert frame using Draft." )
				
				if upload_successful:
					# Upload the thumbnail to NIM.
					ClientUtils.LogText("Nim Thumbnail Upload: " + outputPath )
					self.upload(jobID, outputPath, 'thumb_image', None)
					ClientUtils.LogText("File Uploaded" )
				else:
					# If converstion failed skip upload of thumbnail and let NIM replace with default image
					ClientUtils.LogText("Skipping Thumnail Upload to NIM.")
				
				
				
		if nim_jobPlugin == "Draft" and nim_draftUpload:
			ClientUtils.LogText( "Found Completed NIM Draft Job" )
			
			jobID = job.JobId
			self.nim_jobID = job.GetJobExtraInfoKeyValue( "nimJobID" )
			self.nim_taskID = job.GetJobExtraInfoKeyValue( "nimTaskID" )
			
			nimSrcJob = job.GetJobExtraInfoKeyValue( "nimSrcJob" )
			outputDirectories = job.JobOutputDirectories
			outputFilenames = job.JobOutputFileNames
			
			#Iternate through outputFiles and upload to NIM
			if len(outputFilenames) == 0:
				raise Exception( "ERROR: Could not find an output path in Job properties, no movie will be uploaded to Nim." )
			
			# Just upload the first movie file if there is more than one.
			moviePath = Path.Combine( outputDirectories[0], outputFilenames[0] )
			ClientUtils.LogText("UploadMovie: " + moviePath )
			
			self.upload(nimSrcJob, moviePath, 'draft', None)


# Based on http://code.activestate.com/recipes/146306/
class FormPostHandler(urllib2.BaseHandler):
	"""
	Handler for multipart form data
	"""
	handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first
	
	def http_request(self, request):
		data = request.get_data()
		if data is not None and not isinstance(data, basestring):
			files = []
			params = []
			for key, value in data.items():
				if isinstance(value, file):
					files.append((key, value))
				else:
					params.append((key, value))
			if not files:
				data = urllib.urlencode(params, True) # sequencing on
			else:
				boundary, data = self.encode(params, files)
				content_type = 'multipart/form-data; boundary=%s' % boundary
				request.add_unredirected_header('Content-Type', content_type)
			request.add_data(data)
		return request
	
	def encode(self, params, files, boundary=None, buffer=None):
		if boundary is None:
			boundary = mimetools.choose_boundary()
		if buffer is None:
			buffer = cStringIO.StringIO()
		for (key, value) in params:
			buffer.write('--%s\r\n' % boundary)
			buffer.write('Content-Disposition: form-data; name="%s"' % key)
			buffer.write('\r\n\r\n%s\r\n' % value)
		for (key, fd) in files:
			filename = fd.name.split('/')[-1]
			content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
			file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
			buffer.write('--%s\r\n' % boundary)
			buffer.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
			buffer.write('Content-Type: %s\r\n' % content_type)
			buffer.write('Content-Length: %s\r\n' % file_size)
			fd.seek(0)
			buffer.write('\r\n%s\r\n' % fd.read())
		buffer.write('--%s--\r\n\r\n' % boundary)
		buffer = buffer.getvalue()
		return boundary, buffer
	
	def https_request(self, request):
		return self.http_request(request)
