import tensorflow as tf
from tensorflow.python.platform import gfile
from tf_scripts import retrain as tf_retrain
from sklearn.model_selection import train_test_split
from tflearn.data_utils import to_categorical

import tflearn
import numpy as np
from collections import deque

import time
import os, sys, pickle
from tqdm import tqdm

import Classifier
import Categories

# Base Trainer Class for CNNTrainer and RNNTrainer
class Trainer():
    
    # Constructor for Trainer base class
    def __init__(self, modelVersion):
        
        # Initialize as class variables
        self.tf_files_dir = "../Models/tf_files-v{0}/".format(modelVersion)
        self.dataset_dir = self.tf_files_dir + 'dataset/cnn/'
        self.modelVersion = modelVersion;
        
    # Simple function wrapping mkdir in catch FileExistsError
    def tryCreateDirectory(self, dir):
        try:
            os.mkdir(dir);
        except FileExistsError:
            pass
        
    # Exports .pb file into tensorboard graphable logs
    def extractTBfromGraph(self):

        LOGDIR = self.tf_files_dir + "/"
        
        with tf.Session() as sess:
            model_filename = self.tf_files_dir + '/retrained_graph.pb'
            with gfile.FastGFile(model_filename, 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                g_in = tf.import_graph_def(graph_def)
                LOGDIR='log.txt'
                train_writer = tf.summary.FileWriter(LOGDIR)
                train_writer.add_graph(sess.graph)
                train_writer.flush()
                train_writer.close()

        print("Now run: 'tensorboard --logdir [PATH-TO-LOG-FILE]")

# Class for training CNN layer
class CNNTrainer(Trainer):
    
    # Constructor
    def __init__(self, modelVersion):
        
        # Call super class construction
        super().__init__(modelVersion)
        # Initializes the following
        # self.tf_files_dir
        # self.modelVersion
        
        # Init dataset directory
        self.dataset_dir = self.tf_files_dir + "dataset/cnn/"
        
        
    # Launches the retraining process for the CNN
    def retrain(self, architecture='inception_v3', training_steps=100):
        
        # Performance metrics
        start = time.time();
        
        bottleneck_dir = self.tf_files_dir + 'bottlenecks/'
        model_dir = self.tf_files_dir + 'models/'
        summaries_dir = self.tf_files_dir + 'training_summaries.tb'
        output_graph_dir = self.tf_files_dir + 'retrained_graph.pb'
        output_labels_dir = self.tf_files_dir + 'retrained_labels.txt'
        
        # Very nsecure, replace with safer bridge
        os.system('python -m tf_scripts.retrain --bottleneck_dir=' + bottleneck_dir + ' --how_many_training_steps=' + str(training_steps) + ' --model_dir=' + model_dir + ' --sumarries_dir=' + summaries_dir + ' --output_graph=' + output_graph_dir + ' --output_labels=' + output_labels_dir + ' --architecture=' + architecture + ' --image_dir=' + self.dataset_dir);
        
        # Log time performance details
        elapsedTime = time.time() - start;
        print("Completed training process in {0:2.0f}:{1:2.0f}:{2:2.0f}!".format(elapsedTime%(3600*24)/3600, (elapsedTime%3600)/60, elapsedTime%60));
        
# Example CNN training
# trainer = CNNTrainer()
# trainer.retrain()
    
    
# Class for training RNN layer
class RNNTrainer(Trainer):

    def __init__(self, labels, modelVersion):
        
        # Initialize superclass constructor
        super().__init__(modelVersion)
         # Initializes the following
        # self.tf_files_dir
        # self.modelVersion
        
        # Initialize dataset directory
        self.dataset_dir = self.tf_files_dir + 'dataset/rnn/'
        self.sequences_dir = self.tf_files_dir + 'sequences/'
        
        # Number of frames to consider at once
        self.FRAME_BATCH_LENGTH = 30
        
        # 2048-d vector length for image features before pooling layer from image classifier CNN 
        self.INPUT_LENGTH = 2048 
        
        self.features_dir = self.tf_files_dir + 'features/'
        self.tryCreateDirectory(self.features_dir)
        
        # Save labels to be considered
        self.labels = labels;
        
        
     # Extracts all features from pooling layer of CNN to dataset files for RNN training
    def extractPoolLayerData(self):

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

                print("Loaded tensor in %.2f seconds" % (time.time() - loadStart));
                       
                # Do for all labeled categories
                for label in self.labels:
                    
                    # Generate output folder directory and create folder
                    output_folder_dir = self.features_dir + label + '/';
                    self.tryCreateDirectory(output_folder_dir);
                    
                    # Get videos within category
                    videos = os.listdir(self.dataset_dir + label)
                    
                    # Performance monitoring
                    labelStart = time.time();
                    
                    # Progress bar
                    pbar = tqdm(total=len(videos))

                    # For each video
                    for video in videos:
                    
                        # Load images (frames)
                        frames = [];
                        imagesDir = self.dataset_dir + label + '/' + video + '/'
                        imageNames = os.listdir(imagesDir);

                        # Set pool features output directory to video name
                        output_dir = output_folder_dir + video + '.dat';

                        # Skip files that aleady exists (already processed)
                        if (os.path.exists(output_dir)):
                            pbar.update(1)
                            continue

                        # Store all features in sequential array
                        cnn_features = []

                        # For every image in the video frames directory
                        for i, imageName in enumerate(imageNames):

                            # Load image data
                            image_data = tf.gfile.FastGFile(imagesDir + imageName, 'rb').read()

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


                        # Save features of batch to output file
                        with open(output_dir, 'wb') as featuresOutput:
                            pickle.dump(cnn_features, featuresOutput);
                            featuresOutput.close();

                        # Update progress bar
                        pbar.update(1);

                    # Close progress bar
                    pbar.close()
                    
                    # Log label loading time
                    print (label + " processed in %d seconds!" % (time.time() - labelStart))
                        
                        
    # Get the data from our saved predictions/pooled features, 
    # and extract feature sequences, saving them to disk
    #
    # RETURNS:
    #   sequence_length: <int> - the number of sequences processed
    #
    def extractFeatures(self, frameBatchLength, batchSize):
        
        # Performance metrics
        start = time.time();

        # X and y for dataset
        X = []
        y = []

        # Initialize featuresDeque for serving as frame features buffer
        featuresDeque = deque()
        
        # Initiate num of categories to 0
        num_categories = 0

        # Iterate through all category folders
        categories = os.listdir(self.features_dir)
        for category in self.labels:

            # Count num of categories
            num_categories += 1;

            # List video features files
            videosFeatures = os.listdir(self.features_dir + category);
            
            # Progress bar and start time for performance metrics
            pbar = tqdm(total=len(videosFeatures))
            startTime = time.time()

            # For each feature in the video batch
            for videoFeatures in videosFeatures:

                # Define full path for video features
                videoFeaturesPath = self.features_dir + category + '/' + videoFeatures
                
                # Declaration for scoping reasons
                actualLabel = "";

                # Open and get the features.
                with open(videoFeaturesPath, 'rb') as fin:
                    frameFeatures = pickle.load(fin)

                    # Enumerate and iterate through frames
                    for i, frame in enumerate(frameFeatures):
                        
                        # Only for every four frames
                        if (i % 4) == 0:          
                            
                            # Read features and label
                            cnnFeatures = frame[0]
                            actualLabel = frame[1]
                        
                            # If deque of size of batch length, start adding to X and Y
                            if (len(featuresDeque) == frameBatchLength - 1):
                                featuresDeque.append(cnnFeatures)
                                X.append(np.array(list(featuresDeque)))
                                y.append(Categories.labelToNum(actualLabel))
                                featuresDeque.popleft()
                            else:
                                # Add to the deque
                                featuresDeque.append(cnnFeatures)
                        
                        
                            
                # Update progress bar
                pbar.update(1)

            # Close progress bar and print category done message 
            pbar.close()
            
            # Calculate time for performance metrics
            timeElapsed = time.time() - startTime
            print(category + " finished in {:.2f} seconds.".format(timeElapsed))

            
        # Calculate length of the dataset
        datasetLength = len(X)
            
        # Print size of dataset
        print("Total dataset size: {}".format(datasetLength))

        # Convert to Numpy arrays
        X = np.array(X)
        y = np.array(y)

        # Reshape to dimensions, with batches of defined input length
        X = X.reshape(datasetLength, frameBatchLength, self.INPUT_LENGTH)
        
        print("X Shape:")
        print(X.shape)

        print("Y Shape:")
        print(y.shape)
        
        # One-hot encoded categoricals.
        y = to_categorical(y, num_categories)

        # Split into train and test.
        # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

        # Log loading time
        print("Loaded data in {} seconds!".format(time.time() - start))
        print("Starting save process")
        
        # Calculate num of batches
        num_batches = len(X) // batchSize
        
        # For each batch to be created
        for i in range(0, num_batches):
            
            # Define batch object to save to file
            batch = { 'x':[], 'y':[] }
            
            # For each element in the batch
            for ii in range(0, batchSize):
                
                # Calculate index in outer arrays
                index = (i * batchSize) + ii
            
                # Append X and y elements to batch
                batch['x'].append(X[index])
                batch['y'].append(y[index])
                
                
            # Define the file name
            batchFileName = self.sequences_dir + "sequence-{}.data".format(i)
            
            # Open file in writing mode
            with open(batchFileName, "wb+") as batchFile:
                
                # Dump batch object to batchfile using pickle
                pickle.dump(batch, batchFile)
                
        # Log performance time
        print("Saved feature sequences in {} seconds!".format(time.time() - start))
        
        # Return number of sequences
        return len(X)
    
    
    # Fetch a specified batch by number
    #
    def fetchBatch(self, batchNumber):
        
        # Define X and y to None
        X = None
        y = None
        
        # Define the file name
        batchFileName = self.sequences_dir + "sequence-{}.data".format(batchNumber)
    
        # Open the batch file
        with open(batchFileName, "rb") as batchFile:
            
            # Load batch from file
            batch = pickle.load(batchFile)
            
            X = batch['x']
            y = batch['y']
    
        # Return batch data
        return X, y
    
            
    
    
    # Prepare data, then train
    def autoTrain(self):
        self.extractPoolLayerData();
        self.train();
        
        
    # Execute training after rnn dataset is ready
    def train(self, num_batches):
        
        # Log
        print("Initiating LSTM training...")
        
        # Performance metrics
        start = time.time();
        
        # Training checkpoints
        CHECKPOINT_PATH = self.tf_files_dir + "rnn-checkpoints/"
        
        # Model output dir
        MODEL_OUTPUT_DIR = self.tf_files_dir + "rnn-model/";
        
        # TensorBoard log dir
        TB_LOG_DIR = self.tf_files_dir + "rnn-logs/";

        
        # DEFINE LSTM RNN OPTIONS
        
        # Number of epochs to train for
        num_epochs = 3
                
        # Frames lookback length
        truncated_backprop_length = 30
        
        # Define state size
        state_size = 2048
        
        # Define the num of classification classes
        num_classes = len(self.labels)
        
        # Size of the batch
        batch_size = 1
        
        
        # Define X batch placeholder
        X_batch_ph = tf.placeholder(tf.float32, [batch_size, truncated_backprop_length, self.INPUT_LENGTH], name="sequence_input")
        
        # Y batch has batch_size elements, with categories for each backprop frame
        y_batch_ph = tf.placeholder(tf.int32, [batch_size, num_classes], name="y_output")
        
        # Define cell and hidden state
        cell_state_ph = tf. placeholder(tf.float32, [batch_size, state_size])
        hidden_state_ph = tf.placeholder(tf.float32, [batch_size, state_size])
        
        # Define init state for LSTM cell
        init_state = tf.nn.rnn_cell.LSTMStateTuple(cell_state_ph, hidden_state_ph)
        
        with tf.name_scope('weights'):
            # Initialize weight variable tensors with random data
            W = tf.Variable(np.random.rand(state_size, num_classes), dtype=tf.float32)
            # Define variable summaries for TensorBoard
            variable_summaries(W)
            
        with tf.name_scope('bias'):
            # Initialize bias variable tensors with zeroes
            b = tf.Variable(np.zeros((1 , num_classes)), dtype=tf.float32)
            # Define variable summaries for TensorBoard
            variable_summaries(b)
        
        # Define input series and labels series as unstacking of X and Y placeholders
        inputs_series = tf.unstack(X_batch_ph, axis=1)
        labels_series = tf.unstack(y_batch_ph, axis=1)
        
        # Define LSTM cell
        cell = tf.nn.rnn_cell.BasicLSTMCell(state_size, state_is_tuple=True)
        
        # Create RNN from LSTM cell and inputs
        states_series, current_state = tf.nn.static_rnn(cell, inputs_series, init_state)

        # Define the logits fully connected layer   
        logits_series = [tf.matmul(state, W) + b for state in states_series]
        
        # Define name for prediction op
        with tf.name_scope("predictions_series"):

            # Define softmax layer for one-hot encoding of output classification
            predictions_series = [tf.nn.softmax(logits) for logits in logits_series]
        
        # Define name scope for ops
        with tf.name_scope("loss"):
            # Define losses function
            losses = [tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels) for logits, labels in zip(logits_series, labels_series)]

            # Define variable summaries for losses
            variable_summaries(losses)
            
        # Define total loss function
        total_loss = tf.reduce_mean(losses)
        
        # Define training step optimizer to minimize loss function
        train_step = tf.train.AdagradOptimizer(0.3).minimize(total_loss)
        
        # Initialize saver with all vars and ops
        saver = tf.train.Saver();
        
        # Initialize start time
        startTime = time.time();
                
        print("Initiating TensorFlow Session...")
        
        # INITIALIZE SESSION
        with tf.Session() as sess:
            
            # Start TensorBoard logger
            tbFileWriter = tf.summary.FileWriter(TB_LOG_DIR, sess.graph);
            
            # Initialize all variables
            sess.run(tf.global_variables_initializer())
        
            # Define list to keep track of loss
            loss_list = []
            
            # Define counter for tensorboard
            counter = 0
            
            # Repeat for each epoch
            for epoch_idx in range(0, num_epochs):
                
                print("Loading Data for Epoch", epoch_idx)
                
                # Define cell and hidden state to zeroes
                _current_cell_state = np.zeros((batch_size, state_size))
                _current_hidden_state = np.zeros((batch_size, state_size))
            
                # Batching logistics
                for batch_idx in range(num_batches):
                    
                    # Fetch x and y for current batch
                    x,y = self.fetchBatch(batch_idx)
                    
                    # Calculate start and end indexes
                    start_idx = batch_idx * batch_size
                    end_idx = start_idx + batch_size
                    
                    # Slice the batch
                    batchX = x[start_idx:end_idx,:,:]
                    batchY = y[start_idx:end_idx,:]
                    
                    # TB merge
                    merge = tf.summary.merge_all()
                    
                    # Run the training session
                    summary, _total_loss, _train_step, _current_state, _predictions_series = sess.run([merge, total_loss, train_step, current_state, predictions_series], 
                                                                                             feed_dict={
                                                                                                 X_batch_ph: batchX,
                                                                                                 y_batch_ph: batchY,
                                                                                                 cell_state_ph: _current_cell_state,
                                                                                                 hidden_state_ph: _current_hidden_state
                                                                                             })

                    # Update the current cell states
                    _current_cell_state, _current_hidden_state = _current_state

                    # Keep track of total loss by appending to local list
                    loss_list.append(_total_loss)
                    
                    # Write out tensorboard summary and update the counter
                    tbFileWriter.add_summary(summary, counter)
                    counter += 1;

                    # Log training messages every 2%
                    if batch_idx % (num_batches // 50) == 0:
                        print("Step",batch_idx, "out of", num_batches,  "- Batch loss: ", _total_loss)
                        
                print("Epoch ", epoch_idx, " completed.")
                
                # Define the save path
                savePathDir = CHECKPOINT_PATH + "rnn-epoch-{}/".format(epoch_idx)
                savePath = savePathDir + "lstm-model"
                
                # Make sure firectory is created
                if (not os.path.exists(savePathDir)):
                    os.makedirs(savePathDir)
                
                # Save the epoch as a checkpoint
                saver.save(sess, savePath);
                print("Finished epoch #{0} in {1}".format(datetime.timedelta(seconds=time.time() - startTime)))
                
                
            # Make sure directory exists or create it
            if (not os.path.exists(MODEL_OUTPUT_DIR)):
                os.makedirs(savePathDir)

            # Save the finalized model
            save_path = saver.save(sess, MODEL_OUTPUT_DIR);
            
            print("Saved RNN model to: {}".format(save_path));
            
        # Print elapsed time
        print("Finished traning process in {0}".format(datetime.timedelta(seconds=time.time() - startTime)))
    
#
# Define variable summaries for TensorBoard
#   
def variable_summaries(var):
    """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
    with tf.name_scope('summaries'):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean', mean)
        
        with tf.name_scope('stddev'):
            stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))

        tf.summary.scalar('stddev', stddev)
        tf.summary.scalar('max', tf.reduce_max(var))
        tf.summary.scalar('min', tf.reduce_min(var))
        tf.summary.histogram('histogram', var)
            


# Example RNN training

# Initialize trainer

if __name__ == '__main__':

    # Define the RNN Trainer
    trainer = RNNTrainer(['shooting', 'normal', 'explosion'], 0.5)
    
    # Extract CNN Pool Layer Data
    # trainer.extractPoolLayerData()

    # Launch training process for num of batches
    trainer.train(68137)



