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
        
        
     # Load a specific image into the classifier
    def loadImage(self, image_path):
        # read in the image_data
        self.image_data = tf.gfile.FastGFile(image_path, 'rb').read();
        
    
    # Load the CNN model into class variables
    def loadModel(self):

        # Performance metrics
        start = time.time()

        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(self.tf_files_dir + "retrained_labels.txt")]

        # Unpersists graph from file
        with tf.gfile.FastGFile(self.tf_files_dir + "retrained_graph.pb", 'rb') as f:
            self.graph_def = tf.GraphDef()
            self.graph_def.ParseFromString(f.read())
            self._ = tf.import_graph_def(self.graph_def, name='')

            self.sess = tf.Session()        

            # Feed the image_data as input to the graph and get last prediction
            self.cnn_softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0')

            # Log loading time
            print("Loaded Model v" + str(self.modelVersion) + " in %.2f seconds!" % (time.time() - start));
            
            
    # Classifies images using the CNN model
    def classify(self, image_data=None):
        
        # If no image data was supplied
        if (image_data == None):
            # And classifier hasn't loaded image
            if (self.image_data == None):
                print("No image loaded yet!")
                return
            # Load class image data
            image_data = self.image_data;
            
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
            
        
        
# Defines a classifier that uses the RNN LSTM model
#
class RNNClassifier(Classifier):
    
    #  Constructor from Classifier superclass
    def constructor(self):
        
        # Load RNN model
        self.loadModel()
        
            
    # Loads the LSTM RNN model into class variables
    def loadModel(self):
        
        # Define the file dirs and names
        rnnModelDir = self.tf_files_dir + "rnn-model/"
        metaFilePath = rnnModelDir + "rnn-epoch-1.pb.meta"
        
        # Load labels
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(self.tf_files_dir + "retrained_labels.txt")]
        
        # Performance metrics
        start = time.time()
        
        # Start the tensorflow session
        sess = tf.Session()
        
        # Load meta graph
        saver = tf.train.import_meta_graph(metaFilePath)
        saver.restore(sess, tf.train.latest_checkpoint(rnnModelDir))
        
        # Get the default graph
        graph = tf.get_default_graph()
        
        print(graph.get_operations())
        
        # Load graph tensor by name
        self.rnn_softmax_tensor = graph.get_tensor_by_name('predictions_series:0')
        
    
    # Classifies a sequence of frames using the loaded RNN model
    #
    def classify(self, frame_sequences):
        
        
         # Mage sure frame sequences were supplied
        if not (frame_sequence):
            print("No frame sequence supplied!")
            return
        
        # Define input shape [n, 16, 2048]
        batch_size = 8
        backprop_length = 16
        inputSize = 2048
        
        sequences_data = []
        sequences_provided = len(frame_sequences)
        
        # For each element expected in batch
        for i in range(0, batch_size):
            
            # If a sequence is provided for this batch, add it
            if (i < sequencesProvided):
                sequences_data.append(frame_sequences[i])
                
            # If not, append a zeros entry for placeholding
            else:
                sequences_data.append(np.zeros(backprop_length, input_size))
            
            # Append frame sequence to data 
            sequences_data.append(frame_sequence)
            
        # Get x input tensor
        x_input = tf.get_tensor_by_name("X_batch_ph")
            
        # Get predictions from softmax tensor layer
        predictions = self.sess.run(self.rnn_softmax_tensor, {x_input: frame_sequence})

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
        
        
        