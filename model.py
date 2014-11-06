from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore


engine = create_engine("postgres://localhost:5432/harvester", echo=False)
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
	facebook_id = Column(String(100), nullable = True)
	email = Column(String(100), nullable = False)
	latitude = Column(Float, nullable = False)
	longitude = Column(Float, nullable = False)
	last_log_in = Column(DateTime, nullable = False)

# #these are the matches, connects two items which belong to two different users, once user1 and user2 approves, 
# #there will be a pop up that says "theres a match! and an email to both users"
# class Match_Offer(Base):
# 	__tablename__= "match_offers"
# 	id = Column(Integer, primary_key = True)
# 	item_id_one = Column(Integer, ForeignKey('items.id'))
# 	item_id_two = Column(Integer, ForeignKey('items.id'))
# 	user_one_approves = Column(Boolean, nullable = False)
# 	user_two_approves = Column(Boolean, nullable = False)
# 	date_of_match = Column(DateTime, nullable = False)

# 	#specified which column the foreign key is talking to by saying foreign key = item1 or item2
# 	item_one = relationship("Item", backref=backref("match_offers", order_by=id), foreign_keys=[item_id_one])
# 	item_two = relationship("Item", backref=backref("match_offers", order_by=id), foreign_keys=[item_id_two])

# #these are the messages where the author is a user and a match id will show which two items it matches
# class Message(Base):
# 	__tablename__="messages"
# 	id = Column(Integer, primary_key = True)
# 	author_id = Column(Integer, ForeignKey('users.id'))
# 	match_id = Column(Integer, ForeignKey('match_offers.id'))
# 	message_content = Column(String(1000), nullable = False)

# 	author = relationship("User", backref=backref("messages", order_by=id))
# 	match_offer = relationship("Match_Offer", backref=backref("messages", order_by=id))

# #here are the items. each item is either available(T) or not (F), this will be a field that the user can control
# class Item(Base):
# 	__tablename__="items"
# 	id = Column(Integer, primary_key = True)
# 	user_id = Column(Integer, ForeignKey('users.id'))
# 	available = Column(Boolean, nullable = True)
# 	#how to I store a photo with the path?
# 	#text==varchar???
# 	photo_path = Column(String(100), nullable = False)
# 	description = Column(String(140), nullable = False) 
# 	date_item_added = Column(DateTime, nullable = False)

# 	user = relationship("User", backref=backref("items", order_by=id))

# #here are the possible attributes. e.g.: fruit, gift, 
# class Attribute(Base):
# 	__tablename__="attributes"
# 	id = Column(Integer, primary_key = True)
# 	attribute_type = Column(String(100), nullable = False)

# class ItemAttribute(Base):
# 	__tablename__="itemsattributes"
# 	id = Column(Integer, primary_key = True)
# 	item_id = Column(Integer, ForeignKey('items.id'))
# 	attribute_id = Column(Integer, ForeignKey('attributes.id'))

# 	attribute_type = relationship("Attribute", backref=backref("itemsattributes", order_by=id))
# 	item = relationship("Item", backref=backref("itemsattributes", order_by=id))
# 	#find acutal attribute and item

	# def gift():
	# 	#this function will see if the item is a gift, if it is, then the match 
		#offer field will be marked as the user approves to start with

if __name__ == "__main__":
	Base.metadata.create_all(engine)
