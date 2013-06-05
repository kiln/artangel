var redis = require("redis"),
    r = redis.createClient();

var http = require('http');
http.createServer(function (req, res) {
    r.subscribe("artangel");
    res.writeHead(200, {'Content-Type': 'text/plain', 'Cache-Control': 'no-cache'});
    r.once("message", function (channel, message) {
        res.end(message);
    });

}).listen(8124, "127.0.0.1");
console.log('Server running at http://127.0.0.1:8124/');
