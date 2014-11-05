from flask import Flask, render_template, request
import os
import requests 

app =  Flask(__name__)
app.secret_key="annabanana"

key = os.environ.get("GOOGLE_MAPS_EMBED_KEY")

#this is the home page
@app.route('/')
def home_page():
	return render_template("home.html")

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
	return render_template("profile.html")




if __name__ == '__main__':
	app.run(debug=True)