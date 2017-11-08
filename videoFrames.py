import numpy as np
import cv2

class VideoFragmenter:

	def __init__(self):
		self.interval = 10;
		print ("Created");

	def extractFrames(self, videoLocation, destinationDir):
		cap = cv2.VideoCapture(videoLocation);
		success = True;
		count = 0;

		while (cap.isOpened() and success):
			# Read next frame
			success, image = cap.read();

			if (count % self.interval == 0):

				# Write out onto frame%d.jpg
				cv2.imwrite(destinationDir + "frame%d.jpg" % (count/self.interval), image);

			# Break if esc?
			if (cv2.waitKey(1) == 27):
				break;
			count+= 1;

		cap.release();
		cv2.destroyAllWindows();

vf = VideoFragmenter();
vf.extractFrames("videos/robberies/testvideo.mp4", "frames/");
