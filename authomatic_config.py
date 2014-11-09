from authomatic.providers import oauth2
import os

AUTHOMATIC_CONFIG = {
	'facebook': {   
		'class_': oauth2.Facebook,
		
		# Get these credentials from a new Facebook app at developer.facebook.com
		'consumer_key': os.environ.get('FACEBOOK_ID'),
		'consumer_secret': os.environ.get('FACEBOOK_SECRET'),
		
		# Read about Facebook OAuth scopes here: https://developers.facebook.com/docs/facebook-login/permissions/v2.2
		'scope': ['public_profile', 'user_about_me', 'email'],
	},	
}