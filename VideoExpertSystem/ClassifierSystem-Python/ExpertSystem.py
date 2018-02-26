from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import socketserver, threading
import json, base64
import sys, time
import multiprocessing

from Classifier import Classifier

# Handles multiple classifier instances and a shared queue for task queueing
class ClassifierManager():
    
    def __init__(self, model_version):
        
        MAX_QUEUE_LEN = 30
        NUM_CLASSIFIERS = 3
        
        # Record start time before loading
        start = time.time()
        
        # Define available classifiers queue with their indexes in classifiers array
        self.availableClassifiers = multiprocessing.Queue(NUM_CLASSIFIERS)
        # Define classifier array with classifier objects
        self.classifiers = []
        
        # Load the defined number of classifier workers
        for i in range(0, NUM_CLASSIFIERS):
            self.classifiers.append(Classifier(model_version))
            self.availableClassifiers.put(i)
            
        # Log loading time for classifiers
        print("Loaded", NUM_CLASSIFIERS, "classifiers in {0:.2f} seconds!".format(time.time()-start))
        
        
    # Get classification with next available classifier and returns result
    def getClassification(self, image_data):
        # Get an unused classifier
        classifierID = self.availableClassifiers.get()
        classifier = self.classifiers[classifierID]
        
        # Send image data and get result
        result = classifier.classifyCNN(image_data)
        
        # Make classifier available again
        self.availableClassifiers.put(classifierID)
        
        return result

        
#    # Adds image and handler to task queue
#    def addTask(self, classifierHandler, imageData):
#        
#        # Make sure queue is not full
#        if (self.taskQueue.full()):
#            print("Classification queue is full!")
#            return None
#        
#        # Add to shared queue and let workers handle it
#        self.taskQueue.put((classifierHandler, imageData))
#                    
#        
#    # Starts a worker for each classifier
#    def startWorkers(self):
#        
#        connections = []
#        
#        # For each classifier
#        for i in range(0, NUM_CLASSIFIERS):
#            
#            # Define pipe for process output of time elapsed
#            #parent_conn, child_conn = Pipe()
#            #connections.append(parrent_conn)
#            
#            # Define the process and start it
#            p = Process(target=self.worker, args=(self.classifiers[i]))
#            p.start()
#            
#            # FROM PYTHON 3.5 MULTIPROCESSING DOCUMENTATION
#            # We close the writable end of the pipe now to be sure that
#            # p is the only process which owns a handle for it.  This
#            # ensures that when p closes its handle for the writable end,
#            # wait() will promptly report the readable end as being ready.
#            #child_conn.close()
#            
#        print("Started", NUM_CLASSIFIERS, "workers.")
#        
#        # Print all message connections
##        while connections:
##            for r in multiprocessing.connection.wait(connections):
##                try:
##                    msg = r.recv()
##                except EOFError:
##                    connections.remove(r)
##                except KeyboardInterrupt:
##                    print("Exiting....")
##                    sys.exit()
##                else:
##                    print(msg)
#        
#        
#    # Worker routine for each classifier
#    def worker(self, classifier):
#        try:
#            while True:
#                # Get next task
#                handler, imageData = self.imageQueue.get()
#                
#                # Start time for logging purposes 
#                startTime = time.time()
#                
#                # Classify and get result
#                result = classifier.classifyCNN(imageData)
#                    
#                # Define response format
#                response = {
#                    "result": result
#                }
#                
#                # Send JSON response via handler
#                handler.respondJSON(response)
#                
#                # Print response time
#                # conn.send("Response sent in {:.2f} seconds".format(time.time()-handler.startTime))
#                
#                
#        except KeyboardInterrupt:
#            print("Keyboard Exit")
#            sys.exit()



# Multithreaded implementation of classifier server
class ClassifierHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
                
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
            self.startTime = time.time()
            
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
                    print("Responded classifyInit in {} seconds".format(time.time() - self.startTime))
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
            
            # Log time elapsed and return
            print("Responded classification in {} seconds".format(time.time() - self.startTime))
            return
    
        # Placeholder for generating ID
        def generateID(self):
            return "0012"

classifierManager = ClassifierManager(0.3)
        
#### MAIN ####
if __name__ == '__main__':

    # Define the port numbers
    HOST, HTTP_PORT, SOCKET_PORT = "", 8080, 8081
    
    # Make sure exactly one argument is supplied
    if (len(sys.argv) == 2):
        
        # Server http server on defined address and port, with specified request handler
        httpServer = ClassifierHTTPServer((HOST, HTTP_PORT), ClassifierHTTPServer.ClassifierHTTPHandler);
        #classifier = Classifier(sys.argv[1])
        
        # Little wrapper function to catch keyboard interrupts
        def serveHTTP():
            try:
                httpServer.serve_forever()
            except (KeyboardInterrupt, SystemExit):
                print("Exiting...")
                sys.exit()

        # Log message and start listening on a thread
        print("Starting HTTP server listening on port", HTTP_PORT)
        #threading.Thread(target=serveHTTP).start();
        serveHTTP()
    else:
        # Print usage info
        print("Usage: python3 TensorServer.py (model_number)");
        sys.exit()
    
    