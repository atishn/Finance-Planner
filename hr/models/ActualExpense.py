from __future__ import division
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from hr.models import Base


class ActualExpense(Base):
    __tablename__ = 'actual_expense'
    id = Column(Integer, primary_key=True)
    office_id = Column(Integer, ForeignKey('office.id'))
    client_id = Column(Integer, ForeignKey('client.id'))
    expense_local = Column(Integer)
    expense_global = Column(Integer)
    quarter_end_date = Column(DateTime, nullable=False)

    def __init__(self, office, client, expense_local, expense_global, quarter_end_date):
        self.office = office
        self.client = client
        self.expense_local = expense_local
        self.expense_global = expense_global
        self.quarter_end_date = quarter_end_date
