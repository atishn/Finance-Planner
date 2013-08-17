from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro, money_formatted, quarterly_money
from hr.models.DepartmentUtilization import DepartmentUtilization


class GlobalDepartmentUtilization(object):
    account = None
    year = 0

    department_utilization = []

    def __init__(self, account, year):
        self.year = year
        self.account = account

        self.calculateUtilization()

    def initializeVariables(self):
        self.department_utilization = []


    def calculateUtilization(self):
        self.initializeVariables()

        for department in self.account.departments:
            department_util = DepartmentUtilization(department, self.year)
            self.department_utilization.append(department_util)
