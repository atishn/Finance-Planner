from __future__ import division

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean, Unicode
from sqlalchemy.orm import relationship

from hr.db import db_utc_now
from hr.models import Base


class GhostProject(Base):
    __tablename__ = 'ghost_project'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)

    name = Column(Unicode(40), nullable=False)
    code = Column(Unicode(40), nullable=False)

    account_id = Column(Integer, ForeignKey('account.id'))
    client_id = Column(Integer, ForeignKey('client.id'))

    ghost_client_id = Column(Integer, ForeignKey('ghost_client.id'))
    revenue = Column(Integer, nullable=False)
    likelihood = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    budget_allocations = relationship('BudgetAllocation', backref='ghost_project')

    def __init__(self, name, code, account, client, ghost_client, revenue, likelihood, start_date, end_date):
        self.name = name.lower()
        self.code = code
        self.client = client
        self.ghost_client = ghost_client
        self.revenue = revenue
        self.likelihood = likelihood
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = db_utc_now()
        self.is_active = True
        self.account = account
        self.status = 1

    def _number_of_days(self):
        difference = self.end_date - self.start_date
        return difference.days + 1

    number_of_days = property(_number_of_days)

    def _revenue_per_day(self):
        return self.revenue / self.number_of_days

    revenue_per_day = property(_revenue_per_day)

    def _likely_revenue_per_day(self):
        return self.revenue_per_day * self.likelihood / 100

    likely_revenue_per_day = property(_likely_revenue_per_day)

    def _likely_revenue(self):
        return self.revenue * self.likelihood / 100

    likely_revenue = property(_likely_revenue)