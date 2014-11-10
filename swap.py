from flask import Flask, render_template, request, session, flash, redirect, Markup, url_for, send_from_directory
from werkzeug import secure_filename
# from flask.ext.login import LoginManager, login_user, login_required, logout_user
# import authomatic 
# from authomatic.adapters import WerkzeugAdapter
# from authomatic import Authomatic
import os
import requests 
from model import User, session as dbsession


# from authomatic_config import AUTHOMATIC_CONFIG

app =  Flask(__name__)
app.secret_key="annabanana"

#this is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'gif', 'png', 'pdf', 'txt'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#set up flask login manager and authomatic helpers

# app.config['SOCIAL_FACEBOOK'] = {
#     'consumer_key': os.environ.get("FACEBOOK_ID"),
#     'consumer_secret': os.environ.get("FACEBOOK_SECRET")
# }

# login_manager = LoginManager()
# login_manager.init_app(app)
# authomatic = Authomatic(AUTHOMATIC_CONFIG, 'your secret string', report_errors=False)


key = os.environ.get("GOOGLE_MAPS_EMBED_KEY")

#this is the home page
@app.route('/')
def home_page():
	# user = dbsession.query(User).first()
	session['user'] = {}
	return render_template("home.html")



# Login route for all OAuth providers. If one were to add a second provider 
# (i.e. Twitter, Google), more logic could be added to this method by
# # checkingthe "provider_name" variable
# @app.route('/loginfb/<provider_name>/', methods=['GET', 'POST'])
# def login(provider_name):
# 	response = make_response()
# 	result = authomatic.login(WerkzeugAdapter(request, response), provider_name)

# 	if result:
# 		# If we've received a user from Facebook...
# 		if result.user:
# 			# Get the user's profile data and look for it in our database
# 			result.user.update()
# 			facebook_id = result.user.id
# 			user = dbsession.query(User).filter_by(facebook_id = facebook_id).first()

# 			# If we don't find the user in our database, add it!
# 			if not user:
# 				user = User(facebook_id = facebook_id, email=result.user.email, name=result.user.name)
# 				dbsession.add(user)
# 				dbsession.commit()

# 			# Store the user in our session, logging them in 
# 			login_user(user)

# 		# Redirect somewhere after log in. In this case, the homepage
# 		return redirect('/')

# 	return response

# Clear our session, logging the user out and returning them
# to the home page.
# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect('/')

# flask-login required method
# Tell flask-login how to find the current user in the database
# @login_manager.user_loader
# def load_user(id):
# 	return dbsession.query(User).filter_by(id = id).first()





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
		flash("That email is taken. If you are already a harvester, log in here!"+ Markup("<h1><a href='/loginfb'>Login</a></h1>"))
		return redirect('/signup')
	else:
		dbsession.add(user)
    	dbsession.commit()
    	session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebookid': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
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
		session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebookid': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
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
	user_email = request.form['user_email']

	if session['user']['email'] != user_email:
		flash("email change not allowed")
		return redirect(url_for('editprofile'))

	user_location = request.form['user_location']
	if len(user_location) < 2:
		flash("invalid location")
		return redirect('/editprofile')

	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
		request.form['user_location'])
	if r.json()['status'] == "ZERO_RESULTS":
		flash("could not find location")
		return redirect('/editprofile')

	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
	facebookid =request.form['facebookid']
	user_name = request.form['user_name']
	if len(user_name) < 1:
		flash("invalid user name")
		return redirect('/editprofile')

	user = dbsession.query(User).filter_by(email = session['user']['email']).first()
	user.name = user_name
	user.latitude = user_latitude
	user.longitude = user_longitude
	user.email = user_email
	user.location = user_location
	user.facebookid = facebookid 
	dbsession.commit()
	#upate the session
	session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebookid': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
	

	uploaded_files = request.files.getlist("file[]")
	filenames = []

	for photo in uploaded_files:
		# if file and allowed_file(file.filename):
		print "helloooo!"
		print type(photo)
		print dir(photo)
		filename = secure_filename(photo.filename)
		photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		filenames.append(filename)

	return render_template("profile.html", user=session['user'], photos = filenames)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/harvest')
def harvest():
	return render_template("harvest.html", key=key)




if __name__ == '__main__':
	app.run(debug=True)

