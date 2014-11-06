from flask import Flask, render_template, request
import os
import requests 
from model import User, session as dbsession
from flask.ext.social import Social 

app =  Flask(__name__)
app.secret_key="annabanana"

#facebook app stuff!
app.config['SOCIAL_FACEBOOK'] = {
    'consumer_key': os.environ.get("FACEBOOK_ID"),
    'consumer_secret': os.environ.get("FACEBOOK_SECRET")
}
app.config['SECURITY_POST_LOGIN'] = '/profile'
print os.environ.get("FACEBOOK_ID")
Social(app, dbsession)

key = os.environ.get("GOOGLE_MAPS_EMBED_KEY")

#this is the home page
@app.route('/')
def home_page():
	user = dbsession.query(User).first()
	return render_template("home.html", user=user)

@app.route('/howitworks')
def how_it_works():
	return render_template("howitworks.html")

@app.route('/profile')	
def profile():
	return render_template("profile.html")

@app.route('/editprofile', methods=['GET'])
def editprofile():
	return render_template("editprofile.html", key=key)

#this gets the users address and gets the latitude and longitude
@app.route('/editprofile', methods=['POST'])
def get_user_info():
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	print user_latitude
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	user_email = request.form['user_email']
	user_name = request.form['user_name']
	return render_template("profile.html", name = user_name, longitude=user_longitude, latitude=user_latitude, user_email=user_email)

@app.route('/harvest')
def harvest():
	return render_template("harvest.html", key=key)




if __name__ == '__main__':
	app.run(debug=True)