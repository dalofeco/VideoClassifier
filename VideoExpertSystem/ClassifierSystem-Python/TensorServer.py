from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from Classifier import Classifier

import sys, json
from urllib.parse import urlparse

VIDEO_CACHE_DIR = "../VideoCache/"

class ClassifyRequestHandler(BaseHTTPRequestHandler):
                
    # Respond to GET requests
    def do_GET(self):
        print("GOT request: " + self.path)
        
        # If path is null for some reason, exi
        if (not self.path):
            print("Path is null...")
            sys.exit()
        
        # If GET request is for classification, call function
        if (self.path[0:9] == "/classify"):
            self.handleClassifyRequest()
        else:

            print("Unrecognized GET request")
    
    # Function for handling classification request
    def handleClassifyRequest(self):
        
        # Get the query and parse its components
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        
        # Get the image path query
        imagePath = query_components["image"]
        imagePath = imagePath.replace("%20", " ")

        # Logging 
        print("Handle request for image: " + imagePath)


        # Make sure the path was specified as a query
        if (imagePath):
            
            # Load the specified image in the classifier
            classifier.loadImage(VIDEO_CACHE_DIR + imagePath)

            # Get classification
            result = classifier.classifyCNN()

            # Log result
            print(result)

            # Calculate top category
            topCategory = ""
            highestVal = 0

            # Iterate through results, save highest score with its category
            for key in result:
                if (highestVal < int(result[key])):
                    highestVal = int(result[key])
                    topCategory = key
            

            # Organize result data
            resultData = {topCategory: highestVal}

            # Convert to byte-like type for sending
            resultData = json.dumps(resultData);

            # Send response with result
            self.send_response(200);
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(resultData))
            self.end_headers()
            self.wfile.write(resultData.encode())

# Main
if __name__ == '__main__':

    PORT_NUMBER = 8081
    
    # Make sure exactly one argument is supplied
    if (len(sys.argv) == 2):

        # Classifier class 
        classifier = Classifier(sys.argv[1]);

        print("Started server listening on port ", PORT_NUMBER);

        # Server http server on defined address and port, with specified request handler
        httpd = HTTPServer(("127.0.0.1", PORT_NUMBER), ClassifyRequestHandler);
        httpd.serve_forever();

        
    else:
        # Print usage info
        print("Usage: python3 TensorServer.py (model_number)");
    
    