Harvestr
========

####Project Description
Hoping to reduce food waste, Harvestr connects people with a surplus of backyard produce.  Ten lemons for a bag of tomatoes, for example, or a bushel of kale for a pound of garlic. Users post fruits or veggies they want to trade, then specify what they want and a radius to search within. On this Tinder-style webapp, users swipe through potential trades, marking “yes” when they see something they want and “no” if they aren't interested. When there's a match, both users are notified via email.

This webapp is also for those who are interested in the sharing economy who may not have gardens. Those who have items may choose to "gift" their item, meaning they are not looking to trade, but rather to give their item away for free. Others can then search for "gifts", and the "gifted" items will show up in their search. 

####Table of Contents
- [How it works] (#how-it-works)
- [Technologies Used] (#technologies-used)
- [Run Harvestr on your computer] (#run-harvestr-on-your-computer)

####How it works:
####1. Login With Facebook
![Login With Facebook](/static/images/screenshot1.jpg)
####2. View your profile
![View your profile](/static/images/screenshot2.jpg)
![View your items](/static/images/screenshot3.jpg)
####3. Using the navbar, go to Edit your profile to change your location, add items, or change your item's attributes
![Edit items](/static/images/screenshot4.jpg)
####4. Using the navbar, Go to the Harvest Page where you can filter what you would like to search for
![Harvest items](/static/images/screenshot6.jpg)
####5. Items that meet your search criteria will show up one at a time as you vote "nope" (I would not trade one of my items for this item) or "like" (I would trade one of my items for this item).
![Edit items](/static/images/screenshot7.jpg)
####6. If there is a match, you will see this message
![Edit items](/static/images/screenshot9.jpg)
####7. and both users will an email like this:
![Edit items](/static/images/screenshot11.jpg)

####Technologies used:

Python, Flask, JavaScript, HTML5, CSS3, jQuery, Postgresql, SQLAlchemy, Amazon S3, boto, Google Maps API, Gmail's SMTP, Oauth, Flask-Login, Authomatic 


####Run Harvestr on your computer:

####Environment

1) Clone the repository:
<pre><code>$ git clone https://github.com/annaakullian/Harvestr.git</code></pre>

2) Create and activate a virtual environment in the same directory:
<pre><code>$ virtualenv env
$ . env/bin/activate
</code></pre>

3) Install the required packages 
<pre><code>(env)$ pip isntall -r requirements.txt </code></pre>

####Database and Python Installations

1) Download and run postgres server

2) Create the databse in PostgreSQL by running the generatedb.sh script. This will seed your database with data from a couple of sample users.
<pre><code>(env)$ ./generatedb.sh </code></pre>

3) Install Python 2.7

####Acess Keys:

1) Get access keys for the following variables and write the following code:
<pre><code>(env)$ export GOOGLE_MAPS_EMBED_KEY = [your google maps key]<br/>
(env)$ export FACEBOOK_SECRET = [your facebook secret key]<br/>
(env)$ export FACEBOOK_ID=[your facebook id]<br/>
(env)$ export DATABASE_URL=[your postgres database url]<br/>
(env)$ export MAIL_PASSWORD=[your gmail password]<br/>
(env)$ export AWS_ACCESS_KEY_ID=[your amazon web service access key id]<br/>
(env)$ export AWS_SECRET_ACCESS_KEY=[your amazon web service secret access key]<br/>
(env)$ export MY_BUCKET=[the name of your amazon s3 bucket]<br/>
</code></pre>

####Run the app:

1) Write the following:
<pre><code>(env)$ python swap.py</code></pre>

2) Point your browser to:
<pre><code>http://localhost:5000/</code></pre>
