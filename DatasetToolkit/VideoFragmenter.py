import numpy as np
import cv2
import os, sys
from tqdm import tqdm

MODEL_VERSION = 0.2;

class VideoFragmenter:
    def __init__(self, category, mode):
        
        # Mode for CNN or RNN (different data structure)
        if (mode == 'cnn' or mode == 'rnn'):
            self.MODE = mode;
        else:
            print("ERROR: Invalid MODE specified!")
            sys.exit()
        
        # Define frame interval to consider
        self.interval = 10;
        
        # Define frames per batch (folder)
        self.batchFrameLimit = 100;
        
        # Define directories and create necessary 
        self.tf_files_dir = "../Models/tf_files-v" + str(MODEL_VERSION) + "/"
        self.videosDirectory = self.tf_files_dir + "videos/" + category + "/";
        self.framesDirectory = self.tf_files_dir + "dataset/" + self.MODE + "/" + category + "/"
        self.tryCreateDirectory(self.framesDirectory);
            
    def tryCreateDirectory(self, dir):
        try:
            os.mkdir(dir);
        except FileExistsError:
            pass

    def renameAllVids(self, directory):
        for filename in os.listdir(directory):
            os.mkdir(filename[:-4]);
            os.rename(filename, filename[:-4] + "/" + filename)
        print ("Done!");

    def extractFrames(self, videoName):
        cap = cv2.VideoCapture(self.videosDirectory + videoName);
        success = True;
        count = 0;
        dirCount = 0;
            
        while (cap.isOpened() and success):

            # Read next frame
            success, image = cap.read();
            
            saveDirectory = "";
            
            # Generate save directory for CNN mode
            if (self.MODE == 'cnn'):
                saveDirectory = self.framesDirectory;
            
            # Generate save directory for every X amount of frames on RNN mode
            elif (self.MODE == 'rnn' and count % (self.batchFrameLimit * self.interval) == 0):
                saveDirectory = self.framesDirectory + videoName[:-4] + "-" + str(dirCount) + "/"
                self.tryCreateDirectory(saveDirectory)
                dirCount += 1;
                
            else:
                print("ERROR: MODE not recognized!")
                sys.exit();

            # Wait for defined interval
            if (count % self.interval == 0):

                # Write out onto frame%d.jpg
                cv2.imwrite(saveDirectory + videoName[:-4] + "-%d.jpg" % (count/self.interval), image);

            #Break if esc?
            if (cv2.waitKey(1) == 27):
                break;
            count+= 1;

        cap.release();
        cv2.destroyAllWindows();

        
    # Extracts all frames from videos in directory
    def extractAllFrames(self):

        # Load all video names from directory
        videoNames = os.listdir(self.videosDirectory);
        
        # Progress bar
        pbar = tqdm(total=len(videoNames));
        
        for videoName in videoNames:
            self.extractFrames(videoName);
            
            # Update progress bar every video
            pbar.update(1);
                
        pbar.close()

if __name__ == '__main__':
    # Make sure expected num of arguments
    if (len(sys.argv) != 3):
        print("Usage: VideoFragmenter.py CATEGORY MODE")
    
    elif (len(sys.argv) == 3):
        vf = VideoFragmenter(sys.argv[1], sys.argv[2]);
        vf.extractAllFrames();

