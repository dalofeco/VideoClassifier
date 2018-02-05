import keyboard
import numpy as np
import cv2
import os

interval = 5;
videosDirectory = "videos/guns/";
framesDirectory = "dataset/guns/"
# positiveFrames = [];

# Define null image, videoName, and count out here for scoping purposes
image = None;
videoName = None;
count = 0;

videoNames = os.listdir(videosDirectory);

# Aadd frames to valid directory on space press
def spacePressed():
	if (not videoName is None and not image is None):
		# Write out onto framesDirectory with %d.jpg appended 
		cv2.imwrite(framesDirectory + videoName + "%d.jpg" % (count/interval), image);
		print("Added frame #" + str(count/interval));

	else:
		print("Well well well...");

	# positiveFrames.append(count/interval);

# def backSpacePressed(videoDirectory):
# 	# Stop video playback

# 	# Move video to scraps directory
# 	os.move(videoDirectory, videosDriectory + "scraps/");

# Add keyboard event function on space press
keyboard.add_hotkey(' ', spacePressed, args=[]);

# For every video in videoNames directory
for videoName in videoNames:

	# Initiate video capture
	cap = cv2.VideoCapture(videosDirectory + videoName);
	success = True;

	while (cap.isOpened() and success):

		# Read next frame
		success, image = cap.read();

		# Only analyze every five frames
		if (count % interval == 0):

			# Show the frame on player
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
			cv2.imshow('image', gray);

		# Break if done
		if (cv2.waitKey(1) == 27):
			break;
		
		count+= 1;

	cap.release();
	cv2.destroyAllWindows();



