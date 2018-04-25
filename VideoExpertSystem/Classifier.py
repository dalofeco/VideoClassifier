import tensorflow as tf
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

        # Define the cnn model path
        cnnModelPath = self.tf_files_dir + "retrained_graph.pb"
        
        # Performance metrics
        start = time.time()

        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(self.tf_files_dir + "retrained_labels.txt")]
        
        # Reads graph from file
        with tf.gfile.FastGFile(cnnModelPath, 'rb') as f:
            
            # Gets the graph definition
            self.graph_def = tf.GraphDef()
            self.graph_def.ParseFromString(f.read())
            self._ = tf.import_graph_def(self.graph_def, name='')

            self.sess = tf.Session()        

            # Get the softmax and pool tensor for classification or data extraction
            self.cnn_softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0')
            self.pool_tensor = self.sess.graph.get_tensor_by_name('pool_3:0')

            # Log loading time
            print("Loaded Model v" + str(self.modelVersion) + " in %.2f seconds!" % (time.time() - start));
            
            
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
        self.cnnClassifier = CNNClassifier(self.modelVersion)
        
        # Load RNN model
        self.loadModel()
        
            
    # Loads the LSTM RNN model into class variables
    #
    def loadModel(self):
        
        # Performance metrics
        startTime = time.time()
        
        # Define the file dirs and names
        lstmModelPath = self.tf_files_dir + "rnn-checkpoints/"
        metaFilePath = lstmModelPath + "rnn-epoch-0.pb.meta"
        
        # Load labels
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(self.tf_files_dir + "retrained_labels.txt")]
        
        # Performance metrics
        start = time.time()
        
        # Start the tensorflow session
        with tf.Session() as self.sess:

            # Load meta graph
            saver = tf.train.import_meta_graph(metaFilePath)
            saver.restore(self.sess, tf.train.latest_checkpoint(lstmModelPath))

            # Get the default graph
            graph = tf.get_default_graph()

            # Load graph tensor by name
            self.rnn_softmax_tensor = graph.get_tensor_by_name('predictions_series:0')
        
        # Print performance metrics
        print("Loaded LSTM model in {} seconds!".format(time.time() - startTime))
              
        
    # Process frame sequences to cnn representation sequence
    #
    def processFrameSequences(self, frame_sequences):
        
        # Make sure frame sequences were supplied
        if not (frame_sequence):
            print("No frame sequence supplied!")
            return
        
        # Define frame sequences list for sequences
        frame_sequences = []
        
        # For each sequence
        for sequence in frame_sequences:
            
            # Define a sequence list for holding frames
            sequence = []
          
            # Fpr each frame in the sequence
            for frame in sequence:
            
                # Get pool data and append to list
                sequence.append(self.cnnClassifier.getPoolData(frame))
        
    
    # Classifies a sequence of frames using the loaded RNN model
    #
    def classify(self, frame_sequences):
        
         # Make sure frame sequences were supplied
        if not (frame_sequence):
            print("No frame sequence supplied!")
            return
        
        # Define input shape [n, 16, 2048]
        batch_size = 8
        backprop_length = 16
        inputSize = 2048
        sequencesData = []
        
        processedSequences = self.processFrameSequences(frame_sequences)
        sequencesProvided = len(sequences_data)
        
        # For each element expected in batch
        for i in range(0, batch_size):
            
            # If a sequence is provided for this batch, add it
            if (i < sequencesProvided):
                sequencesData.append(processedSequences[i])
                
            # If not, append a zeros entry for placeholding
            else:
                sequencesData.append(np.zeros([backprop_length, input_size]))

            
        # Get x input tensor
        x_input = tf.get_tensor_by_name("X_batch_ph") 
            
        # Get predictions from softmax tensor layer
        predictions = self.sess.run(self.rnn_softmax_tensor, {x_input: sequencesData})
        
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
        
        
        