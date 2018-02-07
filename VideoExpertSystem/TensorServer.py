from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from Classifier import Classifier

import json
         
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
            self.wfile.write(resultData.encode())

# Main
if __name__ == '__main__':
    
    # Make sure exactly one argument is supplied
    if (len(sys.argv) == 2):

        # Classifier class 
        classifier = Classifier(sys.argv[1]);
        classifier.loadImage("../tests/fire.jpg");

        httpd = HTTPServer(("127.0.0.1", 8081), ClassifyRequestHandler);
        httpd.serve_forever();
        
    else:
        # Print usage info
        print("Usage: python3 TensorServer.py (model_number)");
    
    