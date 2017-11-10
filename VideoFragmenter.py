import numpy as np
import cv2

class VideoFragmenter:

	def __init__(self):
		self.interval = 10;
		self.videosDirectory = "videos/robberies/";

	def renameAllVids(self, directory):
		for filename in os.listdir(directory):
			os.makedirs(filename[:-4]);
			os.rename(filename, filename[:-4] + "/" + filename);
		print ("Done!");

	def extractFrames(self, videoName):

		cap = cv2.VideoCapture(self.videosDirectory + videoName + "/" + videoName + ".mp4");
		success = True;
		count = 0;

		while (cap.isOpened() and success):

			# Read next frame
			success, image = cap.read();

			if (count % self.interval == 0):

				# Write out onto frame%d.jpg
				cv2.imwrite(self.videosDirectory + videoName + "/frames/" + "frame%d.jpg" % (count/self.interval), image);

			# Break if esc?
			if (cv2.waitKey(1) == 27):
				break;
			count+= 1;

		cap.release();
		cv2.destroyAllWindows();


vf = VideoFragmenter();
vf.extractFrames("testvideo");
