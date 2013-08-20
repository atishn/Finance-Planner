from __future__ import division
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from hr.models import Base


class ActualRevenue(Base):
    __tablename__ = 'actual_revenue'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    revenue = Column(Integer, nullable=False)
    quarter_end_date = Column(DateTime, nullable=False)

    def __init__(self, project, revenue, quarter_end_date):
        self.project = project
        self.revenue = revenue
        self.quarter_end_date = quarter_end_date
    