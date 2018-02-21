import keyboard
import numpy as np
import cv2
import os, sys, time

# Options
LOAD_FROM_FILE = True
SAVE_FILE = 'session.sav'
DEFAULT_PLAYBACK_SPEED = 20;


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
    
    def __init__(self, category, version, mode='cnn', state=0, interval=3):
        
        # Validate modes
        if (mode != 'cnn' and mode != 'rnn'):
            print("ERROR: Invalid mode specified! Only 'cnn' and 'rnn' modes supported.")
            sys.exit()
            
        # Save mode
        self.mode = mode;
        
        # Frame interval to consider
        self.interval = interval;
        
        # Playback speed
        self.playbackSpeed = DEFAULT_PLAYBACK_SPEED;
        
        # Recording mode starts off (saving frames to .jpg)
        self.recordFrame = False;
        
        # Optional state for loading previous classification process
        self.state = state;
        
        # Save category and model version
        self.category = category;
        self.model_version = version
        
        # Generate categorical save file
        self.saveFile = self.category + '-' + SAVE_FILE;
        
        # Try to load previous progress from save file
        if (LOAD_FROM_FILE and self.saveFile in os.listdir('.')):
            with open(self.saveFile, 'r') as saveFile:
                data = saveFile.read();
                if (data):
                    self.state = int(data);
                    print("Loaded state...")
                saveFile.close();
        else:
            print("No save file found.");
        
        # Directories
        self.tf_files_dir = "../Models/tf_files-v" + str(self.model_version) + "/"
        self.videosDirectory = self.tf_files_dir + "videos/" + category + "/";
        self.framesDirectory = self.tf_files_dir + "dataset/" + self.mode + "/" + category + "/"
        self.tryCreateDirectory(self.framesDirectory)
        
        # Define null image
        self.image = None;
        
        # Define frame count
        self.frameCount = 0;
        
        # Pause
        self.pause = False;
        
    def tryCreateDirectory(self, dir):
        try:
            os.mkdir(dir);
        except FileExistsError:
            pass
        
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
                                        print("Added frame %d" % self.frameCount);

                                except Exception as e:
                                    print("ERROR: Error with frame #%d" % self.frameCount);
                                    print(e);

                        else:
                            print("WARNING: Image not loaded");

                    # Break if done
                    if (cv2.waitKey(1) == 27):
                        break;
                        
                    if (not self.pause):

                        # Calculate needed sleep time for speed sync and sleep
                        sleepTime = (1 / self.playbackSpeed)                         
                        time.sleep(sleepTime);

                   
                # Release capture and close cv2 video playback window
                cap.release();
                cv2.destroyAllWindows();

            except Exception as e:
                print("ERROR: Capture Error")
                print(e);
                
        # Print done message and delete save file
        print("Finished analyzing {0} videos and {1} frames.".format(len(videoNames), self.frameCount))
        os.remove(self.saveFile)
                
                
    def save(self):
        print("Frame number: ");
        print(self.frameCount);
        
        with open(self.saveFile, 'w') as saveFile:
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

    
# Main function for command line running
if __name__ == '__main__':
    
    # Count arguments supplied
    argCount = len(sys.argv)
    
    # Make sure at least 2 arguments are supplied
    if argCount > 2:
        
        videoClassifier = None;
        
        category = sys.argv[1];
        model_version = sys.argv[2]
        
        # Create new instance of classifier with supplied params
        # Just category and model supplied
        if (argCount == 3):
            videoClassifier = VideoClassifier(category, model_version)
        elif (argCount == 4):
            mode = sys.argv[3];
            videoClassifier = VideoClassifier(category, model_version, mode=mode)
        elif (argCount == 5):
            mode = sys.argv[3]
            state = sys.argv[4]
            videoClassifier = VideoClassifier(category, model_version, mode=mode, state=state)
        elif (argCount == 6):
            mode = sys.argv[3]
            state = sys.argv[4]
            interval = sys.argv[5]
            videoClassifier = VideoClassifier(category, model_version, mode=mode, state=state, interval=interval)
        else:
            print("ERROR: Too many options provided");
            sys.exit();

        # Add keyboard event function on space press
        keyboard.add_hotkey(TOGGLE_RECORD_HOTKEY, recordPressed, args=[]);
        keyboard.add_hotkey(SAVE_EXIT_HOTKEY, savePressed, args=[]);
        keyboard.add_hotkey(EXIT_HOTKEY, exitPressed, args=[]);
        keyboard.add_hotkey(PAUSE_HOTKEY, pausePressed, args=[]);
        keyboard.add_hotkey(FASTER_HOTKEY, fasterPressed, args=[]);
        keyboard.add_hotkey(SLOWER_HOTKEY, slowerPressed, args=[]);

        # Start classification window
        videoClassifier.start()
        
    # Invalid arguments, print usage message
    else:
        print("Usage: VideoClassifier.py (category) (model_version) [mode] [state] [interval]")
        sys.exit()
    
    



