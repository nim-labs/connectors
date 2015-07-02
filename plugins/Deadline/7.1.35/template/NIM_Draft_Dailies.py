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
import sys
import os
import datetime
import copy
import xml.etree.ElementTree as xml

#print sys.path

import Draft
from Draft import *
from DraftParamParser import *


logoFile = r"/path/to/logo.png"
slateFile = r"/path/to/slate_bg.png"
#scale = 0.5

expectedTypes = {}
expectedTypes['username'] = '<string>'
expectedTypes['entity'] = '<string>'
expectedTypes['version'] = '<string>'
expectedTypes['startFrame'] = '<int>'
expectedTypes['endFrame'] = '<int>'
expectedTypes['inFile'] = '<string>'
expectedTypes['outFile'] = '<string>'
#expectedTypes['nimEncodeSRGB'] = '<string>'
	
#expectedTypes['LUT'] = '<string>'

params = ParseCommandLine( expectedTypes, sys.argv )
'''
try:
	params = ParseCommandLine( expectedTypes, sys.argv )
	nimEncodeSRGB = params['nimEncodeSRGB']
except:
	#Failed most likely due to nimEncodeSRGB not exiting
	expectedTypes.pop('nimEncodeSRGB')
	params = ParseCommandLine( expectedTypes, sys.argv )
	nimEncodeSRGB = "False"
'''
nimEncodeSRGB = "False"

inFilePattern = params['inFile']
startFrame = int(params['startFrame'])
endFrame = int(params['endFrame'])

LUT = "None";
if(nimEncodeSRGB == "True"):
	LUT = "sRGB"

# pull the output width height from an input frame
frameNumber = startFrame
inFile = ReplaceFilenameHashesWithNumber(inFilePattern, frameNumber)
inFrame = Image.ReadFromFile(inFile)

# apply the scale
width = 960
height = 540

# create an oversized background frame to composit everything onto
letterBoxScale = 1.0
letterBoxColor = ColorRGBA(0.0, 0.0, 0.0, 1.0)
origBgFrame = Image.CreateImage(width, int(height*(letterBoxScale)))
origBgFrame.SetToColor(letterBoxColor)

# add slate BG
try :
	slateBG = Image.ReadFromFile(slateFile)
	slateBG.Resize( origBgFrame.width, origBgFrame.height )
except :
	slateBG = None

# add a logo to the frame if you can find one
try :
	logo = Image.ReadFromFile(logoFile)
	#logoHeight = int(0.5*(letterBoxScale-1.0)/letterBoxScale*origBgFrame.height)
	#logoWidth = int(logo.width*logoHeight/logo.height)
	logoHeight = int(height * 0.05)
	logoWidth = int(float(logoHeight) / float(logo.height) * float(logo.width))
	logo.Resize( logoWidth, logoHeight )
except :
	logo = None

	
	
# make a video encoder
slateFrames = 1
fps = 24

#kBitRate = int(width*height*fps*3/1000)
#codec = "MJPEG" 
#videoEncoder = VideoEncoder( params['outFile'], fps, origBgFrame.width, origBgFrame.height, kBitRate, codec )

codec = "H264"
(outFileHead, outFileTail) = os.path.split( params['outFile'] )

#tempOutFile = os.path.join( outFileHead,  '~temp_' + outFileTail )
tempOutFile = params['outFile']
videoEncoder = VideoEncoder( tempOutFile, fps, origBgFrame.width, origBgFrame.height, quality = 80 , codec = codec  )



# encode the slate frames
slateBgFrame = copy.deepcopy(origBgFrame)
annotationInfo = AnnotationInfo()
annotationInfo.FontType = "Arial"
annotationInfo.FontWeight = 100
annotationInfo.Color = ColorRGBA(0.0, 0.85, 0.85, 1.0)
annotationInfo.DrawShadow = True
annotationInfo.ShadowColor = ColorRGBA( 0.0, 0.0, 0.85, 1.0 )
	
#annotationInfo.PointSize = int(height*0.11)
#annotation = Image.CreateAnnotation("NTROPIC ", annotationInfo)
#slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.5, 0.9, Anchor.Center, CompositeOperator.OverCompositeOp)

if slateBG != None :
	slateBgFrame.CompositeWithPositionAndAnchor(slateBG, 1.0, 1.0, Anchor.NorthEast, CompositeOperator.OverCompositeOp)

if logo != None :
	slateBgFrame.CompositeWithPositionAndAnchor(logo, 0.1, 0.8, Anchor.NorthWest, CompositeOperator.OverCompositeOp)
	
#annotationInfo.PointSize = int(height*0.11)
#annotation = Image.CreateAnnotation("NTROPIC ", annotationInfo)
#slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.5, 0.8, PositionalGravity.Center, CompositeOperator.OverCompositeOp)

