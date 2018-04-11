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
            self.classifiers.append(RNNClassifier(model_version))
            self.availableClassifiers.put(i)
            
        # Log loading time for classifiers
        print("Loaded", num_classifiers, "classifiers in {0:.2f} seconds!".format(time.time()-start))
        
        
    # Get classification with next available classifier and returns result
    #
    def getClassification(self, data):
        
        # Get an unused classifier
        classifierID = self.availableClassifiers.get()
        classifier = self.classifiers[classifierID]
        
        # Send image data and get result
        result = classifier.classify(data)
        
        # Make classifier available again
        self.availableClassifiers.put(classifierID)
        
        return result
        
    
