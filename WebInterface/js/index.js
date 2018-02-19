var videoFileName = '';
var duration = 0;
const interval = 1;
var count = 0;


// -----------------  SOCKET -------------------
    
function sendSocketData(socket, data, label, name) {
    var stream = ss.createStream()
    ss(socket).emit(label, stream, {size: data.size, name: name})
    var blobStream = ss.createBlobReadStream(data)
    var size = 0
    
    // Print blob streaming progress on console
    blobStream.on('data', function(chunk) {
        size += chunk.length
        console.log(Math.floor(size / data.size * 100) + '%');
    });
    
    // Finally pipe data through socket
    blobStream.pipe(stream)
}


// ---------------- FILE PICKER ----------------

// Function for when file picker selection changes
function selectFile(e) {
    // Get file name
    videoFileName = event.target.files[0].name
    
    // Convert into URL
    var fileURL = URL.createObjectURL(event.target.files[0])
    
    // Get video player and set URL
    videoPlayer = $("#videoPlayer")
    videoPlayer.attr("src", fileURL)
    
    // Set count to 
    count = 0
}

// Define handlers
// $('#videoFilePicker').change(selectFile)

// -----------------------------------------------

// --------------- VIDEO PLAYER ------------------


function getFrame(callback) {
    // Get video player element
    var videoPlayer = document.getElementById('videoPlayer')
    var timeStamp = videoPlayer.currentTime;

    // Create a new canvas object and set height and width equal to video
    var canvas = document.createElement('canvas')
    canvas.height = videoPlayer.videoHeight
    canvas.width = videoPlayer.videoWidth

    // Get context, and draw image of video player on it
    var context = canvas.getContext('2d')
    context.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);
    var image = new Image()
    image.src = canvas.toDataURL()

    // Convert to blob, and call callback function with it
    canvas.toBlob(function(blob) {callback({'blob': blob, 'time': timeStamp})}, 'image/jpeg')

}


// ------------ VIDEO FRAME CLASSIFICATION --------------

// Initiates the analysis process from the start
function startAnalysis() {

    // Initialize socket connection
    socket = io.connect('/stream')
    
    // Make sure video is not paused
    if (document.getElementById('videoPlayer').paused)
        $("#videoPlayer").trigger("play");

    // Define handler for video updates
    $('#videoPlayer').on('timeupdate', function(e) {
        // Only do every X amount of refreshes based on interval
        if (count % interval == 0) {
            classifyFrame(socket)
        }
        count++;
    });
    
    // Define handler for results
    socket.on('results', function(results) {
        stringRepr = ''
        for (var key in results) 
            stringRepr += key + ": " + results[key].toString()
        $('#results').text(stringRepr)
    });
}

// Function to classify the frame currently played on videoPlayer
function classifyFrame(socket) {
    
    // Get current on screen frame and its data
    getFrame(function(frameData) {
        imageBlob = frameData['blob']
        timeStamp = frameData['time']
        
        // Round to nearest integer, multiplying by 100 to consider hundreths
        roundedTimeStamp = Math.round(timeStamp * 100);

        // Send image blob through socket
        sendSocketData(socket, imageBlob, 'video-frame', videoFileName.toString() + "-" + roundedTimeStamp)    

    });
}

// ------------ DOCUMENT READY SCRIPT --------------

// On document load
$(document).ready(function() {
    
    // Define file picker handlers
    $('#videoFilePicker').change(selectFile)
    
    // Define video player handler
    $('#videoPlayer').on('loadedmetadata', function() {
        if ('function' === typeof duration) {
            duration = duration(this.duration)
        }
        this.currentTime = Math.min(Math.max(0, (duration < 0 ? this.duration : 0) + duration), this.duration)
        
    });
    
    // Define classify button handler to start active analysis
    $("#classifyButton").click(startAnalysis);
});
