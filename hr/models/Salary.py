from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro, money_formatted


class Salary(Base):
    __tablename__ = 'salary'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    salary = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    percent_billable = Column(Integer, nullable=False)

    def __init__(self, user, salary, start_date, percent_billable=100):
        self.user = user
        self.salary = salary
        self.start_date = start_date
        self.percent_billable = percent_billable
