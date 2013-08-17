import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base


class SkillsetCategory(Base):
    __tablename__ = 'skillset_category'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)

    name = Column(Unicode(40), nullable=False)
    description = Column(UnicodeText, nullable=True)

    department_id = Column(Integer, ForeignKey('department.id'))

    salary_low = Column(Integer, nullable=True)
    salary_high = Column(Integer, nullable=True)

    skillsets = relationship('Skillset', backref='skillset_category')

    def __init__(self, name, department):
        self.name = name
        self.department = department
        self.created_at = db_utc_now()
        self.is_active = True
    