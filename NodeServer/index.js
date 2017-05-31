const request = require('request');
const chokidar = require('chokidar');
const fs = require('fs');

function MakeRequest (parameter) {
    return {
        "jsonrpc": "2.0",
        "method": "render",
        "params": parameter
    }
}

function postRequest (data) {
    const options = {
        uri: "http://localhost:8081/rpc",
        headers: {
            "Content-type": "application/json",
        },
        json: data
    };
    request.post(options, function (error, response, body)  {
        console.log(body);
    });
}

let watchFilename = 'tmp/scene.json'
if (process.argv[2] !== undefined) {
    watchFilename = process.argv[2];
}

chokidar.watch('/tmp/scene.json', {ignored: /[\/\\]\./}).on('all', (event, path) => {
    const data = JSON.parse(fs.readFileSync('/tmp/scene.json', 'utf8') || "null");
    if (data === null) return;
    console.log(event, path);
    const request = MakeRequest(data);
    console.log(JSON.stringify(request, null, 4));
    postRequest(request);
});
