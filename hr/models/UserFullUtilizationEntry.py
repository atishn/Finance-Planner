import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro,money_formatted,quarterly_money,utilization_per_month

class UserFullUtilizationEntry(object):
    
    percentage = 0
    client = None
    ghost_client = None
    
    def __init__(self,client,percentage,ghost_client=None):
        self.client = client
        self.percentage = percentage
        self.ghost_client = ghost_client
        
