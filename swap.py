"""Functions and handlers for Harvestr.

This file has all function and handlers, and the secret keys from the environment are accessed. 
"""

from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, make_response
from werkzeug import secure_filename
import hashlib
from flask.ext.login import LoginManager, login_user, login_required, logout_user, current_user
import authomatic 
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
import os
import requests 
from model import User, Item, ItemAttribute, MatchOffer, MatchOfferItem, ItemViewed, session as dbsession
import json
from sqlalchemy.sql import exists
from math import sin, cos, sqrt, atan2, radians
import datetime 
from flask.ext.mail import Mail, Message
from authomatic_config import AUTHOMATIC_CONFIG
from boto.s3.key import Key
from boto.s3.connection import S3Connection

#keys and connection for amazon s3
access_key_s3 = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key_s3 = os.environ.get('AWS_SECRET_ACCESS_KEY')

conn = S3Connection('access_key_s3', 'secret_key_s3')
conn = S3Connection()

s3_bucket = conn.get_bucket(os.environ.get("MY_BUCKET"))

DEBUG = True
SECRET_KEY = 'hidden'

#information for the smtp gmail server for sending emails
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_TLS = False
MAIL_USE_SSL= True
MAIL_USERNAME = 'harvestr.swap@gmail.com'
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") 

app =  Flask(__name__)
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "ABC")
app.secret_key=SECRET_KEY
app.config.from_object(__name__)
mail = Mail(app)

# this is the path to the upload directory, if not using Amazon s3
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'gif', 'png', 'pdf', 'txt'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#set up flask login manager and authomatic helpers
login_manager = LoginManager()
login_manager.init_app(app)
authomatic = Authomatic(AUTHOMATIC_CONFIG, 'your secret string', report_errors=False)

#key for googlemaps api
key = os.environ.get("GOOGLE_MAPS_EMBED_KEY")

@app.route('/')
def home_page():
	"""This is the homepage
	"""
	return render_template("home.html")

@app.route('/matchopenitems', methods=['GET'])
def matchopenitems():
	"""This page returns the match's open items.

	From a users profile page, they can click on their match's profile picture which will lead them 
	to a page with all of that user's open items.
	"""
	user_id = request.args.get("user_id")
	user = dbsession.query(User).filter_by(id=user_id).one()
	user_items = user.items
	return render_template("matchopenitems.html", user_items=user_items)

@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
	"""This is the login route for all OAuth providers.

	This route logs a user in with facebook, gets their information from their
	facebook profile, and stores the user in our session. Once the user is logged in,
	they are redirected to their profile page.	
	"""
	# If one were to add a second provider 
	# (i.e. Twitter, Google), more logic could be added to this method by
	# checkingthe "provider_name" variable
	response = make_response()
	result = authomatic.login(WerkzeugAdapter(request, response), provider_name)

	if result:
		# If we've received a user from Facebook...
		if result.user:
			# Get the user's profile data and look for it in our database
			result.user.update()
			facebook_id = result.user.id
			user = dbsession.query(User).filter_by(facebookid = facebook_id).first()

			# If we don't find the user in our database, add it!
			if not user:
				profilepic = "http://graph.facebook.com/"+ facebook_id +"/picture?type=large"
				user = User(facebookid = facebook_id, email=result.user.email, name=result.user.name, profilepic=profilepic)
				dbsession.add(user)
				dbsession.commit()

			# Store the user in our session, logging them in 
			login_user(user)
			current_user.last_log_in = datetime.datetime.now()
			dbsession.commit()

		# Redirect somewhere after log in. In this case, the homepage
		return redirect('/profile')

	return response

@app.route("/logout")
@login_required
def logout():
	"""This route logs the user out.

	This route clears the session, logs the user out, and returns them to the home page.
	"""
	logout_user()
	return redirect('/')

@login_manager.user_loader
def load_user(id):
	"""This route tells flask-login how to find the current user in the database.

	This is a flask-login required method. 
	It returns the current user.
	"""
	return dbsession.query(User).filter_by(id = id).first()

