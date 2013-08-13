from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.OfficeFinancials import OfficeFinancials
from hr.models.OfficeUtilization import OfficeUtilization

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer,ForeignKey('account.id'),nullable=False)
    name = Column(Unicode(3),nullable=False)
    currency_to_usd = Column(Float,nullable=False)

    users = relationship('User',backref='currency')

    def __init__(self,name,account,currency_to_usd):
        self.name = name.lower()
        self.account = account
        self.currency_to_usd = currency_to_usd
    
    def _usd_to_currency(self):
        return 1/self.currency_to_usd
    
    usd_to_currency = property(_usd_to_currency)