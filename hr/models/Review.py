import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base

class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    
    user_id = Column(Integer,ForeignKey('user.id'),nullable=False)
    
    role_id = Column(Integer,ForeignKey('role.id'),nullable=False)
    role = relationship("Role",primaryjoin="Role.id==Review.role_id")
    
    next_role_id = Column(Integer,ForeignKey('role.id'),nullable=True)
    next_role = relationship("Role",primaryjoin="Role.id==Review.next_role_id")
    
    review_cycle_year = Column(Integer, nullable=True)

    midyear_review_date = Column(DateTime, nullable=True)
    midyear_visible_to_user = Column(Boolean,nullable=False)
    
    annual_review_date = Column(DateTime, nullable=True)
    annual_visible_to_user = Column(Boolean,nullable=False)
    annual_comp_date  = Column(DateTime, nullable=True)
    
    skillset_entries = relationship('SkillsetEntry',backref='review')
    
    feedback = relationship('Feedback',backref='review')
    
    self_assessment_goals = Column(UnicodeText, nullable = True)
    self_assessment_performance_midyear = Column(UnicodeText, nullable = True)
    self_assessment_performance_annual = Column(UnicodeText, nullable = True)

    general_midyear_comments = Column(UnicodeText, nullable = True)
    general_annual_comments = Column(UnicodeText, nullable = True)
   
    def __init__(self, user, review_cycle_year):
        self.role = user.role
        self.next_role = user.next_role
        self.review_cycle_year = review_cycle_year
        self.created_at = db_utc_now()
        self.midyear_closed = False
        self.annual_closed = False
        self.midyear_visible_to_user = False
        self.annual_visible_to_user = False
    
    def _current_datetime(self):
        return datetime.datetime.now()
        
    current_datetime = property(_current_datetime)
    