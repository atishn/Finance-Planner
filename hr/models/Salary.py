from __future__ import division
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from hr.models import Base


class Salary(Base):
    __tablename__ = 'salary'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    salary = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    percent_billable = Column(Integer, nullable=False)

    def __init__(self, user, salary, start_date, percent_billable=100):
        self.user = user
        self.salary = salary
        self.start_date = start_date
        self.percent_billable = percent_billable
