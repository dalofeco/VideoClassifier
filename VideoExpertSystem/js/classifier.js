// Array to store frame sequence to send
var frames = []
var frameCount = 0;

// Websocket connection object
var ws = null

// Streaming STATE variable
var STREAMING = false

// Intervals for timed interval functions
const SEND_TIME_INTERVAL = 500;
const FRAME_TIME_INTERVAL = 100;

// Define number of frames to send in a single batch
const NUMBER_OF_FRAMES = 16;

// Interval function placeholders for clearing intervals 
var frameInterval = null
var requestInterval = null

// -------------- DOCUMENT READY SCRIPT -----------------

$(document).ready(function() {

    // Graceful websocket closing before window unload
    window.onbeforeunload = function() {
        if (ws != null) {
            ws.onclose = function() {}; // disable on close handler
            ws.close() // close web socket
            ws = null
        }
    }
    
    // Define file picker handler
    $('#videoFilePicker').change(selectFile)
    
    // Define handler for activating webcam
    $("#webcamButton").click(function() {
    	navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;
		
		if (navigator.getUserMedia) {
			navigator.getUserMedia({video: true}, handleWebcamStream, webcamError)
		}
    });
    
    // Define video player handler
    $('#videoPlayer').on('loadedmetadata', function() {
        if ('function' === typeof duration) {
            duration = duration(this.duration)
            this.currentTime = Math.min(Math.max(0, (duration < 0 ? this.duration : 0) + duration), this.duration)
        }
    });
    
    // Define classify button handler to start active analysis
    $("#classifyButton").click(toggleAnalysis);
});

// ------------------------------------------------------
// -------------------- WEB SOCKETS ---------------------

// Initializer for web socket
function initWebSocket(onopenCallback) {
    
    // Declare websocket object with url
    ws = new WebSocket("ws://" + window.location.hostname + ":8080/ws")
    
    // On websocket connection established
    ws.onopen = onopenCallback
    
    // When message is recieved
    ws.onmessage = function(event) {
        console.log("Recieved message!")
        updateResult(event.data)
    }
    
    // When ws is closed
    ws.onclose = function(event) {
        ws = null
        console.log("Websocket connection closed")
        
        stopAnalysis()
    }
    
    return ws
}

// Sends all stored frames to server via websocket
function sendFramesForClassification(startTime, framesCopy) {
    
    // Make sure ws is not null
    if (ws && frames.length == NUMBER_OF_FRAMES) {
        
        // Log
        console.log("Sending " + framesCopy.length.toString() + " frames.")
        
        // Send JSON array 
        ws.send(JSON.stringify(framesCopy))

    } else {
        console.log("Couldn't send frames: " + framesCopy.length.toString())
    }
}

// ------------------------------------------------------
// ------------ VIDEO FRAME CLASSIFICATION --------------

// Initiates the video analysis process from the start
function startAnalysis() {
    
    // Only start stream if inactive
    if (!STREAMING) {
        
        // Init websocket with defined on open callback
        ws = initWebSocket(function() {

            // Make sure video is not paused
            if (document.getElementById('videoPlayer').paused) 
                $("#videoPlayer").trigger("play")

            // Get new frame and store every defined interval   
            frameInterval = setInterval(function() {
                getFrame(function(frameData) {
                    frames.push(frameData['blob'])
                    frameCount++
                    console.log("Adding frame to frames")
                    
                    // Send frames when count is 16
                    if (frameCount == 16) {
                        
                        frameCopy = frames.slice(0)
                        
                        sendFramesForClassification(Date.now(), frames.slice(0))
                        frameCount = 0
                        frames = []
                    }
                })
            }, FRAME_TIME_INTERVAL)    

//            // Send request every defined interval 
//            requestInterval = setInterval(function() {
//                startTime = Date.now()
//                sendFramesForClassification(startTime)
//            }, SEND_TIME_INTERVAL)    

        }) 
        
        STREAMING = true
    }
}

// Stops video analysis process
function stopAnalysis() {
    // Only stop streaming if active
    if (STREAMING)

        // Clear the interval functions
        clearInterval(frameInterval)
        clearInterval(requestInterval)

        // Pause video if not already paused
        if (!document.getElementById('videoPlayer').paused)
            $("#videoPlayer").trigger("pause");
        
        STREAMING = false
    
    
    // Close websocket connection if active
    if (ws)
        ws.close()
    
    ws = null
}

// Toggle streaming: handler for classify button
function toggleAnalysis() {
    if (!STREAMING) {
        startAnalysis()
    } else {
        stopAnalysis()
    }
}

// ---------- DOM ELEMENT MANIPULATION ----------
function updateResult(result){
    $("#results").text(result)
}

// ------------ DATA MANIPULATION ---------------
function b64Encode(imageBlob, callback) {
    const reader = new FileReader()
    reader.readAsBinaryString(imageBlob)

    // This fires after the blob has been read/loaded.
    reader.addEventListener('loadend', (e) => {

        // Get image blob from result
        const imageBlobText = e.srcElement.result;

        var b64image = btoa(imageBlobText)
        
        callback(b64image)
    })  
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

    // Get canvas context and draw video player image onto it
    var context = canvas.getContext('2d')
    context.drawImage(videoPlayer, 0, 0, canvas.width, canvas.height);
    
    // Get image data by converting to base64 blob
    var image = new Image()
    image.src = canvas.toDataURL()
    
    canvas.toBlob(function(blob) {
        b64Encode(blob, function(b64blob) {
            callback({'blob': b64blob, 'time': timeStamp})
        })    
    }, 'image/jpeg', 1)

}

// ---------------- FILE PICKER ----------------
// Function for when file picker selection changes
function selectFile(e) {
    
    // Get file name if picked
    if (event.target.files.length == 1) {

        videoFileName = event.target.files[0].name

        // Convert into URL
        var fileURL = URL.createObjectURL(event.target.files[0])

        // Get video player and set URL
        videoPlayer = $("#videoPlayer")
        videoPlayer.attr("src", fileURL)

        // Set count to 
        frameCount = 0
    } else if (event.target.files.length > 1) {
        alert("Only 1 video file allowed!")
    } else {
        console.log("No files picked.")
    }
}

// -----------------------------------------------

// ---------------- HTTP HELPERS -----------------
// Sends a POST request, callback must accept response json object
function sendPOST(data, url, content_type, callback) {
    
    // Create reaquests and set headers
    var xhttp = new XMLHttpRequest()
    xhttp.open("POST", url, true)
    xhttp.setRequestHeader("Content-Type", content_type)
    //xhttp.setRequestHeader("Content-Length", data.length)
    xhttp.onreadystatechange = function() {
        // Make sure response is recieved and proper
        if (this.readyState == 4 && this.status == 200) {
            callback(JSON.parse(this.responseText))
        }
    }
    xhttp.send(data)
}