@app.route('/howitworks')
def how_it_works():
	"""This route returns the html page that explains how the app works to the current user 
	"""
	return render_template("howitworks.html")

@app.route('/profile')	
def profile():
	"""This route brings the user to their profile page.

	The profile page shows the users profile picture from facebook, their address, email,
	their open items, and all of their matches. 
	"""
	#looking for matches to show on profile page
	#first, find matches for gifts
	current_user_items = current_user.items
	match_items = []
	#for gift items
	match_offers_of_current_user = dbsession.query(MatchOfferItem).filter_by(user_id=current_user.id).all()
	if match_offers_of_current_user:
		match_offer_ids_of_current_user = [i.match_offer_id for i in match_offers_of_current_user]
		for match_id in match_offer_ids_of_current_user:
			count_matches = match_offer_ids_of_current_user.count(match_id)
			if count_matches == 1:
				match_offer = dbsession.query(MatchOffer).filter(MatchOffer.id == match_id, MatchOffer.date_of_match != None).first()
				if match_offer:
					match_item = dbsession.query(MatchOfferItem).filter_by(match_offer_id=match_id).first()
					if match_item:
						item = dbsession.query(Item).filter_by(id=match_item.item_id).one()
						match_items.append(item)
	if current_user_items: 
		current_user_item_ids = [i.id for i in current_user_items]
		#get all items in match offer items were items belong to current user
		match_offers_of_current_user = dbsession.query(MatchOfferItem).filter(MatchOfferItem.item_id.in_(current_user_item_ids)).all()
		if match_offers_of_current_user:
			match_offer_ids_of_current_user = [i.match_offer_id for i in match_offers_of_current_user]
			for match_id in match_offer_ids_of_current_user:
				match_offer = dbsession.query(MatchOffer).filter(MatchOffer.id == match_id, MatchOffer.date_of_match != None).first()
				if match_offer:
					match_item = dbsession.query(MatchOfferItem).filter_by(match_offer_id=match_id).filter(~MatchOfferItem.item_id.in_(current_user_item_ids)).first()
					if match_item:
						item = dbsession.query(Item).filter_by(id=match_item.item_id).one()
						match_items.append(item)
	return render_template("profile.html", match_items=match_items)

@app.route('/alluserimages', methods=['GET'])	
def allimages():
	"""This route shows an html page with all of the users items.
	"""
	return render_template("alluserimages.html")

@app.route('/editprofile', methods=['GET'])
def editprofile():
	"""This route shows the users information from the database on the edit profile page.
	
	This will display the user's information as wel as their item's information.
	"""
	items_attribute_dictionary = {}
	items = current_user.items
	for item in items:
		for attribute in item.itemsattributes:
			if item.id in items_attribute_dictionary.keys():
				items_attribute_dictionary[item.id][attribute.attribute_name] = attribute.attribute_value
			else:
				items_attribute_dictionary[item.id] = {attribute.attribute_name : attribute.attribute_value}	
	return render_template("editprofile.html", key=key, items_attribute_dictionary = items_attribute_dictionary)

