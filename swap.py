from flask import Flask, render_template, request, session, flash, redirect, Markup, url_for, send_from_directory, make_response, jsonify
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
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from sqlalchemy.sql import exists
from math import sin, cos, sqrt, atan2, radians
import datetime 
from flask.ext.mail import Mail, Message
from authomatic_config import AUTHOMATIC_CONFIG

DEBUG = True
SECRET_KEY = 'hidden'
USERNAME = 'harvestr.swap@gmail.com'
PASSWORD = 'harvestrharvestr'

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_TLS = False
MAIL_USE_SSL= True
MAIL_USERNAME = 'harvestrswap@gmail.com'
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") 

app =  Flask(__name__)
app.secret_key="annabanana"
app.config.from_object(__name__)
mail = Mail(app)



#this is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'gif', 'png', 'pdf', 'txt'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#set up flask login manager and authomatic helpers

login_manager = LoginManager()
login_manager.init_app(app)
authomatic = Authomatic(AUTHOMATIC_CONFIG, 'your secret string', report_errors=False)


key = os.environ.get("GOOGLE_MAPS_EMBED_KEY")


#this is the home pagef
@app.route('/')
def home_page():
	# user = dbsession.query(User).first()
	return render_template("home.html")

@app.route('/test')
def test():
	return render_template("test.html")

@app.route('/matchopenitems', methods=['GET'])
def matchopenitems():
	user_id = request.args.get("user_id")
	user = dbsession.query(User).filter_by(id=user_id).one()
	user_items = user.items
	return render_template("matchopenitems.html", user_items=user_items)

# Login route for all OAuth providers. If one were to add a second provider 
# (i.e. Twitter, Google), more logic could be added to this method by
# # checkingthe "provider_name" variable

@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
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

# Clear our session, logging the user out and returning them
# to the home page.
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

# flask-login required method
# Tell flask-login how to find the current user in the database
@login_manager.user_loader
def load_user(id):
	return dbsession.query(User).filter_by(id = id).first()


@app.route('/howitworks')
def how_it_works():
	return render_template("howitworks.html")

# @app.route('/signup', methods=['GET'])
# def sign_up():
# 	return render_template("signup.html")

#next put flash in template!!
# @app.route('/signup', methods=['POST'])
# def process_new_user():
# 	user_location = request.form['user_location']
# 	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?sensor=false&key=AIzaSyDjesZT-7Vc5qErTJjS2tDIvxLQdYBxOEY&address=" +\
# 		request.form['user_location'])
# 	user_latitude = r.json()['results'][0]['geometry']['location']['lat']
# 	user_longitude = r.json()['results'][0]['geometry']['location']['lng']
# 	user_email = request.form['user_email']
# 	facebookid = request.form['facebookid']
# 	user_name = request.form['user_name']
# 	password = request.form['password']
# 	user = User(latitude = user_latitude, longitude=user_longitude, facebookid=facebookid, name=user_name, email = user_email, password=password, location=user_location)
# 	if dbsession.query(User).filter_by(email = user_email).first():
# 		flash("That email is taken. If you are already a harvester, log in here!"+ Markup("<h1><a href='/loginfb'>Login</a></h1>"))
# 		return redirect('/signup')
# 	else:
# 		dbsession.add(user)
#     	dbsession.commit()
#     	session['user_id'] = user.id
#     	return redirect("/profile")

# @app.route('/login', methods=['GET'])
# def login():
# 	return render_template("login.html")


# @app.route('/login', methods=['POST'])	
# def process_login():
# 	user_email = request.form['user_email']
# 	password = request.form['password']

# 	user = dbsession.query(User).filter_by(password=password).filter_by(email=user_email).first()
# 	if user:
# 		session['user_id'] = user.id
# 		# session['user'] = { 'name': user.name, 'email': user.email, 'location': user.location, 'facebookid': user.facebookid, 'latitude': user.latitude, 'longitude': user.longitude }
# 		return redirect("/profile") 
# 	else:
# 		flash("That user was not recognized. Please try again, or create an account here:"+ Markup("<h1><a href='/signup'>Signup</a></h1>"))
# 		return redirect("/login")

@app.route('/profile')	
def profile():
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
						# item = match_item.item_id
						match_items.append(item)

	# user = dbsession.query(User).get(session['user_id'])
	# item_dictionary = item_dictionary
	return render_template("profile.html", match_items=match_items)

@app.route('/alluserimages', methods=['GET'])	
def allimages():
	# user = dbsession.query(User).first()
	# user = dbsession.query(User).get(session['user_id'])
	return render_template("alluserimages.html")

