import numpy as np
import cv2


def extractFrames(videoLocation, destinationDir):
	cap = cv2.VideoCapture(videoLocation);
	success = True;
	count = 0;

	while (cap.isOpened() and success):
		# Read next frame
		success, image = cap.read();

		# Write out onto frame%d.jpg
		cv2.imwrite(destinationDir + "frame%d.jpg" % count, image);

		# Break if esc?
		if (cv2.waitKey(1) == 27):
			break;
		count+= 1;

	cap.release();
	cv2.destroyAllWindows();

extractFrames("robberies/testvideo.mp4", "frames/");
