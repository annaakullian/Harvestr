Harvestr
========

####Project Description
Hoping to reduce food waste, Harvestr connects people with a surplus of backyard produce.  Ten lemons for a bag of tomatoes, for example, or a bushel of kale for a pound of garlic. Users post fruits or veggies they want to trade, then specify what they want and a radius to search within. On this Tinder-style webapp, users swipe through potential trades, marking “yes” when they see something they want and “no” if they aren't interested. When there's a match, both users are notified via email.

####Table of Contents
- [How itt works] (#how-it-works)
- [Technologies Used] (#technologies-used)
- [Run Harvestr on your computer] (#run-harvestr)

####Run Harvestr on your computer:

####Environment

1) Clone the repository:
<pre><code>$ git clone https://github.com/annaakullian/Harvestr.git</code></pre>

2) Create and activate a virutal environment in the same directory:
$ virtualenv env
$ . env/bin/activate
</code></pre>

3) Install the required packages 

####Database

1) Download and run postgres server
2) Create the databse in PostgreSQL by running the generatedb.sh script. This will seed your database with data from a couple of users.
<pre><code>$ ./generatedb.sh </code></pre>

1. Make sure you have postgres and python 2.7 installed 
2. Clone this repo
3. I recommend creating a virtual environment
4. get access keys for the following variables and write the following code:<br/>
export GOOGLE_MAPS_EMBED_KEY = [your google maps key]<br/>
export FACEBOOK_SECRET = [your facebook secret key]<br/>
export FACEBOOK_ID=[your facebook id]<br/>
export DATABASE_URL=[your postgres database url]<br/>
export MAIL_PASSWORD=[your gmail password]<br/>
export AWS_ACCESS_KEY_ID=[your amazon web service access key id]<br/>
export AWS_SECRET_ACCESS_KEY=[your amazon web service secret access key]<br/>
export MY_BUCKET=[the name of your amazon s3 bucket]<br/>
5.  Write the following code:
pip install -r requirements.txt
./generatedb.sh
python swap.py 

  
####How it works