annotationInfo.DrawShadow = False
annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)

annotationInfo.PointSize = int(height*0.04)
annotation = Image.CreateAnnotation("Artist: "+ params['username'], annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.1, 0.65, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.04)
annotation = Image.CreateAnnotation("File: "+ params['entity'], annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.1, 0.60, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.04)
annotation = Image.CreateAnnotation(params['version'], annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.1, 0.51, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.04)
annotation = Image.CreateAnnotation("Frame Range:  " + str(startFrame) + " - " + str(endFrame), annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.1, 0.45, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.04)
annotation = Image.CreateAnnotation("Resolution: " + str(inFrame.width) + " x " + str(inFrame.height), annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.1, 0.40, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.04)
annotation = Image.CreateAnnotation("LUT: " + LUT, annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.1, 0.35, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.04)
annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)
annotation = Image.CreateAnnotation(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.025, 0.08, Anchor.SouthWest, CompositeOperator.OverCompositeOp)

annotationInfo.PointSize = int(height*0.025)
annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)
annotation = Image.CreateAnnotation(inFile, annotationInfo)
slateBgFrame.CompositeWithPositionAndAnchor(annotation, 0.025, 0.025, Anchor.SouthWest, CompositeOperator.OverCompositeOp)

for frameNumber in range(0, slateFrames) :
	videoEncoder.EncodeNextFrame(slateBgFrame)
		
#if logo != None :
	#origBgFrame.CompositeWithPositionAndAnchor(logo, 0.98, 0.95, Anchor.NorthEast, CompositeOperator.OverCompositeOp)

# encode the video frames
for frameNumber in range(startFrame, endFrame + 1) :

	print "Processing frame: " + str(frameNumber)
	#sys.stdout.flush()
	
	inFile = ReplaceFilenameHashesWithNumber(inFilePattern, frameNumber)
	inFrame = Image.ReadFromFile(inFile)
	inFrame.Resize(width, height)

	#ext = os.path.splitext(inFile)[1][1:].strip()
	if nimEncodeSRGB == "True":
		print "Encoding sRGB"
		displayLut = Draft.LUT.CreateSRGB()
		displayLut.Apply( inFrame )
	#else:
		# print "No LUT Applied"
	
	sys.stdout.flush()
	
	bgFrame = copy.deepcopy(origBgFrame)
	bgFrame.Composite(inFrame, 0.0, 0.5*(letterBoxScale-1.0)/letterBoxScale, CompositeOperator.OverCompositeOp)

	annotationInfo = AnnotationInfo()
	annotationInfo.FontType = "Arial"

	annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)

	#annotationInfo.PointSize = int(height*0.06)
	#annotation = Image.CreateAnnotation(params['entity'], annotationInfo)
	#bgFrame.CompositeWithPositionAndAnchor(annotation, 0.03, 0.97, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

	#annotationInfo.PointSize = int(height*0.045)
	#annotation = Image.CreateAnnotation(params['version'], annotationInfo)
	#bgFrame.CompositeWithPositionAndAnchor(annotation, 0.03, 0.92, Anchor.NorthWest, CompositeOperator.OverCompositeOp)

	#annotationInfo.PointSize = int(height*0.05)
	#annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)
	#annotation = Image.CreateAnnotation(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), annotationInfo)
	#bgFrame.CompositeWithPositionAndAnchor(annotation, 0.025, 0.08, Anchor.SouthWest, CompositeOperator.OverCompositeOp)

	#annotationInfo.PointSize = int(height*0.035)
	#annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)
	#annotation = Image.CreateAnnotation(inFile, annotationInfo)
	#bgFrame.CompositeWithPositionAndAnchor(annotation, 0.025, 0.025, Anchor.SouthWest, CompositeOperator.OverCompositeOp)

	annotationInfo.PointSize = int(height*0.03)
	annotationInfo.Color = ColorRGBA(0.85, 0.85, 0.85, 1.0)
	annotation = Image.CreateAnnotation(str(frameNumber), annotationInfo)
	bgFrame.CompositeWithPositionAndAnchor(annotation, 0.92, 0.01, Anchor.SouthEast, CompositeOperator.OverCompositeOp)

	#bgFrame.WriteToFile(ReplaceFilenameHashesWithNumber(params['outfile'], frameNumber))

	videoEncoder.EncodeNextFrame(bgFrame)
	
# finalize the encoding
videoEncoder.FinalizeEncoding()

'''
#TODO: figure out why os.remove is failing saying file is locked
#	   maybe add timed delay trying every second x 10 till it's free?

Draft.QTFastStart( tempOutFile, params['outFile'] )

try:
	os.remove( tempOutFile )
except:
	print "Failed Removing tempFile after applying QTFastStart"
	traceback( format_exc() )
'''