@app.route('/editprofile', methods=['GET'])
def editprofile():
	# user = dbsession.query(User).get(session['user_id'])
	print "Current user", current_user
	print "Current location", current_user.location
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
	# user = dbsession.query(User).get(session['user_id'])
	# user_email = request.form['user_email']

	# if user.email != user_email:
	# 	flash("email change not allowed")
	# 	return redirect(url_for('editprofile'))

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

	current_user.name = user_name
	current_user.latitude = user_latitude
	current_user.longitude = user_longitude
	# current_user.email = user_email
	current_user.location = user_location
	# dbsession.commit()

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
		#one instead of first because there is only one item by the unique id
		item = dbsession.query(Item).filter_by(id=photo_id).one()
		item.description = item_description
		# dbsession.commit()

	#print "\n\n\n\n\n\n\n\nITEM",request.form

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
			#if key == "forv":
			attribute = dbsession.query(ItemAttribute).filter_by(item_id=photo_id).filter_by(attribute_name=key).first()
			if attribute is None:
				attribute = ItemAttribute(\
					item_id = photo_id,\
					attribute_name = key,\
					attribute_value = value)
				dbsession.add(attribute)
			else:
				attribute.attribute_value = value
			# dbsession.commit()


	uploaded_files = request.files.getlist("file[]")

	new_forvs = request.form.getlist("forv_new[]")
	new_status = request.form.getlist("status_new[]")
	new_gift = request.form.getlist("gift_new[]")
	new_prepicked = request.form.getlist("prepicked_new[]")
	new_description = request.form.getlist("description_new[]")
	filenames = []

	for i in range(len(uploaded_files)):
		# print "\n\n\n\n\n\n\n\n\n\n",i, new_description, new_forvs
		if uploaded_files[i].filename == '':
			continue
		# if file and allowed_file(file.filename):
		filename = secure_filename(uploaded_files[i].filename)
		filedata = uploaded_files[i].stream.read()
		hash_id = hashlib.md5(filedata).hexdigest()
		file_path = "/static/uploads/%s" % filename 
		if dbsession.query(Item).filter_by(hash_id=hash_id).first():
			flash("This photo already exists! You can edit the information on your current photo")
			return redirect(url_for('editprofile'))
		else:
			uploaded_files[i].stream.seek(0)
			uploaded_files[i].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			filenames.append(filename)
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
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/harvest')
def harvest():
	return render_template("harvest.html", key=key)

# /harvest-filter?veggie=veggie&fruit=fruit     
@app.route('/harvest-filter')
def filter():
	veggie = request.args.get('Veggie')
	other = request.args.get('Other')
	fruit = request.args.get('Fruit')
	checked_prepicked = request.args.get('Prepicked')
	checked_gift = request.args.get('Gift')

	# base query of all items by date added  (FIXME: reverse)
	query = dbsession.query(Item).order_by(Item.date_item_added)
	# print len(query.all())
	# ... but not things we offer
	query = query.filter(Item.user_id != current_user.id)

	# query = query.filter(ViewedItem.viewer_id = current_user.id)

	viewed_items = dbsession.query(ItemViewed).filter_by(viewer_id = current_user.id).all()
	print "VIEWED", viewed_items
	if viewed_items:
		viewed_item_ids = []
		for viewed_item in viewed_items:
			viewed_item_ids.append(viewed_item.item_id)
		print "item ids", viewed_item_ids
		query = query.filter(~Item.id.in_(viewed_item_ids))


	#dont show items that the user has already said "yes" or "no" to
	#i want to filter out all of the items 
	#query = query.filter()
	##create a new database called "viewed items". that has a backref: viewers + items viewed 


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
	# TODO: add filter for distance
	harvest_items = query.all()
	# fruits = [ Fruit(name=n, color=c), Fruit(name=n, color=c) ]
	# stuff_to_return = [ {'name': f.name, 'color': f.color } for f in fruits ]
	# stuff_to_return == [ { 'name': f1n, 'color': f1c }, { 'name': f2n, 'color': f2c } ]
	# turn that into json
	to_filter = [ {'id': f.id, 'photo': f.photo_path, 'description': f.description, 'latitude': f.user.latitude, 'longitude':f.user.longitude} for f in harvest_items] 

	#radians?
	R = 6373.0

	user_longitude = current_user.longitude
	user_latitude = current_user.latitude
	lat2 = radians(user_latitude)
	lon2 = radians(user_longitude)

	distance = request.args.get('distance')
	distance = distance.split()
	miles_desired = int(distance[0])

	to_return = []

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
	# print to_return

	# json.dumps(to_return)
	# print len(query.all())
	print "ITEMS", [i['id'] for i in to_return]
	return json.dumps(to_return)
	#distance=1+mile&fruit=

	# return render_template("harvest-result.html", to_return = to_return) 

@app.route('/decision_no/<item_id>')
def vote_no(item_id):  #, current_user_id
	#add item to the database as a viewed item
	viewed_item = ItemViewed(decision="no", item_id=item_id, viewer_id=current_user.id, date_viewed=datetime.datetime.now())
	dbsession.add(viewed_item)
	dbsession.commit()
	return ""

@app.route('/decision/<item_id>')
def vote_yes(item_id):  #, current_user_id
	#harvestee = person whose item current user is interested in
	# current_user  = dbsession.query(User).filter_by(id=current_user_id).one()
	#the item that the current user is interested in. 

	#add item to the database as a viewed item
	message = ""
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
	#if current_user and harvestee have no common match offers already, found = false
	

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
	
    

		# user = joel
		# item = voting-yes-on-this-item (anna's pears)

	    # step2: no, so make an offer
	    # insert into mo:
	    #     null date
	    # insert into moi:
	    #     m.oid, item (pears)
	    #     m.oid, item (random thing of joel)
	    # (and now we wait for anna to offer to joel) 
	
	#the owner of the interested item
	# harvestee = item_interested.user_id 
	# #all harvestee items
	# user_intersted_items = dbsession.query(Item).filter_by(user_id = harvestee.id).all()


	# harvestee_item_ids = []
	# for item in harvestee_items:
	# 	user_intersted_item_ids.append(item.id)


	# current_user_items = dbsession.query(Item).filter_by(user_id=current_user.id)
	

	# current_user_item_ids = []
	# for item in current_user_items:
	# 	current_user_item_ids.append(item.id)

	## same could use list comp here

	#first scenario: user likes an item, and the owner of that items
	#has liked one of the current users items
	
	# item = voting-yes-on-this-item (joels figs)
	# step1: has anna offered anything to joel already?
	# find all moi's where owner-of-item (joel) 
	#    and m.oid in (moi.oid with any item-belonging-to-anna)


	#   (ie joel liked something of anna's and now she likes something of his)
    # if so, it's a match!
    # pick first of those matches and 
    # put mo.date-of-match to now
    # match_offer = MatchOffer()



if __name__ == '__main__':
	app.run(debug=True)

