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


class ActualExpense(Base):
    __tablename__ = 'actual_expense'
    id = Column(Integer, primary_key=True)
    office_id = Column(Integer, ForeignKey('office.id'))
    client_id = Column(Integer, ForeignKey('client.id'))
    expense_local = Column(Integer)
    expense_global = Column(Integer)
    quarter_end_date = Column(DateTime, nullable=False)

    def __init__(self, office, client, expense_local, expense_global, quarter_end_date):
        self.office = office
        self.client = client
        self.expense_local = expense_local
        self.expense_global = expense_global
        self.quarter_end_date = quarter_end_date
