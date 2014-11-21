from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


engine = create_engine("postgres://localhost:5432/harvester", echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))
Base = declarative_base()
Base.query = session.query_property()

#these are the users. i will have to figure out how to save lat and long correctly
class User(Base):
	__tablename__= "users"

	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = True)
	facebookid = Column(String(100), nullable = True)
	email = Column(String(100), nullable = True)
	location = Column(String(100), nullable=True)
	latitude = Column(Float, nullable = True)
	longitude = Column(Float, nullable = True)
	last_log_in = Column(DateTime, nullable = True)

	# flask-login required methods for validating a user
	# ==================================================

	# Check if a user is "active" (i.e. hasn't deleted their account)
	def is_active(self):
		return True

	# Tell flask-login how to find our user id
	def get_id(self):
		return self.id

	# Check if a user is logged in (True for our main User object)
	def is_authenticated(self):
		return True

	# Check if a user is logged out (False for all User objects)
	def is_anonymous(self):
		return False

#keeps track of all of the items a user has seen, whether or not they say "yes" or "no" to it
class ItemViewed(Base):
	__tablename__="itemsviewed"

	id = Column(Integer, primary_key = True)
	item_id = Column(Integer, ForeignKey('items.id'))
	viewer_id = Column(Integer, ForeignKey('users.id'))
	decision = Column(String(100), nullable = True)
	date_viewed = Column(DateTime, nullable = True)

	item =  relationship("Item", backref=backref("itemsviewed", order_by=id))
	viewer = relationship("User", backref=backref("itemsviewed", order_by=id))


#here are the items. each item is either available(T) or not (F), this will be a field that the user can control
class Item(Base):
	__tablename__="items"
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('users.id'))
	# available = Column(Boolean, nullable = False)
	photo_path = Column(String(100), nullable = True)
	description = Column(String(140), nullable = True) 
	date_item_added = Column(DateTime, nullable = True)
	hash_id = Column(String(500), nullable = True)

	user = relationship("User", backref=backref("items", order_by=id))

# #here are the possible attributes. e.g.: fruit, gift, 
# class Attribute(Base):
# 	__tablename__="attributes"
# 	id = Column(Integer, primary_key = True)
#  	attribute_type = Column(String(100), nullable = True)
#  	attribute_value = Column(String(100), nullable = True)

class ItemAttribute(Base):
	__tablename__="itemsattributes"
	id = Column(Integer, primary_key = True)
	item_id = Column(Integer, ForeignKey('items.id'))
	attribute_name = Column(String(200), nullable = True)
	attribute_value = Column(String(200), nullable = True)

	# attribute_type = relationship("Attribute", backref=backref("itemsattributes", order_by=id))
	item = relationship("Item", backref=backref("itemsattributes", order_by=id))

# these are the matches, connects two items which belong to two different users, once user1 and user2 approves, 
# there will be a pop up that says "theres a match! and an email to both users"
class MatchOffer(Base):
	__tablename__= "match_offers"
	id = Column(Integer, primary_key = True)
	date_of_match = Column(DateTime, nullable = True)

#there will be two matchoffer ids that are the same for two matches
class MatchOfferItem(Base):
	__tablename__="match_offer_items"
	id =  Column(Integer, primary_key = True)
	match_offer_id = Column(Integer, ForeignKey('match_offers.id'))
	item_id = Column(Integer, ForeignKey('items.id'))
	user_id = Column(Integer, ForeignKey('users.id'))

	match_offer = relationship("MatchOffer", backref=backref("match_offer_items", order_by=id))
	item = relationship("Item", backref=backref("match_offer_items", order_by=id))
	user = relationship("User", backref=backref("match_offer_items", order_by=id))

# #these are the messages where the author is a user and a match id will show which two items it matches
class Message(Base):
	__tablename__="messages"
	id = Column(Integer, primary_key = True)
	match_offer_item_id = Column(Integer, ForeignKey('match_offer_items.id'))
	message_content = Column(String(1000), nullable = True)

	match_offer_item = relationship("MatchOfferItem", backref=backref("messages", order_by=id))


if __name__ == "__main__":
	Base.metadata.create_all(engine)
