from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import tensorflow as tf

import json
import time

# Version of model to use [tf_files-vX.X]
MODEL_VERSION = 0.1

class Classifier():
	
    def __init__(self, imagePath):    
        # Performance monitoring
        start = time.time();
    
        # Load image into class variable
        self.loadImage(imagePath);
        
        # Counter for logging purposes
        self.count = 0;
        
        # Use the model version directory
        tf_files_dir = "../Models/tf_files-v%s" % MODEL_VERSION

        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(tf_files_dir + "/retrained_labels.txt")]

        # Unpersists graph from file
        with tf.gfile.FastGFile(tf_files_dir + "/retrained_graph.pb", 'rb') as f:
            self.graph_def = tf.GraphDef()
            self.graph_def.ParseFromString(f.read())
            self._ = tf.import_graph_def(self.graph_def, name='')

            with tf.Session() as self.sess:
        
                # Feed the image_data as input to the graph and get last prediction
                self.softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0')

                # Log loading time
                print("Loaded in %s seconds!" % (time.time() - start));

            
    def loadImage(self, image_path):
        # read in the image_data
        self.image_data = tf.gfile.FastGFile(image_path, 'rb').read();
    
    def classifyCNN(self, image_data=None):
        
        if (image_data == None):
            image_data = self.image_data;
        
        predictions = self.sess.run(self.softmax_tensor, {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        result = {};
        
        for node_id in top_k:
            human_string = self.label_lines[node_id]
            score = predictions[0][node_id]
            result[human_string] = int(score * 100);
            
        return result;
            
            
class ClassifyRequestHandler(BaseHTTPRequestHandler):
                
    # Respond to GET requests
    def do_GET(self):
        if self.path == '/classify':
            # Log request and increase counter
            print('GET Request')
            
            # Get classification
            result = classifier.classifyCNN();
            
            # Log result
            print(result);
            
            # Convert to byte-like type
            resultData = json.dumps(result);
            
            # Send response with result
            self.send_response(200);
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(resultData))
            self.end_headers()
            self.wfile.write(resultData.encode());
