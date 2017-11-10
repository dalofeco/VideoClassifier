import keyboard
import numpy as np
import cv2

interval = 5;
videosDirectory = "videos/robberies/";
videoName = "testvideo"
positiveFrames = [];


def spacePressed():
	positiveFrames.append(count/interval);
	print("Added frame #" + str(count/interval));

keyboard.add_hotkey(' ', spacePressed, args=[]);

cap = cv2.VideoCapture(videosDirectory + videoName + "/" + videoName + ".mp4");
success = True;
count = 0;


while (cap.isOpened() and success):

	# Read next frame
	success, image = cap.read();

	if (count % interval == 0):

		# Write out onto frame%d.jpg
		cv2.imwrite(videosDirectory + videoName + "/frames/" + "frame%d.jpg" % (count/interval), image);

		# Show the frame on player
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
		cv2.imshow('image', gray);

	# Break if done
	if (cv2.waitKey(1) == 27):
		break;
	
	count+= 1;

cap.release();
cv2.destroyAllWindows();

print positiveFrames;



