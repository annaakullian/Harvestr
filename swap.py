from flask import Flask, render_template, request, session, flash, redirect, Markup, g
import os
import requests 
from model import User, session as dbsession


app =  Flask(__name__)
app.secret_key="annabanana"

key = os.environ.get("GOOGLE_MAPS_EMBED_KEY")

#this is the home page
@app.route('/')
def home_page():
	# user = dbsession.query(User).first()
	session['user'] = {}
	return render_template("home.html")

@app.route('/howitworks')
def how_it_works():
	return render_template("howitworks.html")

@app.route('/signup', methods=['GET'])
def sign_up():
	return render_template("signup.html")

#next put flash in template!!
@app.route('/signup', methods=['POST'])
def process_new_user():
	user_location = request.form['user_location']
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	user_email = request.form['user_email']
	facebookid =request.form['facebookid']
	user_name = request.form['user_name']
	password = request.form['password']
	user = User(latitude = user_latitude, longitude=user_longitude, facebookid=facebookid, name=user_name, email = user_email, password=password, location=user_location)
	if dbsession.query(User).filter_by(email = user_email).first():
		flash("That email is taken. If you are already a harvester, log in here!"+ Markup("<h1><a href='/login'>Login</a></h1>"))
		return redirect('/signup')
	else:
		dbsession.add(user)
    	dbsession.commit()
    	session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebook': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
    	return render_template("profile.html", user=session['user'])

@app.route('/login', methods=['GET'])
def login():
	return render_template("login.html")


@app.route('/login', methods=['POST'])	
def process_login():
	user_email = request.form['user_email']
	password = request.form['password']

	user = dbsession.query(User).filter_by(password=password).filter_by(email=user_email).first()
	if user:
		session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebook': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
		return render_template("profile.html", user=session['user']) 
	else:
		flash("That user was not recognized. Please try again, or create an account here:"+ Markup("<h1><a href='/signup'>Signup</a></h1>"))
		return redirect("/login")

@app.route('/profile')	
def profile():
	# user = dbsession.query(User).first()
	return render_template("profile.html")

@app.route('/editprofile', methods=['GET'])
def editprofile():
	# user = dbsession.query(User).first()
	return render_template("editprofile.html", key=key, user=session['user'])

@app.route('/editprofile', methods=['POST'])
def get_user_info():
	user_location = request.form['user_location']
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	user_email = request.form['user_email']
	facebookid =request.form['facebookid']
	user_name = request.form['user_name']

	user = dbsession.query(User).filter_by(email = session['user']['email']).first()
	user.name = user_name
	user.latitude = user_latitude
	user.longitude = user_longitude
	user.email = user_email
	user.location = user_location
	user.facebookid = facebookid 
	dbsession.commit()
	#upate the session
	session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebook': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
	return render_template("profile.html", user=session['user'])



@app.route('/harvest')
def harvest():
	return render_template("harvest.html", key=key)




if __name__ == '__main__':
	app.run(debug=True)