var redis = require("redis"),
    url = require("url");

var http = require('http');
http.createServer(function (req, res) {
    var preq = url.parse(req.url, true),
        channel = preq.query.channel;
    console.log("Listening on channel '" + channel + "'...");
    
    var r = redis.createClient();
    r.subscribe(channel);
    res.writeHead(200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'});
    r.once("message", function (channel, message) {
        r.quit();
        console.log(message);
        res.end(message);
    });

}).listen(8124, "127.0.0.1");
console.log('Server running at http://127.0.0.1:8124/');
