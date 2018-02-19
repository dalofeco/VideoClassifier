
var videoFileName = '';
const INTERVAL = 3;
var frameCount = 0;
var ws = null

var STREAMING = false
        
// ------------ DOCUMENT READY SCRIPT --------------

// On document load
$(document).ready(function() {

    window.onbeforeunload = function() {
        if (ws != null) {
            ws.onclose = function() {}; // disable on close handler
            ws.close() // close web socket
            ws = null
        }
    }
    
    // Define file picker handlers
    $('#videoFilePicker').change(selectFile)
    
    // Define video player handler
    $('#videoPlayer').on('loadedmetadata', function() {
        if ('function' === typeof duration) {
            duration = duration(this.duration)
            this.currentTime = Math.min(Math.max(0, (duration < 0 ? this.duration : 0) + duration), this.duration)
        }
    });
    
    // Define classify button handler to start active analysis
    $("#classifyButton").click(toggleStreaming);
});

function toggleStreaming() {
    if (STREAMING) {
        STREAMING = false
        stopVideoAnalysis()
    } else {
        STREAMING = true
        startVideoAnalysis()
    }
    return STREAMING
}

// ---------------- WEB SOCKET -----------------

function initWebSocket(onopenCallback) {
    // Initialize web socket
    ws = new WebSocket("ws://" + document.location.host + "/ws/bind")

    // When message recieved, send FRAME response
    ws.onmessage = function(event) {
        // Get data and display
        msg = event.data
        data = JSON.parse(msg)
        $("#results").text(data['data'])
    }
    
    // Define function for when socket closes
    ws.onclose = function(e) {
        console.log("Socket Closed...")
        console.log(e)
    };

    // Define handler for open event
    ws.onopen = onopenCallback

}

// function handleWebSocketMessage(messageEvent) {
//     console.log(messageEvent.data)
// }

// ---------------------------------------------

// ------------ VIDEO FRAME CLASSIFICATION --------------

// Initiates the video analysis process from the start
function startVideoAnalysis() {

    // Define callback for when socket is initialized
    onopenCallback = function(event) {
        // Make sure video is not paused
        if (document.getElementById('videoPlayer').paused) 
            $("#videoPlayer").trigger("play")

        // Define handler for video updates
        $('#videoPlayer').on('timeupdate', function(e) {
            // Only do every X amount of refreshes based on interval
            if (frameCount % INTERVAL == 0) {
                console.log("Sending frame " + frameCount.toString())
                sendFrameForClassification()
            }
            frameCount++;
        });
    }

    // Initialize web socket connection with callback
    initWebSocket(onopenCallback)    
}

function stopVideoAnalysis() {
    // Remove the video player timeupdate handler
    $('#videoPlayer').on('timeupdate', function(){})

    // Pause video if not already paused
    if (!document.getElementById('videoPlayer').paused)
        $("#videoPlayer").trigger("pause");


    // Close web socket connection
    ws.close()
    ws = null
}

// Function to classify the frame currently played on videoPlayer
function sendFrameForClassification() {
    
    // Get current on screen frame and its data
    getFrame(function(frameData) {
        imageBlob = frameData['blob']
        timeStamp = frameData['time']

        const reader = new FileReader()
        reader.readAsText(imageBlob)

        // This fires after the blob has been read/loaded.
        reader.addEventListener('loadend', (e) => {

            // Make sure socket connection still active
            if (ws != null) {
                const imageBlobText = e.srcElement.result;

                // Round to nearest integer, multiplying by 100 to consider hundreths
                roundedTimeStamp = Math.round(timeStamp * 100);

                // Send image data via socket
                ws.send(imageBlob)
            }
        });

    });
}

// --------------- VIDEO PLAYER ------------------

function getFrame(callback) {
    // Get video player element
    var videoPlayer = document.getElementById('videoPlayer')
    var timeStamp = videoPlayer.currentTime;

    // Create a new canvas object and set height and width equal to video
    var canvas = document.createElement('canvas')
    canvas.height = videoPlayer.videoHeight
    canvas.width = videoPlayer.videoWidth


    var context = canvas.getContext('2d')
    context.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);
    var image = new Image()
    image.src = canvas.toDataURL()
    canvas.toBlob(function(blob) {
        callback({'blob': blob, 'time': timeStamp})
    }, 'image/jpeg', 1)

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
    frameCount = 0
}

// Define handlers
// $('#videoFilePicker').change(selectFile)

// -----------------------------------------------
