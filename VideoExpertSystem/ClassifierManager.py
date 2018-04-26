from Classifier import CNNClassifier
from Classifier import RNNClassifier
import time, sys 
import multiprocessing

# Handles multiple classifier instances and a shared queue for task queueing
class ClassifierManager():
    
    def __init__(self, model_version, num_classifiers):
        
        MAX_QUEUE_LEN = 30
        
        # Record start time before loading
        start = time.time()
        
        # Define available classifiers queue with their indexes in classifiers array
        self.availableClassifiers = multiprocessing.Queue(num_classifiers)
        # Define classifier array with classifier objects
        self.classifiers = []
        
        # Load the defined number of classifier workers
        for i in range(0, num_classifiers):
            self.classifiers.append([CNNClassifier(model_version), RNNClassifier(model_version)])
            self.availableClassifiers.put(i)
            
        # Log loading time for classifiers
        print("Loaded", num_classifiers, "classifiers in {0:.2f} seconds!".format(time.time()-start))
        
        
    # Get classification with next available classifier and returns result
    #
    def getClassification(self, data, modelType):
        
        # Verify cnn model type and make sure at least one frame is provided
        if (modelType == 'cnn-model-1.0' and len(data) >= 1):
        
            # Get an unused classifier
            classifierID = self.availableClassifiers.get()

            # Get the cnn and lstm classifiers
            cnnClassifier = self.classifiers[classifierID][0]
            
            # Classify the first frame found
            result = cnnClassifier.classify(data[0])
            
            # Make classifier available again
            self.availableClassifiers.put(classifierID)
            
            
        # Verify LSTM model type and that 16 frames are provided
        elif (modelType == 'lstm-model-1.0' and len(data) == 16):
            
            # Get an unused classifier
            classifierID = self.availableClassifiers.get()

            # Get the cnn and lstm classifiers
            cnnClassifier = self.classifiers[classifierID][0]            
            lstmClassifer = self.classifiers[classifierID][1]

            # Define pool data array
            poolData = []

            for frame in data:
                # Process with cnn first
                poolData.append(cnnClassifier.getPoolData(frame))

            # Send image data and get result
            result = lstmClassifer.classify(poolData)

            # Make classifier available again
            self.availableClassifiers.put(classifierID)
            
        else:
            print("Invalid classification request type or frame count!")
            result = "Error"
        
        
        return result
        
    
