import numpy as np
import cv2
import os

class VideoFragmenter:

	def __init__(self, category):
		self.interval = 10;
		self.videosDirectory = "videos/" + category + "/";
		self.framesDirectory = "dataset/" + category + "/"

	def renameAllVids(self, directory):
		for filename in os.listdir(directory):
			os.makedirs(filename[:-4]);
			os.rename(filename, filename[:-4] + "/" + filename);
		print ("Done!");

	def extractFrames(self, videoName):

		cap = cv2.VideoCapture(self.videosDirectory + videoName);
		success = True;
		count = 0;

		while (cap.isOpened() and success):

			# Read next frame
			success, image = cap.read();

			if (count % self.interval == 0):

				# Write out onto frame%d.jpg
				cv2.imwrite(self.framesDirectory + videoName[:-4] + "-%d.jpg" % (count/self.interval), image);

			# Break if esc?
			if (cv2.waitKey(1) == 27):
				break;
			count+= 1;

		cap.release();
		cv2.destroyAllWindows();

	def extractAllFrames(self):

		videoNames = os.listdir(self.videosDirectory);
		for videoName in videoNames:
			self.extractFrames(videoName);


vf = VideoFragmenter("shooting");
vf.extractAllFrames();
