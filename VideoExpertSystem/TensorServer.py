from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from Classifier import Classifier
from Classifier import ClassifyRequestHandler
            
# Main
if __name__ == '__main__':

    # Classifier class 
    classifier = Classifier("../tests/fire.jpg");

    httpd = HTTPServer(("127.0.0.1", 8081), ClassifyRequestHandler);
    httpd.serve_forever();
    