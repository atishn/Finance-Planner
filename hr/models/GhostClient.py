from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode
from sqlalchemy.orm import relationship

from hr.db import db_utc_now
from hr.models import Base
from hr.models.GhostClientFinancials import GhostClientFinancials
from hr.models.GhostClientUtilization import GhostClientUtilization


class GhostClient(Base):
    __tablename__ = 'ghost_client'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_tbg = Column(Boolean, nullable=False)

    account_id = Column(Integer, ForeignKey('account.id'))
    office_id = Column(Integer, ForeignKey('office.id'))

    name = Column(Unicode(40))
    code = Column(Unicode(40))

    ghost_projects = relationship('GhostProject', backref='ghost_client')
    team = relationship('UserAllocation', backref='ghost_client')
    ghost_team = relationship('GhostAllocation', backref='ghost_client')

    def __init__(self, name, code, office):
        self.name = name.lower()
        self.code = code
        self.office = office
        self.account_id = office.account_id
        self.is_active = True
        self.created_at = db_utc_now()
        if name is None:
            self.is_tbg = True
        else:
            self.is_tbg = False

    def getFinancials(self, year, user):
        return GhostClientFinancials(self, year, user)

    def getUtilization(self, year):
        return GhostClientUtilization(self, year)