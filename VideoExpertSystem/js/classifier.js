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
var NUMBER_OF_FRAMES = 16;

var MODEL_TYPE = "cnn-model-1.0"

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
    
    // Define handler for switching model type
    $('.model-select-button').on('click', function() {
        
        // Update with the button's ID
        MODEL_TYPE = this.id;
        
        // Update number of frames to send depending on model type
        if (MODEL_TYPE.slice(0,9) == "cnn-model") {
            NUMBER_OF_FRAMES = 4;
        } else if (MODEL_TYPE.slice(0,10) == "lstm-model") {
            NUMBER_OF_FRAMES = 16;
        } else {
            console.log(MODEL_TYPE.slice(0,10))
        }
        
        // Reset franes and count to 0
        frames = []
        frameCount = 0
        
        // Log
        console.log("Changed MODEL_TYPE to " + MODEL_TYPE)
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
        
        request = {}
        request['type'] = MODEL_TYPE;
        request['frames'] = framesCopy;
        
        // Send JSON array 
        ws.send(JSON.stringify(request))

    } else {
        console.log("Couldn't send frames: " + framesCopy.length.toString())
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

            // Make sure video is not paused
            if (document.getElementById('videoPlayer').paused) 
                $("#videoPlayer").trigger("play")

            // Get new frame and store every defined interval   
            frameInterval = setInterval(function() {
                getFrame(function(frameData) {
                    frames.push(frameData['blob'])
                    frameCount++
                    console.log("Adding frame to frames")
                    
                    // Send frames when count target is met
                    if (frameCount == NUMBER_OF_FRAMES) {
                        
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
function updateResult(results){
    
    // Empty results pane
    $("#results-pane").empty()
    
    results = JSON.parse(results)
    
    // For each key
    for (var key in results) {
        
        // Capitalized key for aesthetics
        capitalizedKey = key.charAt(0).toUpperCase() + key.slice(1)
        
        // Create a paragraph element with confidence score
        resultP = document.createElement("p")
        resultP.setAttribute("id", key)
        resultP.setAttribute("class", "resultsText")
        resultP.innerHTML = capitalizedKey + " Confidence Score:&emsp;"
        
        // Create percentage score
        spanScore = document.createElement("span")
        spanScore.setAttribute("class", "scoreText")
        spanScore.innerHTML = results[key].toString() + "%"
        
        // Add score to result p
        resultP.appendChild(spanScore)
        
        // Add to results pane
        $("#results-pane").append(resultP)
        
    }
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

