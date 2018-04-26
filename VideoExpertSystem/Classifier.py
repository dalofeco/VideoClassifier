import tensorflow as tf
import numpy as np
import time


# Base class for classifiers using different models
#
class Classifier():
	
    def __init__(self, modelVersion):
        
        # Version of model to use [tf_files-vX.X]
        self.modelVersion = modelVersion
        
        # Initialize image data to None
        self.image_data = None
        
        # Counter for logging purposes
        self.count = 0
        
        # Use the model version directory
        self.tf_files_dir = "../Models/tf_files-v{}/".format(self.modelVersion)
        
        # Overrideable constructor
        self.constructor()
    
    # Placeholder constructor function, override this instead of __init__()
    def constructor(self):
        pass
    

    
# Defines a classifier that uses a CNN as a model
#
class CNNClassifier(Classifier):    

    # Constructor from Classifier superclass
    def constructor(self):
        
        # Load CNN model
        self.loadModel()
        
    
    # Load the CNN model into class variables
    def loadModel(self):
        
        # Performance metrics
        start = time.time()
        
        # Reset default graphs
        tf.reset_default_graph()

        # Define the cnn model path
        cnnModelPath = self.tf_files_dir + "retrained_graph.pb"
        
        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(self.tf_files_dir + "retrained_labels.txt")]
        
        # Reads graph from file
        with tf.gfile.FastGFile(cnnModelPath, 'rb') as f:
            
            
            # Gets the graph definition
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            self._ = tf.import_graph_def(graph_def, name='')
            
            # Define the tensorflow session
            self.sess = tf.Session()

            # Get the softmax and pool tensor for classification or data extraction
            self.cnn_softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0')
            self.pool_tensor = self.sess.graph.get_tensor_by_name('pool_3:0')

            # Log loading time
            print("Loaded CNN Model v" + str(self.modelVersion) + " in %.2f seconds!" % (time.time() - start));
            
            
    # Classifies images using the CNN model
    def classify(self, image_data):
        
        # If no image data was supplied
        if (image_data == None):
            return -1;
            
        # Get predictions from softmax tensor layer
        predictions = self.sess.run(self.cnn_softmax_tensor, {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        result = {};
        
        for node_id in top_k:
            human_string = self.label_lines[node_id]
            score = predictions[0][node_id]
            result[human_string] = int(score * 100);
            
        return result;
    
    # Gets the pool data from CNN model
    def getPoolData(self, image_data):
        
        # If no image data was supplied
        if (image_data == None):
            return -1;
        
        # Get predictions from softmax tensor layer
        pool_representation = self.sess.run(self.pool_tensor, {'DecodeJpeg/contents:0': image_data})
            
        return pool_representation;
            
            
        
        
# Defines a classifier that uses the RNN LSTM model
#
class RNNClassifier(Classifier):
    
    #  Constructor from Classifier superclass
    def constructor(self):
        
        # Get a cnn classifier for CNN representation of image_data
        # self.cnnClassifier = CNNClassifier(self.modelVersion)
        
        # Load RNN model
        self.loadModel()
        
            
    # Loads the LSTM RNN model into class variables
    #
    def loadModel(self):
        
        # Performance metrics
        startTime = time.time()
        
        # Reset default graphs
        tf.reset_default_graph()
        
        # Define the file dirs and names
        lstmModelPath = self.tf_files_dir + "rnn-model/"
        metaFilePath = lstmModelPath + "lstm-model.meta"
        
        # Load labels
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(self.tf_files_dir + "retrained_labels.txt")]
        
        # Performance metrics
        start = time.time()

        
        # Start the tensorflow session
        self.sess = tf.Session()
        
        # Load meta graph
        saver = tf.train.import_meta_graph(metaFilePath)
        
        # Restore vars from checkpoint
        saver.restore(self.sess, tf.train.latest_checkpoint(lstmModelPath))
        
        # Load graph tensor by name
        self.rnn_softmax_tensor = self.sess.graph.get_tensor_by_name('predictions_series/Softmax:0')
        
        # Print performance metrics
        print("Loaded LSTM model in {:.2f} seconds!".format(time.time() - startTime))
              
        
    # Process frame sequence to cnn representation sequence
    #
    def processFrameSequence(self, frame_sequence):
        
        # Make sure frame sequence was supplied
        if (frame_sequence is None):
            print("No frame sequence supplied!")
            return
        
        # Define a sequence list for holding frames data
        sequence_data = []
          
        # Fpr each frame in the sequence
        for frame in frame_sequence:

            # Get pool data and append to list
            sequence_data.append(self.cnnClassifier.getPoolData(frame))
        
        return sequence_data
        
    
    # Classifies a sequence of frames using the loaded RNN model
    #
    def classify(self, frame_sequence):
        
         # Make sure frame sequence was supplied
        if not (frame_sequence):
            print("No frame sequence supplied!")
            return
        
        # Define input shape [n, 16, 2048]
        batchSize = 8
        backpropLength = 16
        inputSize = 2048
        
        frame_sequence = np.array(frame_sequence)
        frame_sequence = np.reshape(frame_sequence, [1, 16, 2048])
        print(frame_sequence.shape)
        
        # processedSequence = self.processFrameSequence(frame_sequence)
        
        # Get x input tensor
        x_input = self.sess.graph.get_tensor_by_name("x_batch_ph/Placeholder:0") 
        
        # Define cell and hidden state to zeroes
        _current_cell_state = np.zeros((1, 2048))
        _current_hidden_state = np.zeros((1, 2048))
            
        # Get predictions from softmax tensor layer
        predictions = self.sess.run(self.rnn_softmax_tensor, {
            "x_batch_ph/Placeholder:0": frame_sequence,
            "Placeholder:0": _current_cell_state,
            "Placeholder_1:0": _current_hidden_state,
        })
        
        print(predictions)

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        
        print(top_k)

        result = {};
        
        for node_id in top_k:
            human_string = self.label_lines[node_id]
            score = predictions[0][node_id]
            result[human_string] = int(score * 100);
            
        return result;
   
    
    
    
            
            

# classifier = Classifier(0.3)

# print("Starting loadImage")
# classifier.loadImage("../../nc_bus_160719.jpg")
# print("Finished loadImage")
# print("Starting classifyCNN")
# results = classifier.classify()
# print("Finished classifyCNN")


# print(results)
        
        
        