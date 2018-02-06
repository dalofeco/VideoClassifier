import keyboard
import numpy as np
import cv2
import os, sys, time

# Options
LOAD_FROM_FILE = True
SAVE_FILE = 'session.sav'
CATEGORY = 'shooting'
VIDEO_FPS = 30.0

# Customizable keyboard controls
PAUSE_HOTKEY = 'p'
EXIT_HOTKEY = 'q'
SAVE_EXIT_HOTKEY = 's'
TOGGLE_RECORD_HOTKEY = ' '
FASTER_HOTKEY = '+'
SLOWER_HOTKEY = '-'

# Experimental Options
MAX_PLAYBACK_SPEED = 100

class VideoClassifier:
    
    def __init__(self, category, state=0):
        
        # Frame interval to consider
        self.interval = 2;
        
        # Playback speed
        self.playbackSpeed = 5;
        
        # Recording mode starts off (saving frames to .jpg)
        self.recordFrame = False;
        
        # Optional state for loading previous classification process
        self.state = state;
        
        # Try to load previous progress from save file
        if (LOAD_FROM_FILE and SAVE_FILE in os.listdir('.')):
            with open(SAVE_FILE, 'r') as saveFile:
                data = saveFile.read();
                if (data):
                    self.state = int(data);
                    print("Loaded state...")
                saveFile.close();
        else:
            print("No save file found.");
        
        # Directories
        self.videosDirectory = "videos/" + category + "/";
        self.framesDirectory = "dataset/" + category + "/"
        
        # Define null image
        self.image = None;
        
        # Define frame count
        self.frameCount = 0;
        
        # Pause
        self.pause = False;
        
    # Start classification process
    def start(self):
        
        # Get list of all videos in directory
        videoNames = os.listdir(self.videosDirectory);
        
        # For every video in videoNames directory
        for videoName in videoNames:
            
            try:
                # Initiate video capture
                cap = cv2.VideoCapture(self.videosDirectory + videoName);
                success = True;

                while (cap.isOpened() and success):
                    
                    # Record start to sync fps
                    frameStartTime = time.time();
                    
                    # Pause
                    while(self.pause):
                        pass

                    # Read next frame
                    success, image = cap.read();
                    self.frameCount+= 1;
                    
                    # Skip all frames before loaded state
                    if (self.frameCount < self.state):
                        continue;

                    # Only analyze every $(interval) frames
                    if (self.frameCount % self.interval == 0):
                        
                        # Make sure video and image not None
                        if (not image is None):
                            
                            # Try 

                            # Show the frame on player
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
                            cv2.imshow('image', gray);

                            # If in recording frame mode then save the frame
                            if (self.recordFrame):
                                try:
                                    # Only write out new frame every interval to avoid duplicates
                                    if (self.frameCount % self.interval == 0):

                                        # Write out onto framesDirectory with %d.jpg appended 
                                        cv2.imwrite(self.framesDirectory + videoName[:-4] + "-" + str(self.frameCount) + ".jpg", image);
                                        print("Added frame %d", self.frameCount);

                                except Exception as e:
                                    print("ERROR: Error with frame #%d", self.frameCount);
                                    print(e);

                        else:
                            print("WARNING: Image not loaded");

                    # Break if done
                    if (cv2.waitKey(1) == 27):
                        break;
                        
                    if (not self.pause):

                        # Calculate needed sleep time for FPS sync
                        sleepTime = (VIDEO_FPS / 60) - (time.time() - frameStartTime)

                        # Account for playback sleep
                        sleepTime *= (1 / self.playbackSpeed) 
                        
                        # Avoid errors for negative times
                        if (sleepTime > 0):
                            time.sleep(sleepTime);

                   

                cap.release();
                cv2.destroyAllWindows();

            except Exception as e:
                print("ERROR: Capture Error")
                print(e);
                
                
    def save(self):
        print("Frame number: ");
        print(self.frameCount);
        
        with open(SAVE_FILE, 'w') as saveFile:
            saveFile.write(str(self.frameCount));
            saveFile.close();
            
        print("Saved to " + SAVE_FILE);
            
            
    # Toggle recording frames on or off
    def toggleRecordFrame(self):
        if (self.recordFrame):
            self.recordFrame = False;
        else:
            self.recordFrame = True;
    
    # Toggle pause setting
    def pauseToggle(self):
        if self.pause:
            self.pause = False
            print("Unpaused.")
        else:
            self.pause = True
            print("Paused." )
            
    def playFaster(self):
        if self.playbackSpeed < MAX_PLAYBACK_SPEED:
            self.playbackSpeed += 2;
            print("Playback Speed Level: %d" % self.playbackSpeed)
        else:
            print("Playback Speed Level: MAX")
            
    def playSlower(self):
        if self.playbackSpeed > 2:
            self.playbackSpeed -= 2;
            print("Playback Speed Level: %d" % self.playbackSpeed)
        else:
            print("Playback Speed Level: MIN")


# Create new instance of classifier with category (folder name)
videoClassifier = VideoClassifier(CATEGORY);
            
# Add frames to valid directory on space press
def recordPressed():
    videoClassifier.toggleRecordFrame();
    
def savePressed():
    videoClassifier.save();
    
def exitPressed():
    print("Quitting...")
    os._exit(0)
    
def pausePressed():
    videoClassifier.pauseToggle();
    
def fasterPressed():
    videoClassifier.playFaster();
    
def slowerPressed():
    videoClassifier.playSlower();
	
# Add keyboard event function on space press
keyboard.add_hotkey(TOGGLE_RECORD_HOTKEY, recordPressed, args=[]);
keyboard.add_hotkey(SAVE_EXIT_HOTKEY, savePressed, args=[]);
keyboard.add_hotkey(EXIT_HOTKEY, exitPressed, args=[]);
keyboard.add_hotkey(PAUSE_HOTKEY, pausePressed, args=[]);
keyboard.add_hotkey(FASTER_HOTKEY, fasterPressed, args=[]);
keyboard.add_hotkey(SLOWER_HOTKEY, slowerPressed, args=[]);

# Start classification window
videoClassifier.start()


# def backSpacePressed(videoDirectory):
# 	# Stop video playback

# 	# Move video to scraps directory
# 	os.move(videoDirectory, videosDriectory + "scraps/");