@app.route('/editprofile', methods=['POST'])
def get_user_info():
	"""This route gets the user's information from the edit profile page and saves it in the database. 

	Here the user can change any of their information, which will then be updated
	in the database. They can also add items and edit the item's attributes.
	Once they save the information, they will be redirected to the profile page.  
	"""
	#Get the user location, and convert to latitude and longitude
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
	user_name = request.form['user_name']
	if len(user_name) < 1:
		flash("invalid user name")
		return redirect('/editprofile')

	#Get all user and item information and add to database
	current_user.name = user_name
	current_user.latitude = user_latitude
	current_user.longitude = user_longitude
	current_user.location = user_location

	description_attribute = ['item_description']

	item_descriptions = {}
	for k, value in request.form.iteritems():
		if "-" not in k:
			continue;
		item_description, photo_id = k.split("-")
		if item_description not in description_attribute:
			continue
		item_descriptions[photo_id] = value

	for photo_id, item_description in item_descriptions.iteritems():
		item = dbsession.query(Item).filter_by(id=photo_id).one()
		item.description = item_description

	photo_attribs = ['forv', 'status', 'gift', 'prepicked']

	photo_updates = {}
	for k,value in request.form.iteritems():
		if "-" not in k:
			continue;
		attr,photo_id = k.split("-")
		if attr not in photo_attribs:
			continue
		if photo_id in photo_updates.keys():
			photo_updates[photo_id][attr] = value
		else:
			photo_updates[photo_id] = {attr: value}

	for photo_id, photo_attributes in photo_updates.iteritems():
		for key, value in photo_attributes.iteritems():
			attribute = dbsession.query(ItemAttribute).filter_by(item_id=photo_id).filter_by(attribute_name=key).first()
			if attribute is None:
				attribute = ItemAttribute(\
					item_id = photo_id,\
					attribute_name = key,\
					attribute_value = value)
				dbsession.add(attribute)
			else:
				attribute.attribute_value = value

	uploaded_files = request.files.getlist("file[]")

	new_forvs = request.form.getlist("forv_new[]")
	new_status = request.form.getlist("status_new[]")
	new_gift = request.form.getlist("gift_new[]")
	new_prepicked = request.form.getlist("prepicked_new[]")
	new_description = request.form.getlist("description_new[]")

	for i in range(len(uploaded_files)):
		if uploaded_files[i].filename == '':
			continue
		
		filedata = uploaded_files[i].stream.read()
		# give each item a unique hash via their hash id   	
		hash_id = hashlib.md5(filedata).hexdigest() 

		#set up information for photos stored in Amazon s3
		k = Key(s3_bucket) 
		k.key = hash_id 
		k.set_contents_from_string(filedata, policy='public-read')
		file_path = k.generate_url(0, query_auth=False)
		
		if dbsession.query(Item).filter_by(hash_id=hash_id).first():
			flash("This photo already exists! You can edit the information on your current photo")
			return redirect(url_for('editprofile'))
		else:
			item = Item(user_id=current_user.id, photo_path=file_path, hash_id=hash_id, description=new_description[i], date_item_added=datetime.datetime.now())
			dbsession.add(item)
	  		dbsession.commit()
	  	forv_value = new_forvs[i]
	  	status_value = new_status[i]
	  	gift_value = new_gift[i]
	  	prepicked_value = new_prepicked[i]

	  	attribute = ItemAttribute(\
					item_id = item.id,\
					attribute_name = "forv",\
					attribute_value = forv_value)
		dbsession.add(attribute)

		attribute = ItemAttribute(\
					item_id = item.id,\
					attribute_name = "status",\
					attribute_value = status_value)
		dbsession.add(attribute)

		attribute = ItemAttribute(\
					item_id = item.id,\
					attribute_name = "gift",\
					attribute_value = gift_value)
		dbsession.add(attribute)

		attribute = ItemAttribute(\
					item_id = item.id,\
					attribute_name = "prepicked",\
					attribute_value = prepicked_value)
		dbsession.add(attribute)

	dbsession.commit()

	return redirect("/profile")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	"""If not using Amazon S3, the photos would be saved here.
	"""
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/harvest')
def harvest():
	"""This route is where the user can search for items to trade.
	"""
	return render_template("harvest.html", key=key)
 
