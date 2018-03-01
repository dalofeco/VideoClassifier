
var videoFileName = '';
const INTERVAL = 250;
var timeInterval = null
var frameCount = 0;
var ws = null

var STREAMING = false
var lastTime = 0
        
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


// ---------------------------------------------

// ------------ VIDEO FRAME CLASSIFICATION --------------


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

// Initiates the video analysis process from the start
function startVideoAnalysis() {
    
    // Define callback for when socket is initialized
    var startStreamCallback = function(data) {
        console.log("Data:")
        console.log(data)
        
        // Get connection id from server
        connectionID = data['cid']
        
        // Make sure video is not paused
        if (document.getElementById('videoPlayer').paused) 
            $("#videoPlayer").trigger("play")

        // Define handler for video updates
        timeInterval = setInterval(function() {
            startTime = Date.now()

            console.log("Sending frame " + frameCount.toString())
            sendFrameForClassification(connectionID, startTime)
            
            frameCount++;
        }, INTERVAL)
            
    }
    
    
    // Generate data for req
    data = {"id": "0", "intent":"start"}
    
    // Stringify the JSON object and send post
    jsonData = JSON.stringify(data)
    sendPOST(jsonData, '/classifyInit', 'application/json', startStreamCallback)
}

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

function stopVideoAnalysis() {
    // Remove the video player timeupdate handler
    $('#videoPlayer').on('timeupdate', function(){})

    // Pause video if not already paused
    if (!document.getElementById('videoPlayer').paused)
        $("#videoPlayer").trigger("pause");
    
    clearInterval(timeInterval)

}

// Function to classify the frame currently played on videoPlayer
function sendFrameForClassification(connectionID, startTime) {
    
    // Get current on screen frame and its data
    getFrame(function(frameData) {
        imageBlob = frameData['blob']
        timeStamp = frameData['time']

        const reader = new FileReader()
        reader.readAsBinaryString(imageBlob)

        // This fires after the blob has been read/loaded.
        reader.addEventListener('loadend', (e) => {

            // Make sure connectionID is supplied
            if (connectionID != null) {
                const imageBlobText = e.srcElement.result;

//                var b64image = imageBlobText.replace(/^data:image\/(png|jpg);base64,/, "");
                var b64image = btoa(imageBlobText)

                // Send image data via socket
                sendImageData(b64image, connectionID, startTime)
            }
        });

    });
}

// Sends image data over post for with connectionID
function sendImageData(textBlob, connectionID, startTime) {
    
    // Round to nearest integer, multiplying by 100 to consider hundreths
    roundedTimeStamp = Math.round(timeStamp * 100);
    
    // Define data to be sent to server
//    var data = {
//        "cid": connectionID,
//        "data": textBlob.toString(),
//        "timestamp": roundedTimeStamp
//    }
    
    // Send post for classification with callback as updating result
    sendPOST(textBlob, "/classify", "image/jpeg", function(result) {
        var resultText = result['result']
        updateResult("SH:" + resultText['shooting'] + " - " + "NO:" + resultText['normal'])
        console.log("Took " + ((Date.now() - startTime)/1000).toString() + " seconds")
    })
}

function updateResult(result){
    $("#results").text(result)
}



// --------------- VIDEO PLAYER ------------------

function getFrame(callback) {
    
    console.log("Interval: " + (Date.now() - lastTime).toString() + " ms")
    lastTime = Date.now()
    
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
$('#videoFilePicker').change(selectFile)

// -----------------------------------------------