
var videoFileName = '';
var ws = null

const interval = 3;
var frameCount = 0;

var STREAMING = false
        
// ------------ DOCUMENT READY SCRIPT --------------

// On document load
$(document).ready(function() {
    
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

function initWebSocket() {
    // Initialize web socket
    ws = new WebSocket("ws://" + document.location.host + "/ws/bind")
    
    // Define function for when socket closes
    ws.onclose = function(e) {
        console.log("Socket Closed...")
        console.log(e)
    };

    // Define handler for open event
    ws.onopen = function(e) {
        console.log("Socket Opened...")
        console.log(e)
    }

    return ws
}

// function handleWebSocketMessage(messageEvent) {
//     console.log(messageEvent.data)
// }

// ---------------------------------------------
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


// ------------ VIDEO FRAME CLASSIFICATION --------------

// Initiates the video analysis process from the start
function startVideoAnalysis() {

    // Make sure video is not paused
    if (document.getElementById('videoPlayer').paused)
        $("#videoPlayer").trigger("play")

    // Initialize web socket connection
    ws = initWebSocket()

    // When message recieved, send FRAME response
    ws.onmessage = function(event) {

        // Get and parse data
        msg = event.data

        // Frame request, send next frame
        if (msg == "FRAME") {
            sendFrameForClassification()

        // Assume result information, process and show
        } else {
            $("#results").text(msg)
        }
        // } else {
        //     console.log("Unrecognized websocket message")
        //     console.log(event)
        // }
    }
}

function stopVideoAnalysis() {

    // Pause video if not already paused
    if (!document.getElementById('videoPlayer').paused)
        $("#videoPlayer").trigger("pause");

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
            const imageBlobText = e.srcElement.result;

            // Round to nearest integer, multiplying by 100 to consider hundreths
            roundedTimeStamp = Math.round(timeStamp * 100);

            // Send image data via socket
            ws.send(imageBlob)
        });

    });
}

window.onbeforeunload = function() {
    if (ws != nil) {
        ws.onclose = function() {}; // disable on close handler
        ws.close() // close web socket
        ws = nil
    }
}