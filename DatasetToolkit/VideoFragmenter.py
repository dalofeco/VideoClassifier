import numpy as np
import cv2
import os, sys
from tqdm import tqdm

class VideoFragmenter:
    def __init__(self, category, mode, model_version):
        
        # Mode for CNN or RNN (different data structure)
        if (mode == 'cnn' or mode == 'rnn'):
            self.MODE = mode;
        else:
            print("ERROR: Invalid MODE specified!")
            sys.exit()
            
        self.MODEL_VERSION = model_version
        
        # Define frame interval to consider
        self.interval = 2;
        
        # Define directories and create necessary 
        self.tf_files_dir = "../Models/tf_files-v" + str(self.MODEL_VERSION) + "/"
        self.videosDirectory = self.tf_files_dir + "videos/" + category + "/";
        
        # Generate and create dataset save directories for cnn and rnn
        self.datasetDirectory = self.tf_files_dir + "dataset/" + self.MODE + "/" + category + "/"
        self.tryCreateDirectory(self.datasetDirectory);
            
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
        
        saveDir = self.datasetDirectory;
            
         # Generate save directory mode with video titled folder for RNN dataset mode
        if (self.MODE == 'rnn'):
            saveDir = saveDir + videoName[:-4] + '/'
        self.tryCreateDirectory(saveDir)
            
        # Loop through all frames
        while (cap.isOpened() and success):

            # Read next frame
            success, image = cap.read();
                
            # Wait for defined frame interval
            if (count % self.interval == 0):

                # Write out the image
                cv2.imwrite(saveDir + videoName[:-4] + "-%d.jpg" % (count/self.interval), image);

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
    if (len(sys.argv) != 4):
        print("Usage: VideoFragmenter.py CATEGORY MODE MODEL_VERSION")
    
    elif (len(sys.argv) == 4):
        vf = VideoFragmenter(sys.argv[1], sys.argv[2], sys.argv[3]);
        vf.extractAllFrames();

