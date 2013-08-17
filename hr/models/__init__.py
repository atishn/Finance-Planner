# package
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


from hr.models.Department import Department
from hr.models.Office import Office
from hr.models.User import User
from hr.models.Account import Account
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.models.Office import Office
from hr.models.Review import Review
from hr.models.Role import Role
from hr.models.Skillset import Skillset
from hr.models.SkillsetEntry import SkillsetEntry
from hr.models.SkillsetCategory import SkillsetCategory
from hr.models.User import User
from hr.models.Feedback import Feedback
from hr.models.Freelancer import Freelancer
from hr.models.GhostAllocation import GhostAllocation
from hr.models.GhostUser import GhostUser
from hr.models.Client import Client
from hr.models.Project import Project
from hr.models.UserAllocation import UserAllocation
from hr.models.Currency import Currency