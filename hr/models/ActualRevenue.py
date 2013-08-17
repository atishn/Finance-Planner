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


class ActualRevenue(Base):
    __tablename__ = 'actual_revenue'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    revenue = Column(Integer, nullable=False)
    quarter_end_date = Column(DateTime, nullable=False)

    def __init__(self, project, revenue, quarter_end_date):
        self.project = project
        self.revenue = revenue
        self.quarter_end_date = quarter_end_date
    