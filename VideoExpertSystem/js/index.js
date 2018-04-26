
// Array to store frame sequence to send
var frames = []
var frameCount = 0;

// Websocket connection object
var ws = null

// Streaming STATE variable
var STREAMING = false

// Intervals for timed interval functions
const SEND_TIME_INTERVAL = 1000;
const FRAME_TIME_INTERVAL = 200;

// Interval function placeholders for clearing intervals 
var frameInterval = null
var requestInterval = null

// -------------- DOCUMENT READY SCRIPT -----------------

$(document).ready(function() {
    

});


// Sends all stored frames to server via websocket
function sendFramesForClassification(startTime) {
    
    // Make sure ws is not null
    if (ws && frames.length == 16) {
        
        // Log
        console.log("Sending " + frames.length.toString() + " frames.")
        
        // Send JSON array 
        ws.send(JSON.stringify(frames))

        // Clear frames array
        frames = []
    } else {
        console.log("Couldn't send frames: " + frames.length.toString())
    }
}

// ------------- WEB CAM STREAM STUFF -------------------

// WEBCAM STREAM HANDLERS
function handleWebcamStream(stream){
	document.querySelector('#videoPlayer').src = window.URL.createObjectURL(stream);
}

function webcamError (e){
	alert("There is a problem with the video stream.");
}

// ------------------------------------------------------
// ------------ VIDEO FRAME CLASSIFICATION --------------

// Initiates the video analysis process from the start
function startAnalysis() {
    
    // Only start stream if inactive
    if (!STREAMING) {
        
        // Init websocket with defined on open callback
        ws = initWebSocket(function() {
            
            console.log("Opened websocket connection.")

            // Make sure video is not paused
            if (document.getElementById('videoPlayer').paused) 
                $("#videoPlayer").trigger("play")

            // Get new frame and store every defined interval   
            frameInterval = setInterval(function() {
                getFrame(function(frameData) {
                    frames.push(frameData['blob'])
                    frameCount++
                    console.log("Adding frame to frames")
                })
            }, FRAME_TIME_INTERVAL)    

            // Send request every defined interval 
            requestInterval = setInterval(function() {
                startTime = Date.now()
                sendFramesForClassification(startTime)
            }, SEND_TIME_INTERVAL)    

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

