// Express for request handling (web server)
var express = require('express')
var app = express();

var Client = require('node-rest-client').Client;
var client = new Client();

// Experimental (but more accurate) performance metrics
const { performance } = require('perf_hooks');    

var time = require('time');

var fs = require('fs');

// Debug switch
var DEBUG = false;

//-------------------------------------------------------------//

//GET//
app.get('/classify', function(req, res) {
        
    console.log("GET Request");

    // Mark starting point
    //performance.mark('A');
    
    // To time the process, record current time
    var start = performance.now()
    
    client.get("http://127.0.0.1:8081/classify", function(data, response) {
        
        // Print out the recieved data
        console.log(data);
        
        // Log the elapsed milliseconds
        var duration = performance.now() - start;
        console.log(duration.toString() + ' milliseconds');
//    
        res.send(data);
    });
        
//    var exec = require('child_process').exec;
//    exec('cd ../VideoExpertSystem && python3 classify.py ../tests/fire.jpg', (error, stdout, stderr) => {
//        
//        // If an execution error occured, print it and return
//        if (error) {
//            console.error(`exec error : ${error}`);
//            return;
//        }
//        
        // Subtract current seconds with starting time
        // var duration = time.time() - start;
        // console.log(`Processed in: ${duration}`);

        // Mark finished pointm and measure time
        // performance.mark('B');
        // performance.measure('A to B', 'A', 'B');
        // const measure = performance.getEntriesByName('A to B')[0];
        
        // Clear all marks from performance to allow for next measurement
        // performance.clearMarks();
        // performance.clearMeasures();
        
        // var duration = performance.now() - start;
        
        // Log the elapsed milliseconds
        // console.log(duration.toString() + ' milliseconds');

        // debugging mode does not ignore errors/warnings
        // if (DEBUG)
        //     console.log(`stderr: ${stderr}`);
        
        // res.send(`${duration}: ${stdout}`);
        
    // });
});


var server = app.listen(process.env.PORT || '8080', '0.0.0.0', function() {
  if (process.env.PORT) {
    console.log("https://someurlforc9.io/");
  }
  else {
    console.log('App listening at http://%s:%s', server.address().address, server.address().port);
  }
});
