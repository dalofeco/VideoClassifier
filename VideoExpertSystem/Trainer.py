import tensorflow as tf
from tf_scripts import retrain as tf_retrain
from sklearn.model_selection import train_test_split
from tflearn.data_utils import to_categorical
import tflearn
import numpy as np

import time
import os, sys, pickle
from tqdm import tqdm

import Classifier
import Categories

# Class for training CNN layer
class CNNTrainer():
    
    # Constructor
    def __init__(self, modelVersion):
        
        # Initialize as class variables
        self.tf_files_dir = "../Models/tf_files-v{0}/".format(modelVersion)
        self.dataset_dir = self.tf_files_dir + 'dataset/cnn/'
        self.modelVersion = modelVersion;
        
    # Launches the retraining process for the CNN
    def retrain(self, architecture='inception_v3', training_steps=100):
        
        # Performance metrics
        start = time.time();
        
        bottleneck_dir = self.tf_files_dir + 'bottlenecks/'
        model_dir = self.tf_files_dir + 'models/'
        summaries_dir = self.tf_files_dir + 'training_summaries/' + architecture
        output_graph_dir = self.tf_files_dir + 'retrained_graph.pb'
        output_labels_dir = self.tf_files_dir + 'retrained_labels.txt'
        
        # Very nsecure, replace with safer bridge
        os.system('python3 -m tf_scripts.retrain --bottleneck_dir=' + bottleneck_dir + ' --how_many_training_steps=' + str(training_steps) + ' --model_dir=' + model_dir + ' --sumarries_dir=' + summaries_dir + ' --output_graph=' + output_graph_dir + ' --output_labels=' + output_labels_dir + ' --architecture=' + architecture + ' --image_dir=' + self.dataset_dir);
        
        # Log time performance details
        elapsedTime = time.time() - start;
        print("Completed training process in {0:2.0f}:{1:2.0f}:{2:2.0f}!".format(elapsedTime%(3600*24)/3600, (elapsedTime%3600)/60, elapsedTime%60));
        
