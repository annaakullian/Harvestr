from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


engine = create_engine("postgres://localhost:5432/harvester", echo=False)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))
Base = declarative_base()
Base.query = session.query_property()

class User(Base):
	__tablename__= "users"

	id = Column(Integer, primary_key = True) 

def create_tables():
	Base.metadata.create_all(engine)

if __name__ == "__main__":
	main()
	Base.metadata.create_all(engine)
