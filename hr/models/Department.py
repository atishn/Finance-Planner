import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.DepartmentUtilization import DepartmentUtilization
from hr.models.DepartmentFinancials import DepartmentFinancials


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)

    # hack because i can't get the relationships to work
    manager_name = Column(Unicode(40), nullable=True)
    manager_id = Column(Integer, nullable=True)

    name = Column(Unicode(40), nullable=False)

    skillset_categorys = relationship('SkillsetCategory', backref='department')
    roles = relationship('Role', backref='department')
    users = relationship('User', backref='department')
    ghost_users = relationship('GhostUser', backref='department')

    budget_allocations = relationship('BudgetAllocation', backref='department')

    def __init__(self, name, account):
        self.name = name.lower()
        self.account = account
        self.created_at = db_utc_now()
        self.is_active = True

    def getUtilization(self, year):
        return DepartmentUtilization(self, year)

    def getFinancials(self, year, user):
        return DepartmentFinancials(self, year, user)
        