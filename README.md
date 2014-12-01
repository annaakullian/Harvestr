Harvestr
========

Hoping to reduce food waste, Harvestr connects people with a surplus of backyard produce.  Ten lemons for a bag of tomatoes, for example, or a bushel of kale for a pound of garlic. Users post fruits or veggies they want to trade, then specify what they want and a radius to search within. On this Tinder-style webapp, users swipe through potential trades, marking “yes” when they see something they want and “no” if they aren't interested. When there's a match, both users are notified via email.

How to run Harvestr on your computer:

1. Make sure you have postgres and python 2.7 installed 

2. Clone this repo

3. I recommend creating a virtual environment

4. get access keys for the following variables and write the following code:


export GOOGLE_MAPS_EMBED_KEY = [your google maps key]<br/>
export FACEBOOK_SECRET = [your facebook secret key]<br/>
export FACEBOOK_ID=[your facebook id]<br/>
export DATABASE_URL=[your postgres database url]<br/>
export MAIL_PASSWORD=[your gmail password]<br/>
export AWS_ACCESS_KEY_ID=[your amazon web service access key id]<br/>
export AWS_SECRET_ACCESS_KEY=[your amazon web service secret access key]<br/>
export MY_BUCKET=[the name of your amazon s3 bucket]<br/>
  
5. Write the following code:

pip install -r requirements.txt
./generatedb.sh
python swap.py 
