var fs = require('fs'),
	exec = require('child_process').exec,
	text = require('TextBelt');

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

			console.log(users);


			var opts = {
				region: config.sms.region,
				message: config.sms.message
			}

			var sent = 0;

			users.forEach(function( user ) {

				if( 0 === sent && "true" === user.present ) {
					console.log( user.name );
					sent = 1;
					text.send( user.phone, config.sms.message, undefined, config.sms.region, function( err ) {
						console.log( err );
						if ( err ) {
							console.log( err );
							sent = 0;
						}
					});
				}
			});
		});
	});
});
