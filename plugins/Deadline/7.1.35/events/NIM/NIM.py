'''
Copyright (c) 2015, NIM Labs LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
'''
###############################################################
## Imports
###############################################################
from System.Diagnostics import *
from System.IO import *
from System import TimeSpan
from System import DateTime

import os, sys, traceback, re

from Deadline.Events import *
from Deadline.Scripting import *


import string
import urllib, urllib2
import mimetools
import mimetypes

import email.generator as email_gen
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
nim_elementTypeID = None;


###############################################################
## This is the function called by Deadline to get an instance of the event listener.
###############################################################
def GetDeadlineEventListener():
	return NimEventListener()


def CleanupDeadlineEventListener( eventListener ):
	eventListener.Cleanup()


###############################################################
## The NIM event listener class.
###############################################################
class NimEventListener (DeadlineEventListener):
	
	def __init__( self ):
		#self.OnJobSubmittedCallback += self.OnJobSubmitted
		#self.OnJobStartedCallback += self.OnJobStarted
		self.OnJobFinishedCallback += self.OnJobFinished
		#self.OnJobRequeuedCallback += self.OnJobRequeued
		#self.OnJobFailedCallback += self.OnJobFailed
	
	def Cleanup( self ):
		#del self.OnJobSubmittedCallback
		#del self.OnJobStartedCallback
		del self.OnJobFinishedCallback
		#del self.OnJobRequeuedCallback
		#del self.OnJobFailedCallback


	def OnJobSubmitted( self, job ):
		self.LogInfo("NIM - OnJobSubmitted:")

	def OnJobStarted( self, job ):
		self.LogInfo("NIM - OnJobStarted:")
	

	## This is called when the job finishes rendering.
	def OnJobFinished( self, job ):
		self.LogInfo("NIM --------------------------------------")

		self.LogInfo("")
		if self.isNIMJob(job):

			nim_jobPlugin = job.JobPlugin

			if nim_jobPlugin == "Draft":
				#Add Dailies from Draft
				self.AddNimDailies(job)
			else:
				#Log Render to NIM and create thumbnail
				self.LogInfo("Ready to Add Render")
				self.AddNimRender(job)
				self.updateThumbnail(job)
			


	#Determines whether or not this is a NIM Job
	def isNIMJob( self, job ):

		self.LogInfo("NIM - Checking for NIM Job")

		self.nim_URL = self.GetConfigEntry("NimURL")
		self.LogInfo( 'NIM URL: %s' % self.nim_URL)
		
		# If this job has a nimJob then Log to NIM
		nim_jobName = job.GetJobExtraInfoKeyValue( "nim_jobName" )

		if nim_jobName:
			self.LogInfo( "Found NIM Job: '%s'" % nim_jobName )
			
			nim_jobPlugin = job.JobPlugin
			self.LogInfo( "NIM - Plugin Type: %s" % nim_jobPlugin )
			
			#Get all the other Draft-related KVPs
			self.nim_jobName = job.GetJobExtraInfoKeyValue( "nim_jobName" )
			self.nim_jobID = job.GetJobExtraInfoKeyValue( "nim_jobID" )
			self.nim_class = job.GetJobExtraInfoKeyValue( "nim_class" )
			self.nim_taskID = job.GetJobExtraInfoKeyValue( "nim_taskID" )
			self.nim_fileID = job.GetJobExtraInfoKeyValue( "nim_fileID" )
			
			#self.nim_encodeSRGB = job.GetJobExtraInfoKeyValue( "DraftNimEncodeSRGB" )
			#self.nim_elementTypeID = job.GetJobExtraInfoKeyValue( "elementTypeID" )
			self.nim_encodeSRGB = False
			self.nim_elementTypeID = 1

			self.LogInfo("NIM jobID: "+self.nim_jobID )
			self.LogInfo("NIM taskID: "+self.nim_taskID )
			return True

		return False


	def AddNimRender( self, job ):
		jobKey = job.JobId
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
			
		
		self.LogInfo('JobKey: %s' % jobKey)
		self.LogInfo('JobName: %s' % jobName)
		self.LogInfo('JobPlugin: %s' % jobPlugin)
		self.LogInfo('JobFrames: %s' % jobFrames)
		self.LogInfo('Output Dirs: %s' % outputDirs)
		self.LogInfo('Output Files: %s' % outputFiles)
		self.LogInfo('Start Date: %s' % jobStartDate)
		self.LogInfo('End Date: %s' % jobEndDate)
		
		sqlCmd = {	'q' : 'addRender',
					'jobID' : self.nim_jobID,
					'class' : self.nim_class,
					'taskID' : self.nim_taskID,
					'fileID' : self.nim_fileID,
					'renderKey' : jobKey,
					'renderName' : jobName,
					'renderType' : jobPlugin,
					'renderComment' : jobComment,
					'outputDirs' : outputDirs,
					'outputFiles' : outputFiles,
					'elementTypeID' : self.nim_elementTypeID,
					'start_datetime' : jobStartDate,
					'end_datetime' : jobEndDate,
					'avgTime' : avgTime,
					'totalTime' : totalTime,
					'frames' : jobFrames
				}
	
		sql_result = self.sendSqlData(sqlCmd)

		"""
		CHANGE TO GET ID OF ITEM ADDED TO DATABASE
		STILL LOG INCASE ICON CONVERSION CRASHES OUT
		
		if sql_result[0]['result'] == False:
			sql_query = sql_result[0]['query']
			#self.LogInfo(sql_query)
			#msg = 'There was an error when writing to NIM.'
			self.LogInfo( "There was an error when writing to NIM\nQuery: '%s'" % sql_query )
			return
		else:
			self.LogInfo( 'Succesfully published to NIM.' )
			return
		"""   
		self.LogInfo( 'Succesfully published to NIM.' )


	def AddNimDailies( self, job ):

		nim_draftUpload = job.GetJobExtraInfoKeyValue( "DraftUploadToNim" )
		self.LogInfo( "NIM - Draft Upload: %s" % nim_draftUpload )

		nim_jobPlugin = job.JobPlugin
		self.LogInfo( "NIM - Plugin Type: %s" % nim_jobPlugin )

		if nim_jobPlugin == "Draft" and nim_draftUpload:
			self.LogInfo( "Found Completed NIM Draft Job" )
			
			jobKey = job.JobId
			self.nim_jobID = job.GetJobExtraInfoKeyValue( "nim_jobID" )
			self.nim_taskID = job.GetJobExtraInfoKeyValue( "nim_taskID" )
			
			nimSrcJob = job.GetJobExtraInfoKeyValue( "nimSrcJob" )
			outputDirectories = job.JobOutputDirectories
			outputFilenames = job.JobOutputFileNames
			
			#Iternate through outputFiles and upload to NIM
			if len(outputFilenames) == 0:
				raise Exception( "ERROR: Could not find an output path in Job properties, no movie will be uploaded to Nim." )
			
			# Just upload the first movie file if there is more than one.
			moviePath = Path.Combine( outputDirectories[0], outputFilenames[0] )
			self.LogInfo("UploadMovie: " + moviePath )
			
			self.upload(nimSrcJob, moviePath, 'draft', None)


	def updateThumbnail( self, job ):
		# CREATE AND UPLOAD ICON TO NIM
		self.LogInfo("Updating Thumbnail")
		
		try:
			if len(job.JobOutputDirectories) == 0 or len(job.JobOutputFileNames) == 0:
				self.LogInfo( "Deadline is unaware of the output location; skipping thumbnail creation." )
			
			else:
				self.LogInfo( "Deadline is good to go.")

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
							self.LogInfo ("ERROR: Unknown thumbnail frame option: '" + thumbnailFrame + "'")
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
						format = self.GetConfigEntryWithDefault( "ConvertedThumbnailFormat", "JPG" ).lower()
						
						try:
							convertedThumb = self.ConvertThumbnail( outputPath, format )
							if File.Exists( convertedThumb ):
								outputPath = convertedThumb
								upload_successful = True
							else:
								self.LogInfo( "WARNING: Could not find converted thumbnail." )
						except:
							self.LogInfo( "WARNING: Failed to convert frame using Draft." )
					
					if upload_successful:
						# Upload the thumbnail to NIM.
						jobKey = job.JobId
						self.LogInfo("Nim Thumbnail Upload: " + outputPath )
						self.upload(jobKey, outputPath, 'thumb_image', None)
						self.LogInfo("File Uploaded" )
					else:
						# If converstion failed skip upload of thumbnail and let NIM replace with default image
						self.LogInfo("Skipping Thumnail Upload to NIM.")
		except:
			self.LogInfo( traceback.format_exc() )


	#Uses Draft to convert an image to a given format, to prepare for uploading
	def ConvertThumbnail( self, pathToFrame, format ):
		self.LogInfo( "ConvertThumbnail:" )
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
		self.LogInfo( "Appending '%s' to Python search path" % draftRepoPath )	
		if not str(draftRepoPath) in sys.path:
			sys.path.append( draftRepoPath )
		
		self.LogInfo( "Importing Draft to perform Thumbnail conversion..."  )
		try:
			import Draft

			#self.LogInfo( "RELOAD DRAFT" )
			Draft = reload( Draft )			#fix to find proper draft module
			
			self.LogInfo("Successfully imported Draft!")
			self.LogInfo(Draft.__file__)
		except:
			self.LogInfo("Failed to import Draft!")
			self.LogInfo(traceback.format_exc())
		
		
		try:
			self.LogInfo( "Reading in image '%s'"  % pathToFrame )
			originalImage = Draft.Image.ReadFromFile( str(pathToFrame) )
		except:
			self.LogInfo("Failed to read image")
			self.LogInfo(traceback.format_exc())

		# APPLY SRGB LUT
		"""
		try:
			if self.nim_encodeSRGB == "True":
				displayLut = Draft.LUT.CreateSRGB()
				displayLut.Apply( originalImage )
				self.LogInfo( 'Encoding sRGB...' )
		except:
			self.LogInfo('Failed to Apply LUT')
			self.LogInfo(traceback.format_exc())
		"""

		try:
			self.LogInfo( "Converting image to type '%s'"  % format )
			tempPath = Path.Combine( ClientUtils.GetDeadlineTempPath(), "%s.%s" % (Path.GetFileNameWithoutExtension(pathToFrame), format) )
			self.LogInfo( "Writing converted image to temp path '%s'..."  % tempPath )
		except:
			self.LogInfo('Failed to convert image.')
			self.LogInfo(traceback.format_exc())
			
		try:
			originalImage.WriteToFile( str(tempPath) )
			self.LogInfo( "Done!" )
		except:
			self.LogInfo('Failed to write file.')
			self.LogInfo(traceback.format_exc())
		
		try:
			del sys.modules["Draft"]
			del Draft
			self.LogInfo('Unloaded the Draft Module')
		except:
			self.LogInfo('Failed to unload the Draft Module')
			
		return tempPath
	
	
	def upload(self, renderKey, path, item_type=None, display_name=None):
		"""
		Upload a file as an attachment/thumbnail to the entity_type and entity_id
		
		@param renderKey: renderKey for given render to attach to
		@param path: path to file on disk
		"""
		self.LogInfo("NIM upload:")
		is_thumbnail = (item_type == "thumb_image")
		is_mov = (item_type == "draft")
		
		params = {}
		action = "uploadThumb"
		params["q"] = action.encode('ascii')
		params["renderKey"] = renderKey.encode('ascii')
		params["jobID"] = self.nim_jobID.encode('ascii')
		params["taskID"] = self.nim_taskID.encode('ascii')

		if not os.path.isfile(path):
			self.LogInfo("Path must be a valid file.")
		else:
			self.LogInfo("File found at path: %s" % path)
		
		url = self.nim_URL.encode('ascii')
		self.LogInfo("Verifying API URL: %s" % url)

		if is_thumbnail:
			action = "uploadThumb"
			params["q"] = action.encode('ascii')
			params["file"] = open(path,'rb')
			self.LogInfo("Uploading Thumb...")
		elif is_mov:
			action = "uploadMovie"
			params["q"] = action.encode('ascii')
			params["file"] = open(path, "rb")
			self.LogInfo("Uploading Movie...")
		else:
			if display_name is None:
				display_name = os.path.basename(path)
			params["file"] = open(path, "rb")
		
		# Create opener with extended form post support
		try:
			opener = urllib2.build_opener(FormPostHandler)
		except:
			self.LogInfo( "Failed on build_opener")
			self.LogInfo( traceback.format_exc() )

		#self.LogInfo("build_opener: successful")
		# Perform the request
		try:
			#self.LogInfo("Try")
			result = opener.open(url, params).read()
			self.LogInfo( "Result: %s" % result )
		except urllib2.HTTPError, e:
			if e.code == 500:
				self.LogInfo("Server encountered an internal error. \n%s\n(%s)\n%s\n\n" % (url, params, e))
			else:
				self.LogInfo("Unanticipated error occurred uploading %s: %s" % (path, e))
		else:
			if not str(result).startswith("1"):
				self.LogInfo("Could not upload file successfully, but not sure why.\nPath: %s\nUrl: %s\nError: %s" % (path, url, str(result)))
		
	
	def getSqlData(self, sqlCmd):
		
		"""Querys mySQL server and returns decoded json array"""
		"""
		   Problem with json.loads in IronPython
		   Need to write method to parse return string into list
		   *** DOES EVENT NEED TO RECIEVE DATA OTHER THAN CONFIRMATION OF TRANSMIT ***
		   *** SERVER CAN JUST RETURN true/false
		"""
		actionURL = self.nim_URL+urllib.urlencode(sqlCmd)
		self.LogInfo( 'Query URL: %s' % actionURL)
		try:
			f = urllib2.urlopen(actionURL)
		except urllib2.HTTPError, e:
			self.LogInfo( "ErrorCode: %s" % (e.code,) )
		except urllib2.URLError, e:
			self.LogInfo( "Args: %s" % (e.args,) )
		
		self.LogInfo( 'Result: '+ f.read())
		result = json.loads( f.read() )
		f.close()
		self.LogInfo( 'Result: '+ result)
		return result
	
	
	def sendSqlData(self, sqlCmd):
		"""Querys mySQL server and returns decoded json array"""
		actionURL = self.nim_URL+urllib.urlencode(sqlCmd)
		self.LogInfo( 'Query URL: %s' % actionURL)
		try:
			f = urllib2.urlopen(actionURL)
		except urllib2.HTTPError, e:
			self.LogInfo( "ErrorCode: %s" % (e.code,) )
		except urllib2.URLError, e:
			self.LogInfo( "Args: %s" % (e.args,) )
		return


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
			#boundary = mimetools.choose_boundary()
			boundary = email_gen._make_boundary()
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
