import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.GlobalUtilization import GlobalUtilization
from hr.models.GlobalFinancials import GlobalFinancials
from hr.models.GlobalDepartmentUtilization import GlobalDepartmentUtilization
from hr.models.GlobalDepartmentFinancials import GlobalDepartmentFinancials


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)

    start_year = Column(Integer, nullable=True)

    name = Column(Unicode(40), nullable=False)

    midyear_review_start = Column(DateTime, nullable=True)
    midyear_review_setup_deadline = Column(DateTime, nullable=True)
    midyear_review_end_date = Column(DateTime, nullable=True)

    annual_review_start = Column(DateTime, nullable=True)
    annual_review_setup_deadline = Column(DateTime, nullable=True)
    annual_review_end_date = Column(DateTime, nullable=True)

    latest_review_year = Column(Integer, nullable=False)

    currencys = relationship('Currency', backref='account')
    departments = relationship('Department', backref='account')
    offices = relationship('Office', backref='account')
    users = relationship('User', backref='account')
    roles = relationship('Role', backref='account')
    clients = relationship('Client', backref='account')
    ghost_clients = relationship('GhostClient', backref='account')
    ghost_users = relationship('GhostUser', backref='account')
    ghost_projects = relationship('GhostProject', backref='account')
    projects = relationship('Project', backref='account')
    freelancers = relationship('Freelancer', backref='account')
    benefits_and_bonus = Column(Integer, nullable=False)

    def __init__(self, name, latest_review_year):
        self.latest_review_year = latest_review_year
        self.name = name.lower()
        self.created_at = db_utc_now()
        self.is_active = True
        self.benefits_and_bonus = 0
        self.start_year = int(str(datetime.datetime.now().year))

    def _years(self):
        years = []
        years.append(self.start_year)
        y_temp = 2012
        y_now = int(datetime.datetime.now().year)
        while y_temp <= y_now:
            y_temp = y_temp + 1
            years.append(str(y_temp))
        return years

    years = property(_years)

    def getFinancials(self, year, user):
        return GlobalFinancials(self, year, user)

    def getUtilization(self, year):
        return GlobalUtilization(self, year)

    def getDepartmentFinancials(self, year, user):
        return GlobalDepartmentFinancials(self, year, user)

    def getDepartmentUtilization(self, year):
        return GlobalDepartmentUtilization(self, year)