@app.route('/harvest-filter')
def filter():
	"""This returns a list of items based on how the user filters.

	The user can filter within a specified radius, and can filter by attribute of the 
	items. The list of filtered items will display one by one on the harvest page. They 
	are returned as a json string.
	"""
	veggie = request.args.get('Veggie')
	other = request.args.get('Other')
	fruit = request.args.get('Fruit')
	checked_prepicked = request.args.get('Prepicked')
	checked_gift = request.args.get('Gift')

	# base query of all items by date added 
	query = dbsession.query(Item).order_by(Item.date_item_added)
	#filter out all of user's items
	query = query.filter(Item.user_id != current_user.id)
	#don't show items user has already seen 
	viewed_items = dbsession.query(ItemViewed).filter_by(viewer_id = current_user.id).all()
	if viewed_items:
		viewed_item_ids = []
		for viewed_item in viewed_items:
			viewed_item_ids.append(viewed_item.item_id)
		print "item ids", viewed_item_ids
		query = query.filter(~Item.id.in_(viewed_item_ids))
	#filter depending on what the user specified 
	forv_list = []
	if veggie:
		forv_list.append('veggie')
	if fruit:
		forv_list.append('fruit')
	if other:
		forv_list.append('other')

	if checked_gift:
		query = query.filter(exists().where(ItemAttribute.item_id == Item.id)
                                     .where(ItemAttribute.attribute_name=='gift')
                                     .where(ItemAttribute.attribute_value=='yes')
                                     )

	if checked_prepicked:
		query = query.filter(exists().where(ItemAttribute.item_id == Item.id)
                                     .where(ItemAttribute.attribute_name=='prepicked')
                                     .where(ItemAttribute.attribute_value=='yes')
                                     )

	if forv_list:
		query = query.filter(exists().where(ItemAttribute.item_id == Item.id)
	                                 .where(ItemAttribute.attribute_name=='forv')
	                                 .where(ItemAttribute.attribute_value.in_(forv_list))
	                                 )
	#filter out all closed items
	query = query.filter(exists().where(ItemAttribute.item_id==Item.id)
								 .where(ItemAttribute.attribute_name=='status')
								 .where(ItemAttribute.attribute_value=='open')
									)			

	harvest_items = query.all()

	to_filter = [ {'id': f.id, 'photo': f.photo_path, 'description': f.description, 'latitude': f.user.latitude, 'longitude':f.user.longitude} for f in harvest_items] 

	#R is the earth's radius
	R = 6373.0

	user_longitude = current_user.longitude
	user_latitude = current_user.latitude
	lat2 = radians(user_latitude)
	lon2 = radians(user_longitude)

	distance = request.args.get('distance')
	distance = distance.split()
	miles_desired = int(distance[0])

	to_return = []

	#geocoding equation from: http://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude-python 
	for item in to_filter:
		item_latitude = (item['latitude'])
		item_longitude = (item['longitude'])

		lat1 = radians(item_latitude)
		lon1 = radians(item_longitude)

		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		distance = R * c
		distance_miles = distance*0.621371
		if distance_miles<=miles_desired:
			to_return.append(item)

	return json.dumps(to_return)

@app.route('/decision_no/<item_id>')
def vote_no(item_id):  
	"""Route if decision is 'no' to an item.

	The item is added to the viewed items table in the database
	"""
	viewed_item = ItemViewed(decision="no", item_id=item_id, viewer_id=current_user.id, date_viewed=datetime.datetime.now())
	dbsession.add(viewed_item)
	dbsession.commit()
	return ""

