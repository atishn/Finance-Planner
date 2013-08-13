from __future__ import division
import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.utilities import money_formatted_micro,money_formatted

class BudgetAllocation(Base):
    __tablename__ = 'budget_allocation'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer,ForeignKey('department.id'))
    project_id = Column(Integer, ForeignKey('project.id'),nullable=True)
    ghost_project_id = Column(Integer,ForeignKey('ghost_project.id'),nullable=True)
    percent_allocation = Column(Integer, nullable=False)
    
    def __init__(self,department,project,ghost_project,percent_allocation):
        self.department = department
        self.project = project
        self.ghost_project = ghost_project
        self.percent_allocation = percent_allocation
