// CONSTANTS
const SERVER_PORT = 8080  // Port number for server to listen on
const DEBUG = false  // Debug switch
const CLIENT_VIDEO_CACHE_DIR = "../VideoCache/"


// ******************* MODULE DEFININTIONS ********************** \\
// Express for request handling (web server)
var express = require('express')
var app = express();

// Define the server
var server = require('http').Server(app)

// Socket for video streaming
var io = require('socket.io')(server)
var ss = require('socket.io-stream')

var bodyParser = require('body-parser')

// Path for path management
var path = require('path')

// RESTful client for requesting other servers
var Client = require('node-rest-client').Client;
var client = new Client();

// Experimental (but more accurate) performance metrics
const { performance } = require('perf_hooks');    

// File I/O
var fs = require('fs');

// *********************************************************** //
//------------------  MODULE CONFIGURATIONS  ------------------\\

// Serving static files in express
app.use('/js', express.static('js'))
app.use('/css', express.static('css'))

app.use(bodyParser.urlencoded({
    extended: false
}))

app.use(bodyParser.json());

//-------------------------------------------------------------//

// ******** HTTP GET REQUESTS *********** //

// Server index.html file
app.get('/', function(req, res) {
    fs.readFile('index.html', 'utf-8', function(err, data) {
        if (!err) res.send(data)
        else return console.log(err)
    });    
});


app.get('/classify', function(req, res) {
        
    console.log("GET Request");

    // Mark starting point
    //performance.mark('A');
    
    // To time the process, record current time
    var start = performance.now()
    
    // Get classification data from Python classifier server
    client.get("/classify", function(data, response) {
        
        // Print out the recieved data
        console.log(data);
        
        // Log the elapsed milliseconds
        var duration = performance.now() - start;
        console.log(duration.toString() + ' milliseconds');
        
        // Send back data
        res.send(data);
    });
    
});

name = ''
        
// ********** SOCKET HANDLERS *********** //
// Define handler for new incoming connection
io.of('/stream').on('connection', function(socket) {
    // Print connected message and socket object
    console.log("A streaming user connected");
    
    // Define handler for image stream
    ss(socket).on('video-frame', function(stream, data) {
        console.log("Incoming data:")
        console.log(data)
        name = data.name
        
        // Define classify function when stream ends
        stream.on('end', function() {
            console.log("Recieved: " + data.name)
            classifyImage(data.name + '.jpg', socket)
        });
        
        // Create path name
        var filename = CLIENT_VIDEO_CACHE_DIR + data.name
        // Stream data and write out through file stream 
        stream.pipe(fs.createWriteStream(filename + '.jpg'))
        
        
        
    });
    
    // Define handler for on client disconnect 
    socket.on('disconnect', function() {
        console.log("User disconnected");
    })
    
})


// Function to classify image and send socket response
var classifyImage = function(imageName, socket) {

    // To time the process, record current time
    var start = performance.now()

    var imagePath = CLIENT_VIDEO_CACHE_DIR + imageName

    try {
        // Get classification data from classifier server
        client.get("http://localhost:8081/classify?image=" + imageName, function(data, response) {
            
            // Print out the recieved data
            console.log(data);
            
            // Log the elapsed milliseconds
            var duration = performance.now() - start;
            console.log(duration.toString() + ' milliseconds');
            

            try {
                // Send back data
                socket.emit('results', data);
            } catch (err) {
                console.log(err)
            }
            
            // Delete the image file
            fs.unlink(imagePath, function(err) {
                if (err)
                    console.log(err)
            })
        });

    } catch (err) {
        console.log(err);
    }
}


// Start server listening on defined port, and print message when started
server.listen(SERVER_PORT, function() {
    console.log("Listening on " + SERVER_PORT.toString())
})