# Example CNN training
# trainer = CNNTrainer()
# trainer.retrain()
    
    
# Class for training RNN layer
class RNNTrainer():

    def __init__(self, labels, modelVersion):
        
        # Define model version to use (tf_files-v[0.3])
        self.modelVersion = modelVersion
        
        # Initialize important directories as class variables
        self.tf_files_dir = '../Models/tf_files-v{0}/'.format(self.modelVersion)
        self.dataset_dir = self.tf_files_dir + 'dataset/rnn/'
        self.features_dir = self.tf_files_dir + 'features/'
        
        # Save labels to be considered
        self.labels = labels;
        
    # Prepare data, then train
    def autoTrain(self):
        self.extractPoolLayerData(self.labels);
        self.train();
        
    # Execute training after rnn dataset is ready
    def train(self):
        
        print("Initiating RNN training...")
        
        # Define batch size
        batch_size = 20
        
        # Define number of frames
        numOfFrames = 100;
        
        # Performance metrics
        start = time.time();
        
        # Load training data
        X_train, X_test, y_train, y_test = self.readFeatures();
        
        # Log time elapsed loading training data
        print("Training data loaded in %d seconds!", time.time() - start)
        
        # Get num of categories
        numOfCategories = len(y_train[0])
        print("Num of Categories: %d", numOfClasses)
        
        # Get our LSTMRNN
        net = LSTMRNN.getNetwork(numOfClasses, numOfFrames);
        
        # Train the model
        model = tflearn.DNN(net, tensorboard_verbose=0)
        model.fit(X_train, y_train, validation_set=(X_test, y_test), show_metric=True, batch_size=batch_size, snapshot_step=100, n_epoch=4)
        
        # And save it
        model.save(self.tf_files_dir + 'checkpoints/rnn.tflearn');
        
        
    # Extracts all features from pooling layer of CNN to dataset files for RNN training
    def extractPoolLayerData(self, labels):

        # Performance monitoring
        loadStart = time.time();

        # Unpersists graph from file
        with tf.gfile.FastGFile(self.tf_files_dir + "retrained_graph.pb", 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

            with tf.Session() as sess:

                # Feed the image_data as input to the graph and get pool tensor layer
                pool_tensor = sess.graph.get_tensor_by_name('pool_3:0')

                print("Loaded tensor in %d seconds", time.time() - loadStart);
                       
                # Do for all labeled categories
                for label in labels:
                    
                    # Performance monitoring
                    labelStart = time.time();
                    
                    # Generate output folder directory and create folder
                    output_folder_dir = self.features_dir + label + '/';
                    os.mkdir(output_folder_dir);
                    
                    # Do for every batch (frames) within category
                    for batchName in os.listdir(self.dataset_dir + label):
                    
                        # Performance monitoring
                        videoStart = time.time();

                        # Load images (frames)
                        frames = [];
                        imagesDirs = os.listdir(self.dataset_dir + label + '/' + batchName);

                        # Set pool features output directory
                        output_dir = ouput_folder_dir + batchName + '.dat';

                        # Store all features in sequential array
                        cnn_features = []

                        # Progress bar
                        pbar = tqdm(total=len(frames))

                        # For every image in the video frames directory
                        for i, imageDir in enumerate(imagesDirs):

                            # Load image data
                            image_data = tf.gfile.FastGFile(imageDir, 'rb').read();

                            # Run CNN and extract pool tensor representation
                            try:
                                cnn_representation = sess.run(pool_tensor, {'DecodeJpeg/contents:0': image_data})
                            except KeyboardInterrupt:
                                print("Exiting... Detected CTRL+C")
                                sys.exit()
                            except:
                                print("Error making prediction, continuing..");
                                continue;

                            # Save the representation
                            frame_data = [cnn_representation, label];
                            cnn_features.append(frame_data);


                            # Update progress bar
                            if i > 0 and i % 10 == 0:
                                pbar.update(10);

                        pbar.close()

                        # Log batch loading time
                        print(batchName + " processed in %d seconds!" % (time.time() - videoStart));

                        # Open output file for features
                        with open(output_dir, 'wb') as featuresOutput:
                            featuresOutput.write(pickle.dump(cnn_features));
                            featuresOutput.close();
                    
                    # Log label loading time
                    print (label + " processed in %d seconds!" % (time.time() - labelStart))
                        
    # Get the data from our saved predictions/pooled features
    def readFeatures(self):
    
        start = time.time();

        # Local vars.
        X = []
        y = []
        temp_list = []

        # Initiate num of categories to 0
        num_categories = 0

        # Iterate through all category folders
        categories = os.listdir(self.features_dir)
        for category in categories:

            # Count num of categories
            num_categories += 1;

            batchFeatures = os.listdir(category);

            # For each feature in the video batch
            for batchFeatures in batchFeatures:

                # Declaration for scoping reasons
                actualLabel = "";

                # Open and get the features.
                with open(batchFeatures, 'rb') as fin:
                    frames = pickle.load(fin)

                    # Enumerate and iterate through frames
                    for i, frame in enumerate(frames):
                        features = frame[0]
                        actualLabel = frame[1]

                        # Add to the queue
                        temp_list.append(features)

            # Convert our labels into binary.
            labelNum = Categories.labelToNumber(actualLabel);

            # Flatten list, and append to X and Y datasets
            flat = list(temp_list)
            X.append(np.array(flat))
            y.append(labelNum)


        # Print size of dataset
        print("Total dataset size: %d" % len(X))

        # Convert to Numpy arrays
        X = np.array(X)
        y = np.array(y)

        # Reshape 
        X = X.reshape(-1, num_frames, input_length)

        # One-hot encoded categoricals.
        y = to_categorical(y, num_classes)

        # Split into train and test.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

        # Log loading time
        print("Loaded data in %d seconds!", time.time() - start)

        # Return data
        return X_train, X_test, y_train, y_test


# Example RNN training

# Initialize trainer
# trainer = RNNTrainer(['shooting', 'normal', 'explosion'])

# Extract CNN Pool Layer Data
# trainer.extractPoolLayerData()

# Launch training process
# trainer.train()

