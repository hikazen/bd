import datetime
from passlib.hash import bcrypt

from sqlalchemy import (Column, Integer, String, Text, DateTime, create_engine, ForeignKey)
import sqlalchemy

from sqlalchemy.orm import sessionmaker, relationship, declarative_base


DATABASE_URL = 'sqlite:///./test.db'


Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())
    


class Post(AbstractBase):
    __tablename__ = 'posts'

    title = Column(String(length=255),index=True)
    text = Column(Text)
    
    user = relationship('User', back_populates='posts')
    user_id = Column(Integer, ForeignKey('users.id'))


class User(AbstractBase):
    __tablename__ = 'users'

    email = Column(String(length=255),unique=True)
    first_name = Column(String(length=255), nullable=True, default=None)
    last_name = Column(String(length=255), nullable=True, default=None)
    hashed_password = Column(String)

    posts = relationship('Post', back_populates='user')

    def verify_password(self, plain_password):
        return bcrypt(plain_password, self.hashed_password)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


