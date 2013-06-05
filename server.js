var redis = require("redis"),
    r = redis.createClient();

var http = require('http');
http.createServer(function (req, res) {
    console.log("Request received...");
    r.subscribe("artangel");
    res.writeHead(200, {'Content-Type': 'application/json', 'Cache-Control': 'no-cache'});
    r.once("message", function (channel, message) {
        console.log(message);
        res.end(message);
    });

}).listen(8124, "127.0.0.1");
console.log('Server running at http://127.0.0.1:8124/');
