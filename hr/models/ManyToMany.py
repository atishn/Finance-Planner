import bcrypt, locale, datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode, UnicodeText, Text, Table
from hr.db import db_utc_now, convert_db_datetime, parse_datetime_string
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hr.models import Base


permissions_office_financials = Table('permissions_office_financials', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('office_id', Integer, ForeignKey('office.id'))
)
permissions_office_pipeline = Table('permissions_office_pipeline', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('office_id', Integer, ForeignKey('office.id'))
)
permissions_office_utilization = Table('permissions_office_utilization', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('office_id', Integer, ForeignKey('office.id'))
)
permissions_client_financials = Table('permissions_client_financials', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('client_id', Integer, ForeignKey('client.id'))
)
permissions_client_pipeline = Table('permissions_client_pipeline', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('client_id', Integer, ForeignKey('client.id'))
)
permissions_client_utilization = Table('permissions_client_utilization', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('client_id', Integer, ForeignKey('client.id'))
)
permissions_department_financials = Table('permissions_department_financials', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('department_id', Integer, ForeignKey('department.id'))
)
permissions_department_utilization = Table('permissions_department_utilization', Base.metadata,
	 Column('user_id', Integer, ForeignKey('user.id')),
	 Column('department_id', Integer, ForeignKey('department.id'))
)












view_permissions_to_office = Table('view_permissions_to_office', Base.metadata,
	 Column('permissions_id', Integer, ForeignKey('permissions.id')),
	 Column('office_id', Integer, ForeignKey('office.id'))
)

edit_permissions_to_office = Table('edit_permissions_to_office', Base.metadata,
	 Column('permissions_id', Integer, ForeignKey('permissions.id')),
	 Column('office_id', Integer, ForeignKey('office.id'))
)

view_permissions_to_department = Table('view_department_to_office', Base.metadata,
	 Column('permissions_id', Integer, ForeignKey('permissions.id')),
	 Column('department_id', Integer, ForeignKey('department.id'))
)

edit_permissions_to_department = Table('edit_permissions_to_department', Base.metadata,
	 Column('permissions_id', Integer, ForeignKey('permissions.id')),
	 Column('department_id', Integer, ForeignKey('department.id'))
)

