import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    
    review_id = Column(Integer,ForeignKey('review.id'))
    text = Column(UnicodeText, nullable = True)
    
    user_id = Column(Integer,ForeignKey('user.id'),nullable=False)
    
    feedback_accepted = Column(Boolean,nullable=True)
    
    def __init__(self,review,user):
        self.review = review
        self.user = user
        self.created_at = db_utc_now()