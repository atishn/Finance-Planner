from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro, money_formatted, quarterly_money, utilization_per_month


class UserFullUtilization(object):
    name = None
    role = None
    id = 0
    jan = []
    feb = []
    mar = []
    apr = []
    may = []
    jun = []
    jul = []
    aug = []
    sep = []
    oct = []
    nov = []
    dec = []
    utilization = [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]

    def __init__(self, name, role, id):
        self.name = name
        self.role = role
        self.id = id
        self.calculateUtilization()

    def initializeVariables(self):
        self.jan = []
        self.feb = []
        self.mar = []
        self.apr = []
        self.may = []
        self.jun = []
        self.jul = []
        self.aug = []
        self.sep = []
        self.oct = []
        self.nov = []
        self.dec = []
        self.utilization = [self.jan, self.feb, self.mar, self.apr, self.may, self.jun, self.jul, self.aug, self.sep,
                            self.oct, self.nov, self.dec]

    def calculateUtilization(self):
        self.initializeVariables()
     