import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro,money_formatted
from hr.models.ClientFinancials import ClientFinancials
from hr.models.ClientUtilization import ClientUtilization

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)
    
    account_id = Column(Integer,ForeignKey('account.id'),nullable=False)
    office_id = Column(Integer,ForeignKey('office.id'),nullable=False)
    
    name = Column(Unicode(40),nullable=False)
    
    projects = relationship('Project',backref='client')
    ghost_projects = relationship('GhostProject',backref='client')
    team = relationship('UserAllocation',backref='client')
    freelancers = relationship('Freelancer',backref='client')
    ghost_team = relationship('GhostAllocation',backref='client')
    
    actual_expenses = relationship('ActualExpense',backref='client')
        
    def __init__(self,name,office):
        self.name = name.lower()
        self.office = office
        self.is_active = True
        self.created_at = db_utc_now()
        self.account_id = office.account_id
    
    def getFinancials(self,year,user):
        return ClientFinancials(self,year,user)
        
    def getUtilization(self,year):
        return ClientUtilization(self,year)