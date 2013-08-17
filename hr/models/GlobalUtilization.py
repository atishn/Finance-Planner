from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro, money_formatted, quarterly_money
from hr.models.OfficeUtilization import OfficeUtilization


class GlobalUtilization(object):
    account = None
    year = 0

    office_utilization = []

    def __init__(self, account, year):
        self.year = year
        self.account = account

        self.calculateUtilization()

    def initializeVariables(self):
        self.office_utilization = []


    def calculateUtilization(self):
        self.initializeVariables()

        for office in self.account.offices:
            office_util = OfficeUtilization(office, self.year)
            self.office_utilization.append(office_util)
            