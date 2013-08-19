from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro, money_formatted, quarterly_start_date, quarterly_end_date, quarterly_money


class ProjectRevenue(object):
    project = None

    year = 0

    Q1 = 0
    Q2 = 0
    Q3 = 0
    Q4 = 0

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self, project, year):
        self.year = year
        self.project = project

        self.calculateRevenue()

    def calculateRevenue(self):
        revenue = quarterly_money(self.year, self.project.start_date, self.project.end_date,
                                  self.project.revenue_per_day)

        self.Q1 = revenue[0]
        self.Q2 = revenue[1]
        self.Q3 = revenue[2]
        self.Q4 = revenue[3]

    def _annual_revenue(self):
        return self.Q1 + self.Q2 + self.Q3 + self.Q4

    annual_revenue = property(_annual_revenue)