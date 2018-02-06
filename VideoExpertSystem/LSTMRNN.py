
import tflearn

# Class representing the LSTMRNN used for training
class LSTMRNN():
    def getNetwork(numClasses, numOfFrames, depth=256, drouput=0.2):
        
        net = tflearn.input_data(shape=[None, numOfFrames, input_size]);
        net = tflearn.lstm(self.net, depth, dropout=dropout, return_seq=True)
        net = tflearn.lstm(self.net, depth, dropout=dropout)
        net = tflearn.fully_connected(self.net, numClasses, activation='softmax')
        net = tflearn.regression(self.net, optimizer='adam', loss='categorical_crossentropy', name="output1")
        
        return net