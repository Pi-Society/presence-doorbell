var fs = require('fs'),
	http = require('http'),
	exec = require('child_process').exec,
	querystring = require('querystring');

var config = null;

fs.readFile('./config.json', 'utf8', function (err, data) {
	if (err) throw err; // we'll not consider error handling for now
	config = JSON.parse( data );

	var dash_button = require('node-dash-button'),
	dash = dash_button( config.dash_button );

	dash.on('detected', function() {
		console.log('Button pushed!');

		// read file asyncronously in case users come and go
		fs.readFile('./config.json', 'utf8', function (err, data) {
			if (err) throw err; // we'll not consider error handling for now
			config = JSON.parse( data );

			var users = config.users;

			var opts = {
				region: config.sms.region,
				message: config.sms.message
			}

			var sent = 0;

			users.forEach(function( user ) {

				if( 0 === sent && "true" === user.present ) {
					console.log( user.name );
					sent = 1;

					var username = config.sms.user;
					var password = config.sms.password;

					var data = querystring.stringify({
						message: config.sms.message,
						to: user.phone,
						countrycode: 'US'
					});

					const options = {
						hostname: 'api.transmitsms.com',
						port: 80,
						path: '/send-sms.json',
						method: 'POST',
						headers: {
							'Content-Type': 'application/x-www-form-urlencoded',
							'Content-Length': Buffer.byteLength(data),
							'Authorization': 'Basic ' + new Buffer(username + ':' + password).toString('base64')
						}
					};

					const req = http.request(options, (res) => {
						console.log(`STATUS: ${res.statusCode}`);
						console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
						res.setEncoding('utf8');
						res.on('data', (chunk) => {
							console.log(`BODY: ${chunk}`);
						});
						res.on('end', () => {
							console.log('No more data in response.');
						});
					});

					req.write(data);
					req.end();
				}
			});
		});
	});
});
