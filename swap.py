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
	user = dbsession.query(User).first()
	return render_template("home.html", user=user)

@app.route('/howitworks')
def how_it_works():
	return render_template("howitworks.html")

@app.route('/signup', methods=['GET'])
def sign_up():
	return render_template("signup.html")

#next put flash in template!!
@app.route('/signup', methods=['POST'])
def process_new_user():
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	user_location = request.form['user_location']
	user_email = request.form['user_email']
	facebook_id =request.form['facebook_id']
	user_name = request.form['user_name']
	password = request.form['password']
	user = User(latitude = user_latitude, longitude=user_longitude, facebook_id=facebook_id, name=user_name, email = user_email, password=password)
	if dbsession.query(User).filter_by(email = user_email).first():
		flash("That email is taken. If you are already a harvester, log in here!"+ Markup("<h1><a href='/login'>Login</a></h1>"))
		return redirect('/signup')
	else:
		dbsession.add(user)
    	dbsession.commit()
    	#make sure this works
    	dbsession.refresh(user)
    	g.current_user = user 
    	return render_template("profile.html", user=user, facebook_id=facebook_id, user_location = user_location, name = user_name, longitude=user_longitude, latitude=user_latitude, user_email=user_email)

@app.route('/login', methods=['GET'])
def login():
	return render_template("login.html")


@app.route('/login', methods=['POST'])	
def process_login():
	user_email = request.form['user_email']
	password = request.form['password']

	user = dbsession.query(User).filter_by(password=password).filter_by(email=user_email).first()
	if user:
		session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location }
		return render_template("profile.html", user=session['user']) 
	else:
		flash("That user was not recognized. Please try again, or create an account here:"+ Markup("<h1><a href='/signup'>Signup</a></h1>"))
		return redirect("/login")

@app.route('/profile')	
def profile():
	user = dbsession.query(User).first()
	return render_template("profile.html", user=user)

@app.route('/editprofile', methods=['GET'])
def editprofile():
	user = dbsession.query(User).first()
	return render_template("editprofile.html", key=key, user=user)

@app.route('/editprofile', methods=['POST'])
def get_user_info():
	user_location = request.form['user_location']
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	user_email = request.form['user_email']
	facebook_id =request.form['facebook_id']
	user_name = request.form['user_name']
	
	user = dbsession.query(User).filter_by(email = session['user']['email']).first()
	session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebook': user.facebook_id }
	user.name = user_name 
	dbsession.add(user)
	dbsession.commit()
	return render_template("profile.html", user_location = user_location, name = user_name, longitude=user_longitude, latitude=user_latitude, user_email=user_email, user=user)

@app.route('/harvest')
def harvest():
	return render_template("harvest.html", key=key)




if __name__ == '__main__':
	app.run(debug=True)