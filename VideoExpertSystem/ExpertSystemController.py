from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import socketserver, multiprocessing
import json, base64
import sys, time

from Classifier import Classifier
from ClassifierManager import ClassifierManager

from tornado import websocket

# Multithreaded implementation of classifier server
class ExpertSystemController(socketserver.ThreadingMixIn, HTTPServer):
                
    # Handler class for incoming HTTP requests
    class ClassifierHTTPHandler(BaseHTTPRequestHandler):
        
        # RECOGNIZED FILE TYPES FOR SENDING CONSTANTS
        NO_TYPE = -1
        HTML_TYPE = 0
        CSS_TYPE = 1
        JS_TYPE = 2
        JPG_TYPE = 3
        PNG_TYPE = 4
        
        ##########  GET REQUEST HANDLER #########
        # Serve web files for GET requests
        def do_GET(self):

            # If path is null for some reason, exit
            if (not self.path):
                print("Path is null...")
                sys.exit()
                
            # If GET request for favicon.ico
            if (self.path[0:12] == "/favicon.ico"):
                self.sendFile("resources/favicon.ico", self.PNG_TYPE)                    

            # If GET request is for classification, call function
            if (self.path[0:9] == "/classify"):
                self.sendFile("html/classify.html", self.HTML_TYPE)

            # Serve js and css directories
            elif (self.path[0:4] == "/js/"):
                self.sendFile("js/" + self.path[4:], self.JS_TYPE)

            elif (self.path[0:5] == "/css/"):
                self.sendFile("css/" + self.path[5:], self.CSS_TYPE)

            else:
                print("Unrecognized GET request:", self.path)
            

        ## FUNCTIONS FOR SENDING RESPONSES OF DIFFERENT TYPES ##

        # Send file specifying path and type constant of file type
        def sendFile(self, filePath, fileType):
            
            content_type = ""
            if (fileType == self.HTML_TYPE):
                content_type = "text/html"
            elif (fileType == self.CSS_TYPE):
                content_type = "text/css"
            elif (fileType == self.JS_TYPE):
                content_type = "text/js"
            elif (fileType == self.PNG_TYPE):
                content_type = "image/png"
            elif (fileType == self.JPG_TYPE):
                content_type = "image/jpeg"
            else:
                print("Unrecognized file format")
                self.send_error(404)
                return
            
            # Try to fetch that file
            try:
                with open(filePath, 'rb') as file:
                    fileData = file.read()
                    
                    self.send_response(200);
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", len(fileData))
                    self.end_headers()
                    self.wfile.write(fileData)

            except FileNotFoundError:
                self.send_error(404)
                return
            
        ####### POST REQUEST HANDLER #######
        # Respond to POST requests
        def do_POST(self):
            
            # Start time for logging purposes
            startTime = time.time()
            
            # If path is null for some reason, exit
            if (not self.path):
                print("Path is null...")
                sys.exit()
            
            # Get content type
            content_type = self.headers["Content-Type"]
            content_length = self.headers["Content-Length"]
            
            # If content type or length unspecified, return
            if not content_type or not content_length:
                print("No content type specified")
                return
            
            # Parse content length to integer
            content_length = int(content_length)

            # Make sure JSON data specified
            if content_type == "application/json":
                        
                # If POST with classifiyInit request
                if (self.path[0:13] == "/classifyInit"):

                    # Generate ID and send as JSON
                    data = { 'cid': self.generateID() }
                    self.respondJSON(data)
                    
                    # Log time elapsed and return
                    print("Responded classifyInit in {} seconds".format(time.time() - startTime))
                    return

            # If image being sent
            elif content_type == "image/jpeg":
                
                # If POST with classify request 
                if (self.path[0:9] == "/classify"):
                    imageData = self.rfile.read(content_length)

                    # Let classifier manager handle classifiers and pass self parameter to send response
                    response = classifierManager.getClassification(base64.b64decode(imageData.decode('utf-8')))
                    
                    # Organize result and send as JSON
                    data = { 'result': response }                
                    self.respondJSON(data)
                    
                    # Log time elapsed and return
                    print("Responded classify in {} seconds".format(time.time() - startTime))
                    return
            
        
        # Responds request with JSON
        def respondJSON(self, data):
            # Dump to JSON string
            jsonData = json.dumps(data)
            
            # Set response headers
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(jsonData))
            self.end_headers()
            
            # Write json data into request
            self.wfile.write(jsonData.encode())
            return
    
        # Placeholder for generating ID
        def generateID(self):
            return "0012"                

        
#### MAIN ####


if __name__ == '__main__':

    # Define the port numbers
    HOST, HTTP_PORT = "", 8080
    
    # Make sure exactly one argument is supplied
    if (len(sys.argv) == 2):
        
        # Expert system controller listening on defined address and port, with specified request handler
        expertSystemController = ExpertSystemController((HOST, HTTP_PORT), ExpertSystemController.ClassifierHTTPHandler);
        
        # Classifier manager for server to classifier communication
        classifierManager = ClassifierManager(0.3)
        accountManager = AccountManager()
        
        # Log message and start listening
        print("Starting HTTP server listening on port", HTTP_PORT)
        expertSystemController.serve_forever()
    else:
        # Print usage info
        print("Usage: python3 TensorServer.py (model_number)");
        sys.exit()
