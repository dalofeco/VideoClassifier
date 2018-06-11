# NeuralNetworks.py by Dalofeco
# Jun 10, 2018
# 
# NeuralNetworks.py contains class declarations for a CNN
# and an LSTM RNN, which define the networks and relevant
# functions encapsulated in their class.


class CNN():
    
    def __init__(self, tf_files_dir):
        
        # Save tf_files model directory
        self.tf_files_dir = tf_files_dir;
        
        
    # Load CNN model into new local TensorFlow session
    #
    def loadModel(self):
        
        # Performance monitoring
        loadStart = time.time();
        
        # Reads graph from file
        f = tf.gfile.FastGFile(self.tf_files_dir + "retrained_graph.pb", 'rb')

        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

        # Start a tensorflow session
        self.sess = tf.Session()

        # Get pool tensor layer by name from the session graph
        self.pool_tensor = self.sess.graph.get_tensor_by_name('pool_3:0')
        
        # Log performance metrics
        print("Loaded tensor in %.2f seconds" % (time.time() - loadStart));
    
    
    # Extract the pool layer data for specified image
    #
    # PARAMETERS:
    #   image_path: <string> - path for image to be analyzed
    #
    # RETURNS:
    #   frame_features: <vector> - image features vector from pool layer
    #
    def extractPoolLayerData(self, image_data):
        
        # Extract pool tensor representation from image_data
        frame_features = sess.run(pool_tensor, {'DecodeJpeg/contents:0': image_data})
            
        # Return features
        return frame_features
                
        
    # Get the classification for specified image 
    def getClassification(self, image_data):
                
        


class LSTM():
    
    
    # Constructor for LSTM defines the networks parameters 
    def __init__(self, labels):
        
        # Save the labels to be considered
        self.labels = labels;
        
        # Save the number of classes to classify
        self.num_classes = len(labels)
        
        # Define state size
        self.state_size = 2048 # Define state size
        
        # Define the frame batch size
        self.batch_size = 8 
        
        # Define the input vector length (2048-d image vector for image features before pooling layer from image classifier CNN)
        self.input_length = 2048 