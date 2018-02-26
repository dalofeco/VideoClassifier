from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import socketserver, threading
import sys, json
import time

import base64
from Classifier import Classifier

classifier = Classifier(0.3)

class ClassifierHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
            
    class ClassifierHTTPHandler(BaseHTTPRequestHandler):

        # Respond to POST requests
        def do_POST(self):
            
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
                    
                    print("Responded classifyInit in {} seconds".format(time.time() - startTime))
                    return

            # If image being sent
            elif content_type == "image/jpeg":
                
                # If POST with classify request 
                if (self.path[0:9] == "/classify"):
                    imageData = self.rfile.read(content_length)
                    
                    # Load expected values
                    # cid = jsonData['cid']
                    # data = jsonData['data']

                    # Get classifier response
                    response = classifier.classifyCNN(base64.b64decode(imageData.decode('utf-8')))

                    # Organize result and send as JSON
                    data = { 'result': response }                
                    self.respondJSON(data)
                    print("Responded classification in {} seconds".format(time.time() - startTime))
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
        
        
        # Respond to GET requests
        def do_GET(self):

            # If path is null for some reason, exit
            if (not self.path):
                print("Path is null...")
                sys.exit()

            # If GET request is for classification, call function
            if (self.path[0:9] == "/classify"):

                # Open html and send
                with open("html/classify.html") as classifyHTMLFile:
                    classifyHTMLData = classifyHTMLFile.read()

                    # Send response with result
                    self.send_response(200);
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", len(classifyHTMLData))
                    self.end_headers()
                    self.wfile.write(classifyHTMLData.encode())
                    return

            # Serve js and css directories
            elif (self.path[0:4] == "/js/"):
                self.sendFile("js/" + self.path[4:])

            elif (self.path[0:5] == "/css/"):
                self.sendFile("css/" + self.path[5:])

            else:
                print("Unrecognized GET request:", self.path)

        def sendFile(self, filePath):
            
            
            content_type = "text/"
            if filePath[-3:] == "css":
                content_type += "css"
            elif filePath[-2:] == "js":
                content_type += "js"
            else:
                print("Unrecognized file format")
                self.send_error(404)
                return
            
            # Try to fetch that file
            try:
                with open(filePath) as file:
                    fileData = file.read()
                    self.send_response(200);
                    self.send_header("Content-Type", "text/javascript")
                    self.send_header("Content-Length", len(fileData))
                    self.end_headers()
                    self.wfile.write(fileData.encode())

            except FileNotFoundError:
                self.send_error(404)
                return

# Main
if __name__ == '__main__':

    # Define the port numbers
    HOST, HTTP_PORT, SOCKET_PORT = "", 8080, 8081
    
    # Make sure exactly one argument is supplied
    if (len(sys.argv) == 2):
        
        try:    
#            # Create a socket classifier server instance
#            socketServer = ClassifierSocketServer(HOST, SOCKET_PORT, sys.argv[1])
#            print("Starting socket server listening on port", SOCKET_PORT);
#            threading.Thread(target=socketServer.listen).start()
            
            # Server http server on defined address and port, with specified request handler
            httpServer = ClassifierHTTPServer((HOST, HTTP_PORT), ClassifierHTTPServer.ClassifierHTTPHandler);
            #classifier = Classifier(sys.argv[1])
            print("Starting HTTP server listening on port", HTTP_PORT)
            threading.Thread(target=httpServer.serve_forever).start();
            threading.Thread(target=quit).start()
        
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            sys.exit()
        
    else:
        # Print usage info
        print("Usage: python3 TensorServer.py (model_number)");
        sys.exit()
    
    