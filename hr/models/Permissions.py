import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base
from hr.models.ManyToMany import permissions_office_financials,permissions_client_financials,permissions_office_utilization,permissions_client_utilization,permissions_office_pipeline,view_permissions_to_office,edit_permissions_to_office,view_permissions_to_department,edit_permissions_to_department

class Permissions(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    
    user = relationship("User", uselist=False, backref="permissions")
    
    is_administrator = Column(Boolean, nullable=False)
    can_view_salaries = Column(Boolean, nullable=False)
    can_edit_salaries = Column(Boolean, nullable=False)
    
    can_view_all_offices = Column(Boolean, nullable=False)
    can_edit_all_offices = Column(Boolean, nullable=False)
    can_view_all_departments = Column(Boolean, nullable=False)
    can_edit_all_departments = Column(Boolean, nullable=False)
    
    view_offices = relationship("Office",secondary=view_permissions_to_office)
    edit_offices = relationship("Office",secondary=edit_permissions_to_office)
    
    view_departments = relationship("Department",secondary=view_permissions_to_department)
    edit_departments = relationship("Department",secondary=edit_permissions_to_department)
    
    def __init__(self,is_administrator = None, can_view_salaries = None, can_edit_salaries = None, can_view_all_offices = None, can_edit_all_offices = None, can_view_all_departments = None, can_edit_all_departments = None):
        if is_administrator is None:
            self.is_administrator = False
        else:
            self.is_administrator = is_administrator
        if can_view_salaries is None:
            self.can_view_salaries = False
        else:
            self.can_view_salaries = can_view_salaries
        if can_edit_salaries is None:
            self.can_edit_salaries = False
        else:
            self.can_edit_salaries = can_edit_salaries
        if can_view_all_offices is None:
            self.can_view_all_offices = False
        else:
            self.can_view_all_offices = can_view_all_offices
        if can_edit_all_offices is None:
            self.can_edit_all_offices = False
        else:
            self.can_edit_all_offices = can_edit_all_offices
        if can_view_all_departments is None:
            self.can_view_all_departments = False
        else:
            self.can_view_all_departments = can_view_all_departments
        if can_edit_all_departments is None:
            self.can_edit_all_departments = False
        else:
            self.can_edit_all_departments = can_edit_all_departments
        
        