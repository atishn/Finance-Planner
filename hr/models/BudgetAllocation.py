from __future__ import division
from sqlalchemy import Column, ForeignKey, Integer
from hr.models import Base


class BudgetAllocation(Base):
    __tablename__ = 'budget_allocation'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('department.id'))
    project_id = Column(Integer, ForeignKey('project.id'), nullable=True)
    ghost_project_id = Column(Integer, ForeignKey('ghost_project.id'), nullable=True)
    percent_allocation = Column(Integer, nullable=False)

    def __init__(self, department, project, ghost_project, percent_allocation):
        self.department = department
        self.project = project
        self.ghost_project = ghost_project
        self.percent_allocation = percent_allocation
