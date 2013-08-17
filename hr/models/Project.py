from __future__ import division
import bcrypt, locale, datetime, traceback
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro, money_formatted


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)
    name = Column(Unicode(40), nullable=False)

    account_id = Column(Integer, ForeignKey('account.id'))
    client_id = Column(Integer, ForeignKey('client.id'))

    revenue = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    actual_revenues = relationship('ActualRevenue', backref='project')
    budget_allocations = relationship('BudgetAllocation', backref='project')

    def __init__(self, name, account, client, revenue, start_date, end_date):
        self.name = name.lower()
        self.client = client
        self.revenue = revenue
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = db_utc_now()
        self.account = account
        self.is_active = True

    def _number_of_days(self):
        difference = self.end_date - self.start_date
        return difference.days + 1

    number_of_days = property(_number_of_days)

    def _revenue_per_day(self):
        try:
            recognized_revenue = 0
            last_recognized_date = self.start_date
            if self.actual_revenues is None or self.actual_revenues == []:
                return self.revenue / self.number_of_days

            for actual in self.actual_revenues:
                recognized_revenue += actual.revenue
                if actual.quarter_end_date > self.start_date:
                    last_recognized_date = actual.quarter_end_date

            unrecognized_days = (self.end_date - last_recognized_date).days + 1

            rpd = (self.revenue - recognized_revenue) / unrecognized_days

            if rpd < 0:
                rpd = 0
            return rpd
        except:
            traceback.print_exc()

    revenue_per_day = property(_revenue_per_day)
