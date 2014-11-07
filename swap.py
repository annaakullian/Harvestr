from flask import Flask, render_template, request
import os
import requests 
from model import User, session as dbsession

app =  Flask(__name__)
app.secret_key="annabanana"

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
	user = dbsession.query(User).first()
	return render_template("profile.html", user=user)

@app.route('/editprofile', methods=['GET'])
def editprofile():
	user = dbsession.query(User).first()
	return render_template("editprofile.html", key=key, user=user)

#this gets the users address and gets the latitude and longitude
@app.route('/editprofile', methods=['POST'])
def get_user_info():
	user = dbsession.query(User).first()
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	user_location = request.form['user_location']
	user_email = request.form['user_email']
	#put an if statment here to see if user exists 
	user_name = request.form['user_name']
	update_user = User(name=user_name, email=user_email, latitude=user_latitude, longitude=user_longitude, last_log_in="1/2/13")
	dbsession.add(update_user)
	dbsession.commit()
	user = dbsession.query(User).filter_by(name = update_user.name).first()

	return render_template("profile.html", user_location = user_location, name = user_name, longitude=user_longitude, latitude=user_latitude, user_email=user_email, user=user)

@app.route('/harvest')
def harvest():
	return render_template("harvest.html", key=key)




if __name__ == '__main__':
	app.run(debug=True)