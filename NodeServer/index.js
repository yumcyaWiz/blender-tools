const chokidar = require('chokidar');
const fs = require('fs');

let watchFilename = 'tmp/scene.json'
if (process.argv[2] !== undefined) {
    watchFilename = process.argv[2];
}

chokidar.watch('/tmp/scene.json', {ignored: /[\/\\]\./}).on('all', (event, path) => {
    const data = JSON.parse(fs.readFileSync('/tmp/scene.json', 'utf8'));
    console.log(event, path);
    console.log(JSON.stringify(data, null, 4));
});