@app.route('/decision/<item_id>')
def vote_yes(item_id):
	"""Route if decision is 'yes' to an item.

	Checks if there is a match, and returns a json message to the current user. 
	Either an empty string if there is not a match, or a success message if 
	there is a match with the user of the item the current user said yes to.
	"""
	#set message to empty string
	message = ""
	#add item to the database as a viewed item
	viewed_item = ItemViewed(decision="yes", item_id=item_id, viewer_id=current_user.id, date_viewed=datetime.datetime.now())
	dbsession.add(viewed_item)
	dbsession.commit()

	item_interested = dbsession.query(Item).filter_by(id=item_id).first()
	#all items of the harvestee
	harvestee_items = item_interested.user.items
	#the ids of the harvestee's items 
	harvestee_item_ids = [i.id for i in harvestee_items]
	#all items of current user
	current_user_items = current_user.items
	#item ids of current user's items
	current_user_item_ids = [i.id for i in current_user_items]
	#all match offer items of the current user
	current_user_matchoffer_items = dbsession.query(MatchOfferItem).filter(MatchOfferItem.item_id.in_(current_user_item_ids)).all()
	
	found = False

	gift = dbsession.query(ItemAttribute).filter_by(item_id=item_interested.id).filter_by(attribute_name="gift").filter_by(attribute_value="yes").first()
	if gift:
		match_offer=MatchOffer(date_of_match=datetime.datetime.now())
		message = "SUCCESSFUL HARVEST! Congratulations, you have a match. You will receive an email notification shortly with your match's contact info!"
		#email both users that they have a match 
		user1_email = current_user.email
		user2 = dbsession.query(User).filter_by(id=item_interested.user_id).one()
		user2_email = user2.email
		msg = Message("You have a match!", sender='harvestrswap@gmail.com', recipients=[user1_email, user2_email])
		msg.body = "Greetings %s, and %s! Congrats! You are a match. I'll leave it to you to take it from here and swap your items! Thanks for using Harvestr to find some yummy food and eliminate food waste." % (current_user.name, user2.name)
		mail.send(msg)
		dbsession.add(match_offer)
		dbsession.commit()
		match_offer_copy = dbsession.query(MatchOffer).filter_by(date_of_match=match_offer.date_of_match).first()
		match_offer_items = MatchOfferItem(item_id=item_interested.id, match_offer_id=match_offer_copy.id, user_id=current_user.id)
		dbsession.add(match_offer_items)
		found = True
	# if current_user and harvestee have no common match offers already, found = false
	

	#if current user has any match offers already
	if not found and current_user_matchoffer_items:	
		#get the MOI ids for the current user
		current_user_matchoffer_item_ids = [i.match_offer_id for i in current_user_matchoffer_items]
		#what are the match offers harvestee
		harvestee_matchoffer_items = dbsession.query(MatchOfferItem).filter(MatchOfferItem.item_id.in_(harvestee_item_ids)).all()

		if harvestee_matchoffer_items:
			harvestee_matchoffer_item_ids = [i.match_offer_id for i in harvestee_matchoffer_items]
			#the common matches between the current user and the harvestee
			common_matches = set(harvestee_matchoffer_item_ids) & set(current_user_matchoffer_item_ids)

			if common_matches:
				common_matches = list(common_matches)
				first_common_match = common_matches[0]
				match_offer = dbsession.query(MatchOffer).filter_by(id=first_common_match).one()
				## match_offer = first_common_match.match_offer
				match_offer_item=dbsession.query(MatchOfferItem).filter_by(match_offer_id=match_offer.id).first()
				first_user_id = match_offer_item.user_id
				if first_user_id != current_user.id:
					match_offer.date_of_match = datetime.datetime.now()
					message = "SUCCESSFUL HARVEST! Congratulations, you have a match. You will receive an email notification shortly!"
					user1_email = current_user.email
					user2 = dbsession.query(User).filter_by(id=item_interested.user_id).one()
					user2_email = user2.email
					msg = Message("You have a match!", sender='harvestrswap@gmail.com', recipients=[user1_email, user2_email])
					msg.body = "Greetings %s, and %s! Congrats! You are a match. I'll leave it to you to take it from here and swap your items! Thanks for using Harvestr to find some yummy food and eliminate food waste." % (current_user.name, user2.name)
					mail.send(msg)
					found = True

	# else: if harvestee has not liked anything from current_user yet...
	if not found:
		random_item_from_user = dbsession.query(Item).filter_by(user_id=current_user.id).first()
		if random_item_from_user:
			match_offer = MatchOffer()
			dbsession.add(match_offer)
			dbsession.commit()
			match_offer_item1 = MatchOfferItem(item_id=item_interested.id, match_offer_id=match_offer.id, user_id=current_user.id)
			match_offer_item2 = MatchOfferItem(item_id=random_item_from_user.id, match_offer_id=match_offer.id, user_id=current_user.id)
			dbsession.add(match_offer_item1)
			dbsession.add(match_offer_item2)

	dbsession.commit()
	return json.dumps({"message": message})



if __name__ == '__main__':
	PORT = int(os.environ.get(“PORT”, 5000))
	app.run(debug=True, host=“0.0.0.0”, port=PORT)





