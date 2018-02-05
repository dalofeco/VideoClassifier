var express = require('express')
var app = express();

var fs = require('fs');

//-------------------------------------------------------------//

//GET//
app.get('/classify', function(req, res) {
    var exec = require('child_process').exec;
    exec('python classify.py fire.jpg', (error, stdout, stderr) => {
        if (error) {
            console.error('exec error : ${error}');
            return;
        }
        res.send(`${stdout}`);
        //console.log(`stderr: ${stderr}`);
    });
});


var server = app.listen(process.env.PORT || '8080', '0.0.0.0', function() {
  if (process.env.PORT) {
    console.log("https://someurlforc9.io/");
  }
  else {
    console.log('App listening at http://%s:%s', server.address().address, server.address().port);
  }
});
