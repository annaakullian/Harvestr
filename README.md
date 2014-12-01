Harvestr
========

####Project Description
Hoping to reduce food waste, Harvestr connects people with a surplus of backyard produce.  Ten lemons for a bag of tomatoes, for example, or a bushel of kale for a pound of garlic. Users post fruits or veggies they want to trade, then specify what they want and a radius to search within. On this Tinder-style webapp, users swipe through potential trades, marking “yes” when they see something they want and “no” if they aren't interested. When there's a match, both users are notified via email.

####Table of Contents
- [How it works] (#how-it-works)
- [Technologies Used] (#technologies-used)
- [Run Harvestr on your computer] (#run-harvestr-on-your-computer)

####Run Harvestr on your computer:

####Environment

1) Clone the repository:
<pre><code>$ git clone https://github.com/annaakullian/Harvestr.git</code></pre>

2) Create and activate a virutal environment in the same directory:
<pre><code>
$ virtualenv env
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
<pre><code>
(env)$ export GOOGLE_MAPS_EMBED_KEY = [your google maps key]<br/>
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

  
####How it works
