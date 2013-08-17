import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.utilities import money_formatted_micro, money_formatted


class GhostUser(Base):
    __tablename__ = 'ghost_user'
    id = Column(Integer, primary_key=True)

    percent_billable = Column(Integer, nullable=True)
    role_id = Column(Integer, ForeignKey('role.id'))
    office_id = Column(Integer, ForeignKey('office.id'))
    department_id = Column(Integer, ForeignKey('department.id'))
    account_id = Column(Integer, ForeignKey('account.id'))
    start_date = Column(DateTime, nullable=False)

    allocations = relationship('GhostAllocation', backref='ghost_user')

    def __init__(self, role, office, start_date, percent_billable):
        self.role = role
        self.office = office
        self.department_id = role.department_id
        self.account_id = office.account_id
        self.start_date = start_date
        self.percent_billable = percent_billable

    def _loaded_salary_per_day(self):
        return self.role.loaded_salary_per_day

    loaded_salary_per_day = property(_loaded_salary_per_day)

    def _loaded_non_billable_salary_per_day(self):
        return self.loaded_salary_per_day * (1 - (self.percent_billable / 100))

    loaded_non_billable_salary_per_day = property(_loaded_non_billable_salary_per_day)

    def _loaded_billable_salary_per_day(self):
        return self.loaded_salary_per_day * (self.percent_billable) / 100

    loaded_billable_salary_per_day = property(_loaded_billable_salary_per_day)
      
