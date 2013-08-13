import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro,money_formatted

class GhostAllocation(Base):
    __tablename__ = 'ghost_allocation'
    id = Column(Integer, primary_key=True)
    
    ghost_user_id = Column(Integer,ForeignKey('ghost_user.id'))
    client_id = Column(Integer,ForeignKey('client.id'))
    ghost_client_id = Column(Integer,ForeignKey('ghost_client.id'))
    utilization = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    def __init__(self,ghost_user,client,ghost_client,utilization,start_date,end_date):
        self.ghost_user = ghost_user
        self.client = client
        self.ghost_client = ghost_client
        self.utilization = utilization
        self.start_date = start_date
        self.end_date = end_date
