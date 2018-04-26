import base64, json
import time, sys
import tornado
from tornado import websocket

from ClassifierManager import ClassifierManager

# Define a web socket server to handle live video stream from client
class ClassifierServer():
    
    # Constructor function starting server
    def __init__(self, PORT=8080):
        
        # Save port number
        self.PORT = PORT
        
        # Initiate application mapping urls to handlers
        self.application = tornado.web.Application([
            (r'/ws', ClassifierServer.ClassifierWebSocketHandler),
            (r'/classify', ClassifierServer.ClassifierGETHandler),
            (r'/favicon.ico', ClassifierServer.ClassifierGETHandler),
            (r'/', ClassifierServer.ClassifierGETHandler),
            (r'/js/(.*)', tornado.web.StaticFileHandler, {"path": "./js"},),
            (r'/css/(.*)', tornado.web.StaticFileHandler, {"path": "./css"},),
            (r'/dist/(.*)', tornado.web.StaticFileHandler, {"path": "./dist"},),
            (r'/lib/(.*)', tornado.web.StaticFileHandler, {"path": "./lib"},),
            (r'/vendor/(.*)', tornado.web.StaticFileHandler, {"path": "./vendor"},),
        ])
        
        # Initiate tornado http server w/application
        self.http_server = tornado.httpserver.HTTPServer(self.application)

        # Create classifier manager for classifiers 
        # self.classifierManager = ClassifierManager(0.3, 3)
        
        # Start the server
        self.start();
        
    # Function to start server listening
    def start(self):

        # Log listening message
        print("Starting server listening on port", self.PORT)

        # Listen on specified port
        self.http_server.listen(self.PORT)

        # Start the tornado async io loop
        tornado.ioloop.IOLoop.current().start()
        
    def check_origin(self, origin):
        print("Origin:", origin.toString())
        return True
        
    # Handle requests for specific files
    class ClassifierGETHandler(tornado.web.RequestHandler):
        def get(self):
            if self.request.uri == "/":
                self.render('html/index.html')
            elif self.request.uri == "/classify":
                self.render('html/classify.html')                    
            elif self.request.uri == "/favicon.ico":
                with open('resources/favicon.ico', 'rb') as iconFile:
                    self.write(iconFile.read())
            else:
                print("Unrecognized GET:", self.request.uri)
                self.write("404")
                
        
    # Handler for web socket events
    class ClassifierWebSocketHandler(websocket.WebSocketHandler):

        # On open handler
        def open(self):
            print("Opened websocket")

        # On close listener
        def on_close(self):
            print("Closed websocket")

        # Message listener
        def on_message(self, message):
            
            # Save start time
            startTime = time.time()
            
            # Load json encoded message
            b64images = json.loads(message)
            
            # To store decoded images
            images = []
            
            # Iterate through b64 images and decode
            for image in b64images:
                images.append(base64.b64decode(image))
            
            # Get classifier result
            result = classifierManager.getClassification(images)

            # Send response and log time elapsed
            self.write_message(result)
            print("Sent classification in {:.2f} seconds!".format(time.time() - startTime))
            
# MAIN function
if __name__ == "__main__":
    
    # Define the port number
    HTTP_PORT = 8080
    
    # Make sure exactly one argument is supplied
    if (len(sys.argv) == 2):

        classifierManager = ClassifierManager(sys.argv[1], 1)
        socketServer = ClassifierServer(HTTP_PORT)
        socketServer.start()
        
    else:
        # Print usage info
        print("Usage: python3 TornadoServer.py (model_number)");
        sys.exit()
